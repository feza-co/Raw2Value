# RUN-BLOCK [T4.3] — ASTER L1B/L1T atmosferik düzeltme (DOS, ~1h)

**Hedef ortam**: Yerel Python + GDAL HDF4 driver
**Önkoşul**: T4.2 tamam (`data/aster/AST_*.hdf`)
**Süre**: ~30-60 dk (sahne başına ~10-20 dk)
**Asenkron**: KISMEN — DOS hızlı (numpy in-memory), ama T4.4 paralel koşturulabilir.

## Adımlar

1. **GDAL HDF4 driver doğrula**:
   ```bash
   gdalinfo --formats | grep -i hdf4
   # beklenen: HDF4 -raster- (rov-): Hierarchical Data Format Release 4
   ```
   Yoksa Conda: `conda install -c conda-forge gdal libgdal-hdf4`

2. **DOS atmosferik düzeltme (birincil)**:
   ```bash
   for HDF in data/aster/AST_L1T_*.hdf; do
     python code/p4/03_aster_l1b_to_l2.py --in "$HDF" --out data/aster/
   done
   ```
   Çıktı her sahne için: `<stem>_l2_swir.tif`, `<stem>_l2_tir.tif`, `<stem>_l2_meta.json`.

3. **Plan B — DOS başarısız** (hata 3 veya saçma değerler):
   ```bash
   python code/p4/03_aster_l1b_to_l2.py --in data/aster/AST_L1T_X.hdf --no-dos --out data/aster/
   ```
   Karar #4 dayanağı: Ninomiya QI = B11²/(B10·B12) **oran-tabanlı** → mutlak kalibrasyon
   gerekmez. Plan B kabul edilebilir.

## VERIFY-BLOCK [T4.3]
Bana yapıştır:
- `gdalinfo data/aster/<stem>_l2_tir.tif | head -25` — CRS, bant sayısı=5, NoData=0
- `cat data/aster/<stem>_l2_meta.json` — DOS offset değerleri (TIR ~ +200..+1000 DN, anormal değil)
- TIR mean değerlerinin ölçek olarak makul olması (negatif değil, > 0)
- Histogram (matplotlib) ekran görüntüsü — bimodal değil, çan eğrisi

Sanity threshold:
- SWIR DOS offset/band: 5..30 (DN scale)
- TIR DOS offset/band: 100..1500 (radiance scale)
- min > 0 zorunlu (sıfır = NoData)

## DELIVER
```
[P4] T4.3 TAMAM (DOS) | TAMAM-PLANB (no-dos)
Çıktı: data/aster/*_l2_swir.tif, *_l2_tir.tif (×N sahne)
Sanity: ✅ NoData=0 propagate, ✅ DOS offset makul, ✅ TIR mean>0
Sıradaki bağımlı: T4.5 Ninomiya QI/CI/SiO₂ hesabı
```
