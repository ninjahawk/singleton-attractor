"""
benchmark_calibration.py

Empirical calibration of beta(S) using benchmark-performance proxies,
not just training compute. Complements simulations/calibration.py.

Method:
  - Load Epoch's benchmark datasets (gpqa, frontiermath, arc-agi, ...).
  - For each benchmark: build the frontier (running max of best score over
    release date).
  - Convert score -> capability via S = -log10(1 - score). This is unbounded
    as score -> 1, mirroring the unbounded-S assumption of the Yudkowsky
    growth equation. Raw scores saturate at 1; the transform doesn't.
  - Fit log10(S(t)) = a + b*t + gamma*t^2 on the transformed frontier.
  - Bootstrap CI on gamma (5000 draws, fixed seed).

Output: data/epoch/benchmark_beta_estimates.json + figure.
"""

from __future__ import annotations

import csv
import json
import math
import os
from datetime import datetime
from typing import List, Tuple, Dict

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "epoch", "benchmarks")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
OUT_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "epoch", "benchmark_beta_estimates.json")
os.makedirs(FIG_DIR, exist_ok=True)

# Benchmarks chosen for: multi-year coverage, public frontier-model evaluation,
# nontrivial ceiling (not yet saturated at 1.0 across the period).
BENCHMARKS = [
    ("gpqa_diamond.csv", "GPQA Diamond"),
    ("frontiermath.csv", "FrontierMath"),
    ("arc_agi_external.csv", "ARC-AGI"),
    ("swe_bench_verified.csv", "SWE-bench Verified"),
    ("math_level_5.csv", "MATH Level 5"),
]

EPS = 1e-3  # avoid log(0) when score = 1 exactly


def parse_date(s: str) -> float:
    s = s.strip()
    if not s:
        return float("nan")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            d = datetime.strptime(s, fmt)
            return d.year + (d.timetuple().tm_yday - 1) / 365.25
        except ValueError:
            continue
    return float("nan")


def parse_float(s: str) -> float:
    s = s.strip()
    if not s:
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


SCORE_COLS = ["Best score (across scorers)", "mean_score", "Score", "score", "best_score"]


def load_benchmark(path: str) -> List[Tuple[float, float, str]]:
    """Returns (year, score, model) rows with usable date+score."""
    out = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = parse_date(row.get("Release date", ""))
            score = float("nan")
            for col in SCORE_COLS:
                v = parse_float(row.get(col, ""))
                if not math.isnan(v):
                    score = v
                    break
            if math.isnan(year) or math.isnan(score):
                continue
            if score < 0 or score > 1:
                continue
            out.append((year, score, row.get("Model version", "")))
    out.sort(key=lambda r: r[0])
    return out


def frontier(rows):
    """Running maximum of score over time."""
    best = -float("inf")
    front = []
    for y, s, m in rows:
        if s > best:
            best = s
            front.append((y, s, m))
    return front


def transform_to_capability(score: float) -> float:
    """S = -log10(1 - score + EPS). Unbounded as score -> 1."""
    return -math.log10(max(1.0 - score, EPS))


def fit_quadratic(t: np.ndarray, y: np.ndarray):
    X = np.vstack([np.ones_like(t), t, t * t]).T
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef, X


def bootstrap_gamma(years: np.ndarray, log10S: np.ndarray, n_boot: int = 5000, seed: int = 20260513) -> dict:
    rng = np.random.default_rng(seed)
    n = len(years)
    if n < 4:
        return {"ok": False}
    gammas = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, size=n)
        ts = years[idx] - years[idx].mean()
        ys = log10S[idx]
        try:
            coef, _ = fit_quadratic(ts, ys)
            gammas[k] = coef[2]
        except np.linalg.LinAlgError:
            gammas[k] = np.nan
    gammas = gammas[np.isfinite(gammas)]
    lo, hi = np.quantile(gammas, [0.025, 0.975])
    return {
        "ok": True,
        "n_boot": int(len(gammas)),
        "ci95": [float(lo), float(hi)],
        "frac_positive": float((gammas > 0).mean()),
    }


