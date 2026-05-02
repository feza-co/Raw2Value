# Raw2Value AI — Proje Analizi, Gri Noktalar, Global Karşılaştırma ve Tasarım Stratejisi

**Hazırlanma Tarihi:** Mayıs 2026  
**Revizyon:** Final ekip kararlarına göre scope temizliği yapılmış sürüm  
**Bağlam:** Kapadokya Hackathon 2026 — Kategori 3: Akıllı Tedarik Zinciri Sistemleri  
**Odak:** Stratejik analiz, fikir doğrulaması, rakip karşılaştırması, UI/UX tasarım yol haritası

> Bu revizyon, önceki rapordaki güçlü stratejik tespitleri korur; ancak final ekip kararlarıyla çelişen veya 24 saatlik MVP kapsamını gereksiz büyüten önerileri çıkarır ya da **Advanced / Future Work** seviyesine taşır.

---

## Yönetici Özeti (TL;DR)

Raw2Value AI fikri **temelde sağlam ve hackathon kazanma potansiyeli yüksek** bir projedir. Global olarak benzer projeler var (Interos, Verusen, Blue Yonder, Project44 vb.); ancak **bölgesel + hammadde-spesifik + ML-tabanlı + canlı kur + karbon + açık kaynak coğrafi işlem entegrasyonlu** bir kombinasyon, özellikle Nevşehir/TR71 odağıyla, net bir niş oluşturur.

Bu raporda önceki analizde yakalanan gri noktalar korunmuş; fakat final MVP kapsamını bozabilecek kısımlar sadeleştirilmiştir.

**Final ana kararlar:**

1. **Ana kategori:** Kategori 3 — Akıllı Tedarik Zinciri Sistemleri.
2. **Hammadde kapsamı:** Pomza ana demo (%70), perlit destek (%20), kabak çekirdeği destek (%10).
3. **Ürün konumu:** Raw2Value AI bir marketplace veya LLM chatbot değildir; **ML tabanlı B2B tedarik zinciri karar motorudur**.
4. **Ana fonksiyonlar:**
   - **Value Route Optimizer:** hammadde için en iyi katma değerli rota.
   - **B2B Match Finder:** üretici–işleyici–alıcı eşleşmesi.
5. **Demo ana ekranı:** AI Decision Cockpit. Harita destekleyici GeoCarbon panelidir; ana mesaj harita değil, modelin karar üretmesidir.
6. **Zorunlu kurallar:** OpenStreetMap/Nominatim/OpenRouteService + TCMB EVDS + bağımsız nearby processor filtresi.

**En kritik 3 öneri:**

1. “Akıllı tarafı ne?” sorusuna cevap:
   > “Raw2Value AI; hammadde türü, tonaj, kalite, canlı kur, rota mesafesi, karbon ve hedef pazar verilerini kullanarak en uygun işleme rotasını ve B2B eşleşmeyi skorlayan ML tabanlı karar motorudur.”

2. **Counterfactual / What-if demo** ekleyin. Jüri “kuru %20 artır” veya “işleme maliyetini yükselt” dediğinde önerinin değiştiğini canlı gösterin.

3. UI’da **AI Decision Cockpit** merkezli, temiz ve profesyonel bir karar destek sistemi havası verin. Harita, karbon ve nearby processor filtresi için güçlü bir destek paneli olarak kullanılmalı.

---

## 1. Proje Fikrinin Eleştirel Analizi: Güçlü Yanlar

### 1.1 Stratejik olarak doğru olan kararlar

- **Niş seçimi doğru.** TR71/Nevşehir odağı, pomza ve perlit gibi mineral hammaddelerle çok iyi örtüşür. Kabak çekirdeği ise tarımsal katma değer örneği olarak sistemi destekler.

- **“Ham satma, işle ve katma değer yarat” tezi ekonomik olarak savunulabilir.** Ham ürün ile mikronize, paketli, genleştirilmiş veya özel kullanım ürünü arasındaki fiyat farkı, projenin temel değer önerisini oluşturur.

- **LLM yerine ML seçimi doğru.** Mentörün “akıllı tarafı ne?” sorusuna karşı generative AI değil, predictive tabular ML kullanmak akademik ve teknik olarak daha savunulabilir. LLM sadece açıklama, teklif metni veya ürün açıklaması için yardımcı katmandır.

- **Benchmark ve ablation fikri doğru.** Modelin gerçekten karar verdiğini göstermek için rule-based baseline, Random Forest, XGBoost/LightGBM/CatBoost karşılaştırması ve FX/geo/carbon feature ablation’ı kullanılabilir.

### 1.2 Kategori uyumu

Kategori 3 — **Akıllı Tedarik Zinciri Sistemleri** ana kategori olarak korunmalıdır.

Muhtemel rakipler:

