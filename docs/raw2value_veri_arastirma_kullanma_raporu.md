# Raw2Value AI — Veri Araştırma ve Kullanma Raporu

> **Amaç:** Bu doküman, Raw2Value AI projesinde veri araştırması yapacak ekip üyelerinin neyi, neden, nereden ve hangi model feature’ına dönüşecek şekilde araştıracağını netleştirir. Bu rapor, proje ana raporu ve model/augmentation kararlarıyla birlikte kullanılmalıdır.

---

## 0. Veri çalışmasının amacı

Raw2Value AI’da veri toplama amacı yalnızca “model eğitelim” değildir. Veri çalışmasının asıl amacı şu üç şeyi kanıtlamaktır:

1. **Bölgede gerçekten katma değer problemi var.**  
   Pomza, perlit ve kabak çekirdeği ham veya düşük katma değerli satılabiliyor; işleme, paketleme, mikronizasyon, genleştirme, soğuk pres, lojistik ve hedef pazar seçimiyle daha yüksek değerli ürünlere dönüşebiliyor.

2. **Modelin karar verebilmesi için ölçülebilir feature’lar var.**  
   Hammadde türü, tonaj, kalite, işleme rotası, fiyat, maliyet, mesafe, CO₂, canlı kur, hedef pazar, alıcı talebi ve teslim süresi gibi değişkenler model girdisine dönüşebilir.

3. **Sentetik augmentation rastgele değil, domain-informed olacak.**  
   Uydurma veri üretmeyeceğiz. Gerçek kaynaklardan alınan aralıkları, koordinatları, fiyatları, maliyetleri ve iş mantığını kullanarak kontrollü senaryo verisi oluşturacağız.

Raw2Value AI’ın temel iddiası şudur:

> Raw2Value AI bir marketplace veya LLM chatbot değildir. Pomza, perlit ve kabak çekirdeği için katma değerli işleme rotası, kâr/değer artışı, karbon, canlı döviz etkisi ve B2B eşleşme kararlarını ML tabanlı olarak üreten bir akıllı tedarik zinciri karar motorudur.

---

## 1. Final veri kapsamı

### 1.1 MVP’de yalnızca 3 hammadde

Araştırma sadece şu üç hammaddeye odaklanacaktır:

| Öncelik | Hammadde | Kullanım |
|---|---|---|
| 1 | **Pomza / ponza** | Ana demo hammaddesi |
| 2 | **Perlit** | Mineral tarafında genellenebilirlik |
| 3 | **Kabak çekirdeği** | Tarımsal katma değer örneği |

Ağırlık:

```text
Pomza: %70
Perlit: %20
Kabak çekirdeği: %10
```

5+ hammaddeye genişlemiyoruz. Kaolen, zeolit, patates, üzüm, kalsit gibi ürünler araştırılırsa yalnızca **future work / genişleme** olarak not alınacaktır. Ana veri setine dahil edilmeyecektir.

### 1.2 Coğrafi kapsam

```text
Hammadde kaynağı: Nevşehir / TR71
İşleyici lokasyonu: TR71 + yakın sanayi merkezleri
B2B alıcı lokasyonu: Türkiye geneli + seçili ihracat pazarları
```

Türkiye içi örnek alıcı şehirleri:

```text
İstanbul
Ankara
Antalya
İzmir
Kayseri
Mersin
```

Seçili ihracat pazarları:

```text
Almanya
Hollanda
```

Bangladeş, denim yıkama taşı açısından ilginç bir sektör referansı olarak tutulabilir; ancak ana demo Almanya/Hollanda + Türkiye içi B2B alıcılarla daha temiz ve yönetilebilir olmalıdır.

---

## 2. Veri ekibinin ana görevi

Veri ekibi iki tip veri toplayacaktır.

### A) Gerçek / referans veri

Bunlar gerçek kaynaklardan alınacaktır:

- hammadde üretim miktarı
- rezerv / bölgesel önem
- ham ürün fiyat aralıkları
- işlenmiş ürün fiyat aralıkları
- işleme maliyeti tahminleri
- örnek işleyici firmalar
- örnek B2B alıcı sektörleri
- üretici / işleyici / alıcı şehirleri ve koordinatları
- resmi karbon emisyon faktörleri
- canlı kur API bilgisi
- hedef pazar / talep göstergeleri

### B) Domain-informed augmentation için aralıklar

Bunlar veri üretmek için kullanılacak mantıklı aralıklardır:

- tonaj aralıkları
- kalite sınıfları
- fiyat varyasyonları
- işleme maliyeti varyasyonları
- hedef pazar değişimleri
- döviz kuru senaryoları
- taşıma modu senaryoları
- mesafe senaryoları
- talep skoru aralıkları
- risk skoru aralıkları

Amaç rastgele veri üretmek değildir. Amaç, kaynaklardan alınan aralıklara göre kontrollü ve savunulabilir senaryolar üretmektir.

---

## 3. Modelimizin hangi verilere ihtiyacı var?

Raw2Value AI’da iki ana ürün fonksiyonu vardır:

1. **Value Route Optimizer**
2. **B2B Match Finder**

### 3.1 Value Route Optimizer

Bu fonksiyon şu soruya cevap verir:

> “Bu hammaddeyi ham mı satmalıyım, işleyip mi satmalıyım, hangi işleme rotası daha kârlı ve sürdürülebilir?”

Modelin ihtiyaç duyduğu veri grupları:

