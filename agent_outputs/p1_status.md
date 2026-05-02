# P1 — Veri Muhendisi Durum Raporu

**Tarih:** 2026-05-01
**Faz:** Modul A v2, saat 0-4 penceresi (T1.1-T1.4)
**Rol:** P1 — Critical path basi.

## Hazirlanan Dosyalar (kod + RUN-BLOCK)

| Dosya | Tip | T_x | Durum |
|---|---|:-:|:-:|
| `code/p1/01_gee_setup.ipynb` | Colab notebook | T1.1 | HAZIR |
| `code/p1/02_aoi_avanos.py` | Python script | T1.2 | HAZIR |
| `code/p1/03_sentinel2_l2a_fetch.py` | GEE Python script | T1.3 | HAZIR |
| `code/p1/04_s2_coregistration.py` | gdalwarp script | T1.4 | HAZIR |
| `code/p1/run_pipeline.sh` | Pipeline shell | tum | ISKELET (T1.5-T1.9 TODO) |
| `code/p1/requirements.txt` | Python deps | T1.1 | HAZIR |
| `agent_outputs/p1_t1_1_runblock.md` | RUN+VERIFY | T1.1 | HAZIR |
| `agent_outputs/p1_t1_2_runblock.md` | RUN+VERIFY | T1.2 | HAZIR |
| `agent_outputs/p1_t1_3_runblock.md` | RUN+VERIFY | T1.3 | HAZIR (asenkron uyarili) |

## Bekleyen — Kullanici Eylemi

1. **T1.1**: Colab'da `01_gee_setup.ipynb` ac -> service account JSON yukle -> 5 hucre kostur.
2. **T1.2**: yerel terminal -> `python code/p1/02_aoi_avanos.py`.
3. **T1.3**: Colab'da T1.1 notebook'una hucre ekle -> `exec(open('code/p1/03_sentinel2_l2a_fetch.py').read())` -> Task ID al.
   - **ASENKRON**: ~30 dk export bekleyisi. Bu sirada T1.5/T1.6 hazirlayabilirim.

## Bekleyen — P1 Hazirlamasi (sirada)

| T_x | Aciklama | Saat | Tetikleyici |
|---|---|:-:|---|
| T1.5 | S1 GRD (VV+VH) + Lee filter `05_sentinel1_fetch.py` | 4-5.5 | T1.4 verify sonrasi |
| T1.6 | Copernicus DEM + slope `06_dem_slope.py` | 5.5-6.5 | T1.5 paralel |
| T1.7 | 17-kanal Full ARD co-reg `07_full_ard_stack.py` | 6.5-8 | **CRITICAL** — P3 saat 8'de bekliyor |
| T1.8 | Tile 256x256 + 32 px overlap `08_tile_split.py` | 8-10 | P2 saat 10'da bekliyor |
| T1.9 | Manifest JSON export `09_manifest.py` | 10-11 | **CRITICAL** — P3+P4+P5 |
| T1.10 | Landsat Tier 2 snapshot | 11-13 | P5 saat 13'te bekliyor |
| T1.11 | QC raporu | 13-14 | — |

## Critical Path Pozisyonu

```
T1.3 -> T1.4 -> T1.5 -> T1.6 -> T1.7 -> T1.8 -> T1.9 -> [P3 T3.5a]
[su an]   [siradaki kullanici eylemi sonrasi]
```

## Siradaki Tek Kullanici Eylemi

> **Colab'i ac, `code/p1/01_gee_setup.ipynb` notebook'unu yukle, `agent_outputs/p1_t1_1_runblock.md` icindeki RUN-BLOCK'u takip et.**
> T1.1 verify ciktisini bana yapistir; T1.2'yi tetikleyecegim. T1.3 (asenkron ~30dk) tetiklendikten sonra T1.5/T1.6 scriptlerini paralel uretecegim.

## Riskler / Uyarilar

- **T1.3 asenkron**: GEE export ~30 dk. Kullanici bu sure boyunca baska is cevirebilir; ben T1.5+ hazirlarim.
- **Bulut riski (Plan B)**: T1.3'te SCL sonrasi NoData > %15 olursa pre-cache temiz tile fallback'e gecilir (orchestrator onayi gerekir).
- **Sat 4 hard deadline**: P4 (T4.5) S2 ARD bekliyor — T1.4 saat 4'te tamamlanmali, gecikme P4'u kilitler.