- lojistik rota optimizasyonu,
- talep tahmini,
- stok yönetimi,
- basit alıcı-satıcı pazaryeri,
- karbon hesaplayıcı.

**Raw2Value AI’ın farkı:** Diğerleri var olan zinciri optimize ederken, Raw2Value AI **zincirin hangi şekli alması gerektiğini** önerir. Bu operasyonel optimizasyondan daha üst seviyede, stratejik karar desteğidir.

---

## 2. Gri Noktalar ve Riskler

Bu bölümde önceki rapordaki gri noktalar korunmuş, ama final MVP scope’una göre düzeltilmiştir.

---

### 2.1 GRİ NOKTA 1: “Hangi işleme rotası?” listesi net olmalı

**Sorun:** Model rota önerecekse, her hammadde için rota sınıfları önceden net tanımlanmalı. Aksi halde ML modeli “rota öneriyor” gibi görünür ama aslında domain bilgisi eksik kalır.

**Final çözüm:** 3 hammadde için MVP rota listesi aşağıdaki gibi kilitlenmelidir.

#### Pomza için işleme rotaları

1. **Ham satış**  
   Ham veya düşük işlenmiş pomza satışı.

2. **Bims / hafif agrega**  
   Kırma + eleme + boyutlandırma sonrası yapı sektörüne satış.

3. **Mikronize pomza**  
   Öğütme + sınıflandırma + paketleme sonrası kozmetik, kimya, seramik veya katkı sektörlerine satış.

4. **Filtrasyon medyası**  
   Kalibre + yıkama + teknik sınıflandırma sonrası su/yağ/gıda filtrasyonu gibi endüstriyel kullanımlar.

5. **Tekstil / denim yıkama taşı**  
   Boyutlandırılmış ve sınıflandırılmış pomzanın denim/tekstil yıkama süreçlerinde kullanımı.

#### Perlit için işleme rotaları

1. **Ham satış**
2. **Genleştirilmiş perlit**
3. **Tarım substratı**
4. **İzolasyon dolgusu**
5. **Filtrasyon ürünü**

#### Kabak çekirdeği için işleme rotaları

1. **Dökme satış**
2. **Kavrulmuş / paketli premium ürün**
3. **Kabak çekirdeği yağı**
4. **Protein / toz ürün**
5. **Turistik hediyelik paket**

> Not: Kabak çekirdeği future work’e atılmayacak; MVP’de düşük ağırlıklı destek hammadde olarak kalacak. Ana validasyon pomza üzerinde yapılacak, perlit mineral genelleme, kabak çekirdeği ise tarımsal genelleme örneği olarak kullanılacaktır.

---

### 2.2 GRİ NOKTA 2: Üretici–İşleyici–Alıcı eşleşmesinde mini katalog gerekli

**Sorun:** Matching modeli için “hangi işleyici hangi rotayı yapabilir?” ve “hangi alıcı hangi ürünü ister?” bilgisi gerekir. Bu katalog olmadan B2B Match Finder boş görünür.

**Final çözüm:** Hackathon demosu için **15–25 kayıtlık manuel mini-katalog** hazırlanmalıdır.

Mini-katalog içeriği:

- üretici / hammadde sahibi,
- işleyici,
- B2B alıcı,
- şehir / ülke,
- koordinat,
- işleme kapasitesi,
- kabul ettiği hammaddeler,
- üretebildiği işlenmiş ürünler,
- alıcı sektör,
- minimum kalite ve tonaj beklentisi.

**Önemli düzeltme:** Uygulama içi coğrafi işlemde Google Maps kullanılmamalıdır. Kural 3 için açık kaynak coğrafi veri gerekir. Bu yüzden:

- Adres/koordinat: **Nominatim / OpenStreetMap**
- Rota/mesafe: **OpenRouteService**
- Yakın tesis filtresi: **OpenStreetMap / Overpass / kendi mini-katalog + koordinat filtresi**

Google Maps yalnızca manuel araştırma sırasında fikir edinmek için kullanılabilir; uygulama içinde zorunlu kural kanıtı olarak kullanılmamalıdır.

**Jüriye söylenecek cümle:**

> “Demo için kamuya açık kaynaklardan derlenmiş gerçekçi bir üretici–işleyici–alıcı mini-katalog kullandık. Koordinat ve mesafe hesaplarını ise uygulama içinde Nominatim/OpenStreetMap/OpenRouteService ile yaptık.”

---

### 2.3 GRİ NOKTA 3: Karbon hesabı resmi hackathon faktörleriyle yapılmalı

**Önceki riskli öneri:** Karbon hesabında GLEC/IMO/EPA gibi farklı faktörler, kamyon için 62 g CO₂/ton-km vb. değerler önerilmişti.

**Final karar:** MVP’de yalnızca hackathon kurallarında verilen resmi emisyon faktörleri kullanılacaktır.