| Veri grubu | Örnek feature’lar | Ne işe yarar? |
|---|---|---|
| Hammadde bilgisi | raw_material, raw_subtype | Pomza/perlit/kabak ayrımı |
| Miktar | tonnage | Gelir, maliyet, taşıma ve CO₂ hesabı |
| Kalite | quality_grade, quality_unknown | Fiyat ve rota seçimi |
| Teknik bilgi | moisture_pct, purity_pct, particle_size_class | Gelişmiş modda rota güvenini artırır |
| İşleme rotası | processing_route | Hangi ürüne dönüşeceğini belirler |
| Fiyat | raw_price, processed_price | Kâr ve değer artışı hesabı |
| Maliyet | processing_cost, packaging_cost, transport_cost | Net kâr hesabı |
| Coğrafya | source_city, processor_city, buyer_city, distance_km | Lojistik maliyet + CO₂ |
| Döviz | usd_try, eur_try | İhracat kârlılığı |
| Karbon | transport_mode, emission_factor, co2_kg | Kural 1 + sürdürülebilirlik skoru |
| Talep | demand_score, buyer_sector | Pazar uygunluğu |
| Risk | delivery_risk, price_volatility_risk | Match ve rota skoru |

### 3.2 B2B Match Finder

Bu fonksiyon şu soruya cevap verir:

> “Bu üretici/hammadde için en uygun işleyici ve alıcı kim?”

Modelin ihtiyaç duyduğu veri grupları:

| Veri grubu | Örnek feature’lar | Ne işe yarar? |
|---|---|---|
| Üretici bilgisi | supplier_location, raw_material, tonnage | Tedarik başlangıcı |
| İşleyici bilgisi | processor_type, capacity, accepted_materials | İşleme uygunluğu |
| Alıcı bilgisi | buyer_sector, buyer_country, required_quality | Talep uygunluğu |
| Mesafe | source_to_processor_km, processor_to_buyer_km | Maliyet + teslim süresi |
| Kapasite | processor_capacity_ton_month | Tonajı karşılayabilir mi? |
| Kalite eşleşmesi | quality_match_score | Alıcı şartını karşılıyor mu? |
| Kâr | expected_profit_try | En ekonomik eşleşme |
| Karbon | co2_kg | En düşük karbonlu seçenek |
| Teslim süresi | lead_time_days | Hızlı teslim |
| Kur etkisi | fx_impact_score | İhracat kararına etkisi |

---

## 4. Araştırılacak veri başlıkları

### 4.1 Hammadde bölgesel önem verisi

Her hammadde için şu sorular cevaplanacaktır:

| Soru | Neden gerekli? |
|---|---|
| Bu hammadde Nevşehir/TR71 için gerçekten önemli mi? | Proje bağlamı |
| Üretim miktarı veya rezerv bilgisi var mı? | Problem kanıtı |
| Nerelerde yoğunlaşıyor? | Harita ve kaynak lokasyonu |
| Ham satışı yaygın mı? | Katma değer problemi |
| İşlenmiş ürüne dönüşme potansiyeli var mı? | Model rotası |
| AHİKA/TR71 planında destekleyen veri var mı? | Jüri savunması |

### 4.2 Pomza için araştırılacaklar

- Nevşehir pomza rezervi
- Türkiye pomza üretimindeki konumu
- Nevşehir’de pomza ocakları / işletme ruhsatları
- Pomza kullanım alanları
- Ham pomza fiyatı
- Bims blok / hafif agrega fiyatları
- Mikronize pomza fiyatı
- Filtrasyon medyası fiyatı
- Tekstil yıkama taşı fiyatı
- Örnek firmalar:
  - Nevşehir / Kayseri bims firmaları
  - mikronizasyon tesisleri
  - pomza ihracatçıları
- Hedef sektörler:
  - inşaat
  - tekstil
  - kozmetik
  - filtrasyon
  - tarım

### 4.3 Perlit için araştırılacaklar

- Türkiye perlit rezervi
- TR71 / Nevşehir / Acıgöl bağlantısı
- Ham perlit fiyatı
- Genleştirilmiş perlit fiyatı
- Perlit işleme maliyeti
- Genleştirme tesisleri
- Hedef sektörler:
  - tarım substratı
  - izolasyon
  - filtrasyon
  - kriyojenik dolgu
  - hafif yapı malzemesi

### 4.4 Kabak çekirdeği için araştırılacaklar

- Nevşehir kabak çekirdeği üretim miktarı
- Coğrafi işaret bilgisi
- Dökme satış fiyatı
- Kavrulmuş/paketli ürün fiyatı
- Kabak çekirdeği yağı fiyatı
- Kavurma/paketleme/soğuk pres maliyetleri
- Hedef sektörler:
  - çerez firmaları
  - sağlıklı gıda
  - gurme market
  - turistik hediyelik
  - ihracat gıda distribütörleri

---

## 5. Nerelerde araştırma yapılacak?

### 5.1 Öncelik A — Resmi ve güvenilir kaynaklar

Bunlar en güvenilir kaynaklardır. Rapor ve sunumda öncelikle bunlar kullanılmalıdır.

| Kaynak | Ne aranacak? |
|---|---|
| TÜİK | Üretim miktarı, tarımsal ürün verisi, fiyat varsa üretici fiyatı |
| TCMB EVDS | USD/TRY, EUR/TRY canlı kur |
| MTA | Pomza/perlit rezerv ve maden bilgisi |
| MAPEG | Maden ruhsat / rezerv / sektör bilgisi |
| AHİKA / Kalkınma Kütüphanesi | TR71 bölge planı, fizibilite raporları |
| Sanayi ve Teknoloji Bakanlığı | OSB, bölgesel sanayi verisi |
| Ticaret Bakanlığı | İhracat / GTİP / ülke pazarı bilgileri |
| TÜİK Dış Ticaret | Ürün bazlı ihracat / ithalat verisi |
| USGS | Pomza/perlit küresel üretim verileri |

