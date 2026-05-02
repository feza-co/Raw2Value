"""
Adım 2 — Manifest'teki en iyi granülü indir (.netrc auth).
Girdi  : data/aster/_cmr_l1t.json  (veya _cmr_l1b.json)
Çıktı  : data/aster/<dosyaadi>.hdf

.netrc gereksinimi (~/.netrc veya %USERPROFILE%\\_netrc):
    machine urs.earthdata.nasa.gov
    login   <EARTHDATA_KULLANICI>
    password <EARTHDATA_SIFRE>
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# ── Girdi parametreleri ──────────────────────────────────────────────────────
MANIFEST_JSON = Path("data/aster/_cmr_l1b.json")   # L1T boş döndü, L1B kullanılıyor
OUT_DIR       = Path("data/aster")
LIMIT         = 1       # kaç granül indirilecek
CHUNK_MB      = 1       # indirme chunk boyutu (MB)
# ────────────────────────────────────────────────────────────────────────────

def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[HATA] Manifest bulunamadı: {path}")
        print("       Önce cmr_query_l1t.py veya cmr_query_l1b.py çalıştırın.")
        raise SystemExit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def get_auth() -> HTTPBasicAuth | None:
    user = os.environ.get("EARTHDATA_USER")
    pwd  = os.environ.get("EARTHDATA_PASS")
    if user and pwd:
        print(f"[auth] env-var ile giriş: {user}")
        return HTTPBasicAuth(user, pwd)
    print("[auth] env-var yok, .netrc kullanılacak")
    return None


def download(url: str, out_dir: Path, auth, chunk_bytes: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fname    = url.split("/")[-1]
    out_path = out_dir / fname

    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"[atla] Zaten mevcut: {fname}  ({out_path.stat().st_size / 1e6:.1f} MB)")
        return out_path

    print(f"[GET ] {url}")
    session = requests.Session()
    t0 = time.time()

    with session.get(url, auth=auth, stream=True, timeout=300,
                     allow_redirects=True) as r:
        if r.status_code != 200:
            print(f"[HATA] HTTP {r.status_code} — {r.url}")
            if r.status_code == 401:
                print("       401: .netrc veya EARTHDATA_USER/PASS kontrol edin.")
            raise SystemExit(1)

        total = int(r.headers.get("Content-Length", 0))
        written = 0
        with open(out_path, "wb") as f:
            for blob in r.iter_content(chunk_size=chunk_bytes):
                if not blob:
                    continue
                f.write(blob)
                written += len(blob)
                if total:
                    pct = written / total * 100
                    print(f"\r[ind ] {fname}  {written/1e6:.1f}/{total/1e6:.1f} MB  ({pct:.0f}%)",
                          end="", flush=True)

    elapsed = time.time() - t0
    size_mb  = out_path.stat().st_size / 1e6
    print(f"\n[bitti] {fname}  {size_mb:.1f} MB  {elapsed:.1f}s")

    if total and abs(out_path.stat().st_size - total) > 1024:
        print(f"[UYARI] Boyut uyuşmazlığı: beklenen={total}, alınan={out_path.stat().st_size}",
              file=sys.stderr)

    return out_path


def main() -> None:
    granules = load_manifest(MANIFEST_JSON)
    auth     = get_auth()
    chunk    = CHUNK_MB * (1 << 20)

    print("=" * 60)
    print(f"Manifest : {MANIFEST_JSON}  ({len(granules)} granül)")
    print(f"İndirilecek: ilk {LIMIT} granül")
    print("=" * 60)

    for g in granules[:LIMIT]:
        print(f"\nGranül : {g['title']}")
        print(f"Tarih  : {g['start_date']}")
        print(f"Bulut  : {g['cloud_cover']}%")
        url = g["download_urls"][0]
        download(url, OUT_DIR, auth, chunk)

    print("\n[tamam] İndirme tamamlandı.")


if __name__ == "__main__":
    main()