| Taşıma modu | Emisyon faktörü |
|---|---:|
| Hava kargo | 0.500 kg CO₂ / ton-km |
| Deniz yolu | 0.015 kg CO₂ / ton-km |
| Kara / TIR | 0.100 kg CO₂ / ton-km |
| Demiryolu | 0.030 kg CO₂ / ton-km |

Formül:

```text
CO2_kg = tonnage × total_distance_km × emission_factor
```

Örnek:

```text
100 ton × 850 km × 0.100 = 8,500 kg CO₂ = 8.5 tCO₂
```

**MVP’de yapılacak:**

- Üretici → işleyici → alıcı mesafesi dinamik hesaplanır.
- Taşıma modu seçimine göre resmi emisyon faktörü kullanılır.
- CO₂ hem dashboard’da hem route comparison tablosunda gösterilir.

**Advanced / Future Work:**

- işleme karbonu,
- CBAM karbon fiyatı,
- GLEC/IMO/EPA alternatif metodolojileri,
- karbon maliyeti duyarlılık analizi.

Bu konular iyi fikirlerdir; ancak final MVP’nin zorunlu parçası yapılmamalıdır.

---

### 2.4 GRİ NOKTA 4: Döviz etkisi basit ama karar değiştirici olmalı

**Sorun:** Canlı TCMB EVDS kuru yalnızca gösterilirse kuralı zayıf karşılar. Kur, kârlılık veya rota kararını doğrudan etkilemelidir.

**Final MVP feature’ları:**

- `usd_try`
- `eur_try`
- `fx_last_updated`
- `target_currency`
- `fx_scenario_pct`
- `fx_impact_score`

**MVP davranışı:**

- İhracat rotalarında satış fiyatı USD/EUR üzerinden TL’ye çevrilir.
- Kur değişince beklenen kâr ve route score güncellenir.
- What-if slider ile kur değiştirildiğinde rota önerisi değişebiliyorsa bu demo’nun “vay be” anı olur.

**Advanced / Future Work:**

- `fx_volatility_30d`
- `fx_trend_pct_90d`
- `fx_relative_to_5yr_avg`
- forward beklenti / interest parity benzeri finansal modelleme.

Bu türev feature’lar teorik olarak iyi ama 24 saatlik MVP’ye zorunlu eklenmemelidir.

---

### 2.5 GRİ NOKTA 5: Match score “sihirli sayılar” gibi görünmemeli

**Sorun:** Manuel ağırlıklarla hesaplanan `match_score`, “bu ağırlıkları neye göre seçtiniz?” sorusunda zayıf kalabilir.

**Final MVP yaklaşımı:**

B2B Match Finder’da **explainable weighted scoring + reason codes** kullanılacaktır. LightGBM Ranker veya XGBoost Ranker advanced olarak bırakılır.

Örnek MVP formülü:

```text
match_score =
0.35 × profit_score
+ 0.20 × demand_match_score
+ 0.15 × distance_score
+ 0.15 × carbon_score
+ 0.10 × delivery_score
+ 0.05 × quality_match_score
```

Bu ağırlıklar gizli tutulmamalı; kullanıcı önceliğine göre değiştiği açıkça gösterilmelidir.

Örnek:

```text
Düşük karbon önceliği seçilirse:
carbon_score ağırlığı artar,
profit_score ağırlığı azalır.
```

**Jüri savunması:**

> “MVP’de match score açıklanabilir ve kullanıcı önceliklerine göre değişen domain-informed scoring ile hesaplanıyor. Gerçek işlem verisi geldikçe bu katman learning-to-rank modeline dönüştürülecek.”

**Advanced / Future Work:**

- LightGBM Ranker,
- XGBoost Ranker,
- Pareto frontier,
- öğrenilmiş ağırlıklar,
- NDCG@K ölçümü.

---

### 2.6 GRİ NOKTA 6: Kabak çekirdeği farklı domain ama MVP’de kalmalı

**Sorun:** Pomza ve perlit mineral, ton-bazlı ve endüstriyel hammaddelerdir. Kabak çekirdeği ise tarımsal, mevsimsel, gıda regülasyonu olan bir üründür. Aynı model içinde ele alınması feature mühendisliği açısından dikkat ister.

**Final karar:** Kabak çekirdeği future work’e atılmayacak. MVP’de **%10 ağırlıklı destek hammadde** olarak kalacak.

Doğru konumlandırma:

```text
Pomza: Ana demo ve ana model validasyonu.
Perlit: Mineral tarafında genellenebilirlik örneği.
Kabak çekirdeği: Tarımsal katma değer ve Cave2Cloud genişleme örneği.
```

Modelde eklenebilecek ayrım:

```text
material_type = mineral / agricultural
```

Bu feature ile modelin mineral ve tarımsal ürünleri ayırması sağlanabilir. Ancak ana demo kabak çekirdeği üzerine kurulmayacak; pomza akışını bölmeyecek.