def fit_one_benchmark(name: str, rows: List[Tuple[float, float, str]]) -> Dict:
    front = frontier(rows)
    if len(front) < 4:
        return {"ok": False, "reason": "fewer than 4 frontier records", "n_frontier": len(front)}

    years = np.array([r[0] for r in front])
    scores = np.array([r[1] for r in front])
    capability = np.array([transform_to_capability(s) for s in scores])
    log10_cap = np.log10(np.maximum(capability, 1e-6))

    # Fit polynomial in time
    t_centered = years - years.mean()
    coef, X = fit_quadratic(t_centered, log10_cap)
    a, b, gamma = coef
    yhat = X @ coef
    resid = log10_cap - yhat
    n = len(years)
    sigma2 = float(np.sum(resid ** 2) / max(n - 3, 1))
    XtX_inv = np.linalg.inv(X.T @ X)
    se_gamma = math.sqrt(sigma2 * XtX_inv[2, 2])
    ss_tot = float(np.sum((log10_cap - log10_cap.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid ** 2)) / ss_tot if ss_tot > 0 else float("nan")

    boot = bootstrap_gamma(years, log10_cap)

    return {
        "ok": True,
        "name": name,
        "n_total": len(rows),
        "n_frontier": int(n),
        "year_range": [float(years.min()), float(years.max())],
        "score_range": [float(scores.min()), float(scores.max())],
        "gamma": float(gamma),
        "ci95_asymptotic": [float(gamma - 1.96 * se_gamma), float(gamma + 1.96 * se_gamma)],
        "ci95_bootstrap": boot.get("ci95"),
        "bootstrap_frac_positive": boot.get("frac_positive"),
        "r_squared": float(r2),
        "doubling_time_capability_years_at_end": (
            float(math.log10(2) / (b + 2.0 * gamma * (years.max() - years.mean())))
            if (b + 2.0 * gamma * (years.max() - years.mean())) > 0
            else None
        ),
        "transform": "S = -log10(1 - score)",
    }


def main():
    results = {}
    panels = []

    for fname, label in BENCHMARKS:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"SKIP {label}: file not found")
            continue
        rows = load_benchmark(path)
        print(f"{label}: {len(rows)} rows usable")
        result = fit_one_benchmark(label, rows)
        results[fname] = result
        if result.get("ok"):
            panels.append((label, rows, frontier(rows), result))
            print(
                f"  gamma={result['gamma']:+.3f}, "
                f"asym CI=[{result['ci95_asymptotic'][0]:+.3f}, {result['ci95_asymptotic'][1]:+.3f}], "
                f"boot CI=[{result['ci95_bootstrap'][0]:+.3f}, {result['ci95_bootstrap'][1]:+.3f}], "
                f"P(g>0)={result['bootstrap_frac_positive']:.2f}, "
                f"R2={result['r_squared']:.3f}, "
                f"n_front={result['n_frontier']}"
            )

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUT_JSON}")

    # Figure: one panel per benchmark
    n_panels = len(panels)
    if n_panels == 0:
        print("No panels to plot.")
        return
    cols = min(3, n_panels)
    rows_n = (n_panels + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols, figsize=(4.2 * cols, 3.4 * rows_n), squeeze=False)
    for ax_idx, (label, all_rows, front, result) in enumerate(panels):
        r, c = divmod(ax_idx, cols)
        ax = axes[r][c]
        ax.scatter(
            [x[0] for x in all_rows],
            [x[1] for x in all_rows],
            s=10,
            alpha=0.25,
            color="#888",
            label="all evals",
        )
        ax.plot(
            [x[0] for x in front],
            [x[1] for x in front],
            "o-",
            ms=3,
            lw=1.0,
            color="#ff6b35",
            label="frontier",
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Score")
        ax.set_ylim(-0.02, 1.02)
        title = (
            f"{label}\n"
            f"$\\gamma$={result['gamma']:+.2f}, "
            f"$P(\\gamma>0)$={result['bootstrap_frac_positive']:.2f}, "
            f"n={result['n_frontier']}"
        )
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="lower right")

    # turn off any leftover axes
    for ax_idx in range(n_panels, rows_n * cols):
        r, c = divmod(ax_idx, cols)
        axes[r][c].axis("off")

    plt.tight_layout()
    out_png = os.path.join(FIG_DIR, "calibration_benchmarks.png")
    plt.savefig(out_png, dpi=120, bbox_inches="tight", facecolor="white")
    print(f"Wrote {out_png}")


if __name__ == "__main__":
    main()
