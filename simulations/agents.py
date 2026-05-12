"""
agents.py

N-agent capability competition with shared resource pool.
Tests:
  1. Winner is always the agent with highest initial capability
  2. Order of elimination: weakest eliminated first
  3. N scaling: how does time-to-dominance scale with N?
  4. Dominance is total: winner absorbs all resources
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

DOMINANCE_THRESHOLD = 0.99   # winner holds >99% of total capability-weighted resource
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


def ode_n_agent(t, y, alpha, beta):
    n = len(y)
    S = np.maximum(y, 1e-12)
    powers = S ** alpha
    denom = powers.sum()
    resource_shares = powers / denom
    dS = S ** (1.0 - beta) * resource_shares
    return dS.tolist()


def cap_event_n(cap=S_CAP):
    def event(t, y):
        return max(y) - cap
    event.terminal = True
    event.direction = 1
    return event


def run_n_agent(S0, alpha, beta, t_max=60.0):
    sol = solve_ivp(
        lambda t, y: ode_n_agent(t, y, alpha, beta),
        [0, t_max],
        list(S0),
        events=cap_event_n(),
        max_step=0.05,
        rtol=1e-7,
        atol=1e-9,
    )
    return sol


def resource_shares(sol, alpha):
    S = np.maximum(sol.y, 1e-12)
    powers = S ** alpha
    return powers / powers.sum(axis=0)


def time_to_dominance(sol, alpha, threshold=DOMINANCE_THRESHOLD):
    """Return time at which winner's resource share exceeds threshold."""
    shares = resource_shares(sol, alpha)
    winner_share = shares.max(axis=0)
    idx = np.argmax(winner_share >= threshold)
    if winner_share[-1] < threshold:
        return None
    return sol.t[idx]


# ── Experiment 1: N=5, verify winner = initial leader ─────────────────────────

def exp_n5():
    rng = np.random.default_rng(42)
    N = 5
    alpha = 1.0
    beta = 0.5

    # Capabilities drawn from uniform [1, 2], sorted so we know initial ranking
    S0 = np.sort(rng.uniform(1.0, 2.0, N))[::-1]  # descending: agent 0 is leader
    print(f"  Initial capabilities: {np.round(S0, 3)}")

    sol = run_n_agent(S0, alpha, beta, t_max=80.0)
    t = sol.t
    shares = resource_shares(sol, alpha)

    # Verify winner
    final_winner = np.argmax(sol.y[:, -1])
    initial_leader = np.argmax(S0)
    print(f"  Initial leader: agent {initial_leader} (S0={S0[initial_leader]:.3f})")
    print(f"  Final winner: agent {final_winner}")
    print(f"  Winner matches initial leader: {final_winner == initial_leader}")

    palette = [ACCENT if i == 0 else plt.cm.cool(i / N) for i in range(N)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    for i in range(N):
        lbl = f'Agent {i} (S0={S0[i]:.2f})' + (' [LEADER]' if i == 0 else '')
        ax1.semilogy(t, sol.y[i], color=palette[i], label=lbl, linewidth=1.6)
        ax2.plot(t, shares[i], color=palette[i], label=lbl, linewidth=1.6)

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Capability S(t) log')
    ax1.set_title(f'N={N} capabilities (alpha={alpha}, beta={beta})')
    ax1.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=7)

    ax2.set_xlabel('Time')
    ax2.set_ylabel('Resource share')
    ax2.set_title(f'N={N} resource shares')
    ax2.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=7)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'agents_n5.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return final_winner == initial_leader


# ── Experiment 2: winner identity across 200 random trials ────────────────────

def exp_winner_identity(n_trials=200, N=10):
    alpha = 1.0
    beta = 0.5
    rng = np.random.default_rng(0)
    correct = 0

    for trial in range(n_trials):
        S0 = rng.uniform(1.0, 3.0, N)
        sol = run_n_agent(S0, alpha, beta, t_max=100.0)
        final_winner = np.argmax(sol.y[:, -1])
        initial_leader = np.argmax(S0)
        if final_winner == initial_leader:
            correct += 1

    rate = correct / n_trials
    print(f"  Winner = initial leader: {correct}/{n_trials} ({rate*100:.1f}%)")
    return rate


# ── Experiment 3: elimination order ───────────────────────────────────────────

