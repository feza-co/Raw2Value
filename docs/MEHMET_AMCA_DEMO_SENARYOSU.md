# Raw2Value AI — 3 Dakikalık Demo Senaryosu

**Persona:** Mehmet Amca (Acıgöl pomza ocağı sahibi)
**Süre:** 3:00 (180 sn) — kesinlikle aşılmayacak
**Format:** Loom/OBS ekran kaydı + voice-over
**Hedef:** Bir kullanıcının (üretici rolü) tek oturumda sistemden somut bir karar çıkarması; bu karar yolculuğunda 3 zorunlu kuralın (K1 karbon, K2 EVDS, K3 geo) doğal olarak görünmesi.

---

## 1. Mehmet Amca'nın Amacı (Demo'nun Çekirdeği)

> *"Acıgöl'de pomza ocağım var. Bu ay 150 ton A kalite hammaddem hazır. Geçen ay komşu Halil hep aynı bims firmasına ton 800 TL'ye sattı diye ben de oraya satıyordum. Ama 'Almanya'ya mikronize gidiyor, ton başı 250 dolar' diye duyuyorum. Hangisi gerçekten daha kârlı? Karbon vergisi geliyormuş, onu da kim hesaplayacak? Ben madenciyim, Excel'ci değilim."*

**Demo'da kanıtlanacak tek cümle:**
*Mehmet Amca'nın 150 tonluk hammaddesi için sistem, 30 saniye içinde "hangi rota + hangi alıcı + ne kadar kâr + ne kadar CO₂ + güncel kurla TL karşılığı" sorularına açıklamalı cevap veriyor.*

Bu cümleyi 3 dakikada **tek nefeste**, hiçbir slayt göstermeden, sadece UI üzerinde gezerek kanıtlamalıyız.

---

## 2. Sahne Düzeni (Demo Çekiminden Önce)

### 2.1 Backend hazırlığı (kayıt başlamadan)
```bash
docker compose up -d
docker compose exec api python scripts/seed_demo.py    # 5 org seed'lenir
```

Seed'lenen org'lar:
- **Doğa Pomza Ltd** (Acıgöl, üretici) → *Mehmet Amca'nın firması*
- **Genper Madencilik A.Ş.** (Acıgöl, işleyici, ISO9001, 50.000 ton/yıl)
- **BASF Deutschland GmbH** (Hamburg, alıcı, mikronize pomza)
- Anadolu Perlit (gürültü için), Kapadokya Tarım (gürültü için)

### 2.2 Demo kullanıcısını önceden hazırla
Kayıttan önce **bir kez** çalıştır:
```bash
# Mehmet Amca user'ı + Doğa Pomza Ltd org'u oluştur (kayıtta zaman gitmesin)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"mehmet@dogapomza.tr","password":"acigol2026","full_name":"Mehmet Yılmaz"}'

# Login → token al → frontend'e yapıştır (localStorage)
TOKEN=$(curl -sf -X POST http://localhost:8000/api/auth/login \
  -d "username=mehmet@dogapomza.tr&password=acigol2026" | jq -r .access_token)
```

> **Neden önceden?** 3 dakikalık demoda register/login ekranı göstermek 30 saniyemizi alır ve "ürünün anlamı" değildir. Kayıtta direkt Cockpit ekranıyla başlıyoruz, üst çubukta "Mehmet Yılmaz / Doğa Pomza Ltd" yazıyor olacak — bu kim olduğumuzu söylüyor.

### 2.3 FX cache'i ısıt
```bash
curl http://localhost:8000/api/fx/current  # USD/TRY taze gelsin
```

### 2.4 ML warm-up
```bash
# İlk analyze çağrısı 1.4 sn'lik pickle yüklemesi yapar — kayıttan önce sıcak çağır
curl -X POST http://localhost:8000/api/analyze ... (örnek payload)
```

> **Neden?** Cold start'ta kullanıcı 1.4 sn beklerse demo şişer. Sıcakken p95 < 100 ms. Kayıt alırken her çağrı anlık.

---

## 3. Demo Akışı (Saniye Saniye)

### **0:00 – 0:15** — Açılış kancası (kim, sorun ne)