### 5.2 Öncelik B — Akademik kaynaklar

| Kaynak | Ne aranacak? |
|---|---|
| Dergipark | Nevşehir pomza, perlit, kabak çekirdeği, bölgesel üretim çalışmaları |
| Google Scholar | Pumice value added products, perlite expanded products, pumpkin seed oil market |
| MDPI / ScienceDirect / Springer | Supply chain ML, synthetic data, XGBoost, route optimization |
| Akademik tezler | Pomza işleme, perlit genleştirme, kabak çekirdeği yağı |

### 5.3 Öncelik C — Sektörel ve ticari kaynaklar

Bunlar kullanılabilir ama güven seviyesi daha düşüktür. Mutlaka “tahmini / piyasa gözlemi / ticari listeleme” olarak işaretlenmelidir.

| Kaynak | Ne aranacak? |
|---|---|
| Firma web siteleri | Kapasite, ürün çeşitleri, lokasyon |
| Alibaba / TradeKey / Made-in-China | Fiyat bandı, ürün çeşitleri |
| Volza / Trademap / WITS / Comtrade | İhracat pazarları, ürün ticareti |
| Yerel haberler | Üretim miktarı, sektör sorunları |
| Ticaret borsası sayfaları | Kabak çekirdeği fiyat / üretim bilgisi |
| OSB firma listeleri | İşleyici ve B2B alıcı adayları |

### 5.4 Öncelik D — Varsayım üretilecek alanlar

Bunlar gerçek kaynak bulunamazsa tahmini kalabilir:

- demand_score
- risk_score
- processing_cost_usd_ton
- packaging_cost
- buyer_credit_score
- quality_match_score
- delivery_risk
- price_volatility_risk

Ancak bu değerler tamamen rastgele yazılmamalıdır. Her biri için 0–1 arası veya düşük/orta/yüksek gibi kontrollü skala oluşturulmalıdır.

---

## 6. Kaynak güven seviyesi sistemi

Veri toplarken her bilgiye bir güven seviyesi verilecektir.

| Seviye | Kaynak tipi | Örnek | Kullanım |
|---|---|---|---|
| A | Resmi / kamu / açık veri | TÜİK, TCMB, MTA, USGS, AHİKA | Sunumda güçlü kanıt |
| B | Akademik / sektörel | Dergipark, akademik makale, fizibilite raporu | Model ve problem gerekçesi |
| C | Ticari / pazar verisi | TradeKey, Volza, firma sayfası | Fiyat bandı / pazar sinyali |
| D | Varsayım / tahmin | demand_score, risk_score | Augmentation ve demo |

Her veri satırında mümkünse şu alanlar olmalıdır:

```csv
source_name, source_url, source_confidence_level, value_type, notes
```

Örnek:

```csv
pomza_raw_price_usd_ton,WITS HS251311,A,observed_market_average,"2023 FOB average"
mikronize_pomza_price_usd_ton,TradeKey listings,C,market_listing_range,"not official price"
demand_score_germany_cosmetics,team_assumption,D,assumption,"based on target sector relevance"
```

---

## 7. Feature grupları

### 7.1 Hammadde feature’ları

| Feature | Tip | Örnek | Kaynak |
|---|---|---|---|
| raw_material | categorical | pomza | kullanıcı input |
| raw_subtype | categorical | beyaz pomza / ham perlit / çerezlik kabak | araştırma |
| origin_city | categorical | Nevşehir | kullanıcı input |
| origin_district | categorical | Acıgöl | kullanıcı input |
| tonnage | numeric | 100 | kullanıcı input |
| quality_grade | categorical | A/B/C/unknown | kullanıcı input |
| product_form | categorical | ham kaya / kırılmış / elenmiş / toz | kullanıcı input |
| technical_data_available | boolean | true/false | kullanıcı input |
| moisture_pct | numeric/nullable | 7.5 | opsiyonel |
| purity_pct | numeric/nullable | 92 | opsiyonel |
| particle_size_class | categorical/nullable | fine / medium / coarse | opsiyonel |

### 7.2 Basic Mode / Advanced Mode

Üretici teknik değerleri bilmek zorunda değildir.

#### Basic Mode feature’ları

```csv
raw_material
origin_city
origin_district
tonnage
quality_grade_or_unknown
product_form
target_market
business_priority
```

#### Advanced Mode feature’ları

```csv
moisture_pct
purity_pct
particle_size_class
density
lab_report_uploaded
technical_spec_uploaded
```

Eksik teknik bilgi varsa:

```csv
default_values_used = true
data_confidence_score = lower
model_confidence_score = lower
```

Bu çok önemlidir çünkü üretici/köylü/KOBİ nem veya saflık değerini bilmeyebilir. Sistem buna rağmen çalışmalıdır.

---

## 8. İşleme rotası feature’ları

Her hammadde için rota adayları sabit tanımlanacaktır.

### 8.1 Pomza rota adayları

| Route code | Açıklama |
|---|---|
| raw_sale | Ham pomza satışı |
| bims_aggregate | Bims/blok üreticisine satış |
| micronized_pumice | Mikronize pomza |
| filtration_media | Filtrasyon medyası |
| textile_washing_stone | Tekstil/denim yıkama taşı |

