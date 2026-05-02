"""
T4.2 — ASTER L1B / L1T sahne indirme (Avanos AOI).

Strateji:
  1. CMR (Common Metadata Repository) JSON API ile bbox + tarih aralığında
     `AST_L1T` granül arama (L1T tercih, L1B fallback).
  2. Sahne metadata'sını filtrele: bulut < %20, gündüz, AOI ile kesişen.
  3. `data_links` dizisinden HTTP indirme URL'sini al, `.netrc` ile auth'le.
  4. Output: data/aster/AST_<level>_<date>.hdf  (HDF-EOS2)

Karar referansları:
  - K#3: ASTER L1B (GED ürünü değil) — radiance gerekli, emisivite ürünü kullanılmaz
  - K#4: Ninomiya QI = B11²/(B10·B12) **oran-tabanlı** → mutlak kalibrasyon zorunlu değil
  - K#15: 20 m S2 grid hedef, ASTER 90 m → bilinear resample (sonraki adım)

Kullanım:
    python 02_aster_l1b_download.py \
        --aoi 34.7,38.65,34.95,38.78 \
        --start 2024-04-01 --end 2024-09-30 \
        --max-cloud 20 \
        --out data/aster/

Plan B (CMR boş döner / token hatalı):
  --fallback-url <direct_e4ftl01_url> ile elle URL geçilebilir.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from requests.auth import HTTPBasicAuth

CMR_GRANULE_ENDPOINT = "https://cmr.earthdata.nasa.gov/search/granules.json"
SHORT_NAMES_PRIORITY = ["AST_L1T", "AST_L1B"]  # L1T (geocoded) öncelikli


@dataclass(frozen=True)
class Granule:
    granule_ur: str
    short_name: str
    start_date: str
    cloud_cover: float | None
    download_urls: list[str]


def _bbox_str(bbox: tuple[float, float, float, float]) -> str:
    """CMR `bounding_box` formatı: west,south,east,north."""
    return ",".join(f"{v:.6f}" for v in bbox)


def cmr_search(
    bbox: tuple[float, float, float, float],
    start: str,
    end: str,
    max_cloud: float,
    page_size: int = 50,
) -> list[Granule]:
    """CMR'a sorgu at, granül listesi döndür."""
    granules: list[Granule] = []
    for short_name in SHORT_NAMES_PRIORITY:
        params = {
            "short_name": short_name,
            "bounding_box": _bbox_str(bbox),
            "temporal": f"{start}T00:00:00Z,{end}T23:59:59Z",
            "page_size": page_size,
            "sort_key": "-start_date",
            "day_night_flag": "DAY",
        }
        r = requests.get(CMR_GRANULE_ENDPOINT, params=params, timeout=60)
        r.raise_for_status()
        feed = r.json().get("feed", {})
        entries = feed.get("entry", [])
        for entry in entries:
            cc = entry.get("cloud_cover")
            try:
                cc_f = float(cc) if cc is not None else None
            except ValueError:
                cc_f = None
            if cc_f is not None and cc_f > max_cloud:
                continue
            urls = [
                lnk["href"]
                for lnk in entry.get("links", [])
                if lnk.get("rel", "").endswith("/data#")
                and lnk.get("href", "").endswith(".hdf")
            ]
            if not urls:
                continue
            granules.append(
                Granule(
                    granule_ur=entry.get("title", entry.get("id", "unknown")),
                    short_name=short_name,
                    start_date=entry.get("time_start", "unknown"),
                    cloud_cover=cc_f,
                    download_urls=urls,
                )
            )
        if granules:
            print(f"[cmr] {short_name}: {len(granules)} eligible granule(s)")
            break  # öncelikli short_name'de bulduysak yeter
        print(f"[cmr] {short_name}: 0 result, falling back to next short_name")
    return granules


def _auth_from_env() -> HTTPBasicAuth | None:
    user = os.environ.get("EARTHDATA_USER")
    pwd = os.environ.get("EARTHDATA_PASS")
    if user and pwd:
        return HTTPBasicAuth(user, pwd)
    return None


def download_granule(url: str, out_dir: Path, chunk: int = 1 << 20) -> Path:
    """LP DAAC redirect chain'i yöneten indirici. `.netrc` veya env-var auth.

    Beklenen davranış:
      1. İlk istek 302 → urs.earthdata.nasa.gov
      2. requests `.netrc`'den login okur, cookie alır
      3. Yeniden redirect → e4ftl01.cr.usgs.gov dosya
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = url.split("/")[-1]
    out_path = out_dir / fname
    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"[skip] already downloaded: {out_path.name}")
        return out_path

    auth = _auth_from_env()
    session = requests.Session()
    # LP DAAC için kritik: cookie jar
    cookies_path = Path.home() / ".urs_cookies"
    if cookies_path.exists():
        # `requests` LWPCookieJar gerektirir; .netrc auth varsa zaten yeter.
        pass

    print(f"[get] {fname}")
    t0 = time.time()
    with session.get(url, auth=auth, stream=True, timeout=300, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        written = 0
        with open(out_path, "wb") as f:
            for blob in r.iter_content(chunk_size=chunk):
                if not blob:
                    continue
                f.write(blob)
                written += len(blob)
        elapsed = time.time() - t0
    mb = out_path.stat().st_size / 1e6
    print(f"[done] {out_path.name}: {mb:.1f} MB in {elapsed:.1f}s")
    if total and abs(out_path.stat().st_size - total) > 1024:
        print(
            f"[warn] size mismatch: expected {total}, got {out_path.stat().st_size}",
            file=sys.stderr,
        )
    return out_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument(
        "--aoi",
        default="34.70,38.65,34.95,38.78",
        help="bbox: west,south,east,north (Avanos default)",
    )
    p.add_argument("--start", default="2024-04-01")
    p.add_argument("--end", default="2024-09-30")
    p.add_argument("--max-cloud", type=float, default=20.0)
    p.add_argument("--out", default="data/aster")
    p.add_argument("--limit", type=int, default=3, help="kaç sahne indirilecek")
    p.add_argument("--fallback-url", default=None, help="CMR boş dönerse manuel URL")
    p.add_argument("--dry-run", action="store_true", help="indirme yapma, sadece liste")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    bbox = tuple(float(x) for x in args.aoi.split(","))
    if len(bbox) != 4:
        raise SystemExit("--aoi must be 'west,south,east,north'")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.fallback_url:
        print(f"[fallback] downloading manual URL: {args.fallback_url}")
        download_granule(args.fallback_url, out_dir)
        return 0

    granules = cmr_search(bbox, args.start, args.end, args.max_cloud)
    if not granules:
        print("[err] CMR returned 0 granules. Check AOI/date/cloud filters or use --fallback-url.")
        return 2

    chosen = granules[: args.limit]
    summary_path = out_dir / "_cmr_search.json"
    summary_path.write_text(
        json.dumps(
            [
                {
                    "granule_ur": g.granule_ur,
                    "short_name": g.short_name,
                    "start_date": g.start_date,
                    "cloud_cover": g.cloud_cover,
                    "download_urls": g.download_urls,
                }
                for g in chosen
            ],
            indent=2,
        )
    )
    print(f"[manifest] {summary_path}")

    if args.dry_run:
        for g in chosen:
            print(f"  - {g.granule_ur} ({g.cloud_cover}% cloud) -> {g.download_urls[0]}")
        return 0

    for g in chosen:
        for url in g.download_urls:
            try:
                download_granule(url, out_dir)
            except requests.HTTPError as e:
                print(f"[err] {url}: {e}", file=sys.stderr)
                # devam et, diğer URL'yi dene
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
