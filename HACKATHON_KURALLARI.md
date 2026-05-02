# Kapadokya Hackathon 2026 — Hackathon Kuralları
**Cave2Cloud — Kapadokya'dan Global Pazara**
**2–3 Mayıs 2026 | Nevşehir Hacı Bektaş Veli Üniversitesi, Vali Şinasi Kuş Kültür ve Kongre Merkezi**

---

## Giriş

Hackathonlar, yazılımcıların zamanla yarıştığı kod maratonlarıdır. Kapadokya Hackathon 2026'nın teması **Cave2Cloud — Kapadokya'dan Global Pazara**'dır. Bu tema ile bölgedeki üreticileri, zanaatkârları ve işletmeleri dijital dünya pazarlarına taşıyacak, doğal mağara ve yaşam alanları için vizyoner yaklaşımlar geliştirilmesi hedeflenmektedir.

---

## Tema Kategorileri

| # | Kategori |
|---|----------|
| 1 | Dijital İhracat Çözümleri |
| 2 | Yapay Zekâ Destekli E-Ticaret Uygulamaları |
| 3 | Akıllı Tedarik Zinciri Sistemleri |
| 4 | Doğal Depoların Gıda Harici Kullanımına Yönelik Projeler |
| 5 | Doğal Mağara Yaşam ve Depolama Alanları İçin Akıllı Çözümler |

---

## Genel Kurallar

1. Yarışmanın ana teması **Cave2Cloud — Kapadokya'dan Global Pazara** olarak belirlenmiştir. Tüm projelerin bu tema kapsamında geliştirilmesi gerekmektedir.
2. Tüm takım üyelerinin projeye aktif katkı sağlaması gerekmektedir. Mentorlar ve organizasyon ekibi bireysel katkıları takip edecektir.
3. Yarışmak için seçtiğiniz konuya dair tüm çalışmaların hackathon süresi içinde geliştirilmesi gerekmektedir. Daha önceden planlanmış fikirleri hackathon süresi içinde kodlamak kaydıyla hayata geçirebilirsiniz.
4. Hackathon süresince, daha önce yayınlanmış, ticarileşmiş veya başka bir etkinlikte ödül almış projeler kullanılamaz.
5. Takımlar kütüphaneleri, framework'leri ve açık kaynak kodları projelerinde kullanabilir. Kullanılan dış kaynaklar sunumda açıklanmalıdır.
6. Yarışma boyunca sanayici ve akademisyen mentorlar takımları ziyaret edecektir. Fikir danışabilir, teknik ve iş geliştirme desteği alabilirsiniz.
7. Hackathon **2 Mayıs 2026 Cumartesi saat 10:10**'da başlayacak ve 24 saat sonra **3 Mayıs 2026 Pazar saat 10:10**'da sona erecektir. Bu zaman zarfında takım üyelerinin etkinlik alanını terk etmemeleri gerekmektedir.
8. Süre sona erdikten sonra tüm takım üyeleri sunum salonuna geçecek ve sıra gelene kadar salonda bekleyecektir. Bu zaman diliminde kodlama yapmak kesinlikle yasaktır. Takımlar rastgele bir sıra ile sahneye davet edilecektir.
9. Sunumunuzu kendi bilgisayarınızla gerçekleştireceğiniz için projeksiyon çıkışınızın uyumlu olduğundan ve şarjınızın tam olduğundan emin olunuz.
10. Takımlar en az 3, en fazla 5 üyeden oluşur.

---

## Teknik Zorunlu Kurallar

> Aşağıdaki üç teknik kural, etkinlik sabahı tüm takımlara eş zamanlı olarak ilan edilmiştir. Kurallar proje türünden (yazılım, donanım veya animasyon) bağımsız olarak geçerlidir. **Bu 3 kural birbirini tamamlar ve tamamı zorunludur. Birini atlayan proje jüri önüne çıkamaz.**

---

### Kural 1 — Coğrafi Karbon İzi

Projenizde konu alınan ürün, hizmet veya sürecin tahmini karbon ayak izi, **coğrafi veri kullanılarak hesaplanmalı ve kullanıcıya görsel olarak sunulmalıdır.**

- Coğrafi mesafe ve konum verisi için açık kaynaklı bir API veya veri seti kullanılması zorunludur (OpenStreetMap, Nominatim, OpenRouteService vb.)
- Mesafe veya konum verisi **sabit kodlanmış (hardcoded) olamaz**; sunum anında **dinamik olarak hesaplanmalıdır**
- Karbon hesaplama yöntemi ve kullanılan emisyon katsayıları **sunumda açıklanmalıdır**

#### Referans Emisyon Faktörleri

| Taşıma Modu | Emisyon Faktörü (kg CO₂ / ton-km) |
|-------------|----------------------------------|
| ✈ Hava Kargo | 0.500 |
| 🚢 Deniz Yolu | 0.015 |
| 🚛 Kara (TIR) | 0.100 |
| 🚂 Demiryolu | 0.030 |

#### Proje Türüne Göre Uygulama Örneği

