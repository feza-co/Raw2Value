"""T1.6 — Copernicus GLO-30 DEM cetimi (GEE) + slope hesabi.

Giris : GEE COPERNICUS/DEM/GLO30 mozaigi
Cikis : data/dem.tif    (1 bant: yukseklik, metre)
        data/slope.tif  (1 bant: egim, derece)
CRS   : EPSG:32636 (UTM 36N)
Cozunurluk : 20 m (GLO-30 native 30m → GEE bilinear resample)
"""
import ee

from aoi_config import bbox_text, ee_rectangle

PROJECT = "pomza-495012"
# WHY: Service account Drive kotasi yok. earthengine authenticate ile
# kisisel credentials kullanilir -> Drive'a export calisir.
ee.Initialize(project=PROJECT)

AOI_BBOX = ee_rectangle(ee)

dem = (
    ee.ImageCollection("COPERNICUS/DEM/GLO30")
    .filterBounds(AOI_BBOX)
    .select("DEM")
    .mosaic()
    .clip(AOI_BBOX)
)

# WHY: ee.Terrain.slope SRTM/Copernicus DEM'den derece cinsinden egim uretir
slope = ee.Terrain.slope(dem).rename("slope")

elev = dem.rename("elevation").toFloat()
slope = slope.toFloat()

# DEM export
task_dem = ee.batch.Export.image.toDrive(
    image=elev,
    description="Copernicus_DEM_avanos_20m",
    folder="Pomzadoya_GEE_exports",
    fileNamePrefix="dem_avanos",
    region=AOI_BBOX,
    scale=20,
    crs="EPSG:32636",
    maxPixels=1e10,
    fileFormat="GeoTIFF",
)
task_dem.start()
print(f"DEM export baslatildi. Task id: {task_dem.id}")

# Slope export
task_slope = ee.batch.Export.image.toDrive(
    image=slope,
    description="Copernicus_slope_avanos_20m",
    folder="Pomzadoya_GEE_exports",
    fileNamePrefix="slope_avanos",
    region=AOI_BBOX,
    scale=20,
    crs="EPSG:32636",
    maxPixels=1e10,
    fileFormat="GeoTIFF",
)
task_slope.start()
print(f"Slope export baslatildi. Task id: {task_slope.id}")
print(f"AOI: {bbox_text()}")
print("Drive'dan: dem_avanos.tif -> data/dem/dem_avanos.tif")
print("Drive'dan: slope_avanos.tif -> data/dem/slope_avanos.tif")

# Sanity check
stats = elev.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=AOI_BBOX,
    scale=100,
    maxPixels=1e6,
).getInfo()
print(f"DEM sanity — min: {stats.get('elevation_min'):.0f} m, max: {stats.get('elevation_max'):.0f} m")
print("Avanos yuksekligi beklenti: ~900-1300 m arasi (Kapadokya platosu)")
