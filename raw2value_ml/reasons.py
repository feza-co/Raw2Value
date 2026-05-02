"""Türkçe template-tabanlı reason codes — model çıktısının yanına 3 cümlelik gerekçe.

Top-K feature importance üzerinden, eğitim setinin medyanına göre "high/low" şablon
seçilerek Türkçe cümleler üretilir. UI tarafında kullanıcıya açıklama olarak gösterilir.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REASON_TEMPLATES: dict[str, dict[str, str]] = {
    "total_distance_km": {
        "high": "{total_distance_km:.0f} km mesafe lojistik maliyeti yükseltiyor.",
        "low":  "{total_distance_km:.0f} km kısa mesafe maliyet avantajı sağlıyor.",
    },
    "usd_try": {
        "high": "USD/TRY {usd_try:.2f} ihracat gelirini güçlendiriyor.",
        "low":  "USD/TRY {usd_try:.2f} ihracat gelirini sınırlıyor.",
    },
    "eur_try": {
        "high": "EUR/TRY {eur_try:.2f} AB pazarına satışı destekliyor.",
        "low":  "EUR/TRY {eur_try:.2f} AB pazarına satışı zayıflatıyor.",
    },
    "co2_kg": {
        "high": "{co2_kg:.0f} kg CO₂ karbon ayak izini büyütüyor.",
        "low":  "{co2_kg:.0f} kg CO₂ ile düşük karbon avantajı var.",
    },
    "demand_score": {
        "high": "Hedef pazardaki talep skoru {demand_score:.2f} — pazar uygun.",
        "low":  "Hedef pazar talep skoru {demand_score:.2f} — alternatif pazar düşünülebilir.",
    },
    "quality_match_score": {
        "high": "Kalite uyumu yüksek ({quality_match_score:.2f}) — alıcı talebine uygun.",
        "low":  "Kalite uyumu düşük ({quality_match_score:.2f}) — fiyat penalty olası.",
    },
    "tonnage": {
        "high": "{tonnage:.0f} ton büyük tonaj birim maliyeti düşürüyor.",
        "low":  "{tonnage:.0f} ton küçük tonaj birim maliyeti yükseltiyor.",
    },
    "delivery_risk": {
        "high": "Teslim risk skoru {delivery_risk:.2f} yüksek — alternatif transport önerilebilir.",
        "low":  "Teslim risk skoru {delivery_risk:.2f} düşük — operasyonel istikrar yüksek.",
    },
    "processed_price_typical_usd_ton": {
        "high": "İşlenmiş ürün fiyatı {processed_price_typical_usd_ton:.0f} USD/ton — gelir potansiyeli yüksek.",
        "low":  "İşlenmiş ürün fiyatı {processed_price_typical_usd_ton:.0f} USD/ton — pazar fiyatı sınırlı.",
    },
    "raw_price_typical_usd_ton": {
        "high": "Hammadde fiyatı {raw_price_typical_usd_ton:.0f} USD/ton — girdi maliyeti yüksek.",
        "low":  "Hammadde fiyatı {raw_price_typical_usd_ton:.0f} USD/ton — girdi maliyeti elverişli.",
    },
    "processing_cost_typical_usd_ton": {
        "high": "İşleme maliyeti {processing_cost_typical_usd_ton:.0f} USD/ton — operasyonel yük yüksek.",
        "low":  "İşleme maliyeti {processing_cost_typical_usd_ton:.0f} USD/ton — verimli operasyon.",
    },
    "lead_time_days": {
        "high": "{lead_time_days:.0f} gün teslim süresi — hızlı teslimat avantajı yok.",
        "low":  "{lead_time_days:.0f} gün teslim süresi — hızlı teslimat sağlanıyor.",
    },
    "data_confidence_score": {
        "high": "Veri güven skoru {data_confidence_score:.0f}/100 — sağlam temel.",
        "low":  "Veri güven skoru {data_confidence_score:.0f}/100 — bazı varsayımlar kullanıldı.",
    },
    "price_volatility_risk": {
        "high": "Fiyat volatilitesi {price_volatility_risk:.2f} — gelir öngörüsü riskli.",
        "low":  "Fiyat volatilitesi {price_volatility_risk:.2f} — gelir öngörüsü stabil.",
    },
    "fx_scenario_pct": {
        "high": "Kur senaryosu +{fx_scenario_pct:.0%} — pozitif kur etkisi.",
        "low":  "Kur senaryosu {fx_scenario_pct:.0%} — kur baskısı altında.",
    },
}


@lru_cache(maxsize=1)
def _load_medians() -> dict[str, float]:
    """feature_medians.json'ı bir kez yükler ve cache'ler."""
    p = Path(__file__).parent.parent / "data" / "processed" / "feature_medians.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _safe_format(template: str, fname: str, value: Any, features: dict[str, Any]) -> str:
    """Template'i features ile format eder; eksik anahtarda fname'i value ile değiştirir."""
    try:
        return template.format(**features)
    except (KeyError, ValueError, IndexError):
        # Fallback: sadece fname placeholder'ını value ile doldur
        try:
            patched = {fname: value}
            # Diğer placeholder'lar boş kalmasın diye basitçe fname'i replace et
            return template.replace("{" + fname, "{0").format(value)
        except Exception:
            return template


def generate_reason_codes(
    features: dict[str, Any],
    model: Any,
    top_k: int = 3,
) -> list[dict]:
    """Top-K feature importance'a göre Türkçe gerekçe üretir.

    Args:
        features: ham feature sözlüğü (numeric + kategorik değerler).
        model: feature_importances_ ve feature_names_(in_) sağlayan sklearn-uyumlu model.
        top_k: kaç gerekçe üretilecek (default 3).

    Returns:
        [{"feature": str, "importance": float, "value": Any, "text": str}, ...]
    """
    medians = _load_medians()

    # CatBoost feature_names_, sklearn feature_names_in_ — ikisini de destekle.
    if hasattr(model, "feature_names_in_") and getattr(model, "feature_names_in_") is not None:
        names = list(model.feature_names_in_)
    elif hasattr(model, "feature_names_") and getattr(model, "feature_names_") is not None:
        names = list(model.feature_names_)
    else:
        names = list(features.keys())

    importances = list(model.feature_importances_)
    importances_dict = dict(zip(names, importances))

    # Önemli feature'ları azalan sıralamayla; sadece template'i olan ve features'ta değeri
    # bulunan adayları al.
    candidates = sorted(
        (
            (name, imp)
            for name, imp in importances_dict.items()
            if name in REASON_TEMPLATES and features.get(name) is not None
        ),
        key=lambda x: -x[1],
    )

    reasons: list[dict] = []
    used: set[str] = set()
    for fname, imp in candidates:
        if len(reasons) >= top_k:
            break
        value = features.get(fname)
        if value is None:
            continue
        median = medians.get(fname)
        try:
            is_high = float(value) > float(median) if median is not None else True
        except (TypeError, ValueError):
            is_high = True

        template = REASON_TEMPLATES[fname]["high" if is_high else "low"]
        text = _safe_format(template, fname, value, features)

        reasons.append({
            "feature": fname,
            "importance": float(imp),
            "value": value,
            "text": text,
        })
        used.add(fname)

    # Daha az aday varsa (örn. minimal feature dict), template havuzundan eksiği tamamla.
    if len(reasons) < top_k:
        for fname, t in REASON_TEMPLATES.items():
            if len(reasons) >= top_k:
                break
            if fname in used:
                continue
            value = features.get(fname)
            if value is None:
                continue
            median = medians.get(fname)
            try:
                is_high = float(value) > float(median) if median is not None else True
            except (TypeError, ValueError):
                is_high = True
            template = t["high" if is_high else "low"]
            text = _safe_format(template, fname, value, features)
            reasons.append({
                "feature": fname,
                "importance": 0.0,
                "value": value,
                "text": text,
            })
            used.add(fname)

    return reasons[:top_k]
