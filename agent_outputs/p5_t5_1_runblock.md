# RUN-BLOCK [T5.1] — Ortam kurulumu

**Hedef ortam:** yerel Python 3.10/3.11 (conda önerilir, Windows için).
**Önkoşul:** Yok (P5 kendi env'i).
**Beklenen süre:** 1 saat (rasterio/GDAL Windows kurulumu en uzun adım).

## Adımlar

```bash
# Conda yolu (önerilen)
conda create -n pomzadoya-p5 python=3.10 -y
conda activate pomzadoya-p5
conda install -c conda-forge rasterio geopandas shapely fiona pyproj gdal -y
pip install -r code/p5/requirements.txt

# Pip-only fallback
python -m venv .venv-p5
.venv-p5\Scripts\activate
pip install --upgrade pip
pip install -r code/p5/requirements.txt
```

## Doğrulama

```python
import folium, leafmap, shapely, imageio, rasterio, streamlit, geopandas, requests, branca, numpy, pandas
print("p5 stack OK")
```

# VERIFY-BLOCK [T5.1]

Bana yapıştır:
- `pip list | findstr /i "folium leafmap shapely imageio rasterio streamlit geopandas branca"`
- `python -c "import folium, rasterio, geopandas; print('ok')"` çıktısı
- `streamlit hello` ekran görüntüsü (port 8501 çalışıyor mu)

Sanity threshold: 13 paket de listede, ImportError yok.

# DELIVER

```
[P5] T5.1 TAMAM
Çıktı: code/p5/01_env_setup.md, code/p5/requirements.txt
Sanity: ✅ folium 0.15+, rasterio 1.3+, streamlit 1.30+, geopandas 0.14+
Sıradaki: T5.2 WDPA Göreme buffer + OSM cross-check
```
