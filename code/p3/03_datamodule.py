"""
T3.3 — PyTorch DataModule (17 kanal ARD + label mask)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Input:
  - tile dosyalari : /data/ard/tiles/*.tif (17 kanal, 256x256, P1 T1.8)
  - full mask      : /data/labels/full_mask.tif (P2 T2.7)
  - blok CV split  : /data/labels/blok_cv_split.json (P2 T2.6, Roberts 2017 5-fold)

Karar referansi: [K#10] spatial 5-fold blok CV (random KFold YASAK)

split JSON formati (P2 ile sozlesme):
{
  "fold_0": {"train": ["tile_0001.tif", ...], "val": ["tile_0123.tif", ...]},
  "fold_1": {...},
  ...
  "fold_4": {...}
}

ignore_index=255: WDPA Goreme 1000 m buffer (P2 T2.5) — loss'tan haric tutulur.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

try:
    import rasterio
    from rasterio.windows import Window
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


# -----------------------------------------------------------------------
# 1) Default normalizasyon (Sentinel-2 L2A reflectance ~ [0, 1] sonrasi)
#    P1 ARD manifest JSON'unda gercek mean/std saglanmali; burada fallback.
# -----------------------------------------------------------------------
DEFAULT_MEAN = np.array([
    # 13 S2 bant (B01..B12 + B8A) (yaklasik Sentinel-2 L2A normalizasyonu)
    0.10, 0.09, 0.08, 0.10, 0.13, 0.16, 0.18, 0.18, 0.18, 0.04, 0.18, 0.13, 0.07,
    # S1 VV, VH (dB / 25)
    -0.50, -0.70,
    # DEM (m / 2000), slope (deg / 45)
    0.40, 0.20,
], dtype=np.float32)

DEFAULT_STD = np.array([
    0.05, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.03, 0.10, 0.08, 0.05,
    0.20, 0.20,
    0.20, 0.15,
], dtype=np.float32)

IGNORE_INDEX = 255


# -----------------------------------------------------------------------
# 2) Single tile dataset
# -----------------------------------------------------------------------
class PomzaTileDataset(Dataset):
    """17 kanal ARD tile + binary pomza mask dataset.

    Args:
        tile_dir   : tile .tif klasoru (256x256 ardisik tile'lar).
        full_mask  : tum AOI mask path veya tile-bazli mask klasoru.
        tile_list  : okumak istenen tile basename listesi (split'ten gelir).
        manifest   : opsiyonel manifest JSON (mean/std overrid).
        augment    : albumentations Compose veya None.
        ignore_idx : WDPA buffer ignore degeri.
    """

    def __init__(
        self,
        tile_dir: str | Path,
        full_mask: str | Path,
        tile_list: List[str],
        manifest: Optional[Dict] = None,
        augment: Optional[Callable] = None,
        ignore_idx: int = IGNORE_INDEX,
        in_channels: int = 17,
    ):
        if not HAS_RASTERIO:
            raise ImportError("rasterio gerekli. `pip install rasterio`.")
        self.tile_dir = Path(tile_dir)
        self.full_mask_path = Path(full_mask)
        self.tile_list = list(tile_list)
        self.augment = augment
        self.ignore_idx = ignore_idx
        self.in_channels = in_channels

        if manifest is not None and "mean" in manifest and "std" in manifest:
            self.mean = np.asarray(manifest["mean"], dtype=np.float32)
            self.std = np.asarray(manifest["std"], dtype=np.float32)
        elif (
            manifest is not None
            and manifest.get("bands")
            and all("mean" in b and "std" in b for b in manifest["bands"])
        ):
            self.mean = np.asarray(
                [b["mean"] for b in manifest["bands"]], dtype=np.float32
            )
            self.std = np.asarray(
                [b["std"] for b in manifest["bands"]], dtype=np.float32
            )
        else:
            self.mean = DEFAULT_MEAN.copy()
            self.std = DEFAULT_STD.copy()

        if len(self.mean) != in_channels or len(self.std) != in_channels:
            raise ValueError(
                f"mean/std uzunlugu ({len(self.mean)}/{len(self.std)}) "
                f"!= in_channels ({in_channels})"
            )

        # Mask: tek raster ise her tile icin window ile cek;
        # tile_dir/<basename>_mask.tif varsa onu oku.
        self.mask_per_tile = (self.full_mask_path.is_dir())

    def __len__(self) -> int:
        return len(self.tile_list)

    def _read_tile(self, name: str) -> np.ndarray:
        path = self.tile_dir / name
        with rasterio.open(path) as src:
            arr = src.read().astype(np.float32)  # (C, H, W)
        if arr.shape[0] != self.in_channels:
            raise ValueError(
                f"{name}: beklenen {self.in_channels} kanal, bulunan {arr.shape[0]}"
            )
        return arr

    def _read_mask(self, name: str, tile_arr: np.ndarray) -> np.ndarray:
        if self.mask_per_tile:
            # tile-bazli mask
            stem = Path(name).stem
            mask_path = self.full_mask_path / f"{stem}_mask.tif"
            if not mask_path.exists():
                # fallback: name ile birebir
                mask_path = self.full_mask_path / name
            with rasterio.open(mask_path) as src:
                mask = src.read(1).astype(np.uint8)
        else:
            # full mask raster + tile bbox window
            tile_path = self.tile_dir / name
            with rasterio.open(tile_path) as ts:
                bounds = ts.bounds
                tile_crs = ts.crs
            with rasterio.open(self.full_mask_path) as ms:
                if ms.crs != tile_crs:
                    raise ValueError(
                        f"CRS uyumsuz: tile={tile_crs}, mask={ms.crs}. "
                        "P1+P2 co-registration tekrar kontrol et."
                    )
                window = rasterio.windows.from_bounds(
                    *bounds, transform=ms.transform
                )
                mask = ms.read(1, window=window, boundless=True,
                               fill_value=self.ignore_idx).astype(np.uint8)
        # Boyut hizalama
        if mask.shape != tile_arr.shape[1:]:
            # Basit nearest-neighbor crop/pad
            mh, mw = mask.shape
            th, tw = tile_arr.shape[1:]
            out = np.full((th, tw), self.ignore_idx, dtype=np.uint8)
            h = min(mh, th); w = min(mw, tw)
            out[:h, :w] = mask[:h, :w]
            mask = out
        return mask

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        name = self.tile_list[idx]
        tile = self._read_tile(name)             # (C, H, W) float32
        mask = self._read_mask(name, tile)        # (H, W) uint8

        # Normalize
        tile = (tile - self.mean[:, None, None]) / (self.std[:, None, None] + 1e-6)
        # NaN guard (P1 NoData -> 0, mask'e ignore yaz)
        nan_mask = ~np.isfinite(tile).all(axis=0)
        if nan_mask.any():
            tile = np.nan_to_num(tile, nan=0.0, posinf=0.0, neginf=0.0)
            mask = mask.copy()
            mask[nan_mask] = self.ignore_idx

        # Augmentation (albumentations API: image=HWC, mask=HW)
        if self.augment is not None:
            sample = self.augment(
                image=np.transpose(tile, (1, 2, 0)),
                mask=mask,
            )
            tile = np.transpose(sample["image"], (2, 0, 1)).astype(np.float32)
            mask = sample["mask"].astype(np.uint8)

        x = torch.from_numpy(tile).float()
        y = torch.from_numpy(mask).long()
        return x, y


# -----------------------------------------------------------------------
# 3) DataModule wrapper (5-fold blok CV split JSON'undan loader uretir)
# -----------------------------------------------------------------------
class PomzaDataModule:
    """5-fold spatial blok CV DataModule (Roberts 2017).

    Usage:
        dm = PomzaDataModule(
            tile_dir='/data/ard/tiles',
            full_mask='/data/labels/full_mask.tif',
            split_json='/data/labels/blok_cv_split.json',
            batch_size=8, num_workers=4,
            train_aug=albumentations.Compose([...]),
        )
        for fold in range(5):
            dm.set_fold(fold)
            train_loader = dm.train_dataloader()
            val_loader   = dm.val_dataloader()
    """

    def __init__(
        self,
        tile_dir: str | Path,
        full_mask: str | Path,
        split_json: str | Path,
        manifest_json: Optional[str | Path] = None,
        batch_size: int = 8,
        num_workers: int = 4,
        train_aug: Optional[Callable] = None,
        val_aug: Optional[Callable] = None,
        in_channels: int = 17,
        pin_memory: bool = True,
    ):
        self.tile_dir = Path(tile_dir)
        self.full_mask = Path(full_mask)
        self.split_json = Path(split_json)
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.train_aug = train_aug
        self.val_aug = val_aug
        self.in_channels = in_channels
        self.pin_memory = pin_memory

        with open(self.split_json) as f:
            self.splits = json.load(f)

        self.manifest = None
        if manifest_json is not None and Path(manifest_json).exists():
            with open(manifest_json) as f:
                self.manifest = json.load(f)

        self._fold = None

    @property
    def fold_count(self) -> int:
        return len(self.splits)

    def set_fold(self, fold: int):
        if fold < 0 or fold >= self.fold_count:
            raise ValueError(f"fold {fold} disinda. fold_count={self.fold_count}")
        self._fold = fold

    def _build(self, split: str, aug) -> PomzaTileDataset:
        if self._fold is None:
            raise RuntimeError("Once dm.set_fold(k) cagir.")
        key = f"fold_{self._fold}"
        tile_list = self.splits[key][split]
        return PomzaTileDataset(
            tile_dir=self.tile_dir,
            full_mask=self.full_mask,
            tile_list=tile_list,
            manifest=self.manifest,
            augment=aug,
            in_channels=self.in_channels,
        )

    def train_dataloader(self) -> DataLoader:
        ds = self._build("train", self.train_aug)
        return DataLoader(
            ds, batch_size=self.batch_size, shuffle=True,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
            drop_last=True, persistent_workers=(self.num_workers > 0),
        )

    def val_dataloader(self) -> DataLoader:
        ds = self._build("val", self.val_aug)
        return DataLoader(
            ds, batch_size=self.batch_size, shuffle=False,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
            drop_last=False, persistent_workers=(self.num_workers > 0),
        )


# -----------------------------------------------------------------------
# 4) Default augmentation (P2 T2.8 ile uyumlu)
# -----------------------------------------------------------------------
def default_train_aug(p_flip: float = 0.5, p_rot: float = 0.5):
    """Cok-bantli ARD icin guvenli augmentation (renk perturbasyonu YOK)."""
    try:
        import albumentations as A
    except ImportError:
        return None
    return A.Compose([
        A.HorizontalFlip(p=p_flip),
        A.VerticalFlip(p=p_flip),
        A.RandomRotate90(p=p_rot),
        # Reflectance perturbasyonu yok — domain bilgisi kirilmasin.
    ], additional_targets={})


def default_val_aug():
    return None
