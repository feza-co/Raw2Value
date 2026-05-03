<div align="center">
  <h1>🏔️ Raw2Value AI</h1>
  <p><b>Kapadokya'nın hammaddesini, küresel katma değere bağlayan zekâ katmanı.</b></p>
  
  [![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![XGBoost](https://img.shields.io/badge/XGBoost-Ready-orange.svg)](https://xgboost.readthedocs.io/)
  [![Tests](https://img.shields.io/badge/tests-80%2B%20passing-brightgreen.svg)]()
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

## 📖 Proje Nedir? (What)

**Raw2Value AI**, TR71 (Kapadokya) bölgesindeki yerel üreticilerin hammadde (Pomza, Perlit, Kabak Çekirdeği) satış ve işleme süreçlerini optimize eden, makine öğrenmesi tabanlı bir **Karar Destek Motorudur (Decision Support Engine)**. 

Geleneksel B2B pazar yerlerinden farklı olarak, alıcı ve satıcıyı rastgele listelemez. Sisteme girilen *hammadde, tonaj, kalite ve hedef pazar* verilerini işleyerek; en yüksek katma değeri yaratacak **işleme rotasını**, net **kâr tahminini (TRY)**, resmi **CO₂ ayak izini** hesaplar ve tedarik zincirindeki en uygun aktörleri (İşleyici/Alıcı) skorlayarak eşleştirir.

## 🎯 Neden Raw2Value? (Why)

### Devasa Potansiyel, Devasa Kayıp
Türkiye, dünya pomza üretiminin **%45,6'sına** sahip olarak açık ara dünya lideridir. Ancak bu devasa potansiyeli, tonunu ortalama **91,7 Dolara** "ham kaya" olarak ihraç ederek israf etmektedir. Oysa aynı hammadde mikronize edilerek işlendiğinde ton başına değeri **200-300 Dolar** bandına çıkmaktadır.

### Bilgi Asimetrisini Kırmak
Yerel üreticiler ve madenciler, ürünlerini işleyerek satmanın daha kârlı olduğunu bilirler. Ancak:
- Döviz kurlarındaki (EUR/USD) anlık dalgalanmalar,
- Avrupa Birliği Sınırda Karbon Düzenleme Mekanizması (CBAM) kaynaklı karbon vergileri,
- Gerçek navlun (lojistik) maliyetleri,
- Ve kendilerine en uygun yerel işleme tesisini (Processor) bulma zorluğu...

gibi riskleri hesaplayamadıkları için kararlarını **veriyle değil, sezgiyle** verirler. Raw2Value AI, bu "Bilgi Asimetrisini" ortadan kaldırarak; üreticiye şeffaflık, işleyici fabrikalara tam kapasite çalışma fırsatı, Avrupalı alıcılara ise yeşil ve izlenebilir bir tedarik zinciri sunar.

## ⚙️ Nasıl Çalışır? (How)

Sistem **"Yetenek Bazlı" (Capability-Based)** bir aktör modeline dayanır. Hammadde üreticisi sisteme girdiği andan itibaren süreç şu şekilde işler:

1. **Veri Toplama:** Üretici arayüze (Basic/Advanced Mode) malın cinsini ve miktarını girer.
2. **Canlı Zenginleştirme:** Sistem arka planda TCMB'den anlık döviz kurlarını ve OpenRouteService'den gerçek karayolu mesafelerini çeker.
3. **ML Karar Motoru:** Eğitilmiş CatBoost/XGBoost modelleri (Classification & Regression) çalışır.
4. **Çıktı (Deliverables):**
   - Hangi formda satılmalı? *(Örn: Ham satma, Mikronize et)*
   - Ne kadar kâr edilecek? *(TL bazında net öngörü)*
   - Karbon maliyeti nedir? *(Ton-km bazlı tCO2 hesaplaması)*
   - Malı kim işleyecek ve kime satılacak? *(Weighted Match Scoring ile B2B eşleşme)*

---

## 🏗️ Sistem Mimarisi (Architecture)

Raw2Value, yüksek erişilebilirlik ve düşük gecikme süreleri (<500ms) hedefleyerek modern bir mikroservis yapısında kurgulanmıştır.
```mermaid
graph TD
    subgraph Frontend [UI Katmanı]
        UI[Next.js / React Web App]
    end

    subgraph Backend [FastAPI Backend]
        API[API Gateway / Endpoints]
        Router[Business Logic & Rota Yönetimi]
        Cache[(Redis - T-1 Fx Cache)]
        DB[(PostgreSQL - Users, Matches)]
    end

    subgraph MLEngine [AI / ML Engine]
        Infer[Inference API - raw2value_ml]
        ModelProf[Profit Regression Model.pkl]
        ModelRoute[Route Classifier Model.pkl]
        Match[B2B Match Scorer]
    end

    subgraph External [Dış Servisler]
        TCMB[TCMB EVDS - Canlı Kur]
        ORS[OpenRouteService - Mesafe]
        Nominatim[OSM - Geocoding]
    end

    %% Bağlantılar
    UI <-->|JSON/REST| API
    API <--> Router
    Router <--> Cache
    Router <--> DB
    Router <-->|AnalyzePayload| Infer
    Infer --> ModelProf
    Infer --> ModelRoute
    Infer --> Match
    Router <-->|API Calls| External
