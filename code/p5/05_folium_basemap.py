"""
P5 — T5.6: Folium harita altyapısı + baselayer (OpenTopoMap, Esri Satellite, OSM).

İskelet harita üretir, sonraki scriptler (09_layer_manifest.py + dashboard.py)
katmanları üzerine ekler.

Çıktı:
  - code/folium_map.html      (standalone export, T5.13 öncesi placeholder)
"""

from __future__ import annotations

from pathlib import Path

import folium
from folium.plugins import MeasureControl, MiniMap

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_HTML = PROJECT_ROOT / "code" / "folium_map.html"

# Avanos AOI merkezi (yaklaşık)
AVANOS_CENTER = (38.7167, 34.8500)
DEFAULT_ZOOM = 12


def build_basemap(center: tuple[float, float] = AVANOS_CENTER, zoom: int = DEFAULT_ZOOM) -> folium.Map:
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        control_scale=True,
        tiles=None,  # baselayer'ları aşağıda manuel ekliyoruz
    )

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
        attr="© OpenStreetMap contributors",
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        name="OpenTopoMap",
        attr="© OpenTopoMap (CC-BY-SA)",
        max_zoom=17,
        show=True,
    ).add_to(m)

    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        name="Esri Satellite",
        attr="Tiles © Esri",
        max_zoom=19,
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="CartoDB positron",
        name="Carto Light",
        attr="© CartoDB",
        show=False,
    ).add_to(m)

    MeasureControl(primary_length_unit="meters").add_to(m)
    MiniMap(toggle_display=True, position="bottomleft").add_to(m)

    return m


def main():
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    m = build_basemap()
    folium.LayerControl(collapsed=False, position="topright").add_to(m)
    m.save(str(OUT_HTML))
    print(f"[T5.6] baselayer harita yazıldı: {OUT_HTML}")


if __name__ == "__main__":
    main()
