"""
Adım 1b — CMR'da AST_L1B fallback sorgusu (L1T boş dönerse çalıştır).
Girdi  : sabit parametreler (bbox, tarih, bulut eşiği)
Çıktı  : terminale granül listesi + data/aster/_cmr_l1b.json manifest
"""

import json
import requests
from pathlib import Path

# ── Girdi parametreleri ──────────────────────────────────────────────────────
BBOX        = "34.6,38.5,35.1,39.0"
START       = "2020-01-01T00:00:00Z"
END         = "2024-12-31T23:59:59Z"
MAX_CLOUD   = 20.0
PAGE_SIZE   = 20
SHORT_NAME  = "AST_L1B"
OUT_JSON    = Path("data/aster/_cmr_l1b.json")
# ────────────────────────────────────────────────────────────────────────────

URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

params = {
    "short_name":     SHORT_NAME,
    "bounding_box":   BBOX,
    "temporal":       f"{START},{END}",
    "day_night_flag": "DAY",
    "sort_key":       "+cloud_cover",
    "page_size":      str(PAGE_SIZE),
}

print("=" * 60)
print(f"Sorgu  : {SHORT_NAME}  (fallback)")
print(f"BBox   : {BBOX}")
print(f"Tarih  : {START} → {END}")
print(f"Bulut  : <= {MAX_CLOUD}%")
print("=" * 60)

response = requests.get(URL, params=params, timeout=60)

if response.status_code != 200:
    print(f"[HATA] HTTP {response.status_code}: {response.text[:300]}")
    raise SystemExit(1)

entries = response.json().get("feed", {}).get("entry", [])
print(f"CMR toplam sonuç: {len(entries)}\n")

eligible = []
for entry in entries:
    cc_raw = entry.get("cloud_cover")
    try:
        cc = float(cc_raw) if cc_raw is not None else None
    except ValueError:
        cc = None

    if cc is not None and cc > MAX_CLOUD:
        continue

    hdf_links = [
        lnk["href"]
        for lnk in entry.get("links", [])
        if ".hdf" in lnk.get("href", "")
    ]
    if not hdf_links:
        continue

    eligible.append({
        "title":         entry.get("title"),
        "start_date":    entry.get("time_start"),
        "cloud_cover":   cc,
        "download_urls": hdf_links,
    })

print(f"Filtre sonrası uygun granül: {len(eligible)}")
print("-" * 60)

for i, g in enumerate(eligible, 1):
    print(f"[{i}] {g['title']}")
    print(f"     Tarih     : {g['start_date']}")
    print(f"     Bulut     : {g['cloud_cover']}%")
    for url in g["download_urls"]:
        print(f"     İndirme   : {url}")
    print()

if eligible:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(eligible, indent=2, ensure_ascii=False))
    print(f"[manifest] {OUT_JSON} dosyasına yazıldı.")
    print(f"\nEn iyi aday : [{eligible[0]['title']}]  (bulut={eligible[0]['cloud_cover']}%)")
else:
    print("[HATA] L1B de boş döndü. Tarih aralığını veya bulut eşiğini genişletin.")