### 8.2 Perlit rota adayları

| Route code | Açıklama |
|---|---|
| raw_sale | Ham perlit satışı |
| expanded_perlite | Genleştirilmiş perlit |
| agriculture_substrate | Tarım substratı |
| insulation_filler | İzolasyon dolgusu |
| filtration_product | Filtrasyon ürünü |

### 8.3 Kabak çekirdeği rota adayları

| Route code | Açıklama |
|---|---|
| bulk_sale | Dökme satış |
| roasted_packaged | Kavrulmuş/paketli premium ürün |
| pumpkin_seed_oil | Kabak çekirdeği yağı |
| protein_powder | Protein/toz ürün |
| tourism_gift_pack | Turistik hediyelik paket |

Her rota için araştırılacak veri:

```csv
raw_material
processing_route
required_processing_step
processed_product_name
target_sector
raw_price_range
processed_price_range
processing_cost_range
packaging_cost_range
minimum_tonnage
quality_requirement
demo_feasibility
```

---

## 9. Coğrafi ve karbon verisi

Hackathon kuralları gereği CO₂ hesabı coğrafi veri kullanılarak yapılmalı ve kullanıcıya görsel sunulmalıdır. Mesafe/konum verisi yalnızca hardcoded olmamalı; açık kaynak API veya veri seti kullanılmalıdır.

### 9.1 Coğrafi feature’lar

| Feature | Açıklama |
|---|---|
| source_lat | Hammadde kaynağı enlem |
| source_lon | Hammadde kaynağı boylam |
| processor_lat | İşleyici enlem |
| processor_lon | İşleyici boylam |
| buyer_lat | Alıcı enlem |
| buyer_lon | Alıcı boylam |
| source_to_processor_km | Kaynak → işleyici mesafesi |
| processor_to_buyer_km | İşleyici → alıcı mesafesi |
| total_distance_km | Toplam rota mesafesi |
| radius_to_processor_km | Nearby processor filtresi |
| nearest_processor_distance_km | En yakın işleyici mesafesi |

### 9.2 Kullanılacak API’ler

| API | Ne için? |
|---|---|
| Nominatim / OpenStreetMap | Adres → koordinat |
| OpenRouteService | Gerçek rota mesafesi |
| Overpass API | OSB / sanayi / tesis arama |
| TCMB EVDS | Canlı döviz kuru |

### 9.3 Resmi emisyon faktörleri

Hackathon demo modunda sadece şu faktörler kullanılacaktır:

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
100 ton × 850 km × 0.100 = 8,500 kg CO₂
```

Veri araştırmacıları 0.062 gibi farklı akademik faktörler bulursa bunları “alternatif metodoloji / future work” olarak not edebilir; ancak demo hesabında resmi hackathon faktörleri kullanılacaktır.

---

## 10. Döviz ve fiyat verisi

Hackathon kuralına göre TCMB EVDS canlı kur sadece gösterilmeyecek; iş kararını doğrudan etkileyecektir. Kur verisi fiyatlandırma, kârlılık, ihracat rotası veya önerilen işleme rotası üzerinde etkili olmalıdır.

### 10.1 Kur feature’ları

| Feature | Açıklama |
|---|---|
| usd_try | TCMB USD/TRY |
| eur_try | TCMB EUR/TRY |
| fx_last_updated | Son güncelleme zamanı |
| target_currency | TRY/USD/EUR |
| fx_scenario_pct | What-if slider için değişim yüzdesi |
| fx_impact_score | Kurun kâr kararına etkisi |

### 10.2 Fiyat araştırması

Her hammadde/rota için şu fiyatlar aranacaktır:

| Veri | Açıklama |
|---|---|
| raw_price_try_ton | Ham ürün TL/ton |
| raw_price_usd_ton | Ham ürün USD/ton |
| processed_price_try_ton | İşlenmiş ürün TL/ton |
| processed_price_usd_ton | İşlenmiş ürün USD/ton |
| processing_cost_try_ton | İşleme maliyeti |
| packaging_cost_try_ton | Paketleme maliyeti |
| transport_cost_try_ton_km | Taşıma maliyeti |
| export_handling_cost | İhracat/liman/doküman tahmini |
| price_source_level | A/B/C/D güven seviyesi |

### 10.3 Fiyat verisinde dikkat

Fiyatların çoğu kesin olmayacaktır. Bu yüzden tek değer değil, aralık toplanmalıdır:

```csv
raw_price_min
raw_price_max
raw_price_typical
processed_price_min
processed_price_max
processed_price_typical
```

Örnek:

```csv
pomza,micronized_pumice,processed_price_usd_ton,200,300,250,C,"market listing"
```

---

## 11. Model target’ları

### 11.1 expected_profit_try

Model 1 için ana target.

Basit formül:

```text
raw_material_cost_try = raw_price_usd_ton × fx_rate × tonnage

processed_revenue_try = processed_price_usd_ton × fx_rate × tonnage

processing_total_cost_try = processing_cost_try_ton × tonnage

transport_total_cost_try = transport_cost_try_ton_km × total_distance_km × tonnage

packaging_total_cost_try = packaging_cost_try_ton × tonnage

expected_profit_try =
processed_revenue_try
- raw_material_cost_try
- processing_total_cost_try
- transport_total_cost_try
- packaging_total_cost_try
```

Eğer hammadde üreticinin veya işleyicinin kendi hammaddesiyse `raw_material_cost_try` farklı yorumlanabilir:

```text
kendi hammaddesi varsa:
raw_material_cost_try = opportunity_cost
```

Yani üretici veya işleyici ham satabileceği değeri fırsat maliyeti olarak görür.

### 11.2 value_uplift_pct

Ham satışa göre değer artışı:

```text
raw_sale_profit_try = raw_price_usd_ton × fx_rate × tonnage - direct_transport_cost

