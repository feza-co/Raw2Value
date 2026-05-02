# Raw2Value AI — Kapadokya Hackathon 2026 Teknik Araştırma Raporu (Revize)

> **Revizyon notu:** Bu sürüm, final ekip kararlarına göre **scope hizalaması** yapar. Mevcut raporun teknik derinliği, kaynaklı araştırmaları, market/muadil analizleri, hammadde analizleri ve AI/ML model mantığı korunmuştur. MVP zorunlu kapsamı **Varyant B-lite**'a daraltılmış; SHAP / LLM / LightGBM Ranker / Optuna gibi unsurlar **Advanced / Future Work** katmanına taşınmıştır. Hackathon resmi karbon emisyon faktörleri (kara 0,100 / deniz 0,015 / hava 0,500 / demiryolu 0,030 kg CO₂ / ton-km) bütün hesaplara, örneklere ve UI metriklerine yansıtılmıştır.

> **Ton ve hedef:** Bu rapor doğrudan hackathon ekibinin uygulayabileceği, mühendislik düzeyinde teknik derinlikte, kaynaklı bir referans dokümandır. Mentörlere ve jüriye karşı savunulabilir cümleler içerir; varsayım ile gerçek açıkça ayrıştırılmıştır.

## 1. Yönetici Özeti

Raw2Value AI, TR71 (Kapadokya) bölgesinde düşük katma değerle satılan üç hammadde — **pomza (ana demo, %70 ağırlık), perlit (%20) ve çerezlik kabak çekirdeği (%10)** — için en kârlı işleme rotasını öneren, **gradient-boosting modelleri (XGBoost / LightGBM / CatBoost)** üzerine kurulu **B2B akıllı tedarik zinciri karar motorudur**. Ürün bir marketplace **değildir**; bir LLM chatbot **değildir**. İş kararını eğitilmiş ML modeli verir; LLM yalnızca öneriyi Türkçe doğal dille açıklar, teklif/ürün metni üretir ve reason code'ları kullanıcı dostu özetler.

Sistem iki ana fonksiyon altında konumlanır:

- **A. Value Route Optimizer** — Hammadde için en iyi katma değerli işleme rotasını önerir; kâr / değer artışı / CO₂ / teslim süresi / canlı kur / risk / confidence dikkate alınır.
- **B. B2B Match Finder** — Üretici–işleyici–alıcı kombinasyonlarını skorlar ve sıralar; işleyici, alıcı ve pazar eşleşmesini verir.

Bu iki fonksiyonu beslemek üzere geri planda iki ML modeli + bir skorlayıcı çalışır: (i) kâr/değer artışı tahmini (regresyon), (ii) işleme rotası önerisi (multi-class), (iii) **MVP'de açıklanabilir weighted scoring + reason codes** ile B2B match scoring (advanced katmanda LightGBM Ranker). Sistem; hammadde tipi, tonaj, kalite, lokasyon, mesafe, taşıma modu, döviz kuru, hedef pazar ve karbon maliyetini girdi olarak alır. **Üç zorunlu hackathon kuralı** (canlı TCMB EVDS döviz kuru, OpenRouteService ile dinamik mesafe + resmi hackathon emisyon faktörleri üzerinden karbon ayak izi, bağımsız coğrafi işlem olarak nearby processor filtering) tek ekranlı **AI Decision Cockpit**'inde aktif olarak iş kararını etkileyecek biçimde entegre edilir; what-if simülatöründe kullanıcı kuru veya işleme maliyetini değiştirdiğinde model önerisi gözünün önünde değişir.

**Türkiye, USGS Mineral Commodity Summaries 2025 verisine göre dünyanın bir numaralı pomza üreticisidir; 2024 üretimi 8,2 milyon metrik ton, dünya toplamı 18 milyon ton (≈%45,6 pay)**; ihracatın büyük kısmı ise WITS HS 251311 verisiyle yaklaşık $91,7/ton FOB bandında ham olarak yapılır. Mikronize pomza, denim yıkama taşı ve filtrasyon medyası rotaları kat-kat değer artışı sunar. Proje bu açıklığı modelleyip ölçer.

**Ana kategori: Kategori 3 — Akıllı Tedarik Zinciri Sistemleri.** Kategori 1 (Dijital İhracat) ve Kategori 2 (AI E-Ticaret) yalnızca ikincil bağlantı olarak değerlendirilir.

**Final MVP: Varyant B-lite** — Value Route Optimizer + B2B Match Finder + AI Decision Cockpit + 2 ML modeli + weighted scoring B2B match + feature importance/reason codes + üç kural eksiksiz + what-if simulator + Model Evidence ekranı. SHAP / LLM açıklama / LightGBM Ranker / PDF Raw Material Passport / Optuna / PostGIS gibi unsurlar **advanced enhancement / future work** olarak konumlanır. 24 saatte 3-5 kişilik ekiple yapılabilir; risk profili kontrol altındadır.

## 2. En İyi Hammadde Kısa Listesi — Derin Analiz

> **Scope notu:** MVP hammaddeleri **pomza + perlit + kabak çekirdeği** ile sınırlıdır. Patates, üzüm, kalsit, kaolen, zeolit gibi ek hammaddeler yalnızca **future work / sektörel genişleme** olarak değerlendirilir; final MVP'ye girmez.

### 2.1 Pomza (Ana Demo, %70)

**Coğrafi gerçekler (kaynaklı, A — resmi/açık veri):**
- MTA Maden Serisi (mta.gov.tr): Türkiye'de pomza rezervi **2,2 milyar ton** (MAPEG, 2020), en büyük pay Nevşehir'de.
- Nevşehir Bilim ve Teknoloji Dergisi (Dergipark): "Türkiye dünya pomza rezervinin %15,8'ine sahipken Nevşehir ülke rezervinin %17'sine sahiptir; pomza işletme ruhsatlarının %20'si Nevşehir'dedir."
- USGS MCS 2025 (pubs.usgs.gov): "Turkey was the leading global producer of pumice and pumicite, followed by Greece." Türkiye 2024 üretimi **8.200 bin ton**, dünya toplamı **18.000 bin ton** → **≈%45,6 pay**. Türkiye'yi sırasıyla Yunanistan (1.000 kt), **Suudi Arabistan (980 kt)**, **Cezayir (900 kt)**, Uganda (830 kt) izliyor.
- WITS / UN Comtrade 2023 (HS 251311 — ham pomza): **Türkiye $30,89 M / 336.660 ton ihracatla dünya lideri**; **birim fiyat ≈ $91,7/ton FOB**.
- Anadolu Ajansı: "Üretilen pomzanın yüzde 90'a yakını inşaat sektöründe (bims blok) kullanılıyor; sektör Türkiye ekonomisine yılda yaklaşık 15 milyar lira katkı sunuyor."

**Düşük→yüksek katma değer farkı:**

| Form | Tipik fiyat bandı | Birim | Kaynak / Not | Güven seviyesi |
|---|---|---|---|---|
| Ham/dökme bims taşı (yurtiçi toptan) | 450 TL/ton | TRY | aspayapi.com 2024–2025 listeleme | C |
| Ham pomza FOB (ihracat ortalama) | $75–105/ton | USD | TradeKey FOB listeleri + WITS 2023 ortalama $91,7/ton | A (WITS) / C (TradeKey) |
| Bims blok (yapı) | iç piyasa, m³ bazında | TRY/m³ | İhracat istatistiklerinde HS 6810 altında | A |
| Mikronize pomza tozu (kozmetik/kimya/seramik) | $200–300/ton (üst bant) | USD | TradeKey ürün karması; Miner Madencilik 200.000 ton/yıl kapasite | C/D |
| Denim yıkama taşı (3–5 cm beyaz Türk pomza) | $90–150/ton FOB | USD | tradedata.pro Türkiye→Bangladeş kayıtları (Agrosan, Intersac) | C |
| Filtrasyon medyası | premium spec, çok değişken | USD | Sektörel niş, az veri | D |

**Hedef ihracat pazarları (MVP odak: Almanya + Hollanda; Türkiye içi: İstanbul/Ankara/İzmir/Antalya/Kayseri/Mersin):** Volza shipment count + tradedata.pro verisinde Türkiye küresel pomza sevkiyatlarının %31–40'ını yapıyor. Bangladeş (denim merkezi — Volza: "Bangladesh imports most of its Pumice Stone from Turkey, Bangladesh, and China… Turkey was the largest exporter with 93%"), Pakistan, Vietnam, Çin, Hollanda, İtalya, Almanya, ABD önde gelen pazarlar arasında. **Bangladeş denim yıkama taşı ana demo karmaşıklaştırmamak için opsiyonel sektörel referans olarak tutulur**; ana demo Almanya/Hollanda + Türkiye içi alıcılarla kurgulanır.

**Sektör örnek şirketler:** Miner Madencilik (Avanos, mikronize pomza üretimi 200.000 ton/yıl kapasite), Agrosan Maden Çelik (Bangladeş denim taşı tedariki), Intersac Denim Kimyasalları, Pumice World, PonceBloc (Kayseri, Arkas Group — pomza saflaştırma + Fransız/Alman teknolojisi). Nevşehir Pomza Endüstrisi makalesi (Dergipark): "Üreticilerin %80'i Ar-Ge yapmıyor; ihracat azalan eğilimde, çünkü düşük standartlı ürün ve yapı dışı alternatif eksikliği var."

**24 saat demo uygunluğu:** **Yüksek**. Fiyat bandı, koordinat, ihracatçı şirket adları, hedef pazar verileri kamuya açık.

### 2.2 Perlit (Genellenebilirlik Göstergesi, %20)

- İMİB (imib.org.tr) ve insapedia.com: Türkiye perlit rezervi 2001 DPT raporunda 4 milyar ton, 2020 Kalkınma Bakanlığı raporunda 5,7 milyar ton; **görünür rezerv 57 Mt, dünya görünür rezervinin %8'i**. Bazı sektörel kaynaklar (Yeni Şafak, Genper) "dünya rezervinin %70–75'i Türkiye'de" diye yazar; bu görünür+muhtemel toplamı temsil eder. Net görünür rezerv payı %8'dir.
- Ana yataklar: Cumaovası, İzmir-Bergama-Dikili, Eskişehir-Üçsaray, Kütahya, Konya, Erzincan. Nevşehir/Acıgöl ikincil ama TR71 için kullanılabilir bir nokta.
- Ham perlit ($/ton) → genleştirilmiş perlit ($/ton): Genleştirme 750–1200°C'de hacim 20 kata çıkar; enerji-yoğun. Kullanım: tarım substratı, inşaat izolasyonu, filtrasyon (gıda, ilaç).
- Genper Kütahya tesisi: 300.000 ton/yıl ham perlit kırma-eleme + 20.000 ton/yıl genleştirilmiş perlit kapasitesi.
- Perlit denim yıkama (sektörel — Fibre2Fashion): "Perlite treatment reduces the rate of harm caused to large washing machines by pumice stones and gives the denim better supple and softer finish." Modelin "rota" outputunda perlit↔pomza ikamesi gösterilebilir; bu güzel bir ablation senaryosu yaratır.

**24 saat demo uygunluğu:** **Orta**. Veri var ama demo'da pomza kadar görsel değil.

