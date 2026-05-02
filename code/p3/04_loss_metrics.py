"""
T3.3 (loss) + T3.6 (metrics) — Loss + Metrics + threshold sweep
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Loss: BCEWithLogitsLoss + Dice (combo)
  - ignore_index=255 (WDPA Goreme buffer haric tut)
  - pos_weight opsiyonel (sinif dengesizligi icin, P2 raporundan gelir)

Metrics: IoU (Jaccard), F1, precision, recall, MCC
Threshold sweep: F1-max threshold (Karar #14 — sabit 0.5 degil)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


IGNORE_INDEX = 255


# -----------------------------------------------------------------------
# 1) Loss
# -----------------------------------------------------------------------
class BCEDiceLoss(nn.Module):
    """BCE + Dice combo, ignore_index destekli.

    Args:
        bce_weight: BCE agirligi (toplam = bce_weight * BCE + (1-bce_weight) * Dice)
        pos_weight: BCE pos_weight (negatif/pozitif oran = sinif dengesizligi)
        ignore_index: maskte bu deger varsa loss'tan dusur (default 255)
        smooth: Dice'da bolme guvenligi
    """

    def __init__(
        self,
        bce_weight: float = 0.5,
        pos_weight: Optional[float] = None,
        ignore_index: int = IGNORE_INDEX,
        smooth: float = 1.0,
    ):
        super().__init__()
        self.bce_weight = float(bce_weight)
        self.dice_weight = 1.0 - self.bce_weight
        self.ignore_index = ignore_index
        self.smooth = smooth
        self._pos_weight = (
            torch.tensor([pos_weight], dtype=torch.float32)
            if pos_weight is not None else None
        )

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: (B, 1, H, W) raw logits
            target: (B, H, W) long ya da float, {0, 1, ignore_index}
        """
        if logits.dim() == 4 and logits.size(1) == 1:
            logits = logits.squeeze(1)  # (B, H, W)
        target = target.float()

        valid = (target != self.ignore_index)
        if valid.sum() == 0:
            return logits.sum() * 0.0  # graph'i koru, deger sifir

        # BCE (yalnizca valid pikseller)
        pw = self._pos_weight.to(logits.device) if self._pos_weight is not None else None
        bce_full = F.binary_cross_entropy_with_logits(
            logits, target.clamp(0, 1),
            reduction="none", pos_weight=pw,
        )
        bce = (bce_full * valid.float()).sum() / valid.float().sum()

        # Dice
        probs = torch.sigmoid(logits)
        probs_v = probs * valid.float()
        target_v = target.clamp(0, 1) * valid.float()
        intersection = (probs_v * target_v).sum(dim=(1, 2))
        denom = probs_v.sum(dim=(1, 2)) + target_v.sum(dim=(1, 2))
        dice_score = (2.0 * intersection + self.smooth) / (denom + self.smooth)
        dice_loss = 1.0 - dice_score.mean()

        return self.bce_weight * bce + self.dice_weight * dice_loss


# -----------------------------------------------------------------------
# 2) Metrics
# -----------------------------------------------------------------------
@dataclass
class BinaryMetrics:
    iou: float
    f1: float
    precision: float
    recall: float
    accuracy: float
    mcc: float
    threshold: float
    tp: int
    fp: int
    fn: int
    tn: int

    def as_dict(self) -> Dict[str, float]:
        return {
            "iou": self.iou, "f1": self.f1,
            "precision": self.precision, "recall": self.recall,
            "accuracy": self.accuracy, "mcc": self.mcc,
            "threshold": self.threshold,
            "tp": self.tp, "fp": self.fp, "fn": self.fn, "tn": self.tn,
        }


def _confusion(
    probs: np.ndarray,
    target: np.ndarray,
    threshold: float,
    ignore_index: int = IGNORE_INDEX,
) -> Tuple[int, int, int, int]:
    valid = (target != ignore_index)
    p = (probs >= threshold) & valid
    t = (target == 1) & valid
    n = (target == 0) & valid
    tp = int((p & t).sum())
    fp = int((p & n).sum())
    fn = int((~p & valid & t).sum())
    tn = int((~p & valid & n).sum())
    return tp, fp, fn, tn