---

### 2.7 GRİ NOKTA 7: Augmentation savunulabilirliği

**Sorun:** “Domain-informed synthetic data” demek doğru ama mentör “model sentetik veriden ne öğrendi?” diye sorabilir.

**Final savunma hattı:**

#### Katman 1 — Sentetik veri rastgele değildir

Veri üretimi fiziksel, ekonomik ve coğrafi kısıtlarla sınırlandırılmış domain-informed senaryo üretimidir.

Örnek:

- CO₂ random üretilmez; mesafe × tonaj × resmi emisyon faktörüyle hesaplanır.
- Kur hardcoded değildir; TCMB EVDS’ten gelir, what-if senaryosunda yüzdesel oynatılır.
- Fiyat ve maliyetler kaynaklı aralıklar içinde üretilir.

#### Katman 2 — Gerçek / referans mini test set kullanılır

Demo için 30–50 satırlık manuel kürasyonlu mini test set hazırlanır:

- gerçek şehirler,
- gerçekçi işleyici profilleri,
- gerçekçi alıcı sektörleri,
- kaynaklı fiyat/maliyet aralıkları.

#### Katman 3 — Model Evidence ekranı

Model Lab / AI Evidence ekranında:

- dataset satır sayısı,
- gerçek referans satırı,
- augmentation sonrası satır,
- benchmark planı,
- feature importance,
- ablation sonuçları veya placeholder açıklaması gösterilir.

**Dürüstlük notu:** Gerçek eğitim metrikleri yoksa benchmark sayılarını kesin sonuç gibi yazmayın. “Placeholder / hedeflenen deney tasarımı” olarak gösterin.

---

## 3. Kullanıcı ve Rol Modeli Düzeltmesi

Önceki raporda kullanıcı rolleri ayrı ayrı düşünülüyordu. Final kararda sistem **capability-based** olmalı.

### 3.1 Ana roller

- Üretici / hammadde sahibi
- İşleyici / processor
- B2B alıcı
- Admin

### 3.2 Capability modeli

Bir kullanıcı tek role sıkışmaz. Bölgedeki bir KOBİ aynı anda hammadde sahibi, işleyici ve ihracatçı olabilir.

Kabiliyetler:

```text
canSupplyRawMaterial
canProcessMaterial
canBuyMaterial
canExport
hasStorage
hasTransportCapacity
```

Örnek:

> Bir mikronizasyon tesisi hem dışarıdan pomza kabul edebilir hem kendi pomza sahasına sahip olabilir. Sistem onu hem supplier hem processor olarak değerlendirebilir.

### 3.3 Veri modeline yansıması

Önerilen temel tablo:

