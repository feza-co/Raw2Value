"""
P4 Audit-2 PASS-2 validation runner.
Outputs JSON results to stdout consumed by the auditor.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import xy
from rasterio.warp import transform as warp_transform
from scipy.stats import spearmanr

ROOT = Path(r"c:/Users/tuna9/OneDrive/Masaüstü/Pomzadoya")
PLOTS = ROOT / "reports" / "audit2_plots"
PLOTS.mkdir(parents=True, exist_ok=True)

# Ensure code/p4 is importable for fuse_confidence
sys.path.insert(0, str(ROOT / "code" / "p4"))
from fuse_confidence import fuse_confidence  # noqa: E402

RESULTS = {}


def stats(arr: np.ndarray, name: str) -> dict:
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return {"name": name, "valid_pct": 0.0, "n": 0}
    return {
        "name": name,
        "n_total": int(arr.size),
        "n_valid": int(valid.size),
        "valid_pct": round(float(valid.size) / float(arr.size) * 100, 3),
        "min": float(np.min(valid)),
        "max": float(np.max(valid)),
        "mean": float(np.mean(valid)),
        "median": float(np.median(valid)),
        "std": float(np.std(valid)),
        "p5": float(np.percentile(valid, 5)),
        "p25": float(np.percentile(valid, 25)),
        "p50": float(np.percentile(valid, 50)),
        "p75": float(np.percentile(valid, 75)),
        "p95": float(np.percentile(valid, 95)),
    }


def read_raster(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as src:
        a = src.read(1).astype(np.float32)
        nd = src.nodata
        if nd is not None and not (isinstance(nd, float) and np.isnan(nd)):
            a = np.where(a == nd, np.nan, a)
        prof = src.profile.copy()
        prof["transform"] = src.transform
        prof["crs"] = src.crs
        prof["bounds"] = src.bounds
    return a, prof


# ============= FAZ 1: distribution sanity =============
def faz1():
    out = {}

    qi, _ = read_raster(ROOT / "data/layers/aster_qi.tif")
    ci, _ = read_raster(ROOT / "data/layers/aster_ci.tif")
    ndvi, _ = read_raster(ROOT / "data/layers/s2_ndvi.tif")
    bsi, _ = read_raster(ROOT / "data/layers/s2_bsi.tif")
    albedo, _ = read_raster(ROOT / "data/layers/s2_albedo.tif")

    # ---- V1.1 QI ----
    s = stats(qi, "QI")
    # restrict the histogram view to the typical analytical range
    valid = qi[np.isfinite(qi)]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    clip_v = np.clip(valid, 0, 5)
    axs[0].hist(clip_v, bins=80, color="steelblue", edgecolor="white")
    axs[0].axvline(1.0, color="r", ls="--", label="QI=1 reference")
    axs[0].axvspan(0.5, 2.5, color="green", alpha=0.1, label="expected typical")
    axs[0].set_title("ASTER QI histogram (clipped to [0,5])")
    axs[0].set_xlabel("QI")
    axs[0].legend()
    axs[1].boxplot([clip_v], vert=True, showfliers=False)
    axs[1].set_title("QI boxplot (clipped to [0,5])")
    axs[1].set_ylabel("QI")
    plt.tight_layout()
    plt.savefig(PLOTS / "qi_distribution.png", dpi=120)
    plt.close()
    out["V1.1_QI"] = {"stats": s,
                      "expected": "valid_pct>70, 0.5<min, max<3.0, 0.9<median<1.4",
                      "plot": "reports/audit2_plots/qi_distribution.png"}

    # ---- V1.2 CI ----
    s = stats(ci, "CI")
    valid = ci[np.isfinite(ci)]
    fig, ax = plt.subplots(figsize=(8, 4))
    clip_v = np.clip(valid, 0.8, 1.3)
    ax.hist(clip_v, bins=80, color="darkorange", edgecolor="white")
    ax.axvspan(0.95, 1.05, color="green", alpha=0.15, label="expected median band")
    ax.axvline(1.0, color="r", ls="--", label="CI=1 reference")
    ax.set_title("ASTER CI histogram (clipped to [0.8,1.3])")
    ax.set_xlabel("CI")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "ci_distribution.png", dpi=120)
    plt.close()
    out["V1.2_CI"] = {"stats": s,
                      "expected": "0.95<median<1.05",
                      "plot": "reports/audit2_plots/ci_distribution.png"}

    # ---- V1.3 NDVI / BSI ----
    s_ndvi = stats(ndvi, "NDVI")
    s_bsi = stats(bsi, "BSI")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].hist(ndvi[np.isfinite(ndvi)], bins=80, color="green", edgecolor="white")
    axs[0].axvspan(0.05, 0.30, color="orange", alpha=0.15, label="Anatolia semi-arid typical")
    axs[0].set_title("S2 NDVI histogram")
    axs[0].set_xlabel("NDVI")
    axs[0].legend()
    axs[1].hist(bsi[np.isfinite(bsi)], bins=80, color="brown", edgecolor="white")
    axs[1].axvspan(0.0, 0.30, color="orange", alpha=0.15, label="bare-soil expected")
    axs[1].set_title("S2 BSI histogram")
    axs[1].set_xlabel("BSI")
    axs[1].legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "ndvi_bsi_distribution.png", dpi=120)
    plt.close()
    out["V1.3_NDVI_BSI"] = {"ndvi_stats": s_ndvi, "bsi_stats": s_bsi,
                            "expected": "NDVI median 0.05-0.30 (semi-arid), BSI -0.4..0.6 typical, mean ~0.05-0.20",
                            "plot": "reports/audit2_plots/ndvi_bsi_distribution.png"}

    # ---- V1.4 NaN / NoData ----
    layers = {
        "aster_qi": ROOT / "data/layers/aster_qi.tif",
        "aster_ci": ROOT / "data/layers/aster_ci.tif",
        "aster_sio2": ROOT / "data/layers/aster_sio2.tif",
        "aster_qi_20m": ROOT / "data/layers/aster_qi_20m.tif",
        "aster_ci_20m": ROOT / "data/layers/aster_ci_20m.tif",
        "s2_ndvi": ROOT / "data/layers/s2_ndvi.tif",
        "s2_bsi": ROOT / "data/layers/s2_bsi.tif",
        "s2_albedo": ROOT / "data/layers/s2_albedo.tif",
        "s2_sabins": ROOT / "data/layers/s2_sabins.tif",
        "dem_aspect": ROOT / "data/layers/dem_aspect.tif",
        "dem_hillshade": ROOT / "data/layers/dem_hillshade.tif",
        "final_confidence": ROOT / "data/layers/final_confidence.tif",
    }
    nan_table = {}
    names, valid_pcts = [], []
    for k, p in layers.items():
        a, _ = read_raster(p)
        finite = np.isfinite(a)
        v = float(finite.sum()) / float(a.size) * 100
        nan_table[k] = round(v, 2)
        names.append(k); valid_pcts.append(v)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(names, valid_pcts, color="teal")
    ax.axhline(70, color="r", ls="--", label="70% threshold")
    ax.set_xticklabels(names, rotation=40, ha="right")
    ax.set_ylabel("valid pixel %")
    ax.set_title("Per-layer valid (non-NaN) percentage")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "nan_per_layer.png", dpi=120)
    plt.close()
    out["V1.4_NaN"] = {"valid_pct": nan_table,
                       "expected": "all >70% (ASTER ~65% accepted because of TIR scene crop)",
                       "plot": "reports/audit2_plots/nan_per_layer.png"}

    return out


# ============= FAZ 2: ground-truth poly validation =============
GROUND_POINTS = [
    ("Firat_Madencilik", 38.584923, 34.720928, "A"),
    ("Huseyin_Oyman_Mazi", 38.469950, 34.892810, "A-"),
    ("Metin_Sertkaya", 38.496806, 34.824545, "B"),
    ("Elit_Bims", 38.488288, 34.912612, "B"),
    ("Huseyin_Oyman_2601", 38.545056, 34.824968, "B+"),
    ("OzSA", 38.597449, 34.703774, "B"),
    ("Inci", 38.460562, 34.837528, "C"),
    ("Serhat", 38.548220, 34.705544, "B"),
    ("ANC", 38.522847, 34.823008, "B-"),
]


def make_pomza_mask(template_path: Path, radius_m: float = 300.0) -> tuple[np.ndarray, np.ndarray]:
    """Build a synthetic mask: True where pixel is within `radius_m` of any pomza point.
    Returns (pomza_mask, background_mask) with the same shape as template raster.
    background_mask = valid & not within 1500m of pomza points.
    """
    with rasterio.open(template_path) as src:
        H, W = src.height, src.width
        tr = src.transform
        crs_dst = src.crs
        a = src.read(1).astype(np.float32)
        nd = src.nodata

    finite = np.isfinite(a)
    if nd is not None and not (isinstance(nd, float) and np.isnan(nd)):
        finite &= (a != nd)

    # Project lat/lon (EPSG:4326) -> raster CRS
    lons = [pt[2] for pt in GROUND_POINTS]
    lats = [pt[1] for pt in GROUND_POINTS]
    xs, ys = warp_transform("EPSG:4326", crs_dst, lons, lats)
    px = np.array([(x - tr.c) / tr.a for x in xs])
    py = np.array([(y - tr.f) / tr.e for y in ys])

    # Build distance grid via min over points (small N -> ok in O(N*HW))
    yy, xx = np.indices((H, W))
    pomza = np.zeros((H, W), dtype=bool)
    near_buffer = np.zeros((H, W), dtype=bool)
    res = abs(tr.a)
    rad_px = radius_m / res
    buf_px = 1500.0 / res
    for cx, cy in zip(px, py):
        if cx < -2*buf_px or cy < -2*buf_px or cx > W + 2*buf_px or cy > H + 2*buf_px:
            continue
        dx = xx - cx
        dy = yy - cy
        d2 = dx * dx + dy * dy
        pomza |= d2 <= rad_px * rad_px
        near_buffer |= d2 <= buf_px * buf_px

    pomza_m = pomza & finite
    bg_m = (~near_buffer) & finite
    return pomza_m, bg_m


def faz2():
    out = {}
    qi_path = ROOT / "data/layers/aster_qi_20m.tif"
    ci_path = ROOT / "data/layers/aster_ci_20m.tif"
    ndvi_path = ROOT / "data/layers/s2_ndvi.tif"
    bsi_path = ROOT / "data/layers/s2_bsi.tif"

    pmask, bgmask = make_pomza_mask(qi_path, radius_m=300.0)
    n_pomza = int(pmask.sum())
    n_bg = int(bgmask.sum())
    out["mask_summary"] = {"pomza_px": n_pomza, "background_px": n_bg, "radius_m": 300.0}

    qi, _ = read_raster(qi_path)
    ci, _ = read_raster(ci_path)
    ndvi, _ = read_raster(ndvi_path)
    bsi, _ = read_raster(bsi_path)

    def cmp_stats(arr, label):
        p = arr[pmask]; b = arr[bgmask]
        p = p[np.isfinite(p)]; b = b[np.isfinite(b)]
        return {
            "label": label,
            "pomza_n": int(p.size), "bg_n": int(b.size),
            "pomza_median": float(np.median(p)) if p.size else None,
            "pomza_mean": float(np.mean(p)) if p.size else None,
            "bg_median": float(np.median(b)) if b.size else None,
            "bg_mean": float(np.mean(b)) if b.size else None,
            "delta_median": float(np.median(p) - np.median(b)) if p.size and b.size else None,
        }

    s_qi = cmp_stats(qi, "QI")
    s_ci = cmp_stats(ci, "CI")
    s_ndvi = cmp_stats(ndvi, "NDVI")
    s_bsi = cmp_stats(bsi, "BSI")

    # plot 4-panel comparison
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for ax, arr, label, expected in [
        (axs[0, 0], qi, "QI", "pomza > bg"),
        (axs[0, 1], ci, "CI", "pomza ~ bg"),
        (axs[1, 0], ndvi, "NDVI", "pomza < 0.15"),
        (axs[1, 1], bsi, "BSI", "pomza > 0.05"),
    ]:
        p = arr[pmask]; b = arr[bgmask]
        p = p[np.isfinite(p)]; b = b[np.isfinite(b)]
        if label == "QI":
            p = np.clip(p, 0, 5); b = np.clip(b, 0, 5)
        if label == "CI":
            p = np.clip(p, 0.8, 1.3); b = np.clip(b, 0.8, 1.3)
        ax.hist(b, bins=60, color="gray", alpha=0.55, density=True, label=f"background n={b.size}")
        ax.hist(p, bins=60, color="crimson", alpha=0.65, density=True, label=f"pomza n={p.size}")
        ax.set_title(f"{label} | {expected}")
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(PLOTS / "groundtruth_pomza_vs_bg.png", dpi=120)
    plt.close()

    out["V2.1_QI"] = {"stats": s_qi, "expected": "pomza_median > bg_median (QI > 1.0 inside)",
                      "plot": "reports/audit2_plots/groundtruth_pomza_vs_bg.png"}
    out["V2.2_CI"] = {"stats": s_ci, "expected": "pomza_median ~ bg_median (no carbonate signal)"}
    out["V2.3_NDVI_BSI"] = {"ndvi": s_ndvi, "bsi": s_bsi,
                            "expected": "NDVI<0.15 pomza, BSI>0.05 pomza"}
    return out


# ============= FAZ 3: cross-sensor =============
def faz3():
    out = {}
    qi20, _ = read_raster(ROOT / "data/layers/aster_qi_20m.tif")
    bsi, _ = read_raster(ROOT / "data/layers/s2_bsi.tif")
    ndvi, _ = read_raster(ROOT / "data/layers/s2_ndvi.tif")

    # Subsample + finite mask
    rng = np.random.default_rng(42)
    finite = np.isfinite(qi20) & np.isfinite(bsi) & np.isfinite(ndvi)
    idx = np.flatnonzero(finite.ravel())
    if idx.size > 200000:
        idx = rng.choice(idx, 200000, replace=False)

    q = qi20.ravel()[idx]
    b = bsi.ravel()[idx]
    n = ndvi.ravel()[idx]

    # clip QI extremes for robust correlation
    q_clipped = np.clip(q, np.percentile(q, 1), np.percentile(q, 99))

    r_qb, p_qb = spearmanr(q_clipped, b)
    r_qn, p_qn = spearmanr(q_clipped, n)
    out["V3.1_QI_BSI"] = {"r": float(r_qb), "p": float(p_qb), "n": int(idx.size),
                          "expected": "r > 0.15 (positive)"}
    out["V3.2_QI_NDVI"] = {"r": float(r_qn), "p": float(p_qn), "n": int(idx.size),
                            "expected": "r < -0.10 (negative)"}

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    sub = rng.choice(np.arange(idx.size), 8000, replace=False)
    axs[0].scatter(q_clipped[sub], b[sub], s=2, alpha=0.25, color="teal")
    axs[0].set_title(f"QI vs BSI Spearman r={r_qb:+.3f}")
    axs[0].set_xlabel("ASTER QI (20m, clipped)"); axs[0].set_ylabel("S2 BSI")
    axs[1].scatter(q_clipped[sub], n[sub], s=2, alpha=0.25, color="darkgreen")
    axs[1].set_title(f"QI vs NDVI Spearman r={r_qn:+.3f}")
    axs[1].set_xlabel("ASTER QI (20m, clipped)"); axs[1].set_ylabel("S2 NDVI")
    plt.tight_layout()
    plt.savefig(PLOTS / "cross_sensor_corr.png", dpi=120)
    plt.close()
    out["plot"] = "reports/audit2_plots/cross_sensor_corr.png"

    # ---- V3.3 spatial alignment ----
    with rasterio.open(ROOT / "data/ard/s2_ard_20m.tif") as a:
        sa_shape = (a.height, a.width)
        sa_bounds = list(a.bounds)
        sa_crs = str(a.crs)
    with rasterio.open(ROOT / "data/layers/aster_qi_20m.tif") as a:
        aq_shape = (a.height, a.width)
        aq_bounds = list(a.bounds)
        aq_crs = str(a.crs)
    out["V3.3_alignment"] = {
        "s2_ard_20m": {"shape": sa_shape, "bounds": sa_bounds, "crs": sa_crs},
        "aster_qi_20m": {"shape": aq_shape, "bounds": aq_bounds, "crs": aq_crs},
        "match_shape": sa_shape == aq_shape,
        "match_bounds": all(abs(a - b) < 1e-3 for a, b in zip(sa_bounds, aq_bounds)),
        "match_crs": sa_crs == aq_crs,
    }
    return out


# ============= FAZ 4: DEM bias =============
def faz4():
    out = {}
    aspect, _ = read_raster(ROOT / "data/layers/dem_aspect.tif")
    albedo, _ = read_raster(ROOT / "data/layers/s2_albedo.tif")

    # north slope: 315<=aspect<=360 OR 0<=aspect<=45
    # south slope: 135<=aspect<=225
    finite = np.isfinite(aspect) & np.isfinite(albedo)
    north_m = ((aspect >= 315) | (aspect <= 45)) & finite
    south_m = ((aspect >= 135) & (aspect <= 225)) & finite
    al_n = albedo[north_m]
    al_s = albedo[south_m]
    out["V4.1_north_vs_south_albedo"] = {
        "n_north": int(north_m.sum()), "n_south": int(south_m.sum()),
        "north_median": float(np.median(al_n)),
        "south_median": float(np.median(al_s)),
        "south_minus_north": float(np.median(al_s) - np.median(al_n)),
        "expected": "south slopes brighter on sunlit (acquisition geometry); |delta| < 0.05",
    }

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(np.clip(al_n, 0, 0.8), bins=80, alpha=0.55, color="navy", label=f"north n={al_n.size}", density=True)
    ax.hist(np.clip(al_s, 0, 0.8), bins=80, alpha=0.55, color="orange", label=f"south n={al_s.size}", density=True)
    ax.set_title("Albedo distribution by slope aspect (N vs S)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "dem_aspect_albedo_bias.png", dpi=120)
    plt.close()
    out["plot"] = "reports/audit2_plots/dem_aspect_albedo_bias.png"
    return out


# ============= FAZ 5: fusion prototype sanity =============
def faz5():
    out = {}
    qi, _ = read_raster(ROOT / "data/layers/aster_qi_20m.tif")
    ci, _ = read_raster(ROOT / "data/layers/aster_ci_20m.tif")
    H, W = qi.shape

    def run_scenario(raw_val, label, inject_nan=False):
        if inject_nan:
            raw = np.full((H, W), raw_val, dtype=np.float32)
            raw[100:200, 100:200] = np.nan
        else:
            raw = np.full((H, W), raw_val, dtype=np.float32)
        f = fuse_confidence(raw, qi, ci)
        s = stats(f, label)
        # check NaN block
        nan_block = int(np.sum(~np.isfinite(f[100:200, 100:200])))
        return s, nan_block, f

    sA, _, fA = run_scenario(0.9, "scenarioA_raw=0.9")
    sB, _, fB = run_scenario(0.1, "scenarioB_raw=0.1")
    sC, nan_block, fC = run_scenario(0.5, "scenarioC_NaN_block", inject_nan=True)

    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    for ax, arr, title in [
        (axs[0], fA, "A: raw=0.9"),
        (axs[1], fB, "B: raw=0.1"),
        (axs[2], fC, "C: raw=0.5 + 100x100 NaN"),
    ]:
        v = arr[np.isfinite(arr)]
        ax.hist(v, bins=80, color="purple", edgecolor="white")
        ax.set_title(f"fuse {title} median={np.median(v):.3f}")
        ax.set_xlabel("final confidence")
    plt.tight_layout()
    plt.savefig(PLOTS / "fusion_proto_scenarios.png", dpi=120)
    plt.close()

    out["V5.1_A"] = {"stats": sA, "expected": "median 0.4-0.7"}
    out["V5.1_B"] = {"stats": sB, "expected": "median < 0.15"}
    out["V5.1_C"] = {"stats": sC, "expected": "100x100 block all NaN (10000 px)",
                      "nan_block_count": nan_block,
                      "expected_nan_block": 10000}
    out["plot"] = "reports/audit2_plots/fusion_proto_scenarios.png"
    return out


def main():
    RESULTS["faz1"] = faz1()
    RESULTS["faz2"] = faz2()
    RESULTS["faz3"] = faz3()
    RESULTS["faz4"] = faz4()
    RESULTS["faz5"] = faz5()
    out_path = ROOT / "agent_outputs" / "_audit2_results.json"
    out_path.write_text(json.dumps(RESULTS, indent=2, default=str), encoding="utf-8")
    print(json.dumps(RESULTS, indent=2, default=str))


if __name__ == "__main__":
    main()
