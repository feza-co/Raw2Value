# P2 — Etiketleme Lead Durum Raporu

> Tarih: 2026-05-01
> Modül: A (v2 — Akademik Hizalama)
> Sahip: P2 — Etiketleme Lead
> Kaynak: `Modul_A_Critical_Path_Dependency_v2.md` § P2

---

## 1. Hazır Çıktılar (Saat 0 — Hazırlık Aşaması)

### Şablonlar / Dokümanlar (`code/p2/`)
| Dosya | İçerik | Görev |
|---|---|---|
| `01_qgis_setup.md` | QGIS LTR 3.34 kurulum + EPSG:32636 + S2 RGB altlık + Esri yedek | T2.1 |
| `02_mapeg_query_template.md` | MAPEG ÇED + Nevşehir 2014 + OSM cross-check sorgu şablonu, CSV schema | T2.2 |
| `03_polygon_template.gpkg.md` | Manuel poligon attribute schema (12 alan), çizim protokolü, kalite kriterleri | T2.3 |

### Python Scriptleri (`code/p2/`)
| Dosya | İşlev | Görev |
|---|---|---|
| `04_pixel_sampling.py` | Pozitif piksel örneklemesi (saha başına ~300, stratified random within polygon) | T2.4 |
| `05_negative_sampling.py` | Negatif piksel örneklemesi (2 km buffer dışı, ~6000 piksel, AOI içi) | T2.5 |
| `06_wdpa_ignore_mask.py` | WDPA Göreme + 1000 m buffer + ignore_mask.tif (uint8, 255=ignore) | T2.6 |
| `07_spatial_block_cv.py` | Roberts 2017 spatial 5-fold blok CV, verde + manuel grid fallback | T2.7 |
| `08_rasterize_mask.py` | full_mask.tif: pos=1, neg=0, ignore=255 (CRITICAL PATH, saat 13) | T2.8 |
| `09_augmentation.py` | Geometric (flip/rotate) + spektral (brightness/contrast/noise) | T2.9 |
| `requirements.txt` | geopandas, rasterio, shapely, verde, scikit-learn, ... | env |

### RUN-BLOCK Dosyaları (`agent_outputs/`)
| Dosya | Görev | Kritiklik |
|---|---|---|
| `p2_t2_1_runblock.md` | T2.1 QGIS kurulum (1h, manuel) | normal |
| `p2_t2_2_runblock.md` | T2.2 MAPEG sorgu (2h, manuel) | normal |
| `p2_t2_3_runblock.md` | T2.3 manuel poligon (4h, **EN YORUCU**) — her 30 dk check-in | **YÜKSEK** |
| `p2_status.md` | Bu dosya | — |

---

## 2. P2 Yol Haritası — Saat-Saat (v2 § 1.P2)

```
Saat  Görev                                        Durum    Notlar
----  -------------------------------------------  -------  -------------------------------
0-1   T2.1 QGIS kurulum                            ⏳ HAZ   şablon hazır → kullanıcı manuel
1-3   T2.2 MAPEG ÇED + Nevşehir 2014 sorgu        ⏳ HAZ   şablon + CSV schema hazır
3-7   T2.3 Manuel pozitif poligon (30-40 saha)    ⏳ HAZ   schema + check-in protokolü hazır
                                                            ★ EN YORUCU GÖREV ★
7-8   T2.4 Pozitif piksel örnekleme (~10K)        ⏳ HAZ   04_pixel_sampling.py — auto run
8-9   T2.5 Negatif örnekleme (2km buffer dışı)    ⏳ HAZ   05_negative_sampling.py — auto run
9-10  T2.6 WDPA buffer + ignore_mask              ⏳ HAZ   06_wdpa_ignore_mask.py — auto run
10-11 T2.7 Spatial 5-fold blok CV (Roberts 2017)  ⏳ HAZ   07_spatial_block_cv.py — auto run
11-13 T2.8 Raster mask → Full label               ⏳ HAZ   08_rasterize_mask.py — CRITICAL
                                                            ★ T3.5 BLOKÇUSU ★
13-14 T2.9 Augmentation pipeline                  ⏳ HAZ   09_augmentation.py — class hazır
14-16 T2.10 P3 DataLoader entegrasyon             —        P3 ile koordinasyon
16-17 T2.11 Etiket QC raporu                      —        sınıf+blok dağılımı
17-18.5 T2.12 P3 inference hata analizi           —        FP/FN tur 2
18.5-20 HELP→P5 KPI doğrulama                     —        slack
18-24 T2.13/T2.14 Entegrasyon + KOD FREEZE        —        son aşama

⏳ HAZ = şablon/script hazır, çalıştırılmaya hazır
```

---

## 3. Bağımlılıklar — Kim → Kim

### P2 Tüketicisi (Bana Bağlı Olanlar)
| Saat | Çıktı | Kime | Görevi |
|---|---|---|---|
| 7 | positive_polygons.gpkg (ön versiyon) | P3 | T3.4 sanity check için |
| 11 | data/labels/blok_cv_split.json | P3 | T3.5 cross-validation |
| 13 | data/labels/full_mask.tif | P3 | T3.5 fine-tune asıl input — **CRITICAL** |
| 14 | augmentation pipeline | P3 | T2.10 DataLoader entegrasyonu |

