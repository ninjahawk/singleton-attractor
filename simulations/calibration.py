"""
calibration.py

Empirical calibration of beta(S) to frontier-AI training compute.

Treats S = training compute (FLOP) as a capability proxy.
For each year, takes the running maximum compute (the "frontier") and
estimates the local growth exponent beta from the model
    dS/dt = c * S^(1 - beta)
in log-log form: log(dS/dt) = log(c) + (1 - beta) * log(S).

Reports beta estimate, 95% confidence interval, residual structure, and
sub-window estimates (2012-2018, 2018-2022, 2022-2025).

Output: data/epoch/beta_estimates.json plus a figure.
"""

from __future__ import annotations

import csv
import json
import math
import os
from datetime import datetime
from typing import List, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "epoch")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
OUT_JSON = os.path.join(DATA_DIR, "beta_estimates.json")
os.makedirs(FIG_DIR, exist_ok=True)


def parse_date(s: str) -> float:
    s = s.strip()
    if not s:
        return float("nan")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            d = datetime.strptime(s, fmt)
            year = d.year + (d.timetuple().tm_yday - 1) / 365.25
            return year
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


def load_compute(path: str) -> List[Tuple[float, float, str]]:
    """Returns list of (year, log10_flop, model_name) for usable rows."""
    out = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = parse_date(row.get("Publication date", ""))
            flop = parse_float(row.get("Training compute (FLOP)", ""))
            if math.isnan(year) or math.isnan(flop) or flop <= 0:
                continue
            out.append((year, math.log10(flop), row.get("Model", "")))
    out.sort(key=lambda r: r[0])
    return out


