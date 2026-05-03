"""One-shot training script — bypasses notebooks, produces model_profit.pkl + model_route.pkl.

Demo prep helper. Equivalent to running ml/notebooks/04_gbm_benchmark.ipynb cells 4 + 6.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ml.src.train_profit import train_profit_models
from ml.src.train_route import train_route_models

SEED = 42

df = pd.read_parquet(REPO_ROOT / "data/processed/training_set_v1.parquet")
print(f"[1/3] training_set shape: {df.shape}")

print("[2/3] training profit models (xgb / lgb / catboost)...")
metrics_p, best_p, models_p = train_profit_models(df, seed=SEED)
for k, v in metrics_p.items():
    print(f"  {k}: rmse={v['rmse']:.0f}  mae={v['mae']:.0f}  r2={v['r2']:.4f}  mape={v['mape']:.3f}  train_sec={v['train_sec']:.1f}")
print(f"  BEST profit -> {best_p}")
joblib.dump(models_p[best_p], REPO_ROOT / "models/model_profit.pkl")
print("  saved models/model_profit.pkl")

print("[3/3] training route models (xgb / lgb / catboost)...")
metrics_r, best_r, models_r, classes = train_route_models(df, seed=SEED)
for k, v in metrics_r.items():
    print(f"  {k}: acc={v['accuracy']:.4f}  macro_f1={v['macro_f1']:.4f}  top2={v.get('top2_accuracy', 0):.4f}  train_sec={v['train_sec']:.1f}")
print(f"  BEST route -> {best_r}")
print(f"  classes ({len(classes)}): {classes}")
joblib.dump(models_r[best_r], REPO_ROOT / "models/model_route.pkl")
print("  saved models/model_route.pkl")

results = {
    "profit": {**metrics_p, "best_model": best_p},
    "route": {**metrics_r, "best_model": best_r, "classes": classes},
    "seed": SEED,
}
out = REPO_ROOT / "data/processed/gbm_results.json"
out.write_text(json.dumps(results, indent=2, default=float))
print(f"saved {out}")
print("DONE")
