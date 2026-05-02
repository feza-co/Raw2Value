# [P1] T1.1 — Ortam Kurulumu + GEE Auth

## RUN-BLOCK [T1.1]
**Hedef ortam:** Google Colab (https://colab.research.google.com)
**Onkosul:**
- Google hesabi
- GCP projesi acilmis + Earth Engine API enabled
- Service account JSON anahtari indirilmis (GCP > IAM > Service Accounts)

**Adimlar:**
1. Colab'da yeni notebook ac, `code/p1/01_gee_setup.ipynb` dosyasini yukle (File > Upload notebook).
2. Hucre 1: bagimliliklar — `!pip install earthengine-api ...` calistir.
3. Hucre 2: Service account JSON yukle. Hucre tetiklenince file picker acilir.
   - Yukle: `pomzadoya-sa.json` (kendi indirdigin dosya).
   - **PASTE_TOKEN_HERE:** JSON icerigi `client_email` + `project_id` icermeli.
4. Hucre 3: `ee.Initialize(credentials, project=...)` — "GEE init OK" gormelisin.
5. Hucre 4: Drive mount + `data/` alt klasorleri olustur.
6. Hucre 5: sanity — Avanos merkezinde S2 sahnesi ID'si yazilir.

**Beklenen sure:** ~10 dk (auth + drive mount dahil).

## VERIFY-BLOCK [T1.1]
Bana yapistir:
- Hucre 3 ciktisi: `GEE init OK — project: <senin-proje-id>`
- Hucre 5 ciktisi: `S2 sanity — id: COPERNICUS/S2_SR_HARMONIZED/...`
- `bands: ['B1','B2',...,'B12']` listesi
- Drive mount cikti satiri: `Mounted at /content/drive`

**Sanity threshold:**
- ee.Number(42).getInfo() == 42 dondurmeli (auth canli)
- Sanity S2 sahnesi `id` alani `2024-0[6-9]` icermeli (yaz donemi sahne mevcut)

## DELIVER (sen yapistirinca soyleyecegim)
```
[P1] T1.1 TAMAM
Cikti: ee oturumu canli, /content/drive/MyDrive/Pomzadoya/data/ klasorleri hazir
Sanity: GEE init OK, S2 sanity sahne donduruldu
Siradaki: T1.2 AOI cizimi (RUN-BLOCK p1_t1_2_runblock.md)
```
