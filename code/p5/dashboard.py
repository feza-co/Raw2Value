"""
P5 — T5.12: Streamlit dashboard (Pomzadoya hackathon, Modül A v2).

3 sayfa:
  1. Saha Tarama       — Folium harita + 5 katman toggle
  2. AI Analizi        — RAW probability vs FUSED final_confidence overlay
  3. Operasyonel Karar — KPI tablosu, UNESCO red flag listesi, Landsat timelapse

Çalıştırma:
    streamlit run code/p5/dashboard.py
"""

from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit.components.v1 import html as st_html

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAYERS_JSON = PROJECT_ROOT / "data" / "layers.json"
KPI_JSON = PROJECT_ROOT / "reports" / "kpi.json"
RED_FLAGS_JSON = PROJECT_ROOT / "reports" / "red_flags.json"
GIF_PATH = PROJECT_ROOT / "data" / "temporal" / "landsat_timelapse.gif"
HISTORICAL_SUMMARY = PROJECT_ROOT / "reports" / "historical_pomza_summary.json"
RULES_HELPER = PROJECT_ROOT / "code" / "p5" / "11_cave2cloud_rules.py"

AVANOS_CENTER = (38.7167, 34.85)


def _load_json(p: Path, default=None):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def _load_rules_helper():
    spec = importlib.util.spec_from_file_location("cave2cloud_rules", RULES_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Rules helper yuklenemedi: {RULES_HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _make_basemap() -> folium.Map:
    m = folium.Map(location=AVANOS_CENTER, zoom_start=12, tiles=None, control_scale=True)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=False).add_to(m)
    folium.TileLayer(
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        name="OpenTopoMap",
        attr="© OpenTopoMap",
        show=True,
    ).add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Esri Satellite",
        attr="Esri",
        show=False,
    ).add_to(m)
    Fullscreen().add_to(m)
    return m


def _add_manifest_layers(m: folium.Map, manifest: dict):
    """Manifest'teki katmanları haritaya ekle (placeholder marker / GeoJSON)."""
    for layer in manifest.get("layers", []):
        path = PROJECT_ROOT / layer["path"]
        if not path.exists():
            folium.Marker(
                AVANOS_CENTER,
                popup=f"{layer['name']} — dosya yok ({layer['path']})",
                icon=folium.Icon(color="gray"),
            ).add_to(folium.FeatureGroup(name=f"[!] {layer['name']}", show=False).add_to(m))
            continue

        if layer["type"].startswith("vector"):
            try:
                import geopandas as gpd
                gdf = gpd.read_file(path).to_crs(4326)
                style = layer.get("style", {})
                folium.GeoJson(
                    gdf.__geo_interface__,
                    name=layer["name"],
                    style_function=lambda _f, s=style: {
                        "color": s.get("color", "#3388ff"),
                        "weight": s.get("weight", 2),
                        "fillOpacity": 0.0 if s.get("fill") is False else 0.3,
                        "dashArray": s.get("dash"),
                    },
                    show=layer.get("default_visible", False),
                ).add_to(m)
            except Exception as exc:
                st.warning(f"{layer['name']} okunamadı: {exc}")
        else:
            # Raster: Folium native değil → leafmap/ImageOverlay tercih edilir.
            # Burada placeholder FeatureGroup ekliyoruz; production'da rio-tiler + TileLayer.
            fg = folium.FeatureGroup(name=layer["name"], show=layer.get("default_visible", False))
            folium.Marker(
                AVANOS_CENTER,
                popup=f"{layer['name']} — {path.name}",
                icon=folium.Icon(color="blue", icon="image", prefix="fa"),
            ).add_to(fg)
            fg.add_to(m)


