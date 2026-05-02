# Raw2Value AI ML Pipeline

Kapadokya Hackathon 2026 — Team Feza. Türkiye'nin pomza, perlit ve kabak çekirdeği hammaddelerini en yüksek katma değerli ürüne dönüştürecek route + buyer + lojistik tavsiyesi üreten ML sistemi.

Hedef: Hammadde + lokasyon + miktar girdisinden, 15 işleme rotası arasından net kâr / CO2 / risk dengesi en iyi olan rotayı seçip, alıcı şehir ve taşıma modu önerisini gerekçeli şekilde döndürmek.

## Deliverables
- `raw2value_ml/` — eğitilmiş model ve inference paketi (FastAPI ile entegre).
- `models/` — eğitilmiş artefaktlar (`.parquet` model objeleri, `metadata.json`, `model_evidence.json`).
- `data/reference/` — Master Excel'den üretilmiş referans parquet tabloları.
- `ml/notebooks/` — uçtan uca eğitim ve değerlendirme defterleri.