### 2.3 Kabak Çekirdeği (Tarımsal Katma Değer, %10)

- TÜİK 2024 (kapadokyahaber.com.tr ile teyit): Nevşehir'de 221.350 dekar alanda **23.670 ton üretim**, ekonomik katkı **1.343.144.897 TL**.
- Nevşehir Ticaret Borsası: "Türkiye'de üretilen kabak çekirdeğinin yaklaşık yüzde 35'i Nevşehir'de yetiştiriliyor." 2019'da coğrafi işaret tescili: "Nevşehir'in sütle kavrulmuş meşhur çerezlik kabak çekirdeği".
- Yoğun yetiştirme: Acıgöl, Ürgüp, merkez köyleri.
- Dökme satış (üretici fiyatı, tarla kapısı) → paketli kavrulmuş premium → soğuk pres kabak çekirdeği yağı: **Grand View Research Horizon databook verbatim:** *"The global pumpkin seed oil market generated a revenue of USD 1,144.8 million in 2024 and is expected to reach USD 2,067.6 million by 2030."* CAGR **%10,5 (2025–2030)**. Avrupa pazarı **2023 yılı için %35,9 pay** ("The Europe pumpkin seed oil market accounted for a revenue share of 35.9% in 2023.") — Slovenya ve Avusturya öncü.
- AB için ihracat: Avrupa premium organik kabak çekirdeği yağına yüksek talep gösteriyor (Slovenya, Avusturya tradition).
- Kapadokya markası ile turistik hediyelik paket potansiyeli — Avanos, Göreme, Uçhisar turist akışı.
- Kalkınma Kütüphanesi (kalkinmakutuphanesi.gov.tr): "Nevşehir İli Kabak Çekirdeği Kavurma ve Paketleme Tesisi Ön Fizibilite Raporu" mevcut — proje doğrudan kullanır.

**24 saat demo uygunluğu:** **Yüksek**. Sayılar güçlü, hikâye iyi (geleneksel ürün → premium paket → AB yağ ihracatı).

## 3. Hammadde → İşlenmiş Ürün Dönüşüm Matrisi

| Hammadde | Yerel kaynak (koord) | Ham satış formu & fiyat | Olası işlenmiş ürünler & fiyat | İşleme adımları | Hedef sektör | Yurtiçi B2B (TR) | İhracat B2B (MVP) | Tahmini değer artışı | Demo uygunluk | Veri | ML uygunluğu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Pomza | Nevşehir merkez, Acıgöl, Ürgüp; ~38,62°N 34,71°E; 440 Mm³ ruhsatlı rezerv | Ham/dökme: 450 TL/ton iç + $91,7/ton FOB ortalama (WITS 2023) | (a) Bims blok yapı; (b) Mikronize pomza $200–300/ton; (c) Denim yıkama taşı $90–150/ton FOB; (d) Filtrasyon medyası premium niş; (e) Tarım pomzası | Kırma → eleme → boyut tasnifi → (mikronize için) bilyeli değirmen + air classifier → paketleme | İnşaat, tekstil/denim, kozmetik, su arıtma, tarım | İstanbul, Ankara, İzmir, Antalya, Kayseri, Mersin (inşaat + kozmetik) | Almanya, Hollanda (ana demo); Bangladeş opsiyonel sektör referansı | Mikronize 2–3×, denim taşı 1,5–2× | Yüksek | Yüksek (TÜİK, USGS, WITS, OEC, Volza, MTA) | Yüksek |
| Perlit | Acıgöl/Nevşehir ikincil; Cumaovası, Kütahya, Erzincan ana; TR71 için ~38,55°N 34,50°E | Ham: ~$50–70/ton (sektörel tahmin — D varsayım) | Genleştirilmiş perlit (tarım substratı, izolasyon, filtrasyon) ~3–5× | Kırma → eleme → 750–1200°C genleştirme fırını → boyutlandırma → paketleme | Tarım, inşaat izolasyonu, filtre | İstanbul, Ankara, Antalya seraları | Almanya, Hollanda (topraksız tarım, izolasyon) | 3–5× (enerji yoğun) | Orta | Orta (DPT, İMİB raporları + Genper kapasitesi) | Yüksek |
| Kabak çekirdeği | Nevşehir merkez köyleri, Acıgöl, Ürgüp; ~38,63°N 34,72°E; 221.350 dekar (TÜİK 2024) | Tarla kapısı dökme: ~57 TL/kg (TÜİK 2024 ekonomik katkı / rekolte oranı — D tahmin) | (a) Kavrulmuş paketli premium ~2–3×; (b) Kabak çekirdeği yağı (cold-pressed) ~5–10×; (c) Protein tozu/fonksiyonel gıda; (d) Turistik hediyelik Kapadokya markalı paket | Yıkama → kurutma → kavurma (taş fırın 45 dk) → boyut tasnifi → paketleme; yağ için soğuk pres | Çerez sanayi, gurme gıda, sağlıklı yağ pazarı | İstanbul, Ankara, İzmir (çerez + gurme); Antalya turistik | Almanya, Hollanda Türk diasporası + AB organik gıda | Paketli için 2–3×; yağ için 5–10× | Yüksek | Yüksek (TÜİK, NTB, Grand View Research) | Yüksek |

## 4. AI/ML Model Blueprint

### 4.1 Model 1 — Value Uplift / Profit Prediction (Regresyon)

**Hedef değişken:** `expected_profit_try` (TRY/ton, hammadde başına işlenmiş ürün net kârı). Türetilmiş hedef: `value_uplift_pct = (processed_price − raw_price − processing_cost − transport_cost) / raw_price`.

> **Target leakage uyarısı:** `expected_profit_try`, `value_uplift_pct` ve `match_score` türetilmiş hedef/çıktı değişkenleridir; **model input'una doğrudan sokulmamalıdır**. `processed_price` ve `processing_cost` senaryo/rota adayı feature'ı olabilir, ancak target ile aynı formülü tekrar ettirecek şekilde kullanılırsa leakage yaratır — bu nedenle bunlar input olarak verildiğinde regresyon hedefi `value_uplift_pct` yerine bağımsız bir kâr proxy'si üzerinden tasarlanır veya bu feature'lar drop edilir.

**Algoritma seçim gerekçesi:** Tabular, heterojen (numeric+kategorik), küçük-orta ölçek (1K–15K satır), missing değer toleransı yüksek olmalı → **CatBoost Regressor (default tercih)**, alternatif XGBoost ve LightGBM. CatBoost native categorical handling sağlar. LightGBM leaf-wise büyüme ile küçük dataset'te overfitting riski olduğundan early stopping + class weighting kritik. Literatür referansı: arxiv 2406.13166 — supply chain ML için gradient-boosted modeller logistic regression baseline'ından hem doğruluk hem stabilite anlamında belirgin avantajlı.

**Feature listesi:**

- **Numerik:** `tonnage` (1–1000), `quality_grade_numeric` (A=3,B=2,C=1), `distance_km` (ORS canlı), `processing_cost_try_per_ton`, `electricity_cost_kwh_try`, `usd_try` (TCMB), `eur_try`, `co2_kg_per_ton_km` (taşıma moduna göre), `target_market_demand_score` (0–1, manuel).
- **Kategorik:** `raw_material_type` (pomza/perlit/kabak), `quality_grade` (A/B/C), `origin_district` (Nevşehir/Acıgöl/Ürgüp/Avanos), `target_market_country`, `processing_route_candidate`, `transport_mode` (kara/deniz/hava/demiryolu).
- **Türetilmiş:** `transport_cost_total = distance_km × tonnage × freight_rate`, `co2_total_kg = distance_km × tonnage × emission_factor_kg_co2_per_ton_km` (hackathon resmi faktörler — bkz. §6), `fx_revenue_try = price_usd × tonnage × usd_try`, `margin_after_co2_tax`, `data_confidence_score`, `model_confidence_score`.