def frontier_curve(rows: List[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
    """Running maximum of log10 compute over time."""
    front = []
    best = -float("inf")
    best_name = ""
    for year, lc, name in rows:
        if lc > best:
            best = lc
            best_name = name
            front.append((year, lc, name))
    return front


def fit_beta(years: np.ndarray, log10_S: np.ndarray) -> dict:
    """
    Fit dS/dt = c * S^(1-beta), i.e. d(ln S)/dt = c * S^(-beta).

    In ln-space let y = ln S. Then dy/dt = c * exp(-beta * y).
    Take ln: ln(dy/dt) = ln(c) - beta * y.
    Linear regression of ln(dy/dt) on y gives slope = -beta.

    Returns slope, intercept, beta, sigma_beta (asymptotic), R^2, n.
    """
    y = log10_S * math.log(10.0)  # ln S
    # numerical derivative dy/dt via finite differences
    if len(years) < 3:
        return {"n": int(len(years)), "ok": False}
    dy_dt = np.gradient(y, years)
    valid = (dy_dt > 0) & np.isfinite(dy_dt)
    if valid.sum() < 3:
        return {"n": int(valid.sum()), "ok": False}
    y_v = y[valid]
    ln_dy = np.log(dy_dt[valid])
    # OLS
    X = np.vstack([np.ones_like(y_v), y_v]).T
    coef, residuals, rank, sv = np.linalg.lstsq(X, ln_dy, rcond=None)
    intercept, slope = coef
    yhat = X @ coef
    resid = ln_dy - yhat
    n = len(y_v)
    if n > 2:
        sigma2 = float(np.sum(resid ** 2) / (n - 2))
        XtX_inv = np.linalg.inv(X.T @ X)
        se_slope = math.sqrt(sigma2 * XtX_inv[1, 1])
    else:
        se_slope = float("nan")
    ss_tot = float(np.sum((ln_dy - ln_dy.mean()) ** 2))
    ss_res = float(np.sum(resid ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    beta = -slope
    se_beta = se_slope
    ci95 = (beta - 1.96 * se_beta, beta + 1.96 * se_beta)
    return {
        "n": int(n),
        "ok": True,
        "beta": float(beta),
        "se_beta": float(se_beta),
        "ci95": [float(ci95[0]), float(ci95[1])],
        "intercept_ln_c": float(intercept),
        "r_squared": float(r2),
        "slope": float(slope),
    }


def windowed_fits(rows: List[Tuple[float, float, str]], windows: List[Tuple[float, float]]) -> dict:
    out = {}
    for lo, hi in windows:
        sub = [(y, s, n) for (y, s, n) in rows if lo <= y < hi]
        if len(sub) < 3:
            out[f"{int(lo)}-{int(hi)}"] = {"n": len(sub), "ok": False}
            continue
        years = np.array([r[0] for r in sub])
        log10S = np.array([r[1] for r in sub])
        out[f"{int(lo)}-{int(hi)}"] = fit_beta(years, log10S)
    return out


def _fit_quadratic(t: np.ndarray, y: np.ndarray):
    X = np.vstack([np.ones_like(t), t, t * t]).T
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef, X


def bootstrap_ci_gamma(
    years: np.ndarray,
    log10_S: np.ndarray,
    n_boot: int = 5000,
    seed: int = 20260513,
) -> dict:
    """
    Block bootstrap of the curvature gamma in log10(S) = a + b*t + gamma*t^2.

    Frontier records are unevenly spaced in time and may have correlated
    residuals (a single architectural breakthrough can create several
    record-setters in quick succession). The asymptotic OLS CI assumes
    IID residuals; bootstrapping the (year, log10_S) pairs gives a more
    honest interval.
    """
    rng = np.random.default_rng(seed)
    n = len(years)
    if n < 4:
        return {"ok": False, "n": n}
    gammas = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, size=n)
        ts = years[idx] - years[idx].mean()
        ys = log10_S[idx]
        try:
            coef, _ = _fit_quadratic(ts, ys)
            gammas[k] = coef[2]
        except np.linalg.LinAlgError:
            gammas[k] = np.nan
    gammas = gammas[np.isfinite(gammas)]
    lo, hi = np.quantile(gammas, [0.025, 0.975])
    return {
        "ok": True,
        "n_boot": int(len(gammas)),
        "gamma_mean": float(np.mean(gammas)),
        "gamma_median": float(np.median(gammas)),
        "ci95_boot": [float(lo), float(hi)],
        "frac_positive": float((gammas > 0).mean()),
    }


def fit_polynomial_growth(years: np.ndarray, log10_S: np.ndarray) -> dict:
    """
    Fit log10(S) = a + b*t + gamma*t^2.

    If d(log10 S)/dt = b + 2*gamma*t (growing in t) then growth is
    super-exponential, corresponding to beta < 0.
    Specifically: dS/dt = c * S^(1-beta) implies, in log10 S vs t,
    the trajectory is concave-up (beta < 0) or concave-down (beta > 0)
    or linear (beta = 0).

    Returns gamma (curvature), asymptotic 95% CI, bootstrap 95% CI, R^2.
    """
    t = years - years.mean()  # center for numerical stability
    coef, X = _fit_quadratic(t, log10_S)
    a, b, gamma = coef
    yhat = X @ coef
    resid = log10_S - yhat
    n = len(t)
    sigma2 = float(np.sum(resid ** 2) / (n - 3)) if n > 3 else float("nan")
    XtX_inv = np.linalg.inv(X.T @ X)
    se_gamma = math.sqrt(sigma2 * XtX_inv[2, 2])
    ss_tot = float(np.sum((log10_S - log10_S.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid ** 2)) / ss_tot if ss_tot > 0 else float("nan")
    # convert: rate at end of window = b + 2*gamma*(t_end - t_mean)
    rate_end = b + 2.0 * gamma * (years.max() - years.mean())
    rate_start = b + 2.0 * gamma * (years.min() - years.mean())
    boot = bootstrap_ci_gamma(years, log10_S)
    return {
        "n": int(n),
        "ok": True,
        "a_intercept_log10S_at_mean_year": float(a),
        "b_log10_per_year_at_mean_year": float(b),
        "gamma_curvature": float(gamma),
        "se_gamma_asymptotic": float(se_gamma),
        "ci95_gamma_asymptotic": [float(gamma - 1.96 * se_gamma), float(gamma + 1.96 * se_gamma)],
        "ci95_gamma_bootstrap": boot.get("ci95_boot"),
        "bootstrap_n": boot.get("n_boot"),
        "bootstrap_frac_positive": boot.get("frac_positive"),
        "r_squared": float(r2),
        "doubling_time_years_at_start": float(math.log10(2) / rate_start) if rate_start > 0 else None,
        "doubling_time_years_at_end": float(math.log10(2) / rate_end) if rate_end > 0 else None,
        "interpretation": (
            "accelerating (super-exponential, beta<0)" if gamma > 0
            else "decelerating (sub-exponential, beta>0)" if gamma < 0
            else "exponential (beta=0)"
        ),
        "mean_year": float(years.mean()),
    }


def main():
    front_path = os.path.join(DATA_DIR, "frontier_ai_models.csv")
    notable_path = os.path.join(DATA_DIR, "notable_ai_models.csv")

    print("Loading frontier dataset...")
    front_rows = load_compute(front_path)
    print(f"  {len(front_rows)} rows with usable date+compute")

    print("Loading notable dataset...")
    notable_rows = load_compute(notable_path)
    print(f"  {len(notable_rows)} rows with usable date+compute")

    # Frontier curve = running max within frontier dataset
    frontier_front = frontier_curve(front_rows)
    print(f"Frontier curve: {len(frontier_front)} record-setters")

    # Frontier curve from notable (broader) for comparison
    notable_frontier = frontier_curve(notable_rows)
    print(f"Notable-derived frontier: {len(notable_frontier)} record-setters")

    # Pick the broader frontier (notable derived) as primary
    primary = notable_frontier
    years = np.array([r[0] for r in primary])
    log10S = np.array([r[1] for r in primary])

    print("\nFull-window fit (notable-derived frontier):")
    full = fit_beta(years, log10S)
    print(json.dumps(full, indent=2))

    print("\nSub-window fits:")
    windows = [
        (2010.0, 2018.0),
        (2018.0, 2022.0),
        (2022.0, 2026.5),
        (2012.0, 2026.5),
    ]
    win = windowed_fits(primary, windows)
    print(json.dumps(win, indent=2))

    # Frontier-dataset fit for comparison
    frontier_only = fit_beta(
        np.array([r[0] for r in frontier_front]),
        np.array([r[1] for r in frontier_front]),
    )

    # Polynomial-in-time fits (more robust than numerical differentiation).
    poly_windows = [
        (2010.0, 2018.0),
        (2018.0, 2022.0),
        (2022.0, 2026.5),
        (2012.0, 2026.5),
        (2010.0, 2026.5),
    ]
    poly_fits = {}
    for lo, hi in poly_windows:
        sub = [(y, s, n) for (y, s, n) in primary if lo <= y < hi]
        if len(sub) < 4:
            poly_fits[f"{int(lo)}-{int(hi)}"] = {"n": len(sub), "ok": False}
            continue
        poly_fits[f"{int(lo)}-{int(hi)}"] = fit_polynomial_growth(
            np.array([r[0] for r in sub]),
            np.array([r[1] for r in sub]),
        )

    print("\nPolynomial-in-time fits (curvature gamma; gamma>0 means beta<0):")
    print(json.dumps(poly_fits, indent=2))

    out = {
        "primary_frontier_source": "notable_ai_models.csv (running max)",
        "n_frontier_steps": len(primary),
        "full_window_fit": full,
        "frontier_dataset_fit": frontier_only,
        "windowed_power_law_fits": win,
        "polynomial_in_time_fits": poly_fits,
        "earliest_year": float(primary[0][0]) if primary else None,
        "latest_year": float(primary[-1][0]) if primary else None,
        "earliest_log10_flop": float(primary[0][1]) if primary else None,
        "latest_log10_flop": float(primary[-1][1]) if primary else None,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {OUT_JSON}")

    # --------- figure ---------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    ax = axes[0]
    ax.scatter(
        [r[0] for r in notable_rows],
        [r[1] for r in notable_rows],
        s=4,
        alpha=0.18,
        color="#888",
        label="all notable models",
    )
    ax.plot(
        [r[0] for r in primary],
        [r[1] for r in primary],
        "o-",
        ms=3,
        lw=1.0,
        color="#ff6b35",
        label="frontier (running max)",
    )
    ax.set_xlabel("Publication year")
    ax.set_ylabel("log$_{10}$(training compute / FLOP)")
    ax.set_title("Frontier training compute, 1950–present")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)

    # second panel: ln(dy/dt) vs y for the frontier — shows slope = -beta
    y = log10S * math.log(10.0)
    dy = np.gradient(y, years)
    valid = (dy > 0) & np.isfinite(dy)
    ax2 = axes[1]
    ax2.scatter(y[valid], np.log(dy[valid]), s=12, color="#ff6b35")
    if full.get("ok"):
        yy = np.linspace(y[valid].min(), y[valid].max(), 50)
        ax2.plot(yy, full["intercept_ln_c"] + full["slope"] * yy, "k--", lw=1)
        ax2.set_title(
            f"Fit: ln(dy/dt) vs ln S\n"
            f"β = {full['beta']:.3f} (95% CI [{full['ci95'][0]:.3f}, {full['ci95'][1]:.3f}]),  "
            f"R² = {full['r_squared']:.3f},  n = {full['n']}"
        )
    ax2.set_xlabel("ln S")
    ax2.set_ylabel("ln (dy/dt)")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    out_png = os.path.join(FIG_DIR, "calibration_beta.png")
    plt.savefig(out_png, dpi=120, bbox_inches="tight")
    print(f"Wrote {out_png}")


if __name__ == "__main__":
    main()
