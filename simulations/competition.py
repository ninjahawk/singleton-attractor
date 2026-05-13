"""
competition.py

Two-agent capability competition with shared resource pool.
Tests:
  1. Marginal initial advantage produces ratio rho -> inf (competitive exclusion)
  2. Initial gap sensitivity: all initial gaps produce exclusion
  3. Alpha sensitivity: higher alpha -> faster divergence
  4. Beta-threshold effect: when one agent crosses the threshold, separation accelerates
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os

FIGURES = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES, exist_ok=True)

BG = 'white'
FG = 'black'
ACCENT = '#ff6b35'
GRID = '#cccccc'

T_MAX = 40.0
S_CAP = 1e8


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#888888')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def beta_fixed(S, beta):
    """Constant beta — no threshold."""
    return beta


def beta_threshold(S, beta_low, beta_high, threshold, steepness=5.0):
    """Smooth sigmoid transition: beta_high below threshold, beta_low above."""
    return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))


def ode_two_agent(t, y, alpha, beta_fn):
    S1, S2 = y
    if S1 <= 0 or S2 <= 0:
        return [0.0, 0.0]

    b1 = beta_fn(S1)
    b2 = beta_fn(S2)

    # Resource share under fast-equilibration approximation:
    # R_i / R_max = S_i^alpha / (S1^alpha + S2^alpha)
    denom = S1 ** alpha + S2 ** alpha
    if denom == 0:
        return [0.0, 0.0]

    dS1 = (S1 ** (1.0 - b1)) * (S1 ** alpha / denom)
    dS2 = (S2 ** (1.0 - b2)) * (S2 ** alpha / denom)
    return [dS1, dS2]


def cap_event(cap=S_CAP):
    def event(t, y):
        return max(y) - cap
    event.terminal = True
    event.direction = 1
    return event


def run_two_agent(S1_0, S2_0, alpha, beta_fn, t_max=T_MAX):
    sol = solve_ivp(
        lambda t, y: ode_two_agent(t, y, alpha, beta_fn),
        [0, t_max],
        [S1_0, S2_0],
        events=cap_event(),
        max_step=0.02,
        rtol=1e-8,
        atol=1e-10,
    )
    return sol


# ── Experiment 1: baseline competitive exclusion ──────────────────────────────

def exp_baseline():
    """S1(0) = 1.1, S2(0) = 1.0. Constant beta=0.5. Show ratio diverges."""
    alpha = 1.0
    beta = 0.5
    beta_fn = lambda S: beta_fixed(S, beta)

    sol = run_two_agent(1.1, 1.0, alpha, beta_fn, t_max=T_MAX)
    t = sol.t
    S1, S2 = sol.y[0], sol.y[1]
    rho = S1 / S2

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor(BG)
    for ax in axes:
        style_ax(ax)

    axes[0].plot(t, S1, color=ACCENT, label='Agent 1 (leader)', linewidth=1.8)
    axes[0].plot(t, S2, color='#1f77b4', label='Agent 2', linewidth=1.8)
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Capability S(t)')
    axes[0].set_title('Capability trajectories')
    axes[0].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)

    axes[1].semilogy(t, S1, color=ACCENT, label='Agent 1', linewidth=1.8)
    axes[1].semilogy(t, S2, color='#1f77b4', label='Agent 2', linewidth=1.8)
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('S(t) — log scale')
    axes[1].set_title('Capability — log scale')
    axes[1].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)

    axes[2].semilogy(t, rho, color='#2ca02c', linewidth=1.8)
    axes[2].set_xlabel('Time')
    axes[2].set_ylabel('rho = S1/S2 — log scale')
    axes[2].set_title(f'Ratio divergence (initial gap 10%, alpha={alpha}, beta={beta})')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'comp_baseline.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    final_rho = rho[-1]
    print(f"  Final ratio rho = {final_rho:.2f} at t = {t[-1]:.2f}")
    return final_rho


# ── Experiment 2: initial gap sensitivity ─────────────────────────────────────

def exp_initial_gap():
    """Vary initial gap from 1% to 100%. Show all produce rho -> inf."""
    gaps = [0.01, 0.05, 0.10, 0.25, 0.50, 1.00]
    alpha = 1.0
    beta = 0.5
    beta_fn = lambda S: beta_fixed(S, beta)

    palette = plt.cm.viridis(np.linspace(0.15, 0.9, len(gaps)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    for gap, color in zip(gaps, palette):
        S2_0 = 1.0
        S1_0 = 1.0 + gap
        sol = run_two_agent(S1_0, S2_0, alpha, beta_fn)
        t, rho = sol.t, sol.y[0] / sol.y[1]

        lbl = f'+{gap*100:.0f}%'
        ax1.semilogy(t, rho, color=color, label=lbl, linewidth=1.6)
        ax2.plot(t, rho, color=color, label=lbl, linewidth=1.6)

    ax1.set_xlabel('Time')
    ax1.set_ylabel('rho = S1/S2 — log scale')
    ax1.set_title('Ratio divergence by initial gap (log)')
    ax1.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8, title='Initial advantage', title_fontsize=8)

    ax2.set_xlabel('Time')
    ax2.set_ylabel('rho = S1/S2')
    ax2.set_title('Ratio divergence by initial gap (linear)')
    ax2.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8, title='Initial advantage', title_fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'comp_initial_gap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


# ── Experiment 3: alpha sensitivity ───────────────────────────────────────────

def exp_alpha():
    """Vary alpha from 0.25 to 2.0. Show effect on divergence rate."""
    alphas = [0.25, 0.5, 1.0, 1.5, 2.0]
    beta = 0.5
    beta_fn = lambda S: beta_fixed(S, beta)

    palette = plt.cm.plasma(np.linspace(0.15, 0.9, len(alphas)))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    for alpha, color in zip(alphas, palette):
        sol = run_two_agent(1.1, 1.0, alpha, beta_fn)
        t, rho = sol.t, sol.y[0] / sol.y[1]
        ax.semilogy(t, rho, color=color, label=f'alpha={alpha}', linewidth=1.8)

    ax.set_xlabel('Time')
    ax.set_ylabel('rho = S1/S2 — log scale')
    ax.set_title('Divergence rate vs alpha — higher alpha = faster exclusion')
    ax.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=9)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'comp_alpha.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


# ── Experiment 4: beta-threshold effect ───────────────────────────────────────

def exp_beta_threshold():
    """
    Compare two scenarios with identical initial conditions and alpha:
      A) Both agents in constant beta=0.5 (subexponential, no threshold)
      B) Threshold at T=5: beta drops from 0.5 to -0.3 above T

    Agent 1 starts at 1.1, Agent 2 at 1.0.
    In scenario B, Agent 1 crosses the threshold and enters superexponential growth.
    Agent 2 does not (or crosses later).
    """
    alpha = 1.0
    threshold = 5.0
    beta_high = 0.5
    beta_low = -0.3

    beta_fn_flat = lambda S: beta_fixed(S, 0.5)
    beta_fn_thresh = lambda S: beta_threshold(S, beta_low, beta_high, threshold)

    S1_0, S2_0 = 1.1, 1.0

    sol_flat = run_two_agent(S1_0, S2_0, alpha, beta_fn_flat, t_max=15.0)
    sol_thresh = run_two_agent(S1_0, S2_0, alpha, beta_fn_thresh, t_max=15.0)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        style_ax(ax)

    # Row 1: flat beta
    t_f, S1_f, S2_f = sol_flat.t, sol_flat.y[0], sol_flat.y[1]
    rho_f = S1_f / S2_f
    axes[0, 0].semilogy(t_f, S1_f, color=ACCENT, label='Agent 1', linewidth=1.8)
    axes[0, 0].semilogy(t_f, S2_f, color='#1f77b4', label='Agent 2', linewidth=1.8)
    axes[0, 0].set_title(f'Flat beta={beta_high} — capabilities')
    axes[0, 0].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('S(t) log')

    axes[0, 1].semilogy(t_f, rho_f, color='#2ca02c', linewidth=1.8)
    axes[0, 1].set_title(f'Flat beta={beta_high} — ratio')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('rho log')

    # Row 2: threshold beta
    t_th, S1_th, S2_th = sol_thresh.t, sol_thresh.y[0], sol_thresh.y[1]
    rho_th = S1_th / S2_th
    axes[1, 0].semilogy(t_th, S1_th, color=ACCENT, label='Agent 1', linewidth=1.8)
    axes[1, 0].semilogy(t_th, S2_th, color='#1f77b4', label='Agent 2', linewidth=1.8)
    axes[1, 0].axhline(threshold, color='#888888', linestyle='--', linewidth=1, label=f'Threshold T={threshold}')
    axes[1, 0].set_title(f'Threshold beta (high={beta_high} -> low={beta_low} at T={threshold}) — capabilities')
    axes[1, 0].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('S(t) log')

    axes[1, 1].semilogy(t_th, rho_th, color=ACCENT, linewidth=1.8, label='Threshold')
    axes[1, 1].semilogy(t_f, rho_f, color='#555555', linewidth=1.4, linestyle='--', label='Flat (reference)')
    axes[1, 1].set_title('Threshold vs flat — ratio comparison')
    axes[1, 1].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('rho log')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'comp_threshold.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    # Report acceleration
    final_rho_flat = rho_f[-1]
    final_rho_thresh = rho_th[-1]
    print(f"  Final ratio — flat: {final_rho_flat:.2f}, threshold: {final_rho_thresh:.2f}")
    print(f"  Threshold accelerates separation by factor: {final_rho_thresh / final_rho_flat:.1f}x at t={t_th[-1]:.1f}")


if __name__ == '__main__':
    print("=== Two-Agent Competition ===\n")

    print("Experiment 1: Baseline competitive exclusion")
    exp_baseline()

    print("\nExperiment 2: Initial gap sensitivity")
    exp_initial_gap()

    print("\nExperiment 3: Alpha sensitivity")
    exp_alpha()

    print("\nExperiment 4: Beta-threshold effect")
    exp_beta_threshold()

    print("\nDone.")