def compute_metrics(
    probs: np.ndarray,
    target: np.ndarray,
    threshold: float = 0.5,
    ignore_index: int = IGNORE_INDEX,
) -> BinaryMetrics:
    """Probabilite haritasi + ground truth -> metrik seti.

    probs : (..., H, W) float [0, 1]
    target: (..., H, W) int  {0, 1, ignore_index}
    """
    probs = np.asarray(probs)
    target = np.asarray(target)
    tp, fp, fn, tn = _confusion(probs, target, threshold, ignore_index)
    eps = 1e-9
    precision = tp / max(tp + fp, eps)
    recall = tp / max(tp + fn, eps)
    f1 = 2 * precision * recall / max(precision + recall, eps)
    iou = tp / max(tp + fp + fn, eps)
    accuracy = (tp + tn) / max(tp + tn + fp + fn, eps)
    # MCC
    denom = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    mcc = (tp * tn - fp * fn) / max(denom, eps)
    return BinaryMetrics(
        iou=iou, f1=f1, precision=precision, recall=recall,
        accuracy=accuracy, mcc=mcc, threshold=float(threshold),
        tp=tp, fp=fp, fn=fn, tn=tn,
    )


# -----------------------------------------------------------------------
# 3) Threshold sweep (F1-max) — Karar #14
# -----------------------------------------------------------------------
def threshold_sweep(
    probs: np.ndarray,
    target: np.ndarray,
    thresholds: Optional[np.ndarray] = None,
    ignore_index: int = IGNORE_INDEX,
) -> Dict:
    """F1-max threshold tarama.

    Returns:
        {
          "thresholds": [...],
          "f1": [...], "iou": [...], "precision": [...], "recall": [...],
          "best_threshold": float, "best_f1": float, "best_iou": float
        }
    """
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 19)
    f1s, ious, prs, rcs = [], [], [], []
    for t in thresholds:
        m = compute_metrics(probs, target, threshold=float(t),
                            ignore_index=ignore_index)
        f1s.append(m.f1); ious.append(m.iou)
        prs.append(m.precision); rcs.append(m.recall)
    f1s = np.asarray(f1s); ious = np.asarray(ious)
    best_idx = int(np.argmax(f1s))
    return {
        "thresholds": thresholds.tolist(),
        "f1": f1s.tolist(), "iou": ious.tolist(),
        "precision": prs, "recall": rcs,
        "best_threshold": float(thresholds[best_idx]),
        "best_f1": float(f1s[best_idx]),
        "best_iou": float(ious[best_idx]),
    }


# -----------------------------------------------------------------------
# 4) Streaming accumulator (DataLoader uzerinde toplama)
# -----------------------------------------------------------------------
class MetricAccumulator:
    """Validation loop'unda raw probabiliteleri & target'i biriktir.

    Usage:
        acc = MetricAccumulator()
        for x, y in val_loader:
            with torch.no_grad():
                logits = model(x.cuda())
                probs = torch.sigmoid(logits).cpu().numpy()
            acc.update(probs, y.numpy())
        sweep = acc.threshold_sweep()
    """

    def __init__(self, ignore_index: int = IGNORE_INDEX, max_pixels: int = 5_000_000):
        self.ignore_index = ignore_index
        self.max_pixels = max_pixels
        self._probs = []
        self._target = []
        self._n = 0

    def update(self, probs: np.ndarray, target: np.ndarray):
        # Sub-sample if exceeding budget (random spatial subsample)
        flat_p = probs.reshape(-1)
        flat_t = target.reshape(-1)
        if self._n + flat_p.size > self.max_pixels:
            keep = max(0, self.max_pixels - self._n)
            if keep == 0:
                return
            idx = np.random.choice(flat_p.size, size=keep, replace=False)
            flat_p = flat_p[idx]; flat_t = flat_t[idx]
        self._probs.append(flat_p)
        self._target.append(flat_t)
        self._n += flat_p.size

    def get_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        if not self._probs:
            return np.zeros(0), np.zeros(0)
        return np.concatenate(self._probs), np.concatenate(self._target)

    def metrics(self, threshold: float = 0.5) -> BinaryMetrics:
        p, t = self.get_arrays()
        return compute_metrics(p, t, threshold=threshold,
                               ignore_index=self.ignore_index)

    def threshold_sweep(self, thresholds: Optional[np.ndarray] = None) -> Dict:
        p, t = self.get_arrays()
        return threshold_sweep(p, t, thresholds=thresholds,
                               ignore_index=self.ignore_index)
