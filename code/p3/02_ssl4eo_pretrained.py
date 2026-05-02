"""
T3.2 — SSL4EO-S12 pretrained yukleme + 13->17 multi-channel adapter
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Karar referansi: [K#2] SSL4EO-S12 pretrained, [K#6] multi-channel adapter

SSL4EO-S12 referans:
  Wang et al. 2023, "SSL4EO-S12: A Large-Scale Multi-Modal, Multi-Temporal
  Dataset for Self-Supervised Learning in Earth Observation" (IEEE GRSM)
  HuggingFace: wangyi111/SSL4EO-S12
  GitHub: https://github.com/zhu-xlab/SSL4EO-S12

Adapter mantigi (13 -> 17 kanal):
  SSL4EO-S12 13 Sentinel-2 bandi ile pretrain edildi (B01..B12 + B8A).
  Bizim ARD 17 kanal: 13 S2 + S1 VV + S1 VH + DEM + slope.
  Yeni 4 kanal icin agirlik = mevcut 13 SSL4EO bandinin ortalamasi
  (ImageNet'te BGR -> 1ch grayscale icin de ayni teknik kullanilir,
  Carreira-Perpinan 2017, "Inflated 3D ConvNets" patternine yakin).

Kullanim:
    model = build_ssl4eo_unet(num_classes=1, in_channels=17,
                              ssl4eo_ckpt='/models/ssl4eo_s12_resnet50.pt')
    out = model(torch.randn(1, 17, 256, 256))   # -> (1, 1, 256, 256)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import segmentation_models_pytorch as smp


# -----------------------------------------------------------------------
# 1) SSL4EO-S12 weight indirme
# -----------------------------------------------------------------------
SSL4EO_HF_REPO = "wangyi111/SSL4EO-S12"
SSL4EO_DEFAULT_FILENAME = "B13_rn50_moco_0099_ckpt.pth"   # ResNet-50 MoCo, 13ch
DEFAULT_SSL4EO_CHANNELS = 13


def download_ssl4eo_weights(
    cache_dir: str | os.PathLike = "/models/pretrained",
    filename: str = SSL4EO_DEFAULT_FILENAME,
    repo_id: str = SSL4EO_HF_REPO,
) -> Path:
    """SSL4EO-S12 ResNet-50 MoCo agirligini HuggingFace'ten indir.

    Asenkron RUN-BLOCK ipucu (Colab):
        from huggingface_hub import hf_hub_download
        path = hf_hub_download(repo_id='wangyi111/SSL4EO-S12',
                               filename='B13_rn50_moco_0099_ckpt.pth',
                               cache_dir='/models/pretrained')
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise ImportError(
            "huggingface-hub gerekli. `pip install huggingface-hub` koş."
        ) from e

    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        cache_dir=str(cache_dir),
    )
    return Path(local_path)


# -----------------------------------------------------------------------
# 2) Multi-channel adapter (13 -> 17)
# -----------------------------------------------------------------------
def expand_first_conv(
    conv: nn.Conv2d,
    new_in_channels: int,
    src_channels: int = DEFAULT_SSL4EO_CHANNELS,
    init: str = "mean_replicate",
) -> nn.Conv2d:
    """SSL4EO-S12 ilk conv katmani (13 in_channels) -> N kanala genislet.

    Args:
        conv: SSL4EO pretrained ilk conv (Conv2d, in=13).
        new_in_channels: Hedef kanal sayisi (ARD'de 17).
        src_channels: Kaynak kanal sayisi (SSL4EO-S12'de 13).
        init: "mean_replicate" -> yeni kanal agirligi = mevcut kanallarin ortalamasi.
              "zero"           -> yeni kanal agirligi = 0 (linear probe icin guvenli).

    Notes:
        Yeni kanallar (S1 VV, S1 VH, DEM, slope) S2 reflectance'tan farkli
        statistige sahip. mean_replicate baslangici "agnostik" yapar; fine-tune
        ile bu agirliklar gradient yoluyla domain'e adapte olur.
        Referans: He et al. 2017 "Mask R-CNN" + Carreira & Zisserman 2017
        I3D weight-inflation tekniginin 2D analogu.
    """
    if conv.in_channels != src_channels:
        raise ValueError(
            f"Beklenen src_channels={src_channels}, conv.in_channels={conv.in_channels}"
        )
    if new_in_channels < src_channels:
        raise ValueError(
            f"new_in_channels ({new_in_channels}) < src_channels ({src_channels})"
        )

    new_conv = nn.Conv2d(
        in_channels=new_in_channels,
        out_channels=conv.out_channels,
        kernel_size=conv.kernel_size,
        stride=conv.stride,
        padding=conv.padding,
        dilation=conv.dilation,
        groups=conv.groups,
        bias=(conv.bias is not None),
    )

    with torch.no_grad():
        # Mevcut 13 bandi koru
        new_conv.weight[:, :src_channels] = conv.weight.clone()

        # Ek (new - src) kanal icin init
        n_extra = new_in_channels - src_channels
        if n_extra > 0:
            if init == "mean_replicate":
                # 13 SSL4EO bandinin ortalamasini her yeni kanala kopyala
                mean_w = conv.weight.mean(dim=1, keepdim=True)  # (out, 1, k, k)
                new_conv.weight[:, src_channels:] = mean_w.repeat(1, n_extra, 1, 1)
            elif init == "zero":
                new_conv.weight[:, src_channels:] = 0.0
            else:
                raise ValueError(f"Bilinmeyen init: {init}")

        if conv.bias is not None:
            new_conv.bias[:] = conv.bias.clone()

    return new_conv