value_uplift_pct =
(expected_profit_try - raw_sale_profit_try) / abs(raw_sale_profit_try)
```

Alternatif daha basit demo formülü:

```text
value_uplift_pct =
(processed_price_usd_ton - raw_price_usd_ton - processing_cost_usd_ton)
/ raw_price_usd_ton
```

### 11.3 recommended_route_label

Model 2 için target.

Her senaryo için en iyi rota şöyle belirlenebilir:

```text
recommended_route_label = max(route_score)
```

`route_score` formülü:

```text
route_score =
0.45 × normalized_profit_score
+ 0.20 × demand_score
+ 0.15 × carbon_score
+ 0.10 × delivery_score
+ 0.10 × confidence_score
```

Bu formül sentetik label üretmek için kullanılabilir. Model daha sonra bu label’ı öğrenir.

### 11.4 match_score

B2B Match Finder için MVP skoru:

```text
match_score =
0.35 × profit_score
+ 0.20 × demand_match_score
+ 0.15 × distance_score
+ 0.15 × carbon_score
+ 0.10 × delivery_score
+ 0.05 × quality_match_score
```

Eğer alıcı “düşük karbon” önceliği seçerse ağırlıklar değişebilir:

```text
low_carbon_priority:
carbon_score = 0.30
profit_score = 0.25
```

Bu, what-if simülatöründe gösterilebilir.

---

## 12. Target leakage uyarısı

Veri ekibi şuna çok dikkat edecektir:

> Target değişkenleri model input’una doğrudan sokulmayacak.

Yanlış:

```csv
input_features = expected_profit_try, value_uplift_pct, match_score
target = recommended_route_label
```

Doğru:

```csv
input_features =
raw_material,
tonnage,
quality_grade,
processing_route_candidate,
raw_price,
processed_price,
processing_cost,
distance,
co2,
fx_rate,
demand_score,
lead_time

target =
expected_profit_try veya recommended_route_label
```

Özellikle `expected_profit_try` target olarak kullanılacaksa aynı modelin input’una konulmaz. `match_score` target veya skor çıktısıysa input olmamalıdır.

---

## 13. Dataset şeması

Aşağıdaki ana CSV şeması kullanılabilir.

```csv
sample_id,
raw_material,
raw_subtype,
origin_city,
origin_district,
origin_lat,
origin_lon,

user_role,
user_capabilities,
can_supply_raw_material,
can_process_material,
can_buy_material,
can_export,
has_storage,
has_transport_capacity,

input_mode,
technical_data_available,
quality_grade,
quality_unknown,
product_form,
moisture_pct,
purity_pct,
particle_size_class,
lab_report_uploaded,
default_values_used,
data_confidence_score,

tonnage,
processing_route_candidate,
processed_product_name,
processor_id,
processor_type,
processor_city,
processor_lat,
processor_lon,
processor_capacity_ton_month,
processor_accepts_material,
processor_has_own_raw_material,

buyer_id,
buyer_type,
buyer_sector,
buyer_city,
buyer_country,
buyer_lat,
buyer_lon,
buyer_required_quality,
buyer_required_tonnage,
buyer_currency,

raw_price_min_usd_ton,
raw_price_max_usd_ton,
raw_price_typical_usd_ton,
processed_price_min_usd_ton,
processed_price_max_usd_ton,
processed_price_typical_usd_ton,
processing_cost_min_usd_ton,
processing_cost_max_usd_ton,
processing_cost_typical_usd_ton,
packaging_cost_usd_ton,

source_to_processor_km,
processor_to_buyer_km,
total_distance_km,
transport_mode,
emission_factor_kg_co2_ton_km,
emission_factor_source,
co2_kg,
transport_cost_usd_ton_km,
transport_total_cost_usd,

usd_try,
eur_try,
fx_last_updated,
target_currency,
fx_scenario_pct,

demand_score,
quality_match_score,
delivery_score,
risk_score,
lead_time_days,

expected_profit_try,
value_uplift_pct,
recommended_route_label,
match_score,