**Veri seti boyutu (MVP):** 1.000–3.000 augmented satır + 50–150 gerçek/referans/manuel kalibrasyon noktası. CPU üzerinde <30 saniye eğitim. GPU gerekmez. (Advanced hedef: 200–400 gerçek + 10K–15K augmented; MVP'nin üstünde, opsiyonel.)

**Metrikler:** RMSE, MAE, R², MAPE. 5-fold KFold cross-validation. Demo'da rule-based baseline ile karşılaştırma şarttır; gerçek metrikler eğitim sonunda doldurulur.

**Confidence:** `model_confidence_score`, CatBoost'un quantile regression modu + bagging variance üzerinden hesaplanır (advanced: `RMSEWithUncertainty` loss + ensemble variance, %90 prediction interval).

**Explainability (MVP):** **Feature importance + reason codes** — gradient boosting native importance + her tahmin için en etkili 3-5 feature'ın template-based Türkçe açıklaması.
**Explainability (Advanced):** SHAP TreeExplainer (Lundberg & Lee, NeurIPS 2017; arxiv 1802.03888 KDD 2018) — global summary plot + tek tahmin için force plot.

### 4.2 Model 2 — Processing Route Recommendation (Multi-class Sınıflandırma)

**Hedef değişken:** `recommended_processing_route ∈ {pomza:[ham, bims_blok, mikronize, filtrasyon, denim_yikama], perlit:[ham, genlestirilmis, tarim_substrati, izolasyon, filtrasyon], kabak:[dokme, paketli_kavrulmus, yag, protein_tozu, turistik_hediye]}`. Çok-sınıflı; her hammadde için kendi sınıf seti.

İmplementasyon iki seçenek:
- **(a)** Tek model, `raw_material_type` feature olarak; output 15 sınıf.
- **(b)** Üç ayrı model, hammadde başına 5 sınıf.

MVP için **(a) tercih edilir** — daha az model, ortak feature representation öğrenmesi. Demo'da hammadde değişince UI ilgili sınıfları maskeler.

**Algoritma:** XGBoost Classifier (`multi:softprob`), Random Forest baseline, CatBoost MultiClass. Model 1 ile aynı feature seti + `processing_capacity_available_in_region` (yakın işleyici sayısı), `seasonal_demand_index`.

**Metrikler:** Accuracy, macro-F1, top-3 accuracy, confusion matrix.

**Confidence:** `predict_proba` softmax skorları → top-1 olasılık `<` 0,5 ise model "düşük güven" işareti döner ve cockpit "model belirsiz, üst alternatifleri inceleyin" uyarısı verir.

### 4.3 B2B Match Finder — Skorlayıcı

**MVP yaklaşımı (zorunlu):** **Açıklanabilir weighted scoring + reason codes**. ML modellerinin çıktıları (M1 kâr tahmini, M2 rota önerisi) ile domain ağırlıkları birleşir:

```
match_score = w1·distance_inverse + w2·capacity_match + w3·price_offer
            + w4·payment_terms_score + w5·certification_match - w6·co2_cost
```

Ağırlıklar (`w1..w6`) konfigüre edilebilir; her aday için top katkı yapan 3 feature **reason code** olarak sıralanır ("Mesafe avantajı", "Kapasite tam uyumlu", "Düşük karbon" vb.).

**Advanced yaklaşımı (opsiyonel, zaman kalırsa):** **LightGBM `LGBMRanker` with `objective='lambdarank'`**, NDCG@5 metriği. Aynı veriden learning-to-rank modeli denenir. Microsoft LambdaRank dökümantasyonu ve Vespa.ai ranking docs takip edilir; öğrenme-sıralama literatürü (Burges et al.) referans.

**Feature seti (per query-document pair):** `producer_to_processor_distance`, `processor_to_buyer_distance`, `processor_capacity_ton_year`, `processor_certification_count`, `buyer_credit_score`, `historical_completion_rate`, `payment_term_days`, `target_market_match`, `fx_pair_compatibility`, `co2_cost_total`.

**B2B Match Finder kapsamı (üç senaryo):**

- **Üretici sorusu:** "Elimde bu hammadde var; hangi işleyici ve hangi alıcıyla daha iyi sonuç alırım?"
- **İşleyici sorusu:** "Ben bu hammaddeyi işleyebilirim veya kendi hammaddeme sahibim; hangi alıcı/pazar daha mantıklı?"
- **B2B alıcı sorusu:** "Ben şu kalitede/tonajda ürün arıyorum; Nevşehir/TR71 içindeki hangi hammadde + işleyici + rota benim için en uygun?"

**Metrikler (advanced için):** NDCG@5, MAP, MRR. Test split her sorgu (group) bazında olmalı; data leakage önlenir.

### 4.4 Benchmark Tablosu

> **Şeffaflık notu:** Aşağıdaki tablo **hedeflenen benchmark tasarımıdır**. Sayılar **örnek/placeholder** değerlerdir; gerçek eğitimden sonra güncellenecek ve Model Evidence ekranında gösterilecektir. Demo öncesi gerçek test sonuçlarıyla değiştirilir.

Eğitim plan: ~1.500 satır augmented data (MVP), 80/10/10 train/val/test, seed=42.

| Model | RMSE (kâr) | MAE | R² | Accuracy (rota) | Macro-F1 | Eğitim süresi | Durum |
|---|---|---|---|---|---|---|---|
| Rule-based baseline (heuristic if-else) | TBD | TBD | TBD | TBD | TBD | <1s | placeholder |
| Linear / Logistic Regression | TBD | TBD | TBD | TBD | TBD | ~2s | placeholder |
| Random Forest (n=200) | TBD | TBD | TBD | TBD | TBD | ~8s | placeholder |
| **XGBoost (depth=6, lr=0.1, n=500)** | TBD | TBD | TBD | TBD | TBD | ~12s | placeholder |
| LightGBM | TBD | TBD | TBD | TBD | TBD | ~6s | placeholder |
| CatBoost | TBD | TBD | TBD | TBD | TBD | ~18s | placeholder |

> Mentörlere sunum cümlesi: "Model Lab ekranında rule-based baseline ile gradient boosting modellerini karşılaştırıyoruz; gerçek eğitim sonrası test metrikleri burada gösterilecek. Bu sonuçlar hackathon sırasında üretilen augmented holdout set üzerinde ölçülecek; gerçek pilot verisiyle yeniden kalibre edilecektir."

### 4.5 Ablation Çalışması (Tasarım)

> **Şeffaflık notu:** Aşağıdaki ablation tablosu da tasarım iskeletidir; sayısal sütunlar gerçek eğitimden sonra doldurulacaktır.

| Konfigürasyon | RMSE artışı (beklenen yön) | Karar değişim oranı | Yorum |
|---|---|---|---|
| Tam model (baseline) | 0 | 0 | Referans |
| FX feature'ları çıkarıldı (-usd_try, -eur_try) | ↑ | yüksek | Kur kararı belirliyor → **Kural 2 doğrulanır** |
| Geo/mesafe çıkarıldı | ↑↑ | en yüksek | En kritik feature seti → **Kural 1 ve 3 doğrulanır** |
| CO₂ çıkarıldı | ↑ orta | orta | Karbon vergisi senaryosunda büyür |
| Demand score çıkarıldı | ↑ | orta | Pazar talebi feature'ı ROI'yi sertleştirir |
| Quality grade çıkarıldı | ↑ | orta-yüksek | A/B/C grade fiyat farkını yakalıyor |

Bu ablation jüriye **"sentetik veri değil, domain-informed; her feature bilinçli mühendislik"** mesajını netleştirir.

## 5. Veri Seti Şeması ve Örnek Satırlar

### 5.1 CSV Şeması (`raw2value_training.csv`)

```
record_id, raw_material, raw_subtype, origin_district, origin_lat, origin_lon,
tonnage, quality_grade,
input_mode, technical_data_available, lab_report_uploaded, default_values_used,
moisture_pct, purity_pct, particle_size_class,
raw_price_try_per_ton, raw_price_usd_per_ton,
processing_route, processed_price_usd_per_ton, processing_cost_try_per_ton,
processor_id, processor_lat, processor_lon, processor_capacity_ton_year,
buyer_id, buyer_country, buyer_lat, buyer_lon,
distance_origin_processor_km, distance_processor_buyer_km, total_distance_km,
transport_mode, freight_rate_try_per_ton_km,
emission_factor_kg_co2_per_ton_km, emission_factor_source, co2_total_kg,
usd_try, eur_try, target_market_demand_score,
expected_profit_try, value_uplift_pct, label_for_ranking,
data_confidence_score, model_confidence_score,
user_capabilities, organization_capability_flags,
timestamp
```

> **Not:** `expected_profit_try`, `value_uplift_pct`, `label_for_ranking` **hedef/çıktı sütunlarıdır**; model input'una sokulmaz (target leakage). `data_confidence_score` veri kalitesi (eksik teknik alan, default kullanım vb.) bazlı; `model_confidence_score` modelin tahmin belirsizliği bazlı türetilir.

### 5.2 Örnek Satırlar — Hackathon Resmi Emisyon Faktörleriyle Yeniden Hesaplanmış (5 kayıt)

**Formül:** `co2_total_kg = tonnage × total_distance_km × emission_factor_kg_co2_per_ton_km`
**Hackathon resmi faktörler:** Hava 0,500 · Deniz 0,015 · Kara/TIR 0,100 · Demiryolu 0,030 (kg CO₂ / ton-km)

```
1, pomza, beyaz_asidik, Acigol, 38.5491, 34.5152, 150, A,
   advanced, true, false, false,
   8.5, 92.0, fine,
   12500, 380, mikronize, 820, 180,
   miner_madencilik, 38.7196, 34.8460, 200000,
   kozmetik_germany, 52.5200, 13.4050,
   22.3, 2480.5, 2502.8,
   kara, 2.85,
   0.100, hackathon_official, 37542.0,
   33.45, 36.20, 0.78,
   142000, 1.84, 3,
   0.92, 0.87,
   "[canSupplyRawMaterial]", "[supplier]",
   2026-05-02
   # CO2: 150 × 2502.8 × 0.100 = 37,542 kg ≈ 37.54 tCO2

2, pomza, beyaz_asidik, Nevsehir, 38.6244, 34.7152, 300, B,
   basic, false, false, true,
   NULL, NULL, NULL,
   11200, 340, denim_yikama, 135, 75,
   agrosan, 38.7000, 34.8000, 150000,
   intersac_bangladesh, 23.8103, 90.4125,
   12.4, 5876.2, 5888.6,
   deniz, 2.85,
   0.015, hackathon_official, 26498.7,
   33.45, 36.20, 0.92,
   28500, 0.41, 2,
   0.65, 0.74,
   "[canSupplyRawMaterial]", "[supplier]",
   2026-05-02
   # CO2: 300 × 5888.6 × 0.015 = 26,498.7 kg ≈ 26.50 tCO2 (deniz hakim mod)

3, perlit, ham_genlestirilebilir, Acigol, 38.5500, 34.5100, 80, A,
   advanced, true, true, false,
   3.2, 75.5, medium,
   9500, 290, genlestirilmis, 1450, 520,
   genper_kutahya, 39.4167, 29.9833, 300000,
   tarim_holland, 52.1326, 5.2913,
   580.0, 3120.0, 3700.0,
   kara, 2.85,
   0.100, hackathon_official, 29600.0,
   33.45, 36.20, 0.71,
   98000, 2.53, 3,
   0.95, 0.83,
   "[canSupplyRawMaterial,canProcessMaterial]", "[supplier,processor]",
   2026-05-02
   # CO2: 80 × 3700 × 0.100 = 29,600 kg ≈ 29.60 tCO2

4, kabak_cekirdegi, cogr_isaret_cerezlik, Acigol, 38.5491, 34.5152, 5, A,
   basic, false, false, true,
   NULL, NULL, NULL,
   57000, 1700, kavrulmus_paketli, 4800, 1200,
   acigol_firin_1, 38.5500, 34.5160, 1000,
   peyman_ist, 41.0082, 28.9784,
   2.5, 720.0, 722.5,
   kara, 2.85,
   0.100, hackathon_official, 361.25,
   33.45, 36.20, 0.85,
   142000, 1.72, 3,
   0.70, 0.78,
   "[canSupplyRawMaterial]", "[supplier]",
   2026-05-02
   # CO2: 5 × 722.5 × 0.100 = 361.25 kg ≈ 0.36 tCO2

5, kabak_cekirdegi, cogr_isaret_cerezlik, Urgup, 38.6310, 34.9120, 2, A,
   advanced, true, true, false,
   5.0, 98.5, NULL,
   57000, 1700, yag_soguk_pres, 28500, 8500,
   urgup_yag_atolyesi, 38.6300, 34.9100, 500,
   bio_planete_de, 48.1351, 11.5820,
   1.0, 2120.0, 2121.0,
   kara, 2.85,
   0.100, hackathon_official, 424.2,
   33.45, 36.20, 0.92,
   38500, 11.18, 3,
   0.93, 0.85,
   "[canSupplyRawMaterial,canProcessMaterial,canExport]", "[supplier,processor,exporter]",
   2026-05-02
   # CO2: 2 × 2121 × 0.100 = 424.2 kg ≈ 0.42 tCO2
```

> **kg / ton dönüşümü:** Tüm `co2_total_kg` alanı kilogram bazındadır. UI'da hem **kg** (hassas) hem **tCO₂** (1.000 kg = 1 ton) gösterilir. Birim karışıklığı raporun her yerinde tutarlıdır.

### 5.3 Veri Hacmi ve Augmentation

**MVP hedefi:**
- **50–150 gerçek/referans/manuel kalibrasyon noktası.** Kaynaklar: Volza shipment kayıtları, MTA fiyat raporları, Nevşehir Ticaret Borsası tescil verileri, Genper/Akper kapasiteleri, USGS MCS 2025, WITS HS 251311, Grand View Research raporları.
- **1.000–3.000 domain-informed augmented satır.** Demo için ~1.500 satır yeterlidir.

**Advanced hedef (opsiyonel, zaman kalırsa):**
- 200–400 gerçek/referans satır
- 10K–15K augmented satır

**Augmentation yöntemi:**
- Tonaj: log-uniform [1, 1000]
- Kalite: kategorik {A:0.5, B:0.35, C:0.15}
- Kur: TCMB EVDS son 3 yıllık günlük serisi (`TP.DK.USD.A.YTL`, `TP.DK.EUR.A.YTL`) sample
- Mesafe: gerçek koordinatlar arası ORS Matrix API ile gerçek değer; pertürbasyon ±%5
- Fiyat: gerçek bant + Gauss noise (σ=%8)
- Karbon: hackathon resmi emisyon faktörleri (kara/deniz/hava/demiryolu) + ±%10
- Teknik alanlar (nem/saflık/parçacık): bölgesel default aralıklar; eksik olduğunda `default_values_used = true` + `data_confidence_score` düşürülür

**Tamamen sentetik DEĞİL:** Her feature bandı kaynaklı; modelin gördüğü dağılım gerçekle uyumlu. Mentörlere savunma cümlesi: "Tabular foundation models literatürü (arxiv 2602.19237) küçük örneklem sentetik augmentation'la hibrit yaklaşımı meşrulaştırır; gerçek sevkiyat verisi (Volza, tradedata.pro) noktalama olarak kullanıldı."

**Train/Val/Test split:** Stratified 80/10/10 (`raw_material` ve `processing_route` üzerinden), seed=42. Time-aware split ek varyant: 2024 verisi train, 2025 verisi test (concept drift gösterimi).

**Kalibrasyon kontrolü:** Beklenen kâr aralığı gerçek WITS birim fiyatları ($91/ton ham → $200–300/ton mikronize) ile tutarlı olmalı; aksi halde augmentation parametreleri yeniden ayarlanır.

### 5.4 Basic Mode / Advanced Mode (Üretici Girdileri)

Üretici, nem / saflık / parçacık boyutu / kimyasal analiz gibi teknik değerleri bilmek zorunda **değildir**.

**Basic Mode (zorunlu alanlar):**
- Hammadde türü
- Lokasyon
- Yaklaşık tonaj
- Gözle kalite: `bilmiyorum / düşük / orta / yüksek`
- Ürün formu: `ham kaya / kırılmış / elenmiş / toz / paketli`
- Hedef pazar
- Öncelik: `maksimum kâr / düşük karbon / hızlı teslim`

**Advanced Mode (opsiyonel alanlar):**
- Nem oranı (%)
- Saflık (%)
- Parçacık boyutu sınıfı
- Yoğunluk
- Teknik analiz / laboratuvar raporu
- Teknik föy (PDF upload)

**Eksik teknik bilgi mantığı:**
- Sistem, hammadde + lokasyon bazlı **bölgesel default aralıklar** kullanır.
- `default_values_used = true` ve `technical_data_available = false` flag'leri set edilir.
- `data_confidence_score` düşürülür (örn. 1.0'dan 0.65'e).
- `model_confidence_score` üzerinde **uyarı banner'ı** gösterilir:
  > *"Nem ve saflık bilgisi girilmedi. Sistem bölgesel varsayılan aralıklarla tahmin yaptı. Bu nedenle model güven skoru orta seviyededir. Daha hassas öneri için Advanced Mode'a geçebilirsiniz."*

## 6. Kural Uyum Matrisi (Hackathon Resmi Faktörler)

> **Önemli düzeltme:** Bu raporun önceki sürümünde bazı yerlerde GLEC framework 0,062 kg CO₂/ton-km road freight faktörü kullanılıyordu. Hackathon demo modunda **HACKATHON_KURALLARI.md içindeki resmi referans faktörler** kullanılır:
>
> - **Hava kargo:** 0,500 kg CO₂ / ton-km
> - **Deniz yolu:** 0,015 kg CO₂ / ton-km
> - **Kara / TIR:** 0,100 kg CO₂ / ton-km
> - **Demiryolu:** 0,030 kg CO₂ / ton-km
>
> GLEC sadece **akademik referans / future work / alternatif metodoloji** notu olarak kalır; Kural 1 uyumu, README, demo, örnek hesaplar ve UI metrikleri resmi hackathon faktörleriyle çalışır.

| Kural | Uygulama | Backend kanıtı | Frontend gösterim | Jüri açıklaması | Risk | Fallback |
|---|---|---|---|---|---|---|
| **K1: Coğrafi Karbon Ayak İzi** | OpenRouteService Matrix API ile origin→processor→buyer mesafesi (km); ton-km × hackathon resmi emisyon faktörü (`transport_mode` alanına göre kara 0,100 / deniz 0,015 / hava 0,500 / demiryolu 0,030 kg CO₂/ton-km) | `POST /api/analyze` içinde: ORS Matrix call → distance_km → tonaj × mesafe × faktör | Cockpit harita üzerinde rota çizimi + CO₂ pasta grafiği + total kg / tCO₂ | "Karbon ayak izini gerçek yol mesafesinden hesaplıyoruz, kuş uçuşu değil; faktör hackathon resmi referans değerlerinden. GLEC framework akademik referans olarak repoda not düşülmüştür." | ORS rate limit (free tier 40 req/min) | Haversine fallback formülü + son bilinen çağrı cache (Redis 1h TTL) |
| **K2: Canlı Döviz Kuru** | TCMB EVDS REST API: `https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.A.YTL,TP.DK.EUR.A.YTL&type=json&key={KEY}`; günlük güncellenen kur Model 1 feature'ı olarak girer | `GET /api/fx/current`: 30 dk TTL cache + scheduler | Cockpit "Canlı Kur" widget'ı + what-if slider (kur ±%20 → kâr tahmini anında değişir) | "Kur sadece ekranda yazmıyor; ML modelinin feature vector'unun bir parçası ve karara doğrudan etkisi var. What-if'te göstereceğiz." | TCMB API hafta sonu/tatilde aynı veri | Son bilinen değer + "T-1" rozet |
| **K3: Bağımsız Coğrafi İşlem** | Nominatim/Pelias geocoding + radius search (bir üretici noktasından 100 km içindeki tüm işleyiciler) — **karbon hesabından farklı, nearby processor filtering** işlevsel coğrafi sorgu | `GET /api/processors/nearby?lat=38.62&lon=34.71&radius_km=100`: PostgreSQL+PostGIS `ST_DWithin` query (advanced) veya basit Haversine bbox filter (MVP) | "En yakın işleyici bul" butonu + listeden seçim → B2B Match Finder'a besler | "Karbon hesabı ton-km içinken, bu işlem kapasite ve yakınlık taraması — iki farklı coğrafi kullanım." | Nominatim heavy-use policy (1 req/sec) | Self-hosted Nominatim + statik işleyici CSV (TR71 illeri için ~100 nokta) |

## 7. AI Decision Cockpit — Demo Akışı

### 7.1 Tek Ekran (1080p Single Page)

Layout (12-col grid, React + Tailwind + Recharts):

```
┌──────────────────────────────────────────────────────────────────────┐
│ [LOGO] Raw2Value AI — Kapadokya Hackathon 2026 [Live: USD 33.45 TL]  │
├──────────────┬───────────────────────────────────────┬───────────────┤
│ INPUT FORM   │ AI RECOMMENDATION (Top-1)             │ FX PANEL      │
│ Hammadde:▼   │ → Mikronize Pomza                     │ USD: 33.45 ↑  │
│ Tonaj:[150]  │ Güven: %87  Kâr: 142.000 TL          │ EUR: 36.20 ↑  │
│ Kalite:▼ A   │ CO₂: 37.542 kg (37,54 tCO₂) Kara     │ Kur etkisi:   │
│ Hedef:▼ DE   │ Reason: mesafe / kur / pazar         │ +%5 → kâr     │
│ Mode: Basic  │ [Detay aç]                           │ +%6.2         │
├──────────────┼───────────────────────────────────────┤───────────────┤
│ TOP-3 ROUTES │ MAP (Leaflet+OSM)                     │ FEATURE       │
│ ALTERNATIFLER│ ●Origin →●Processor →●Buyer           │ IMPORTANCE    │
│ 1. Mikronize │ Route: 2.502 km (kara/TIR)            │ (Native)      │
│    142K, %87 │                                       │ ▆ distance    │
│ 2. Denim     │                                       │ ▆ usd_try     │
│    28K, %72  │                                       │ ▆ tonnage     │
│ 3. Ham FOB   │                                       │ ▆ quality     │
│    18K, %65  │                                       │ ▆ co2         │
├──────────────┴───────────────────────────────────────┤───────────────┤
│ WHAT-IF SIMULATOR                                    │ TOP-3 BUYERS  │
│ [Kur ±%20] [İşleme maliyeti ±%30] [Karbon ağırlığı] │ (Match score) │
│ [Tonaj 1-1000] [Kalite A/B/C] [Transport mode]      │ 1. Cosmetic-DE│
│ → Model önerisi anında değişir                       │ 2. Bims-NL    │
│                                                      │ 3. Filtre-TR  │
└──────────────────────────────────────────────────────┴───────────────┘
```

### 7.2 3 Dakikalık Demo Akışı

| Süre | Sahne | Konuşan |
|---|---|---|
| 0:00–0:30 | Problem: "Türkiye %45,6 dünya pomza payı (USGS MCS 2025) ama $91,7/ton ham ihracat (WITS 2023) — 5–10 kat değer kaybı." | Lider |
| 0:30–1:30 | Default senaryo (Basic Mode): Acıgöl, 150 ton, A kalite, hedef Almanya kozmetik, transport=kara. Cockpit "Mikronize Pomza, %87 güven, 142K TL kâr, 37,54 tCO₂" döner. Reason codes: distance / usd_try / target market en kritik. | Demo sunucu |
| 1:30–2:30 | What-if: Slider'la kur USD 33→28'e iner; **model önerisi anında "Denim Yıkama → Hollanda" veya "Ham FOB"a döner** (FX feature aktif kanıtı). Sonra ORS rotası harita üzerinde açılır + CO₂ değişir (kara→deniz seçilirse 37,54 → ~26,5 tCO₂). | Demo sunucu + Backend |
| 2:30–3:00 | Model Evidence ekranı kısa gösterim (placeholder/gerçek ayrımıyla benchmark) + Kapanış: Kategori 3 + Kategori 2 ve 1 ikincil bağlantılar, üç kuralın aktif çalıştığı, ölçeklenebilir SaaS yolu. | Lider |

## 8. 3 Proje Varyantı Analizi

| Boyut | Varyant A (Güvenli MVP) | **Varyant B-lite (Final MVP) ★** | Varyant B (Advanced) | Varyant C (Ticari SaaS) |
|---|---|---|---|---|
| Pitch | "24h'te çalışan AI tedarik zinciri karar motoru" | **"ML-first Decision Cockpit + 2 fonksiyon + 3 kural"** | "+ SHAP + LLM + Ranker katmanı" | "B2B SaaS, abonelik" |
| AI katmanı | Sade weighted scoring | **Model 1 + Model 2 + weighted scoring B2B + reason codes** | + LightGBM Ranker + SHAP + LLM | + multi-tenant + role-based |
| Frontend | Sade React tablo + form | **Polished cockpit + harita + canlı widget'lar + what-if + Model Evidence** | + SHAP plotları + LLM paneli | + multi-tenant dashboard |
| API'ler | EVDS + ORS | **EVDS + ORS + Nominatim** | + LLM + SHAP servisi | + Stripe + auth + audit |
| Veri | <1K satır | **~1.500 satır augmented + 50–150 referans** | + 10K–15K satır | + canlı producer feed |
| Demo | Tek lineer flow | **Cockpit + what-if + reason codes + model evidence** | + SHAP force plot + LLM açıklama | Multi-user (zor) |
| Riskler | "Az iddialı" | **24h kısıt, model kalitesi placeholder** | LLM API down, SHAP perf | 24h'te yetişmez |
| Kazanma gerekçesi | Tüm kurallar geçti | **Çalışan demo + iki net fonksiyon + üç kural feature olarak** | "Vay be" anı + akademik | Ticari potansiyel |

**Karar:** **Varyant B-lite final MVP**. Saat 18'de Model 2 yetişmediyse Varyant A'ya bir adım (Model 2'yi kuralsallaştır). Saat 18+ sonrası zaman kalırsa SHAP / LLM açıklama / LightGBM Ranker advanced enhancement olarak eklenir.

## 9. Final Önerilen MVP

**İsim:** Raw2Value AI

**Kategori:** **3 (Akıllı Tedarik Zinciri Sistemleri) — birincil**. Kategori 2 (AI E-Ticaret) ve Kategori 1 (Dijital İhracat) yalnızca ikincil bağlantılardır.

**Platform tipi:** Marketplace **değildir**. LLM chatbot **değildir**. **ML tabanlı B2B akıllı tedarik zinciri karar motoru.** LLM yalnızca açıklama, teklif metni, ürün açıklaması ve reason code özetlemesi için kullanılır; iş kararını ML modeli verir.

**İki ana fonksiyon:**

- **A. Value Route Optimizer** — Hammadde için en iyi katma değerli işleme rotasını öneriyor; kâr / değer artışı / CO₂ / teslim süresi / canlı kur / risk / confidence dikkate alıyor.
- **B. B2B Match Finder** — Üretici–işleyici–alıcı kombinasyonlarını skorlayıp sıralıyor; işleyici, alıcı ve pazar eşleşmesi.

**Problem (1 paragraf):** TR71 (Kapadokya) bölgesi — Nevşehir, Aksaray, Kırşehir, Kırıkkale, Niğde — dünya pomza üretiminin **%45,6'sına** ev sahipliği yapan (USGS MCS 2025: 8,2 Mt/18 Mt), perlit ve çerezlik kabak çekirdeğinde Türkiye lideri olan bir hammadde havzasıdır (TÜİK 2024: Nevşehir 23.670 ton kabak çekirdeği, Türkiye üretiminin %35'i). Ne var ki üreticilerin %80'i Ar-Ge yapmıyor (Dergipark Nevşehir Pomza Endüstrisi araştırması), pomza ihracatının büyük bölümü ~$91,7/ton FOB ham olarak satılıyor (WITS HS 251311 2023), oysa mikronize pomza $200–300/ton, kabak çekirdeği yağı global pazarı 2024'te **$1.144,8 milyon** ve 2030'a kadar **$2.067,6 milyon** öngörülüyor (Grand View Research Horizon databook). Üretici, hangi rotanın hangi alıcı için en kârlı olduğunu, kur dalgalandığında nasıl değiştiğini, karbon maliyetinin etkisini ve en yakın işleyiciyi sezgi ile tahmin etmek zorunda kalıyor.

**Çözüm (1 paragraf):** Raw2Value AI, Value Route Optimizer ve B2B Match Finder fonksiyonları altında iki gradient-boosting modeli + açıklanabilir weighted scoring ile bu kararı 200 ms altında üretir. Üretici hammadde tipi, tonaj, kalite ve hedef pazarı (Basic Mode) girer; isteyen Advanced Mode'a geçip nem/saflık/parçacık ekler. Sistem TCMB EVDS'ten canlı kuru, OpenRouteService'ten gerçek yol mesafesini ve hackathon resmi emisyon faktörlerini, OpenStreetMap üzerinden yakın işleyici tesisleri alır; kâr/CO₂/teslim süresini hesaplar; top-3 alternatif rota ve top-N B2B alıcıyı sıralı verir. Reason codes ve feature importance ile her tahminin "neden böyle" açıklaması cockpit'te. (Advanced katman: SHAP + LLM Türkçe doğal dil — opsiyonel.)

### 9.1 Kapsam ve Lokasyon

- **Hammadde kaynağı (MVP):** Nevşehir / TR71.
- **İşleyici lokasyonu (MVP):** TR71 + yakın sanayi merkezleri.
- **B2B alıcı lokasyonu (MVP):**
  - **Türkiye geneli:** İstanbul, Ankara, Antalya, İzmir, Kayseri, Mersin
  - **Seçili ihracat pazarları:** Almanya, Hollanda
  - **Opsiyonel sektör referansı:** Bangladeş (denim taşı tarihsel pazar referansı; ana demo dallanmasın)

### 9.2 Capability-Based Kullanıcı Modeli

Kullanıcılar katı rollere hapsedilmez. Bölgedeki bir KOBİ aynı anda hammadde sahibi, işleyici ve ihracatçı olabilir. **İşleyici rolü, sadece dışarıdan hammadde alıp işleyen tesis değildir; bir işleyici kendi hammaddesine de sahip olabilir ve sistemde aynı zamanda tedarikçi gibi davranabilir.**

**Capability flag'leri:**

- `canSupplyRawMaterial`
- `canProcessMaterial`
- `canBuyMaterial`
- `canExport`
- `hasStorage`
- `hasTransportCapacity`

**Örnek:** Avanos'ta bir mikronizasyon tesisi hem dışarıdan pomza kabul edebilir hem kendi pomza sahasına sahip olabilir. Sistem onu hem **supplier** hem **processor** olarak kullanabilir. B2B Match Finder bu durumda hem tedarik tarafında hem işleme tarafında aday gösterir.

### 9.3 Personalar (Capability Model İçinde)

- **Üretici (Mehmet Bey):** Acıgöl pomza ocağı sahibi, 200–500 ton/ay. `canSupplyRawMaterial = true`. Kuru takip edemez, hangi alıcıya satacağını bilmez. Soru: *"Elimde bu hammadde var; hangi işleyici ve hangi alıcıyla daha iyi sonuç alırım?"*
- **İşleyici (Miner Madencilik):** Avanos mikronize tesisi, kapasite optimum çalışmıyor. `canProcessMaterial = true` + opsiyonel `canSupplyRawMaterial = true`. Soru: *"Ben bu hammaddeyi işleyebilirim veya kendi hammaddeme sahibim; hangi alıcı/pazar daha mantıklı?"*
- **B2B Alıcı (Almanya kozmetik / Hollanda tarım / İstanbul inşaat):** `canBuyMaterial = true`. Soru: *"Ben şu kalitede/tonajda ürün arıyorum; Nevşehir/TR71 içindeki hangi hammadde + işleyici + rota benim için en uygun?"*
- **Admin:** Sistem yönetimi + aggregate dashboard.

> **OSB / kalkınma ajansı / teknopark yöneticisi**, MVP'nin ana rolü değildir; admin aggregate dashboard kullanıcısı veya **future stakeholder** olarak konumlanır.

### 9.4 Ana ekranlar (MVP)

(1) Onboarding + capability seçimi, (2) **AI Decision Cockpit** (ana ekran), (3) Organization profile, (4) Processor / buyer catalog, (5) **Model Evidence** ekranı, (6) Reports & history.

### 9.5 Mimari (ASCII)

```
                        ┌─────────────────┐
                        │   FRONTEND      │
                        │  React/Next.js  │
                        │  + Tailwind     │
                        │  + Leaflet      │
                        │  + Recharts     │
                        └────────┬────────┘
                                 │ REST/JSON
                        ┌────────▼────────┐
                        │   FASTAPI       │
                        │   Backend       │
                        │  (Python 3.11)  │
                        └────────┬────────┘
                ┌────────────────┼────────────────────┐
        ┌───────▼───────┐ ┌──────▼──────┐ ┌──────────▼──────────┐
        │ Model Service │ │ Geo Service │ │ Integration Service │
        │ - Profit M1   │ │ - ORS Matrix│ │ - TCMB EVDS         │
        │ - Route M2    │ │ - Nominatim │ │ - LLM (advanced)    │
        │ - Match WS    │ │ - Haversine │ │ - SHAP (advanced)   │
        └───────┬───────┘ └──────┬──────┘ └──────────┬──────────┘
                │                │                    │
                └────────────────┼────────────────────┘
                        ┌────────▼────────┐
                        │  PostgreSQL     │
                        │  (PostGIS adv.) │
                        │  + Redis cache  │
                        └─────────────────┘
```

### 9.6 PostgreSQL Şeması — Capability-Based

**Yeni: `organizations` tablosu** (capability flag'leriyle):

```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(200),
  organization_type VARCHAR(50),       -- 'producer' / 'processor' / 'buyer' / 'admin' (capability-driven, sertifika değil)
  district VARCHAR(100),
  city VARCHAR(100),
  country VARCHAR(100),
  geom GEOGRAPHY(POINT, 4326),

  can_supply_raw_material BOOLEAN DEFAULT FALSE,
  can_process_material   BOOLEAN DEFAULT FALSE,
  can_buy_material       BOOLEAN DEFAULT FALSE,
  can_export             BOOLEAN DEFAULT FALSE,
  has_storage            BOOLEAN DEFAULT FALSE,
  has_transport_capacity BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_organizations_geom ON organizations USING GIST(geom);
CREATE INDEX idx_org_supply ON organizations(can_supply_raw_material);
CREATE INDEX idx_org_process ON organizations(can_process_material);
CREATE INDEX idx_org_buy ON organizations(can_buy_material);
```

**Profile / detail tabloları** (organizations'a bağlı):

```sql
CREATE TABLE producer_profiles (
  organization_id UUID PRIMARY KEY REFERENCES organizations(id),
  raw_materials VARCHAR(50)[],
  capacity_ton_year INT,
  quality_grades VARCHAR(20)[]
);

CREATE TABLE processor_profiles (
  organization_id UUID PRIMARY KEY REFERENCES organizations(id),
  processing_routes VARCHAR(50)[],
  capacity_ton_year INT,
  certifications VARCHAR(50)[],
  unit_cost_try_per_ton DECIMAL(10,2)
);

CREATE TABLE buyer_profiles (
  organization_id UUID PRIMARY KEY REFERENCES organizations(id),
  product_interests VARCHAR(50)[],
  payment_terms_days INT,
  credit_score DECIMAL(3,2)
);

CREATE TABLE shipment_history (
  id BIGSERIAL PRIMARY KEY,
  producer_org_id UUID REFERENCES organizations(id),
  processor_org_id UUID REFERENCES organizations(id),
  buyer_org_id UUID REFERENCES organizations(id),
  raw_material VARCHAR(50), processing_route VARCHAR(50),
  tonnage DECIMAL(10,2), quality_grade VARCHAR(2),
  raw_price_try DECIMAL(12,2), processed_price_usd DECIMAL(12,2),
  distance_km DECIMAL(8,2), transport_mode VARCHAR(20),
  emission_factor_kg_co2_per_ton_km DECIMAL(6,4), co2_kg DECIMAL(10,2),
  fx_usd_try DECIMAL(8,4), profit_try DECIMAL(12,2),
  data_confidence_score DECIMAL(3,2), model_confidence_score DECIMAL(3,2),
  created_at TIMESTAMPTZ
);
```

> Bir organizasyon hem `can_supply_raw_material = true` hem `can_process_material = true` olduğunda hem `producer_profiles` hem `processor_profiles` tablolarında kaydı olabilir; B2B Match Finder her iki tarafta da aday olarak değerlendirir.

### 9.7 FastAPI Endpoint Listesi

**MVP endpointleri:**

```
GET    /health
GET    /api/fx/current             → TCMB EVDS canlı (cached 30dk)
POST   /api/analyze                → tek response: route + profit + CO2 + FX + match score + reason codes + confidence
POST   /api/what-if                → batch inference, multiple scenarios (kur / maliyet / mod / tonaj)
GET    /api/processors/nearby      → radius search (Kural 3, Haversine bbox MVP, PostGIS advanced)
GET    /api/model-evidence         → benchmark + ablation summary (placeholder/gerçek)
```

**Advanced endpointleri (opsiyonel, zaman kalırsa):**

```
POST   /api/v1/predict/profit
POST   /api/v1/predict/route
POST   /api/v1/match/buyers        → LightGBM Ranker
POST   /api/v1/explain/llm         → LLM Türkçe açıklama
GET    /api/v1/dashboard/aggregate
POST   /api/v1/explain/shap        → SHAP TreeExplainer
POST   /api/v1/footprint           → ORS Matrix detaylı CO2 breakdown
```

### 9.8 Eğitim Workflow (Jupyter/Colab)

1. `01_data_collection.ipynb` — TÜİK, USGS, WITS, Volza, NTB verilerinin manuel toplanması.
2. `02_data_augmentation.ipynb` — Domain-informed augmentation, ~1.500 satır üretim (advanced: 10K+).
3. `03_baseline_models.ipynb` — Rule-based, LinReg, RandomForest benchmark.
4. `04_xgboost_lgbm_catboost.ipynb` — Hyperparameter tuning (advanced: Optuna 50 trials).
5. `05_match_scoring.ipynb` — Weighted scoring + reason codes (MVP); advanced: LightGBM `LGBMRanker`, NDCG@5.
6. `06_explainability.ipynb` — Feature importance + reason code template'leri (MVP); advanced: SHAP TreeExplainer.
7. `07_export_models.ipynb` — `joblib.dump(model, "model.pkl")` + ONNX export opsiyonel.

**Deploy:** Docker Compose (frontend + backend + postgres + redis); Render veya Railway için backend, Vercel için frontend, Neon/Supabase Postgres. Demo gününde lokalden tunneling (ngrok/cloudflared) yedek.

## 10. 24 Saatlik Geliştirme Planı (3-5 Kişilik Ekip)

Roller: ML (M), Backend (B), Frontend (F), Tasarım (T), Lider/Domain (L).

**Öncelik sırası (final B-lite):**

1. Frontend Decision Cockpit skeleton
2. TCMB EVDS + geo/carbon servisleri (hackathon resmi emisyon faktörleri)
3. Model 1 ve Model 2 (veya model benzeri reproducible training pipeline)
4. Weighted B2B match scoring + reason codes
5. What-if simulator
6. Model Evidence ekranı
7. README + demo video + pitch

**Opsiyonel (zaman kalırsa):** SHAP, LLM, LightGBM Ranker, PDF / Raw Material Passport, PostGIS, Optuna.

| Saat | M (ML) | B (Backend) | F (Frontend) | T (Tasarım) | L (Lider) |
|---|---|---|---|---|---|
| 0–3 | Veri schema kesinleştir, gerçek referans noktaları topla | FastAPI scaffold + Postgres + Redis kur | Next.js + Tailwind iskelet, Cockpit skeleton | Wireframe + renk paleti | Sunum metni v0, repo + README |
| 3–6 | Augmentation ~1.500 satır, baseline rule-based hazır | EVDS + ORS endpoint çalıştır + hackathon emisyon faktörleri util | Cockpit grid layout + form | Logo + slayt taslak | Q&A taslağı |
| 6–9 | Model 1 + Model 2 final, joblib kayıt | `/api/analyze`, `/api/fx/current`, `/api/processors/nearby` + organizations seed | Form input + map (Leaflet) + recommendation paneli | Slayt 1–5 | Demo akışı yazım |
| 9–12 | Weighted B2B Match Scoring + reason codes + ablation tasarımı | `/api/what-if` + caching | Top-3 alternatif tablo + harita rotası + match results | Slayt 6–10 | Mentör check-in |
| 12–15 | Feature importance plot + Model Evidence verisi | `/api/model-evidence` + error handling + fallback | What-if sliders + canlı kur widget + Model Evidence ekranı | UI iyileştirme | Pratik demo run-through |
| 15–18 | (Advanced if time) SHAP integration / Optuna tune | Test endpointler + Docker compose final + .env | UI polish + animation + responsive | Kapanış slaytı + ekip kartı | Final pitch metin |
| 18–21 | (Advanced if time) LightGBM Ranker | Deploy hazırlık (Render+Vercel) + smoke test | (Advanced if time) SHAP plot embed / LLM açıklama paneli | Demo videosu kayıt | Q&A drill |
| 21–24 | Backup model dump | Deploy + smoke test | Final layout + dark mode | Slayt finalize | Genel rehearsal × 3 |

Saat 18 checkpoint'i kritik: O saatte advanced unsurlar yetişmediyse MVP scope'una sıkı sıkıya bağlı kal — weighted scoring + reason codes + 2 model + cockpit + 3 kural + what-if + Model Evidence yeterli.

## 11. Mentör / Jüri Q&A (16 sert soru)

| # | Soru | Cevap |
|---|---|---|
| 1 | Bu sistemin akıllı olan tarafı ne? | İki gradient-boosting modeli (kâr regresyonu + rota multi-class) ve açıklanabilir weighted scoring B2B match — Value Route Optimizer ve B2B Match Finder olarak iki fonksiyonda. Feature importance + reason codes ile her tahminin nedenini gösteriyoruz. LLM açıklamayı yapar; **kararı LLM vermez, ML modeli verir.** Advanced katmanda SHAP + LightGBM Ranker + LLM açıklama eklenir. |
| 2 | Bu sadece bir marketplace değil mi? | **Marketplace değil, decision engine.** Marketplace listeleme yapar; biz aday rotaları sıralıyor + kâr+CO₂+teslim süresi+karbon vergi senaryosunu birlikte optimize ediyoruz. Listing değil; ML çıktısı + domain ağırlıklı skorlama. |
| 3 | Gerçekten model eğittiniz mi? | Evet. Model Evidence ekranında rule-based baseline ile gradient boosting modelleri karşılaştırılıyor; gerçek eğitim sonrası test metrikleri orada gösterilecek. Ablation çalışmasının iskeleti hazır; sayılar gerçek eğitim sonunda doldurulacak. Model artifactları repoda. |
| 4 | Hangi veriyi kullandınız? | Hibrit: Gerçek referans 50–150 nokta (USGS MCS 2025, WITS HS 251311 2023 — Türkiye $30,89M / 336.660 ton, TÜİK Nevşehir 23.670 ton kabak çekirdeği, Volza shipment kayıtları, Genper/Akper kapasiteleri) + domain-informed augmentation ~1.500 satır. Tamamen sentetik değil. (Advanced hedef: 200–400 gerçek + 10K–15K augmented.) |
| 5 | Neden sadece LLM kullanmadınız? | LLM tabular karar problemlerinde tutarsız, kalibre değil, fiyat/CO₂ feature'ları üzerinde sayısal optimum bulamıyor. Tabular foundation models karşılaştırması (arxiv 2602.19237) hâlâ XGBoost/LGBM'in regresyonda öne geçtiğini söylüyor. LLM bizim için açıklama katmanı (advanced); MVP'de zaten reason codes ve template-based Türkçe özet kullanıyoruz. |
| 6 | Model nasıl karar veriyor? | XGBoost/CatBoost gradient-boosted tree ensemble — split-finding bilgi kazancı bazlı; her tahmin için top-N feature contribution reason code olarak gösteriliyor. Cockpit'te canlı görülebilir. (Advanced: SHAP TreeExplainer ile per-feature katkı.) |
| 7 | Canlı döviz kuru iş kararını nasıl etkiliyor? | TCMB EVDS'ten USD/TRY ve EUR/TRY günlük çekiliyor, Model 1'in feature vector'ünde. What-if slider'da kuru ±%20 değiştirince **modelin top-1 önerisinin kâr sıralaması ve hatta rota değişiyor**. Ablation tasarımında FX feature'ı çıkarınca RMSE artışı bekleniyor (gerçek değer eğitim sonunda). |
| 8 | Karbon ayak izi nasıl hesaplanıyor? | OpenRouteService Matrix API'sinden gerçek yol mesafesi (km) → tonaj × mesafe × **hackathon resmi emisyon faktörü** (`transport_mode` alanına göre kara 0,100 / deniz 0,015 / hava 0,500 / demiryolu 0,030 kg CO₂/ton-km). Kuş uçuşu değil, gerçek rota. GLEC framework akademik referans olarak repoda not düşülmüş. |
| 9 | Kural 3, Kural 1'den nasıl farklı? | Kural 1: rota üzerinden ton-km hesabı (taşıma karbonu). Kural 3: bir noktadan radius ile **nearby processor filtering** — kapasite eşleştirme (PostGIS `ST_DWithin` advanced; MVP'de Haversine bbox). İki ayrı işlevsel coğrafi kullanım. |
| 10 | API çağrıları başarısız olursa? | EVDS down → son cached değer + "T-1" rozet. ORS rate-limit → Haversine fallback + Redis cache. Nominatim → self-hosted + statik CSV. Hiçbir API hard dependency değil. |
| 11 | Bu nasıl gerçek bir işe dönüşür? | B2B SaaS, ayda 500–2000 TL/üretici abonelik, OSB toplu lisans, ihracatçı birliği partnership. AHİKA destek programları (Sektörel Rekabet Edebilirlik) + TÜBİTAK 1507 hibe yolu. |
| 12 | Kim para ödeyecek? | Birincil: pomza üreticileri ve OSB'ler — Nevşehir ilinde 2022 itibarıyla **toplam 8.353 işyeri ve 52.408 çalışan** mevcut (investinnevsehir.com — il toplamı). Nevşehir Merkez OSB özelinde 53 firma, 1.494 kişi istihdam (aynı kaynak — OSB özel ayrımı). Hedef pazarımız bu işyeri tabanı içinde madencilik, gıda işleme ve ihracatla ilgili olan dilim. İkincil: ihracatçılar (Agrosan, Intersac), kalkınma ajansları abonelik. Üçüncül: data API. |
| 13 | Neden Kapadokya/TR71? | Pomza dünya lideri (Türkiye %45,6 — USGS 2025), perlit önemli pay, kabak çekirdeği TR71 (Nevşehir Türkiye'nin %35'i), AHİKA aktif kalkınma desteği, Nevşehir OSB ve KSS altyapısı, üniversite-sanayi işbirliği boşluğu (Dergipark) → bizim doldurabileceğimiz alan. |
| 14 | Neden Kategori 3? | Çünkü ana iş kararını **akıllı tedarik zinciri** modeli veriyor: hammadde→işleyici→alıcı zinciri, en kârlı dönüşüm rotası, lojistik karbon optimizasyonu. **Kategori 2 (B2B e-ticaret) ve Kategori 1 (dijital ihracat) yalnızca ikincil bağlantılar.** |
| 15 | Rekabet avantajınız ne? | (a) Bölgeye özgü domain-informed dataset (kimsenin kabak çekirdeği + pomza + perlit kombinasyonu yok), (b) eğitilmiş ML + açıklanabilir reason codes, (c) capability-based kullanıcı modeli (bir KOBİ aynı anda supplier+processor olabilir), (d) üç zorunlu kuralı iş kararına bağlamak — sadece görsel değil. |
| 16 | Veriniz sentetikse model güvenilir mi? | Tamamen sentetik değil. Gerçek noktalar (WITS $91,7/ton FOB, TÜİK 23.670 ton, USGS 8,2 Mt) anchor olarak; augmentation onların etrafında controlled distribution. Ablation çalışmasının her feature için RMSE etkisi ölçülüyor. Eksik teknik bilgi durumunda `data_confidence_score` ve `model_confidence_score` düşürülüyor; UI'da uyarı banner'ı gösteriliyor. Production'da gerçek shipment feed entegrasyonu yol haritamızda. |

## 12. 1 Dakikalık Pitch (≈320 kelime)

> Türkiye dünya pomza üretiminin yüzde kırk beş virgül altısına sahip — USGS 2025 raporu sekiz nokta iki milyon ton üretim, dünya toplamı on sekiz milyon. Ama bu hammaddenin ihracat ortalama birim fiyatı, Dünya Bankası WITS verisine göre, sadece ton başına doksan iki dolar. Mikronize edip kozmetiğe sattığınızda iki yüz, denim yıkama taşı yapıp Bangladeş'e gönderdiğinizde yüz yirmi-yüz elli dolar. Aynı durum perlit ve kabak çekirdeğinde de var: Nevşehir Türkiye'nin çerezlik kabak çekirdeği üretiminin yüzde otuz beşini yapıyor, dökme satıyor; oysa Avrupa'da soğuk pres kabak çekirdeği yağı pazarı Grand View Research databook'una göre 2024'te bir milyar yüz kırk dört nokta sekiz milyon dolar, 2030'a kadar iki milyar altmış yedi nokta altı milyona çıkıyor.
>
> Üretici bu kararı sezgi ile veriyor. Hangi rota daha kârlı? Kur dalgalandığında ne değişir? Karbon vergisi gelirse? En yakın işleyici nerede? Bunlar tek bir basit web sayfası ile çözülmez.
>
> Raw2Value AI iki ana fonksiyon altında çalışıyor: Value Route Optimizer ve B2B Match Finder. Geri planda iki gradient-boosting modeli — kâr regresyonu ve rota multi-class — ve açıklanabilir weighted scoring B2B eşleştirme var. TCMB EVDS canlı kur, OpenRouteService gerçek mesafe ve hackathon resmi karbon faktörleri, OpenStreetMap üzerinden yakın işleyici taraması — üç hackathon zorunlu kuralı sadece ekranda değil, ML modelinin feature vector'ünde aktif. What-if slider'da kuru veya taşıma modunu değiştirince modelin top-1 önerisi gözünüzün önünde değişiyor; reason codes her tahminin nedenini söylüyor. Model Evidence ekranında rule-based baseline ile gradient boosting karşılaştırılıyor — gerçek metrikler eğitim sonunda doldurulacak.
>
> LLM açıklama yapabiliyor — ama kararı eğitilmiş ML modeli veriyor. Capability-based kullanıcı modeli sayesinde bir KOBİ aynı anda hem tedarikçi hem işleyici olabiliyor.
>
> Kategori 3 — Akıllı Tedarik Zinciri. Yirmi dört saatte 3-5 kişilik ekiple çalışıyor. Sonrası SaaS: pomza üreticisinin, perlit işleyicisinin, kabak çekirdeği ihracatçısının her gün açıp baktığı tek panel. Kapadokya'nın hammaddesini katma değere bağlayan zekâ katmanı. Raw2Value AI.

## 13. 3 Dakikalık Demo Metni (Sahne Sahne)

**[0:00–0:30] Lider — kamera 1, slayt 2 (Problem)**
> "Burada bir sayı: Türkiye dünya pomza üretiminin yüzde kırk beş virgül altısı, USGS 2025 verisi. Ve şu sayı: ihracat ortalama doksan iki dolar ton, ham, WITS 2023. Üreticinin elinde dünya lideri bir kaynak var, ama mikronize, denim, filtrasyon hangisinin daha kârlı olduğunu, kur değişince ne değişeceğini bilemediği için ham gönderiyor. Çözmemiz gereken sadece bir marketplace değil; bir karar motoru."

**[0:30–1:30] Demo sunucu — ekran cockpit**
> "Acıgöl, yüz elli ton, A kalite, hedef Almanya kozmetik, taşıma kara/TIR. Basic Mode'dayız — nem, saflık girilmedi, sistem bölgesel default'larla devam ediyor, model güven skoru orta. [Forma girer.] Analyze. Üç yüz milisaniye sonra: Mikronize Pomza, yüzde seksen yedi güven, yüz kırk iki bin TL kâr, otuz yedi virgül beş tCO₂. Reason codes — distance, usd_try, target market en kritik. Top-3 alternatif: denim yıkama Hollanda ve ham FOB. Sağda B2B match top-3 alıcı."

**[1:30–2:30] Demo sunucu — what-if slider**
> "Şimdi en kritik kısım. TCMB EVDS canlı kur otuz üç nokta kırk beş. What-if slider'la yirmi sekize çekiyorum. [Slider hareket.] Bakın — modelin top-1 önerisi anında değişti. Çünkü kur düşünce dolar bazlı kâr azalıyor, mesafe-bazlı taşıma TL maliyeti baskın geliyor. Şimdi taşıma modunu kara'dan deniz'e çeviriyorum — ORS rotası harita üzerinde değişiyor, CO₂ otuz yedi virgül beş tondan yaklaşık yirmi altı virgül beş tona iniyor — hackathon resmi emisyon faktörleri devrede. Bu sentetik bir gösterge değil — feature vector'ün gerçek bir bileşeni."

**[2:30–3:00] Lider — kamera 1, kapanış**
> "Üç zorunlu kural — kur, karbon, bağımsız geo işlem — sadece ekranda değil, kararın merkezinde. İki ML modeli, açıklanabilir weighted scoring B2B match, reason codes. Capability-based kullanıcı modeli sayesinde bir tesis hem supplier hem processor olabiliyor. Model Evidence ekranı benchmark planımızı gösteriyor. Kategori üç birincil, iki ve bir ikincil. Raw2Value AI: Kapadokya'nın hammaddesini değere bağlayan zekâ katmanı. Teşekkürler."

## 14. README Taslağı

````markdown
# Raw2Value AI 🪨🌱

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> TR71 Kapadokya bölgesindeki yerel hammaddeler (pomza, perlit, kabak çekirdeği) için en kârlı katma değerli dönüşüm rotasını öneren, eğitilmiş ML modelleriyle çalışan **B2B akıllı tedarik zinciri karar motoru**. Marketplace değil, LLM chatbot değil — decision engine.

![Demo](docs/demo.gif)

## ✨ Özellikler (MVP)

- 🤖 **2 ML modeli + skorlayıcı:** kâr/değer regresyonu, rota multi-class, weighted B2B match scoring
- 💱 **Canlı TCMB EVDS** USD/EUR/TRY kuru — modelin feature vector'ünde
- 🗺️ **OpenRouteService** ile gerçek yol mesafesi + **hackathon resmi emisyon faktörleri** (kara 0,100 / deniz 0,015 / hava 0,500 / demiryolu 0,030 kg CO₂/ton-km)
- 🧭 **Nominatim / Haversine** ile bağımsız nearby processor filtering (Kural 3)
- 🎯 **Feature importance + reason codes** ile her tahminin Türkçe gerekçesi
- 📊 **AI Decision Cockpit** — tek ekran karar arayüzü
- 🎚️ **What-if simülatörü** — kur, maliyet, tonaj, kalite, transport mode
- 🔎 **Model Evidence ekranı** — rule-based baseline vs. gradient boosting karşılaştırması
- 🧩 **Basic / Advanced Mode** — teknik alanlar opsiyonel; eksikse default + confidence düşür
- 🧱 **Capability-based organization model** — bir KOBİ aynı anda supplier + processor + exporter olabilir

## 🌟 Advanced (opsiyonel, future work)

- LightGBM `LGBMRanker` learning-to-rank
- SHAP TreeExplainer ile global + force plot
- LLM Türkçe doğal dil açıklama
- Raw Material Passport PDF
- PostGIS `ST_DWithin` + GIST index
- Optuna hyperparameter tuning

## 🏗️ Mimari

```
Frontend (Next.js + Leaflet) → FastAPI → [Model + Geo + Integration] → PostgreSQL / Redis
```

## 🚀 Kurulum

```bash
git clone https://github.com/<team>/raw2value-ai
cd raw2value-ai
cp .env.example .env  # EVDS_API_KEY, ORS_API_KEY ekle
docker-compose up --build
```

API: http://localhost:8000/docs · UI: http://localhost:3000

## 🧪 API Kullanımı (MVP)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
        "raw_material":"pomza",
        "tonnage":150,
        "quality":"A",
        "target_country":"DE",
        "transport_mode":"kara",
        "input_mode":"basic"
      }'
```

## 🧠 Model Eğitimi

```bash
cd ml
jupyter notebook 04_xgboost_lgbm_catboost.ipynb
python train.py --model catboost --output ../backend/models/
```

## ✅ Kural Uyumu

- **K1 (Karbon):** ORS Matrix → ton-km × hackathon resmi emisyon faktörü (`transport_mode` bazlı). GLEC framework `docs/methodology.md` içinde akademik alternatif olarak.
- **K2 (Kur):** TCMB EVDS → ML feature → what-if'te canlı etki
- **K3 (Bağımsız Geo):** Nominatim radius search → nearby processor filtering (Kural 1'den ayrı işlev). Advanced: PostGIS `ST_DWithin`.

## 👥 Ekip

[Team members]

## 📄 Lisans

MIT
````

## 15. 10 Slayt İskeleti

| # | Slayt | Anahtar mesaj |
|---|---|---|
| 1 | Kapak | Raw2Value AI — Logo, ekip, Kapadokya Hackathon 2026 |
| 2 | Problem | Türkiye %45,6 dünya pomza payı (USGS 2025) ama $91,7/ton ham ihracat (WITS 2023) — değer kaybı |
| 3 | Çözüm | İki fonksiyon (Value Route Optimizer + B2B Match Finder) + AI Decision Cockpit — kâr/rota/alıcı tek ekranda. **Marketplace değil, decision engine.** |
| 4 | Neden ML, Neden LLM Değil | Tabular karar problemi → XGBoost / CatBoost > LLM (arxiv 2602.19237 referans); LLM açıklama için (advanced) |
| 5 | Mimari | ASCII diyagram + tech stack + capability-based organization model |
| 6 | Demo Screenshot | Cockpit + harita + reason codes + what-if (kara→deniz mod değişimi → CO₂ değişiyor) |
| 7 | Kural Uyumu | K1/K2/K3 matrisi + canlı kanıt — **hackathon resmi emisyon faktörleri** |
| 8 | Benchmark + Ablation | Tasarım iskeleti + placeholder/gerçek ayrımı: "Model Evidence ekranında rule-based baseline ile gradient boosting karşılaştırılıyor; gerçek eğitim sonrası test metrikleri burada gösterilecek." Ablation'da FX/Geo/CO₂ feature'lar çıkarıldığında RMSE etkisi ölçülecek. |
| 9 | İş Modeli | SaaS: üretici/OSB/ihracatçı abonelik; AHİKA-TÜBİTAK destek yolu; capability-based KOBİ pazarı |
| 10 | Ekip + Kapanış | "Kapadokya'nın hammaddesini değere bağlayan zekâ katmanı" |

## 16. Rekabetçi & Akademik Konumlandırma

**Rekabet:**
- Generic marketplace'ler (sahibinden, alibaba sektörel): Sadece liste; karar veremiyor — muadil market analizi de bu boşluğu doğruluyor: **decision intelligence gerekir**.
- Sektörel ERP (SAP, IFS): Tedarik zinciri optimize ediyor ama lokal hammadde-rota uzayını eğitmiyor.
- Chatbot tarzı çözümler (LLM-only): Sayısal optimizasyon ve kalibre tahmin yetersiz.
- **Bizim farkımız:** Bölge-spesifik (TR71), eğitilmiş tabular ML, açıklanabilir weighted scoring, capability-based kullanıcı modeli, üç hackathon kuralı iş kararına bağlı.

**Akademik framing (mentör/jüri'ye):**
- **Tabular ML kârlılık tahmini:** "Inventory Demand Forecasting Using XGBoost and LightGBM" (Nguyen et al., IOS Press 2024). Bizim setup tam çizgide.
- **Learning-to-Rank B2B matching (advanced):** LambdaRank (Burges et al.) + LightGBM `LGBMRanker` — Microsoft araştırması; Vespa.ai dökümantasyonu.
- **Explainable AI (advanced):** Lundberg & Lee (NeurIPS 2017) "A Unified Approach to Interpreting Model Predictions" + KDD 2018 "Consistent Individualized Feature Attribution for Tree Ensembles" (arxiv 1802.03888) — SHAP TreeExplainer kanonik.
- **Supply chain ML literatürü:** "Enhancing supply chain security with automated machine learning" (arxiv 2406.13166) — gradient-boosted modellerin baseline'a kıyasla yüksek precision sağladığı, sınıf dengesizliği için class weighting kritik bulgu.
- **Foundation models comparison:** "Evaluating SAP RPT-1 for Enterprise Business Process Prediction" (arxiv 2602.19237) — tabular foundation modeller hâlâ GBDT'nin gerisinde, özellikle regresyon ve büyük dataset.

**Geçmiş hackathon kazanma paterni (genel):** Çalışan demo, net teknik derinlik, vay-be anı, kural eksiksiz uyum, iş modeli netliği. Raw2Value AI bu beşini birden hedefliyor.

## 17. Kaynak Güven Seviyesi

Rapor çok kaynaklı olduğundan kaynaklar güven seviyesine göre ayrılmıştır. Bu ayrım özellikle **fiyat ve pazar büyüklüğü iddialarında** kullanılır.

| Seviye | Tip | Kaynaklar |
|---|---|---|
| **A** | Resmi / kamu / açık veri | TÜİK, TCMB EVDS, USGS Mineral Commodity Summaries, MTA Maden Serisi, AHİKA, Hackathon Kuralları (HACKATHON_KURALLARI.md), MAPEG, WITS / UN Comtrade |
| **B** | Akademik / sektörel | Dergipark makaleleri (Nevşehir Pomza Endüstrisi vb.), İMİB raporları, şirket kapasite sayfaları (Genper, Akper, Miner Madencilik), Anadolu Ajansı sektörel haberleri |
| **C** | Ticari veri / marketplace | TradeKey FOB listeleri, Volza shipment kayıtları, tradedata.pro, Grand View Research Horizon databook özetleri, Fibre2Fashion |
| **D** | Varsayım / tahmin | Mikronize pomza fiyat üst bandı, kabak çekirdeği tarla kapısı fiyatı (TÜİK ekonomik katkı / rekolte oranından türetilmiş), işleme maliyeti varsayımları, `target_market_demand_score`, `risk_score`, augmentation parametreleri |

Raporda fiyat/hacim iddialarında kullanılan kaynak seviyesi parantez içinde işaretlenmiştir (§2.1, §3 ve §5'te örneklenmiştir).

---

## 18. Revizyon Kontrol Listesi

- [x] Ana kategori Kategori 3 olarak korundu.
- [x] Hammadde scope'u pomza + perlit + kabak çekirdeği olarak korundu.
- [x] Pomza ana demo olarak korundu (%70 ağırlık).
- [x] Capability-based user model eklendi (`canSupplyRawMaterial`, `canProcessMaterial`, `canBuyMaterial`, `canExport`, `hasStorage`, `hasTransportCapacity`).
- [x] İşleyicinin kendi hammaddesine sahip olabileceği eklendi (§9.2 örnek + dataset capability flag'leri + organizations tablosu).
- [x] B2B alıcı kapsamı Türkiye geneli (İstanbul, Ankara, Antalya, İzmir, Kayseri, Mersin) + seçili ihracat pazarları (Almanya, Hollanda) olarak düzeltildi; Bangladeş opsiyonel sektör referansına indirildi.
- [x] Basic Mode / Advanced Mode eklendi (§5.4).
- [x] Teknik hammadde alanları (nem, saflık, parçacık) opsiyonel hale getirildi.
- [x] Eksik teknik bilgi için default değer + confidence düşürme mantığı eklendi (uyarı banner'ı dahil).
- [x] Karbon emisyon faktörleri hackathon resmi değerlerine göre düzeltildi: kara 0,100 / deniz 0,015 / hava 0,500 / demiryolu 0,030. GLEC akademik referans olarak konumlandırıldı.
- [x] CO₂ örnek hesapları yeniden hesaplandı (5 örnek satır + cockpit metrikleri + demo metni). Formül `co2_kg = tonnage × distance_km × emission_factor` tüm raporda tutarlı.
- [x] Dataset şemasına `transport_mode`, `emission_factor_source`, `input_mode`, `technical_data_available`, `moisture_pct`, `purity_pct`, `particle_size_class`, `lab_report_uploaded`, `default_values_used`, `data_confidence_score`, `model_confidence_score`, `user_capabilities`, `organization_capability_flags` alanları eklendi.
- [x] Target leakage uyarısı `expected_profit_try`, `value_uplift_pct`, `match_score` için eklendi.
- [x] Veri hacmi yumuşatıldı: MVP 50–150 gerçek + 1.000–3.000 augmented (~1.500); advanced 200–400 + 10K–15K.
- [x] Benchmark sayıları placeholder/gerçek ayrımıyla dürüstleştirildi (TBD + "gerçek eğitim sonunda doldurulacak").
- [x] Ablation tablosu yön (↑ / ↑↑) ile gösterildi, kesin sayı verilmedi.
- [x] Pitch ve Q&A'dan "XGBoost R²=0,89" gibi kesin ifadeler kaldırıldı; Model Evidence ekranı atfı eklendi.
- [x] Varyant B-lite final MVP yapıldı (§8 ve §9).
- [x] LightGBM Ranker advanced/opsiyonel yapıldı; MVP'de weighted scoring + reason codes.
- [x] SHAP ve LLM advanced/opsiyonel yapıldı; MVP explainability = feature importance + reason codes; MVP açıklama = template-based Türkçe.
- [x] Weighted B2B Match Scoring MVP olarak konumlandırıldı; B2B Match Finder kapsamı üç senaryoyla (üretici / işleyici / alıcı sorusu) netleştirildi.
- [x] Endpoint listesi MVP (`/api/analyze`, `/api/what-if`, `/api/fx/current`, `/api/processors/nearby`, `/api/model-evidence`, `/health`) ve Advanced olarak ikiye ayrıldı.
- [x] Veritabanı modeli capability-based hale getirildi: `organizations` ana tablo, `producer_profiles` / `processor_profiles` / `buyer_profiles` bağlı detay tabloları.
- [x] OSB yöneticisi MVP ana rolü olmaktan çıkarıldı; admin aggregate dashboard kullanıcısı veya future stakeholder olarak konumlandırıldı. Ana MVP rolleri: Üretici, İşleyici, B2B Alıcı, Admin.
- [x] B2B Match Finder kapsamı üç sorudan (üretici/işleyici/alıcı) netleşti (§4.3 + §9.3).
- [x] Demo akışı pomza + Nevşehir + Türkiye içi/Almanya-Hollanda + AI Decision Cockpit + what-if + Kural 1/2/3 + Model Evidence ekseninde hizalandı.
- [x] README ve slide iskeleti final B-lite scope'una göre düzeltildi (3 model + LightGBM Ranker + SHAP + LLM ifadeleri MVP'den çıkarılıp advanced'a alındı).
- [x] Kaynak güven seviyesi (A/B/C/D) eklendi (§17).
- [x] 24 saat planı B-lite öncelik sırasına (frontend skeleton → EVDS+geo → 2 model → weighted match → what-if → Model Evidence → README/demo) hizalandı.
- [x] Yeni scope creep eklenmedi; mevcut iyi teknik kararlar (XGBoost/LightGBM/CatBoost ailesi, AI Decision Cockpit, What-if simulator, ORS/Nominatim/EVDS, domain-informed augmentation, source confidence ayrımı, muadil market analizi argümanı) korundu.

---

**Notlar (epistemik şeffaflık):**
- Benchmark/ablation tablo sayıları **placeholder'dır**, gerçek değerler eğitim sonunda doldurulacak ve Model Evidence ekranında gösterilecek.
- Pomza ham fiyat $91,7/ton FOB ortalaması **WITS HS 251311 2023 verisidir (A)**; mikronize $200–300 bandı TradeKey ürün karması gözlemidir (C), kesin İMİB raporu erişilemedi.
- Perlit "dünya rezervinin %70–75'i Türkiye'de" iddiası bazı sektörel sitelerde geçer; İMİB ve insapedia.com daha tutucu rakam (%8 görünür rezerv, 57 Mt) verir; raporda her iki bilgi de açıkça verildi.
- USD/TRY kuru 33,45 ve EUR/TRY 36,20 demo örnek değerleridir; gerçek demo'da TCMB EVDS'ten canlı çekilecek.
- Kabak çekirdeği tarla kapısı fiyatı (~57 TL/kg) TÜİK 2024 ekonomik katkı / rekolte oranından **türetilmiş tahmindir (D)**, üretici fiyatı kayıt değildir.
- Nevşehir 8.353 işyeri rakamı **il toplamıdır**; Nevşehir Merkez OSB özelinde 53 firma + 1.494 kişi istihdam (Q&A #12'de açıkça ayrıştırıldı).
- Karbon hesabında demo modu hackathon resmi emisyon faktörlerini kullanır; GLEC framework değerleri repoda `docs/methodology.md` altında alternatif metodoloji notu olarak tutulur.