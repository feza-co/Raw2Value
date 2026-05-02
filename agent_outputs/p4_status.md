# P4 Spektral Mühendis — DURUM (2026-05-01)

## Üretilen artefaktlar (kod)

| # | Dosya | Görev | Durum |
|---|---|---|---|
| 01 | `code/p4/01_earthdata_setup.md` | T4.1 — Earthdata token + .netrc | HAZIR |
| 02 | `code/p4/02_aster_l1b_download.py` | T4.2 — CMR API + LP DAAC indirme | HAZIR |
| 03 | `code/p4/03_aster_l1b_to_l2.py` | T4.3 — DOS atmosferik düzeltme + Plan B (--no-dos) | HAZIR |
| 04 | `code/p4/04_s2_indices.py` | T4.4 — NDVI/BSI/Albedo Liang/Sabins | HAZIR |
| 05 | `code/p4/05_ninomiya_qi.py` | **T4.5** — QI=B11²/(B10·B12), CI=B13/B14, SiO₂ | HAZIR |
| 06 | `code/p4/06_resample_to_s2_grid.py` | T4.6 — bilinear 20m resample (gdalwarp + rasterio fallback) | HAZIR |
| 07 | `code/p4/07_fusion_prototype.py` | T4.7 — sentetik P3 ile füzyon prototipi | HAZIR |
| 08 | `code/p4/08_dem_aspect_hillshade.py` | T4.8 — gdaldem + numpy fallback | HAZIR |
| 09 | `code/p4/09_layer_export.py` | T4.10 — COG export + manifest + layer_docs.md | HAZIR |
| 10 | `code/p4/fuse_confidence.py` | **T4.12 KRİTİK** — score-level füzyon API + CLI | HAZIR |
| 11 | `code/p4/requirements.txt` | bağımlılıklar | HAZIR |

## Üretilen artefaktlar (RUN-BLOCK)

| # | Dosya | Görev |
|---|---|---|
| 12 | `agent_outputs/p4_t4_1_runblock.md` | T4.1 setup |
| 13 | `agent_outputs/p4_t4_2_runblock.md` | T4.2 indirme (asenkron 30 dk) |
| 14 | `agent_outputs/p4_t4_3_runblock.md` | T4.3 atmosferik düzeltme (~1h) + Plan B |
| 15 | `agent_outputs/p4_t4_12_runblock.md` | **T4.12 CRITICAL** canlı füzyon (saat 18-20) |
| 16 | `agent_outputs/p4_status.md` | bu dosya |

## Kritik kararlar / dayanaklar

- **K#3** ASTER L1T (geocoded radiance) öncelikli, L1B fallback. GED ürünü değil.
- **K#4** QI = B11²/(B10·B12) **oran-tabanlı** → DOS başarısızsa Plan B = `--no-dos` ile L1T radiance.
- **K#6** `final_confidence = raw_prob × QI_norm × (1 − CI_norm)` (T4.12 CRITICAL PATH).
- **K#13** S2 albedo Liang 2001 katsayıları aynen kodda.
- **K#15** ASTER 90 m → 20 m **bilinear** resample. Nearest YASAK (kodda enforce edilmez,
  fakat sadece `Resampling.bilinear` ile çağrı yapılır).

## fuse_confidence API kontratı (P3 ile saat 17–18 hizalanacak)

```python
def fuse_confidence(
    raw_prob: np.ndarray,            # [0,1] float32, shape (H,W) | (1,H,W) | (H,W,1)
    qi: np.ndarray,                  # native QI raster (~0.5..2.5)
    ci: np.ndarray,                  # native CI raster (~0.95..1.10)
    *,
    qi_norm_kwargs: dict | None = None,
    ci_norm_kwargs: dict | None = None,
) -> np.ndarray:                     # final_confidence float32 [0,1] (H,W)
```

Default normalize: `percentile_minmax_norm(arr, lo_pct=2, hi_pct=98)`.

CLI eşdeğeri:
```
python code/p4/fuse_confidence.py --raw <raw_prob.tif> --qi <qi_20m.tif> --ci <ci_20m.tif> --out <final.tif>
```

## Bekleyen dış girdiler

| Saat | Sağlayıcı | Dosya | T4.x kullanır |
|:-:|:-:|---|---|
| 4   | P1 | S2 ARD 20m (B2,B3,B4,B8,B11,B12) | T4.4 |
| 8   | P1 | DEM 20m | T4.8 |
| 17.5 | P3 | `data/inference/raw_prob.tif` | **T4.12 CRITICAL** |

## Açık riskler

1. **CMR boş dönerse** (T4.2) — `--fallback-url` ile manuel URL gerekir; insanın
   Earthdata Search UI ekrandan vermesi lazım.
2. **GDAL HDF4 driver** — Windows wheel'lerinde sıklıkla yok; Conda zorunlu.
3. **T4.12 saat 20'ye yetişmezse** — Plan B (RAW + ASTER ayrı katman); demo'da kalite düşer,
   orchestrator'a kırmızı sinyal.
4. **QI/CI shape uyumsuzluğu** — T4.6 resample doğru çalışmazsa T4.12 SystemExit raise eder
   ve fuse_confidence Plan B otomatik raw_prob'u geçirir (CLI'da uyarı log'a düşer).

## Sıradaki adımlar

- **Saat 0–1**: T4.1 setup tamamlanır (insan, Earthdata token).
- **Saat 1–3**: T4.2 ASTER indirme asenkron başlar.
- **Saat 3–5**: T4.3 DOS düzeltme (Plan B yedekli).
- **Saat 5–7**: T4.4 S2 indeksleri (P1 ARD geldikten sonra).
- **Saat 7–9**: T4.5 Ninomiya QI/CI/SiO₂.
- **Saat 9–10**: T4.6 20 m resample.
- **Saat 10–12**: T4.7 sentetik füzyon prototipi (sanity).
- **Saat 12–13**: T4.8 DEM aspect/hillshade.
- **Saat 13–15**: HELP→P5 Folium katman desteği.
- **Saat 15–17**: T4.10 layer export + manifest.
- **Saat 17–18**: HELP→P3 `fuse_confidence` API hizalama (kontrat zaten sabit).
- **Saat 18–20**: **T4.12 CRITICAL PATH canlı**.
- **Saat 20–24**: T4.13 KOD FREEZE + dry-run.