source_name,
source_url,
source_confidence_level,
assumption_notes
```

---

## 14. Minimum MVP dataset boyutu

Gerçekçi hedef:

| Veri türü | MVP hedef |
|---|---:|
| Gerçek / referans / manuel kalibrasyon noktası | 50–150 |
| Augmentation sonrası satır | 1.000–3.000 |
| Demo için ideal | ~1.500 |

Dağılım:

| Hammadde | Oran | Yaklaşık satır |
|---|---:|---:|
| Pomza | %70 | 1.050 |
| Perlit | %20 | 300 |
| Kabak çekirdeği | %10 | 150 |

Bu MVP için yeterlidir. 10K+ satır advanced hedef olabilir ama MVP için şart değildir.

---

## 15. Augmentation stratejisi

### 15.1 Neden augmentation?

Gerçek B2B işlem verimiz yok. Ancak modelin farklı senaryoları görmesi gerekiyor:

- farklı tonajlar
- farklı kalite sınıfları
- farklı işleme rotaları
- farklı şehirler
- farklı alıcı pazarları
- farklı döviz kuru senaryoları
- farklı taşıma modları
- farklı maliyetler

Bu yüzden domain-informed augmentation yapılacaktır.

### 15.2 Augmentation kuralları

Her gerçek/referans satırdan 10–30 varyasyon üretilebilir.

| Feature | Augmentation mantığı |
|---|---|
| tonnage | log-uniform veya aralık içi örnekleme |
| quality_grade | A/B/C/unknown dağılımı |
| raw_price | kaynak aralığı içinde ±%5–15 |
| processed_price | rota bazlı aralık içinde ±%5–20 |
| processing_cost | rota bazlı maliyet aralığı |
| target_market | Türkiye içi / Almanya / Hollanda |
| transport_mode | road/sea/rail/air |
| fx_rate | canlı kur + ±%5/10/20 what-if |
| distance | gerçek şehir koordinatlarından API ile |
| co2 | formülle hesaplanır, random üretilmez |
| demand_score | pazar/ürün uyumuna göre kontrollü |

### 15.3 Random yapılmayacak alanlar

Şunlar rastgele yazılmayacaktır:

```text
co2_kg
total_distance_km
fx_rate
emission_factor
recommended_route_label
expected_profit_try
value_uplift_pct
```

Bunlar formül veya API ile hesaplanacaktır.

---

## 16. Akademik dayanak

Veri raporunda şu akademik yöntemleri kullanabilirsiniz:

| Yöntem | Raw2Value’da kullanım |
|---|---|
| Domain-informed synthetic data | Gerçek aralıklara dayalı veri artırma |
| Monte Carlo simulation | Kur, maliyet, talep senaryoları |
| Bootstrapping | Küçük gerçek veriden belirsizlik üretme |
| SMOTE | Route sınıflarında ciddi dengesizlik varsa opsiyonel |
| SMOGN | Çok yüksek/düşük kâr örnekleri azsa regression için opsiyonel |
| CTGAN / TVAE | Future work; 24 saat için şart değil |
| Feature importance | MVP açıklanabilirlik |
| SHAP | Advanced açıklanabilirlik |
| Benchmark | Modelin rule-based baseline’dan iyi olup olmadığını göstermek |
| Ablation | Kur/geo/karbon gerçekten kararı etkiliyor mu göstermek |

Akademik referans araştırmasında şu başlıkları aratın:

```text
SMOTE Chawla et al. 2002
ADASYN He et al. 2008
XGBoost Chen Guestrin 2016
LightGBM Ke et al. 2017
CatBoost Prokhorenkova 2018
SHAP Lundberg Lee 2017
CTGAN Xu et al. 2019
Bootstrap Efron 1979
SMOGN imbalanced regression
Learning to Rank LambdaMART Burges
Tabular data augmentation synthetic data survey
Supply chain machine learning gradient boosting
```

Not: Bu referanslar metodoloji dayanağı için kullanılacaktır. MVP’de hepsini uygulamak zorunda değiliz.

---

## 17. Benchmark planı

### 17.1 Regression benchmark

Amaç:

```text
expected_profit_try veya value_uplift_pct tahmini
```

Modeller:

| Model | Zorunlu mu? |
|---|---|
| Rule-based baseline | Evet |
| Linear Regression | Evet |
| Random Forest Regressor | Evet |
| XGBoost / LightGBM / CatBoost | En az biri |

Metrikler:

```text
MAE
RMSE
R²
MAPE, dikkatli kullanılmalı
```

### 17.2 Classification benchmark

Amaç:

```text
recommended_route_label tahmini
```

Modeller:

| Model | Zorunlu mu? |
|---|---|
| Majority class baseline | Evet |
| Logistic Regression | Opsiyonel |
| Random Forest Classifier | Evet |
| XGBoost / LightGBM / CatBoost Classifier | En az biri |

Metrikler:

```text
Accuracy
Macro F1
Weighted F1
Confusion matrix
Top-2 accuracy
```

### 17.3 Match scoring benchmark

MVP’de gerçek ranker şart değildir.

Karşılaştırılacaklar:

| Yöntem | MVP durumu |
|---|---|
| Manual weighted scoring | Kesin |
| ML-assisted weighted scoring | Kesin |
| XGBoost/LightGBM Ranker | Advanced |

Metrikler:

```text
Top-1 agreement
Top-3 agreement
NDCG@3, advanced
Manual sanity check
```

---

## 18. Ablation planı

Ablation çalışmasının amacı şunu göstermektir:

> Kur, mesafe ve karbon yalnızca ekranda görünen süs değil; model kararını etkiliyor.

| Çıkarılan feature grubu | Beklenen yorum |
|---|---|
| FX features çıkarıldı | İhracat rotası kararları zayıflar |
| Geo/distance çıkarıldı | İşleyici/alıcı eşleşmesi bozulur |
| Carbon features çıkarıldı | Düşük karbon tercihleri etkisizleşir |
| Demand features çıkarıldı | Pazar uygunluğu zayıflar |
| Quality features çıkarıldı | Teknik kaliteye bağlı rota ayrımı azalır |
| Processing cost çıkarıldı | İşlenmiş ürün kâr tahmini bozulur |

Rapor cümlesi:

```text
Ablation sonucunda FX, geo ve carbon feature grupları çıkarıldığında model skorunun ve önerilen rotanın değişmesi, bu zorunlu kuralların yalnızca gösterim değil karar mekanizmasının parçası olduğunu kanıtlar.
```

---

## 19. Arkadaşlara görev dağılımı

### Arkadaş 1 — Hammadde ve pazar araştırması

Sorumluluk:

```text
Pomza + perlit + kabak çekirdeği için gerçek kaynaklı veri toplamak.
```

Araştıracakları:

#### Pomza

- Nevşehir/Türkiye rezerv bilgisi
- üretim miktarı
- ham fiyat
- bims/hafif agrega fiyatı
- mikronize pomza fiyatı
- tekstil yıkama taşı fiyatı
- filtrasyon medyası pazarı
- işleyici firmalar
- alıcı sektörler

#### Perlit

- ham perlit fiyatı
- genleştirilmiş perlit fiyatı
- işleme maliyeti
- genleştirme tesisleri
- tarım/izolasyon/filtrasyon pazarları

#### Kabak çekirdeği

- Nevşehir üretim miktarı
- dökme fiyat
- kavrulmuş paketli fiyat
- kabak çekirdeği yağı fiyatı
- kavurma/paketleme/soğuk pres maliyeti
- alıcı sektörler

Teslim formatı:

```csv
raw_material,
data_point,
value_min,
value_max,
value_typical,
unit,
source_name,
source_url,
source_confidence_level,
notes
```

Örnek:

```csv
pomza,raw_price_usd_ton,75,105,91.7,USD/ton,WITS,A,"HS 251311 average"
pomza,micronized_price_usd_ton,200,300,250,USD/ton,TradeKey,C,"market listing, verify"
kabak_cekirdegi,bulk_price_try_kg,45,70,57,TRY/kg,TÜİK-derived,D,"estimated from production/economic contribution"
```

### Arkadaş 2 — Veri modeli, feature ve augmentation araştırması

Sorumluluk:

```text
Toplanan verinin modele nasıl gireceğini, hangi feature’a dönüşeceğini ve augmentation kurallarını hazırlamak.
```

Araştıracakları:

- XGBoost/LightGBM/CatBoost için tabular feature tasarımı
- missing value handling
- categorical encoding
- Basic Mode / Advanced Mode input mantığı
- domain-informed augmentation
- Monte Carlo scenario üretimi
- benchmark metrikleri
- ablation planı
- confidence score tasarımı
- target leakage kontrolü

Teslim formatı:

```csv
feature_name,
feature_group,
data_type,
source,
used_in_model_1,
used_in_model_2,
used_in_match_score,
required_or_optional,
default_strategy,
notes
```

Örnek:

```csv
tonnage,material,numeric,user_input,true,true,true,required,none,"main scale variable"
moisture_pct,technical,numeric,user_advanced_input,true,false,false,optional,regional_default,"lowers confidence if missing"
usd_try,fx,numeric,TCMB_EVDS,true,true,true,required,last_cached,"business decision feature"
co2_kg,carbon,numeric,formula,true,true,true,required,calculate_from_distance,"do not random generate"
```

---

## 20. Excel / Google Sheet yapısı

İki arkadaşın aynı dosyada çalışması için şu sheet’leri açın.

### Sheet 1 — `source_registry`

| source_id | source_name | source_url | source_type | confidence_level | owner | notes |
|---|---|---|---|---|---|---|

### Sheet 2 — `material_reference_data`

| raw_material | data_point | min | max | typical | unit | source_id | confidence | notes |
|---|---|---:|---:|---:|---|---|---|---|

### Sheet 3 — `processing_routes`

| raw_material | route_code | processed_product | processing_steps | target_sector | quality_requirement | demo_priority |
|---|---|---|---|---|---|---|

### Sheet 4 — `organizations`

| org_id | name | city | country | lat | lon | can_supply | can_process | can_buy | can_export | accepted_materials | notes |
|---|---|---|---:|---:|---|---|---|---|---|---|

### Sheet 5 — `buyer_markets`

| buyer_id | buyer_type | sector | city | country | required_product | required_quality | demand_score | source_id |
|---|---|---|---|---|---|---|---:|---|

### Sheet 6 — `feature_dictionary`

| feature | group | type | source | model_usage | required | default_strategy | leakage_risk |
|---|---|---|---|---|---|---|---|

### Sheet 7 — `augmentation_rules`

| feature | method | min | max | distribution | based_on_source | notes |
|---|---|---:|---:|---|---|---|

### Sheet 8 — `assumptions_log`

| assumption_id | assumption | reason | affected_features | confidence | how_to_validate_later |
|---|---|---|---|---|---|

---

## 21. Model için minimum feature set

Model ilk MVP’de en az şu feature’larla çalışabilir:

```csv
raw_material
processing_route_candidate
tonnage
quality_grade
quality_unknown
product_form
origin_district
processor_type
buyer_country
buyer_city
target_sector
raw_price_typical_usd_ton
processed_price_typical_usd_ton
processing_cost_typical_usd_ton
source_to_processor_km
processor_to_buyer_km
total_distance_km
transport_mode
emission_factor_kg_co2_ton_km
co2_kg
usd_try
eur_try
demand_score
lead_time_days
risk_score
data_confidence_score
```

Advanced feature’lar:

```csv
moisture_pct
purity_pct
particle_size_class
lab_report_uploaded
processor_capacity_ton_month
buyer_required_quality
buyer_credit_score
historical_completion_rate
seasonal_demand_index
carbon_priority_weight
profit_priority_weight
```

---

## 22. Confidence score tasarımı

Model yalnızca skor vermemeli; güven de vermelidir.

### 22.1 Data confidence score

Veri eksikliğine göre:

```text
100 = tüm teknik ve fiyat verileri kaynaklı
80 = fiyat ve lokasyon kaynaklı, teknik veri eksik
60 = fiyat aralıkları tahmini, teknik veri eksik
40 = çoğu varsayım
```

Örnek confidence etkileri:

```text
Nem ve saflık yoksa -10
Fiyat C kaynaktan geliyorsa -10
İşleme maliyeti varsayımsa -15
Mesafe canlı API’den geldiyse +10
Kur canlı TCMB’den geldiyse +10
```

### 22.2 Model confidence score

Modelin güveni:

```text
model_confidence_score =
prediction_probability veya ensemble_consistency
× data_confidence_adjustment
```

Demo mesajı:

```text
Model güveni: %72
Not: Teknik analiz bilgisi girilmediği için güven skoru orta seviyededir.
```

---

## 23. Ekip içi kalite kontrol

Veri toplayan arkadaşlar her veri için şu soruları cevaplamalıdır:

1. Bu veri hangi hammaddeyle ilgili?
2. Hangi modele girecek?
3. Feature adı ne?
4. Birimi ne?
5. Kaynak güven seviyesi ne?
6. Bu değer gerçek mi, tahmin mi, aralık mı?
7. Augmentation için kullanılabilir mi?
8. Target leakage yaratır mı?
9. Demo’da gösterilecek mi?
10. Jüri sorarsa kaynağı savunabilir miyiz?

---

## 24. Veri araştırmacılarına verilecek kısa görev mesajı

Aşağıdaki metin ekip arkadaşlarına doğrudan gönderilebilir:

```text
Raw2Value AI için veri araştırması yapıyoruz. Lütfen rastgele kaynak toplamayın; her bulduğunuz verinin hangi model feature’ına dönüşeceğini düşünerek ilerleyin.