- **Yazılım:** Kullanıcı çıkış/hedef girer → Nominatim koordinat → OpenRouteService mesafe → CO₂ hesabı → ekranda gösterim
- **Donanım:** Sensörden ağırlık okunur → Konum manuel/GPS → Aynı formül uygulanır → Cihaz veya web arayüzünde gösterim
- **Animasyon:** Anlatılan ürünün çıkış ve varış noktası belirlenir → API'den mesafe çekilir → Karbon değeri animasyon içinde veya sunum slaytında görsel olarak yer alır

---

### Kural 2 — Canlı Döviz Kuru

Projenizde **TCMB EVDS**'ten çekilen döviz kuru verisi belirli aralıklarla otomatik yenilenmeli; projenizde yer alan tüm fiyat, maliyet veya bütçe değerleri, sunum anında T.C. Merkez Bankası'nın güncel döviz kuru verisiyle **dinamik olarak hesaplanmış** olmalıdır.

- Son güncelleme zamanı arayüzde görünmeli ve bağlantı kesilmesi durumunda kullanıcı bilgilendirilmelidir
- Kur verisi yalnızca gösterilmekle kalmamalı; uygulamada **en az bir iş kararını (fiyatlandırma, karlılık, maliyet hesabı vb.) doğrudan tetiklemelidir**
- **Hardcoded kur kesinlikle kabul edilmez**
- Kullanılan para birimi çifti arayüzde görünür olmalıdır

---

### Kural 3 — Coğrafi Veri

Projenizde **en az bir coğrafi işlem** yapılmalıdır: mesafe hesaplama, rota gösterimi veya konum bazlı filtreleme.

- Veri kaynağı açık kaynaklı olmalıdır (OpenStreetMap, Nominatim, OpenRouteService, Overpass API vb.)
- Ticari API'lerin (Google Maps vb.) kullanımı bu kural kapsamında **geçerli sayılmaz**
- Bu coğrafi işlem, Kural 1'deki karbon hesabından **bağımsız**, projenin **farklı bir işlevinde** uygulanmalıdır
- Kullanılan API ve veri kaynağı sunumda açıklanmalı, tercih gerekçesi jüri sorularında yanıtlanabilmelidir

> **Uyarı:** Kural 1 ve Kural 3 farklı amaçlara hizmet eder. Kural 1 karbon hesabını, Kural 3 genel coğrafi işlemi ölçer. Birini yapmak diğerini otomatik karşılamaz.

---

### Bonus — Kuralların Birleşimi

Kural 1, 2 ve 3'ü **tek bir hesap zincirinde birleştiren takımlar** ek puan alabilir. Kuralların uygulanma şekli jüri tarafından değerlendirilecektir.

> Coğrafi API ile mesafe → CO₂ hesabı → Karbon maliyeti TCMB kuruyla TL ve hedef dövizde gösterim

---

## Teslimat Zorunlulukları

Her takım, en geç **3 Mayıs Pazar 09:00**'a kadar aşağıdaki paketi eksiksiz teslim etmek zorundadır.

| Teslimat Öğesi | Açıklama | Zorunlu |
|----------------|----------|---------|
| GitHub / GitLab Repo (Public) | Tüm kaynak kodu erişilebilir ve çalıştırılabilir olmalıdır. **"Saatlik commit atılması zorunludur."** | ✅ Evet |
| README Dosyası | Min. 500 kelime: Proje ne, neden, nasıl + mimari diyagram | ✅ Evet |
| Demo Videosu | Max. 3 dakika — Loom veya YouTube (liste dışı erişim) | ✅ Evet |
| Canlı Demo Linki | Vercel, Render, Railway vb. üzerinde deploy edilmiş uygulama | Önerilir |

### Teslim Zamanı ve Ön Değerlendirme

- Pazar sabahı 09:00'a kadar teslim edilmeyen projeler değerlendirme dışı kalacaktır.
- Jüri, sunum başlamadan önce kodlarınızı, README dosyalarını ve demo videolarını inceleyerek ön değerlendirme yapacaktır.
- Bu sayede 7 dakikalık sunum süresi yalnızca demo ve soru-cevaplara ayrılacaktır.

---

## Sunum Kuralları

11. Hackathon sonunda her takım bir sözcü seçecek ve jüri karşısında projesini sunacaktır. Sunum açık katılımlıdır.
12. Sunum süresi kesinlikle **7 dakikadır**. Yedinci dakikada söz kesilir.

| Bölüm | Süre | İçerik |
|-------|------|--------|
| Demo | 3 dakika | Canlı demo veya kayıtlı demo videosu — canlı tercih edilir |
| İş Modeli & Kural Açıklaması | 2 dakika | İş modeli + 3 zorunlu teknik kuralın nasıl uygulandığı |
| Jüri Soruları | 2 dakika | Teknik ve iş odaklı sorular |

