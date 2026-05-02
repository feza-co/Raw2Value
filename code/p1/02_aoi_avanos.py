"""T1.2 — Avanos AOI polygon üretici.

Bbox: 34.60-35.00 E, 38.40-38.90 N (Avanos / Nevsehir genisletilmis).
Guncelleme: P2 pozitif poligonlar (38.47-38.71 N) orijinal AOI'nin (38.65-38.85 N)
guneyinde kaliyor. Guncellenmis bbox tum pomza sahalarini kapsiyor.
Source CRS: EPSG:4326 (WGS84) — analiz CRS'i: EPSG:32636 (UTM 36N).
Cikti: data/aoi/avanos_aoi.geojson + .gpkg (her iki CRS'te).
"""
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon

from aoi_config import AOI_LABEL, BBOX_WGS84, bbox_text

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "aoi"
OUT.mkdir(parents=True, exist_ok=True)

poly = Polygon([
    (BBOX_WGS84[0], BBOX_WGS84[1]),
    (BBOX_WGS84[2], BBOX_WGS84[1]),
    (BBOX_WGS84[2], BBOX_WGS84[3]),
    (BBOX_WGS84[0], BBOX_WGS84[3]),
    (BBOX_WGS84[0], BBOX_WGS84[1]),
])

gdf_wgs = gpd.GeoDataFrame(
    {"name": ["avanos_aoi"], "source": ["P1_T1.2"], "aoi_version": [AOI_LABEL]},
    geometry=[poly],
    crs="EPSG:4326",
)
gdf_utm = gdf_wgs.to_crs("EPSG:32636")

# WGS84 (etiketleme/QGIS altligi icin)
gdf_wgs.to_file(OUT / "avanos_aoi.geojson", driver="GeoJSON")
gdf_wgs.to_file(OUT / "avanos_aoi.gpkg", driver="GPKG", layer="aoi_wgs84")

# UTM 36N (analiz / ARD grid icin)
gdf_utm.to_file(OUT / "avanos_aoi_utm36n.geojson", driver="GeoJSON")
gdf_utm.to_file(OUT / "avanos_utm36n.geojson", driver="GeoJSON")
gdf_utm.to_file(OUT / "avanos_aoi.gpkg", driver="GPKG", layer="aoi_utm36n")

minx, miny, maxx, maxy = gdf_utm.total_bounds
area_km2 = gdf_utm.geometry.area.iloc[0] / 1e6
print(f"AOI bbox (WGS84): {bbox_text()}")
print(f"AOI bounds (UTM 36N): {minx:.0f},{miny:.0f} -> {maxx:.0f},{maxy:.0f}")
print(f"AOI area: {area_km2:.1f} km^2")
print(f"Output: {OUT}/avanos_aoi.geojson + .gpkg")