Ana kapsam:
- Pomza ana demo hammaddesi
- Perlit ve kabak çekirdeği destek hammaddeleri
- Hammadde kaynağı Nevşehir/TR71
- Alıcılar Türkiye geneli + Almanya/Hollanda gibi seçili pazarlar

Toplanacak veri türleri:
1. Hammadde üretim/rezerv/bölgesel önem verisi
2. Ham fiyat aralıkları
3. İşlenmiş ürün fiyat aralıkları
4. İşleme maliyet aralıkları
5. İşleme rotaları
6. İşleyici ve alıcı firma/şehir/sektör bilgileri
7. Hedef sektör ve talep sinyali
8. Kaynak koordinatları ve şehirler
9. Augmentation için mantıklı min-max aralıklar
10. Akademik referanslar: data augmentation, XGBoost/LightGBM/CatBoost, SHAP, benchmark, ablation

Her veri şu formatta teslim edilecek:
- veri noktası
- min/max/typical değer
- birim
- kaynak linki
- kaynak güven seviyesi: A/B/C/D
- hangi feature’a dönüşeceği
- notlar

Dikkat:
- Teknik hammadde değerleri opsiyonel. Üretici nem/saflık bilmiyorsa sistem default değer + düşük confidence ile çalışacak.
- CO2 değeri random üretilmeyecek; mesafe × tonaj × hackathon resmi emisyon faktörüyle hesaplanacak.
- Kur canlı TCMB EVDS’ten gelecek; araştırmada sadece hangi kur feature’larının kullanılacağını hazırlayın.
- Benchmark sayıları uydurulmayacak; eğitimden sonra gerçek değerlerle doldurulacak.
```

---

## 25. En kritik sonuç

Veri ekibi şu prensibi unutmamalıdır:

> Bizim veri setimiz “gerçekmiş gibi davranan sentetik veri” olmayacak.  
> Bizim veri setimiz, **gerçek kaynaklı referans noktalarıyla kalibre edilmiş, domain-informed senaryo veri seti** olacak.

Jüriye söylenecek savunma cümlesi:

```text
Hackathon MVP’sinde gerçek işlem geçmişi olmadığı için hibrit veri stratejisi kullandık. Bölgesel hammadde bilgisi, canlı kur, açık kaynak coğrafi mesafe ve kaynaklı fiyat aralıkları gerçek/referans verilerden geliyor. Eksik kombinasyonları ise domain-informed augmentation ile çoğalttık. Böylece model rastgele veriyle değil, gerçekçi iş senaryolarıyla eğitildi. Pilot aşamada gerçek teklif ve satış verisi geldikçe model yeniden eğitilecek.
```

Bu veri yaklaşımı hem teknik olarak savunulabilir hem de hackathon süresine gerçekçi şekilde uygundur.

---

## 26. Hızlı kontrol listesi

- [ ] Sadece pomza, perlit, kabak çekirdeği araştırılıyor.
- [ ] Pomza ana demo hammaddesi olarak korunuyor.
- [ ] Kaynak güven seviyesi A/B/C/D olarak işaretleniyor.
- [ ] Her veri bir feature’a bağlanıyor.
- [ ] Her fiyat aralık olarak tutuluyor.
- [ ] CO₂ random değil, formülle hesaplanıyor.
- [ ] Emisyon faktörleri hackathon resmi değerlerine göre kullanılıyor.
- [ ] Kur TCMB EVDS ile canlı alınacak şekilde planlanıyor.
- [ ] Basic Mode / Advanced Mode ayrımı korunuyor.
- [ ] Teknik bilgi eksikse confidence düşürme stratejisi uygulanıyor.
- [ ] Benchmark sayıları uydurulmuyor.
- [ ] Augmentation kuralları gerçek aralıklara dayanıyor.
- [ ] Target leakage kontrolü yapılıyor.
- [ ] B2B alıcı kapsamı Türkiye geneli + seçili ihracat pazarı olarak tutuluyor.
