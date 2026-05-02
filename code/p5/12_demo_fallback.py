"""
P5 — T5.14: PNG fallback üretici (Streamlit fail saat 20 senaryosu).

Pre-rendered statik HTML + PNG sequence:
  - demo/fallback/01_saha_tarama.png   (Folium harita ekran görüntüsü stand-in)
  - demo/fallback/02_ai_analizi.png
  - demo/fallback/03_operasyonel.png
  - demo/fallback/index.html           (3 sayfayı sırayla gösteren statik dashboard)
  - demo/fallback/landsat_timelapse.gif (T5.7 GIF kopyası)

Kullanıcı laptop wifi kapalı modda `demo/fallback/index.html` açar, demo akar.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "demo" / "fallback"
GIF_SRC = PROJECT_ROOT / "data" / "temporal" / "landsat_timelapse.gif"

PAGES = [
    ("01_saha_tarama.png", "Saha Tarama", "Folium 5 katman", "Avanos AOI + UNESCO buffer"),
    ("02_ai_analizi.png", "AI Analizi", "RAW vs FUSED", "Historical Landsat 1985→2025"),
    ("03_operasyonel.png", "Operasyonel Karar", "KPI + Red flag", "Yıllık büyüme + UNESCO ihlal"),
]


def _placeholder_png(out_path: Path, title: str, subtitle: str, footer: str):
    img = Image.new("RGB", (1280, 720), (245, 245, 250))
    d = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("arial.ttf", 56)
        sub_font = ImageFont.truetype("arial.ttf", 32)
        foot_font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        title_font = sub_font = foot_font = ImageFont.load_default()

    d.rectangle([(0, 0), (1280, 100)], fill=(30, 60, 110))
    d.text((40, 25), "Pomzadoya — Modül A v2", fill="white", font=title_font)
    d.text((40, 200), title, fill=(30, 60, 110), font=title_font)
    d.text((40, 290), subtitle, fill=(80, 80, 80), font=sub_font)
    d.text((40, 660), footer, fill=(120, 120, 120), font=foot_font)

    img.save(out_path)


def _index_html(pages):
    rows = "\n".join(
        f'<section><h2>{p[1]}</h2><img src="{p[0]}" alt="{p[1]}"/><p>{p[2]} — {p[3]}</p></section>'
        for p in pages
    )
    gif_block = (
        '<section><h2>Landsat timelapse</h2><img src="landsat_timelapse.gif" alt="Landsat 1985-2025"/></section>'
        if (OUT / "landsat_timelapse.gif").exists() else ""
    )
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Pomzadoya — Demo Fallback</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f4f4f8;color:#222}}
header{{background:#1e3c6e;color:#fff;padding:24px 32px}}
section{{margin:24px auto;max-width:1280px;background:#fff;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,.08);border-radius:8px}}
img{{width:100%;height:auto;border-radius:4px}}
h2{{margin-top:0;color:#1e3c6e}}
footer{{text-align:center;padding:24px;color:#888}}
</style></head><body>
<header><h1>Pomzadoya — Modül A v2</h1><p>Pre-rendered demo (offline fallback)</p></header>
{rows}
{gif_block}
<footer>Plan B: T5.12 Streamlit fail → T5.14 statik fallback aktif.</footer>
</body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, title, sub, foot in PAGES:
        _placeholder_png(OUT / fn, title, sub, foot)
        print(f"[T5.14] {fn}")
    if GIF_SRC.exists():
        shutil.copy2(GIF_SRC, OUT / "landsat_timelapse.gif")
        print(f"[T5.14] GIF kopyalandı.")
    (OUT / "index.html").write_text(_index_html(PAGES), encoding="utf-8")
    print(f"[T5.14] index -> {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