13. Sunum sırasında jüri kodu ekrana yansıtmanızı ve uygulamanın çalıştırılmasını talep edebilir. Ek bir hazır sunum (slayt) zorunlu değildir; ancak kullanılabilir.
14. Sunum Türkçe yapılmalıdır.
15. Sunumunuzu kendi bilgisayarınızla yapacağınız için projeksiyon çıkışınızın uyumlu olduğundan ve şarjının tam olduğundan emin olunuz.

---

## Değerlendirme Kriterleri

| Kriter | Ağırlık | Açıklama |
|--------|---------|----------|
| Teknik Uygulama | %25 | Kod kalitesi, mimari, stabilite |
| Çalışırlık & Tamamlanma | %15 | Proje gerçekten çalışıyor mu? Demo canlı mı? |
| Kullanıcı Deneyimi & Tasarım | %15 | Sezgisellik, görsel kalite |
| Yenilikçilik & Özgünlük | %20 | Özgün fikir, alışılmışın dışında yaklaşım |
| Etki & Pazar Potansiyeli | %25 | Cave2Cloud uyumu + iş modeli + gerçek dünya etkisi |
| Zorunlu Kural Uyumu | Zorunlu (kurallar kullanılmadıysa değerlendirmeye alınmaz) | 3 teknik kuralın uygulanma kalitesi ve entegrasyon derinliği |

---

## Etkinlik Takvimi

### 2 Mayıs 2026 — Cumartesi

| Saat | Etkinlik |
|------|----------|
| 09:30 – 10:00 | Katılımcı Kaydı |
| 10:00 – 10:10 | Hackathon Kurallarının ve Temanın Detaylı Açıklanması / Teknik Zorunlu Kurallar Bu Anda İlan Edilir |
| 10:10 | Hackathon Takım Çalışmaları Başlangıcı |
| 3 Mayıs Pazar 09:00'a kadar | Teslimat: GitHub + Demo Video + README |

### 3 Mayıs 2026 — Pazar

| Saat | Etkinlik |
|------|----------|
| 10:10 | Hackathon Takım Çalışmaları Sona Erer *(Takımlar 09:00'dan 10:10'a kadar çalışmaya devam edebilirler, ancak jüri bu kısımda geliştirilen dosyaları değerlendirmeye almaz)* |
| 10:10 – 10:30 | Takımlar Sunum Salonuna Geçer |
| 10:30 – 14:00 | Takım Sunumları — Her Takım 7 Dakika (Açık Katılımlı Jüri Değerlendirmesi) |
| 14:00 – 14:30 | Jüri Karar Değerlendirme Toplantısı |
| 14:30 | Sonuçların İlan Edilmesi ve Ödül Töreni |

---

## Önerilen Araçlar ve Altyapı

### Uygulama Deploy Platformları
| Canlı Demo Linki | Vercel, Render, Railway vb. üzerinde deploy edilmiş uygulama | Önerilir |

> **Önemli Not:** Projenizi canlıya almak (deploy etmek) kesinlikle zorunlu değildir, ancak jürinin ve mentorların projenizi daha hızlı ve sorunsuz inceleyebilmesi için şiddetle **önerilir**.

| Platform | İdeal Kullanım | Ücret |
|----------|---------------|-------|
| Vercel | Frontend / Next.js / React | Ücretsiz |
| Netlify | Statik site, serverless functions | Ücretsiz |
| Render | Full-stack, API, backend | Ücretsiz (750 saat/ay) |
| Railway | Backend + veritabanı dahil | Ücretsiz ($5 kredi) |
| Supabase | PostgreSQL + Auth + Storage | Ücretsiz (2 proje) |
| Hugging Face Spaces | AI/ML modeli içeren projeler | Ücretsiz (GPU dahil) |

### Zorunlu Kurallar İçin API Önerileri

| API | İlgili Kural | Adres |
|-----|-------------|-------|
| Nominatim (OpenStreetMap) | Kural 1 & 3 | nominatim.openstreetmap.org |
| OpenRouteService | Kural 1 & 3 | openrouteservice.org |
| TCMB EVDS | Kural 2 | evds3.tcmb.gov.tr |

### Sunum ve Doküman Araçları

| Araç | Amaç |
|------|------|
| Gamma.app | AI destekli hızlı sunum hazırlama |
| Excalidraw / draw.io | Mimari diyagram |
| Loom | Demo videosu kaydetme |
| Figma | Prototype ve UI mockup |
| GitHub Pages | Statik site ücretsiz yayınlama |

### Tavsiye Edilen Kombinasyon

**Vercel** (frontend deploy) + **Supabase** (veritabanı + auth) ikilisi 24 saatlik hackathon için en hızlı ve sorunsuz kombinasyondur.

Zorunlu kural API'leri için: **Nominatim + OpenRouteService** ücretsiz ve API anahtarı gerektirmez.

---

## Acil İletişim

| Kanal | Bilgi |
|-------|-------|
| Telefon | 0544 743 06 45 – 0533 142 43 99 |

---

## Belgeler

- Hackathon Şartnamesi — hackathon.kapadokyateknopark.com.tr
- EK1. Taahhütname Formu
- EK2. KVKK Aydınlatma/Bilgilendirme Formu
- EK3. Muvafakat Dilekçesi
