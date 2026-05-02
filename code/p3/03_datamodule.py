"""
T3.3 — PyTorch DataModule (P1 manifest sözleşmesi ile sıkı uyumlu).
Modul A v2, P3 ML Mühendisi (Pomzadoya hackathon).

═══════════════════════════════════════════════════════════════════════════
P1 ↔ P3 SÖZLEŞMESİ (data/manifest.json — datacı P1 sahibi, tek source-of-truth)
═══════════════════════════════════════════════════════════════════════════
1. ARD: 17 bant, EPSG:32636, 20m, NoData = manifest["ard"]["nodata"] (-9999.0).
2. Bant sırası ve mean/std: manifest["bands"][i]["mean"]/["std"], i=0..16.
   Sıra: B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12,VV_dB,VH_dB,DEM,slope,NDVI,BSI,Albedo.
3. Sentinel-2 reflectance scale (manifest["scale"] = 10000.0) YALNIZ idx 0-9
   bantlarına uygulanmıştır — mean/std zaten scaled DN üzerinden hesaplandığı
   için P3 normalizasyonu scale'i KULLANMAZ; doğrudan (x - mean)/std uygular.
4. Tile dizini: manifest["tiles"]["tiles_dir"] (ham 17 bant tile'lar 256×256).
5. Slope: full_ard band 13 (idx 13) — `data/dem/slope_avanos.tif` ham dosyası
   bozuk/NaN olduğu için ASLA tüketilmez. Tile zaten 17 bantlık ARD'den split
   olduğundan slope tile içeriden okunur (ek dosya yok).

NoData KURALI (P1'in açık talimatı):
  -9999 finite kalır → sadece NaN/inf kontrolü YETERSİZ.
  DataLoader normalize etmeden ÖNCE her kanalda piksel değerini test eder:
    valid = (tile != nodata) & np.isfinite(tile)   # per-pixel & per-channel
    tile_invalid = ~valid.all(axis=0)               # piksel hiç bir kanalda
                                                    # invalid → tüm piksel atılır
  Mask: invalid piksellerine ignore_idx (255) yazılır → BCEDiceLoss bunları atlar.
  Tile değeri: invalid pikseller per-channel mean ile DOLDURULUR (sıfırla DEĞİL),
  böylece normalize sonrası z-score = 0 → conv katmanına nötr girdi gider.
═══════════════════════════════════════════════════════════════════════════

Input:
  - tile dosyaları   : data/tiles/*.tif (manifest tiles.tiles_dir)
  - full mask        : data/labels/full_mask.tif (P2 T2.8)
  - blok CV split    : data/labels/blok_cv_split.json (P2 T2.7, Roberts 2017)
  - manifest         : data/manifest.json (P1 T1.9) — ZORUNLU

split JSON formatı (P2 ile sözleşme):
{
  "fold_0": {"train": ["000_001.tif", ...], "val": ["004_002.tif", ...]},
  "fold_1": {...},
  ...
  "fold_4": {...}
}

ignore_index=255: WDPA Göreme 1000 m buffer (P2 T2.6) + ARD NoData pikselleri.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

try:
    import rasterio
    from rasterio.windows import from_bounds as window_from_bounds
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


IGNORE_INDEX = 255
EXPECTED_BANDS = 17
EXPECTED_NODATA = -9999.0
EXPECTED_CRS_EPSG = 32636


# -----------------------------------------------------------------------
# 1) Manifest sözleşmesi — tek source-of-truth (P1 T1.9)
# -----------------------------------------------------------------------
@dataclass(frozen=True)
class ManifestContract:
    """P1 manifest.json'unun P3 için doğrulanmış görünümü.

    Attributes:
        mean         : (C,) float32 per-band ampirik ortalama (manifest bands[i].mean).
        std          : (C,) float32 per-band ampirik std.
        nodata       : NoData değeri (-9999.0).
        in_channels  : 17.
        band_names   : ["B2","B3",...,"Albedo"].
        tile_dir     : Tile dizininin manifest-belirttiği yolu (REPO köküne göre).
        scale        : S2 reflectance scale (10000.0) — bilgi amaçlı; P3 kullanmaz.
        crs_epsg     : 32636 (sanity check için).
    """
    mean: np.ndarray
    std: np.ndarray
    nodata: float
    in_channels: int
    band_names: List[str]
    tile_dir: Path
    scale: float
    crs_epsg: int

    @classmethod
    def from_json(cls, manifest_path: str | Path, repo_root: Optional[Path] = None) -> "ManifestContract":
        manifest_path = Path(manifest_path)
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"Manifest bulunamadı: {manifest_path}. "
                "P1'in data/manifest.json çıktısı zorunludur — DEFAULT fallback yok."
            )
        with open(manifest_path, encoding="utf-8") as f:
            m = json.load(f)

        # 1. Bantlar
        bands = m.get("bands")
        if not bands or not isinstance(bands, list):
            raise ValueError(f"Manifest 'bands' listesi eksik: {manifest_path}")
        if len(bands) != EXPECTED_BANDS:
            raise ValueError(
                f"Manifest bant sayısı {len(bands)}, beklenen {EXPECTED_BANDS}. "
                "P1 T1.7 17-kanal Full ARD üretmeliydi."
            )
        for i, b in enumerate(bands):
            if "mean" not in b or "std" not in b or "name" not in b:
                raise ValueError(
                    f"Manifest bands[{i}] içinde mean/std/name eksik: {b}"
                )

        mean = np.asarray([b["mean"] for b in bands], dtype=np.float32)
        std = np.asarray([b["std"] for b in bands], dtype=np.float32)
        if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(std)):
            raise ValueError(
                f"Manifest mean/std finite değil: mean={mean}, std={std}"
            )
        if np.any(std <= 0):
            raise ValueError(
                f"Manifest std sıfır/negatif bant var: {std.tolist()}"
            )

        # 2. NoData
        ard = m.get("ard", {})
        nodata = float(ard.get("nodata", EXPECTED_NODATA))
        if nodata != EXPECTED_NODATA:
            print(f"[DM] UYARI: manifest nodata={nodata} (beklenen {EXPECTED_NODATA}).")

        # 3. CRS
        crs = ard.get("crs", f"EPSG:{EXPECTED_CRS_EPSG}")
        try:
            crs_epsg = int(str(crs).split(":")[-1])
        except Exception:
            crs_epsg = EXPECTED_CRS_EPSG
        if crs_epsg != EXPECTED_CRS_EPSG:
            print(f"[DM] UYARI: manifest CRS={crs_epsg} (beklenen {EXPECTED_CRS_EPSG}).")

        # 4. Tile dir (Windows backslash veya forward slash tolere et)
        tiles_meta = m.get("tiles", {})
        raw_tile_dir = tiles_meta.get("tiles_dir", "data/tiles")
        # Normalize: backslash -> forward slash, sonra Path
        tile_dir_norm = Path(str(raw_tile_dir).replace("\\", "/"))
        if repo_root is not None and not tile_dir_norm.is_absolute():
            tile_dir_norm = (repo_root / tile_dir_norm).resolve()

        # 5. Scale (bilgi amaçlı — P3 kullanmaz, mean/std zaten scaled DN'den)
        scale = float(m.get("scale", 10000.0))

        return cls(
            mean=mean,
            std=std,
            nodata=nodata,
            in_channels=EXPECTED_BANDS,
            band_names=[b["name"] for b in bands],
            tile_dir=tile_dir_norm,
            scale=scale,
            crs_epsg=crs_epsg,
        )

    def summary(self) -> str:
        return (
            f"ManifestContract(in_ch={self.in_channels}, nodata={self.nodata}, "
            f"crs=EPSG:{self.crs_epsg}, tile_dir={self.tile_dir}, "
            f"mean[0]={self.mean[0]:.2f}, std[0]={self.std[0]:.2f}, "
            f"bands={','.join(self.band_names[:5])}...{self.band_names[-1]})"
        )


# -----------------------------------------------------------------------
# 2) Single tile dataset
# -----------------------------------------------------------------------
class PomzaTileDataset(Dataset):
    """17 kanal ARD tile + binary pomza mask dataset.

    P1 sözleşmesi sıkı: tile 17 bant, NoData=-9999.

    Args:
        contract   : ManifestContract — P1 manifest.json'undan üretilmiş.
        tile_dir   : Tile .tif klasörü (contract.tile_dir override eder).
        full_mask  : Tüm AOI mask path veya tile-bazlı mask klasörü (P2 T2.8).
        tile_list  : Okunacak tile basename listesi (split'ten gelir).
        augment    : albumentations Compose veya None.
        ignore_idx : WDPA buffer + NoData ignore değeri (default 255).
    """

    def __init__(
        self,
        contract: ManifestContract,
        full_mask: str | Path,
        tile_list: List[str],
        tile_dir: Optional[str | Path] = None,
        augment: Optional[Callable] = None,
        ignore_idx: int = IGNORE_INDEX,
    ):
        if not HAS_RASTERIO:
            raise ImportError("rasterio gerekli. `pip install rasterio`.")
        self.contract = contract
        self.tile_dir = Path(tile_dir) if tile_dir is not None else contract.tile_dir
        self.full_mask_path = Path(full_mask)
        self.tile_list = list(tile_list)
        self.augment = augment
        self.ignore_idx = ignore_idx
        self.in_channels = contract.in_channels
        self.nodata = contract.nodata
        self.mean = contract.mean
        self.std = contract.std

        # Mask: dizin ise tile-bazlı, dosya ise window'lu okuma.
        self.mask_per_tile = self.full_mask_path.is_dir()

    def __len__(self) -> int:
        return len(self.tile_list)

    # -- I/O helpers ------------------------------------------------------

    def _read_tile_raw(self, name: str) -> np.ndarray:
        path = self.tile_dir / name
        if not path.exists():
            raise FileNotFoundError(
                f"Tile yok: {path} "
                f"(tile_dir={self.tile_dir}, manifest sözleşmesi)."
            )
        with rasterio.open(path) as src:
            arr = src.read().astype(np.float32)  # (C, H, W)
        if arr.shape[0] != self.in_channels:
            raise ValueError(
                f"{name}: kanal sayısı {arr.shape[0]}, manifest beklentisi "
                f"{self.in_channels}. P1 T1.7 Full ARD 17 bant olmalı."
            )
        return arr

    def _read_mask(self, name: str, tile_shape_hw: Tuple[int, int]) -> np.ndarray:
        if self.mask_per_tile:
            stem = Path(name).stem
            candidates = [
                self.full_mask_path / f"{stem}_mask.tif",
                self.full_mask_path / name,
                self.full_mask_path / f"{stem}.tif",
            ]
            mask_path = next((p for p in candidates if p.exists()), None)
            if mask_path is None:
                raise FileNotFoundError(
                    f"Tile-bazlı mask bulunamadı: {candidates[0].name} (P2 T2.8)."
                )
            with rasterio.open(mask_path) as src:
                mask = src.read(1).astype(np.uint8)
        else:
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
                window = window_from_bounds(*bounds, transform=ms.transform)
                mask = ms.read(
                    1, window=window, boundless=True,
                    fill_value=self.ignore_idx,
                ).astype(np.uint8)

        # Boyut hizalama (nearest crop/pad)
        th, tw = tile_shape_hw
        if mask.shape != (th, tw):
            mh, mw = mask.shape
            out = np.full((th, tw), self.ignore_idx, dtype=np.uint8)
            h, w = min(mh, th), min(mw, tw)
            out[:h, :w] = mask[:h, :w]
            mask = out
        return mask

    # -- Core normalization & NoData handling ----------------------------

    def _normalize_with_nodata(
        self, tile: np.ndarray, mask: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """P1 sözleşmesi: -9999 finite kalır → açık eşitlik kontrolü.

        Plan:
          1. valid_per_channel = (tile != nodata) & np.isfinite(tile)  shape (C,H,W)
          2. valid_pixel       = valid_per_channel.all(axis=0)         shape (H,W)
          3. mask[~valid_pixel] = ignore_idx → loss bunları atlar.
          4. Invalid kanalları per-channel mean ile DOLDUR (sıfırla değil) →
             normalize sonrası z = 0, conv'a nötr girdi.
          5. (tile - mean) / std → standart z-score.
        """
        valid_per_ch = (tile != self.nodata) & np.isfinite(tile)
        valid_pixel = valid_per_ch.all(axis=0)

        # Mask güncelle (ignore_idx'e zaten eşit olabilir; her durumda ezelim).
        if not valid_pixel.all():
            mask = mask.copy()
            mask[~valid_pixel] = self.ignore_idx

        # Invalid kanal pikselini per-channel mean ile doldur.
        # (Per-pixel düzeyinde değil — kanal düzeyinde: belirli kanalda invalid
        # piksel her kanalda mean'e set edilebilir; ancak diğer geçerli kanalları
        # bozmamak için yalnızca o kanaldaki invalid pikseli mean'e çekiyoruz.)
        if not valid_per_ch.all():
            for c in range(tile.shape[0]):
                invalid_c = ~valid_per_ch[c]
                if invalid_c.any():
                    tile[c, invalid_c] = self.mean[c]

        # Normalize (mean/std manifest'ten — scaled DN üstünden)
        tile = (tile - self.mean[:, None, None]) / (self.std[:, None, None] + 1e-6)

        # Son güvenlik ağı: yukarıdaki doldurma sonrası NaN/inf kalmamalı,
        # ama numerik kazaya karşı sıfıra çek (mask zaten ignore'a çekilmiş).
        if not np.isfinite(tile).all():
            tile = np.nan_to_num(tile, nan=0.0, posinf=0.0, neginf=0.0)

        return tile, mask

    # -- Sample fetch -----------------------------------------------------

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        name = self.tile_list[idx]
        tile = self._read_tile_raw(name)                    # (C,H,W) float32, ham (-9999 dahil)
        mask = self._read_mask(name, tile.shape[1:])        # (H,W) uint8

        tile, mask = self._normalize_with_nodata(tile, mask)

        # Augmentation (albumentations API: image=HWC, mask=HW)
        if self.augment is not None:
            sample = self.augment(
                image=np.transpose(tile, (1, 2, 0)),
                mask=mask,
            )
            tile = np.transpose(sample["image"], (2, 0, 1)).astype(np.float32)
            mask = sample["mask"].astype(np.uint8)

        x = torch.from_numpy(np.ascontiguousarray(tile)).float()
        y = torch.from_numpy(np.ascontiguousarray(mask)).long()
        return x, y


# -----------------------------------------------------------------------
# 3) DataModule wrapper (5-fold blok CV split JSON'undan loader üretir)
# -----------------------------------------------------------------------
class PomzaDataModule:
    """5-fold spatial blok CV DataModule (Roberts 2017).

    P1 sözleşmesi: manifest_json ZORUNLU. DEFAULT fallback yok.

    Usage:
        dm = PomzaDataModule(
            tile_dir='data/tiles',
            full_mask='data/labels/full_mask.tif',
            split_json='data/labels/blok_cv_split.json',
            manifest_json='data/manifest.json',   # required
            batch_size=8, num_workers=4,
            train_aug=default_train_aug(),
        )
        for fold in range(dm.fold_count):
            dm.set_fold(fold)
            train_loader = dm.train_dataloader()
            val_loader   = dm.val_dataloader()
    """

    def __init__(
        self,
        tile_dir: str | Path | None,
        full_mask: str | Path,
        split_json: str | Path,
        manifest_json: str | Path,
        batch_size: int = 8,
        num_workers: int = 4,
        train_aug: Optional[Callable] = None,
        val_aug: Optional[Callable] = None,
        in_channels: int = EXPECTED_BANDS,
        pin_memory: bool = True,
    ):
        if manifest_json is None:
            raise ValueError(
                "manifest_json zorunlu. P1'in data/manifest.json çıktısı "
                "tek veri sözleşmesidir — DEFAULT fallback kaldırıldı. "
                "06_train.py'a --manifest-json data/manifest.json geçirin."
            )

        # Repo kökünü çözümle (manifest path'i göreli ise mutlak yapacağız).
        manifest_path = Path(manifest_json).resolve()
        repo_root = manifest_path.parent.parent  # data/manifest.json -> repo/

        self.contract = ManifestContract.from_json(manifest_path, repo_root=repo_root)
        if self.contract.in_channels != in_channels:
            raise ValueError(
                f"in_channels argümanı ({in_channels}) ile manifest "
                f"({self.contract.in_channels}) uyumsuz."
            )

        # Tile dir: kullanıcı override → manifest contract → fallback.
        if tile_dir is not None:
            self.tile_dir = Path(str(tile_dir).replace("\\", "/")).resolve()
        else:
            self.tile_dir = self.contract.tile_dir
        if not self.tile_dir.is_dir():
            raise FileNotFoundError(
                f"Tile dizini yok: {self.tile_dir}. "
                "P1 T1.8 tile splitting çıktısı bekleniyor."
            )

        self.full_mask = Path(full_mask)
        self.split_json = Path(split_json)
        if not self.split_json.exists():
            raise FileNotFoundError(
                f"Split JSON yok: {self.split_json} (P2 T2.7 Roberts 5-fold)."
            )

        with open(self.split_json) as f:
            self.splits = json.load(f)
        if not self.splits:
            raise ValueError(f"Split JSON boş: {self.split_json}")

        self.batch_size = batch_size
        self.num_workers = num_workers
        self.train_aug = train_aug
        self.val_aug = val_aug
        self.in_channels = in_channels
        self.pin_memory = pin_memory
        self._fold: Optional[int] = None

        print(f"[DM] {self.contract.summary()}")
        print(f"[DM] tile_dir={self.tile_dir}, folds={self.fold_count}")

    @property
    def fold_count(self) -> int:
        return len(self.splits)

    def set_fold(self, fold: int):
        if fold < 0 or fold >= self.fold_count:
            raise ValueError(
                f"fold {fold} dışında. fold_count={self.fold_count}"
            )
        self._fold = fold

    def _build(self, split: str, aug) -> PomzaTileDataset:
        if self._fold is None:
            raise RuntimeError("Önce dm.set_fold(k) çağır.")
        key = f"fold_{self._fold}"
        if key not in self.splits:
            raise KeyError(
                f"Split JSON'da {key} yok. Mevcut: {list(self.splits.keys())}"
            )
        if split not in self.splits[key]:
            raise KeyError(
                f"Split JSON {key} altında '{split}' yok. "
                f"Mevcut: {list(self.splits[key].keys())}"
            )
        tile_list = self.splits[key][split]
        if not tile_list:
            raise ValueError(f"{key}/{split} boş tile listesi.")

        return PomzaTileDataset(
            contract=self.contract,
            full_mask=self.full_mask,
            tile_list=tile_list,
            tile_dir=self.tile_dir,
            augment=aug,
        )

    def train_dataloader(self) -> DataLoader:
        ds = self._build("train", self.train_aug)
        return DataLoader(
            ds, batch_size=self.batch_size, shuffle=True,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
            drop_last=True,
            persistent_workers=(self.num_workers > 0),
        )

    def val_dataloader(self) -> DataLoader:
        ds = self._build("val", self.val_aug)
        return DataLoader(
            ds, batch_size=self.batch_size, shuffle=False,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
            drop_last=False,
            persistent_workers=(self.num_workers > 0),
        )


# -----------------------------------------------------------------------
# 4) Default augmentation (P2 T2.9 ile uyumlu)
# -----------------------------------------------------------------------
def default_train_aug(p_flip: float = 0.5, p_rot: float = 0.5):
    """Çok-bantlı ARD için güvenli augmentation.

    Reflectance/dB/derece kanallarını kıracağı için renk perturbasyonu YOK
    (ColorJitter, Brightness, RGBShift vb.). Sadece geometrik dönüşümler.
    """
    try:
        import albumentations as A
    except ImportError:
        return None
    return A.Compose([
        A.HorizontalFlip(p=p_flip),
        A.VerticalFlip(p=p_flip),
        A.RandomRotate90(p=p_rot),
    ])


def default_val_aug():
    return None


# -----------------------------------------------------------------------
# 5) Self-test (manifest contract sanity)
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python 03_datamodule.py <manifest.json>")
        sys.exit(2)
    contract = ManifestContract.from_json(sys.argv[1])
    print(contract.summary())
    print(f"  mean: {contract.mean}")
    print(f"  std:  {contract.std}")
    print(f"  nodata: {contract.nodata}, scale: {contract.scale}, "
          f"crs: EPSG:{contract.crs_epsg}")
    print(f"  tile_dir: {contract.tile_dir}")