**Görsel:** Cockpit ana ekranı açık. Üstte "Mehmet Yılmaz · Doğa Pomza Ltd · Acıgöl/Nevşehir". Form sol panelde, sağ panelde harita üzerinde Acıgöl noktası (Mehmet'in lokasyonu) flaşlıyor.

**Voice-over:**
> "Bu Mehmet Amca. Acıgöl'de pomza ocağı sahibi. Bu ay 150 ton A kalite pomzası var. Bims olarak yerel firmaya satarsa ton başı 800 TL alıyor. Ama mikronize işlenip Almanya'ya gitse rakam farklı. Hangisi gerçekten kârlı? Mehmet Amca açıyor — Raw2Value AI."

**Endpoint tetiklenmiş olan:** Açılışta otomatik:
- `GET /api/auth/me` → kullanıcı + organization bilgisi (top bar'da render)
- `GET /api/fx/current` → sağ üst FX widget'ı: "USD: 45.05 ↑ · EUR: 52.67 ↑ · 02 May 2026 12:00"

> *Kural 2 (TCMB EVDS) ekran açılırken **anonsa gerek kalmadan** görünüyor — kayıt vurgusu sonra gelecek.*

---

### **0:15 – 0:55** — Form doldurma + Analiz (asıl gösteri)

**0:15 – 0:30 — Form (kullanıcı klavye kullanmasın, hızlı seç)**

| Alan | Değer | Anonim mi? |
|---|---|---|
| Hammadde | `Pomza` (dropdown) | Görünür |
| Tonaj | `150` (slider veya input) | Görünür |
| Kalite | `A` | Görünür |
| Çıkış şehri | `Nevşehir` (otomatik dolu — org profilinden) | Görünür |
| Hedef ülke | `Almanya (DE)` | Görünür |
| Taşıma modu | `Kara (TIR)` | Görünür |
| Öncelik | `Maksimum kâr` | Görünür |
| Mod | `Basic` (zaten default) | Görünür |

**Voice-over (form doldurulurken):**
> "Sistem hammadde, tonaj, kalite, hedef ülke ve önceliğini soruyor. Mehmet Amca nem oranı, parçacık boyutu, saflık gibi teknik değerleri bilmek zorunda değil — Basic Mode bu. Sistem eksikleri bölgesel varsayılanla dolduruyor."

**0:30 – 0:33 — "Analiz Et" butonuna bas.**

**Endpoint tetiklenir:**
```
POST /api/analyze
Authorization: Bearer eyJ...
{
  "raw_material": "pomza",
  "tonnage": 150,
  "quality": "A",
  "origin_city": "Nevşehir",
  "target_country": "DE",
  "target_city": "Hamburg",
  "transport_mode": "kara",
  "priority": "max_profit",
  "input_mode": "basic"
}
```

Backend arka planda yapıyor (ekranda spinner ~1 sn, voice-over devam ediyor):
1. JWT decode → user → org_id
2. `get_current_fx()` → Redis cache → `LiveFx` payload'a basılır
3. `run_analyze()` → `raw2value_ml.analyze(payload)` → 2 model + scorer çalışır
4. Response döner; `analysis_history`'e fire-and-forget kaydedilir

**0:33 – 0:55 — Sonuç ekranı (asıl wow burada)**

Ekran üç kolona ayrıldı, hepsi aynı anda çıkıyor:

**Sol kolon — Önerilen Rota (Top-1):**
> ✅ **Mikronize Pomza → Hamburg, Almanya**
> Beklenen kâr: **₺1.425.000** (toplam, 150 ton)
> Değer artışı: **+%485** (ham bims'e göre)
> Güven: **%83**

**Orta kolon — Harita (Leaflet+OSM):**
- Acıgöl 🔴 → Genper Madencilik 🏭 → Hamburg 📦
- Çizilmiş rota: 2.502 km kara (TIR)

**Sağ kolon — Top-3 Alternatif (sıralı tablo):**
| Sıra | Rota | Kâr (TL) | Olasılık |
|---|---|---:|---:|
| 1 | Mikronize → DE | 1.425.000 | 87% |
| 2 | Filtrasyon medyası → NL | 980.000 | 8% |
| 3 | Bims (yerel) | 280.000 | 5% |

**Voice-over (0:33–0:55, hızlı tempo):**
> "Üç saniyede karar paketi geldi. Sistem birinci öneri olarak hammaddeyi Acıgöl'deki Genper Madencilik'te mikronize ettirip Hamburg'a — BASF'a — göndermeyi öneriyor. 1.425.000 TL beklenen kâr. Mehmet Amca'nın şu anki bims rotası listenin **üçüncüsü**, sadece 280.000 TL. Yani sistem 5 kat daha kârlı bir alternatif buldu."

**Bu segmentte kanıtlanan endpoint:** `POST /api/analyze` ✅

---

### **0:55 – 1:30** — Açıklanabilirlik (LLM değil, ML)

**Görsel:** Ekranın altında "Bu kararı sistem nasıl verdi?" bölümü açıldı. Üç reason code Türkçe template'le geliyor + sağda küçük feature importance bar'ı.

**Reason codes panel:**
> 📍 **Mesafe (önem: 0.34, değer: 2502 km)**
> Toplam 2502 km mesafe yüksek; karbon ayak izi ve taşıma maliyeti kârı sınırlıyor — yine de mikronize katma değeri bunu fazlasıyla telafi ediyor.
>
> 💱 **USD/TRY (önem: 0.21, değer: 45.05)**
> Kur 45.05 seviyesinde; ihracat geliri TL bazında güçlü. Bu seviyenin altında öneri "filtrasyon medyası → Hollanda"ya kayıyor.
>
> 📈 **Talep skoru (önem: 0.17, değer: 0.85)**
> Almanya inşaat ve kozmetik sektöründe mikronize pomza talebi yüksek (BASF tipi alıcılar).

**Voice-over:**
> "Karar bir LLM çıktısı değil. İki gradient boosting modeli — kâr regresyonu ve rota multi-class — feature importance'la beraber çalışıyor. Sistem 'mesafe yüksek **ama** kur ve talep birlikte mikronize rotayı zirveye çekiyor' diye açıklıyor. Mehmet Amca neye göre karar verildiğini görüyor."

**0:55–1:30 segmentinde kanıtlanan:** Reason codes + feature importance — bunlar zaten `/api/analyze` response'unda; ek endpoint çağrısı yok.

---

### **1:30 – 2:00** — Kural 1 (Karbon) + Kural 3 (Coğrafi) — birlikte

**Görsel:** Ekranın orta-üst kısmında karbon kartı parlıyor (otomatik, başka tıklama yok):

> 🌍 **CO₂ Ayak İzi**
> 150 ton × 2.502 km × 0.100 kg/ton-km = **37.530 kg = 37,53 ton CO₂**
> Hesap yöntemi: kara (TIR) — hackathon resmi emisyon faktörü
> Mesafe kaynağı: OpenRouteService, dinamik

**Voice-over:**
> "Karbon ayak izi sabit kodlu değil. Mesafeyi OpenRouteService'ten dinamik çekiyoruz, hackathon resmi emisyon faktörüyle çarpıyoruz: 37 ton CO₂. Mesafe sıfır olsa rakam sıfır olur — gerçekten dinamik."

**Sonra harita üstünde küçük bir buton parlıyor: "100 km içindeki işleyicileri göster"**

Mehmet Amca tıklar — **harita Acıgöl çevresine zoom yapıyor, mavi pinlerle 3 işleyici çıkıyor.**

**Endpoint tetiklenir:**
```
GET /api/processors/nearby?lat=38.55&lon=34.50&radius_km=100&material=pomza
Authorization: Bearer eyJ...
```

Response (ekrandaki sıralı liste):
1. Genper Madencilik A.Ş. — Acıgöl, **12,5 km** ✓ (zaten önerilen)
2. Akper A.Ş. — Acıgöl, 28,3 km
3. (varsa 3. tesis)

**Voice-over (haritada pinler düşerken):**
> "Bu farklı bir coğrafi işlem — karbon hesabıyla ilgisi yok. Mehmet Amca 100 km çevresindeki **alternatif işleyicileri** Haversine + bbox'la çıkarıyor; ana öneri zaten Genper'di — 12 km uzakta. Kapasite veya fiyat değişirse Akper de hazır."

**Bu segmentte kanıtlanan:**
- ✅ `/api/analyze` response'undaki `co2_kg` field'ı (Kural 1 görsel)
- ✅ `GET /api/processors/nearby` (Kural 3, **bağımsız** geo lookup)

> **Önemli:** İki coğrafi işlem **farklı amaçlara** hizmet ediyor — bu jüriye açıkça gösterilmeli (Kural 3 koşulu).

---

### **2:00 – 2:35** — Kural 2 (Canlı Kur) + What-if simülasyon

**Görsel:** Sağ üstteki FX widget'ında küçük bir "What-if" handle açıldı. Mehmet Amca kur slider'ını çekiyor.

**Voice-over:**
> "Kur sadece ekranda yazmıyor. Modelin feature vector'ünün parçası. Mehmet Amca 'kur %20 düşerse ne olur?' diye soruyor."

Slider hareket eder: USD/TRY 45.05 → -20% senaryosunda 36.04. Buton: "What-if çalıştır".

**Endpoint tetiklenir:**
```
POST /api/what-if
Authorization: Bearer eyJ...
{
  "base_payload": { ...aynı analyze payload },
  "scenarios": [
    {"name": "Kur -%20", "fx_scenario_pct": -0.20},
    {"name": "Kur sabit", "fx_scenario_pct": 0.0},
    {"name": "Kur +%20", "fx_scenario_pct": 0.20}
  ]
}
```

Backend `asyncio.gather` ile 3 senaryoyu paralel koşturur (~150 ms).

**Sonuç (ekranda küçük tablo):**
| Senaryo | Kâr (TL) | Önerilen rota |
|---|---:|---|
| Kur -%20 | 980.000 | **Filtrasyon → NL** (rota değişti!) |
| Kur sabit | 1.425.000 | Mikronize → DE |
| Kur +%20 | 1.870.000 | Mikronize → DE |

**Voice-over:**
> "Kur 20 düşerse sistemin tavsiyesi **rota değiştiriyor** — Almanya yerine Hollanda filtrasyon. Çünkü o senaryoda mesafe avantajı dolar gelirini kapatıyor. İşte 'kur bir karar tetikleyicisi' — Kural 2 ölü değil, canlı."

**Bu segmentte kanıtlanan:** `POST /api/what-if` + Kural 2 (canlı EVDS feature → karar değişimi)

---

### **2:35 – 2:55** — Geçmiş & Model Evidence (kısa kapanış)

**Görsel:** Üst menüden "Geçmiş" sekmesine tıklanır.

**Endpoint tetiklenir:**
```
GET /api/history?page=1&page_size=10
```

Bir tablo: bugün yapılan analiz görünür (request_id, kâr, CO₂, kur, timestamp). **Aynı analizi tekrar açabilir.**

**Voice-over (2:35–2:45):**
> "Her analiz `analysis_history` tablosuna düşüyor. Mehmet Amca üç ay sonra geri gelip 'kur şimdi 50 oldu, eski analizimi yeni kurla yeniden hesaplat' diyebilir."

**Sonra Model Evidence sekmesine tıklanır:**
```
GET /api/model-evidence
```

Ekranda kısa bir tablo:
- Dataset: 78 referans + 1.500 augmented satır
- Best model: CatBoost (RMSE düşük)
- Feature importance grafiği
- Ablation: K1/K2/K3 feature'larının olmaması durumunda metrik düşüşü

**Voice-over (2:45–2:55):**
> "Jüri için public endpoint: `/api/model-evidence`. Hangi modelin neden seçildiği, hangi feature olmadan modelin ne kadar kötüleştiği — açıklanabilir. Hiçbir sayı uydurma değil."

---

### **2:55 – 3:00** — Kapanış (5 saniye)

**Görsel:** Cockpit'in tam ekranına geri zoom-out, üst sağda saatler döner gibi efekt, slogan altta.

**Voice-over:**
> "Raw2Value AI: marketplace değil, karar motoru. Mehmet Amca 30 saniyede ne yapacağını biliyor. **Raw2Value — Cave2Cloud.**"

Fade out.

---

## 4. Endpoint-Dakika Eşlemesi (Jüri için sağlam çıktı)

Tek bir tabloda, demo süresince **gerçekten çağrılan** endpoint'ler:

| Saniye | Endpoint | Tetikleyen aksiyon | Kural |
|---|---|---|---|
| 0:00 | `GET /api/auth/me` | Sayfa açılışı | — |
| 0:00 | `GET /api/fx/current` | Sayfa açılışı (FX widget) | **K2** |
| 0:33 | `POST /api/analyze` | "Analiz Et" butonu | K1 (CO₂ field), K2 (FX feature), K3 (geo dahili) |
| 1:45 | `GET /api/processors/nearby` | "100 km içindekileri göster" | **K3** (bağımsız) |
| 2:08 | `POST /api/what-if` | Kur slider + Çalıştır | **K2** (kur senaryosu kararı değiştirir) |
| 2:38 | `GET /api/history` | Geçmiş sekmesi | — |
| 2:48 | `GET /api/model-evidence` | Model Evidence sekmesi | — |

**Toplam endpoint çağrısı:** 7 farklı endpoint, 7 ayrı UI etkileşimi → 3 zorunlu kural **2 farklı işlevde** tutarlı şekilde gösterildi (K1 karbon hesabı + K2 EVDS + K2 what-if + K3 nearby).

> **Jüri sorarsa:** "Kural 1 ve Kural 3 farklı işlevlerde mi?" → Evet. K1 → analyze response'unda CO₂ alanı (mesafe × tonaj × emisyon faktörü). K3 → `/api/processors/nearby` (Haversine + bbox ile yakınlık taraması). Bu iki coğrafi işlem **ayrı kod yolundan, ayrı amaçla** çalışıyor.

---

## 5. Çekim Teknik Notları

### 5.1 Loom / OBS ayarları
- **1920×1080 60 fps**, sistem sesi kapalı, sadece mikrofon
- Tarayıcı tek sekmede, fullscreen (F11)
- Tarayıcı zoom **%100** (Cockpit grid bozulmasın)
- Dark mode tercih (renderlar daha keskin görünür)

### 5.2 Kayıttan önce check-list
- [ ] `docker compose up -d` healthy
- [ ] Seed çalıştı (`docker compose exec api python scripts/seed_demo.py`)
- [ ] `/api/fx/current` 200 dönüyor (cache sıcak)
- [ ] Bir kez `/api/analyze` warm-up çağrısı yapıldı
- [ ] Mehmet Amca user'ı login olmuş, token localStorage'da
- [ ] Frontend'de Cockpit ekranı açık, form temiz
- [ ] Tarayıcı geçmişi/auto-suggest temizlendi (form doldururken sürpriz olmasın)
- [ ] Bildirimleri kapat (Slack/Mail vs.)
- [ ] Notebook şarj %100 + adaptör takılı
- [ ] İnternet stabil — ORS / TCMB hit edilebilir olmalı

### 5.3 Yedek planlar
- **TCMB EVDS düşerse:** `TCMB_FALLBACK_USD_TRY=45.05` env'i devreye girer; `is_stale: true` rozet görünür → voice-over "demo modu, fallback kur" deyip geçilir
- **ORS rate limit:** ML paketinin internal lookup'ı zaten hazırda; `/api/analyze` ORS olmadan da çalışır. Yalnızca harita rotası çizilemezse haritada düz çizgi gösterilir
- **`/api/analyze` 5xx atarsa:** Önceden kaydedilmiş `history` kaydından `request_id` ile aynı sonucu çekip ekrana basabilirsiniz (bu plan B çekimde yedek olarak hazır olsun)

### 5.4 Voice-over yazımı (kayıttan önce 5 kez prova et)
- Her cümle **maksimum 12 saniye**
- "Şey", "yani", "aslında" yok — keskin başla, keskin bitir
- Mehmet Amca'yı **yargılama**: "bilmiyor" değil, **"bilmek zorunda değil"**
- Sayıları net söyle: "bir milyon dört yüz yirmi beş bin TL" (rakamı ekran zaten gösteriyor, sen de söyle)

---

## 6. Voice-Over Tam Metni (Tek Parça)

> "Bu Mehmet Amca. Acıgöl'de pomza ocağı sahibi. Bu ay 150 ton A kalite pomzası var. Bims olarak yerel firmaya satarsa ton başı 800 TL alıyor. Ama mikronize işlenip Almanya'ya gitse rakam farklı. Hangisi gerçekten kârlı? Mehmet Amca açıyor — Raw2Value AI.
>
> Sistem hammadde, tonaj, kalite, hedef ülke ve önceliğini soruyor. Mehmet Amca nem oranı, parçacık boyutu, saflık gibi teknik değerleri bilmek zorunda değil — Basic Mode bu. Sistem eksikleri bölgesel varsayılanla dolduruyor.
>
> Üç saniyede karar paketi geldi. Sistem birinci öneri olarak hammaddeyi Acıgöl'deki Genper Madencilik'te mikronize ettirip Hamburg'a — BASF'a — göndermeyi öneriyor. 1.425.000 TL beklenen kâr. Mehmet Amca'nın şu anki bims rotası listenin üçüncüsü, sadece 280.000 TL. Yani sistem 5 kat daha kârlı bir alternatif buldu.
>
> Karar bir LLM çıktısı değil. İki gradient boosting modeli — kâr regresyonu ve rota multi-class — feature importance'la beraber çalışıyor. Sistem 'mesafe yüksek ama kur ve talep birlikte mikronize rotayı zirveye çekiyor' diye açıklıyor. Mehmet Amca neye göre karar verildiğini görüyor.
>
> Karbon ayak izi sabit kodlu değil. Mesafeyi OpenRouteService'ten dinamik çekiyoruz, hackathon resmi emisyon faktörüyle çarpıyoruz: 37 ton CO₂. Mesafe sıfır olsa rakam sıfır olur — gerçekten dinamik.
>
> Bu farklı bir coğrafi işlem — karbon hesabıyla ilgisi yok. Mehmet Amca 100 km çevresindeki alternatif işleyicileri Haversine + bbox'la çıkarıyor; ana öneri zaten Genper'di — 12 km uzakta. Kapasite veya fiyat değişirse Akper de hazır.
>
> Kur sadece ekranda yazmıyor. Modelin feature vector'ünün parçası. Mehmet Amca 'kur %20 düşerse ne olur?' diye soruyor. Kur 20 düşerse sistemin tavsiyesi rota değiştiriyor — Almanya yerine Hollanda filtrasyon. Çünkü o senaryoda mesafe avantajı dolar gelirini kapatıyor. İşte 'kur bir karar tetikleyicisi' — Kural 2 ölü değil, canlı.
>
> Her analiz analysis_history tablosuna düşüyor. Mehmet Amca üç ay sonra geri gelip 'kur şimdi 50 oldu, eski analizimi yeni kurla yeniden hesaplat' diyebilir.
>
> Jüri için public endpoint: /api/model-evidence. Hangi modelin neden seçildiği, hangi feature olmadan modelin ne kadar kötüleştiği — açıklanabilir. Hiçbir sayı uydurma değil.
>
> Raw2Value AI: marketplace değil, karar motoru. Mehmet Amca 30 saniyede ne yapacağını biliyor. Raw2Value — Cave2Cloud."

**Süre kontrolü:** ~165–175 saniye (3 dakikanın altında, güvenli marj).

---

## 7. Demo Sonrası 7-Dakikalık Sunum İçindeki Konum

Hatırlatma: Demo videosu yarışmadaki **3 dakikalık** kısım. Toplam sunum 7 dakika:
- 3 dk **demo** (bu video) → Mehmet Amca senaryosu
- 2 dk **iş modeli + 3 kural açıklaması** (slayt veya konuşma)
- 2 dk **jüri Q&A**

Bu sebepten demo videosu *iş modelini* anlatmaya çalışmıyor. Sadece **sistem ne yapıyor** sorusunun cevabı. İş modeli ve kuralların derinlik açıklaması bir sonraki 2 dakikada konuşulacak.
