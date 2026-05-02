# RUN-BLOCK [T3.5] — SSL4EO-S12 U-Net 5-fold blok CV fine-tune (CRITICAL PATH)

**Owner:** P3 — ML Muhendisi
**Hedef ortam:** Colab Pro H100 / A100 (b=4 -> 0.89 GB ile rahat)
**Sure:** 1-2 saat (H100, ~250-500 tile, 30 epoch). 3h budget icinde.
**Onkosul (saat ~12-13):**
- ✅ P1 T1.7 ARD: `/content/drive/MyDrive/pomzadoya/data_p1/ard/full_ard_20m.tif`
- ✅ P1 T1.8 tile'lar: `/content/drive/MyDrive/pomzadoya/data_p1/tiles/*.tif`
- ✅ P1 T1.9 manifest: `/content/drive/MyDrive/pomzadoya/data_p1/manifest.json` (veya `data_p1/ard/manifest.json`)
- ✅ P2 T2.6 split JSON: `data_p1/labels/blok_cv_split.json` veya `data/labels/blok_cv_split.json` (P2 hangi case kullaniyorsa)
- ✅ P2 T2.8 raster mask: `data_p1/labels/full_mask.tif` veya `data/labels/full_mask.tif` (CRITICAL — saat ~13)

**ONEMLI — Drive klasor yapisi (2026-05-02 saat ~21 itibariyle):**
- P1 capital `Pomzadoya/` kullaniyor (`data/aoi, ard, dem, landsat, s1_stack, s2_raw, tiles`).
- P3 lowercase `pomzadoya/` kullaniyor (`data/, models/, reports/`).
- P3 -> P1 koprusu: `pomzadoya/data_p1` symlink -> `Pomzadoya/data/`.
- P2 nereye yazacagi belli degil; on-flight kontrol her iki path'i de tarar.

