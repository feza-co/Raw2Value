# Pomzadoya — QA Kalite Raporu v1

> **Hazırlayan:** QA review (Claude Opus 4.7, read-only).
> **Tarih:** 2026-05-02
> **Branch:** `p3-tuna` @ `71e49ef` (Merge origin/main into p3-tuna)
> **Kapsam:** SADECE tamamlanmış bölümler — P1 (T1.2-T1.10) + P3 (T3.1-T3.4 SLACK + 9 slack işi).
> **Yöntem:** Sadece statik kod analizi, manifest doğrulama, sözleşme uyumu. Hiçbir kod değiştirilmedi, hiç çalıştırılmadı.

---

## 0. TL;DR — Genel Skor

| Kategori | Ağırlık | Skor (100) | Yorum |
|---|---:|---:|---|
| 1. Kontrat netliği (P1↔P3) | 15 | 72 | Bant sırası tutuyor, **scale meta-veri çelişkili**, manifest path Windows-native. |
| 2. Veri sözleşmesi doğruluğu | 10 | 78 | Mean/std/bounds/shape/tile-count tutarlı. **Bant başına NoData yüzdesi yok**, files-map eksik. |
| 3. Hata / edge-case dayanıklılığı | 15 | 62 | NoData/NaN guard'lar var; **predict_raw() input-validation yok**, edge tile blend bölme tehlikesi. |
| 4. Bilimsel doğruluk | 10 | 88 | Liang 2001, Roberts 2017, Ninomiya QI, Lee filter, Roy 2016 — formüller doğru, dokümante. |
| 5. Reprodüksibilite | 10 | 65 | Seed=42 ✓, `set -euo pipefail` ✓, **P3 deps `>=` loose pin**, hardcoded Colab path. |
| 6. Pipeline orkestrasyonu | 10 | 55 | **GEE async polling/state yok**, "ATLANDI" sessiz akış, idempotency belirsiz. |
| 7. Cross-platform & path hijyeni | 10 | 60 | Manifest backslash, Bash-only run_pipeline, PowerShell eşleniği yok. |
| 8. Güvenlik / secret hijyeni | 5 | 75 | `.gitignore` kapsamlı; commit history'de cred sızıntısı görünmüyor; risk ipynb cell output. |
| 9. Test / sanity coverage | 5 | 55 | `synthetic_sanity` real distribution değil; gerçek tile testi/fixture yok. |
| 10. Dokümantasyon (docstring + briefing) | 10 | 82 | Briefing'ler net, docstring'ler I/O kontratlı; **SSL4EO bant mapping belirsiz**. |
| **GENEL AĞIRLIKLI** | **100** | **69** | **C+** — Hackathon kapsamına uygun, production reuse için 4 Critical fix gerek. |

**Bulgu sayısı:** 31 (4 Critical, 9 High, 12 Medium, 4 Low, 2 Info).
**Hackathon kararı:** Mevcut çıktılar dry-run #1 için yeterli — Critical #1 (manifest scale belirsizliği) ve Critical #3 (SSL4EO bant mapping) **T3.5 fine-tune başlamadan** netleşmeli, aksi halde fine-tune sonuçları yanıltıcı olur.

---

## 1. Kapsam ve Verilerin Yerel Durumu

### 1.1 Tamamlanmış görevler (commit'lere göre)