```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(200),
  organization_type VARCHAR(50),
  district VARCHAR(100),
  city VARCHAR(100),
  country VARCHAR(100),
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,

  can_supply_raw_material BOOLEAN DEFAULT FALSE,
  can_process_material BOOLEAN DEFAULT FALSE,
  can_buy_material BOOLEAN DEFAULT FALSE,
  can_export BOOLEAN DEFAULT FALSE,
  has_storage BOOLEAN DEFAULT FALSE,
  has_transport_capacity BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

`producers`, `processors`, `buyers` tabloları gerekiyorsa bu `organizations` tablosuna bağlı profil/detail tabloları olarak kullanılabilir.

---

## 4. Material Analyzer Input Düzeltmesi: Basic Mode / Advanced Mode

Üretici nem, saflık, parçacık boyutu veya kimyasal analiz gibi teknik değerleri bilmek zorunda değildir.

### 4.1 Basic Mode

Kullanıcı sadece şunları girer:

- hammadde türü,
- lokasyon,
- yaklaşık tonaj,
- gözle kalite: bilmiyorum / düşük / orta / yüksek,
- ürün formu: ham kaya / kırılmış / elenmiş / toz / paketli,
- hedef pazar,
- öncelik: maksimum kâr / düşük karbon / hızlı teslim.

### 4.2 Advanced Mode

Teknik kullanıcı veya işleyici varsa şunları ekleyebilir:

- nem oranı,
- saflık,
- parçacık boyutu,
- yoğunluk,
- teknik analiz,
- laboratuvar raporu,
- teknik föy.

### 4.3 Eksik teknik bilgi durumunda

Sistem çalışmaya devam eder.

- bölgesel/default aralık kullanılır,
- `data_confidence_score` düşürülür,
- `model_confidence_score` üzerinde uyarı gösterilir.

UI uyarısı:

```text
Nem ve saflık bilgisi girilmedi. Sistem bölgesel varsayılan aralıklarla tahmin yaptı. Bu nedenle model güven skoru orta seviyededir.
```

---

## 5. Zorunlu Hackathon Kurallarıyla Uyum Matrisi

| Kural | Raw2Value AI uygulaması | UI kanıtı | MVP notu |
|---|---|---|---|
| Kural 1 — Coğrafi karbon izi | OpenRouteService mesafesi × tonaj × resmi emisyon faktörü | CO₂ kartı, rota karşılaştırma tablosu, GeoCarbon paneli | Hardcoded mesafe yok |
| Kural 2 — Canlı döviz kuru | TCMB EVDS USD/TRY ve EUR/TRY; kâr ve rota skorunu etkiler | canlı kur kartı, son güncelleme zamanı, what-if slider | Kur sadece gösterilmez, karar değiştirir |
| Kural 3 — Bağımsız coğrafi işlem | Nearby processor filtering / radius search | 50/100/250 km içindeki işleyiciler listesi | Karbon hesabından bağımsız coğrafi işlem |

---

## 6. Global Rakip ve Benzer Proje Analizi

Aşağıdaki tablo, mevcut global çözümlere göre Raw2Value AI’ın pozisyonunu gösterir. Net mesaj: doğrudan birebir rakip yok; proje kendine özgü bir niştedir.

| Platform | Ne yapıyor? | Raw2Value AI farkı |
|---|---|---|
| Interos | Tedarikçi risk izleme | Mevcut zinciri izler; Raw2Value zincirin nasıl kurulması gerektiğini önerir |
| Verusen | Malzeme ve tedarikçi eşleştirme | İşleme rotası + katma değer kararını dahil etmez |
| Find My Factory | Tedarikçi keşfi | Arama motoru gibi çalışır; kâr/karbon/kur optimizasyonu yoktur |
| Blue Yonder | Enterprise supply-chain planning | Fortune 500 odaklıdır; Raw2Value bölgesel KOBİ/hammadde odaklıdır |
| Project44 | Sevkiyat görünürlüğü | Lojistik visibility odaklıdır; value transformation yoktur |
| Amazon Connect Decisions | Genel karar merkezi | Hammadde-spesifik, TR71/TCMB/yerel geo odak yoktur |

### 6.1 Rekabet avantajı

1. **Bölgesel derinlik:** TR71/Nevşehir hammadde verisi.
2. **Hammadde-spesifik feature mühendisliği:** pomza rota sınıfları, perlit genleştirme, kabak çekirdeği paketleme/yağ rotaları.
3. **Türkiye-spesifik entegrasyon:** TCMB EVDS, TÜİK/MTA/AHİKA referansları, açık kaynak coğrafi veri.
4. **Decision engine konumu:** basit marketplace değil, karar destek sistemi.

---

## 7. Eksik Olan / Eklenmesi Düşünülmeli

Bu bölümde önceki rapordaki öneriler sadeleştirildi. MVP’ye alınacaklar ve Advanced/Future Work ayrıldı.

### 7.1 Risk skorlama

`risk_score` tek sayı gibi görünmemeli. Alt bileşenlerle açıklanabilir olmalı.

MVP alt bileşenleri:

- teslim süresi riski,
- fiyat/maliyet belirsizliği,
- alıcı pazar uygunluğu,
- veri confidence seviyesi.

Advanced/Future Work:

- OECD ülke riski,
- regülasyon riski,
- CBAM etkisi,
- sınır geçişi riski,
- mevsimsel rota riski.

### 7.2 What-if simülatörü

Demo’nun en güçlü anı bu olmalı.

MVP slider’ları:

- USD/TRY veya EUR/TRY ±%20,
- işleme maliyeti ±%30,
- tonaj,
- hedef pazar,
- karbon önceliği.

Advanced:

- karbon fiyatı,
- multi-leg lojistik,
- FX volatility,
- Pareto frontier.

### 7.3 Confidence göstergesi

ML çıktısı tek nokta olmamalı; en azından model confidence gösterilmeli.

MVP:

```text
Model güveni: %72
Veri güveni: Orta
Neden: teknik analiz bilgisi eksik, fakat lokasyon/kur/mesafe canlı veriden geldi.
```

Advanced:

- bootstrap prediction interval,
- quantile regression,
- SHAP-based uncertainty explanation.

### 7.4 Pilot müşteri hipotezi

Önceki rapordaki “pilot görüşmesi planlandı” gibi kesin ifadeler, gerçekten görüşme yoksa kullanılmamalıdır.

Doğru cümle:

> “Hackathon sonrası ilk pilot hedefimiz Nevşehir TSO, OSB, ticaret borsası ve yerel işleyici firmalarla görüşerek gerçek teklif/satış verisi toplamaktır.”

### 7.5 Mevsimsellik ve kapasite

MVP’de basit tutulabilir ama veri şemasında yer açılmalıdır.

MVP:

- `lead_time_days`,
- `processor_capacity_ton_month`,
- `seasonal_demand_index` opsiyonel.

Future Work:

- gerçek stok,
- kapasite kısıtlı optimizasyon,
- multi-producer allocation.

### 7.6 Multi-leg lojistik

Önceki raporda üretici → işleyici → liman → alıcı gibi çok bacaklı lojistik önerilmişti. MVP’de bu kapsam fazla büyür.

MVP:

```text
Üretici → İşleyici → B2B Alıcı
```

Future Work:

```text
Üretici → İşleyici → Liman / intermodal node → Alıcı
```

---

## 8. Demo’da Göstermek İçin “Wow” Anları

Öncelik sırası final MVP’ye göre düzeltilmiştir.

1. **Slider hareketi → öneri değişiyor**  
   Kur veya işleme maliyeti değişince top-1 rota değişir.

2. **AI Decision Cockpit**  
   Pomza input’u → kâr, değer artışı, CO₂, kur etkisi, eşleşme, reason codes tek ekranda.

3. **GeoCarbon mini harita**  
   Nevşehir → işleyici → Türkiye içi veya Almanya/Hollanda alıcı rotası.

4. **Reason codes / feature importance**  
   “high_value_uplift”, “favorable_fx_rate”, “near_processor”, “low_carbon_route”.

5. **Model Evidence ekranı**  
   Benchmark planı, dataset özeti, ablation mantığı.

Advanced/Future:

- SHAP plot,
- Pareto frontier,
- karbon fiyatı simülasyonu,
- multi-leg lojistik animasyonu.

---

## 9. Pitch ve Sunum Stratejisi

### 9.1 Pitch yapısı — 3 dakika

#### 0:00–0:20 — Problem hook

> “Nevşehir/TR71 bölgesi pomza gibi güçlü hammaddelere sahip. Ancak yerel üretici çoğu zaman ham veya düşük katma değerli satış yapıyor. Asıl değer, doğru işleme rotası ve doğru B2B eşleşmeyle oluşuyor.”

#### 0:20–0:50 — Çözüm tek cümle + ekran

> “Raw2Value AI, hammaddeyi hangi işleme rotasıyla, hangi işleyici ve hangi alıcıyla daha kârlı ve düşük karbonlu değerlendirebileceğini ML tabanlı olarak öneren bir karar destek sistemidir.”

#### 0:50–1:50 — Canlı demo

- Pomza seçilir.
- Lokasyon: Nevşehir.
- Tonaj: 100 ton.
- Hedef pazar: İstanbul / Almanya / Hollanda karşılaştırması.
- AI Decision Cockpit öneriyi gösterir.
- Canlı TCMB kuru görünür.
- CO₂ resmi emisyon faktörüyle hesaplanır.
- Nearby processor filtresi gösterilir.

#### 1:50–2:20 — Akıllı taraf

- Value Route Optimizer sonucu gösterilir.
- B2B Match Finder sonucu gösterilir.
- Reason codes ve feature importance açılır.
- Kur/maliyet slider’ı oynatılır; öneri değişirse canlı gösterilir.

Benchmark metrikleri gerçekten üretilmediyse kesin rakam vermeyin.

Doğru ifade:

> “Model Lab ekranında rule-based baseline ile gradient boosting modellerini karşılaştırıyoruz. Gerçek eğitim sonuçları demo seti üzerinde bu tabloda gösteriliyor; placeholder olan değerleri kesin sonuç gibi sunmuyoruz.”

#### 2:20–2:50 — Kural uyumu

- Kural 1: OpenRouteService mesafe + resmi CO₂ faktörü.
- Kural 2: TCMB EVDS canlı kur + kâr/rota kararına etkisi.
- Kural 3: Nearby processor filtering.

#### 2:50–3:00 — Kapanış

> “Raw2Value AI bir marketplace değil; Kapadokya hammaddesini katma değerli tedarik zincirine bağlayan ML tabanlı karar motorudur.”

### 9.2 Slide tasarımı

- Maksimum 8 slide.
- Canlı ekran görüntüleri ve UI öncelikli.
- Ana ekran AI Decision Cockpit olmalı.
- Harita tek başına ana mesaj olmamalı.
- Kural uyumu ayrı net slaytta gösterilmeli.
- Eğer benchmark sayıları placeholder ise açıkça işaretlenmeli.

### 9.3 Hatırlanabilir slogan

Türkçe ana slogan:

> “Hammaddeyi değil, katma değeri yönetin.”

İngilizce destek sloganı:

> “Don’t sell the rock. Sell the value.”

---

## 10. Jüri Q&A — Zor Sorular ve Düzeltilmiş Cevaplar

### S: Bu sistemin akıllı tarafı ne?

**C:** Raw2Value AI; hammadde, tonaj, kalite, canlı kur, mesafe, karbon, işleme maliyeti ve talep verisini kullanarak en uygun işleme rotasını ve B2B eşleşmeyi skorlayan ML tabanlı karar motorudur. LLM varsa yalnızca açıklama üretir; iş kararını model/skorlama katmanı verir.

### S: Bu sadece marketplace değil mi?

**C:** Hayır. Marketplace alıcı-satıcı listeler. Raw2Value önce “bu hammadde neye dönüşürse daha fazla değer yaratır?” sorusunu çözer; sonra işleyici ve alıcı eşleşmesini önerir.

### S: Aynı şeyi Excel’de yapamaz mıyım?

**C:** Excel tek bir deterministik formül verir. Raw2Value ise alternatif rotaları, canlı kur değişimini, mesafe/karbon etkisini, işleme maliyetini, hedef pazarı ve B2B eşleşmeyi aynı karar ekranında karşılaştırır. Ayrıca what-if ile kararın nasıl değiştiğini gösterir.

### S: Weighted match score “sihirli sayı” değil mi?

**C:** MVP’de ağırlıklar gizli değildir; kullanıcı önceliğine göre görünür şekilde değişir. Örneğin düşük karbon önceliği seçildiğinde karbon ağırlığı artar. Gerçek işlem verisi geldikçe bu katman learning-to-rank modeline dönüştürülecek.

### S: SHAP açıklaması nihai kullanıcı için anlamlı mı?

**C:** MVP’de kullanıcıya doğrudan SHAP grafiği göstermiyoruz; reason codes ve feature importance gösteriyoruz. SHAP teknik jüri veya Model Lab için advanced açıklanabilirlik katmanı olarak kalabilir.

### S: Sentetik veriyle eğitilen model gerçek dünyada çalışır mı?

**C:** Hackathon MVP’sinde hibrit veri stratejisi kullanıyoruz: gerçek/referans veri + domain-informed augmentation. Bu veri pilot gerçek işlem verisinin yerine geçmez; ama senaryo çeşitliliği sağlar. Pilot aşamada gerçek teklif ve satış verisi geldikçe model yeniden eğitilir.

### S: Üretici nem/saflık bilgisini bilmiyorsa sistem çalışır mı?

**C:** Evet. Basic Mode’da üretici yalnızca hammadde, lokasyon, tonaj, gözle kalite ve ürün formu girer. Teknik değerler bilinmiyorsa sistem bölgesel varsayılan aralık kullanır ve confidence skorunu düşürür.

### S: İşleyici sadece dışarıdan alan tesis mi?

**C:** Hayır. Sistem capability-based çalışır. Bir işleyici hem dışarıdan hammadde alabilir hem kendi hammaddesine sahip olabilir. Bu durumda sistem onu hem tedarikçi hem işleyici olarak değerlendirir.

### S: Karbon hesabında hangi faktörü kullandınız?

**C:** Hackathon demo modunda kural dosyasındaki resmi faktörleri kullanıyoruz: kara/TIR 0.100, deniz 0.015, demiryolu 0.030, hava 0.500 kg CO₂/ton-km. CO₂ = tonaj × mesafe × emisyon faktörü.

### S: Pilot müşteri var mı?

**C:** Hackathon sonrası ilk hedefimiz Nevşehir TSO, OSB, ticaret borsası ve yerel işleyicilerle görüşerek gerçek teklif/satış verisi toplamaktır. Bunu kesinleşmiş anlaşma gibi değil, pilot hedefi olarak konumlandırıyoruz.

---

## 11. Akademik Referans Listesi

### Doğrulanmış / güçlü referanslar

1. **Chawla, Bowyer, Hall, Kegelmeyer (2002).** *SMOTE: Synthetic Minority Over-sampling Technique.* Journal of Artificial Intelligence Research, 16, 321–357. DOI: 10.1613/jair.953
2. **He, Bai, Garcia, Li (2008).** *ADASYN: Adaptive Synthetic Sampling Approach for Imbalanced Learning.* IJCNN 2008. DOI: 10.1109/IJCNN.2008.4633969
3. **Chen & Guestrin (2016).** *XGBoost: A Scalable Tree Boosting System.* KDD '16. DOI: 10.1145/2939672.2939785
4. **Ke et al. (2017).** *LightGBM: A Highly Efficient Gradient Boosting Decision Tree.* NeurIPS 2017.
5. **Prokhorenkova et al. (2018).** *CatBoost: unbiased boosting with categorical features.* NeurIPS 2018. arXiv: 1706.09516
6. **Lundberg & Lee (2017).** *A Unified Approach to Interpreting Model Predictions.* NeurIPS 2017.
7. **Xu et al. (2019).** *Modeling Tabular data using Conditional GAN.* NeurIPS 2019.
8. **Efron (1979).** *Bootstrap Methods: Another Look at the Jackknife.* Annals of Statistics, 7(1), 1–26.
9. **Burges (2010).** *From RankNet to LambdaRank to LambdaMART: An Overview.* Microsoft Research Technical Report MSR-TR-2010-82.

### Doğrulanmalı / dikkatli kullanılmalı

- SMOGN regression-oriented oversampling kaynakları.
- TR71 pomza/perlit istatistikleri için MTA/MAPEG orijinal raporları.
- Ticari pazar kaynakları: Volza, TradeKey, tradedata.pro, Grand View Research özetleri. Bunlar fiyat bandı ve pazar sinyali için kullanılabilir ama resmi veri gibi sunulmamalıdır.

**Kural:** Kaynak uydurmayın. Emin olmadığınız her sayıya “doğrulanmalı” veya “varsayım” notu ekleyin.

---

## 12. 24 Saatlik Zaman Yönetimi Önerisi

Final MVP’ye göre sadeleştirilmiş zaman planı:

| Saat | Aksiyon |
|---|---|
| 0–2 | Veri şeması finalize, mini katalog taslağı, ekip rol dağılımı |
| 2–5 | TCMB EVDS + Nominatim/OpenRouteService + CO₂ servisleri |
| 5–8 | Domain-informed dataset + augmentation pipeline |
| 8–11 | Model 1: value/profit prediction + Model 2: route recommendation |
| 11–13 | B2B Match Finder: weighted scoring + reason codes |
| 13–17 | AI Decision Cockpit + route comparison + mini map |
| 17–19 | What-if simulator + confidence / reason codes |
| 19–21 | Model Evidence ekranı + benchmark/ablation planı |
| 21–22 | README + kural uyum tablosu + demo script |
| 22–23 | Demo video / canlı demo provası |
| 23–24 | Buffer, bug fix, final pitch provası |

### MVP’de kesin yapılacaklar

- AI Decision Cockpit
- Value Route Optimizer
- B2B Match Finder
- TCMB EVDS canlı kur
- OpenRouteService/Nominatim mesafe/rota
- resmi hackathon emisyon faktörleriyle CO₂
- nearby processor filtering
- what-if simulator
- reason codes / feature importance
- Model Evidence ekranı

### Advanced / Future Work

- LightGBM/XGBoost Ranker
- SHAP force plot / summary
- Pareto frontier
- multi-leg lojistik
- CBAM karbon fiyatı
- FX volatility feature’ları
- CTGAN/TVAE deep augmentation
- tam PDF passport
- mobil responsive

---

## 13. Final Tavsiye — Tek Cümlelik Strateji

> “Pomzayı ana demo yapın; perlit ve kabak çekirdeğini destekleyici genelleme örneği olarak tutun. AI Decision Cockpit’te canlı kur, resmi karbon hesabı, yakın işleyici filtresi ve what-if simülasyonu ile model kararının değiştiğini gösterin. Ranker, SHAP, Pareto ve çok katmanlı karbon gibi iyi ama ağır fikirleri advanced olarak konumlandırın; MVP’yi çalışan, anlaşılır ve savunulabilir tutun.”

---

## 14. Revizyon Kontrol Listesi

- [x] Ana kategori Kategori 3 olarak korundu.
- [x] Pomza ana demo olarak korundu.
- [x] Perlit destek hammadde olarak korundu.
- [x] Kabak çekirdeği future work’e atılmadı, %10 destek olarak korundu.
- [x] AI Decision Cockpit ana demo ekranı yapıldı.
- [x] Harita ana demo olmaktan çıkarıldı, destek paneli olarak konumlandı.
- [x] Karbon hesabı hackathon resmi emisyon faktörlerine göre düzeltildi.
- [x] GLEC/IMO/EPA alternatifleri future work’e taşındı.
- [x] FX volatility ve gelişmiş finansal feature’lar advanced yapıldı.
- [x] LightGBM/XGBoost Ranker advanced yapıldı.
- [x] Pareto frontier advanced yapıldı.
- [x] SHAP advanced yapıldı; MVP explainability reason codes/feature importance oldu.
- [x] Benchmark metriklerinin placeholder/gerçek ayrımı vurgulandı.
- [x] Capability-based role model eklendi.
- [x] İşleyicinin kendi hammaddesine sahip olabileceği eklendi.
- [x] Basic Mode / Advanced Mode eklendi.
- [x] Teknik hammadde alanları opsiyonel hale getirildi.
- [x] Mini-katalog önerisi korundu ama Google Maps uygulama içi zorunlu API olmaktan çıkarıldı.
- [x] Pilot müşteri iddiası kesin anlaşma gibi değil, hedef olarak yazıldı.
- [x] Multi-leg lojistik future work’e taşındı.
- [x] 24 saat planı B-lite MVP’ye göre sadeleştirildi.

---

*Bu rapor Raw2Value AI hackathon ekibi için stratejik analiz dokümanıdır. Akademik referansların DOI doğrulamaları yapılmalıdır. Pazar verileri resmi kaynak, akademik kaynak, ticari kaynak ve varsayım olarak ayrı işaretlenmelidir.*