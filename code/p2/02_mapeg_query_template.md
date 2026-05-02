# T2.2 — MAPEG ÇED + Nevşehir İl Çevre Durum Raporu 2014 Sorgu Şablonu

> **Görev sahibi:** P2 — Etiketleme Lead
> **Süre:** ~2 saat (saat 1–3)
> **Öncül:** T2.1 (QGIS hazır)
> **Çıktı:** `data/labels/uretici_saha_listesi.csv` — 30–40 doğrulanmış pomza sahası
> **Akademik referans:** [K#11] — MAPEG ÇED + Nevşehir İl Çevre Durum Raporu 2014

---

## 1. Kaynaklar (Birincil)

### 1a. MAPEG (Maden ve Petrol İşleri Genel Müdürlüğü) ÇED Sorgu
- **Ana URL:** https://www.mapeg.gov.tr/
- **ÇED Karar Sorgu (T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı):** https://eced.csb.gov.tr/ced/jsp/ek1/3
- **MAPEG Maden Ruhsat Sorgu (e-Maden):** https://e-maden.mapeg.gov.tr/

### 1b. Nevşehir İl Çevre Durum Raporu 2014
- **PDF:** Çevre, Şehircilik ve İklim Değişikliği Bakanlığı il çevre durum raporları arşivi → "Nevşehir İl Çevre Durum Raporu 2014"
- **Aranacak URL:** https://webdosya.csb.gov.tr/db/ced/icerikler/nevsehir_2014_icdr-20151230152325.pdf (geçerli değilse: https://ced.csb.gov.tr/ → İl Raporları → Nevşehir → 2014)
- **İlgili bölüm:** "B.1 Madencilik Faaliyetleri" / "B.1.2 Pomza" → Avanos İlçesi pomza ruhsatları tablosu

### 1c. Tamamlayıcı Kaynaklar (Çapraz Doğrulama)
- **Avanos Belediyesi Mücavir Alan Haritası:** https://www.avanos.bel.tr/ → İmar / Mücavir Alan
- **OSM Overpass:** `landuse=quarry AND material=pumice` Avanos AOI içinde
- **Google Earth Pro Historical Imagery:** 2014 vs 2025 karşılaştırması (sahanın hâlâ aktif mi)

---

## 2. Arama Kriterleri

### MAPEG ÇED Sorgu Form Alanları
```
İl: NEVŞEHİR
İlçe: AVANOS
Sektör: Madencilik
Faaliyet türü: Pomza (Pümis Taşı / Bims) Ocağı
ÇED süreci: ÇED Olumlu, ÇED Gerekli Değil, ÇED Süreci Devam (hepsi alın)
Tarih aralığı: 2010-01-01 → 2026-01-01
```

### Nevşehir İl Çevre Raporu 2014 Manuel Tarama
PDF'i Ctrl+F ile **şu anahtar kelimelerle** ara:
- `Avanos`
- `pomza`
- `bims`
- `pümis`
- `IV. Grup`
- `ruhsat`
- `işletme izni`

Tablolarda şu kolonlar olmalı:
| MAPEG Ruhsat No | Üretici / Firma | Köy/Mevki | Ruhsat Alanı (ha) | Durum | İşletme Yılı |

---

## 3. Çıktı Tablo Şeması — `uretici_saha_listesi.csv`

```csv
saha_id,mapeg_ruhsat_no,uretici,firma_tipi,koy_mevki,kaynak,durum,ruhsat_alani_ha,baslangic_yili,notlar
S001,IR-067845,Acme Pomza Madencilik A.Ş.,A.Ş.,Çalış Köyü,MAPEG ÇED 2018,Aktif,12.5,2018,ÇED Olumlu
S002,IR-072901,Avanos Pomza Ltd.,Ltd.,Bahçelievler,Nevşehir 2014 Tablo B.1.7,Aktif,8.3,2012,Ruhsat yenilendi 2022
...
```

### Alan Açıklamaları
| Alan | Tip | Açıklama |
|---|---|---|
| `saha_id` | str | Otomatik artan, `S001`–`S040` |
| `mapeg_ruhsat_no` | str | MAPEG ruhsat numarası (varsa), `IR-XXXXXX` formatı |
| `uretici` | str | Şirket veya kişi adı |
| `firma_tipi` | str | A.Ş. / Ltd. / Şahıs / Belediye |
| `koy_mevki` | str | Köy ve mevki adı (Avanos ilçesi içi) |
| `kaynak` | str | "MAPEG ÇED YYYY" / "Nevşehir 2014 Tablo X" / "OSM" / "Saha tespiti" |
| `durum` | str | `Aktif` / `Pasif` / `Terkedilmiş` / `Belirsiz` |
| `ruhsat_alani_ha` | float | Ruhsat alanı (hektar), bilinmiyorsa boş |
| `baslangic_yili` | int | İşletme başlangıç yılı |
| `notlar` | str | Ek bilgi (ÇED durumu, çevre ihlal kayıtları, vb.) |

---

## 4. QGIS Attribute Schema (T2.3 Manuel Poligon İçin Bağlantı)

`uretici_saha_listesi.csv` → QGIS'te **Layer → Add Layer → Add Delimited Text Layer** ile yüklenir, sonra T2.3'te çizilen poligonlara `saha_id` ile **JOIN** edilir.

Bu sayede her poligon `mapeg_ruhsat_no`, `uretici`, `durum` bilgisini kalıtım yoluyla alır.

---

## 5. Sorgu Akışı (Adım Adım)

### Adım 1: MAPEG ÇED (45 dk)
1. https://eced.csb.gov.tr/ced/jsp/ek1/3 aç.
2. Filtreleri uygula: İl=Nevşehir, İlçe=Avanos, Sektör=Madencilik.
3. Sonuçları taraflar listesinden CSV'ye dök (sayfa kaynağından kopyala-yapıştır gerekebilir).
4. Her ÇED kararının PDF dosyasını kontrol et — koordinat veya parsel bilgisi varsa not düş.

### Adım 2: Nevşehir İl Çevre Raporu 2014 PDF (45 dk)
1. PDF'i indir, açık-erişim arşivinden.
2. Bölüm B.1 Madencilik tablolarını bul.
3. Avanos satırlarını CSV'ye aktar.
4. **MAPEG sonuçları ile çapraz doğrula** — aynı ruhsat numarası iki kaynakta da varsa güven artar (`kaynak=MAPEG+Nevşehir2014`).

### Adım 3: OSM ve Saha Doğrulama (30 dk)
1. QGIS QuickOSM eklentisi ile Avanos AOI içinde `landuse=quarry` çek.
2. Pomza dışı taş ocaklarını ele (granit, mermer, vb. — `material` etiketi varsa).
3. MAPEG/Nevşehir listesinde olmayan ama OSM'de görünen sahaları **manuel doğrulama listesi**ne ekle (Google Earth Pro ile pomza renk imzasını kontrol et).

### Adım 4: Kaynaştırma ve Final Liste (15 dk)
1. 3 kaynaktan gelen sahaları birleştir.
2. Tekrarları (aynı `mapeg_ruhsat_no` veya aynı koy_mevki) merge et.
3. **Hedef: 35 ± 5 saha.** Az ise `durum=Belirsiz` olanları dahil et; çok ise `durum=Pasif/Terkedilmiş` olanları sona at.

---

## 6. VERIFY

```
✓ uretici_saha_listesi.csv satır sayısı: 30–40
✓ saha_id unique
✓ kaynak alanı boş değil (her saha en az 1 kaynaktan teyitli)
✓ koy_mevki Avanos ilçesi sınırları içinde (AOI shapefile ile kontrol)
✓ durum dağılımı: Aktif ≥ 25, Pasif/Terkedilmiş ≤ 15
```

---

## 7. Plan B

- **MAPEG portalı çalışmıyor:** Wayback Machine üzerinden cache kontrol (https://web.archive.org/web/2024*/eced.csb.gov.tr).
- **Nevşehir 2014 PDF erişilemiyor:** 2015 veya 2016 raporu da uygun (yıllar arası tablolar tekrarlı).
- **Yetersiz saha (< 30):** P5'in WDPA + OSM cross-check kanalından 5 saha daha eklenebilir; orchestrator onayı ile.

---

*T2.2 tamamlandığında P2 T2.3'e geçer (manuel poligon, 4 saat).*