def page_saha_tarama():
    st.header("1) Saha Tarama")
    st.caption("Folium + 5 katman: S2 RGB, ASTER QI, S1 change, UNESCO buffer, **P4 FUSED final_confidence**.")

    manifest = _load_json(LAYERS_JSON, default={"layers": []})
    if not manifest.get("layers"):
        st.error(f"Manifest yok: {LAYERS_JSON}. `python code/p5/09_layer_manifest.py` çalıştır.")
        return

    plan = manifest.get("plan", "A")
    if plan == "B":
        st.warning("Plan B aktif — P4 FUSED `final_confidence.tif` yok, P3 RAW olasılığı gösteriliyor.")
    else:
        st.success("Plan A aktif — P4 FUSED `final_confidence.tif` ana katman.")

    m = _make_basemap()
    _add_manifest_layers(m, manifest)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    st_html(m.get_root().render(), height=620, scrolling=False)

    with st.expander("Katman manifest'i"):
        st.json(manifest)


def page_ai_analizi():
    st.header("2) AI Analizi")
    st.caption("Historical RAW (T5.10) vs Current FUSED (T5.13) karşılaştırması.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Historical RAW (Landsat 1985→2025)")
        summary = _load_json(HISTORICAL_SUMMARY, default=[])
        if summary:
            df = pd.DataFrame(
                [{"year": e.get("year"), "area_ha": e.get("area_ha"), "n_polygons": e.get("n_polygons")}
                 for e in summary if "area_ha" in e]
            )
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.line_chart(df.set_index("year")["area_ha"], height=240)
        else:
            st.info("Historical inference henüz koşmadı (08_historical_pomza_inference.py).")

    with col2:
        st.subheader("Current FUSED (S2 + ASTER, 2025)")
        final_conf = PROJECT_ROOT / "data" / "ard" / "final_confidence.tif"
        if final_conf.exists():
            st.success(f"FUSED katman var: {final_conf.relative_to(PROJECT_ROOT)}")
            st.metric("threshold", "P3 T3.6 F1-max")
        else:
            st.warning("FUSED katman yok — Plan B (P3 RAW) kullanılıyor.")

    st.divider()
    st.subheader("Landsat timelapse (Roy 2016 harmonized)")
    if GIF_PATH.exists():
        st.image(str(GIF_PATH), caption="1985 → 2025 (Roy 2016 cross-sensor harmonized)")
    else:
        st.info("GIF üretilmedi henüz: 07_landsat_timelapse_gif.py")


def page_operasyonel():
    st.header("3) Operasyonel Karar")
    st.caption("KPI + UNESCO red flag özeti.")

    kpi = _load_json(KPI_JSON, default={})
    if not kpi:
        st.error("KPI yok — 10_kpi_calc.py çalıştır.")
        return

    growth = kpi.get("growth", {})
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Toplam büyüme",
        f"{growth.get('growth_pct_total', 0):.1f} %"
        if growth.get("growth_pct_total") is not None else "—",
        f"{growth.get('first_year', '')}-{growth.get('last_year', '')}",
    )
    c2.metric(
        "CAGR",
        f"{growth.get('cagr_pct', 0):.2f} %"
        if growth.get("cagr_pct") is not None else "—",
    )
    viol = kpi.get("unesco_violations", {}).get("violations_per_year", {})
    total_viol = sum(viol.values()) if viol else 0
    c3.metric("UNESCO ihlal (toplam)", total_viol)

    st.subheader("Yıllık alan (ha)")
    annual = kpi.get("annual_areas", {})
    if annual:
        df = pd.DataFrame(
            [{"year": int(k), **v} for k, v in annual.items()]
        ).sort_values("year")
        st.dataframe(df, use_container_width=True)

    st.subheader("UNESCO red flag listesi")
    flags = _load_json(RED_FLAGS_JSON, default=[])
    if flags:
        df = pd.DataFrame(flags)
        red = df[df["intersects_unesco"] == True] if "intersects_unesco" in df.columns else df
        st.dataframe(red, use_container_width=True)
    else:
        st.info("Red flag raporu yok (03_red_flag_logic.py).")


