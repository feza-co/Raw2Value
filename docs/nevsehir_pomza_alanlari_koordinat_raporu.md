# Nevşehir Aktif / Potansiyel Aktif Pomza Alanları Koordinat Raporu

**Proje:** PomzaScope — Kapadokya Hackathon 2026  
**Bölge:** Nevşehir / Kapadokya Pomza Kuşağı  
**Hazırlama Tarihi:** 1 Mayıs 2026  
**Dosya Formatı:** Markdown (`.md`)  
**Amaç:** Nevşehir’de açık kaynaklardan doğrulanabilen aktif, güncel ÇED sürecinde olan veya resmi raporlarda geçmiş üretim kaydı bulunan pomza sahalarının koordinat bazlı ön listesini çıkarmak ve PomzaScope MVP’sinde kullanılabilecek şekilde raporlamak.

---

## İçindekiler

1. [Yönetici Özeti](#1-yönetici-özeti)  
2. [Kapsam ve Kullanım Amacı](#2-kapsam-ve-kullanım-amacı)  
3. [Metodoloji](#3-metodoloji)  
4. [Aktiflik ve Güven Düzeyi Sınıflandırması](#4-aktiflik-ve-güven-düzeyi-sınıflandırması)  
5. [Güncel ÇED / Kapasite Artışı Süreci Görülen Sahalar](#5-güncel-çed--kapasite-artışı-süreci-görülen-sahalar)  
6. [Resmi Raporda Koordinatı Verilen Pomza Sahaları](#6-resmi-raporda-koordinatı-verilen-pomza-sahaları)  
7. [Toplu Koordinat Listesi](#7-toplu-koordinat-listesi)  
8. [CSV Formatında Koordinat Listesi](#8-csv-formatında-koordinat-listesi)  
9. [GeoJSON Taslağı](#9-geojson-taslağı)  
10. [PomzaScope MVP İçin Kullanım Önerisi](#10-pomzascope-mvp-için-kullanım-önerisi)  
11. [Önceliklendirilmiş Saha Listesi](#11-önceliklendirilmiş-saha-listesi)  
12. [Riskler, Sınırlamalar ve Teyit Gerektiren Noktalar](#12-riskler-sınırlamalar-ve-teyit-gerektiren-noktalar)  
13. [Sonuç](#13-sonuç)  
14. [Kaynakça](#14-kaynakça)

---

## 1. Yönetici Özeti

Bu raporda Nevşehir’deki pomza sahaları iki ana güven düzeyinde listelenmiştir:

1. **Güncel ÇED / kapasite artışı kaydı görülen sahalar**  
   Bu sahalar, 2024 ve yakın dönem ÇED duyurularında geçtiği için “güncel aktiflik ihtimali yüksek” kabul edilmiştir.

2. **Resmi İl Çevre Durum Raporu’nda koordinatı, ruhsat bilgisi veya üretim kaydı verilen sahalar**  
   Bu sahalar için koordinatlar resmi raporda UTM koordinatlarıyla verilmiştir. UTM koordinatları WGS84 enlem-boylam sistemine çevrilerek yaklaşık saha merkez noktası şeklinde sunulmuştur.

Nevşehir’de pomza varlığı özellikle şu kuşaklarda yoğunlaşmaktadır:

- **Nevşehir Merkez — Göre Köyü çevresi**
- **Ürgüp — Şahinefendi — Mazı hattı**
- **Avanos — Gülşehir — Acıgöl çevresi**
- **Kaymaklı ve yakın çevresi**
- **Sarıyaprak mevkii ve Göre yolu çevresi**

Bu liste, PomzaScope projesinde pozitif pomza etiketi üretimi, uydu tabanlı change detection, UNESCO buffer kontrolü ve saha önceliklendirme dashboard’u için başlangıç veri seti olarak kullanılabilir.

> **Önemli not:** Bu rapordaki koordinatlar saha merkez noktası / yaklaşık lokasyon niteliğindedir. Hukuki ruhsat sınırı veya kesin maden poligonu değildir. Kesin ruhsat sınırı için MAPEG ruhsat poligonları, ÇED başvuru dosyasındaki köşe koordinatları veya resmi kurum verileri gerekir.

---

## 2. Kapsam ve Kullanım Amacı

Bu raporun kapsamı, Nevşehir’deki pomza sahalarını **koordinat bazlı ön envanter** haline getirmektir.

Bu çalışma özellikle şu amaçlara hizmet eder:

- PomzaScope Modül A için ilk pozitif saha adaylarını belirlemek
- Sentinel-2 / Sentinel-1 / DEM tabanlı modelde manuel etiketleme başlangıç noktaları sağlamak
- QGIS üzerinde ocak sınırı çizimi için referans noktalar üretmek
- Change detection yapılacak eski/yeni saha adaylarını belirlemek
- UNESCO / Göreme Milli Parkı buffer overlay analizi için riskli yakınlıkları kontrol etmek
- Demo dashboard’da gösterilecek gerçekçi saha örneklerini seçmek

Bu raporun kapsamı dışında kalan konular:

- Kesin MAPEG ruhsat poligonu üretimi
- Hukuki ruhsat sınırı teyidi
- Saha mülkiyet durumu
- Ocak işletme izin tarihleri ve güncel üretim miktarlarının resmi teyidi
- Pomza kalite sınıflandırması
- Sahaya gidilerek yapılan fiziksel doğrulama

---

## 3. Metodoloji

Bu raporda kullanılan yöntem aşağıdaki adımlardan oluşur:

### 3.1 Kaynak Tarama

Aşağıdaki açık kaynak türleri kullanılmıştır:

- Nevşehir Çevre, Şehircilik ve İklim Değişikliği İl Müdürlüğü ÇED duyuruları
- Nevşehir İl Çevre Durum Raporu
- AHİKA Pomza Araştırma ve Uygulama Merkezi Fizibilite Raporu
- PomzaScope proje içi araştırma raporu
- PomzaScope Modül A development rol dağıtımı dokümanı
- Kamuya açık haber / duyuru kaynakları

### 3.2 Koordinat Çıkarma

Koordinatlar üç şekilde üretilmiştir:

1. **ÇED duyurusunda sadece mevki adı geçen sahalar:**  
   Mevki veya köy merkezine göre yaklaşık koordinat verilmiştir.

2. **İki yerleşim arasında tanımlanan sahalar:**  
   İki yerleşim noktası arasında temsilî orta nokta verilmiştir.

3. **Resmi raporda UTM koordinatı verilen sahalar:**  
   UTM koordinatları WGS84 enlem-boylam sistemine çevrilmiş ve yaklaşık saha merkez noktası olarak listelenmiştir.

### 3.3 Güven Düzeyi Atama

Her saha için aşağıdaki güven notları kullanılmıştır:

- **A:** Güncel ÇED / kapasite artışı / aktiflik göstergesi güçlü
- **A-:** Güncel süreç var ancak koordinat yaklaşık veya temsilî
- **B+:** Resmi geçmiş üretim kaydı var ve güncel kaynaklarla kısmen destekleniyor
- **B:** Resmi geçmiş üretim / ruhsat / kapasite kaydı var; güncel aktiflik ayrıca teyit edilmeli
- **B-:** Geçmiş faaliyet dönemi var; son durum belirsiz
- **C:** Potansiyel saha / ruhsatlı alan; üretim veya güncel aktiflik zayıf / belirsiz

---

## 4. Aktiflik ve Güven Düzeyi Sınıflandırması

| Aktiflik Seviyesi | Açıklama | Kullanım Önerisi |
|---|---|---|
| **A — Güncel aktif / yüksek güven** | Son yıllarda ÇED süreci, kapasite artışı veya halkın katılımı ilanı bulunan saha | Demo ve saha önceliklendirme için en güçlü aday |
| **A- — Güncel süreç var, koordinat yaklaşık** | Güncel ÇED/kapasite izi var ancak koordinat mevki veya temsilî orta nokta | Uydu görüntüsüyle manuel doğrulama yapılmalı |
| **B+ — Geçmiş üretim + ek aktiflik sinyali** | Resmi raporda üretim kaydı var, ayrıca başka güncel kayıtlarla destekleniyor | Model pozitif etiketi için iyi aday |
| **B — Resmi üretim kaydı var / güncel teyit gerekli** | Resmi raporda üretim ve ruhsat bilgisi var; bugünkü aktiflik ayrıca kontrol edilmeli | Change detection ve Sentinel-2 kontrolü yapılmalı |
| **B- — Faaliyet dönemi geçmişte kalmış olabilir** | Faaliyet dönemi belirtilmiş ancak güncel statü belirsiz | Yedek aday olarak tutulmalı |
| **C — Potansiyel / düşük güven** | Mevki, ruhsat veya kapasite bilgisi var ama üretim veya aktiflik net değil | Öncelik düşük; manuel harita kontrolü gerekir |

---

## 5. Güncel ÇED / Kapasite Artışı Süreci Görülen Sahalar

Aşağıdaki sahalar, güncel veya yakın dönem ÇED / kapasite artışı duyuruları nedeniyle aktiflik ihtimali en yüksek olan sahalardır.

| No | Saha / Firma | İlçe / Mevki | Ruhsat / Proje Bilgisi | Koordinat | Aktiflik Notu | Güven |
|---:|---|---|---|---|---|---|
| 1 | **Fırat Madencilik** | Nevşehir Merkez / Göre Köyü | İR:4363 Pomza Taşı Ocağı Kapasite Artışı ve Yıkama-Eleme Tesisi | **38.584923, 34.720928** | ÇED süreci başlamış güncel kapasite artışı projesi | A |
| 2 | **Hüseyin Oyman** | Ürgüp / Şahinefendi — Mazı arası | Ruhsat No: 200709055 / Erişim No: 3149968 / IV-A Grup Pomza Ocağı Kapasite Artışı | **38.469950, 34.892810** | 2024 halkın katılımı / kapasite artışı ilanı görülen saha; koordinat temsilî orta nokta | A- |

### 5.1 Fırat Madencilik — Göre Köyü

- **Firma:** Fırat Madencilik
- **Ruhsat:** İR:4363
- **Proje:** Pomza Taşı Ocağı Kapasite Artışı ve Yıkama-Eleme Tesisi
- **Konum:** Nevşehir Merkez, Göre Köyü mevkii
- **Koordinat:** `38.584923, 34.720928`
- **Değerlendirme:** Güncel ÇED süreci görüldüğü için PomzaScope demo’sunda birincil saha adayıdır.

### 5.2 Hüseyin Oyman — Şahinefendi / Mazı Hattı

- **Firma / Kişi:** Hüseyin Oyman
- **Ruhsat:** 200709055 / Erişim No: 3149968
- **Proje:** IV-A Grup Pomza Ocağı Kapasite Artışı
- **Konum:** Ürgüp, Şahinefendi Köyü ile Mazı Köyü çevresi
- **Koordinat:** `38.469950, 34.892810`
- **Değerlendirme:** Koordinat temsilî orta nokta olduğu için Sentinel-2 / Google Earth / QGIS üzerinden ocak sınırı ayrıca doğrulanmalıdır.

---

## 6. Resmi Raporda Koordinatı Verilen Pomza Sahaları

Aşağıdaki koordinatlar, Nevşehir İl Çevre Durum Raporu’ndaki UTM koordinatlarının WGS84 sistemine çevrilmesiyle elde edilen yaklaşık merkez noktalarıdır.

| No | Firma / Ruhsat | Faaliyet Türü | Kapasite / Alan Bilgisi | Yaklaşık Merkez Koordinatı | Aktiflik Notu | Güven |
|---:|---|---|---|---|---|---|
| 1 | **Metin Sertkaya — İR:20063271** | 4. Grup Pomza Ocağı | 30.000 ton/yıl; izin alanı 122,66 ha; ruhsat alanı 567,89 ha | **38.496806, 34.824545** | 2014 resmi üretim kaydı var; güncel aktiflik teyit edilmeli | B |
| 2 | **Elit Bims — İR:20051226** | 4. Grup Pomza Taşı Ocağı | 15.000 ton/yıl; 23,95 ha | **38.488288, 34.912612** | 2014 resmi üretim kaydı var; güncel aktiflik teyit edilmeli | B |
| 3 | **Hüseyin Oyman — İR:2601** | 4. Grup Pomza Ocağı | 76.205 ton/yıl; 79,60 ha | **38.545056, 34.824968** | 2014 resmi üretim kaydı var; farklı ruhsat/proje ile güncel ÇED izi de bulunuyor | B+ |
| 4 | **Öz-SA Madencilik — İR:5402** | 4. Grup Pomza / Bims Ocağı | 50.000 ton/yıl; 24,62 ha | **38.597449, 34.703774** | 2014 resmi üretim kaydı var; güncel aktiflik teyit edilmeli | B |
| 5 | **İnci Madencilik — Ruhsat No:12085** | 4. Grup Pomza | 45.000 ton/yıl | **38.460562, 34.837528** | Raporda 2014 yılında üretim gerçekleşmediği belirtilmiş; potansiyel/ruhsatlı saha | C |
| 6 | **Serhat Madencilik — Ruhsat No:9774** | 4. Grup Pomza | 60.000 ton/yıl | **38.548220, 34.705544** | Resmi koordinat ve kapasite var; güncel aktiflik teyit edilmeli | B |
| 7 | **ANC Madencilik — İR:3654** | Madencilik / Pomza | Alan bilgisi raporda verilmiş; faaliyet süreci 2013–2023 olarak geçiyor | **38.522847, 34.823008** | Faaliyetin devam edeceği belirtilmiş; 2023 sonrası güncel teyit gerekli | B- |

### 6.1 Metin Sertkaya — İR:20063271

- **Faaliyet:** 4. Grup Pomza Ocağı
- **Kapasite:** 30.000 ton/yıl
- **İzin alanı:** 122,66 ha
- **Ruhsat alanı:** 567,89 ha
- **Koordinat:** `38.496806, 34.824545`
- **PomzaScope yorumu:** Büyük ruhsat/izin alanı nedeniyle change detection ve maden genişleme analizi için güçlü adaydır.

### 6.2 Elit Bims — İR:20051226

- **Faaliyet:** 4. Grup Pomza Taşı Ocağı
- **Kapasite:** 15.000 ton/yıl
- **Alan:** 23,95 ha
- **Koordinat:** `38.488288, 34.912612`
- **PomzaScope yorumu:** Koordinatı net ve pomza faaliyeti açıkça geçtiği için manuel pozitif poligon çiziminde kullanılabilir.

### 6.3 Hüseyin Oyman — İR:2601

- **Faaliyet:** 4. Grup Pomza Ocağı
- **Kapasite:** 76.205 ton/yıl
- **Alan:** 79,60 ha
- **Koordinat:** `38.545056, 34.824968`
- **PomzaScope yorumu:** Hem geçmiş üretim kaydı hem de farklı güncel ÇED izi nedeniyle yüksek öncelikli saha adayıdır.

### 6.4 Öz-SA Madencilik — İR:5402

- **Faaliyet:** 4. Grup Pomza / Bims Ocağı
- **Kapasite:** 50.000 ton/yıl
- **Alan:** 24,62 ha
- **Koordinat:** `38.597449, 34.703774`
- **PomzaScope yorumu:** Göre / Sarıyaprak çevresi için modelin pozitif pomza öğrenmesini güçlendirebilir.

### 6.5 İnci Madencilik — Ruhsat No:12085

- **Faaliyet:** 4. Grup Pomza
- **Kapasite:** 45.000 ton/yıl
- **Koordinat:** `38.460562, 34.837528`
- **PomzaScope yorumu:** Raporda üretim olmadığı notu bulunduğu için aktif saha olarak değil, potansiyel ruhsatlı alan olarak değerlendirilmelidir.

### 6.6 Serhat Madencilik — Ruhsat No:9774

- **Faaliyet:** 4. Grup Pomza
- **Kapasite:** 60.000 ton/yıl
- **Koordinat:** `38.548220, 34.705544`
- **PomzaScope yorumu:** Koordinat ve kapasite bilgisi olduğu için uydu görüntüsüyle güncel yüzey açıklığı kontrol edilmelidir.

### 6.7 ANC Madencilik — İR:3654

- **Faaliyet:** Pomza / madencilik sahası
- **Faaliyet süreci:** Raporda 2013–2023 dönemi belirtilmiştir.
- **Koordinat:** `38.522847, 34.823008`
- **PomzaScope yorumu:** 2023 sonrası güncel aktifliği belirsizdir; Landsat / Sentinel zaman serisiyle saha değişimi kontrol edilmelidir.

---

## 7. Toplu Koordinat Listesi

| No | Saha | Enlem | Boylam | Durum | Güven |
|---:|---|---:|---:|---|---|
| 1 | Fırat Madencilik İR:4363 Göre Köyü | 38.584923 | 34.720928 | Güncel ÇED süreci | A |
| 2 | Hüseyin Oyman Şahinefendi-Mazı temsilî nokta | 38.469950 | 34.892810 | Güncel kapasite artışı ilanı | A- |
| 3 | Metin Sertkaya İR:20063271 | 38.496806 | 34.824545 | 2014 resmi üretim kaydı; güncel teyit gerekli | B |
| 4 | Elit Bims İR:20051226 | 38.488288 | 34.912612 | 2014 resmi üretim kaydı; güncel teyit gerekli | B |
| 5 | Hüseyin Oyman İR:2601 | 38.545056 | 34.824968 | 2014 resmi üretim kaydı; güncel teyit gerekli | B+ |
| 6 | Öz-SA Madencilik İR:5402 | 38.597449 | 34.703774 | 2014 resmi üretim kaydı; güncel teyit gerekli | B |
| 7 | İnci Madencilik Ruhsat 12085 | 38.460562 | 34.837528 | 2014 üretim yok; potansiyel ruhsatlı saha | C |
| 8 | Serhat Madencilik Ruhsat 9774 | 38.548220 | 34.705544 | Resmi koordinat ve kapasite var; güncel teyit gerekli | B |
| 9 | ANC Madencilik İR:3654 | 38.522847 | 34.823008 | 2013–2023 faaliyet dönemi; güncel teyit gerekli | B- |

---

## 8. CSV Formatında Koordinat Listesi

Bu blok doğrudan `.csv` dosyasına kaydedilip QGIS, Google Earth veya Python içinde kullanılabilir.

```csv
name,latitude,longitude,status,confidence
Fırat Madencilik İR:4363 Göre Köyü,38.584923,34.720928,Güncel ÇED süreci,A
Hüseyin Oyman Şahinefendi-Mazı temsilî nokta,38.469950,34.892810,Güncel kapasite artışı ilanı,A-
Metin Sertkaya İR:20063271,38.496806,34.824545,2014 resmi üretim kaydı; güncel teyit gerekli,B
Elit Bims İR:20051226,38.488288,34.912612,2014 resmi üretim kaydı; güncel teyit gerekli,B
Hüseyin Oyman İR:2601,38.545056,34.824968,2014 resmi üretim kaydı; güncel teyit gerekli,B+
Öz-SA Madencilik İR:5402,38.597449,34.703774,2014 resmi üretim kaydı; güncel teyit gerekli,B
İnci Madencilik Ruhsat 12085,38.460562,34.837528,2014 üretim yok; potansiyel ruhsatlı saha,C
Serhat Madencilik Ruhsat 9774,38.548220,34.705544,Resmi koordinat ve kapasite var; güncel teyit gerekli,B
ANC Madencilik İR:3654,38.522847,34.823008,2013-2023 faaliyet dönemi; güncel teyit gerekli,B-
```

---

## 9. GeoJSON Taslağı

Bu GeoJSON taslağı QGIS veya web harita katmanı için başlangıç noktası olarak kullanılabilir. Noktalar kesin saha poligonu değildir; yalnızca yaklaşık merkez / temsilî lokasyondur.

```json
{
  "type": "FeatureCollection",
  "name": "nevsehir_pomza_saha_noktalari",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Fırat Madencilik İR:4363 Göre Köyü",
        "status": "Güncel ÇED süreci",
        "confidence": "A"
      },
      "geometry": {"type": "Point", "coordinates": [34.720928, 38.584923]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Hüseyin Oyman Şahinefendi-Mazı temsilî nokta",
        "status": "Güncel kapasite artışı ilanı",
        "confidence": "A-"
      },
      "geometry": {"type": "Point", "coordinates": [34.892810, 38.469950]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Metin Sertkaya İR:20063271",
        "status": "2014 resmi üretim kaydı; güncel teyit gerekli",
        "confidence": "B"
      },
      "geometry": {"type": "Point", "coordinates": [34.824545, 38.496806]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Elit Bims İR:20051226",
        "status": "2014 resmi üretim kaydı; güncel teyit gerekli",
        "confidence": "B"
      },
      "geometry": {"type": "Point", "coordinates": [34.912612, 38.488288]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Hüseyin Oyman İR:2601",
        "status": "2014 resmi üretim kaydı; güncel teyit gerekli",
        "confidence": "B+"
      },
      "geometry": {"type": "Point", "coordinates": [34.824968, 38.545056]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Öz-SA Madencilik İR:5402",
        "status": "2014 resmi üretim kaydı; güncel teyit gerekli",
        "confidence": "B"
      },
      "geometry": {"type": "Point", "coordinates": [34.703774, 38.597449]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "İnci Madencilik Ruhsat 12085",
        "status": "2014 üretim yok; potansiyel ruhsatlı saha",
        "confidence": "C"
      },
      "geometry": {"type": "Point", "coordinates": [34.837528, 38.460562]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "Serhat Madencilik Ruhsat 9774",
        "status": "Resmi koordinat ve kapasite var; güncel teyit gerekli",
        "confidence": "B"
      },
      "geometry": {"type": "Point", "coordinates": [34.705544, 38.548220]}
    },
    {
      "type": "Feature",
      "properties": {
        "name": "ANC Madencilik İR:3654",
        "status": "2013-2023 faaliyet dönemi; güncel teyit gerekli",
        "confidence": "B-"
      },
      "geometry": {"type": "Point", "coordinates": [34.823008, 38.522847]}
    }
  ]
}
```

---

## 10. PomzaScope MVP İçin Kullanım Önerisi

Bu koordinatlar PomzaScope MVP’sinde aşağıdaki teknik iş akışlarında kullanılabilir.

### 10.1 Pozitif Etiket Başlangıç Noktası

Bu sahalar, Sentinel-2 / Sentinel-1 / DEM tabanlı modelde **pozitif pomza etiketi** üretmek için başlangıç noktası olabilir.

Ancak doğrudan nokta koordinatı model eğitimi için yeterli değildir. Bunun yerine QGIS üzerinde şu işlem yapılmalıdır:

1. Koordinat noktası haritaya eklenir.
2. Sentinel-2 RGB / SWIR / Google Earth görüntüsü açılır.
3. Açık ocak sınırı manuel poligon olarak çizilir.
4. Poligon `positive_polygons.geojson` dosyasına eklenir.
5. Saha çevresinde yanlış pozitif oluşturabilecek yüzeyler ayrıca negatif örnek olarak etiketlenir.

### 10.2 Change Detection Kontrolü

Özellikle **2014 üretim kaydı olan ama güncel aktifliği belirsiz** sahalarda Sentinel-2 ve Landsat zaman serisi ile açık ocak genişlemesi kontrol edilebilir.

Önerilen kontrol yılları:

- 2015
- 2020
- 2023
- 2025
- 2026

Önerilen layer’lar:

- Sentinel-2 RGB
- Sentinel-2 SWIR composite
- BSI — Bare Soil Index
- NDVI
- Sentinel-1 amplitude difference
- Landsat historical snapshots

### 10.3 UNESCO / Koruma Alanı Risk Katmanı

PomzaScope Modül A’da UNESCO buffer overlay katmanı bulunduğu için bu koordinatlar Göreme Milli Parkı ve çevresindeki hassas alanlara uzaklık analizi için kullanılabilir.

Önerilen yaklaşım:

1. WDPA veya OSM üzerinden Göreme Milli Parkı polygon’u alınır.
2. 1000 m buffer oluşturulur.
3. Pomza koordinatları bu buffer ile kesiştirir.
4. Buffer içinde veya çok yakınında kalan sahalar “red flag” olarak işaretlenir.
5. Sonuç `red_flag_alerts.json` ve harita overlay katmanı olarak dashboard’a eklenir.

### 10.4 Model Geliştirme İçin Veri Ayrımı

Bu sahalar modelde şu şekilde kullanılabilir:

| Veri Türü | Kullanım |
|---|---|
| Güncel ÇED sahaları | Pozitif etiket için öncelikli |
| Resmi üretim kaydı olan sahalar | Pozitif veya change detection kontrol sahası |
| Üretim olmadığı belirtilen ruhsatlı sahalar | Dikkatli kullanılmalı; doğrudan pozitif sayılmamalı |
| UNESCO buffer içi / yakınındaki alanlar | Etiket dışı veya risk overlay |
| Tarım, yerleşim, tüf yüzeyi, yol, su | Negatif örnek |

---

## 11. Önceliklendirilmiş Saha Listesi

| Öncelik | Saha | Neden Öncelikli? | Önerilen İşlem |
|---:|---|---|---|
| 1 | **Fırat Madencilik — Göre Köyü** | Güncel ÇED süreci var; demo için güçlü saha | İlk manuel poligon burada çizilmeli |
| 2 | **Hüseyin Oyman — Ürgüp / Şahinefendi-Mazı** | Güncel kapasite artışı izi var; Ürgüp hattı stratejik | Uydu görüntüsüyle saha merkezi netleştirilmeli |
| 3 | **Hüseyin Oyman — İR:2601** | Resmi üretim kaydı yüksek; koordinat net | Pozitif etiket ve change detection için kullanılmalı |
| 4 | **Elit Bims — İR:20051226** | Pomza üretim kaydı ve koordinat net | Pozitif örnek adayı |
| 5 | **Serhat Madencilik — Ruhsat 9774** | Pomza ruhsatı ve kapasite bilgisi var | Sentinel-2 ile güncel açıklık kontrolü yapılmalı |
| 6 | **Öz-SA Madencilik — Sarıyaprak mevkii** | Üretim kaydı var; farklı lokasyon çeşitliliği sağlar | Pozitif örnek / saha çeşitliliği için kullanılmalı |
| 7 | **ANC Madencilik — İR:3654** | Büyük saha / geçmiş faaliyet süreci var | 2023 sonrası güncel durum change detection ile kontrol edilmeli |
| 8 | **Metin Sertkaya — İR:20063271** | Geniş ruhsat/izin alanı var | Büyük saha analizi için yedek aday |
| 9 | **İnci Madencilik — Ruhsat 12085** | Üretim olmadığı belirtilmiş | Pozitif yerine potansiyel/karşılaştırma sahası olarak tutulmalı |

---

## 12. Riskler, Sınırlamalar ve Teyit Gerektiren Noktalar

### 12.1 MAPEG Ruhsat Poligonu Eksikliği

MAPEG ruhsat poligonları açık kaynakta tam ve toplu şekilde doğrulanamamıştır. Bu nedenle rapordaki noktalar hukuki ruhsat sınırı değildir.

**Mitigasyon:**

- MAPEG e-Maden üzerinden tekil ruhsat sorgusu yapılmalı.
- ÇED başvuru dosyalarındaki koordinat tabloları aranmalı.
- QGIS üzerinde manuel ocak sınırı çizilmeli.

### 12.2 Güncel Aktiflik Belirsizliği

2014 raporundaki üretim bilgileri bugünkü aktiflik anlamına gelmez. Bir saha geçmişte üretim yapmış olabilir ama bugün kapanmış, pasifleşmiş veya rehabilitasyona girmiş olabilir.

**Mitigasyon:**

- Sentinel-2 2023–2026 görüntüleri kontrol edilmeli.
- Landsat uzun dönem değişim analizi yapılmalı.
- Firma web siteleri ve güncel ÇED duyuruları tekrar kontrol edilmeli.

### 12.3 Temsilî Koordinat Riski

Bazı sahalarda ÇED duyurusu yalnızca köy / mevki adı verdiği için koordinat temsilîdir.

**Mitigasyon:**

- Noktanın çevresinde 2–5 km çapında görsel uydu taraması yapılmalı.
- Açık ocak yüzeyleri SWIR ve RGB composite ile ayrıştırılmalı.

### 12.4 Model Etiketi İçin Nokta Verinin Yetersizliği

Tek nokta koordinatı, segmentation modeli için yeterli değildir.

**Mitigasyon:**

- Her noktanın çevresinde manuel poligon çizilmeli.
- Pozitif ve negatif örnekler dengelenmeli.
- UNESCO ve hassas alanlar etiket dışı bırakılmalı.

### 12.5 Pomza / Tüf / Açık Kayaç Karışma Riski

Kapadokya’da pomza, tüf, çıplak açık kayaç ve volkanik yüzeyler spektral olarak karışabilir.

**Mitigasyon:**

- NDVI ile bitki dışlanmalı.
- BSI ile çıplak yüzey ayrılmalı.
- Albedo ve SWIR oranları kullanılmalı.
- Yanlış pozitifleri azaltmak için negatif örneklerde Göreme/Zelve tüf yüzeyleri kullanılmalı.

---

## 13. Sonuç

Nevşehir’de PomzaScope MVP’si için ilk aşamada kullanılabilecek en güçlü saha adayları şunlardır:

1. **Fırat Madencilik — Göre Köyü**
2. **Hüseyin Oyman — Ürgüp / Şahinefendi-Mazı hattı**
3. **Hüseyin Oyman — İR:2601**
4. **Elit Bims — İR:20051226**
5. **Serhat Madencilik — Ruhsat 9774**
6. **Öz-SA Madencilik — Sarıyaprak mevkii**
7. **ANC Madencilik — İR:3654**

Bu koordinat listesi hackathon geliştirme sürecinde aşağıdaki işler için doğrudan kullanılabilir:

- Pozitif pomza saha adaylarının QGIS’e aktarılması
- Sentinel-2 / Sentinel-1 change detection yapılması
- Manuel poligon etiketleme başlatılması
- U-Net veya rule-based pomza tespit modelinin ilk veri setinin oluşturulması
- UNESCO buffer / red flag overlay kontrolünün yapılması
- Dashboard’da gerçek saha örneklerinin gösterilmesi

Ancak nihai ürün veya resmi analiz için bu noktaların mutlaka MAPEG, ÇED dosyaları, güncel uydu görüntüsü ve gerekirse saha doğrulaması ile teyit edilmesi gerekir.

---

## 14. Kaynakça

### 14.1 Kamu ve Kurumsal Kaynaklar

1. **Nevşehir Çevre, Şehircilik ve İklim Değişikliği İl Müdürlüğü** — Fırat Madencilik İR:4363 Pomza Taşı Ocağı Kapasite Artışı ve Yıkama-Eleme Tesisi ÇED duyurusu.  
   URL: https://nevsehir.csb.gov.tr/nevsehir-ili-merkez---ilcesinde--duyuru-367015

2. **Nevşehir Valiliği / Çevre ve Şehircilik İl Müdürlüğü** — Nevşehir İli 2014 Yılı Çevre Durum Raporu.  
   URL: https://webdosya.csb.gov.tr/db/ced/editordosya/Nevsehir_icdr2014.pdf

3. **AHİKA** — Pomza Araştırma ve Uygulama Merkezi Fizibilite Raporu.  
   URL: https://ahika.gov.tr/assets/ilgilidosyalar/Pomza-Arastirma-ve-Uygulama-Merkezi-Fizibilite-Raporu.pdf

4. **Ürgüp Haber** — ÇED sürecine halkın katılımı toplantısı duyurusu / Hüseyin Oyman IV-A Grup Pomza Ocağı Kapasite Artışı.  
   URL: https://www.urguphaber.com.tr/2024/07/19/duyuru-ced-surecine-halkin-katilimi-toplantisi/

### 14.2 Proje İçi Dokümanlar

5. **PomzaScope — Kapadokya Hackathon 2026 Deep Research Raporu**  
   Not: Uydu seçimi, MAPEG veri erişimi, pomza modelleme yaklaşımı, MAPEG poligonlarının açık kaynakta doğrulanamaması ve PomzaScope stack önerileri için kullanılmıştır.

6. **Modül A — 5 Kişilik Development Rol Dağıtımı**  
   Not: PomzaScope Modül A teknik akışı, veri pipeline, etiketleme, ML, spektral indeksler, change detection ve UNESCO overlay kapsamı için kullanılmıştır.

---

## Ek A — QGIS Kullanım Notu

Bu dosyadaki CSV bloğu ayrı bir `.csv` dosyası olarak kaydedildikten sonra QGIS’e şu şekilde aktarılabilir:

1. QGIS açılır.
2. `Layer > Add Layer > Add Delimited Text Layer` seçilir.
3. CSV dosyası seçilir.
4. X field: `longitude`
5. Y field: `latitude`
6. CRS: `EPSG:4326 — WGS 84`
7. Noktalar haritada görüntülenir.
8. Sentinel-2 veya Google Satellite altlığı açılarak ocak sınırları manuel çizilir.

---

## Ek B — PomzaScope İçin Önerilen Dosya Yapısı

```text
/data/labels/
  ├── positive_polygons.geojson
  ├── negative_polygons.geojson
  ├── candidate_pumice_points.csv
  └── candidate_pumice_points.geojson

/data/change_and_overlay/
  ├── s1_amplitude_diff_2024_2025.tif
  ├── landsat_timeseries/
  ├── wdpa_goreme_buffer1000m.geojson
  └── red_flag_alerts.json

/frontend/
  ├── layers.json
  └── folium_map_init.py
```

---

## Ek C — Hızlı Kontrol Checklist’i

- [ ] Koordinatlar QGIS’e yüklendi mi?
- [ ] Her koordinat çevresinde açık ocak görünüyor mu?
- [ ] Güncel Sentinel-2 görüntüsünde yüzey açıklığı var mı?
- [ ] 2015–2026 arası büyüme / değişim var mı?
- [ ] UNESCO buffer’a yakınlık kontrol edildi mi?
- [ ] Pozitif poligonlar elle çizildi mi?
- [ ] Negatif örnekler dengeli seçildi mi?
- [ ] Üretim olmadığı belirtilen sahalar pozitif etikete otomatik dahil edilmedi mi?
- [ ] Güncel ÇED sahaları önceliklendirildi mi?
- [ ] CSV ve GeoJSON dashboard’a bağlandı mı?

---

**Rapor sonu.**
