# P5 — T5.1 Environment Setup

Pomzadoya hackathon, Modül A v2. P5 (Change Detection + UNESCO + Visualization) için
yerel kurulum talimatı. Hedef: Streamlit + Folium + S1 amplitude difference + Roy 2016
Landsat harmonizasyon + UNESCO buffer overlay.

## 1. Python sürümü
- Python 3.10 veya 3.11 (geopandas/rasterio Windows tekerleklerinin sağlam olduğu sürümler).
- Conda *önerilir* (rasterio + GDAL bağımlılığı pip + Windows kombinasyonunda zorlu).

## 2. Conda ile (önerilen yol)
```bash
conda create -n pomzadoya-p5 python=3.10 -y
conda activate pomzadoya-p5
conda install -c conda-forge rasterio geopandas shapely fiona pyproj gdal -y
pip install -r code/p5/requirements.txt
```

## 3. Pip-only fallback (hızlı, riskli)
```bash
python -m venv .venv-p5
.venv-p5\Scripts\activate    # Windows PowerShell
pip install --upgrade pip
pip install -r code/p5/requirements.txt
```
Eğer `pip install rasterio` Windows'ta hata verirse:
1. https://www.lfd.uci.edu/~gohlke/pythonlibs/ adresinden `GDAL`, `rasterio`, `Fiona`,
   `Shapely`, `pyproj` whl dosyalarını çek.
2. Sırasıyla `pip install <whl>` ile yükle.
3. `pip install geopandas`.

## 4. Doğrulama
```python
import folium, leafmap, shapely, imageio, rasterio, streamlit, geopandas, requests, branca, numpy, pandas
print("p5 stack OK")
```

## 5. Streamlit ilk koşum
```bash
streamlit run code/p5/dashboard.py
# Tarayıcı: http://localhost:8501
```

## 6. Notlar
- Folium HTML standalone export için ek paket gerekmez (`m.save("folium_map.html")`).
- imageio GIF için `pip install imageio[ffmpeg]` gerekirse devreye girer (yalnız MP4 için).
- WDPA shapefile boyutu büyük (~2 GB). Sadece Türkiye subset'i `data/aoi/wdpa_tr.gpkg`
  altında saklanmalı.
- OSM Overpass cross-check için sadece `requests` yeter; ayrı paket yok.