def load_ssl4eo_resnet50_state_dict(ckpt_path: str | os.PathLike) -> dict:
    """SSL4EO-S12 MoCo checkpoint'inden ResNet-50 backbone state_dict'i cikar.

    SSL4EO-S12 MoCo .pth dosyasi typically anahtar olarak
    'state_dict' veya 'model' icerir. Encoder anahtarlari
    'module.encoder_q.0.<...>' veya 'encoder.<...>' formatinda.
    Bu fonksiyon farkli formatlari normalize eder.
    """
    raw = torch.load(str(ckpt_path), map_location="cpu")
    if isinstance(raw, dict) and "state_dict" in raw:
        sd = raw["state_dict"]
    elif isinstance(raw, dict) and "model" in raw:
        sd = raw["model"]
    else:
        sd = raw

    out = {}
    prefixes_to_strip = (
        "module.encoder_q.0.",
        "module.encoder_q.",
        "encoder_q.0.",
        "encoder_q.",
        "module.",
        "backbone.",
        "encoder.",
    )
    for k, v in sd.items():
        new_k = k
        for p in prefixes_to_strip:
            if new_k.startswith(p):
                new_k = new_k[len(p):]
                break
        # FC head'i at (segmentation icin gerek yok)
        if new_k.startswith("fc.") or new_k.startswith("classifier."):
            continue
        out[new_k] = v
    return out


# -----------------------------------------------------------------------
# 3) U-Net + SSL4EO-S12 backbone + 13->17 adapter
# -----------------------------------------------------------------------
def build_ssl4eo_unet(
    num_classes: int = 1,
    in_channels: int = 17,
    ssl4eo_ckpt: Optional[str | os.PathLike] = None,
    encoder_name: str = "resnet50",
    init: str = "mean_replicate",
    strict_load: bool = False,
) -> nn.Module:
    """SSL4EO-S12 pretrained ResNet-50 backbone'lu U-Net (17 kanal input).

    Args:
        num_classes : segmentation cikis kanali (1 -> binary pomza).
        in_channels : ARD kanal sayisi (default 17 = 13 S2 + VV + VH + DEM + slope).
        ssl4eo_ckpt : SSL4EO-S12 .pth dosyasi yolu (None ise random init).
        encoder_name: smp encoder ismi (resnet50 SSL4EO ile uyumlu).
        init        : adapter init stratejisi ("mean_replicate" | "zero").
        strict_load : state_dict yukleme strict mi?

    Returns:
        smp.Unet model. Egitim icin .train() ve cuda()'ya gec.
    """
    # Once 13 kanal olarak insa et (SSL4EO weights'i kolay yuklemek icin)
    model = smp.Unet(
        encoder_name=encoder_name,
        encoder_weights=None,
        in_channels=DEFAULT_SSL4EO_CHANNELS,
        classes=num_classes,
    )

    # SSL4EO-S12 backbone agirliklari yukle
    if ssl4eo_ckpt is not None and os.path.exists(str(ssl4eo_ckpt)):
        sd = load_ssl4eo_resnet50_state_dict(ssl4eo_ckpt)
        missing, unexpected = model.encoder.load_state_dict(sd, strict=strict_load)
        print(f"[SSL4EO] Yuklendi. Missing keys: {len(missing)}, Unexpected: {len(unexpected)}")
        if len(missing) > 0:
            print(f"[SSL4EO] Ornek missing: {missing[:5]}")
        if len(unexpected) > 0:
            print(f"[SSL4EO] Ornek unexpected: {unexpected[:5]}")
    else:
        print(f"[SSL4EO] UYARI: ckpt bulunamadi ({ssl4eo_ckpt}). Random init.")

    # Ilk conv'u 13 -> in_channels'e genislet
    if in_channels != DEFAULT_SSL4EO_CHANNELS:
        first_conv = model.encoder.conv1  # ResNet ilk conv
        new_first = expand_first_conv(
            first_conv,
            new_in_channels=in_channels,
            src_channels=DEFAULT_SSL4EO_CHANNELS,
            init=init,
        )
        model.encoder.conv1 = new_first
        print(f"[ADAPTER] conv1 genisletildi: {DEFAULT_SSL4EO_CHANNELS} -> {in_channels} ({init})")

    return model


# -----------------------------------------------------------------------
# 4) Quick sanity (script olarak calistirilirsa)
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, default=None,
                        help="SSL4EO-S12 .pth yolu (yoksa random init)")
    parser.add_argument("--in-channels", type=int, default=17)
    parser.add_argument("--device", type=str,
                        default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    device = torch.device(args.device)
    model = build_ssl4eo_unet(
        num_classes=1,
        in_channels=args.in_channels,
        ssl4eo_ckpt=args.ckpt,
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"Param sayisi : {n_params/1e6:.2f} M")

    x = torch.randn(2, args.in_channels, 256, 256, device=device)
    with torch.no_grad():
        y = model(x)
    print(f"Input  : {tuple(x.shape)}")
    print(f"Output : {tuple(y.shape)}")
    assert y.shape == (2, 1, 256, 256), "Output shape uyumsuz!"
    print("OK — SSL4EO-S12 + 13->17 adapter calisti.")
