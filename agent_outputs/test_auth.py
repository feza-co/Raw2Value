import os
import sys
from pathlib import Path

import requests


# 1) .netrc dosyasi var mi?
netrc_path = Path.home() / ".netrc"
if not netrc_path.exists():
    sys.exit(f"[FAIL] .netrc bulunamadi: {netrc_path}")

content = netrc_path.read_text()
if "urs.earthdata.nasa.gov" not in content:
    sys.exit("[FAIL] .netrc icinde urs.earthdata.nasa.gov kaydi yok")
print(f"[OK]   .netrc bulundu: {netrc_path}")

# 2) .netrc izinleri (Linux/Colab'da zorunlu)
if sys.platform != "win32":
    mode = oct(os.stat(netrc_path).st_mode & 0o777)
    if mode != "0o600":
        print(f"[WARN] .netrc mode {mode} - 600 olmali. Duzelt: chmod 600 ~/.netrc")
    else:
        print(f"[OK]   .netrc mode {mode}")

# 3) CMR ping (anonim - auth gerektirmez)
r = requests.get(
    "https://cmr.earthdata.nasa.gov/search/collections.json",
    params={"short_name": "AST_L1T"},
    timeout=15,
)
print(f"[{'OK' if r.status_code == 200 else 'FAIL'}]   CMR ping: HTTP {r.status_code}")
if r.status_code == 200:
    hits = r.json().get("feed", {}).get("entry", [])
    print(f"       AST_L1T koleksiyon sayisi: {len(hits)}")

# 4) Earthdata profile (kimlik dogrulama testi)
try:
    import netrc as netrc_mod

    auth = netrc_mod.netrc().authenticators("urs.earthdata.nasa.gov")
    if auth is None:
        print("[FAIL] netrc.authenticators() None dondu - kayit eksik")
    else:
        user, _, _ = auth
        print(f"[OK]   .netrc kullanici: {user}")
except Exception as e:
    print(f"[FAIL] .netrc parse hatasi: {e}")

# requests.Session ile auth dene
try:
    import netrc as netrc_mod

    auth = netrc_mod.netrc().authenticators("urs.earthdata.nasa.gov")
    if auth is None:
        raise RuntimeError("urs.earthdata.nasa.gov icin .netrc kaydi yok")

    user, _, password = auth
    session = requests.Session()
    session.auth = (user, password)
    resp = session.get(
        "https://urs.earthdata.nasa.gov/profile",
        allow_redirects=True,
        timeout=15,
    )
    ok = resp.status_code == 200 and "Earthdata" in resp.text
    print(f"[{'OK' if ok else 'FAIL'}]   Earthdata profile: HTTP {resp.status_code}")
    if not ok and resp.status_code != 200:
        print(f"       Ilk 200 karakter: {resp.text[:200]}")
except Exception as e:
    print(f"[FAIL] Profile testi: {e}")

print("\n--- OZET ---")
print("Her satir [OK] ise T4.1 TAMAM. [FAIL] varsa bana yapistir.")
