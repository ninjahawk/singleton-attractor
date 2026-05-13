"""
stochastic.py

Tests OQ3: does stochastic noise affect whether a singleton emerges?

Model: multiplicative noise on capability dynamics
  dS_i = S_i^(1-beta) * (R_i/R_max) dt + sigma * S_i * dW_i

Euler-Maruyama integration (standard for multiplicative SDEs).

Questions:
  1. At what noise level does winner identity start to change?
  2. Does noise prevent singleton emergence (ratio still diverges)?
  3. At very high noise, do agents sometimes flip outcomes?
  4. Is there a noise threshold above which the theorem breaks?
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

FIGURES = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES, exist_ok=True)

BG = 'white'
FG = 'black'
ACCENT = '#ff6b35'
GRID = '#cccccc'


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#888888')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def sigmoid_beta(beta_low, beta_high, threshold, steepness=5.0):
    def fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))
    return fn


def euler_maruyama(S1_0, S2_0, alpha, beta_fn, sigma, dt=0.005, t_max=20.0, rng=None):
    """
    Two-agent Euler-Maruyama SDE integration.
    Returns final (S1, S2) and time series.
    """
    if rng is None:
        rng = np.random.default_rng()

    n_steps = int(t_max / dt)
    sqrt_dt = np.sqrt(dt)
    S_CAP = 1e8

    S1, S2 = S1_0, S2_0
    t_series = np.zeros(n_steps + 1)
    S1_series = np.zeros(n_steps + 1)
    S2_series = np.zeros(n_steps + 1)
    t_series[0] = 0
    S1_series[0] = S1
    S2_series[0] = S2

    for i in range(n_steps):
        S1 = max(S1, 1e-12)
        S2 = max(S2, 1e-12)

        denom = S1 ** alpha + S2 ** alpha
        r1 = S1 ** alpha / denom
        r2 = S2 ** alpha / denom

        b1 = beta_fn(S1)
        b2 = beta_fn(S2)

        drift1 = S1 ** (1.0 - b1) * r1
        drift2 = S2 ** (1.0 - b2) * r2

        noise1 = sigma * S1 * rng.standard_normal() * sqrt_dt
        noise2 = sigma * S2 * rng.standard_normal() * sqrt_dt

        S1 = S1 + drift1 * dt + noise1
        S2 = S2 + drift2 * dt + noise2

        S1 = max(S1, 1e-12)
        S2 = max(S2, 1e-12)

        t_series[i + 1] = (i + 1) * dt
        S1_series[i + 1] = S1
        S2_series[i + 1] = S2

        if max(S1, S2) > S_CAP:
            t_series = t_series[:i + 2]
            S1_series = S1_series[:i + 2]
            S2_series = S2_series[:i + 2]
            break

    return t_series, S1_series, S2_series


# ── Experiment 1: sample trajectories at different noise levels ───────────────

def exp_sample_trajectories():
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S1_0, S2_0 = 1.1, 1.0

    sigmas = [0.0, 0.05, 0.15, 0.30]
    rng = np.random.default_rng(42)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        style_ax(ax)

    for ax, sigma in zip(axes.flat, sigmas):
        # Run 5 sample trajectories
        for trial in range(5):
            t, S1, S2 = euler_maruyama(S1_0, S2_0, alpha, beta_fn, sigma,
                                        dt=0.005, t_max=20.0, rng=rng)
            ax.semilogy(t, S1, color=ACCENT, linewidth=0.8, alpha=0.7)
            ax.semilogy(t, S2, color='#1f77b4', linewidth=0.8, alpha=0.7)

        ax.set_title(f'sigma={sigma} — orange=Agent1, blue=Agent2')
        ax.set_xlabel('Time')
        ax.set_ylabel('Capability log')

    plt.suptitle('Stochastic trajectories at varying noise levels', color=FG, fontsize=11)
    plt.tight_layout()
    path = os.path.join(FIGURES, 'stoch_trajectories.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


# ── Experiment 2: winner rate vs noise level ──────────────────────────────────

def exp_winner_rate(n_trials=300):
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S1_0, S2_0 = 1.1, 1.0
    rng = np.random.default_rng(0)

    sigmas = np.logspace(-3, 0, 20)  # 0.001 to 1.0
    winner_rates = []
    singleton_rates = []  # fraction where final ratio > 10
    mean_ratios = []

    for sigma in sigmas:
        wins = 0
        singletons = 0
        ratios = []
        for _ in range(n_trials):
            t, S1, S2 = euler_maruyama(S1_0, S2_0, alpha, beta_fn, sigma,
                                        dt=0.005, t_max=20.0, rng=rng)
            S1f, S2f = S1[-1], S2[-1]
            if S1f > S2f:
                wins += 1
            ratio = S1f / S2f if S2f > 0 else np.inf
            if ratio > 10.0 or ratio < 0.1:
                singletons += 1
            ratios.append(ratio)

        winner_rates.append(wins / n_trials)
        singleton_rates.append(singletons / n_trials)
        mean_ratios.append(np.median(ratios))

    print(f"\n  {'sigma':>8}  {'winner rate':>12}  {'singleton rate':>15}  {'median ratio':>13}")
    for s, wr, sr, mr in zip(sigmas, winner_rates, singleton_rates, mean_ratios):
        print(f"  {s:>8.4f}  {wr:>12.1%}  {sr:>15.1%}  {mr:>13.2f}")

    # Find noise threshold where winner rate drops below 60%
    threshold_noise = None
    for s, wr in zip(sigmas, winner_rates):
        if wr < 0.60:
            threshold_noise = s
            break
    if threshold_noise:
        print(f"\n  Winner rate drops below 60% at sigma ~ {threshold_noise:.4f}")
    else:
        print(f"\n  Winner rate stays above 60% across all tested noise levels")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    ax1.semilogx(sigmas, [r * 100 for r in winner_rates], color=ACCENT,
                 linewidth=1.8, marker='o', markersize=5, label='Winner = initial leader')
    ax1.semilogx(sigmas, [r * 100 for r in singleton_rates], color='#2ca02c',
                 linewidth=1.8, marker='s', markersize=5, label='Singleton emerges (ratio >10x)')
    ax1.axhline(50, color='#555555', linestyle='--', linewidth=1, label='Chance level')
    ax1.set_xlabel('Noise level (sigma)')
    ax1.set_ylabel('Rate (%)')
    ax1.set_title(f'Stochastic outcome rates ({n_trials} trials per sigma)')
    ax1.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)
    ax1.set_ylim(0, 105)

    ax2.loglog(sigmas, mean_ratios, color=ACCENT, linewidth=1.8, marker='o', markersize=5)
    ax2.axhline(1.0, color='#555555', linestyle='--', linewidth=1)
    ax2.set_xlabel('Noise level (sigma)')
    ax2.set_ylabel('Median final ratio S1/S2')
    ax2.set_title('Median separation ratio vs noise')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'stoch_winner_rate.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    return sigmas, winner_rates, threshold_noise


# ── Experiment 3: noise with near-equal starts ────────────────────────────────

def exp_near_equal(n_trials=500):
    """
    With very small initial gap (1%), does noise become decisive?
    Compare sigma=0 (deterministic) vs sigma=0.1 vs sigma=0.3.
    """
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S1_0, S2_0 = 1.01, 1.0  # 1% gap
    rng = np.random.default_rng(7)

    sigmas = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]
    print(f"\n  Near-equal starts (1% gap): winner rate for Agent 1")
    print(f"  {'sigma':>8}  {'winner rate':>12}")

    results = []
    for sigma in sigmas:
        wins = 0
        for _ in range(n_trials):
            t, S1, S2 = euler_maruyama(S1_0, S2_0, alpha, beta_fn, sigma,
                                        dt=0.005, t_max=20.0, rng=rng)
            if S1[-1] > S2[-1]:
                wins += 1
        rate = wins / n_trials
        results.append(rate)
        print(f"  {sigma:>8.2f}  {rate:>12.1%}")

    return sigmas, results


if __name__ == '__main__':
    print("=== Stochastic Simulation ===\n")

    print("Experiment 1: Sample trajectories at different noise levels")
    exp_sample_trajectories()

    print("\nExperiment 2: Winner rate vs noise level (300 trials per sigma)")
    sigmas, winner_rates, threshold_noise = exp_winner_rate()

    print("\nExperiment 3: Near-equal starts (1% gap) under noise (500 trials)")
    exp_near_equal()

    print("\nDone.")
