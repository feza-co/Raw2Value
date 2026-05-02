# RUN-BLOCK [T4.2] — ASTER L1B/L1T sahne indirme (ASENKRON ~30 dk)

**Hedef ortam**: Colab / Yerel
**Önkoşul**: T4.1 tamam (`.netrc`, `.urs_cookies`), `pip install -r code/p4/requirements.txt`
**Süre**: ~30 dk (CMR sorgu ~10 sn + 1-3 sahne × ~10 dk indirme)
**Asenkron**: EVET. İndirme arkaplanda; bu sırada T4.5 Ninomiya formül script'i hazır,
T4.4 S2 indeks script'i P1 ARD'sini bekliyor — paralel iş üret.

## Adımlar

1. **AOI seç** (Avanos default bbox):
   ```
   west=34.70  south=38.65  east=34.95  north=38.78
   ```

2. **CMR dry-run** (önce listele, indirme yapma):
   ```bash
   python code/p4/02_aster_l1b_download.py \
       --aoi 34.70,38.65,34.95,38.78 \
       --start 2024-04-01 --end 2024-09-30 \
       --max-cloud 20 \
       --out data/aster/ \
       --limit 3 --dry-run
   ```
   Çıktı: `data/aster/_cmr_search.json`. 0 sonuç dönerse:
   - `--max-cloud` 40'a çıkar
   - tarih aralığını `2023-04-01..2024-10-31` yap
   - hâlâ 0 → `--fallback-url <e4ftl01_url>` ile manuel URL geç

3. **Gerçek indirme** (ASENKRON başlat):
   ```bash
   nohup python code/p4/02_aster_l1b_download.py \
       --aoi 34.70,38.65,34.95,38.78 \
       --start 2024-04-01 --end 2024-09-30 \
       --max-cloud 20 \
       --out data/aster/ --limit 3 \
       > data/aster/_download.log 2>&1 &
   echo $! > data/aster/_download.pid
   ```
   Windows PowerShell:
   ```powershell
   Start-Job -ScriptBlock {
     python C:\Users\tuna9\OneDrive\Masaüstü\Pomzadoya\code\p4\02_aster_l1b_download.py `
       --aoi 34.70,38.65,34.95,38.78 --start 2024-04-01 --end 2024-09-30 `
       --max-cloud 20 --out data\aster --limit 3
   } -Name aster_dl
   ```

4. **Paralel iş** (indirme sürerken):
   - `python code/p4/05_ninomiya_qi.py --help` smoke test
   - P1'den S2 ARD geldi mi: `ls data/s2/*ard*.tif`
   - geldi ise → `python code/p4/04_s2_indices.py --ard <ARD>`

## VERIFY-BLOCK [T4.2]
Bana yapıştır:
- `ls -la data/aster/*.hdf` (1+ sahne, > 100 MB her biri)
- `cat data/aster/_cmr_search.json | python -m json.tool` (granule_ur, cloud_cover, time_start)
- `gdalinfo data/aster/AST_L1T_*.hdf | head -50` — subdataset listesi
- `tail -20 data/aster/_download.log` — error yok

## Plan B (CMR boş veya indirme fail)
- Earthdata Search UI: https://search.earthdata.nasa.gov → AST_L1T → AOI çiz → manuel URL al
- `python code/p4/02_aster_l1b_download.py --fallback-url <URL> --out data/aster/`

## DELIVER
```
[P4] T4.2 TAMAM
Çıktı: data/aster/AST_L1T_*.hdf (×N), _cmr_search.json
Sanity: ✅ N≥1 sahne, ✅ size>100MB, ✅ gdalinfo subdataset listesi tam (B1..B14)
Sıradaki bağımlı: T4.3 atmosferik düzeltme
```
