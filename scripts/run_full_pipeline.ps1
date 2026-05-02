# Raw2Value ML pipeline (Windows PowerShell)
# Calistirma: pwsh scripts/run_full_pipeline.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path (Join-Path $PSScriptRoot "..")

Write-Host "=== [0/8] pip install -e ." -ForegroundColor Cyan
pip install -e . | Out-Null; if (-not $?) { exit 1 }

Write-Host "=== [1/8] ETL Excel -> parquet" -ForegroundColor Cyan
python -m ml.src.etl --xlsx data/master/raw2value_v4.xlsx --out data/reference/
if (-not $?) { exit 1 }

Write-Host "=== [2/8] Augmentation: training_set_v1" -ForegroundColor Cyan
python -c "from ml.src.augmentation import build_training_set; df = build_training_set(); df.to_parquet('data/processed/training_set_v1.parquet')"
if (-not $?) { exit 1 }

Write-Host "=== [3/8] Feature pipeline fit" -ForegroundColor Cyan
python -c "import pandas as pd; from ml.src.feature_pipeline import fit_and_save; df = pd.read_parquet('data/processed/training_set_v1.parquet'); fit_and_save(df, kind='xgboost', out_path='models/feature_pipeline.pkl')"
if (-not $?) { exit 1 }

Write-Host "=== [4/8] Baselines" -ForegroundColor Cyan
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/03_baselines.ipynb
if (-not $?) {
    Write-Host "nbconvert failed, trying nbclient fallback" -ForegroundColor Yellow
    python -m nbclient ml/notebooks/03_baselines.ipynb
    if (-not $?) { exit 1 }
}

Write-Host "=== [5/8] GBM benchmark" -ForegroundColor Cyan
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/04_gbm_benchmark.ipynb
if (-not $?) {
    python -m nbclient ml/notebooks/04_gbm_benchmark.ipynb
    if (-not $?) { exit 1 }
}

Write-Host "=== [6/8] Ablation" -ForegroundColor Cyan
jupyter nbconvert --execute --to notebook --inplace ml/notebooks/05_ablation.ipynb
if (-not $?) {
    python -m nbclient ml/notebooks/05_ablation.ipynb
    if (-not $?) { exit 1 }
}

Write-Host "=== [7/8] Export evidence + metadata" -ForegroundColor Cyan
python -m ml.src.evidence
if (-not $?) { exit 1 }

Write-Host "=== [8/8] Tests" -ForegroundColor Cyan
python -m pytest ml/tests/ -v
if (-not $?) { exit 1 }

Write-Host ""
Write-Host "Pipeline complete. Backend hazir." -ForegroundColor Green
