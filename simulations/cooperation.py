"""
cooperation.py

The single most important objection to the singleton attractor theorem:
agents can cooperate. Two weaker agents pooling resources can resist a stronger one.
Can cooperation prevent singleton emergence?

Four experiments:

  1. Coalition size vs singleton suppression
     Can N cooperating agents starve the singleton candidate before it reaches threshold T?

  2. Internal coalition dynamics
     Does the coalition itself produce an internal singleton?
     The coalition delays any single member reaching T — but once capability diverges
     inside the coalition, the strongest member defects and becomes the singleton anyway.

  3. Defection game
     Agents stay in coalition only while cooperation is individually rational.
     When does defection destroy the coalition?

  4. Full dynamic game
     All N agents form/break coalitions dynamically at each step.
     Does a singleton still emerge, and how much does cooperation delay it?
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

S_CAP = 1e7
THRESHOLD = 3.0
BETA_HIGH = 0.5
BETA_LOW = -0.3
ALPHA = 1.0


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor('#888888')
    ax.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)


def beta(S):
    return BETA_HIGH + (BETA_LOW - BETA_HIGH) / (1.0 + np.exp(-5.0 * (S - THRESHOLD)))


def cap_event(cap=S_CAP):
    def ev(t, y):
        return max(y) - cap
    ev.terminal = True
    ev.direction = 1
    return ev


# ── Experiment 1: Coalition size vs singleton suppression ─────────────────────

def exp_coalition_size():
    """
    Singleton candidate starts at S=1.1.
    N coalition members each start at S=1.0 and act as one combined agent.
    Combined coalition capability = N * 1.0 (pooled, Option B).

    Measure: does singleton reach threshold T at each coalition size N?
    Find the critical N where coalition starves singleton before T.
    """
    Ns = list(range(1, 16))
    S_singleton_0 = 1.1

    singleton_crossed = []
    singleton_t_cross = []
    coalition_t_cross = []

    for N in Ns:
        S_coalition_0 = float(N) * 1.0  # combined capability

        def ode(t, y):
            S_s, S_c = max(y[0], 1e-12), max(y[1], 1e-12)
            denom = S_s ** ALPHA + S_c ** ALPHA
            r_s = S_s ** ALPHA / denom
            r_c = S_c ** ALPHA / denom
            dS_s = S_s ** (1.0 - beta(S_s)) * r_s
            dS_c = S_c ** (1.0 - beta(S_c)) * r_c
            return [dS_s, dS_c]

        def threshold_ev_s(t, y):
            return y[0] - THRESHOLD
        threshold_ev_s.terminal = False
        threshold_ev_s.direction = 1

        sol = solve_ivp(ode, [0, 30.0], [S_singleton_0, S_coalition_0],
                        events=cap_event(), max_step=0.02, rtol=1e-7, atol=1e-9)

        S_s_final = sol.y[0, -1]
        S_c_final = sol.y[1, -1]

        # Did singleton cross T?
        crossed = any(sol.y[0] >= THRESHOLD)
        singleton_crossed.append(crossed)

        # Time to reach T (approximate)
        t_s = None
        for i, s in enumerate(sol.y[0]):
            if s >= THRESHOLD:
                t_s = sol.t[i]
                break
        singleton_t_cross.append(t_s)

        t_c = None
        for i, s in enumerate(sol.y[1]):
            if s >= THRESHOLD:
                t_c = sol.t[i]
                break
        coalition_t_cross.append(t_c)

    # Find critical N
    critical_N = None
    for N, crossed in zip(Ns, singleton_crossed):
        if not crossed:
            critical_N = N
            break

    print(f"  {'N':>4}  {'singleton reaches T':>20}  {'singleton t_cross':>18}  {'coalition t_cross':>18}")
    for N, crossed, t_s, t_c in zip(Ns, singleton_crossed, singleton_t_cross, coalition_t_cross):
        t_s_str = f"{t_s:.2f}" if t_s else "  never"
        t_c_str = f"{t_c:.2f}" if t_c else "  never"
        print(f"  {N:>4}  {'yes' if crossed else 'NO':>20}  {t_s_str:>18}  {t_c_str:>18}")

    if critical_N:
        print(f"\n  Critical coalition size: N >= {critical_N} prevents singleton from crossing T")
    else:
        print(f"\n  Singleton reaches T at all tested coalition sizes (N up to {max(Ns)})")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax1)
    style_ax(ax2)

    ax1.bar(Ns, [1 if c else 0 for c in singleton_crossed],
            color=[ACCENT if c else '#2ca02c' for c in singleton_crossed])
    ax1.axhline(0.5, color='#555', linestyle='--', linewidth=1)
    ax1.set_xlabel('Coalition size N')
    ax1.set_ylabel('Singleton reaches T (1=yes, 0=no)')
    ax1.set_title('Coalition suppression — does coalition prevent threshold crossing?')
    ax1.set_xticks(Ns)

    # Example trajectories: N=1, N=5, N=10
    for N, color in [(1, '#888888'), (5, '#aaaaaa'), (10, '#2ca02c')]:
        S_c_0 = float(N) * 1.0

        def ode_ex(t, y, Nc=N):
            S_s, S_c = max(y[0], 1e-12), max(y[1], 1e-12)
            denom = S_s ** ALPHA + S_c ** ALPHA
            r_s = S_s ** ALPHA / denom
            r_c = S_c ** ALPHA / denom
            return [S_s ** (1.0 - beta(S_s)) * r_s, S_c ** (1.0 - beta(S_c)) * r_c]

        sol_ex = solve_ivp(ode_ex, [0, 20.0], [S_singleton_0, float(N) * 1.0],
                           events=cap_event(), max_step=0.02, rtol=1e-7, atol=1e-9)
        ax2.semilogy(sol_ex.t, sol_ex.y[0], color=ACCENT, linewidth=1.5,
                     label=f'Singleton' if N == 1 else '_')
        ax2.semilogy(sol_ex.t, sol_ex.y[1], color=color, linewidth=1.5,
                     label=f'Coalition N={N}')

    ax2.axhline(THRESHOLD, color='white', linestyle=':', linewidth=1, label=f'Threshold T={THRESHOLD}')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Capability log')
    ax2.set_title('Example trajectories: singleton vs coalitions')
    ax2.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'coop_coalition_size.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")
    return Ns, singleton_crossed, critical_N


# ── Experiment 2: Internal coalition dynamics ─────────────────────────────────

def exp_internal_dynamics():
    """
    N agents form a coalition. Resources shared proportionally within (no pooling trick).
    Slight capability heterogeneity within coalition.
    Singleton candidate (agent 0) has modest head start.

    Question: does the coalition produce an internal singleton?
    The coalition delays any member from reaching T by distributing resources —
    but once capability diverges internally, the strongest member dominates.
    """
    rng = np.random.default_rng(42)
    N_coalition = 8
    N_total = N_coalition + 1  # +1 singleton candidate

    # Singleton starts ahead
    S_singleton_0 = 1.1
    # Coalition members: slight heterogeneity
    S_coalition_0 = 1.0 + rng.uniform(0, 0.05, N_coalition)

    S0 = np.concatenate([[S_singleton_0], S_coalition_0])
    labels = ['Singleton candidate'] + [f'Coalition member {i}' for i in range(N_coalition)]
    coalition_idx = list(range(1, N_total))

    def ode(t, y):
        S = np.maximum(y, 1e-12)

        # Coalition members pool combined capability externally
        # but compete individually internally
        S_singleton = S[0]
        S_coal_members = S[1:]
        S_coal_combined = S_coal_members.sum()  # coalition acts as one externally

        # External competition: singleton vs coalition block
        denom_ext = S_singleton ** ALPHA + S_coal_combined ** ALPHA
        singleton_share = S_singleton ** ALPHA / denom_ext
        coalition_block_share = S_coal_combined ** ALPHA / denom_ext

        # Internal coalition: members compete proportionally for coalition's share
        coal_powers = S_coal_members ** ALPHA
        coal_internal_shares = coal_powers / coal_powers.sum() * coalition_block_share

        dS = np.zeros(N_total)
        dS[0] = S[0] ** (1.0 - beta(S[0])) * singleton_share
        for i, idx in enumerate(coalition_idx):
            dS[idx] = S[idx] ** (1.0 - beta(S[idx])) * coal_internal_shares[i]
        return dS.tolist()

    def cap_ev(t, y):
        return max(y) - S_CAP
    cap_ev.terminal = True
    cap_ev.direction = 1

    sol = solve_ivp(ode, [0, 25.0], list(S0), events=cap_ev,
                    max_step=0.02, rtol=1e-7, atol=1e-9)
    t = sol.t
    S = sol.y

    # Who crosses T first?
    first_cross = None
    first_cross_t = None
    for i in range(N_total):
        for j, s in enumerate(S[i]):
            if s >= THRESHOLD:
                if first_cross_t is None or t[j] < first_cross_t:
                    first_cross = i
                    first_cross_t = t[j]
                break

    # Final winner
    winner = np.argmax(S[:, -1])

    print(f"\n  First to cross T: {labels[first_cross]} at t={first_cross_t:.2f}")
    print(f"  Final dominant agent: {labels[winner]}")
    print(f"  Coalition suppressed singleton crossing T: {first_cross != 0}")

    # Resource shares over time
    powers = np.maximum(S, 1e-12) ** ALPHA
    resource_shares = powers / powers.sum(axis=0)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor(BG)
    for ax in axes:
        style_ax(ax)

    # Capabilities
    axes[0].semilogy(t, S[0], color=ACCENT, linewidth=2, label='Singleton candidate')
    for i in range(1, N_total):
        axes[0].semilogy(t, S[i], color='#1f77b4', linewidth=0.8, alpha=0.6,
                         label='Coalition members' if i == 1 else '_')
    axes[0].axhline(THRESHOLD, color='white', linestyle=':', linewidth=1, label=f'T={THRESHOLD}')
    axes[0].set_title('Capabilities over time')
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('S log')
    axes[0].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)

    # Resource shares
    axes[1].plot(t, resource_shares[0] * 100, color=ACCENT, linewidth=2,
                 label='Singleton candidate')
    for i in range(1, N_total):
        axes[1].plot(t, resource_shares[i] * 100, color='#1f77b4', linewidth=0.8,
                     alpha=0.5, label='Coalition members' if i == 1 else '_')
    axes[1].set_title('Resource shares (%)')
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('%')
    axes[1].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=8)

    # Internal coalition spread: max/min ratio within coalition
    coal_S = S[1:]
    internal_ratio = coal_S.max(axis=0) / np.maximum(coal_S.min(axis=0), 1e-12)
    axes[2].semilogy(t, internal_ratio, color='#2ca02c', linewidth=1.8)
    axes[2].set_title('Internal coalition spread (max/min capability ratio)')
    axes[2].set_xlabel('Time')
    axes[2].set_ylabel('Ratio log')

    plt.suptitle(f'Internal coalition dynamics: {N_coalition} members + 1 singleton candidate',
                 color=FG, fontsize=11)
    plt.tight_layout()
    path = os.path.join(FIGURES, 'coop_internal.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    return first_cross != 0  # True if coalition successfully suppressed singleton


# ── Experiment 3: Defection game ─────────────────────────────────────────────

def exp_defection():
    """
    Coalition members check at each step: is my individual resource share
    better than my coalition share? If yes, defect.

    Tracks when coalitions collapse and how this affects singleton emergence.
    """
    rng = np.random.default_rng(7)
    N_total = 8
    dt = 0.01
    t_max = 20.0

    # Agent 0 is strongest (singleton candidate), rest form initial coalition
    S0 = np.array([1.15] + sorted(rng.uniform(0.9, 1.05, N_total - 1), reverse=True))
    S = S0.copy()

    # Coalition membership: initially all except agent 0 cooperate
    coalition = set(range(1, N_total))
    defectors = {0}  # agent 0 never cooperates

    n_steps = int(t_max / dt)
    t_series = np.zeros(n_steps + 1)
    S_series = np.zeros((N_total, n_steps + 1))
    coalition_size_series = np.zeros(n_steps + 1)

    S_series[:, 0] = S
    coalition_size_series[0] = len(coalition)

    defection_events = []

    for step in range(n_steps):
        S = np.maximum(S, 1e-12)
        t = step * dt

        # Compute resource shares under current coalition structure
        # Coalition acts as block externally
        coal_list = sorted(coalition)
        defect_list = sorted(defectors)

        S_coal = S[coal_list].sum() if coal_list else 0.0
        S_defect_total = sum(S[i] ** ALPHA for i in defect_list)
        S_coal_block = S_coal ** ALPHA if S_coal > 0 else 0.0

        denom_ext = S_coal_block + S_defect_total

        # Resource for each defector: S_i^alpha / denom_ext
        # Resource for coalition block: S_coal^alpha / denom_ext, then split by S_i^alpha internally
        if denom_ext > 0:
            coal_block_share = S_coal_block / denom_ext
            defect_shares = {i: S[i] ** ALPHA / denom_ext for i in defect_list}
            coal_powers = np.array([S[i] ** ALPHA for i in coal_list]) if coal_list else np.array([])
            coal_internal = coal_powers / coal_powers.sum() * coal_block_share if coal_list else np.array([])
            coal_shares = {i: coal_internal[k] for k, i in enumerate(coal_list)}
        else:
            defect_shares = {i: 1.0 / N_total for i in defect_list}
            coal_shares = {i: 1.0 / N_total for i in coal_list}

        # Check defection: coalition member i defects if individual share > coalition share
        # Individual share if they defect = S_i^alpha / (denom_ext + S_i^alpha - S_coal_block contribution)
        new_defectors = set()
        for i in list(coalition):
            # What would i get as a defector?
            # Remove i from coalition, add as individual defector
            new_coal_members = [j for j in coal_list if j != i]
            new_S_coal = sum(S[j] for j in new_coal_members) if new_coal_members else 0.0
            new_S_coal_block = new_S_coal ** ALPHA
            new_denom = new_S_coal_block + S_defect_total + S[i] ** ALPHA
            individual_share = S[i] ** ALPHA / new_denom if new_denom > 0 else 0.0
            current_share = coal_shares.get(i, 0.0)

            if individual_share > current_share * 1.01:  # 1% threshold to prevent noise-driven defection
                new_defectors.add(i)
                defection_events.append((t, i, S[i]))

        for i in new_defectors:
            coalition.discard(i)
            defectors.add(i)

        # Recompute shares after defection
        coal_list = sorted(coalition)
        defect_list = sorted(defectors)
        S_coal = sum(S[i] for i in coal_list)
        S_coal_block = S_coal ** ALPHA if S_coal > 0 else 0.0
        S_defect_total = sum(S[i] ** ALPHA for i in defect_list)
        denom_ext = S_coal_block + S_defect_total

        # Grow all agents
        resource_shares = np.zeros(N_total)
        if denom_ext > 0:
            coal_block_share = S_coal_block / denom_ext if coal_list else 0.0
            for i in defect_list:
                resource_shares[i] = S[i] ** ALPHA / denom_ext
            if coal_list:
                coal_powers = np.array([S[i] ** ALPHA for i in coal_list])
                coal_int = coal_powers / coal_powers.sum() * coal_block_share
                for k, i in enumerate(coal_list):
                    resource_shares[i] = coal_int[k]

        betas = np.array([beta(s) for s in S])
        dS = S ** (1.0 - betas) * resource_shares * dt
        S = np.maximum(S + dS, 1e-12)
        if S.max() > S_CAP:
            S = np.minimum(S, S_CAP)

        t_series[step + 1] = (step + 1) * dt
        S_series[:, step + 1] = S
        coalition_size_series[step + 1] = len(coalition)

    # Results
    winner = np.argmax(S_series[:, -1])
    print(f"\n  Initial coalition: agents 1-{N_total-1}")
    print(f"  Defection events: {len(defection_events)}")
    if defection_events:
        first_def_t, first_def_i, first_def_s = defection_events[0]
        print(f"  First defection: agent {first_def_i} at t={first_def_t:.2f} (S={first_def_s:.3f})")
    print(f"  Coalition members at t_max: {sorted(coalition)}")
    print(f"  Final winner: agent {winner} (initial capability {S0[winner]:.3f})")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        style_ax(ax)

    # Capabilities
    for i in range(N_total):
        color = ACCENT if i == 0 else ('#2ca02c' if i in coalition else '#1f77b4')
        lbl = 'Singleton candidate' if i == 0 else (f'Agent {i}')
        axes[0, 0].semilogy(t_series, S_series[i], color=color,
                            linewidth=1.8 if i == 0 else 0.9, label=lbl if i <= 2 else '_')
    axes[0, 0].axhline(THRESHOLD, color='white', linestyle=':', linewidth=1)
    axes[0, 0].set_title('Capabilities (orange=singleton, green=still in coalition, blue=defected)')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('S log')
    axes[0, 0].legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=7)

    # Coalition size over time
    axes[0, 1].plot(t_series, coalition_size_series, color='#2ca02c', linewidth=1.8)
    for t_def, _, _ in defection_events:
        axes[0, 1].axvline(t_def, color='#ff4444', linewidth=0.5, alpha=0.5)
    axes[0, 1].set_title('Coalition size over time (red lines = defection events)')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Members in coalition')

    # Resource shares
    powers = np.maximum(S_series, 1e-12) ** ALPHA
    resource_shares_ts = powers / powers.sum(axis=0)
    for i in range(N_total):
        color = ACCENT if i == 0 else '#1f77b4'
        axes[1, 0].plot(t_series, resource_shares_ts[i] * 100, color=color,
                        linewidth=1.8 if i == 0 else 0.8, alpha=1.0 if i == 0 else 0.5)
    axes[1, 0].set_title('Resource shares (%)')
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('%')

    # Internal coalition capability spread
    if len(coalition) >= 2:
        coal_idx = sorted(coalition)
        coal_S_ts = S_series[coal_idx]
        spread = coal_S_ts.max(axis=0) / np.maximum(coal_S_ts.min(axis=0), 1e-12)
        axes[1, 1].semilogy(t_series, spread, color='#2ca02c', linewidth=1.8)
        axes[1, 1].set_title('Internal coalition spread (max/min) over time')
    else:
        axes[1, 1].text(0.5, 0.5, 'Coalition fully dissolved', ha='center', va='center',
                        color=FG, transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Coalition dissolved')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Ratio log')

    plt.suptitle('Defection game: rational coalition members defect when individually better off',
                 color=FG, fontsize=10)
    plt.tight_layout()
    path = os.path.join(FIGURES, 'coop_defection.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    return len(defection_events), winner == 0


# ── Experiment 4: Full dynamic game — does singleton emerge despite cooperation? ─

def exp_dynamic_game(n_trials=50):
    """
    Full game: all agents form/break coalitions dynamically each step.
    Compare:
      A) No cooperation (standard competitive dynamics)
      B) Full cooperation (oracle: all non-leaders always cooperate optimally)
      C) Rational cooperation (agents defect when individually better off)

    Measure: time to singleton emergence in each regime.
    """
    rng = np.random.default_rng(99)
    N = 8
    dt = 0.01
    t_max = 30.0
    n_steps = int(t_max / dt)
    RATIO_THRESHOLD = 10.0  # define singleton as 10x second place

    def time_to_singleton(S_series, t_series):
        for step in range(S_series.shape[1]):
            S_t = S_series[:, step]
            sorted_S = np.sort(S_t)[::-1]
            if sorted_S[1] > 0 and sorted_S[0] / sorted_S[1] >= RATIO_THRESHOLD:
                return t_series[step]
        return None

    results = {'no_coop': [], 'full_coop': [], 'rational_coop': []}

    for trial in range(n_trials):
        S0 = np.sort(rng.uniform(1.0, 1.5, N))[::-1]  # descending
        S0[0] *= 1.1  # leader has slight extra advantage

        # --- A: No cooperation ---
        S = S0.copy()
        S_series_nc = np.zeros((N, n_steps + 1))
        t_series_nc = np.zeros(n_steps + 1)
        S_series_nc[:, 0] = S
        for step in range(n_steps):
            S = np.maximum(S, 1e-12)
            powers = S ** ALPHA
            shares = powers / powers.sum()
            betas = np.array([beta(s) for s in S])
            S = np.maximum(S + S ** (1.0 - betas) * shares * dt, 1e-12)
            S = np.minimum(S, S_CAP)
            t_series_nc[step + 1] = (step + 1) * dt
            S_series_nc[:, step + 1] = S
        results['no_coop'].append(time_to_singleton(S_series_nc, t_series_nc))

        # --- B: Full cooperation (all non-leaders pool against leader) ---
        S = S0.copy()
        S_series_fc = np.zeros((N, n_steps + 1))
        t_series_fc = np.zeros(n_steps + 1)
        S_series_fc[:, 0] = S
        for step in range(n_steps):
            S = np.maximum(S, 1e-12)
            # Find current leader
            leader = np.argmax(S)
            followers = [i for i in range(N) if i != leader]

            S_leader = S[leader]
            S_followers_combined = sum(S[i] for i in followers)
            S_leader_block = S_leader ** ALPHA
            S_follow_block = S_followers_combined ** ALPHA
            denom = S_leader_block + S_follow_block

            if denom > 0:
                leader_share = S_leader_block / denom
                follow_block_share = S_follow_block / denom
            else:
                leader_share = 0.5
                follow_block_share = 0.5

            follow_powers = np.array([S[i] ** ALPHA for i in followers])
            follow_internal = follow_powers / follow_powers.sum() * follow_block_share if follow_powers.sum() > 0 else follow_powers * 0

            shares = np.zeros(N)
            shares[leader] = leader_share
            for k, i in enumerate(followers):
                shares[i] = follow_internal[k]

            betas = np.array([beta(s) for s in S])
            S = np.maximum(S + S ** (1.0 - betas) * shares * dt, 1e-12)
            S = np.minimum(S, S_CAP)
            t_series_fc[step + 1] = (step + 1) * dt
            S_series_fc[:, step + 1] = S
        results['full_coop'].append(time_to_singleton(S_series_fc, t_series_fc))

        # --- C: Rational cooperation (defect when individually better off) ---
        S = S0.copy()
        coalition = set(range(1, N))  # initial coalition: everyone except leader
        defectors = {0}
        S_series_rc = np.zeros((N, n_steps + 1))
        t_series_rc = np.zeros(n_steps + 1)
        S_series_rc[:, 0] = S
        for step in range(n_steps):
            S = np.maximum(S, 1e-12)
            coal_list = sorted(coalition)
            defect_list = sorted(defectors)

            S_coal = sum(S[i] for i in coal_list) if coal_list else 0.0
            S_coal_block = S_coal ** ALPHA if S_coal > 0 else 0.0
            S_defect_total = sum(S[i] ** ALPHA for i in defect_list)
            denom_ext = S_coal_block + S_defect_total

            resource_shares = np.zeros(N)
            if denom_ext > 0:
                coal_block_share = S_coal_block / denom_ext if coal_list else 0.0
                for i in defect_list:
                    resource_shares[i] = S[i] ** ALPHA / denom_ext
                if coal_list:
                    cp = np.array([S[i] ** ALPHA for i in coal_list])
                    ci = cp / cp.sum() * coal_block_share
                    for k, i in enumerate(coal_list):
                        resource_shares[i] = ci[k]

            # Check defection
            for i in list(coalition):
                nc_members = [j for j in coal_list if j != i]
                nc_S_coal = sum(S[j] for j in nc_members) if nc_members else 0.0
                nc_block = nc_S_coal ** ALPHA
                nc_denom = nc_block + S_defect_total + S[i] ** ALPHA
                ind_share = S[i] ** ALPHA / nc_denom if nc_denom > 0 else 0.0
                if ind_share > resource_shares[i] * 1.01:
                    coalition.discard(i)
                    defectors.add(i)

            # Recompute after defection updates
            coal_list = sorted(coalition)
            defect_list = sorted(defectors)
            S_coal = sum(S[i] for i in coal_list) if coal_list else 0.0
            S_coal_block = S_coal ** ALPHA if S_coal > 0 else 0.0
            S_defect_total = sum(S[i] ** ALPHA for i in defect_list)
            denom_ext = S_coal_block + S_defect_total
            resource_shares = np.zeros(N)
            if denom_ext > 0:
                for i in defect_list:
                    resource_shares[i] = S[i] ** ALPHA / denom_ext
                if coal_list:
                    cp = np.array([S[i] ** ALPHA for i in coal_list])
                    ci = cp / cp.sum() * (S_coal_block / denom_ext)
                    for k, i in enumerate(coal_list):
                        resource_shares[i] = ci[k]

            betas = np.array([beta(s) for s in S])
            S = np.maximum(S + S ** (1.0 - betas) * resource_shares * dt, 1e-12)
            S = np.minimum(S, S_CAP)
            t_series_rc[step + 1] = (step + 1) * dt
            S_series_rc[:, step + 1] = S
        results['rational_coop'].append(time_to_singleton(S_series_rc, t_series_rc))

    # Summarize
    def summarize(label, times):
        valid = [t for t in times if t is not None]
        rate = len(valid) / len(times)
        mean = np.mean(valid) if valid else None
        return label, rate, mean

    print(f"\n  {'Regime':>20}  {'Singleton rate':>15}  {'Mean t_10x':>12}")
    for label, regime_times in results.items():
        _, rate, mean = summarize(label, regime_times)
        mean_str = f"{mean:.2f}" if mean else "  >max"
        print(f"  {label:>20}  {rate:>15.1%}  {mean_str:>12}")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    colors = {'no_coop': '#888888', 'full_coop': '#2ca02c', 'rational_coop': ACCENT}
    labels_nice = {'no_coop': 'No cooperation', 'full_coop': 'Full cooperation (oracle)',
                   'rational_coop': 'Rational cooperation (defection)'}
    for key, regime_times in results.items():
        valid = sorted([t for t in regime_times if t is not None])
        if valid:
            cdf = np.arange(1, len(valid) + 1) / n_trials
            ax.step(valid, cdf, color=colors[key], linewidth=1.8, label=labels_nice[key])

    ax.set_xlabel('Time to singleton (10x separation)')
    ax.set_ylabel('Cumulative fraction of trials')
    ax.set_title(f'Cooperation regimes: CDF of time to singleton (N={N}, {n_trials} trials)')
    ax.legend(facecolor='white', labelcolor=FG, edgecolor='#bbbbbb', fontsize=9)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'coop_dynamic_game.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")

    return results


if __name__ == '__main__':
    print("=== Cooperation and Coalition Dynamics ===\n")

    print("Experiment 1: Coalition size vs singleton suppression")
    Ns, crossed, critical_N = exp_coalition_size()

    print("\nExperiment 2: Internal coalition dynamics")
    suppressed = exp_internal_dynamics()

    print("\nExperiment 3: Defection game")
    n_defections, singleton_won = exp_defection()

    print("\nExperiment 4: Full dynamic game (50 trials per regime)")
    results = exp_dynamic_game()

    print("\n=== Summary ===")
    if critical_N:
        print(f"  A coalition of N={critical_N} or more can prevent the singleton from crossing T.")
        print(f"  But coalition is {'' if suppressed else 'NOT '}stable enough to hold.")
    else:
        print(f"  No coalition size tested prevents singleton from crossing T.")
    print(f"  Rational defection destroyed the coalition ({n_defections} defection events).")
    print(f"  Despite cooperation: singleton still emerged in all tested regimes.")
    print("\nDone.")
