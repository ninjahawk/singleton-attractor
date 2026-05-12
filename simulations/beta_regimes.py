"""
beta_regimes.py

Tests OQ1: what happens when agents have fundamentally different beta functions?

Three cases:
  A) Baseline — both agents have same threshold beta (confirm prior results)
  B) Asymmetric ceiling — Agent 1 can reach beta<0, Agent 2 cannot (flat beta=0.5 always)
     Question: when does Agent 1 win despite potentially starting behind?
  C) Threshold race — both can reach beta<0 but at different thresholds T1 < T2
     Question: does lower threshold always win, or can initial position override?
  D) Phase diagram — initial capability ratio vs threshold gap -> who wins?
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

S_CAP = 1e7


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a2a')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def sigmoid_beta(beta_low, beta_high, threshold, steepness=5.0):
    def fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))
    return fn


def flat_beta(beta):
    return lambda S: beta


def run_two(S1_0, S2_0, alpha, beta1_fn, beta2_fn, t_max=20.0):
    def ode(t, y):
        S1, S2 = max(y[0], 1e-12), max(y[1], 1e-12)
        denom = S1 ** alpha + S2 ** alpha
        r1 = (S1 ** alpha) / denom
        r2 = (S2 ** alpha) / denom
        dS1 = S1 ** (1.0 - beta1_fn(S1)) * r1
        dS2 = S2 ** (1.0 - beta2_fn(S2)) * r2
        return [dS1, dS2]

    def cap_ev(t, y):
        return max(y) - S_CAP
    cap_ev.terminal = True
    cap_ev.direction = 1

    return solve_ivp(ode, [0, t_max], [S1_0, S2_0],
                     events=cap_ev, max_step=0.02, rtol=1e-7, atol=1e-9)


def separation(sol, at_end=True):
    idx = -1
    S1, S2 = sol.y[0, idx], sol.y[1, idx]
    if S2 <= 0:
        return np.inf
    return S1 / S2


# ── Case A: same threshold beta (baseline) ────────────────────────────────────

def case_a():
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0

    sol = run_two(1.1, 1.0, alpha, beta_fn, beta_fn)
    rho = sol.y[0] / sol.y[1]

    print(f"  Case A: final ratio = {rho[-1]:.1f}x, winner = Agent {'1' if sol.y[0,-1] > sol.y[1,-1] else '2'}")
    return rho[-1]


# ── Case B: asymmetric ceiling ─────────────────────────────────────────────────

def case_b():
    """
    Agent 1: threshold beta (can enter superexponential at T=3)
    Agent 2: flat beta=0.5 (subexponential always)

    Vary S2(0) from 1.0 to 20.0, with S1(0)=1.0 fixed.
    Find: at what starting disadvantage does Agent 1 lose?
    """
    alpha = 1.0
    beta1_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    beta2_fn = flat_beta(0.5)

    # Sweep S2(0) — how far ahead does agent 2 need to start to win?
    S2_starts = np.logspace(0, 2, 40)  # 1.0 to 100.0
    S1_start = 1.0

    winners = []
    final_ratios = []

    for S2_0 in S2_starts:
        sol = run_two(S1_start, S2_0, alpha, beta1_fn, beta2_fn, t_max=25.0)
        S1_final = sol.y[0, -1]
        S2_final = sol.y[1, -1]
        winners.append(1 if S1_final > S2_final else 2)
        final_ratios.append(S1_final / S2_final if S2_final > 0 else np.inf)

    # Find crossover
    crossover = None
    for i, (S2_0, w) in enumerate(zip(S2_starts, winners)):
        if w == 2:
            crossover = S2_starts[i - 1] if i > 0 else S2_0
            break

    if crossover:
        print(f"  Case B: Agent 1 (threshold) loses when Agent 2 starts at S2(0) > ~{crossover:.1f}")
        print(f"  Agent 1 wins at 1:{crossover:.1f} initial disadvantage or less")
    else:
        print("  Case B: Agent 1 (threshold beta) wins at all tested initial disadvantages (up to 100x)")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    colors = [ACCENT if w == 1 else '#1f77b4' for w in winners]
    ax1.scatter(S2_starts, final_ratios, c=colors, s=40, zorder=5)
    ax1.axhline(1.0, color='#555555', linestyle='--', linewidth=1)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Agent 2 initial capability S2(0)   [Agent 1 fixed at 1.0]')
    ax1.set_ylabel('Final ratio S1/S2')
    ax1.set_title('Case B: threshold agent vs flat agent\norange = Agent 1 wins, blue = Agent 2 wins')

    # Show example trajectories
    for S2_0, color, lbl in [(2.0, '#aaaaaa', 'S2(0)=2'), (10.0, '#888888', 'S2(0)=10'),
                              (50.0, '#555555', 'S2(0)=50')]:
        sol = run_two(S1_start, S2_0, alpha, beta1_fn, beta2_fn, t_max=25.0)
        ax2.semilogy(sol.t, sol.y[0], color=ACCENT, linewidth=1.5,
                     label=f'Agent 1 (threshold)' if S2_0 == 2.0 else '_')
        ax2.semilogy(sol.t, sol.y[1], color=color, linewidth=1.5, label=f'Agent 2 {lbl}')

    ax2.set_xlabel('Time')
    ax2.set_ylabel('Capability S(t) — log')
    ax2.set_title('Case B: example trajectories at different initial disadvantages')
    ax2.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'br_case_b.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return S2_starts, winners, crossover


# ── Case C: threshold race ─────────────────────────────────────────────────────

def case_c():
    """
    Both agents can reach beta<0, but at different thresholds.
    Agent 1: threshold T1 (lower — reaches superexponential sooner)
    Agent 2: threshold T2 > T1 (higher — has subexponential advantage longer)

    Both start with equal initial capability = 1.0.
    Vary T1 from 1.5 to 5.0, T2 fixed at 5.0. Who wins?
    Then: vary initial capabilities at fixed T1=3, T2=5.
    """
    alpha = 1.0
    T2 = 5.0
    beta_high = 0.5
    beta_low = -0.3

    T1_values = np.linspace(1.5, 4.9, 20)
    winners_equal = []

    for T1 in T1_values:
        beta1_fn = sigmoid_beta(beta_low, beta_high, T1)
        beta2_fn = sigmoid_beta(beta_low, beta_high, T2)
        sol = run_two(1.0, 1.0, alpha, beta1_fn, beta2_fn, t_max=20.0)
        winners_equal.append(1 if sol.y[0, -1] > sol.y[1, -1] else 2)

    # With equal starts, lower threshold always wins?
    all_agent1 = all(w == 1 for w in winners_equal)
    print(f"\n  Case C (equal starts, varying T1 vs T2={T2}): Agent 1 (lower T) always wins: {all_agent1}")

    # Now: T1=3.0 fixed, T2=5.0 fixed, vary S1(0) vs S2(0)
    T1_fixed, T2_fixed = 3.0, 5.0
    beta1_fn = sigmoid_beta(beta_low, beta_high, T1_fixed)
    beta2_fn = sigmoid_beta(beta_low, beta_high, T2_fixed)

    S_ratios = np.logspace(-1, 1, 40)  # S2(0)/S1(0) from 0.1 to 10
    S1_base = 1.0
    winners_ratio = []
    final_ratios_c = []

    for ratio in S_ratios:
        S2_0 = S1_base * ratio
        sol = run_two(S1_base, S2_0, alpha, beta1_fn, beta2_fn, t_max=20.0)
        S1f, S2f = sol.y[0, -1], sol.y[1, -1]
        winners_ratio.append(1 if S1f > S2f else 2)
        final_ratios_c.append(S1f / S2f)

    crossover_c = None
    for i, (r, w) in enumerate(zip(S_ratios, winners_ratio)):
        if w == 2:
            crossover_c = S_ratios[i - 1] if i > 0 else r
            break

    if crossover_c:
        print(f"  Case C (T1=3, T2=5): Agent 1 loses when S2(0)/S1(0) > ~{crossover_c:.2f}")
        print(f"  Lower-threshold agent can overcome up to {crossover_c:.2f}x initial disadvantage")
    else:
        print(f"  Case C (T1=3, T2=5): Agent 1 (lower T) wins at all tested initial ratios (up to 10x disadvantage)")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    colors = [ACCENT if w == 1 else '#1f77b4' for w in winners_ratio]
    ax1.scatter(S_ratios, final_ratios_c, c=colors, s=40, zorder=5)
    ax1.axhline(1.0, color='#555555', linestyle='--', linewidth=1)
    ax1.axvline(1.0, color='#555555', linestyle=':', linewidth=1, label='Equal start')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('S2(0)/S1(0)   [>1 means Agent 2 starts ahead]')
    ax1.set_ylabel('Final ratio S1/S2')
    ax1.set_title(f'Threshold race: T1={T1_fixed} vs T2={T2_fixed}\norange=Agent1 wins, blue=Agent2 wins')
    ax1.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    # Example trajectories
    for S2_0, color, lbl in [(0.5, '#888888', 'S2(0)=0.5'), (1.0, '#aaaaaa', 'S2(0)=1.0'),
                              (3.0, '#666666', 'S2(0)=3.0')]:
        sol = run_two(1.0, S2_0, alpha, beta1_fn, beta2_fn, t_max=20.0)
        ax2.semilogy(sol.t, sol.y[0], color=ACCENT, linewidth=1.5,
                     label=f'Agent 1 (T={T1_fixed})' if S2_0 == 0.5 else '_')
        ax2.semilogy(sol.t, sol.y[1], color=color, linewidth=1.5, label=f'Agent 2 {lbl}')

    ax2.set_xlabel('Time')
    ax2.set_ylabel('Capability log')
    ax2.set_title(f'Threshold race: T1={T1_fixed} vs T2={T2_fixed} — trajectories')
    ax2.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'br_case_c.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return crossover_c


# ── Case D: phase diagram ─────────────────────────────────────────────────────

def case_d():
    """
    Phase diagram: initial capability ratio S2(0)/S1(0) vs threshold gap (T2 - T1).
    Agent 1 always has T1=2.0. T2 varies.
    Find the boundary between Agent 1 winning and Agent 2 winning.
    """
    alpha = 1.0
    beta_high = 0.5
    beta_low = -0.3
    T1 = 2.0
    beta1_fn = sigmoid_beta(beta_low, beta_high, T1)

    T2_values = np.linspace(2.5, 8.0, 14)
    S_ratio_values = np.logspace(-0.5, 1.5, 16)  # S2/S1 from ~0.3 to ~30

    phase = np.zeros((len(T2_values), len(S_ratio_values)))

    for i, T2 in enumerate(T2_values):
        beta2_fn = sigmoid_beta(beta_low, beta_high, T2)
        for j, ratio in enumerate(S_ratio_values):
            S2_0 = ratio  # S1(0)=1.0
            sol = run_two(1.0, S2_0, alpha, beta1_fn, beta2_fn, t_max=20.0)
            phase[i, j] = 1 if sol.y[0, -1] > sol.y[1, -1] else 0

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    im = ax.imshow(phase, aspect='auto', origin='lower', cmap='RdYlGn',
                   extent=[np.log10(S_ratio_values[0]), np.log10(S_ratio_values[-1]),
                           T2_values[0] - T1, T2_values[-1] - T1],
                   vmin=0, vmax=1)

    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1])
    cbar.set_ticklabels(['Agent 2 wins', 'Agent 1 wins'])
    cbar.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)

    ax.set_xlabel('log10(S2(0)/S1(0))   [>0 means Agent 2 starts ahead]')
    ax.set_ylabel('Threshold gap (T2 - T1)')
    ax.set_title(f'Phase diagram: Agent 1 (T={T1}, threshold) vs Agent 2 (T=T1+gap, threshold)\nGreen = Agent 1 wins, Red = Agent 2 wins')
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    ax.tick_params(colors=FG)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'br_phase_diagram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    # Print boundary
    print(f"\n  Phase diagram: Agent 1 (T1={T1}) vs Agent 2 (T2=T1+gap)")
    print(f"  {'T2-T1':>8}  {'Max S2/S1 where Agent 1 still wins':>38}")
    for i, T2 in enumerate(T2_values):
        row = phase[i]
        last_win = None
        for j in range(len(S_ratio_values) - 1, -1, -1):
            if row[j] == 1:
                last_win = S_ratio_values[j]
                break
        gap = T2 - T1
        if last_win:
            print(f"  {gap:>8.2f}  {last_win:>38.2f}x")
        else:
            print(f"  {gap:>8.2f}  {'Agent 1 never wins':>38}")

    return phase


if __name__ == '__main__':
    print("=== Beta Regime Analysis ===\n")

    print("Case A: Baseline (same threshold beta)")
    case_a()

    print("\nCase B: Asymmetric ceiling (Agent 1 threshold, Agent 2 flat)")
    S2_starts, winners, crossover = case_b()

    print("\nCase C: Threshold race")
    crossover_c = case_c()

    print("\nCase D: Phase diagram")
    case_d()

    print("\nDone.")
