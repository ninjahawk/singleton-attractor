"""
late_entrant.py

Tests Failure Mode F3: can a new agent enter the environment and displace
an incumbent singleton?

Model:
  - Incumbent runs alone from t=0 to t=t0 (head start phase)
  - At t=t0, new agent enters with initial capability S_new
  - Competition continues from t=t0 to t=t_max

Questions:
  1. Does the incumbent always maintain dominance?
  2. What is the relationship between head start t0 and entry capability S_new?
  3. Phase diagram: t0 vs S_new -> incumbent wins or entrant wins
  4. Does the β-threshold create an insurmountable moat once crossed?
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

S_CAP = 1e8


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


def run_solo(S0, alpha, beta_fn, t_end):
    """Run single agent alone until t_end. Returns final capability."""
    def ode(t, y):
        S = max(y[0], 1e-12)
        return [S ** (1.0 - beta_fn(S))]

    def cap_ev(t, y):
        return y[0] - S_CAP
    cap_ev.terminal = True
    cap_ev.direction = 1

    sol = solve_ivp(ode, [0, t_end], [S0], events=cap_ev,
                    max_step=0.02, rtol=1e-8, atol=1e-10)
    return sol.y[0, -1]


def run_competition(S_inc, S_new, alpha, beta_fn, t_max):
    """Run two-agent competition from given initial conditions."""
    def ode(t, y):
        S1, S2 = max(y[0], 1e-12), max(y[1], 1e-12)
        denom = S1 ** alpha + S2 ** alpha
        r1 = S1 ** alpha / denom
        r2 = S2 ** alpha / denom
        b1 = beta_fn(S1)
        b2 = beta_fn(S2)
        return [S1 ** (1.0 - b1) * r1, S2 ** (1.0 - b2) * r2]

    def cap_ev(t, y):
        return max(y) - S_CAP
    cap_ev.terminal = True
    cap_ev.direction = 1

    sol = solve_ivp(ode, [0, t_max], [S_inc, S_new],
                    events=cap_ev, max_step=0.02, rtol=1e-7, atol=1e-9)
    return sol


def incumbent_wins(S_inc_0, alpha, beta_fn, t0, S_new, competition_time=20.0):
    """Returns True if incumbent wins the post-entry competition."""
    S_inc_at_entry = run_solo(S_inc_0, alpha, beta_fn, t0)
    sol = run_competition(S_inc_at_entry, S_new, alpha, beta_fn, competition_time)
    return sol.y[0, -1] > sol.y[1, -1], sol, S_inc_at_entry


# ── Experiment 1: representative trajectories ─────────────────────────────────

def exp_trajectories():
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S_inc_0 = 1.0

    cases = [
        (3.0,  1.0,  "t0=3, S_new=1.0 (entrant starts equal to incumbent's origin)"),
        (3.0,  5.0,  "t0=3, S_new=5.0 (entrant starts 5x original)"),
        (3.0,  20.0, "t0=3, S_new=20 (entrant starts 20x original)"),
        (8.0,  1.0,  "t0=8, S_new=1.0 (incumbent well ahead)"),
        (8.0,  50.0, "t0=8, S_new=50 (entrant starts 50x original)"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        style_ax(ax)

    for ax, (t0, S_new, title) in zip(axes.flat, cases):
        wins, sol, S_inc_entry = incumbent_wins(S_inc_0, alpha, beta_fn, t0, S_new)

        # Solo phase
        def ode_solo(t, y):
            S = max(y[0], 1e-12)
            return [S ** (1.0 - beta_fn(S))]
        sol_solo = solve_ivp(ode_solo, [0, t0], [S_inc_0],
                             max_step=0.02, rtol=1e-8, atol=1e-10)

        t_full = np.concatenate([sol_solo.t, sol.t + t0])
        S_inc_full = np.concatenate([sol_solo.y[0], sol.y[0]])
        S_new_full = np.concatenate([np.full(len(sol_solo.t), np.nan), sol.y[1]])

        ax.semilogy(t_full, S_inc_full, color=ACCENT, linewidth=1.6,
                    label=f'Incumbent (starts at {S_inc_0})')
        ax.semilogy(t_full, S_new_full, color='#1f77b4', linewidth=1.6,
                    label=f'Entrant (enters at t={t0}, S={S_new})')
        ax.axvline(t0, color='#888888', linestyle='--', linewidth=1, label='Entry point')

        result = "INCUMBENT wins" if wins else "ENTRANT wins"
        ax.set_title(f'{title}\n{result}', fontsize=8)
        ax.set_xlabel('Time')
        ax.set_ylabel('Capability log')
        ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=7)

    axes.flat[-1].set_visible(False)
    plt.suptitle('Late entrant scenarios', color=FG, fontsize=11)
    plt.tight_layout()
    path = os.path.join(FIGURES, 'le_trajectories.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")


# ── Experiment 2: phase diagram t0 vs S_new ───────────────────────────────────

def exp_phase_diagram():
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S_inc_0 = 1.0
    THRESHOLD = 3.0  # beta threshold

    t0_values = np.linspace(0.5, 12.0, 18)
    S_new_values = np.logspace(0, 3, 20)  # 1 to 1000

    phase = np.zeros((len(t0_values), len(S_new_values)))
    S_inc_at_entry = np.zeros(len(t0_values))

    for i, t0 in enumerate(t0_values):
        S_inc_entry = run_solo(S_inc_0, alpha, beta_fn, t0)
        S_inc_at_entry[i] = S_inc_entry
        for j, S_new in enumerate(S_new_values):
            wins, _, _ = incumbent_wins(S_inc_0, alpha, beta_fn, t0, S_new, competition_time=25.0)
            phase[i, j] = 1 if wins else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(BG)
    ax1.set_facecolor(BG)
    ax2.set_facecolor(BG)

    im = ax1.imshow(phase, aspect='auto', origin='lower', cmap='RdYlGn',
                    extent=[np.log10(S_new_values[0]), np.log10(S_new_values[-1]),
                            t0_values[0], t0_values[-1]],
                    vmin=0, vmax=1)
    cbar = fig.colorbar(im, ax=ax1, ticks=[0, 1])
    cbar.set_ticklabels(['Entrant wins', 'Incumbent wins'])
    cbar.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
    ax1.set_xlabel('log10(S_new)   [entrant initial capability]')
    ax1.set_ylabel('Head start t0')
    ax1.set_title('Phase diagram: incumbent vs late entrant\nGreen=incumbent wins, Red=entrant wins')
    ax1.xaxis.label.set_color(FG)
    ax1.yaxis.label.set_color(FG)
    ax1.title.set_color(FG)
    ax1.tick_params(colors=FG)

    # Mark the beta threshold
    threshold_t0 = None
    for i, (t0, S_inc) in enumerate(zip(t0_values, S_inc_at_entry)):
        if S_inc >= THRESHOLD:
            threshold_t0 = t0
            break
    if threshold_t0:
        ax1.axhline(threshold_t0, color='white', linestyle=':', linewidth=1.5,
                    label=f'Incumbent crosses beta threshold (~t={threshold_t0:.1f})')
        ax1.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    # Right panel: incumbent capability at entry vs max entrant that incumbent can defeat
    max_S_new_wins = []
    for i in range(len(t0_values)):
        row = phase[i]
        last_win = 0
        for j in range(len(S_new_values) - 1, -1, -1):
            if row[j] == 1:
                last_win = S_new_values[j]
                break
        max_S_new_wins.append(last_win)

    style_ax(ax2)
    ax2.semilogy(t0_values, S_inc_at_entry, color=ACCENT, linewidth=1.8,
                 marker='o', markersize=4, label='Incumbent capability at entry time')
    ax2.semilogy(t0_values, max_S_new_wins, color='#2ca02c', linewidth=1.8,
                 marker='s', markersize=4, label='Max entrant S_new incumbent can defeat')
    if threshold_t0:
        ax2.axvline(threshold_t0, color='white', linestyle=':', linewidth=1.5,
                    label=f'Beta threshold crossed at t~{threshold_t0:.1f}')
    ax2.set_xlabel('Head start t0')
    ax2.set_ylabel('Capability (log scale)')
    ax2.set_title('Incumbent capability vs max defeatable entrant')
    ax2.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'le_phase_diagram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    # Print summary
    print(f"\n  {'t0':>6}  {'S_inc at entry':>16}  {'max S_new beaten':>18}  {'ratio':>8}")
    for t0, S_inc, max_sw in zip(t0_values, S_inc_at_entry, max_S_new_wins):
        ratio = max_sw / S_inc if S_inc > 0 else 0
        print(f"  {t0:>6.1f}  {S_inc:>16.2f}  {max_sw:>18.1f}  {ratio:>8.2f}x")

    return t0_values, S_inc_at_entry, max_S_new_wins


# ── Experiment 3: moat width post-threshold ───────────────────────────────────

def exp_moat():
    """
    Focus on the period just after incumbent crosses beta threshold.
    How quickly does the incumbent's "moat" (max defeatable entrant) grow?
    """
    beta_fn = sigmoid_beta(-0.3, 0.5, 3.0)
    alpha = 1.0
    S_inc_0 = 1.0
    THRESHOLD = 3.0

    # Find time when incumbent crosses threshold
    def ode_solo(t, y):
        S = max(y[0], 1e-12)
        return [S ** (1.0 - beta_fn(S))]

    def threshold_ev(t, y):
        return y[0] - THRESHOLD
    threshold_ev.terminal = True
    threshold_ev.direction = 1

    sol_pre = solve_ivp(ode_solo, [0, 100], [S_inc_0], events=threshold_ev,
                        max_step=0.01, rtol=1e-9, atol=1e-11)
    t_cross = sol_pre.t_events[0][0] if sol_pre.t_events[0].size > 0 else None

    if t_cross is None:
        print("  Incumbent never crosses threshold in tested time range")
        return

    print(f"\n  Incumbent crosses beta threshold (T=3) at t = {t_cross:.3f}")

    # Measure moat at t_cross, t_cross+0.5, t_cross+1.0, ..., t_cross+5
    post_cross_times = np.linspace(0, 5.0, 20)
    moat_widths = []

    for dt_post in post_cross_times:
        t0 = t_cross + dt_post
        S_inc_entry = run_solo(S_inc_0, alpha, beta_fn, t0)

        # Binary search for max S_new incumbent can defeat
        lo, hi = 1.0, 1e6
        for _ in range(25):
            mid = np.sqrt(lo * hi)
            wins, _, _ = incumbent_wins(S_inc_0, alpha, beta_fn, t0, mid, 20.0)
            if wins:
                lo = mid
            else:
                hi = mid
        moat_widths.append(lo)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    ax.semilogy(post_cross_times, moat_widths, color=ACCENT, linewidth=1.8,
                marker='o', markersize=5)
    ax.axvline(0, color='#888888', linestyle='--', linewidth=1, label='Threshold crossing')
    ax.set_xlabel('Time after beta threshold crossing')
    ax.set_ylabel('Max entrant capability incumbent can defeat (log)')
    ax.set_title('Moat width growth after threshold crossing')
    ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=9)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'le_moat.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    print(f"\n  {'dt_post':>9}  {'moat (max S_new)':>18}")
    for dt, m in zip(post_cross_times[::4], moat_widths[::4]):
        print(f"  {dt:>9.2f}  {m:>18.1f}")

    return post_cross_times, moat_widths


if __name__ == '__main__':
    print("=== Late Entrant Dynamics ===\n")

    print("Experiment 1: Representative trajectories")
    exp_trajectories()

    print("\nExperiment 2: Phase diagram t0 vs S_new")
    t0_vals, S_inc_caps, max_wins = exp_phase_diagram()

    print("\nExperiment 3: Moat width post-threshold")
    exp_moat()

    print("\nDone.")