### P2'nin Sağlayıcıları (Beni Bekleyenler)
| Saat | Girdi | Kimden | Kullanım |
|---|---|---|---|
| 4 | S2 RGB altlık (T1.4) | P1 | T2.3 manuel çizim altlığı (Esri yedek var) |
| 8 | 17-kanal Full ARD (T1.7) | P1 | T2.4-T2.6 raster grid referansı |
| 10 | Tile dosyaları (T1.8) | P1 | T2.7 spatial blok CV input — **T2.8 öncesi şart** |

---

## 4. Risk + Plan B Tetik Noktaları

| Risk | Tetik Saati | Aksiyon |
|---|---|---|
| T2.3 yavaş (saat 4:30'da <9 saha) | 4:30 | Orchestrator'a sinyal → HELP→P2 saat 14'te kesin |
| T2.7 5-fold blok problemli (yetersiz dolu blok) | 11 | Plan B: 3-fold'a düş (--n-folds 3, K#10 metodoloji korunur) |
| T1.8 tile geç (saat 10 sonrası) | 10:30 | T2.7 blok CV beklemede, T2.8 deadline (saat 13) riskte |
| T2.8 critical path slip | 13 | P3 T3.5 fine-tune gecikir → tüm kritik patika kayar |

### Plan B — 5-fold → 3-fold (orchestrator onayı gerekir)
```bash
python code/p2/07_spatial_block_cv.py \
    --n-folds 3 --blocks-x 3 --blocks-y 3 \
    --out data/labels/blok_cv_split.json
```
Akademik gerekçe: Roberts et al. 2017 — blok boyutu domain'e göre ayarlanır, 3-fold istatistiksel güveni hafif düşürür ama metodoloji aynı kalır.

---

## 5. Şu Anda Beklenen Aksiyon

**Kullanıcıya sıradaki adım:**
1. T2.1 RUN-BLOCK'u aç → QGIS kurulumu başlat (saat 0-1)
2. P1'in T1.4 çıktısını paralelde takip et (S2 RGB altlık, saat 4'te gelir)
3. T2.2 MAPEG sorgu için tarayıcı + PDF okuyucu hazırla

**Orchestrator/agent (ben):**
- T2.3 başladığında her 30 dk check-in scheduler aktif edilebilir.
- T1.8 tile manifest geldiğinde T2.4 + T2.7 + T2.8 zincirini script chain ile koştururum.

---

## 6. Çıktı Klasör Yapısı (Beklenen)

```
data/
├── aoi/avanos_aoi.gpkg                    (P1 T1.2)
├── raw/
│   ├── s2_l2a_avanos_rgb.tif              (P1 T1.4)
│   └── wdpa_goreme.gpkg                   (manuel indirme — protectedplanet.net)
├── ard/
│   └── tile_manifest.json                 (P1 T1.9)
├── qgis_projects/
│   └── avanos_etiketleme.qgz              (T2.1)
└── labels/
    ├── uretici_saha_listesi.csv           (T2.2)
    ├── positive_polygons.gpkg             (T2.3) — 30-40 feature
    ├── positive_pixels.gpkg               (T2.4) — ~10K Point
    ├── negative_pixels.gpkg               (T2.5) — ~6K Point
    ├── wdpa_buffer.gpkg                   (T2.6)
    ├── ignore_mask.tif                    (T2.6) — uint8, 255=ignore
    ├── blok_cv_split.json                 (T2.7) — Roberts 2017 5-fold
    └── full_mask.tif                      (T2.8) — uint8 0/1/255  ★ CRITICAL ★
```

---

## 7. Akademik Hizalama Doğrulama

| Karar | Uygulandı mı? | Nerede |
|---|---|---|
| K#8 — Göreme + 1000 m UNESCO buffer | ✓ | `06_wdpa_ignore_mask.py` (WDPA_BUFFER_M=1000) |
| K#10 — Roberts 2017 spatial 5-fold blok CV | ✓ | `07_spatial_block_cv.py` (verde + manuel grid) |
| K#11 — MAPEG ÇED + Nevşehir 2014 sorgu | ✓ | `02_mapeg_query_template.md` |
| K#12 — Negatif örnek 2 km buffer dışı | ✓ | `05_negative_sampling.py` (POSITIVE_BUFFER_M=2000) |
| K#15 — 20m grid, EPSG:32636 | ✓ | tüm scriptler PIXEL_SIZE_M=20, EPSG:32636 |
| WDPA buffer içi = ignore_index (negatif değil) | ✓ | `08_rasterize_mask.py` (IGNORE_VAL=255, mask değer hiyerarşisi) |
| Piksel-bazlı örnekleme (poligon-bazlı değil) | ✓ | T2.4/T2.5 Point geometry, label=0/1 |

---

*Hazır. T2.1-T2.3 kullanıcı yapacak; T2.4-T2.9 script chain otomatik (girdi geldikçe).*
