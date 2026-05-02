"""T1.5 — Sentinel-1 GRD cekimi (GEE), Lee speckle filtresi, dB donusumu.

Giris : GEE COPERNICUS/S1_GRD koleksiyonu (IW modu, VV+VH)
Cikis : data/s1_stack/s1_vvvh_avanos.tif  (2 bant: VV_dB, VH_dB)
CRS   : EPSG:32636 (UTM 36N)
Cozunurluk : 20 m (Karar #15 — S2 grid'e eslesir)
Tarih : S2 ile eslestirilmis yaz 2024 penceresi
"""
import ee

PROJECT = "pomza-495012"
# WHY: Service account Drive kotası yok. earthengine authenticate ile
# kişisel credentials kullanılır → Drive'a export çalışır.
ee.Initialize(project=PROJECT)

AOI_BBOX = ee.Geometry.Rectangle([34.70, 38.65, 35.00, 38.85])
DATE_START = "2024-06-01"
DATE_END   = "2024-09-30"

# WHY: ENL~4.4, Sentinel-1 IW GRD icin standart deger (ESA donanima gore)
ENL = 4.4


def lee_filter(img, radius=3):
    """Lee speckle filtresi — linear scale. ENL tabanli gurultu varyans tahmini."""
    kernel = ee.Kernel.square(radius)
    mean = img.reduceNeighborhood(ee.Reducer.mean(), kernel)
    variance = img.reduceNeighborhood(ee.Reducer.variance(), kernel)
    noise_var = mean.pow(2).divide(ENL)
    w = variance.divide(variance.add(noise_var))
    return mean.add(w.multiply(img.subtract(mean)))


def to_db(img):
    """Linear power → dB: 10*log10(x). Sifir degerlerini onceden maskeler."""
    return img.where(img.gt(0), img.log10().multiply(10.0)).rename(img.bandNames())


def preprocess_s1(img):
    linear = lee_filter(img, radius=3)
    db = to_db(linear)
    return db.copyProperties(img, ["system:time_start"])


col = (
    ee.ImageCollection("COPERNICUS/S1_GRD")
    .filterBounds(AOI_BBOX)
    .filterDate(DATE_START, DATE_END)
    .filter(ee.Filter.eq("instrumentMode", "IW"))
    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
    .select(["VV", "VH"])
    .map(preprocess_s1)
)

count = col.size().getInfo()
print(f"S1 GRD sahneleri (IW, VV+VH, Lee+dB): {count}")

# Median composite — sezonluk degisimi ortalar, speckle varyansi azaltir
composite = col.median().clip(AOI_BBOX).toFloat()

task = ee.batch.Export.image.toDrive(
    image=composite,
    description="S1_GRD_VV_VH_avanos_20m",
    folder="Pomzadoya_GEE_exports",
    fileNamePrefix="s1_vvvh_avanos",
    region=AOI_BBOX,
    scale=20,
    crs="EPSG:32636",
    maxPixels=1e10,
    fileFormat="GeoTIFF",
)
task.start()
print(f"S1 export task baslatildi. Task id: {task.id}")
print("GEE Tasks panelinden izle (~20-30 dk). Drive'dan data/s1_stack/ altina indir.")
print("Bant sirasi: Band 1=VV_dB, Band 2=VH_dB")
