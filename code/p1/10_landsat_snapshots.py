"""T1.10 — Landsat Tier 2 snapshot cetimi (GEE).

Cikis : data/landsat/L{sensor}_{year}.tif — her yil icin ayri dosya
Yillar: 1985, 1990, 2000, 2010, 2025
Bantlar: SR_B1..SR_B7 (Collection 2 Level-2 Surface Reflectance)
CRS   : EPSG:32636, 30 m native (Landsat native — 20m'e upsample edilmez)

P5 Roy 2016 cross-sensor harmonizasyonu data/landsat/ altindaki dosyalari okur.
Bu script ham SR verisini export eder, harmonizasyon P5 sorumluluğundadir.

Sensör → Koleksiyon eslemesi (Collection 2):
  1985, 1990 : Landsat 5 TM  → LANDSAT/LT05/C02/T1_L2
  2000, 2010 : Landsat 7 ETM+ → LANDSAT/LE07/C02/T1_L2
  2025       : Landsat 9 OLI  → LANDSAT/LC09/C02/T1_L2
"""
import ee

from aoi_config import bbox_text, ee_rectangle

ee.Initialize(project="pomza-495012")

AOI_BBOX = ee_rectangle(ee)

# WHY: Yaz penceresi — pomza yuzey donemi, dusuk bulut olasiligi Kapadokya'da
SUMMER_WINDOW = ("06-01", "09-30")

SNAPSHOTS = [
    {"year": 1985, "collection": "LANDSAT/LT05/C02/T1_L2", "sensor": "L5"},
    {"year": 1990, "collection": "LANDSAT/LT05/C02/T1_L2", "sensor": "L5"},
    {"year": 2000, "collection": "LANDSAT/LE07/C02/T1_L2", "sensor": "L7"},
    {"year": 2010, "collection": "LANDSAT/LE07/C02/T1_L2", "sensor": "L7"},
    {"year": 2025, "collection": "LANDSAT/LC09/C02/T1_L2", "sensor": "L9"},
]

# WHY: Collection 2 Level-2 SR bantlari — TM/ETM+ ve OLI icin ortak isimler
# TM/ETM+: SR_B1(Blue) SR_B2(Green) SR_B3(Red) SR_B4(NIR) SR_B5(SWIR1) SR_B7(SWIR2)
# OLI-2  : SR_B2(Blue) SR_B3(Green) SR_B4(Red) SR_B5(NIR) SR_B6(SWIR1) SR_B7(SWIR2)
# P5 harmonizasyonu icin hem TM hem OLI bantlari export edilir; P5 secim yapar.
TM_BANDS  = ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"]
OLI_BANDS = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]
OUT_NAMES = ["Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2"]


def _apply_scale(img, sensor: str):
    """Collection 2 Level-2 olcekleme: 0.0000275 * DN - 0.2"""
    bands = OLI_BANDS if sensor == "L9" else TM_BANDS
    scaled = img.select(bands).multiply(0.0000275).add(-0.2).rename(OUT_NAMES)
    return scaled.copyProperties(img, ["system:time_start"])


def _cloud_mask_tm(img):
    """Landsat TM/ETM+ bulut maskesi (QA_PIXEL bit 3=cloud, bit 4=cloud_shadow)."""
    qa = img.select("QA_PIXEL")
    cloud = qa.bitwiseAnd(1 << 3).neq(0)
    shadow = qa.bitwiseAnd(1 << 4).neq(0)
    return img.updateMask(cloud.Not().And(shadow.Not()))


def _cloud_mask_oli(img):
    """Landsat 8/9 OLI bulut maskesi (aynı QA_PIXEL bitleri)."""
    return _cloud_mask_tm(img)


tasks = []
for snap in SNAPSHOTS:
    year    = snap["year"]
    coll_id = snap["collection"]
    sensor  = snap["sensor"]

    date_start = f"{year}-{SUMMER_WINDOW[0]}"
    date_end   = f"{year}-{SUMMER_WINDOW[1]}"

    cloud_fn = _cloud_mask_oli if sensor == "L9" else _cloud_mask_tm

    col = (
        ee.ImageCollection(coll_id)
        .filterBounds(AOI_BBOX)
        .filterDate(date_start, date_end)
        .map(cloud_fn)
        .map(lambda img, s=sensor: _apply_scale(img, s))
    )

    count = col.size().getInfo()
    print(f"{sensor} {year}: {count} sahne bulundu ({date_start}–{date_end})")

    if count == 0:
        # Plan B: pencereyi genislet — Landsat revisit 16 gun
        date_start_ext = f"{year}-04-01"
        date_end_ext   = f"{year}-10-31"
        col = (
            ee.ImageCollection(coll_id)
            .filterBounds(AOI_BBOX)
            .filterDate(date_start_ext, date_end_ext)
            .map(cloud_fn)
            .map(lambda img, s=sensor: _apply_scale(img, s))
        )
        count = col.size().getInfo()
        print(f"  [Plan B] Genis pencere ({date_start_ext}–{date_end_ext}): {count} sahne")

    if count == 0:
        print(f"  [UYARI] {sensor} {year} icin sahne bulunamadi — atlaniyor")
        continue

    composite = col.median().clip(AOI_BBOX).toFloat()
    prefix    = f"L{sensor[-1]}_{year}"   # ornekgin: L5_1985

    task = ee.batch.Export.image.toDrive(
        image=composite,
        description=f"Landsat_{sensor}_{year}_avanos",
        folder="Pomzadoya_GEE_exports",
        fileNamePrefix=prefix,
        region=AOI_BBOX,
        scale=30,         # Landsat native 30m — WHY: upsample edilmez (Roy 2016 harmonizasyon 30m uzerinde)
        crs="EPSG:32636",
        maxPixels=1e10,
        fileFormat="GeoTIFF",
    )
    task.start()
    tasks.append({"sensor": sensor, "year": year, "task_id": task.id, "prefix": prefix})
    print(f"  Export baslatildi: task={task.id}")

print("\n[T1.10] Tum Landsat export task'lari baslatildi.")
print(f"AOI: {bbox_text()}")
print("Drive klasoru: Pomzadoya_GEE_exports/")
print("Her dosyayi data/landsat/ altina indirin:")
for t in tasks:
    print(f"  {t['prefix']}.tif  ({t['sensor']} {t['year']})")
print("P5 bu dosyalari Roy 2016 harmonizasyonuyla kullanir.")
