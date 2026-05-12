"""
timescale.py

Derives empirical scaling laws for time to singleton emergence.

Sweeps: alpha, initial gap, N, and beta_low.
Fits power-law relationships. Goal: a formula t* = f(alpha, gap, N, beta)
that makes the theorem quantitatively predictive.

Metrics:
  t_10x:  time until leader/second ratio > 10
  t_100x: time until leader/second ratio > 100
  t_dom:  time until leader resource share > 99%
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
import os

FIGURES = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES, exist_ok=True)

BG = '#0a0a0a'
FG = '#e0e0e0'
ACCENT = '#ff6b35'
GRID = '#1e1e1e'

S_CAP = 1e9
T_MAX = 600.0


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a2a')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def sigmoid_beta(beta_low, beta_high=0.5, threshold=3.0, steepness=5.0):
    def fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))
    return fn


def ode_n_agent(y, alpha, beta_fns):
    n = len(y)
    S = np.maximum(y, 1e-12)
    powers = S ** alpha
    denom = powers.sum()
    shares = powers / denom
    betas = np.array([beta_fns[i](S[i]) for i in range(n)])
    dS = S ** (1.0 - betas) * shares
    return dS


def run(S0_arr, alpha, beta_fns, t_max=T_MAX):
    n = len(S0_arr)

    def ode(t, y):
        return ode_n_agent(y, alpha, beta_fns).tolist()

    def cap_ev(t, y):
        return max(y) - S_CAP
    cap_ev.terminal = True
    cap_ev.direction = 1

    return solve_ivp(ode, [0, t_max], list(S0_arr),
                     events=cap_ev, max_step=0.05, rtol=1e-7, atol=1e-9)


def measure_timescales(sol, alpha, ratio_targets=(10.0, 100.0), dom_threshold=0.99):
    S = np.maximum(sol.y, 1e-12)
    t = sol.t

    # ratio timescales
    sorted_S = np.sort(S, axis=0)[::-1]
    ratio = sorted_S[0] / sorted_S[1]

    results = {}
    for target in ratio_targets:
        idx = np.argmax(ratio >= target)
        results[f't_{int(target)}x'] = t[idx] if ratio[-1] >= target else None

    # dominance timescale
    powers = S ** alpha
    leader_share = powers.max(axis=0) / powers.sum(axis=0)
    idx_dom = np.argmax(leader_share >= dom_threshold)
    results['t_dom'] = t[idx_dom] if leader_share[-1] >= dom_threshold else None

    return results


def run_trial(alpha, gap, N, beta_low, threshold=3.0, n_trials=5, rng=None):
    """Average timescales over n_trials random initial conditions."""
    if rng is None:
        rng = np.random.default_rng(42)
    beta_fn = sigmoid_beta(beta_low, threshold=threshold)

    t10_list, t100_list, tdom_list = [], [], []

    for _ in range(n_trials):
        base = 1.0
        S0 = base + rng.uniform(0, gap * base, N)
        S0[0] = base + gap  # ensure at least one agent has full gap advantage
        S0 = np.sort(S0)[::-1]

        sol = run(S0, alpha, [beta_fn] * N)
        ts = measure_timescales(sol, alpha)

        if ts['t_10x'] is not None:
            t10_list.append(ts['t_10x'])
        if ts['t_100x'] is not None:
            t100_list.append(ts['t_100x'])
        if ts['t_dom'] is not None:
            tdom_list.append(ts['t_dom'])

    return (
        np.mean(t10_list) if t10_list else None,
        np.mean(t100_list) if t100_list else None,
        np.mean(tdom_list) if tdom_list else None,
    )


# ── Sweep 1: alpha ─────────────────────────────────────────────────────────────

def sweep_alpha():
    alphas = np.linspace(0.3, 2.5, 14)
    rng = np.random.default_rng(1)

    t10, t100, tdom = [], [], []
    for a in alphas:
        r = run_trial(alpha=a, gap=0.1, N=2, beta_low=-0.3, rng=rng)
        t10.append(r[0])
        t100.append(r[1])
        tdom.append(r[2])

    valid = [(a, t, td) for a, t, td in zip(alphas, t10, tdom) if t is not None and td is not None]
    av, tv, tdv = zip(*valid) if valid else ([], [], [])

    print(f"  {'alpha':>7}  {'t_10x':>8}  {'t_100x':>9}  {'t_dom':>8}")
    for a, t10v, t100v, tdv2 in zip(alphas, t10, t100, tdom):
        t10s = f"{t10v:.1f}" if t10v else "  >max"
        t100s = f"{t100v:.1f}" if t100v else "  >max"
        tds = f"{tdv2:.1f}" if tdv2 else "  >max"
        print(f"  {a:>7.2f}  {t10s:>8}  {t100s:>9}  {tds:>8}")

    # Fit power law: t ~ C * alpha^k
    if len(av) >= 4:
        def power_law(x, C, k):
            return C * np.array(x) ** k
        try:
            popt_t10, _ = curve_fit(power_law, av, tv, p0=[10.0, -1.0], maxfev=5000)
            popt_dom, _ = curve_fit(power_law, av, tdv, p0=[100.0, -1.0], maxfev=5000)
            print(f"\n  Fit t_10x  ~ {popt_t10[0]:.2f} * alpha^{popt_t10[1]:.3f}")
            print(f"  Fit t_dom  ~ {popt_dom[0]:.2f} * alpha^{popt_dom[1]:.3f}")
            return alphas, t10, tdom, popt_t10, popt_dom
        except Exception as e:
            print(f"  Fit failed: {e}")

    return alphas, t10, tdom, None, None


# ── Sweep 2: initial gap ───────────────────────────────────────────────────────

def sweep_gap():
    gaps = np.logspace(-2, 0, 16)  # 0.01 to 1.0
    rng = np.random.default_rng(2)

    t10, t100, tdom = [], [], []
    for gap in gaps:
        r = run_trial(alpha=1.0, gap=gap, N=2, beta_low=-0.3, rng=rng)
        t10.append(r[0])
        t100.append(r[1])
        tdom.append(r[2])

    valid = [(g, t, td) for g, t, td in zip(gaps, t10, tdom) if t is not None and td is not None]
    gv, tv, tdv = zip(*valid) if valid else ([], [], [])

    print(f"  {'gap':>7}  {'t_10x':>8}  {'t_100x':>9}  {'t_dom':>8}")
    for g, t10v, t100v, tdv2 in zip(gaps, t10, t100, tdom):
        t10s = f"{t10v:.1f}" if t10v else "  >max"
        t100s = f"{t100v:.1f}" if t100v else "  >max"
        tds = f"{tdv2:.1f}" if tdv2 else "  >max"
        print(f"  {g:>7.3f}  {t10s:>8}  {t100s:>9}  {tds:>8}")

    if len(gv) >= 4:
        def power_law(x, C, k):
            return C * np.array(x) ** k
        try:
            popt_t10, _ = curve_fit(power_law, gv, tv, p0=[5.0, -0.5], maxfev=5000)
            popt_dom, _ = curve_fit(power_law, gv, tdv, p0=[50.0, -0.5], maxfev=5000)
            print(f"\n  Fit t_10x  ~ {popt_t10[0]:.2f} * gap^{popt_t10[1]:.3f}")
            print(f"  Fit t_dom  ~ {popt_dom[0]:.2f} * gap^{popt_dom[1]:.3f}")
            return gaps, t10, tdom, popt_t10, popt_dom
        except Exception as e:
            print(f"  Fit failed: {e}")

    return gaps, t10, tdom, None, None


# ── Sweep 3: N agents ──────────────────────────────────────────────────────────

def sweep_N():
    Ns = [2, 3, 5, 8, 10, 15, 20]
    rng = np.random.default_rng(3)

    t10, t100, tdom = [], [], []
    for N in Ns:
        r = run_trial(alpha=1.0, gap=0.1, N=N, beta_low=-0.3, rng=rng)
        t10.append(r[0])
        t100.append(r[1])
        tdom.append(r[2])

    valid = [(N, t, td) for N, t, td in zip(Ns, t10, tdom) if t is not None and td is not None]
    Nv, tv, tdv = zip(*valid) if valid else ([], [], [])

    print(f"  {'N':>4}  {'t_10x':>8}  {'t_100x':>9}  {'t_dom':>8}")
    for N, t10v, t100v, tdv2 in zip(Ns, t10, t100, tdom):
        t10s = f"{t10v:.1f}" if t10v else "  >max"
        t100s = f"{t100v:.1f}" if t100v else "  >max"
        tds = f"{tdv2:.1f}" if tdv2 else "  >max"
        print(f"  {N:>4}  {t10s:>8}  {t100s:>9}  {tds:>8}")

    if len(Nv) >= 4:
        def power_law(x, C, k):
            return C * np.array(x) ** k
        try:
            popt_t10, _ = curve_fit(power_law, Nv, tv, p0=[5.0, 0.5], maxfev=5000)
            popt_dom, _ = curve_fit(power_law, Nv, tdv, p0=[50.0, 0.5], maxfev=5000)
            print(f"\n  Fit t_10x  ~ {popt_t10[0]:.2f} * N^{popt_t10[1]:.3f}")
            print(f"  Fit t_dom  ~ {popt_dom[0]:.2f} * N^{popt_dom[1]:.3f}")
            return Ns, t10, tdom, popt_t10, popt_dom
        except Exception as e:
            print(f"  Fit failed: {e}")

    return Ns, t10, tdom, None, None


# ── Sweep 4: beta_low ──────────────────────────────────────────────────────────

def sweep_beta_low():
    beta_lows = np.linspace(-0.05, -1.0, 14)
    rng = np.random.default_rng(4)

    t10, t100, tdom = [], [], []
    for bl in beta_lows:
        r = run_trial(alpha=1.0, gap=0.1, N=2, beta_low=bl, rng=rng)
        t10.append(r[0])
        t100.append(r[1])
        tdom.append(r[2])

    valid = [(bl, t, td) for bl, t, td in zip(beta_lows, t10, tdom) if t is not None and td is not None]
    blv, tv, tdv = zip(*valid) if valid else ([], [], [])

    print(f"  {'beta_low':>9}  {'t_10x':>8}  {'t_100x':>9}  {'t_dom':>8}")
    for bl, t10v, t100v, tdv2 in zip(beta_lows, t10, t100, tdom):
        t10s = f"{t10v:.1f}" if t10v else "  >max"
        t100s = f"{t100v:.1f}" if t100v else "  >max"
        tds = f"{tdv2:.1f}" if tdv2 else "  >max"
        print(f"  {bl:>9.3f}  {t10s:>8}  {t100s:>9}  {tds:>8}")

    if len(blv) >= 4:
        # Use |beta_low| for power law
        abs_bl = [-b for b in blv]
        def power_law(x, C, k):
            return C * np.array(x) ** k
        try:
            popt_t10, _ = curve_fit(power_law, abs_bl, tv, p0=[5.0, -0.5], maxfev=5000)
            popt_dom, _ = curve_fit(power_law, abs_bl, tdv, p0=[50.0, -0.5], maxfev=5000)
            print(f"\n  Fit t_10x  ~ {popt_t10[0]:.2f} * |beta_low|^{popt_t10[1]:.3f}")
            print(f"  Fit t_dom  ~ {popt_dom[0]:.2f} * |beta_low|^{popt_dom[1]:.3f}")
            return beta_lows, t10, tdom, popt_t10, popt_dom
        except Exception as e:
            print(f"  Fit failed: {e}")

    return beta_lows, t10, tdom, None, None


# ── Plot all sweeps ────────────────────────────────────────────────────────────

def plot_sweeps(alpha_res, gap_res, N_res, beta_res):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        style_ax(ax)

    def plot_one(ax, x, t10, tdom, fit10, fitdom, xlabel, log_x=False):
        valid10 = [(xi, ti) for xi, ti in zip(x, t10) if ti is not None]
        validdom = [(xi, ti) for xi, ti in zip(x, tdom) if ti is not None]
        if valid10:
            xv, tv = zip(*valid10)
            ax.plot(xv, tv, color=ACCENT, marker='o', markersize=5, linewidth=1.6, label='t_10x')
        if validdom:
            xv, tv = zip(*validdom)
            ax.plot(xv, tv, color='#2ca02c', marker='s', markersize=5, linewidth=1.6, label='t_dom (99%)')

        if fit10 is not None and len(valid10) >= 4:
            x_fit = np.linspace(min(xv), max(xv), 100)
            ax.plot(x_fit, fit10[0] * x_fit ** fit10[1], color=ACCENT,
                    linestyle='--', linewidth=1, alpha=0.6,
                    label=f'fit: {fit10[0]:.1f}·x^{fit10[1]:.2f}')
        if fitdom is not None and len(validdom) >= 4:
            x_fit = np.linspace(min(xv), max(xv), 100)
            ax.plot(x_fit, fitdom[0] * x_fit ** fitdom[1], color='#2ca02c',
                    linestyle='--', linewidth=1, alpha=0.6,
                    label=f'fit: {fitdom[0]:.1f}·x^{fitdom[1]:.2f}')

        if log_x:
            ax.set_xscale('log')
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Time')
        ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    alphas, t10_a, tdom_a, fit10_a, fitdom_a = alpha_res
    plot_one(axes[0, 0], alphas, t10_a, tdom_a, fit10_a, fitdom_a, 'Alpha')
    axes[0, 0].set_title('Timescale vs alpha')

    gaps, t10_g, tdom_g, fit10_g, fitdom_g = gap_res
    plot_one(axes[0, 1], gaps, t10_g, tdom_g, fit10_g, fitdom_g, 'Initial gap', log_x=True)
    axes[0, 1].set_title('Timescale vs initial gap')

    Ns, t10_N, tdom_N, fit10_N, fitdom_N = N_res
    plot_one(axes[1, 0], Ns, t10_N, tdom_N, fit10_N, fitdom_N, 'N (agents)')
    axes[1, 0].set_title('Timescale vs N')

    beta_lows, t10_b, tdom_b, fit10_b, fitdom_b = beta_res
    abs_bl = [-b for b in beta_lows]
    plot_one(axes[1, 1], abs_bl, t10_b, tdom_b, fit10_b, fitdom_b, '|beta_low|', log_x=True)
    axes[1, 1].set_title('Timescale vs |beta_low|')

    plt.suptitle('Singleton emergence timescale — parameter sweeps', color=FG, fontsize=11)
    plt.tight_layout()
    path = os.path.join(FIGURES, 'timescale_sweeps.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"\n  Saved: {path}")


# ── Combined scaling formula ───────────────────────────────────────────────────

def combined_formula(alpha_res, gap_res, N_res, beta_res):
    """
    Assemble the separate fits into a combined formula:
    t_10x ~ C * alpha^a * gap^b * N^c * |beta_low|^d
    """
    print("\n  Combined scaling formula:")

    _, _, _, fit10_a, _ = alpha_res
    _, _, _, fit10_g, _ = gap_res
    _, _, _, fit10_N, _ = N_res
    _, _, _, fit10_b, _ = beta_res

    parts = []
    if fit10_a is not None:
        parts.append(f"alpha^{fit10_a[1]:.2f}")
    if fit10_g is not None:
        parts.append(f"gap^{fit10_g[1]:.2f}")
    if fit10_N is not None:
        parts.append(f"N^{fit10_N[1]:.2f}")
    if fit10_b is not None:
        parts.append(f"|beta_low|^{fit10_b[1]:.2f}")

    if parts:
        print(f"  t_10x ~ C * {' * '.join(parts)}")
        print(f"  (C absorbs threshold position and beta_high; fits are independent single-variable)")
    else:
        print("  Insufficient fit data for combined formula")


if __name__ == '__main__':
    print("=== Timescale Scaling Analysis ===\n")

    print("Sweep 1: Alpha (gap=0.1, N=2, beta_low=-0.3)")
    alpha_res = sweep_alpha()

    print("\nSweep 2: Initial gap (alpha=1.0, N=2, beta_low=-0.3)")
    gap_res = sweep_gap()

    print("\nSweep 3: N agents (alpha=1.0, gap=0.1, beta_low=-0.3)")
    N_res = sweep_N()

    print("\nSweep 4: beta_low depth (alpha=1.0, gap=0.1, N=2)")
    beta_res = sweep_beta_low()

    plot_sweeps(alpha_res, gap_res, N_res, beta_res)
    combined_formula(alpha_res, gap_res, N_res, beta_res)

    print("\nDone.")