| Görev | Durum | Commit | Çıktı (manifest claim) |
|---|---|---|---|
| T1.2 AOI üretimi | ✅ Local | `dc9d08a` | `data/aoi/avanos_aoi*.geojson/.gpkg` (4 dosya disk'te ✓) |
| T1.3 S2 L2A çekim (GEE) | ✅ Async | — | Drive: `s2_l2a_avanos_median_2024_20m.tif` |
| T1.4 S2 ARD co-reg | ✅ | `14bd2a8` | `data/ard/s2_ard_20m.tif` (10 bant, 20m) |
| T1.5–T1.6 S1 + DEM | ✅ | `8304246`, `3232d22` | `data/s1_stack/`, `data/dem/` |
| T1.7 17-kanal Full ARD | ✅ | `ccfe04d` | `data/ard/full_ard_20m.tif` (17 bant) |
| T1.8 tile splitting | ✅ | `615bc7f` | `data/tiles/000_000.tif`…`004_005.tif` (30 tile) |
| T1.9 manifest + stats | ✅ | `4689669` | `data/manifest.json` (yerel diskte ✓) |
| T1.10 Landsat snapshot | ✅ Async | `8adab2b` | Drive: 5 yıl × Landsat |
| T3.1–T3.4 SSL4EO + slack | ✅ | `968c9ac` | `code/p3/02-12_*.py` |

### 1.2 ⚠ Yerel disk vs Drive ayrılığı — bilinçli ama doğrulamayı kısıtlıyor

Bu makinede (`c:\Users\tuna9\OneDrive\Masaüstü\Pomzadoya\data\`) yalnızca:

```
data/manifest.json          ✓ 5.7 KB
data/aoi/ (4 dosya)          ✓ 120 KB
data/ard/                    ✗ boş
data/tiles/                  ✗ boş
data/s1_stack/, dem/, landsat/, layers/, change/, temporal/, labels/  ✗ hepsi boş
```

Tüm raster çıktılar Drive'da (master coordination § 4 "Veri politikası"). Bu **bilinçli tasarım** — repo şişmesin diye. Ama QA açısından:

- **Manifest claim'leri (4.077% NoData, 30 tile, mean[0]=1254.3, vs.) bu makinede _tekrar üretilemez/doğrulanamaz_.** Manifest'in kendisi, üreten scriptin (T1.9) çıktısı olarak doğrulanabilir tek kaynak.
- Bu rapor, kod ve manifest'i source-of-truth alıyor. Drive'daki gerçek raster içeriğine **erişim yok**, dolayısıyla "manifest yalan söylüyor mu?" sorusu yanıtsız.
- **Öneri (Info):** Drive'a `pomzadoya-data-checksums.json` (sha256 her tile + ARD) yükle; en azından bütünlük doğrulanabilir.

---

## 2. Boyut Bazlı Detaylı Bulgular

> Severity: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low | ℹ Info

---

### 2.1 Kontrat netliği (P1 ↔ P3 manifest)

#### 🔴 [C-1] `manifest.scale = 10000.0` çoklu-unit bantlar için yanıltıcı
**Dosya:** `data/manifest.json:5`, `code/p1/09_export_manifest.py:25,202`
**Bulgu:** `scale: 10000.0` yalnızca S2 reflectance (idx 0–9) için anlamlı. dB (10–11), metre (12), derece (13), index (14–16) için anlamsız. Manifest'te **scale anahtarının kapsamı belirtilmemiş**. Bant başına `unit` alanı doğru yazılmış (✓) ama tek-değer `scale` aleyhinde çelişiyor.
**Etki:** P3 datamodule scale uygulamadığı için (sadece mean/std normalizasyonu) güvende, **ama P4/P5 bir tüketici scale'ı tüm bantlara uygularsa** S1/DEM/slope verileri anlamsız hale gelir → fusion fail.
**Öneri:** Manifest'e `scale_applies_to: "bands_0_9_only"` veya `scales: {0..9: 10000, 10..16: null}` ekle. P4/P5 sözleşmesinde "scale yalnız S2" netliği açık yaz.

#### 🔴 [C-2] SSL4EO 13-kanal bant sırası ↔ P1 manifest mapping belirsiz
**Dosya:** `code/p3/02_ssl4eo_pretrained.py:14-15,80-141`, `code/p3/06_train.py`
**Bulgu:** P1 manifest 10 S2 bandı içeriyor (B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12 — **B1/B9/B10 yok**). SSL4EO-S12 pretrained 13 S2 bandı görmüş (resmi listede genelde B1,B2,B3,B4,B5,B6,B7,B8,B8A,B9,B10,B11,B12). Adapter (`expand_first_conv()`) S1/DEM/slope için "mean of pretrained kernels" replicate yapıyor (akademik olarak iyi), ama:
- Pretrained 13 → P1 10 indeksleri **hangi sıraya hizalanıyor?** Dokümante değil.
- Eksik 3 SSL4EO kanalı (B1, B9, B10) için ne yapılıyor (drop? skip slice?) belirgin değil.
- `model.encoder.load_state_dict(sd, strict=False)` → eksik/beklenmeyen anahtarlar **sessiz kabul ediliyor** (sadece ilk 5 print).
**Etki:** Yanlış mapping ile fine-tune _görünüşte_ çalışır (loss düşer), ama pretrained ağırlıklar yanlış kanalın üstüne biner → SSL4EO transfer öğrenmesi anlamsızlaşır → 5-fold IoU 0.52 hedefi düşer.
**Öneri:** `code/p3/02_ssl4eo_pretrained.py` üst kısmına bir tablo ekle: `SSL4EO_BAND_ORDER = [...]; P1_BAND_ORDER = [...]; CHANNEL_MAP = {p1_idx → ssl4eo_idx or "init_from_mean"}`. Load sonrası `len(missing) > 0` ise **uyarı + ağırlık başlatma stratejisi** logla.

#### 🟠 [H-1] `DEFAULT_MEAN/STD` placeholder runtime fallback warning'siz
**Dosya:** `code/p3/03_datamodule.py:50-69,262`
**Bulgu:** Manifest geçilmediğinde 0–1 ölçekli placeholder fallback. P1 ARD ham 0–10000 ölçekte. Path.exists() check var, **ama warning yok** — sessiz fallback. Eğer `--manifest-json` unutulursa `(x − 0.10)/0.05` ile (1254 − 0.10)/0.05 ≈ 25 080 z-score → loss patlar/NaN/divergent.
**Öneri:** Fallback path'inde `warnings.warn("MANIFEST EKSİK — DEFAULT placeholder kullanılıyor; T3.5 öncesi --manifest-json zorunlu", UserWarning)` ekle. T3.5 RUN-BLOCK'ta `--manifest-json` parametresini **required** yap.

#### 🟠 [H-2] `predict_raw()` input kanal sayısı validate edilmiyor
**Dosya:** `code/p3/07_inference.py:83-131`
**Bulgu:** Tile (C,H,W) input alıyor, model `in_channels` değerine eşit olmazsa torch forward'da içsel hata. Açık `assert tile.shape[0] == self.in_channels` yok.
**Etki:** P5'in `predict_raw()` çağrısı yanlış kanal sayılı array geçirirse, hata mesajı kriptik (`RuntimeError: Given groups=1, weight of size [...]`). Hata yerine erken validation tercih edilmeli.
**Öneri:** Function başına `if tile.ndim==3 and tile.shape[0] != self.in_channels: raise ValueError(...)` ekle.

#### 🟡 [M-1] Manifest path Windows backslash format
**Dosya:** `data/manifest.json:7,217-227,225-230`
**Bulgu:** `"path": "data\\ard\\full_ard_20m.tif"` ve diğer `files.*` alanları Windows backslash kullanıyor. `pathlib.Path("data\\ard\\...")` Linux/Mac'te tek-string olarak parse eder (split kullanan herhangi bir tüketici kırılır). `rasterio.open()` direkt yutar (forward-tolerant), **ama** path manipulation yapan tüketici (örn. P5'in dashboard.py veya log) kırılır.
**Öneri:** `09_export_manifest.py` içinde `Path.as_posix()` ile serialize et — manifest forward-slash olur, Windows da yutar.

#### ℹ [I-1] Bant sırası P1↔P3 tutuyor
**Dosya:** `code/p1/07_full_coregistration.py:31-35`, `code/p3/03_datamodule.py:108-124`
**Bulgu:** B11=idx 8, B12=idx 9, VV=10, VH=11, DEM=12, slope=13, NDVI=14, BSI=15, Albedo=16. P3 datamodule manifest'ten okuyor — sıra tutarlı. ✓

---

### 2.2 Veri sözleşmesi doğruluğu (manifest + tile_index)

#### 🟡 [M-2] Bant başına NoData yüzdesi yok
**Dosya:** `code/p1/09_export_manifest.py:84-104`, `data/manifest.json:22`
**Bulgu:** Manifest **tek global** NoData yüzdesi (4.077%) raporluyor. Bant başına ayrılmış değil. S1 (örn. ölçü kapsama dışı bölge yüksek NoData) ortalama içinde gizlenebilir. P3 datamodule mean/std hesaplarken bant başına NoData maskesini kullanıyor olsa da (ki kullanıyor — `np.isfinite & != NODATA` filtresi 09_export_manifest.py:93-100), manifest tüketicisi (P5) "hangi bantta veri kaybı?" sorusunu yanıtlayamaz.
**Öneri:** `bands[i].nodata_pct` alanı ekle (T1.9 zaten bant başına istatistik döngüsünde — basit ek hesap).

#### 🟡 [M-3] `files` map eksik (Landsat, tile_index referansı yok)
**Dosya:** `data/manifest.json:225-230`
**Bulgu:** `files` sözlüğü {full_ard, s1_stack, dem, slope}. Landsat snapshot'ları (T1.10 5 dosya) ve `data/tiles/tile_index.json` (varsa) yok. P5 Landsat dosyalarını **ad-konvansiyonu** ile bulmak zorunda — kırılgan.
**Öneri:** `files.landsat: ["data/landsat/L5_1985.tif", ...]` ve `files.tile_index: "data/tiles/tile_index.json"` ekle.

#### 🟡 [M-4] `tile_index.json` yerel diskte yok (manifest belirtir)
**Dosya:** `code/p1/08_tile_splitting.py:121-131`, `code/p1/09_export_manifest.py:158-163`
**Bulgu:** T1.8 `tile_index.json`'u yazıyor (script var ✓), T1.9 onu okumaya çalışıyor ama yoksa default değerle (`tile_size=256, overlap=32, stride=224`) silently doldurmuş. Bu commit'te makinede `data/tiles/` boş olduğu için index dosyası burada da yok (Drive'da olabilir). T1.9 bu durumda bile manifest üretiyor — **defaults'a güveniyor**, gerçek üretilen tile metadata'sıyla cross-check yapmıyor.
**Öneri:** T1.9'da `tile_index.json` mecburi yap; yoksa fail.

#### ℹ [I-2] Bounds, shape, tile-count matematiksel olarak tutarlı
**Bulgu:** (674060−647520)/20 = 1327 sütun, (4302040−4279300)/20 = 1137 satır. n_rows = ⌈(1137−32)/224⌉ = 5, n_cols = ⌈(1327−32)/224⌉ = 6, total = 30 ✓. Manifest claim'leri kendi içinde tutarlı.

#### 🟢 [L-1] Mean/std değerleri coğrafi-fiziksel olarak inanılır
**Bulgu:**
- DEM mean = 1088 m ✓ Kapadokya platosu (~1000–1200 m beklenti).
- Slope std = 7.4°, mean = 7.85° ✓ tepelik bölge.
- VV = −12.7 dB, VH = −21.5 dB ✓ kuru karışık zemin tipik.
- NDVI = 0.18 ✓ karışık tarım/çıplak.
- BSI = 0.13, Albedo = 0.23 ✓ pomza/açık zemin için makul.
- S2 reflectance 1254–3512 DN aralığı ✓ scale=10000 ile [0.125, 0.351] makul.

---

### 2.3 Hata / edge-case dayanıklılığı

#### 🔴 [C-3] Edge-tile cosine-blend bölme tehlikesi
**Dosya:** `code/p3/07_inference.py:217-220`
**Bulgu:** `prob_acc /= np.maximum(weight_acc, 1e-6)`. Bir piksel hiç bir tile tarafından kapsanmazsa weight_acc=0 → bölme 1e-6'ya düşer → prob × 1e6 = saçma değer. NoData padding zaten edge tile'lara konmuş, bu yüzden gerçek riski az ama 256×256 grid kenarlarında AOI sınırı dışı pikseller için tetiklenebilir.
**Öneri:** `prob_acc[weight_acc < 1e-3] = 0.5` (belirsizlik = 0.5 RAW olasılık) açık fallback ekle.

#### 🔴 [C-4] `predict_raw()` model checkpoint missing → unhandled crash
**Dosya:** `code/p3/07_inference.py:58-66`
**Bulgu:** `torch.load(model_path)` doğrudan; dosya yoksa `FileNotFoundError` raw çıkar. P5 dashboard runtime'ında bu çağrılırsa kullanıcı kripto traceback görür.
**Öneri:** `if not Path(model_path).exists(): raise RuntimeError(f"Model bulunamadı: {model_path}. Önce T3.5 fine-tune'u tamamla veya plan B fallback kullan.")` ekle.

#### 🟠 [H-3] T1.9 NoData budget margin %0.92 (5%'in 1% altında)
**Dosya:** `code/p1/09_export_manifest.py:30,103-104`, `data/manifest.json:22`
**Bulgu:** Şu anki NoData oranı 4.077%, eşik 5%. P2 ignore_mask geldiğinde NoData artar (T2.6 + T2.8 raster mask). Eşiği aşarsa T1.9 `sys.exit(1)` → pipeline durur, **ama T1.8 tile splitting zaten disk'e yazmış** — orphan tile'lar.
**Öneri:** T1.9'u T1.8'den ÖNCE çalıştır (validation gate); ya da T1.9 fail olduğunda cleanup adımı (tiles dir temizle) ekle.

#### 🟠 [H-4] `06_train.py` checkpoint atomic-rename değil, NaN-loss guard yok
**Dosya:** `code/p3/06_train.py:170,220-227`
**Bulgu:**
- `clip_grad_norm_(max_norm=5.0)` var ✓ ama loss NaN olursa yine save ediliyor — best_iou kontrolü iou'ya bakar ama iou da NaN ise undefined davranış. `if not torch.isfinite(loss): break` yok.
- `torch.save(...)` direct write — kesinti durumunda korrupt checkpoint. Atomic temp+rename pattern yok.
**Öneri:** Epoch başında `if not torch.isfinite(loss).all(): logger.error(...); break` ekle. Save: `torch.save(state, tmp); tmp.rename(final)` deseni.

#### 🟠 [H-5] DataModule -9999 → 0 dönüşümü normalizasyona girmiş histogramı bozar
**Dosya:** `code/p3/03_datamodule.py:194-200`
**Bulgu:** Akış: tile oku → -9999 NoData yerinde duruyor → mean/std normalizasyon → `nan_to_num` 0'a → mask ignore_idx=255. Normalizasyondan **önce** -9999 yerine bant ortalamasıyla doldurma yapılmıyor; bu yüzden NoData pikselleri normalizasyon içinde z = (−9999−1254)/532 ≈ −20.7 değerine gider, ardından 0'a clip. Loss'tan dışlanıyor (mask ignore) ama batch normalizasyonu / AdaIN gibi katmanlar varsa istatistik bozulur.
**Etki:** UNet'te batch-norm yok (SSL4EO ResNet encoder var), bu yüzden gerçek etkisi düşük. Yine de temiz değil.
**Öneri:** Tile yüklemeden hemen sonra `tile[tile == -9999] = mean[c]` (per-channel) yap; sonra normalize.

#### 🟡 [M-5] Synthetic sanity gerçek dağılımı temsil etmiyor
**Dosya:** `code/p3/05_synthetic_sanity.py:73`
**Bulgu:** `torch.randn()` (Gauss 0,1) — P1 ARD'nin gerçek dağılımı çok farklı (S2 1000–3500 DN, S1 negatif dB, vs.). Test forward+backward FINITE çıkıyor ama gerçekte first batch normalization/clamp davranışı farklı olabilir. NoData=-9999 simülasyonu yok.
**Öneri:** Manifest mean/std'den `torch.randn() * std + mean` (per-channel) ile sentetik üret; %5 piksele -9999 enjekte et.

#### 🟢 [L-2] Resume-from-checkpoint yok
**Dosya:** `code/p3/06_train.py:69`
**Bulgu:** `--start-fold 3` ile fold atlanabilir, ama epoch ortasında kesinti olursa o fold sıfırdan başlar.
**Öneri:** Hackathon süresinde önemli değil; production reuse için ekle.

---

### 2.4 Bilimsel doğruluk

#### ℹ [I-3] Formüller doğru ve dokümante
- **Liang 2001 albedo:** `0.356·B2 + 0.130·B4 + 0.373·B8 + 0.085·B11 + 0.072·B12 − 0.0018` ✓ (`07_full_coregistration.py:113-127`).
- **NDVI, BSI:** Standart formüller ✓.
- **Lee filter (S1):** ENL=4.4 (Sentinel-1 IW GRD ESA standart) ✓ (`05_sentinel1_grd_fetch.py:23-31`).
- **Cloud mask:** SCL kategorileri 4,5,6,11 KEEP / 3,8,9,10,1 MASK ✓ ESA L2A spec.
- **Landsat C2 L2 ölçek:** `0.0000275 × DN − 0.2` ✓ resmi formül (`10_landsat_snapshots.py:42-46`).
- **Roy 2016 cross-sensor:** P5'in sorumluluğu, P1 sadece ham SR export ediyor ✓.

#### 🟢 [L-3] Reflectance scale auto-detect heuristic kırılgan
**Dosya:** `code/p1/07_full_coregistration.py:120`
**Bulgu:** `reflectance_scale = 1e-4 if valid.any() and np.nanmax(b2[valid]) > 1.5 else 1.0`. Heuristic — eğer B2 max > 1.5 ise DN, değilse zaten reflectance. Edge case: çok karanlık AOI'da B2 max < 1.5 olabilir → yanlış scale → albedo 0–1 yerine 0–0.0001.
**Öneri:** Manifest scale değerini parametre olarak okusun. Hackathon kapsamında düşük risk (Avanos güneşli — B2 reflectance > 1.5 garantili).

---

### 2.5 Reprodüksibilite

#### 🟠 [H-6] P3 `requirements.txt` çoğunlukla `>=` (loose pin)
**Dosya:** `code/p3/requirements.txt`
**Bulgu:** P1 sıkı pin (`==0.1.384` vs.) ✓; P3 loose (`torch>=2.1.0`, `segmentation_models_pytorch>=0.3.3`). Hackathon'dan sonra çevreyi yeniden kurarsan torch 2.5+ ve smp 0.4+ gelir, breaking changes muhtemel.
**Öneri:** RUN-BLOCK'larda test edilmiş tam versiyonları sabitle.

#### 🟡 [M-6] Hardcoded Colab Drive path
**Dosya:** `code/p3/06_train.py:10-15`
**Bulgu:** `/content/drive/MyDrive/pomzadoya/...` default path. Required arg'lar override ediyor ✓ ama yerel testte unutulursa Colab path Linux/Windows'ta yok → açıklayıcı hata yerine permission/path error.
**Öneri:** Default'u `None` yap, `--data-dir` zorunlu kıl.

#### 🟡 [M-7] GCP project hardcoded `pomza-495012`
**Dosya:** `code/p1/05_sentinel1_grd_fetch.py:11`, `06_dem_slope.py:11`, `10_landsat_snapshots.py:18`
**Bulgu:** Başka ekip üyesi (örn. P5 helper) ya da gelecekte fork'lanan projede GCP project ID değişir; hardcoded → 3 dosyada bul-değiştir gerekecek.
**Öneri:** `os.environ.get("GEE_PROJECT", "pomza-495012")` pattern; `.env.example` dosyası.

#### 🟡 [M-8] P1 service-account vs personal-auth çelişkisi
**Dosya:** `code/p1/05_sentinel1_grd_fetch.py:12-13` yorumlar
**Bulgu:** Yorum: "Service account Drive kotası yok → kişisel auth". Ama `ee.Initialize(project=...)` yine GCP project parametresi alıyor — auth fallback davranışı belirsiz. Yeni bir kullanıcı için "hangi auth?" karar ağacı belgesiz.
**Öneri:** `handoff/P1_BRIEFING.md`'ye 3-adımlık karar ağacı ekle. Veya `code/p1/AUTH.md`.

#### ℹ [I-4] Seed=42 + deterministic
**Dosya:** `code/p3/06_train.py:243-244`
**Bulgu:** torch + numpy seed sabit ✓.

---

### 2.6 Pipeline orkestrasyonu

#### 🟠 [H-7] `run_pipeline.sh` GEE async polling/state yok
**Dosya:** `code/p1/run_pipeline.sh:28-65`
**Bulgu:** Script T1.3 GEE export tetikler → script bitirir → kullanıcı 30dk bekleyip Drive'dan elle indirir → script'i **tekrar çalıştırır**. İkinci run'da T1.4 dosyayı bulur ✓ ama T1.5/T1.6 **yine GEE task tetikler** (duplicate export!), T1.7 girdileri bekler. Script idempotent değil — her run yeni async export kuyruğa yığar.
**Etki:** GEE task quota dolar, Drive'da `_v1`, `_v2` çakışan dosyalar.
**Öneri:** Her GEE script'in başına `if EXPECTED_OUTPUT.exists(): print("skip"); sys.exit(0)` guard ekle. Veya `run_pipeline.sh`'i wave-based böl: `run_pipeline.sh --wave 1` (GEE start), `--wave 2` (local processing).

#### 🟠 [H-8] `set -euo pipefail` ile "ATLANDI" sessiz akış çelişkisi
**Dosya:** `code/p1/run_pipeline.sh:10,38-44,72-83`
**Bulgu:** `set -e` aktif, ama T1.4/T1.7/T1.8/T1.9 her biri `if [ -f "$VAR" ]; then ... else echo "ATLANDI"; fi` — else dalı `exit 1` yerine sessiz devam. Pipeline bütün-hat çalışmasa bile script success exit eder. Kullanıcı "tamam mı?" sorusuna `$?=0` görür ve yanıltılır.
**Öneri:** Else dallarına `exit 2` (skip), `exit 1` (failure) ayrı kodlar. Ya da `--strict` flag ile her ATLANDI fail.

#### 🟡 [M-9] Pipeline sıralama mantığı: T1.8 önce, T1.9 sonra (yanlış sıra)
**Dosya:** `code/p1/run_pipeline.sh:88-108`
**Bulgu:** T1.8 (tile splitting) NoData budget'i hâlâ kontrol edilmemiş ARD üzerinden tile'lar üretir; T1.9 bunun ardından gelir. T1.9 fail ederse T1.8 zaten 30 dosya yazmış — orphan/inkonsistent state.
**Öneri:** T1.9 validation kısmını T1.8 öncesine al (gate). Veya T1.8 + T1.9 atomic transaction (temp dir → final).

#### 🟢 [L-4] `set -euo pipefail`'ın `pipefail` kısmı kullanılmamış
**Bulgu:** Pipe (`|`) kullanan komut yok → `pipefail` no-op. Kullanım niyeti açık (defensiveness) ✓.

---

### 2.7 Cross-platform & path hijyeni

#### 🟠 [H-9] `run_pipeline.sh` Windows'ta çalışmaz, PowerShell eşleniği yok
**Dosya:** `code/p1/run_pipeline.sh`
**Bulgu:** Proje sahibi Windows 11. WSL2 kurulumu briefing'te zorunlu kılınmamış. PowerShell `run_pipeline.ps1` yok. Mevcut iş akışında P1 her .py dosyasını tek tek çalıştırıyor olabilir (commit history bunu destekliyor — her T1.x ayrı commit).
**Öneri:** `run_pipeline.ps1` (en azından T1.2 + T1.4 + T1.7 + T1.8 + T1.9 — yerel python adımları) ekle.

#### 🟡 [M-10] `Path(__file__).resolve().parents[2]` cwd-bağımsız ama validate edilmez
**Dosya:** Tüm P1 .py dosyaları (5 dosyada aynı pattern)
**Bulgu:** Pattern doğru ✓ ama `REPO.is_dir()` veya beklenen alt klasör (`data/`, `code/`) varlık check'i yok. Subprocess child'da `__file__` bazen göreli olabilir → yanlış REPO çözümlenir.
**Öneri:** Her script başına `assert (REPO / "data").is_dir(), f"Bekleneyen repo kökü: {REPO}"`.

#### 🟡 [M-1 tekrar] Manifest backslash format (yukarıda)

---

### 2.8 Güvenlik / secret hijyeni

#### 🟢 [L-5] `.gitignore` kapsamlı
**Dosya:** `.gitignore`
**Bulgu:** `*.json` (ama `manifest.json` whitelist), `.netrc`, `.env`, `__pycache__`, model `.pt`, raster `.tif` filterleniyor. Service account JSON için `pomzadoya-sa.json` özel ya da `*.json` genel filter. Commit history'de credential görünmüyor (3232d22 commit mesajı "Service account auth" ama dosya değil).
**Öneri:** Ekstra: `git-secrets` veya `pre-commit` hook ile JSON içinde `"type": "service_account"` pattern'i blokla.

#### 🟡 [M-11] Colab notebook (`01_gee_setup.ipynb`) cell output'larında auth token sızabilir
**Dosya:** `code/p1/01_gee_setup.ipynb`
**Bulgu:** Notebook git'te (✓ `.ipynb_checkpoints/` filterli ama `.ipynb` kendisi commit ediliyor olabilir). Cell output'unda `ee.Authenticate()` token print etmez normalde, ama print debug eklenmişse risk var. Bu raporda ipynb içeriği taranmadı (binary tarama gereksiz olur).
**Öneri:** `nbstripout` pre-commit hook ekle — tüm output'ları temizler.

#### ℹ [I-5] No secrets in committed code
**Bulgu:** P1 source dosyalarında hardcoded API key/token yok ✓.

---

### 2.9 Test / sanity coverage

#### 🟡 [M-12] Gerçek tile fixture yok, integration test yok
**Bulgu:** Synthetic sanity dışında hiçbir test yok. P1 ARD üretici fonksiyonların unit test'i yok (örn. `_compute_ndvi`, `_compute_bsi`, `_compute_albedo` — saf NumPy, kolay test). Manifest doğrulama (T1.9) bile bir kez gerçek dosyayla çalışıyor; regression yok.
**Öneri:** `tests/test_indices.py` küçük: NumPy array ile NDVI=(0.5−0.1)/(0.5+0.1)=0.667 kontrolü. P3 datamodule için 32×32 fake tile + manifest mock ile fixture.

#### 🟢 [L-6] Sanity script PASS/FAIL belirsiz
**Dosya:** `code/p3/05_synthetic_sanity.py`
**Bulgu:** Çıktı print bazlı; `sys.exit(1)` only loss not finite ise. Daha geniş "PASS criteria" yok (örn. loss düşmesi bekleniyor mu?).

---

### 2.10 Dokümantasyon

#### ℹ [I-6] Briefing'ler ve master-coordination çok iyi
**Bulgu:** `handoff/00_MASTER_COORDINATION.md`, `01_STATUS_REPORT.md`, `P1_BRIEFING.md`–`P5_BRIEFING.md` — 24h hackathon için olağanüstü yapılandırılmış. Critical path, risk path, plan B'ler, manuel iş yükü dağılımı net.

#### 🟡 [M-13] SSL4EO bant mapping docstring'de belirsiz (C-2 ile bağlı)
**Dosya:** `code/p3/02_ssl4eo_pretrained.py:14-15`
**Bulgu:** "SSL4EO-S12 13 Sentinel-2 bandi ile pretrain edildi (B01..B12 + B8A)" — sıra net değil. P1 bant sırasıyla nasıl hizalandığı yok. Yukarıda C-2 olarak Critical işaretlendi.

#### 🟢 [L-7] P3 docstring I/O kontratları net
**Bulgu:** `predict_raw()` shape/dtype/range açık (`07_inference.py:97-101`), `BCEDiceLoss` parametreleri açık (`04_loss_metrics.py`).

---

## 3. Kritik Bulgular Özet (Aksiyon Sıralı)

| # | Severity | Bulgu | Sahip | Süre tahmini |
|---|---|---|---|---|
| **C-1** | 🔴 | Manifest scale meta-veri yanıltıcı | P1 | 15dk (T1.9 patch) |
| **C-2** | 🔴 | SSL4EO ↔ P1 bant mapping belgesiz | P3 | 30dk (docstring + load log) |
| **C-3** | 🔴 | Edge-tile blend bölme tehlikesi | P3 | 10dk (07_inference.py:220 patch) |
| **C-4** | 🔴 | predict_raw model-missing crash | P3 | 5dk (try/except wrap) |
| **H-1** | 🟠 | DEFAULT mean/std fallback warning yok | P3 | 5dk |
| **H-2** | 🟠 | predict_raw input kanal validate yok | P3 | 5dk |
| **H-3** | 🟠 | NoData budget margin %0.92 | P1 | 30dk (atomik T1.8+T1.9) |
| **H-4** | 🟠 | Train NaN-loss guard + atomic save yok | P3 | 15dk |
| **H-5** | 🟠 | -9999 → 0 normalizasyon kirliliği | P3 | 15dk |
| **H-6** | 🟠 | P3 deps loose pin | P3 | 10dk (pip freeze) |
| **H-7** | 🟠 | GEE async idempotency yok | P1 | 30dk |
| **H-8** | 🟠 | Pipeline "ATLANDI" sessiz exit | P1 | 15dk |
| **H-9** | 🟠 | PowerShell eşleniği yok (Windows) | P1 | 45dk |

**Toplam Critical+High aksiyon süresi: ~3.5 saat.**
Hackathon kalan süresine göre öncelik: C-2, C-3, C-4, H-1, H-2 (P3 fine-tune öncesi mecbur).

---

## 4. Boyut Skorları — Dayanak

```
1. Kontrat netliği            72/100  (-15 C-1, -10 C-2, -3 H-1)
2. Veri sözleşmesi             78/100  (-7 M-2, -7 M-3, -6 M-4, -2 M-1)
3. Hata/edge-case             62/100  (-12 C-3, -10 C-4, -8 H-3, -5 H-4, -3 H-5)
4. Bilimsel doğruluk          88/100  (-7 L-3, -5 ölçek heuristic)
5. Reprodüksibilite            65/100  (-12 H-6, -8 M-6, -8 M-7, -7 M-8)
6. Pipeline orkestrasyonu     55/100  (-15 H-7, -15 H-8, -10 M-9, -5 L-4)
7. Cross-platform             60/100  (-15 H-9, -15 M-1, -10 M-10)
8. Güvenlik                    75/100  (-15 M-11, +ext credit .gitignore)
9. Test coverage               55/100  (-25 M-12, -10 L-6, -10 sentetik gerçeklik)
10. Dokümantasyon              82/100  (-10 M-13, -8 SSL4EO mapping)

Ağırlıklı toplam: 69.0/100
```

---

## 5. Hackathon Karar Çerçevesi

### 5.1 "Saat 18 entegrasyon başlangıcı" için yeterli mi?

| Bağımlılık | Durum | Değerlendirme |
|---|---|---|
| P1 → P2 (S2 RGB altlık, saat 4) | ✅ | Drive'da `s2_l2a_avanos_median_2024_20m.tif` |
| P1 → P3 (Full ARD, saat 8) | ✅ | `data/ard/full_ard_20m.tif` (manifest claim) |
| P1 → P3 (tiles, saat 9-12) | ✅ | 30 tile (manifest claim) |
| P1 → P3 (manifest mean/std) | ⚠ | Var ama **scale uyarısı eksik** (C-1) |
| P3 fine-tune girdileri | ⚠ | T2.7 split + T2.8 mask **bekliyor** (P2 çıktıları) |
| P3 → P4/P5 (`predict_raw`) | ⚠ | API hazır, **C-3/C-4 fix önerilir** |

**Karar:** P1 mevcut çıktıları downstream için yeterli. P3 fine-tune (T3.5) başlamadan önce **mecbur**: C-2 (bant mapping doc), H-1 (manifest required flag).

### 5.2 Plan B fallback durumu

`code/p3/12_fallback_threshold.py` mevcut ✓ — model collapse senaryosunda BSI+Albedo+NDVI threshold ile pomza maskesi üretiyor. Fallback'in varlığı resilience puanını yukarı çekiyor.

### 5.3 Production reuse için önemli olanlar (hackathon dışı)

- C-1, C-2, C-3, C-4 (4 critical)
- H-7 (idempotency), H-9 (Windows), M-12 (test fixture), M-1 (cross-platform manifest)

---

## 6. Öneri Buckets

### 6.1 Hackathon-içi must-fix (≤30 dk)

1. C-2: `02_ssl4eo_pretrained.py`'a SSL4EO_BAND_ORDER + P1_BAND_ORDER + CHANNEL_MAP tablosu ekle.
2. C-3: `07_inference.py:220` öncesi `weight_acc < 1e-3` fallback.
3. C-4: `07_inference.py:58` checkpoint exists check + RuntimeError.
4. H-1: `03_datamodule.py:262` warning ekle.
5. H-2: `predict_raw()` başına in_channels assert.

### 6.2 Hackathon-arası nice-to-have (entegrasyon penceresinde)

- C-1 manifest scale notu.
- H-3 NoData budget atomicity (T1.8/T1.9 sıra düzelt).
- H-4 NaN guard + atomic checkpoint.
- M-1 manifest forward-slash.

### 6.3 Production reuse

- M-12 test fixtures.
- H-9 PowerShell port.
- H-6 deps tight pin.
- M-7 env var GEE_PROJECT.
- M-11 nbstripout.

---

## 7. Ekler

### 7.1 Yerel disk envanteri (analiz anı)

```
data/manifest.json           ✓ 5.7 KB (T1.9 çıktısı)
data/aoi/avanos_aoi.geojson  ✓ 391 B
data/aoi/avanos_aoi.gpkg     ✓ 119 KB
data/aoi/avanos_aoi_utm36n.geojson  ✓ 573 B
data/aoi/avanos_utm36n.geojson      ✓ 573 B (duplicate sanırım)
data/{ard, tiles, s1_stack, dem, landsat, layers, change, temporal, labels}/  ✗ Drive'da
```

### 7.2 İncelenen dosyalar

```
code/p1/02_aoi_avanos.py            (45 satır)
code/p1/03_sentinel2_l2a_fetch.py    (65)
code/p1/04_s2_coregistration.py      (171)
code/p1/05_sentinel1_grd_fetch.py    (76)
code/p1/06_dem_slope.py              (71)
code/p1/07_full_coregistration.py    (208)
code/p1/08_tile_splitting.py         (142)
code/p1/09_export_manifest.py        (223)
code/p1/10_landsat_snapshots.py      (125)
code/p1/run_pipeline.sh              (124)
code/p1/requirements.txt
code/p3/02_ssl4eo_pretrained.py      (281)
code/p3/03_datamodule.py             (326)
code/p3/04_loss_metrics.py           (252)
code/p3/05_synthetic_sanity.py       (129)
code/p3/06_train.py                  (280)
code/p3/07_inference.py              (421)
code/p3/08_gradcam.py                (165)
code/p3/09_ablation.py               (164)
code/p3/10_threshold_tuning.py       (114)
code/p3/11_export_fp16.py            (139)
code/p3/12_fallback_threshold.py     (126)
code/p3/requirements.txt
data/manifest.json
handoff/00_MASTER_COORDINATION.md
handoff/01_STATUS_REPORT.md
handoff/P1_BRIEFING.md (kısmi)
handoff/P3_BRIEFING.md (kısmi)
```

Toplam: ~3650 satır Python + 124 satır shell + 5.7 KB manifest + ~1500 satır Markdown briefing.

### 7.3 Yöntem notu

- 3 paralel keşif ajanı: P3 kod incelemesi, pipeline orkestrasyon incelemesi, manifest+veri kontratı incelemesi.
- Sentez: 31 bulgu → 10 boyut → ağırlıklı skor.
- Hiçbir kod değiştirilmedi; hiçbir script çalıştırılmadı; Drive'daki gerçek raster içeriklerine erişim olmadı (manifest'in kendisi source-of-truth alındı).

### 7.4 Sınırlamalar

- Drive'daki gerçek `full_ard_20m.tif`'in NoData yüzdesi gerçekten 4.077% mi, manifest'in kendisi yalan söylüyor mu — **doğrulanamadı**.
- Tile içeriklerinin 256×256 olduğu doğrulanamadı (sadece script'in öyle yazdığı doğrulandı).
- P2 çıktıları (T2.7 split, T2.8 mask) henüz yok — P3 fine-tune entegrasyonu test edilemedi.
- Notebook (`01_gee_setup.ipynb`) cell output güvenliği taranmadı (binary).

---

*v1 raporu sonu. v2: P2 çıktıları + ilk fine-tune sonuçları geldikten sonra entegrasyon QA'i + Drive-doğrulamalı raster sanity.*
