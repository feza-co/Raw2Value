"""T1.3 — Sentinel-2 L2A cekimi + SCL bulut maskeleme (GEE).

Karar #15 (SWIR native 20m): SWIR (B11/B12) zaten 20m, NIR/Red 10m bantlar
20m grid'e bilinear downsample (T1.4 co-registration adiminda).

Bantlar (10): B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12
SCL maskesi: 4 (vegetation), 5 (bare soil), 6 (water), 11 (snow) -> KEEP
            3 (cloud_shadow), 8/9/10 (cloud), 1 (saturated) -> MASK
Hedef bulut orani: CLOUDY_PIXEL_PERCENTAGE < 20

Kullanim: bu script GEE Code Editor'a yapistirilir VEYA Colab'da
01_gee_setup.ipynb sonrasinda calistirilir. Export GEE'nin kendi
Drive/Asset target'ina gider — sonuclar repo'ya manuel/rclone ile alinir.
"""
import ee

# WHY: GEE auth disarida yapilir (01_gee_setup.ipynb), burada Initialize varsayalir.
ee.Initialize()

AOI_BBOX = ee.Geometry.Rectangle([34.70, 38.65, 35.00, 38.85])

DATE_START = "2024-06-01"
DATE_END   = "2024-09-30"

S2_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]

# WHY: SCL kategorileri ESA L2A urun spec'i (Sen2Cor)
SCL_KEEP = [4, 5, 6, 11]


def mask_s2_scl(img):
    scl = img.select("SCL")
    mask = ee.Image(0)
    for v in SCL_KEEP:
        mask = mask.Or(scl.eq(v))
    return img.updateMask(mask).select(S2_BANDS).copyProperties(img, ["system:time_start"])


col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
       .filterBounds(AOI_BBOX)
       .filterDate(DATE_START, DATE_END)
       .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
       .map(mask_s2_scl))

count = col.size().getInfo()
print(f"S2 L2A scenes (cloud<20%, SCL-masked): {count}")

# Median composite — pomza yuzeyi seasonal stable, median tek-sahne bulut artiklarini siler
composite = col.median().clip(AOI_BBOX).toFloat()

# Export to Drive — kullanici GEE Tasks panelinden 'Run' der
task = ee.batch.Export.image.toDrive(
    image=composite,
    description="S2_L2A_avanos_20m",
    folder="Pomzadoya_GEE_exports",
    fileNamePrefix="s2_l2a_avanos_median_2024_20m",
    region=AOI_BBOX,
    scale=20,           # Karar #15 SWIR native grid
    crs="EPSG:32636",
    maxPixels=1e10,
    fileFormat="GeoTIFF",
)
task.start()
print(f"Export task baslatildi. Task id: {task.id}")
print("GEE Tasks panelinden ilerlemeyi izle (~25-35 dk).")
