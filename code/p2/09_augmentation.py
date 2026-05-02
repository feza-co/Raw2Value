"""
T2.9 — Augmentation Pipeline
=============================

Geometric + spektral augmentation.
PyTorch Dataset'in `__getitem__` icinde cagrilacak şekilde callable.

Geometric (geometri etiket ile uyumlu olmalı — mask da donusur):
- Horizontal flip
- Vertical flip
- 90/180/270 degree rotation
- Random crop (opsiyonel — tile zaten 256x256, kapali)

Spektral (sadece raster, mask DEĞİŞMEZ):
- Brightness jitter   (±10%)
- Contrast jitter     (±10%)
- Gaussian noise      (small sigma)

NOT (v2): Goreve sinirli — daha agir augmentation (mixup, cutmix) FP riski yuksek
pomzaya benzer beyaz-kenar artefaktlari ureteceginden ATLANDI.

Kullanim:
    from code.p2.09_augmentation import PomzaAugmentor
    aug = PomzaAugmentor(p_flip=0.5, p_rot=0.5, brightness=0.1, contrast=0.1)
    img_aug, mask_aug = aug(img, mask)
"""

import numpy as np


class PomzaAugmentor:
    """
    img: np.ndarray, shape (C, H, W), float32 [0, 1] beklenir
    mask: np.ndarray, shape (H, W), uint8 (0/1/255)
    Donus: ayni shape'lerde augmente versiyonu.
    """

    def __init__(
        self,
        p_flip_h=0.5,
        p_flip_v=0.5,
        p_rot=0.5,
        brightness=0.10,
        contrast=0.10,
        noise_sigma=0.01,
        seed=None,
    ):
        self.p_flip_h = p_flip_h
        self.p_flip_v = p_flip_v
        self.p_rot = p_rot
        self.brightness = brightness
        self.contrast = contrast
        self.noise_sigma = noise_sigma
        self.rng = np.random.default_rng(seed)

    def __call__(self, img, mask):
        img, mask = self._geometric(img, mask)
        img = self._spectral(img)
        return img, mask

    def _geometric(self, img, mask):
        # Horizontal flip (sol-sag)
        if self.rng.random() < self.p_flip_h:
            img = img[:, :, ::-1].copy()
            mask = mask[:, ::-1].copy()
        # Vertical flip (yukari-asagi)
        if self.rng.random() < self.p_flip_v:
            img = img[:, ::-1, :].copy()
            mask = mask[::-1, :].copy()
        # 90/180/270 rotation
        if self.rng.random() < self.p_rot:
            k = int(self.rng.integers(1, 4))  # 1, 2, or 3 (×90°)
            img = np.rot90(img, k=k, axes=(1, 2)).copy()
            mask = np.rot90(mask, k=k).copy()
        return img, mask

    def _spectral(self, img):
        # Brightness: img * (1 + jitter)
        if self.brightness > 0:
            jitter = self.rng.uniform(-self.brightness, self.brightness)
            img = img * (1.0 + jitter)
        # Contrast: (img - mean) * (1 + jitter) + mean (channel-wise)
        if self.contrast > 0:
            jitter = self.rng.uniform(-self.contrast, self.contrast)
            mean = img.mean(axis=(1, 2), keepdims=True)
            img = (img - mean) * (1.0 + jitter) + mean
        # Gaussian noise
        if self.noise_sigma > 0:
            noise = self.rng.normal(0, self.noise_sigma, size=img.shape).astype(img.dtype)
            img = img + noise
        # Clip [0, 1] (degerler sicrasin diye)
        img = np.clip(img, 0.0, 1.0).astype(np.float32)
        return img


# Sanity self-test
if __name__ == "__main__":
    print("[T2.9] PomzaAugmentor self-test")
    aug = PomzaAugmentor(seed=42)
    img = np.random.rand(17, 256, 256).astype(np.float32)  # 17-kanal ARD
    mask = np.zeros((256, 256), dtype=np.uint8)
    mask[100:150, 100:150] = 1  # synthetic positive
    mask[0:10, 0:10] = 255       # synthetic ignore

    img2, mask2 = aug(img, mask)
    print(f"  In:  img {img.shape} dtype={img.dtype} range=[{img.min():.3f}, {img.max():.3f}]")
    print(f"       mask {mask.shape} unique={np.unique(mask)}")
    print(f"  Out: img {img2.shape} dtype={img2.dtype} range=[{img2.min():.3f}, {img2.max():.3f}]")
    print(f"       mask {mask2.shape} unique={np.unique(mask2)}")
    assert img2.shape == img.shape
    assert mask2.shape == mask.shape
    assert set(np.unique(mask2).tolist()).issubset({0, 1, 255})
    print("  ✓ Self-test passed")
