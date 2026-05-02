"""
Helper — Copernicus DEM (GLO-30) Avanos AOI tile fetch + mosaic + 20m UTM resample.

P1 T1.6 üretimi (Copernicus DEM 20m) bu turda gelmediği için P4'ün T4.8 (DEM aspect/
hillshade) bağımlılığı eksik kalıyor. AWS open-data registry'den (no-auth) tile'ları
indirir, mosaic eder, P1 ARD grid'ine birebir oturtur.

AWS public bucket:
    https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N{lat}_00_E{lon}_00_DEM/...

Bağımlılık YOK (Earthdata gerekmez, public bucket).
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path

import requests
from osgeo import gdal

gdal.UseExceptions()

EPSG_32636_WKT = (
    'PROJCS["WGS 84 / UTM zone 36N",GEOGCS["WGS 84",DATUM["WGS_1984",'
    'SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],'
    'UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
    'PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",33],'
    'PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],'
    'PARAMETER["false_northing",0],UNIT["metre",1],'
    'AUTHORITY["EPSG","32636"]]'
)


def list_tiles(bbox_wgs: tuple[float, float, float, float]) -> list[str]:
    w, s, e, n = bbox_wgs
    lat_min, lat_max = math.floor(s), math.ceil(n)
    lon_min, lon_max = math.floor(w), math.ceil(e)
    tiles = []
    for lat in range(lat_min, lat_max):
        for lon in range(lon_min, lon_max):
            ns = "N" if lat >= 0 else "S"
            ew = "E" if lon >= 0 else "W"
            tile = f"Copernicus_DSM_COG_10_{ns}{abs(lat):02d}_00_{ew}{abs(lon):03d}_00_DEM"
            tiles.append(tile)
    return tiles


def download_tile(tile_id: str, out_dir: Path) -> Path:
    url = f"https://copernicus-dem-30m.s3.amazonaws.com/{tile_id}/{tile_id}.tif"
    out_path = out_dir / f"{tile_id}.tif"
    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"[skip] {out_path.name} already exists ({out_path.stat().st_size/1e6:.1f} MB)")
        return out_path
    print(f"[get] {url}")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    out_dir.mkdir(parents=True, exist_ok=True)
    total = int(r.headers.get("Content-Length", 0))
    written = 0
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
            written += len(chunk)
            if total:
                print(f"\r  {written/1e6:.1f}/{total/1e6:.1f} MB ({written/total*100:.0f}%)",
                      end="", flush=True)
    print()
    return out_path


def mosaic_and_warp(tile_paths: list[Path], reference_tif: Path, out_path: Path,
                   res: float = 20.0) -> None:
    """Tile'ları mosaic et + P1 ARD bounds + 20m UTM 36N grid'ine warp et."""
    # 1. Reference bounds (UTM)
    ref = gdal.Open(str(reference_tif))
    gt = ref.GetGeoTransform()
    xmin = gt[0]
    ymax = gt[3]
    width = ref.RasterXSize
    height = ref.RasterYSize
    xmax = xmin + width * gt[1]
    ymin = ymax + height * gt[5]
    extent = (xmin, ymin, xmax, ymax)
    print(f"[target] EPSG:32636, {res}m, extent={extent}")

    # 2. VRT mosaic of tiles (still in WGS84 EPSG:4326 height)
    vrt_path = out_path.with_suffix(".vrt")
    gdal.BuildVRT(str(vrt_path), [str(p) for p in tile_paths])

    # 3. Warp VRT → UTM 36N + extent + 20m bilinear
    warp_opts = gdal.WarpOptions(
        format="GTiff",
        dstSRS=EPSG_32636_WKT,
        outputBounds=extent,
        xRes=res, yRes=res,
        resampleAlg="bilinear",
        creationOptions=["COMPRESS=DEFLATE", "PREDICTOR=2", "TILED=YES",
                         "BLOCKXSIZE=256", "BLOCKYSIZE=256"],
        dstNodata=-9999,
    )
    gdal.Warp(str(out_path), str(vrt_path), options=warp_opts)
    vrt_path.unlink()
    print(f"[ok] DEM written -> {out_path}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference", default="data/ard/s2_ard_20m.tif")
    p.add_argument("--cache", default="data/dem/_tiles/")
    p.add_argument("--out", default="data/dem/dem.tif")
    p.add_argument("--res", type=float, default=20.0)
    args = p.parse_args()

    # AOI bounds in WGS84 (Avanos)
    bbox_wgs = (34.4, 38.6, 35.1, 39.0)
    tiles = list_tiles(bbox_wgs)
    print(f"[tiles] {len(tiles)}: {tiles}")

    cache = Path(args.cache)
    paths = [download_tile(t, cache) for t in tiles]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    mosaic_and_warp(paths, Path(args.reference), out, res=args.res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