def page_cave2cloud_uyumu():
    st.header("4) Cave2Cloud Uyumu")
    st.caption("Zorunlu kurallar: OSRM/OSM rota, CO2 hesabı, TCMB EVDS canlı kur.")

    helper = _load_rules_helper()

    st.subheader("Pomza taşıma karbon ve kur hesabı")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        origin_lat = st.number_input("Saha lat", value=38.66883, format="%.6f")
        origin_lon = st.number_input("Saha lon", value=34.763343, format="%.6f")
    with c2:
        dest_lat = st.number_input("Fabrika lat", value=38.7167, format="%.6f")
        dest_lon = st.number_input("Fabrika lon", value=34.85, format="%.6f")
    with c3:
        tonnage = st.number_input("Yük (ton)", min_value=1.0, value=25.0, step=1.0)
        mode_label = st.selectbox("Taşıma modu", ["road", "rail", "sea", "air"], index=0)
    with c4:
        pair = st.selectbox("Kur çifti", ["USD/TRY", "EUR/TRY"], index=0)
        carbon_price = st.number_input("Karbon fiyatı ($/tCO2)", min_value=0.0, value=75.0, step=5.0)

    if st.button("Dinamik hesapla", type="primary"):
        try:
            result = helper.compute_demo_decision(
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
                tonnage,
                mode_label,
                pair,
                carbon_price,
            )
            route = result["route"]
            fx = result["fx"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rota mesafesi", f"{route['distance_km']:.1f} km")
            m2.metric("Süre", f"{route['duration_min']:.0f} dk")
            m3.metric("CO2", f"{result['co2_kg']:.1f} kg")
            if result["carbon_cost_try"] is not None:
                m4.metric("Karbon maliyeti", f"{result['carbon_cost_try']:.0f} TL")
                st.success(f"TCMB EVDS kur ({pair}) kullanıldı. Güncelleme: {fx['updated_at']}")
            else:
                m4.metric("Karbon maliyeti", "EVDS anahtarı yok")
                st.error(
                    "TCMB_EVDS_API_KEY ortam değişkeni yok. Kural 2 için sunum öncesi "
                    "EVDS anahtarı tanımlanmalı; hardcoded kur kullanılmadı."
                )
            st.json(result)
        except Exception as exc:
            st.error(f"Dinamik hesap başarısız: {exc}")

    st.divider()
    st.markdown(
        "- Kural 1: rota mesafesi OSRM/OpenStreetMap ile dinamik hesaplanır ve CO2'ye çevrilir.\n"
        "- Kural 2: kur TCMB EVDS'ten `TCMB_EVDS_API_KEY` ile çekilir; anahtar yoksa kullanıcı uyarılır.\n"
        "- Kural 3: rota mesafesi ve süre, karbon hesabından ayrı bir coğrafi işlev olarak gösterilir."
    )


def main():
    st.set_page_config(page_title="Pomzadoya — Modül A v2", layout="wide", page_icon="⛏️")
    st.sidebar.title("Pomzadoya — Modül A v2")
    st.sidebar.caption("P5 dashboard")
    page = st.sidebar.radio(
        "Sayfa",
        ("1) Saha Tarama", "2) AI Analizi", "3) Operasyonel Karar", "4) Cave2Cloud Uyumu"),
    )
    st.sidebar.divider()
    st.sidebar.write("Akademik referanslar:")
    st.sidebar.markdown(
        "- Mazza 2023 (S1 amplitude diff)\n"
        "- Roy 2016 (Landsat cross-sensor)\n"
        "- Ninomiya 2002 (ASTER QI, K#4)\n"
        "- Liang 2001 (albedo, K#13)\n"
        "- Roberts 2017 (spatial CV, K#10)"
    )

    if page.startswith("1"):
        page_saha_tarama()
    elif page.startswith("2"):
        page_ai_analizi()
    elif page.startswith("3"):
        page_operasyonel()
    else:
        page_cave2cloud_uyumu()


if __name__ == "__main__":
    main()
