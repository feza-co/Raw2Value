"""
Helper — ASTER L1B HDF içindeki gömülü 121 GCP'yi (UTM 36N koordinatlarında)
kullanarak TIR Bant 10-14'ü UTM 36N georeferenced GeoTIFF stack'e dönüştür.

Sorun: ASTER L1B HDF'de GCP'ler UTM 36N (X=628679, Y=4364150 gibi metre)
değerlerinde gömülü ama GCP_PROJECTION boş. GDAL "unnamed PROJCS" üretiyor,
sonraki adımlarda CRS resolve edilemiyor.

Çözüm: GCP'lere EPSG:32636 WKT string'ini manuel ata, sonra gdalwarp ile
hedef bbox'a affine fit yap.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from osgeo import gdal, osr

gdal.UseExceptions()

# WGS 84 / UTM Zone 36N — EPSG:32636 (hard-coded WKT, EPSG database independent)
EPSG_32636_WKT = (
    'PROJCS["WGS 84 / UTM zone 36N",'
    'GEOGCS["WGS 84",'
    'DATUM["WGS_1984",'
    'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
    'AUTHORITY["EPSG","6326"]],'
    'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
    'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],'
    'AUTHORITY["EPSG","4326"]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["latitude_of_origin",0],'
    'PARAMETER["central_meridian",33],'
    'PARAMETER["scale_factor",0.9996],'
    'PARAMETER["false_easting",500000],'
    'PARAMETER["false_northing",0],'
    'UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
    'AXIS["Easting",EAST],AXIS["Northing",NORTH],'
    'AUTHORITY["EPSG","32636"]]'
)

TIR_BANDS = {
    "B10": "ImageData10",
    "B11": "ImageData11",
    "B12": "ImageData12",
    "B13": "ImageData13",
    "B14": "ImageData14",
}


def georef_band(hdf_path: Path, band_name: str, out_tif: Path,
                tres: float = 90.0) -> dict:
    """ASTER TIR subdataset'i gerçek-koordinat'lı GeoTIFF'e dönüştür."""
    uri = f'HDF4_EOS:EOS_SWATH:"{hdf_path.as_posix()}":TIR_Swath:{band_name}'
    src = gdal.Open(uri)
    if src is None:
        raise RuntimeError(f"Could not open {uri}")
    gcps = src.GetGCPs()
    if not gcps:
        raise RuntimeError(f"No GCPs found in {uri}")

    # Step 1: Translate to a temp GeoTIFF with proper SRS on GCPs
    tmp_path = out_tif.parent / f"_tmp_{band_name}.tif"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    translate_opts = gdal.TranslateOptions(
        format="GTiff",
        outputType=gdal.GDT_Float32,
        GCPs=gcps,
        outputSRS=EPSG_32636_WKT,
    )
    gdal.Translate(str(tmp_path), src, options=translate_opts)
    src = None

    # Step 2: Warp tmp → resampled UTM grid
    warp_opts = gdal.WarpOptions(
        format="GTiff",
        dstSRS=EPSG_32636_WKT,
        srcSRS=EPSG_32636_WKT,
        xRes=tres, yRes=tres,
        resampleAlg="bilinear",
        targetAlignedPixels=True,
        creationOptions=["COMPRESS=DEFLATE", "PREDICTOR=2", "TILED=YES"],
        srcNodata=0, dstNodata=0,
        tps=True,  # use thin-plate spline from GCPs
    )
    gdal.Warp(str(out_tif), str(tmp_path), options=warp_opts)
    tmp_path.unlink()

    # Sanity
    g = gdal.Open(str(out_tif))
    info = {
        "out": str(out_tif),
        "size": [g.RasterXSize, g.RasterYSize],
        "geotransform": list(g.GetGeoTransform()),
        "srs": g.GetSpatialRef().GetName() if g.GetSpatialRef() else None,
    }
    return info


def stack_tir_bands(out_files: list[Path], stack_path: Path) -> None:
    """5 single-band GeoTIFF'i 5-bant stack'e birleştir (B10..B14)."""
    vrt_opts = gdal.BuildVRTOptions(separate=True, srcNodata=0, VRTNodata=0)
    vrt_path = stack_path.with_suffix(".vrt")
    gdal.BuildVRT(str(vrt_path), [str(p) for p in out_files], options=vrt_opts)
    translate_opts = gdal.TranslateOptions(
        format="GTiff",
        outputType=gdal.GDT_Float32,
        creationOptions=["COMPRESS=DEFLATE", "PREDICTOR=2", "TILED=YES",
                         "BIGTIFF=IF_SAFER"],
        noData=0,
    )
    gdal.Translate(str(stack_path), str(vrt_path), options=translate_opts)
    vrt_path.unlink()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hdf", required=True, help="ASTER L1B .hdf path")
    p.add_argument("--out", default="data/aster/_geo/")
    p.add_argument("--stack", default="data/aster/AST_TIR_geo_stack.tif")
    p.add_argument("--tres", type=float, default=90.0)
    args = p.parse_args()

    hdf_path = Path(args.hdf)
    out_dir = Path(args.out)
    stack_path = Path(args.stack)

    band_files: list[Path] = []
    info_per_band: dict[str, dict] = {}
    for label, sds in TIR_BANDS.items():
        band_tif = out_dir / f"AST_TIR_{label}_geo.tif"
        info = georef_band(hdf_path, sds, band_tif, tres=args.tres)
        info_per_band[label] = info
        band_files.append(band_tif)
        print(f"[ok] {label} -> {band_tif}  size={info['size']}  gt={info['geotransform'][:3]}...")

    stack_tir_bands(band_files, stack_path)
    print(f"[ok] 5-band TIR stack -> {stack_path}")

    meta = {
        "source": str(hdf_path),
        "stack": str(stack_path),
        "bands_order": list(TIR_BANDS.keys()),
        "subdataset_map": TIR_BANDS,
        "target_crs": "EPSG:32636",
        "target_res_m": args.tres,
        "resampling": "bilinear (TPS warp)",
        "per_band": info_per_band,
    }
    (out_dir / "_geo_meta.json").write_text(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
