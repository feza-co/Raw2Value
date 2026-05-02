#!/usr/bin/env bash
set -euo pipefail

# Raw2Value ML pipeline — sıfırdan train + test + paketleme
# Çalıştırma: bash scripts/run_full_pipeline.sh

cd "$(dirname "$0")/.."

echo "=== [0/8] pip install -e ."
pip install -e . > /tmp/r2v_install.log 2>&1 || { cat /tmp/r2v_install.log; exit 1; }

echo "=== [1/8] ETL Excel -> parquet"
python -m ml.src.etl --xlsx data/master/raw2value_v4.xlsx --out data/reference/

echo "=== [2/8] Augmentation: training_set_v1"
python -c "from ml.src.augmentation import build_training_set; df = build_training_set(); df.to_parquet('data/processed/training_set_v1.parquet')"

echo "=== [3/8] Feature pipeline fit"
python -c "
import pandas as pd
from ml.src.feature_pipeline import fit_and_save
df = pd.read_parquet('data/processed/training_set_v1.parquet')
fit_and_save(df, kind='xgboost', out_path='models/feature_pipeline.pkl')
"

echo "=== [4/8] Baselines"
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/03_baselines.ipynb || python -m nbclient ml/notebooks/03_baselines.ipynb

echo "=== [5/8] GBM benchmark"
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/04_gbm_benchmark.ipynb || python -m nbclient ml/notebooks/04_gbm_benchmark.ipynb

echo "=== [6/8] Ablation"
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/05_ablation.ipynb || python -m nbclient ml/notebooks/05_ablation.ipynb

echo "=== [7/8] Export evidence + metadata"
python -m ml.src.evidence

echo "=== [8/8] Tests"
python -m pytest ml/tests/ -v

echo ""
echo "Pipeline complete. Backend hazir."
