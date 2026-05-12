"""
intelligence_explosion.py

Verifies the single-agent growth equation dS/dt = S^(1-β) across all growth regimes.
Tests:
  1. Three growth regimes: β<0 (superexponential), β=0 (exponential), β>0 (subexponential)
  2. Finite-time singularity for β<0: measures t* numerically and compares to theory t* = S0^β/|β|
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

S_MAX = 1e5
T_MAX = 60.0


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a2a')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def make_singularity_event():
    def event(t, S):
        return S[0] - S_MAX
    event.terminal = True
    event.direction = 1
    return event


def integrate(beta, S0=1.0, t_max=T_MAX):
    event = make_singularity_event()
    sol = solve_ivp(
        lambda t, S: [S[0] ** (1.0 - beta)],
        [0, t_max],
        [S0],
        events=event,
        max_step=0.05,
        rtol=1e-9,
        atol=1e-11,
    )
    return sol


def theoretical_singularity_time(beta, S0=1.0):
    # Time to reach S_MAX, from analytical solution of dS/dt = S^(1-β):
    # integrating: S^β/β = t + C, C = S0^β/β
    # t(S) = (S^β - S0^β) / β
    if beta >= 0:
        return None
    return (S_MAX ** beta - S0 ** beta) / beta


# ── Experiment 1: growth regime sweep ─────────────────────────────────────────

def exp_growth_regimes():
    betas = [-0.5, -0.2, 0.0, 0.2, 0.5, 1.0]
    palette = ['#d62728', '#ff7f0e', ACCENT, '#2ca02c', '#1f77b4', '#9467bd']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    for beta, color in zip(betas, palette):
        sol = integrate(beta)
        t, S = sol.t, sol.y[0]
        lbl = f'β = {beta:+.1f}'

        cap = min(500, S.max())
        mask = S <= cap
        ax1.plot(t[mask], S[mask], color=color, label=lbl, linewidth=1.8)

        ax2.semilogy(t, S, color=color, label=lbl, linewidth=1.8)

        if sol.t_events[0].size > 0:
            t_sing = sol.t_events[0][0]
            ax1.axvline(t_sing, color=color, linestyle=':', alpha=0.45, linewidth=1)
            ax2.axvline(t_sing, color=color, linestyle=':', alpha=0.45, linewidth=1)

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Capability S(t)')
    ax1.set_title('Growth regimes — linear')
    ax1.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    ax2.set_xlabel('Time')
    ax2.set_ylabel('S(t) — log scale')
    ax2.set_title('Growth regimes — log')
    ax2.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'ie_growth_regimes.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")
    return path


# ── Experiment 2: finite-time singularity verification ────────────────────────

def exp_singularity_times():
    betas = [-0.1, -0.2, -0.3, -0.5, -0.75, -1.0]
    palette = plt.cm.plasma(np.linspace(0.15, 0.9, len(betas)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    records = []
    for beta, color in zip(betas, palette):
        sol = integrate(beta, t_max=200)
        t, S = sol.t, sol.y[0]
        t_theory = theoretical_singularity_time(beta)
        t_num = sol.t_events[0][0] if sol.t_events[0].size > 0 else None

        records.append((beta, t_theory, t_num))

        ax1.semilogy(t, S, color=color, linewidth=1.8,
                     label=f'β={beta:+.2f}, t*={t_theory:.1f}')
        ax1.axvline(t_theory, color=color, linestyle='--', alpha=0.5, linewidth=1)

    # theory vs numerical scatter
    t_th = [r[1] for r in records if r[2] is not None]
    t_nu = [r[2] for r in records if r[2] is not None]
    ax2.scatter(t_th, t_nu, color=ACCENT, s=80, zorder=5)
    lim = max(max(t_th), max(t_nu)) * 1.05
    ax2.plot([0, lim], [0, lim], color='#555555', linestyle='--', linewidth=1)
    ax2.set_xlabel('t* theoretical')
    ax2.set_ylabel('t* numerical')
    ax2.set_title('Theory vs. numerical — singularity time')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('S(t) — log scale')
    ax1.set_title('Finite-time singularity (β < 0)')
    ax1.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'ie_singularity_times.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    print(f"\n  {'beta':>6}  {'t* theory':>12}  {'t* numerical':>14}  {'error %':>9}")
    for beta, t_th, t_nu in records:
        if t_nu is not None:
            err = abs(t_nu - t_th) / t_th * 100
            print(f"  {beta:>6.2f}  {t_th:>12.4f}  {t_nu:>14.4f}  {err:>8.3f}%")
        else:
            print(f"  {beta:>6.2f}  {t_th:>12.4f}  {'not reached':>14}")

    return records


if __name__ == '__main__':
    print("=== Intelligence Explosion: Growth Regime Analysis ===\n")

    print("Experiment 1: Growth regimes")
    exp_growth_regimes()

    print("\nExperiment 2: Finite-time singularity verification")
    records = exp_singularity_times()

    max_err = max(abs(r[2] - r[1]) / r[1] * 100 for r in records if r[2] is not None)
    print(f"\n  Max singularity time error: {max_err:.3f}%")
    print("\nDone.")
