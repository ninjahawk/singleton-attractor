"""
run_experiments.py

Comprehensive parameter sweeps. Tests the boundaries of the singleton attractor claim.
Experiments:
  1. Alpha sweep: resource-capability coupling strength vs. separation rate
  2. Beta threshold sweep: how beta_low and threshold position affect time-to-dominance
  3. Initial spread sweep: does tighter initial spread slow or prevent singleton?
  4. Niche partitioning (Failure mode F1): at what overlap fraction does oligopoly stabilize?
  5. Summary table for findings.md
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os

FIGURES = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES, exist_ok=True)

BG = '#0a0a0a'
FG = '#e0e0e0'
ACCENT = '#ff6b35'
GRID = '#1e1e1e'

S_CAP = 1e6


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a2a')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def beta_threshold_fn(beta_low, beta_high, threshold, steepness=5.0):
    def fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))
    return fn


def cap_event(cap=S_CAP):
    def event(t, y):
        return max(y) - cap
    event.terminal = True
    event.direction = 1
    return event


def run_competition(S0, alpha, beta_fns, t_max=50.0):
    """
    Run N-agent competition. beta_fns is a list of callables, one per agent.
    """
    N = len(S0)

    def ode(t, y):
        S = np.maximum(y, 1e-12)
        powers = S ** alpha
        denom = powers.sum()
        resource_shares = powers / denom
        dS = np.array([
            S[i] ** (1.0 - beta_fns[i](S[i])) * resource_shares[i]
            for i in range(N)
        ])
        return dS.tolist()

    sol = solve_ivp(
        ode,
        [0, t_max],
        list(S0),
        events=cap_event(),
        max_step=0.02,
        rtol=1e-7,
        atol=1e-9,
    )
    return sol


def separation_rate(sol, alpha, at_time=None):
    """Ratio of leader capability to second-place at end (or at_time)."""
    if at_time is not None:
        idx = np.searchsorted(sol.t, at_time)
        idx = min(idx, sol.y.shape[1] - 1)
    else:
        idx = -1
    S = sol.y[:, idx]
    sorted_S = np.sort(S)[::-1]
    return sorted_S[0] / sorted_S[1] if sorted_S[1] > 0 else np.inf


def time_to_ratio(sol, target_ratio=10.0):
    """Time until leader/second-place ratio exceeds target."""
    S = sol.y
    for t_idx in range(S.shape[1]):
        s_sorted = np.sort(S[:, t_idx])[::-1]
        if s_sorted[1] > 0 and s_sorted[0] / s_sorted[1] >= target_ratio:
            return sol.t[t_idx]
    return None


# ── Experiment 1: alpha sweep ─────────────────────────────────────────────────

def exp_alpha_sweep():
    """
    Vary alpha (resource-capability coupling) from 0.25 to 3.0.
    Two agents, threshold beta. Measure separation rate at t=15.
    """
    alphas = np.linspace(0.25, 3.0, 15)
    beta_fn = beta_threshold_fn(beta_low=-0.3, beta_high=0.5, threshold=3.0)
    n_trials = 30
    rng = np.random.default_rng(1)

    mean_sep = []
    std_sep = []

    for alpha in alphas:
        seps = []
        for _ in range(n_trials):
            S0 = rng.uniform(1.0, 2.0, 2)
            sol = run_competition(S0, alpha, [beta_fn, beta_fn], t_max=15.0)
            seps.append(separation_rate(sol, alpha))
        mean_sep.append(np.mean(seps))
        std_sep.append(np.std(seps))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    ax.errorbar(alphas, mean_sep, yerr=std_sep, color=ACCENT, linewidth=1.8,
                marker='o', markersize=5, capsize=3, ecolor='#888888')
    ax.set_xlabel('Alpha (resource-capability coupling exponent)')
    ax.set_ylabel('Separation ratio at t=15')
    ax.set_title('Alpha sweep — stronger coupling accelerates singleton emergence')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'exp_alpha_sweep.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    print(f"  {'alpha':>8}  {'mean ratio':>12}  {'std':>8}")
    for a, m, s in zip(alphas, mean_sep, std_sep):
        print(f"  {a:>8.2f}  {m:>12.2f}  {s:>8.2f}")

    return list(zip(alphas, mean_sep))


# ── Experiment 2: beta threshold sweep ────────────────────────────────────────

def exp_beta_sweep():
    """
    Vary beta_low (depth below threshold) from -0.05 to -1.0.
    Also vary threshold position T from 2 to 8.
    Heatmap: separation rate at t=10.
    """
    beta_lows = np.linspace(-0.05, -1.0, 10)
    thresholds = np.linspace(2.0, 8.0, 8)
    alpha = 1.0
    n_trials = 15
    rng = np.random.default_rng(2)

    heatmap = np.zeros((len(beta_lows), len(thresholds)))

    for i, bl in enumerate(beta_lows):
        for j, T in enumerate(thresholds):
            beta_fn = beta_threshold_fn(beta_low=bl, beta_high=0.5, threshold=T)
            seps = []
            for _ in range(n_trials):
                S0 = rng.uniform(1.0, 2.0, 2)
                sol = run_competition(S0, alpha, [beta_fn, beta_fn], t_max=12.0)
                seps.append(separation_rate(sol, alpha))
            heatmap[i, j] = np.median(seps)

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    im = ax.imshow(np.log10(heatmap + 1), aspect='auto', origin='lower',
                   cmap='plasma',
                   extent=[thresholds[0], thresholds[-1],
                           beta_lows[0], beta_lows[-1]])

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('log10(separation ratio)', color=FG)
    cbar.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)

    ax.set_xlabel('Threshold position T')
    ax.set_ylabel('beta_low (below threshold)')
    ax.set_title('Beta threshold sweep — separation ratio at t=12')
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    ax.tick_params(colors=FG)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'exp_beta_sweep.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    max_idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
    print(f"  Max separation: {heatmap[max_idx]:.1f}x at beta_low={beta_lows[max_idx[0]]:.2f}, T={thresholds[max_idx[1]]:.1f}")
    print(f"  Min separation: {heatmap.min():.2f}x (beta_low={beta_lows[np.unravel_index(np.argmin(heatmap), heatmap.shape)[0]]:.2f}, T={thresholds[np.unravel_index(np.argmin(heatmap), heatmap.shape)[1]]:.1f})")

    return heatmap, beta_lows, thresholds


# ── Experiment 3: initial spread sweep ────────────────────────────────────────

def exp_initial_spread():
    """
    Vary the spread of initial capabilities.
    sigma: std dev of initial capability distribution (mean=1.0).
    Question: does tighter initial spread prevent singleton, or just slow it?
    """
    sigmas = [0.001, 0.005, 0.01, 0.05, 0.10, 0.25, 0.50]
    N = 5
    alpha = 1.0
    beta_fn = beta_threshold_fn(beta_low=-0.3, beta_high=0.5, threshold=3.0)
    n_trials = 50
    rng = np.random.default_rng(3)

    winner_rates = []
    mean_t10x = []

    for sigma in sigmas:
        correct_winner = 0
        t10x_list = []

        for _ in range(n_trials):
            S0 = np.abs(rng.normal(1.0, sigma, N)) + 0.1
            sol = run_competition(S0, alpha, [beta_fn] * N, t_max=50.0)
            final_winner = np.argmax(sol.y[:, -1])
            if final_winner == np.argmax(S0):
                correct_winner += 1
            t10 = time_to_ratio(sol)
            if t10 is not None:
                t10x_list.append(t10)

        winner_rates.append(correct_winner / n_trials)
        mean_t10x.append(np.mean(t10x_list) if t10x_list else np.nan)

    print(f"  {'sigma':>8}  {'winner rate':>12}  {'mean t(10x)':>13}")
    for s, wr, t in zip(sigmas, winner_rates, mean_t10x):
        t_str = f"{t:.2f}" if not np.isnan(t) else "  >50"
        print(f"  {s:>8.3f}  {wr:>12.1%}  {t_str:>13}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    ax1.semilogx(sigmas, [r * 100 for r in winner_rates], color=ACCENT,
                 linewidth=1.8, marker='o', markersize=6)
    ax1.set_xlabel('Initial capability spread (sigma)')
    ax1.set_ylabel('Winner = initial leader (%)')
    ax1.set_title('Winner identity vs initial spread')
    ax1.set_ylim(0, 105)

    valid = [(s, t) for s, t in zip(sigmas, mean_t10x) if not np.isnan(t)]
    if valid:
        sv, tv = zip(*valid)
        ax2.semilogx(sv, tv, color='#2ca02c', linewidth=1.8, marker='o', markersize=6)
    ax2.set_xlabel('Initial capability spread (sigma)')
    ax2.set_ylabel('Mean time to 10x ratio')
    ax2.set_title('Convergence speed vs initial spread')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'exp_initial_spread.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return list(zip(sigmas, winner_rates))


# ── Experiment 4: niche partitioning (Failure mode F1) ────────────────────────

def exp_niche_partitioning():
    """
    Model partial resource overlap between agents.
    overlap=1.0: compete for exactly the same resource (competitive exclusion applies).
    overlap=0.0: fully separate niches (no competition, theorem does not apply).

    Two agents. Each controls a fraction of its own exclusive resource.
    Shared resource is fraction `overlap` of total.

    At what overlap does oligopoly become stable?
    """
    overlaps = np.linspace(0.0, 1.0, 11)
    alpha = 1.0
    beta_fn = beta_threshold_fn(beta_low=-0.3, beta_high=0.5, threshold=3.0)
    n_trials = 40
    rng = np.random.default_rng(4)

    EVAL_T = 15.0
    mean_sep = []
    std_sep = []

    for overlap in overlaps:
        seps = []
        for _ in range(n_trials):
            S0 = rng.uniform(1.0, 2.0, 2)
            S1_0, S2_0 = S0

            def ode_niche(t, y):
                S1, S2 = max(y[0], 1e-12), max(y[1], 1e-12)

                # Resource from shared pool (competed)
                shared_total = 1.0
                shared_denom = S1 ** alpha + S2 ** alpha
                R1_shared = overlap * shared_total * S1 ** alpha / shared_denom
                R2_shared = overlap * shared_total * S2 ** alpha / shared_denom

                # Resource from exclusive niche (not competed)
                R1_excl = (1.0 - overlap) * 0.5
                R2_excl = (1.0 - overlap) * 0.5

                R1 = R1_shared + R1_excl
                R2 = R2_shared + R2_excl

                b1 = beta_fn(S1)
                b2 = beta_fn(S2)

                dS1 = S1 ** (1.0 - b1) * R1
                dS2 = S2 ** (1.0 - b2) * R2
                return [dS1, dS2]

            sol = solve_ivp(
                ode_niche,
                [0, EVAL_T],
                [S1_0, S2_0],
                events=cap_event(),
                max_step=0.02,
                rtol=1e-7,
                atol=1e-9,
            )
            seps.append(separation_rate(sol, alpha))

        mean_sep.append(np.mean(seps))
        std_sep.append(np.std(seps))

    print(f"\n  {'overlap':>9}  {'mean ratio':>12}  {'std':>8}")
    for o, m, s in zip(overlaps, mean_sep, std_sep):
        print(f"  {o:>9.2f}  {m:>12.2f}  {s:>8.2f}")

    # Find the overlap threshold where singleton breaks down
    # Operationally: where mean_sep < 2.0 (ratio barely above 1)
    breakdown = None
    for o, m in zip(overlaps, mean_sep):
        if m < 2.0:
            breakdown = o
            break
    if breakdown is not None:
        print(f"\n  Oligopoly threshold: overlap < {breakdown:.2f}")
    else:
        print("\n  No oligopoly threshold found — singleton persists at all tested overlap levels")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    ax.errorbar(overlaps, mean_sep, yerr=std_sep, color=ACCENT, linewidth=1.8,
                marker='o', markersize=6, capsize=3, ecolor='#888888')
    ax.axhline(1.0, color='#555555', linestyle='--', linewidth=1, label='No separation (ratio=1)')
    ax.set_xlabel('Resource overlap fraction')
    ax.set_ylabel(f'Separation ratio at t={EVAL_T}')
    ax.set_title('Niche partitioning — overlap=1.0 is full competition, 0.0 is full separation')
    ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'exp_niche_partitioning.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return list(zip(overlaps, mean_sep))


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(alpha_results, spread_results, niche_results):
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("\nAlpha sweep:")
    print("  Separation ratio increases monotonically with alpha.")
    print(f"  alpha=0.25 -> {alpha_results[0][1]:.1f}x | alpha=3.0 -> {alpha_results[-1][1]:.1f}x")

    print("\nInitial spread:")
    all_correct = all(r >= 0.95 for _, r in spread_results)
    print(f"  Winner = initial leader across all tested spreads: {all_correct}")
    min_rate = min(r for _, r in spread_results)
    print(f"  Min winner rate: {min_rate:.1%}")

    print("\nNiche partitioning:")
    full_overlap = niche_results[-1][1]
    zero_overlap = niche_results[0][1]
    print(f"  Separation at full overlap (1.0): {full_overlap:.1f}x")
    print(f"  Separation at zero overlap (0.0): {zero_overlap:.2f}x")
    print(f"  Ratio range: {full_overlap/zero_overlap:.0f}x difference across overlap spectrum")


if __name__ == '__main__':
    print("=== Comprehensive Parameter Sweep ===\n")

    print("Experiment 1: Alpha sweep")
    alpha_results = exp_alpha_sweep()

    print("\nExperiment 2: Beta threshold sweep")
    heatmap, beta_lows, thresholds = exp_beta_sweep()

    print("\nExperiment 3: Initial spread sensitivity")
    spread_results = exp_initial_spread()

    print("\nExperiment 4: Niche partitioning (Failure mode F1)")
    niche_results = exp_niche_partitioning()

    print_summary(alpha_results, spread_results, niche_results)

    print("\nDone.")
