# P4 Layer Manifest

| Katman | Dosya | CRS | Çözünürlük | Aralık | Formül | Referans |
|---|---|---|---|---|---|---|
| S2 NDVI | `s2_ndvi.tif` | EPSG:32636 | 20 m | [-0.2, 0.8] | `(B8 - B4) / (B8 + B4)` | Tucker 1979 |
| S2 BSI (Bare Soil Index) | `s2_bsi.tif` | EPSG:32636 | 20 m | [-0.4, 0.6] | `((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2))` | Rikimaru 2002 |
| S2 Albedo (Liang 2001 shortwave broadband) | `s2_albedo.tif` | EPSG:32636 | 20 m | [0.1, 0.55] | `0.356·B2+0.130·B4+0.373·B8+0.085·B11+0.072·B12 - 0.0018` | Liang 2001 |
| S2 Sabins B11/B12 (clay/carbonate 2.2 µm) | `s2_sabins.tif` | EPSG:32636 | 20 m | [0.7, 2.0] | `B11 / B12` | Sabins 1999 |
| ASTER Quartz Index (Ninomiya) | `aster_qi.tif` | EPSG:32636 | 90 m | [0.5, 2.5] | `B11² / (B10·B12)` | Ninomiya & Fu 2003 |
| ASTER Carbonate Index (Ninomiya) | `aster_ci.tif` | EPSG:32636 | 90 m | [0.95, 1.1] | `B13 / B14` | Ninomiya 1995 |
| ASTER SiO₂% Estimator | `aster_sio2.tif` | EPSG:32636 | 90 m | [40.0, 80.0] | `56.2 + 12.4·log10(QI)` | Ninomiya 2003 (indicative) |
| ASTER QI (20m S2 grid, bilinear) | `aster_qi_20m.tif` | EPSG:32636 | 20 m | [0.5, 2.5] | `B11²/(B10·B12) → bilinear resample` | Ninomiya & Fu 2003 + Karar #15 |
| ASTER CI (20m S2 grid, bilinear) | `aster_ci_20m.tif` | EPSG:32636 | 20 m | [0.95, 1.1] | `B13/B14 → bilinear resample` | Ninomiya 1995 + Karar #15 |
| DEM Aspect (deg) | `dem_aspect.tif` | EPSG:32636 | 20 m | [0, 360] | `gdaldem aspect (Horn 1981)` | Horn 1981 |
| DEM Hillshade (az=315, alt=45) | `dem_hillshade.tif` | EPSG:32636 | 20 m | [0, 255] | `Lambertian; gdaldem hillshade` | Burrough 1986 |
| P3×P4 Final Confidence (FUSED) | `final_confidence.tif` | EPSG:32636 | 20 m | [0.0, 1.0] | `raw_prob × QI_norm × (1 - CI_norm)` | Karar #6 (score-level fusion) |

## Yorum Notları
### S2 NDVI
- Yorum: Düşük NDVI → bare ground; pomza yığınları NDVI < 0.15 olur.
- MD5: `af4dad7d149363e29526b9cd925ccfce`  ·  Boyut: 6.776 MB

### S2 BSI (Bare Soil Index)
- Yorum: Yüksek BSI → çıplak toprak / kaya; pomza saha BSI > 0.15.
- MD5: `061ca74d6f25bc7a157f17015563b440`  ·  Boyut: 6.774 MB

### S2 Albedo (Liang 2001 shortwave broadband)
- Yorum: Pomza yüksek albedo (0.30–0.45 tipik) — açık renk.
- MD5: `ccd6d2bc706025323d970deb0e235ba2`  ·  Boyut: 6.619 MB

### S2 Sabins B11/B12 (clay/carbonate 2.2 µm)
- Yorum: B12 (2.19 µm) clay/carbonate hydroxyl absorption merkezi; B11/B12 yüksek → silikat/aluminoz mineraller (pomza dahil) baskın. Pomza tipik 1.1–1.5.
- MD5: `a2ace4b31a0d160366f210b4cb9856f2`  ·  Boyut: 6.333 MB

### ASTER Quartz Index (Ninomiya)
- Yorum: Pomza saha mean QI > 1.2 (kuvars + felsic glass).
- MD5: `7685114efa38934189e0388288d844cb`  ·  Boyut: 1.666 MB

### ASTER Carbonate Index (Ninomiya)
- Yorum: Yüksek CI → karbonat → pomza olasılığı düşer.
- MD5: `bc7b77ea41be96219b952db466b4f008`  ·  Boyut: 1.599 MB

### ASTER SiO₂% Estimator
- Yorum: Yorum amaçlı — karar girişi DEĞİL (kalibrasyon saha-bazlı).
- MD5: `2ebd933f75f67204905ff8a971b07fb2`  ·  Boyut: 1.508 MB

### ASTER QI (20m S2 grid, bilinear)
- Yorum: P4 fuse_confidence girdisi.
- MD5: `7a068cd5f3dc7169b6f077bd7c8ceee6`  ·  Boyut: 1.22 MB

### ASTER CI (20m S2 grid, bilinear)
- Yorum: P4 fuse_confidence eksi-ağırlık girdisi.
- MD5: `2ade4555b40cfa1756b5ea8cec33215a`  ·  Boyut: 1.17 MB

### DEM Aspect (deg)
- Yorum: Yüzey yön açısı; saha-eğimi cross-reference.
- MD5: `ccfbfba179a7236f1d4cbabe58aeabb4`  ·  Boyut: 5.187 MB

### DEM Hillshade (az=315, alt=45)
- Yorum: Görsel altlık.
- MD5: `49765951c6092e675d888467028853cb`  ·  Boyut: 0.868 MB

### P3×P4 Final Confidence (FUSED)
- Yorum: **P5 T5.13 ana katmanı** — eşik 0.5 üstü pomza adayı.
- MD5: `847f56ad335704e63a7de174b36b29b2`  ·  Boyut: 1.463 MB