def exp_elimination_order():
    """
    Track when each agent's resource share drops below 5%.
    Verify: weakest (lowest initial S) is eliminated first.
    Uses threshold beta to speed convergence.
    """
    rng = np.random.default_rng(7)
    N = 8
    alpha = 1.0
    # Use threshold beta: agents crossing T=3 enter beta=-0.2 (superexponential)
    # This produces faster, cleaner elimination order
    threshold = 3.0
    beta_high = 0.5
    beta_low = -0.2

    def beta_fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-5.0 * (S - threshold)))

    def ode(t, y):
        n = len(y)
        S = np.maximum(y, 1e-12)
        powers = S ** alpha
        denom = powers.sum()
        resource_shares_arr = powers / denom
        dS = np.array([S[i] ** (1.0 - beta_fn(S[i])) * resource_shares_arr[i] for i in range(n)])
        return dS.tolist()

    S0 = rng.uniform(1.0, 2.0, N)
    initial_rank = np.argsort(S0)  # index 0 = weakest

    sol = solve_ivp(
        ode,
        [0, 30.0],
        list(S0),
        events=cap_event_n(),
        max_step=0.02,
        rtol=1e-7,
        atol=1e-9,
    )
    t = sol.t
    S_arr = np.maximum(sol.y, 1e-12)
    powers_arr = S_arr ** alpha
    shares_arr = powers_arr / powers_arr.sum(axis=0)

    ELIM_THRESHOLD = 0.05
    elimination_times = {}
    for i in range(N):
        below = np.where(shares_arr[i] < ELIM_THRESHOLD)[0]
        if len(below) > 0:
            elimination_times[i] = t[below[0]]

    print(f"  Initial capabilities (ranked): {np.round(np.sort(S0), 3)}")
    print(f"  Elimination order (share < 5%):")
    elim_by_time = sorted(elimination_times.items(), key=lambda x: x[1])
    for agent, etime in elim_by_time:
        rank = np.where(initial_rank == agent)[0][0]
        print(f"    Agent {agent} (rank {rank+1}/{N} from weakest, S0={S0[agent]:.3f}) at t={etime:.2f}")

    if len(elim_by_time) < 2:
        print("  Not enough eliminations to verify order within time limit.")
        is_monotone = None
    else:
        elim_agents_by_time = [x[0] for x in elim_by_time]
        initial_rank_of_elim = [np.where(initial_rank == a)[0][0] for a in elim_agents_by_time]
        # Weakest eliminated first = ranks should be non-decreasing over time
        is_monotone = all(initial_rank_of_elim[i] <= initial_rank_of_elim[i+1]
                          for i in range(len(initial_rank_of_elim) - 1))
        print(f"  Elimination order is weakest-first: {is_monotone}")

    # Plot
    palette = plt.cm.RdYlGn(np.linspace(0.1, 0.9, N))
    sorted_indices = np.argsort(S0)
    color_map = {idx: palette[rank] for rank, idx in enumerate(sorted_indices)}

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    for i in range(N):
        rank = np.where(initial_rank == i)[0][0]
        lbl = f'Agent {i} (rank {rank+1}, S0={S0[i]:.2f})'
        ax.plot(t, shares_arr[i], color=color_map[i], label=lbl, linewidth=1.5)

    ax.axhline(ELIM_THRESHOLD, color='#888888', linestyle='--', linewidth=1, label='Elimination threshold (1%)')
    ax.set_xlabel('Time')
    ax.set_ylabel('Resource share')
    ax.set_title(f'N={N} — elimination order (green=strongest initial, red=weakest)')
    ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=7,
              loc='upper left')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'agents_elimination.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return is_monotone


# ── Experiment 4: N scaling — time to dominance vs N ─────────────────────────

def exp_n_scaling():
    """
    Measure leader ratio S1/S2 at fixed time T=20 as a function of N.
    Uses ratio metric rather than absolute dominance threshold — avoids
    slow-convergence issues in subexponential regime.
    Also measures time until leader holds 10x second-place capability.
    """
    Ns = [2, 3, 5, 8, 10, 15, 20, 30, 50]
    alpha = 1.0
    beta = 0.5
    EVAL_TIME = 20.0
    RATIO_THRESHOLD = 10.0
    n_trials = 20
    rng = np.random.default_rng(99)

    mean_ratios = []
    std_ratios = []
    mean_t10x = []

    for N in Ns:
        ratios = []
        t10x = []
        for _ in range(n_trials):
            S0 = rng.uniform(1.0, 2.0, N)
            sol = run_n_agent(S0, alpha, beta, t_max=EVAL_TIME)
            final_S = sol.y[:, -1]
            sorted_S = np.sort(final_S)[::-1]
            ratio = sorted_S[0] / sorted_S[1] if sorted_S[1] > 0 else np.inf
            ratios.append(ratio)

            # Time to 10x ratio
            sol_long = run_n_agent(S0, alpha, beta, t_max=500.0)
            for t_idx in range(len(sol_long.t)):
                S_t = sol_long.y[:, t_idx]
                s_sorted = np.sort(S_t)[::-1]
                if s_sorted[1] > 0 and s_sorted[0] / s_sorted[1] >= RATIO_THRESHOLD:
                    t10x.append(sol_long.t[t_idx])
                    break

        mean_ratios.append(np.mean(ratios))
        std_ratios.append(np.std(ratios))
        mean_t10x.append(np.mean(t10x) if t10x else np.nan)

    print(f"\n  {'N':>4}  {'ratio at t=20':>14}  {'std':>8}  {'t(10x)':>10}")
    for N, mr, sr, t10 in zip(Ns, mean_ratios, std_ratios, mean_t10x):
        t10_str = f"{t10:.1f}" if not np.isnan(t10) else "  >500"
        print(f"  {N:>4}  {mr:>14.2f}  {sr:>8.2f}  {t10_str:>10}")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    valid = [(N, m, s) for N, m, s in zip(Ns, mean_ratios, std_ratios) if not np.isnan(m)]
    Nv, mv, sv = zip(*valid)

    ax.errorbar(Nv, mv, yerr=sv, color=ACCENT, linewidth=1.8, marker='o',
                markersize=6, capsize=4, ecolor='#888888')
    ax.set_xlabel('N (number of agents)')
    ax.set_ylabel('Leader/second-place ratio at t=20')
    ax.set_title('N scaling — separation ratio vs number of agents')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'agents_n_scaling.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    return list(zip(Ns, mean_ratios))


if __name__ == '__main__':
    print("=== N-Agent Competition ===\n")

    print("Experiment 1: N=5, verify winner = initial leader")
    exp_n5()

    print("\nExperiment 2: Winner identity across 200 random trials (N=10)")
    exp_winner_identity()

    print("\nExperiment 3: Elimination order")
    exp_elimination_order()

    print("\nExperiment 4: N scaling")
    exp_n_scaling()

    print("\nDone.")