**Karar referanslari:**
- [K#10] Spatial 5-fold blok CV (Roberts 2017)
- [K#13] AMP FP16 (export profili)
- [K#14] F1-max threshold (validation raporu)
- [K#6] RAW olasilik output, threshold YASAK

---

## ON-FLIGHT KONTROL (saat ~12, P1+P2 tesliminden once)

Yeni hucreye yapistir — bu hucre path resolver gibi davranir,
bulduklarini /tmp/p3_state/paths.sh dosyasina yazar; egitim
hucresi bu env dosyasini source eder.

```bash
%%bash
echo "=== Path resolver: P1 ARD + tiles + manifest ==="
ARD_CANDIDATES=(
  "/content/drive/MyDrive/pomzadoya/data_p1/ard/full_ard_20m.tif"
  "/content/drive/MyDrive/pomzadoya/data_p1/ard/full_ard.tif"
  "/content/drive/MyDrive/Pomzadoya/data/ard/full_ard_20m.tif"
)
ARD=""; for f in "${ARD_CANDIDATES[@]}"; do [ -f "$f" ] && ARD="$f" && break; done
echo "ARD: ${ARD:-YOK}"

TILES_CANDIDATES=(
  "/content/drive/MyDrive/pomzadoya/data_p1/tiles"
  "/content/drive/MyDrive/pomzadoya/data_p1/ard/tiles"
  "/content/drive/MyDrive/Pomzadoya/data/tiles"
)
TILES=""; for d in "${TILES_CANDIDATES[@]}"; do
  [ -d "$d" ] && [ "$(ls "$d"/*.tif 2>/dev/null | wc -l)" -gt 0 ] && TILES="$d" && break
done
echo "TILES: ${TILES:-YOK}  (sayi: $(ls "$TILES"/*.tif 2>/dev/null | wc -l))"

MANIFEST_CANDIDATES=(
  "/content/drive/MyDrive/pomzadoya/data_p1/ard/manifest.json"
  "/content/drive/MyDrive/pomzadoya/data_p1/manifest.json"
  "/content/drive/MyDrive/Pomzadoya/data/manifest.json"
)
MANIFEST=""; for f in "${MANIFEST_CANDIDATES[@]}"; do [ -f "$f" ] && MANIFEST="$f" && break; done
echo "MANIFEST: ${MANIFEST:-YOK}"

echo ""
echo "=== Path resolver: P2 split + mask ==="
SPLIT_CANDIDATES=(
  "/content/drive/MyDrive/pomzadoya/data_p1/labels/blok_cv_split.json"
  "/content/drive/MyDrive/pomzadoya/data/labels/blok_cv_split.json"
  "/content/drive/MyDrive/Pomzadoya/data/labels/blok_cv_split.json"
)
SPLIT=""; for f in "${SPLIT_CANDIDATES[@]}"; do [ -f "$f" ] && SPLIT="$f" && break; done
echo "SPLIT: ${SPLIT:-YOK}"

MASK_CANDIDATES=(
  "/content/drive/MyDrive/pomzadoya/data_p1/labels/full_mask.tif"
  "/content/drive/MyDrive/pomzadoya/data/labels/full_mask.tif"
  "/content/drive/MyDrive/Pomzadoya/data/labels/full_mask.tif"
)
MASK=""; for f in "${MASK_CANDIDATES[@]}"; do [ -f "$f" ] && MASK="$f" && break; done
echo "MASK: ${MASK:-YOK}"

CKPT="/content/drive/MyDrive/pomzadoya/models/pretrained/models--wangyi111--SSL4EO-S12/snapshots/75c72195d35201dc1fb210818993518c25da566b/B3_rn50_moco_0099_full_ckpt.pth"
echo "CKPT: $([ -f "$CKPT" ] && echo "$CKPT" || echo "YOK")"

mkdir -p /tmp/p3_state
cat > /tmp/p3_state/paths.sh << EOF
export ARD="$ARD"
export TILES="$TILES"
export MANIFEST="$MANIFEST"
export SPLIT="$SPLIT"
export MASK="$MASK"
export CKPT="$CKPT"
EOF
echo ""
echo "=== /tmp/p3_state/paths.sh ==="
cat /tmp/p3_state/paths.sh

echo ""
echo "=== Saglik kontrolu ==="
[ -n "$ARD" ] && [ -n "$TILES" ] && [ -n "$SPLIT" ] && [ -n "$MASK" ] && [ -n "$CKPT" ] && \
  echo "  -> TUM ONKOSULLAR HAZIR, T3.5 BASLATILABILIR." || \
  echo "  -> EKSIK ONKOSUL VAR. P1/P2'den eksiklere bak."

echo ""
echo "=== Mask + tile CRS uyumu (eger ikisi de varsa) ==="
if [ -n "$MASK" ] && [ -n "$TILES" ]; then
python << EOF
import rasterio, glob, numpy as np
mask = rasterio.open("$MASK")
print(f"mask CRS={mask.crs}, bounds={mask.bounds}, shape={mask.shape}, dtype={mask.dtypes[0]}")
data = mask.read(1)
u, c = np.unique(data, return_counts=True)
print(f"mask unique: {dict(zip(u.tolist(), c.tolist()))}")
mask.close()

t = rasterio.open(sorted(glob.glob("$TILES/*.tif"))[0])
print(f"\ntile CRS={t.crs}, bounds={t.bounds}, count={t.count}, shape={t.height}x{t.width}, dtype={t.dtypes[0]}")
t.close()
EOF
fi

echo ""
echo "=== Split JSON ozet ==="
if [ -n "$SPLIT" ]; then
python << EOF
import json
sp = json.load(open("$SPLIT"))
print(f"fold sayisi: {len(sp)}")
for k, v in sorted(sp.items()):
    print(f"  {k}: train={len(v['train'])} val={len(v['val'])}")
EOF
fi
```

Eski (referans icin) — basit dosya kontrol seti:
```bash
%%bash
cd /content/Pomzadoya
echo "=== Onkosul dosya kontrolu (referans, path resolver kullanmaz) ==="
PROJ=/content/drive/MyDrive/pomzadoya
for f in \
  data/ard/full_ard_20m.tif \
  data/ard/manifest.json \
  data/labels/blok_cv_split.json \
  data/labels/full_mask.tif \
  models/pretrained/models--wangyi111--SSL4EO-S12/snapshots/75c72195d35201dc1fb210818993518c25da566b/B3_rn50_moco_0099_full_ckpt.pth
do
  if [ -f "$PROJ/$f" ]; then
    sz=$(du -h "$PROJ/$f" | cut -f1)
    echo "  VAR ($sz): $f"
  else
    echo "  YOK : $f"
  fi
done
echo ""
echo "=== Tile sayisi ==="
ls $PROJ/data/ard/tiles/*.tif 2>/dev/null | wc -l
echo ""
echo "=== Split JSON ozet ==="
python -c "
import json
sp = json.load(open('$PROJ/data/labels/blok_cv_split.json'))
print(f'fold sayisi: {len(sp)}')
for k, v in sorted(sp.items()):
    print(f'  {k}: train={len(v[\"train\"])} val={len(v[\"val\"])}')
print('train+val toplam:', sum(len(v['train'])+len(v['val']) for v in sp.values()) // len(sp))
"
echo ""
echo "=== Mask CRS + bounds (tile uyumu icin) ==="
python << 'EOF'
import rasterio
mask = rasterio.open("/content/drive/MyDrive/pomzadoya/data/labels/full_mask.tif")
print(f"mask CRS    : {mask.crs}")
print(f"mask bounds : {mask.bounds}")
print(f"mask shape  : {mask.shape}")
print(f"mask dtype  : {mask.dtypes[0]}")
import numpy as np
data = mask.read(1)
unique, counts = np.unique(data, return_counts=True)
print(f"mask unique values: {dict(zip(unique.tolist(), counts.tolist()))}")
mask.close()

import glob
tiles = sorted(glob.glob("/content/drive/MyDrive/pomzadoya/data/ard/tiles/*.tif"))[:1]
if tiles:
    t = rasterio.open(tiles[0])
    print(f"\nornek tile : {tiles[0]}")
    print(f"tile CRS   : {t.crs}")
    print(f"tile bounds: {t.bounds}")
    print(f"tile shape : ({t.count}, {t.height}, {t.width})")
    print(f"tile dtype : {t.dtypes[0]}")
    t.close()
EOF
```

**Beklenen:** Tum dosyalar VAR, tile/mask CRS ayni, mask unique = `{0, 1}` veya `{0, 1, 255}`.

**Hata varsa:**
- `mask CRS != tile CRS` -> P1+P2 co-registration kirik. Devam etme, P1/P2'ye HELP.
- `mask unique = {0}` (hep sifir) -> P2 T2.7 mask uretimi sorunlu.
- `tile shape != (17, 256, 256)` -> P1 T1.8 tile splitting yanlis kanal sayisi.

---

## AMPIRIK MEAN/STD HESABI (saat ~11, P1 ARD gelir gelmez)

P1 manifest.json'unda mean/std YOK (2026-05-02 itibariyle). DEFAULT_MEAN/STD
placeholder, T3.5 normalize dogrulugu icin **gercek tile'lardan ampirik
hesap GEREKLI**. Yoksa model yanlis kanal istatistikleri ile egitilir.

P1 ARD/tiles geldikten sonra (path resolver hucresi `TILES != YOK`) bu hucreyi koş:

```python
import numpy as np
import rasterio
import glob
import json
import os
from pathlib import Path

# Path resolver env'i Python'a aktar
state_path = "/tmp/p3_state/paths.sh"
env = {}
for line in open(state_path):
    line = line.strip()
    if line.startswith("export "):
        k, _, v = line[len("export "):].partition("=")
        env[k] = v.strip('"')
TILES = env["TILES"]
MANIFEST = env["MANIFEST"]
assert TILES, "TILES bos — path resolver'i once koş"

tile_paths = sorted(glob.glob(f"{TILES}/*.tif"))
print(f"Tile sayisi: {len(tile_paths)}")
assert len(tile_paths) > 0

# Welford online mean/std (memory-safe, 30 tile * 17ch * 256*256 = 32M sample)
n_total = 0
mean = None
M2 = None
nodata = -9999.0  # P1 manifest'inden

for i, tp in enumerate(tile_paths):
    with rasterio.open(tp) as src:
        arr = src.read().astype(np.float64)  # (C, H, W)
    C = arr.shape[0]
    if mean is None:
        mean = np.zeros(C); M2 = np.zeros(C)

    # Per-channel valid (nodata exclude)
    for c in range(C):
        ch = arr[c]
        valid = ch[(ch != nodata) & np.isfinite(ch)]
        if valid.size == 0:
            continue
        # Welford incremental update
        n_old = n_total if c == 0 else 0  # her bant icin ayri ama toplam tek sayar
        # Aslinda her bantta ayri akumulator gerek; basitlestir: tek tile her bant ayri.
        ch_mean = valid.mean()
        ch_var = valid.var()
        ch_n = valid.size
        # Combine with running stats (per channel)
        if i == 0:
            mean[c] = ch_mean
            M2[c] = ch_var * ch_n
        else:
            delta = ch_mean - mean[c]
            new_n = n_total + ch_n  # n_total burada onceki cumulative
            mean[c] = mean[c] + delta * ch_n / new_n
            M2[c] = M2[c] + ch_var * ch_n + delta**2 * n_total * ch_n / new_n
    if i == 0:
        n_total = arr[0][(arr[0] != nodata) & np.isfinite(arr[0])].size
    else:
        n_total += arr[0][(arr[0] != nodata) & np.isfinite(arr[0])].size

std = np.sqrt(M2 / max(n_total, 1))
print(f"\nAmpirik mean per kanal:")
band_names = [
    "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
    "VV_dB", "VH_dB", "DEM", "slope", "NDVI", "BSI", "Albedo",
]
for c in range(len(mean)):
    name = band_names[c] if c < len(band_names) else f"ch{c}"
    print(f"  [{c:2d}] {name:8s} mean={mean[c]:12.4f}  std={std[c]:12.4f}")

# Manifest'e mean/std yaz (P1'in dosyasini override etmeyelim; copy uretip
# yeni manifest_p3.json olarak kaydet, --manifest-json bayragi buna isaret eder)
manifest = json.load(open(MANIFEST))
manifest["normalization"] = {
    "mean": mean.tolist(),
    "std": std.tolist(),
    "nodata": nodata,
    "computed_by": "P3 ampirik hesap, T3.5 oncesi",
    "n_tiles_used": len(tile_paths),
    "n_pixels": int(n_total),
}
out_manifest = Path(MANIFEST).parent / "manifest_p3.json"
with open(out_manifest, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"\nP3 manifest yazildi: {out_manifest}")

# Env'i guncelle
import subprocess
subprocess.run(["sed", "-i", f's|^export MANIFEST=.*|export MANIFEST="{out_manifest}"|',
                state_path], check=True)
print(f"/tmp/p3_state/paths.sh MANIFEST guncellendi -> {out_manifest}")
print("\nOK — ampirik istatistik manifest_p3.json'a yazildi, T3.5 EGITIM HUCRESI artik bunu kullanacak.")
```

**Sanity threshold:**
- S2 bantlari mean/std beklentisi:
  - 0-1 olcekteyse: mean ~ 0.05-0.20, std ~ 0.03-0.10
  - 0-10000 olcekteyse: mean ~ 500-2000, std ~ 300-1000
- S1 dB: mean -10 ila -25, std 3-7
- DEM: mean ~1000-1700 m (Avanos), std 200-500
- slope: mean 5-15 deg, std 5-15
- NDVI: mean -0.1 ila 0.4, std 0.2-0.4
- BSI: mean -0.2 ila 0.2, std 0.1-0.3
- Albedo: mean 0.10-0.25, std 0.05-0.15

**Hata varsa:**
- S2 mean ~ 0.10 ama beklenen 1000 -> P1 0-1 olcek kullaniyor, DEFAULT_MEAN/STD tahminim dogru.
- S2 mean ~ 1000 -> P1 0-10000 olcek, DEFAULT'lar hatali (10000x off), normalize bozulur.
- Hicbir bant icin valid pixel yok -> nodata mask'i tum tile'i kapliyor, tile crop bozuk.

---

## EGITIM HUCRESI (gercek run, ~1-2h H100)

Path resolver hucresinden gelen env'i source ederek koş:

```bash
%%bash
source /tmp/p3_state/paths.sh
cd /content/Pomzadoya
PROJ=/content/drive/MyDrive/pomzadoya

# Opsiyonel W&B (atla = default):
# from google.colab import userdata; import os
# os.environ["WANDB_API_KEY"] = userdata.get("WANDB_API_KEY")  # Colab Secret'a once ekle

# MANIFEST opsiyonel — yoksa --manifest-json bayragi atlanir, DEFAULT_MEAN/STD kullanilir.
MANIFEST_FLAG=""
[ -n "$MANIFEST" ] && MANIFEST_FLAG="--manifest-json $MANIFEST"

python code/p3/06_train.py \
    --tile-dir       "$TILES" \
    --full-mask      "$MASK" \
    --split-json     "$SPLIT" \
    $MANIFEST_FLAG \
    --ssl4eo-ckpt    "$CKPT" \
    --output-dir     $PROJ/models \
    --reports-dir    $PROJ/reports \
    --in-channels 17 \
    --epochs 30 \
    --batch-size 8 \
    --lr 1e-4 \
    --weight-decay 1e-4 \
    --num-workers 2 \
    --folds 5 \
    --bce-weight 0.5 \
    --amp \
    --seed 42 \
    2>&1 | tee $PROJ/reports/t3_5_train.log
```

**NOT:** Yukaridaki hucre `/tmp/p3_state/paths.sh` env dosyasini source eder.
Path resolver hucresini once kosturmazsan TILES/MASK/SPLIT/CKPT degiskenleri
bos olur ve `06_train.py` "tile_dir not found" gibi hata verir.

**Bayrak gerekceleri:**
- `--epochs 30` -> Brifing standardi, H100'de gercekci dataset icin <2h.
- `--batch-size 8` -> Sentetik H100'de b=4 peak 0.89 GB; b=8 ile ~2 GB, rahat. T4'te b=4 dusur.
- `--lr 1e-4` -> AdamW + CosineLR (06_train.py icinde) standart.
- `--num-workers 2` -> Colab'da 4'ten fazla `Too many open files` riski; 2 dengeli.
- `--amp` -> AMP fp16, hiz x1.5-2 (Karar #13 export profili).
- `--seed 42` -> Tekrarlanabilirlik (P4/P5 ile karsilastirilabilir).
- W&B opsiyonel — env'de yoksa script otomatik atliyor, hata vermez.

---

## ASYNC PROTOKOL (egitim koşarken paralel iş — saat 12-15)

### Arka plan: Egitim ilerleme monitor (yan hucre)

```python
# Ayri hucrede koş, egitimle paralel ilerler.
import time, json, subprocess
from pathlib import Path

log = Path("/content/drive/MyDrive/pomzadoya/reports/t3_5_train.log")
last_size = 0
print("Egitim monitor basladi. Her 30 sn'de log uzunlugunu rapor eder.")
print("Hucreyi durdurmak icin: Ctrl+M, I (interrupt).")
while True:
    if log.exists():
        s = log.stat().st_size
        if s != last_size:
            tail = subprocess.check_output(["tail", "-3", str(log)]).decode()
            print(f"\n[{time.strftime('%H:%M:%S')}] log {s} bytes:\n{tail}")
            last_size = s
    time.sleep(30)
```

### Ön plan: paralel iş (T3.5 koşarken yap)

1. **İş 9** — `reports/p3_architecture.md` yaz (CPU-only, GPU bos kalmaz).
2. **İş 8** — FP16 export kuru test (T3.5 fold0 ckpt'i biter bitmez baslat, ayri hucre).

### Plan B tetiklemesi (T3.5 yarisinda, fold0+1 sonu)

Eger fold0 ve fold1 val IoU < 0.30 ise (toplam ~30 dk H100):
- Egitimi durdur (Ctrl+M, I).
- Plan B-1 dene: `--rgb-only` (S2 RGB sade baseline).
- Yine olmazsa Plan B-2: `python code/p3/12_fallback_threshold.py` (Sabins+BSI manuel threshold, model-free).

---

## VERIFY-BLOCK [T3.5] (saat ~14-15)

```python
# Egitim bittikten sonra ayri hucrede koş.
import json
from pathlib import Path

models_dir = Path("/content/drive/MyDrive/pomzadoya/models")
reports_dir = Path("/content/drive/MyDrive/pomzadoya/reports")

print("=== Checkpoint dosyalari ===")
for k in range(5):
    p = models_dir / f"unet_pomza_ssl4eo_fold{k}.pt"
    if p.exists():
        sz = p.stat().st_size / 1e6
        print(f"  fold{k}: {sz:6.1f} MB")
    else:
        print(f"  fold{k}: YOK")

print("\n=== 5-fold metrikleri ===")
metrics_path = reports_dir / "metrics_5fold.json"
if metrics_path.exists():
    m = json.load(open(metrics_path))
    print(json.dumps(m, indent=2))
    if "fold_results" in m:
        ious = [r["best_iou"] for r in m["fold_results"]]
        import statistics
        mean_iou = statistics.mean(ious)
        std_iou  = statistics.stdev(ious) if len(ious) > 1 else 0.0
        print(f"\nMean val IoU: {mean_iou:.4f}")
        print(f"Std  val IoU: {std_iou:.4f}")
        print(f"Sanity threshold: mean > 0.45 (brifing), std < 0.08 (consistency)")
        print(f"  -> mean OK?  {mean_iou > 0.45}")
        print(f"  -> std  OK?  {std_iou < 0.08}")
else:
    print(f"  YOK: {metrics_path}")
```

**Sanity threshold:**
- 5 ckpt dosyasi (fold0..fold4), her biri ~130 MB.
- `metrics_5fold.json` mevcut, fold_results array'inde 5 satir.
- **Mean val IoU > 0.45** (brifing hedefi).
- **Std val IoU < 0.08** (fold tutarliligi).

**Sonuc senaryolari:**
- ✅ Mean > 0.45, std < 0.08 -> T3.6 threshold tuning + T3.10 RAW inference'e gec.
- ⚠️ Mean 0.30-0.45 -> Plan B-1 (`--rgb-only`) bir fold'da test, beraberinde devam.
- 🛑 Mean < 0.30 -> Plan B-2 (Sabins+BSI fallback), grup chat'e HELP.

---

## DELIVER (sen yapistirinca ben yazacagim)

```
[P3] T3.5 SSL4EO-S12 5-fold fine-tune TAMAM (2026-05-02, Colab Pro H100)

Cikti:
  - models/unet_pomza_ssl4eo_fold{0..4}.pt (5 dosya, ~130 MB her biri)
  - reports/metrics_5fold.json
  - reports/t3_5_train.log

Metric:
  - Mean val IoU = <X.XXX>
  - Std  val IoU = <X.XXX>
  - Best threshold (her fold) = ...
  - Egitim suresi: <Y> dk H100

Bagimli (devam):
  - T3.6 F1-max threshold tuning (15-16)
  - T3.7 Ablation 5 konfig (15-16.5)
  - T3.10 RAW inference fn (16.5-17.5) — P4 + P5 CRITICAL
  - T3.11 Grad-CAM (17.5-18.5)
```

---

## NOTLAR

- **best_iou tracking:** `06_train.py:218-228` her epoch sonu val sweep yapar, eger `sweep["best_iou"] > best_iou` ise checkpoint'i kaydeder. Yani plateau'dan sonra bos epoch'lar GPU saatini yer ama **best ckpt korunur**.
- **Early stop YOK** -> 30 epoch hepsi koşar. H100'de bu sorun degil (toplam <2h). T4'te 6h alabilir.
- **start-fold:** Fold ortasinda crash olursa `--start-fold <k>` ile devam et, onceki fold'lar tekrar koşmaz.
- **VRAM yetmezse:** `--batch-size 4 --num-workers 1` veya `--amp` zorunlu.
- **W&B:** Real-time dashboard icin saat ~11'de Colab Secret'a `WANDB_API_KEY` ekle, hucre ustune `os.environ["WANDB_API_KEY"] = userdata.get("WANDB_API_KEY")` koy, `--wandb` bayragini ac.
