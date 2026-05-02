# [P1] T1.2 — AOI Tanimi (Avanos Polygon, EPSG:32636)

## RUN-BLOCK [T1.2]
**Hedef ortam:** Yerel terminal (Windows PowerShell veya WSL/bash) **VEYA** Colab hucresi.
**Onkosul:**
- T1.1 tamam (geopandas/shapely yuklu).
- Repo kokunde calistiriliyor: `c:/Users/tuna9/OneDrive/Masaüstü/Pomzadoya/`

**Adimlar:**

### A) Yerel (PowerShell):
```powershell
cd "c:\Users\tuna9\OneDrive\Masaüstü\Pomzadoya"
pip install -r code/p1/requirements.txt
python code\p1\02_aoi_avanos.py
```

### B) Colab (T1.1 notebook'unda yeni hucre):
```python
%cd /content/drive/MyDrive/Pomzadoya
!python code/p1/02_aoi_avanos.py
```

**Beklenen sure:** ~30 sn.

**Bbox:** 34.70-35.00 E, 38.65-38.85 N (Avanos / Nevsehir).
**CRS:** Source EPSG:4326 -> Reproject EPSG:32636 (UTM 36N).

## VERIFY-BLOCK [T1.2]
Bana yapistir:
- Script son 3 satir ciktisi (`AOI bounds (UTM 36N): ...`, `AOI area: ... km^2`, `Output: ...`)
- `ls data/aoi/` (4 dosya gorulmeli):
  - `avanos_aoi.geojson` (WGS84)
  - `avanos_aoi_utm36n.geojson` (UTM 36N)
  - `avanos_aoi.gpkg` (iki layer: aoi_wgs84 + aoi_utm36n)

**Sanity threshold:**
- AOI alani: ~700 km^2 +/- %20 (bbox 0.30 deg lon x 0.20 deg lat ~= 28x22 km)
- UTM bounds: minx ~= 647000, miny ~= 4279000 (Avanos UTM 36N civari)

## DELIVER (sen yapistirinca soyleyecegim)
```
[P1] T1.2 TAMAM
Cikti: data/aoi/avanos_aoi.geojson, .gpkg, _utm36n.geojson
Sanity: alan ~7XX km^2, UTM 36N bounds dogrulandi
Siradaki: T1.3 S2 L2A fetch (RUN-BLOCK p1_t1_3_runblock.md) — ASENKRON, ~30 dk GEE export
```
