"""
continuous_entry.py

Tests OQ6: can continuous agent entry prevent singleton emergence?

Model:
  - Incumbent starts at t=0
  - At each step, new agents enter at rate lambda (Poisson process)
  - Entry capability drawn from Pareto distribution (heavy tail — tests extreme entrants)
  - Run for t_max, track whether incumbent maintains dominance

Questions:
  1. At what entry rate does the incumbent start losing?
  2. Does moat growth rate outpace entry threat rate?
  3. Phase diagram: entry rate vs entry capability distribution -> incumbent survival
  4. Is there a safe lambda threshold above which F3 is always a concern?
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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


def sigmoid_beta(beta_low=-0.3, beta_high=0.5, threshold=3.0, steepness=5.0):
    def fn(S):
        return beta_high + (beta_low - beta_high) / (1.0 + np.exp(-steepness * (S - threshold)))
    return fn


def euler_step(S, alpha, beta_fn, dt, resource_shares=None):
    n = len(S)
    S = np.maximum(S, 1e-12)
    if resource_shares is None:
        powers = S ** alpha
        resource_shares = powers / powers.sum()
    betas = np.array([beta_fn(s) for s in S])
    dS = S ** (1.0 - betas) * resource_shares * dt
    return np.maximum(S + dS, 1e-12)


def run_continuous_entry(S_inc_0, alpha, beta_fn, lam, pareto_scale,
                          pareto_shape, t_max=30.0, dt=0.01, rng=None):
    """
    Simulate incumbent vs continuous entry stream.

    Entry process: Poisson(lambda * dt) new agents per step.
    Entry capability: Pareto(scale, shape) — heavy tail.
    Agents are removed when their resource share < 0.1% (effectively dead).

    Returns: (incumbent_survived, t_first_loss, peak_n_agents)
    """
    if rng is None:
        rng = np.random.default_rng()

    agents = np.array([S_inc_0])  # index 0 = incumbent
    n_steps = int(t_max / dt)
    incumbent_survived = True
    t_first_loss = None
    peak_n = 1

    for step in range(n_steps):
        t = step * dt
        n = len(agents)

        # Entry: Poisson number of new agents this step
        n_new = rng.poisson(lam * dt)
        if n_new > 0:
            new_caps = pareto_scale * (rng.pareto(pareto_shape, n_new) + 1)
            agents = np.concatenate([agents, new_caps])

        agents = np.maximum(agents, 1e-12)
        if len(agents) > peak_n:
            peak_n = len(agents)

        # Step all agents
        powers = agents ** alpha
        total = powers.sum()
        if total == 0:
            break
        resource_shares = powers / total
        betas = np.array([beta_fn(s) for s in agents])
        dS = agents ** (1.0 - betas) * resource_shares * dt
        agents = np.maximum(agents + dS, 1e-12)

        # Cap
        if agents.max() > S_CAP:
            agents = np.minimum(agents, S_CAP)

        # Prune dead agents (resource share < 0.1%)
        powers = agents ** alpha
        shares = powers / powers.sum()
        alive = shares >= 0.001
        if not alive[0]:
            incumbent_survived = False
            if t_first_loss is None:
                t_first_loss = t
            break
        agents = agents[alive]

    # Final check
    if agents[0] != agents.max():
        incumbent_survived = False
        if t_first_loss is None:
            t_first_loss = t_max

    return incumbent_survived, t_first_loss, peak_n


# ── Experiment 1: lambda sweep ─────────────────────────────────────────────────

def exp_lambda_sweep(n_trials=100):
    beta_fn = sigmoid_beta()
    alpha = 1.0
    pareto_scale = 1.0   # entrants start at ~1x incumbent's origin
    pareto_shape = 2.0   # shape=2: E[X]=2, heavy tail but finite mean

    lambdas = np.logspace(-2, 1, 16)  # 0.01 to 10 per unit time
    survival_rates = []

    print(f"  {'lambda':>9}  {'survival rate':>14}  {'mean peak agents':>18}")
    for lam in lambdas:
        rng = np.random.default_rng(int(lam * 1000))
        survived = 0
        peak_ns = []
        for _ in range(n_trials):
            s, _, peak = run_continuous_entry(
                1.0, alpha, beta_fn, lam, pareto_scale, pareto_shape,
                t_max=30.0, dt=0.01, rng=rng
            )
            if s:
                survived += 1
            peak_ns.append(peak)
        rate = survived / n_trials
        survival_rates.append(rate)
        print(f"  {lam:>9.4f}  {rate:>14.1%}  {np.mean(peak_ns):>18.1f}")

    # Find critical lambda
    critical = None
    for lam, sr in zip(lambdas, survival_rates):
        if sr < 0.90:
            critical = lam
            break
    if critical:
        print(f"\n  Survival drops below 90% at lambda ~ {critical:.4f}")
    else:
        print(f"\n  Survival stays above 90% at all tested lambda values")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    ax.semilogx(lambdas, [r * 100 for r in survival_rates], color=ACCENT,
                linewidth=1.8, marker='o', markersize=6)
    ax.axhline(90, color='#555555', linestyle='--', linewidth=1, label='90% threshold')
    ax.axhline(50, color='#333333', linestyle=':', linewidth=1, label='50% (chance)')
    ax.set_xlabel('Entry rate lambda (agents per time unit)')
    ax.set_ylabel('Incumbent survival rate (%)')
    ax.set_title(f'Continuous entry: incumbent survival vs entry rate\n(Pareto entrants, scale={pareto_scale}, shape={pareto_shape}, {n_trials} trials)')
    ax.set_ylim(0, 105)
    ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'ce_lambda_sweep.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")
    return lambdas, survival_rates, critical


# ── Experiment 2: entry capability distribution sweep ─────────────────────────

def exp_capability_sweep(n_trials=100):
    """
    Fix lambda=1.0. Vary Pareto shape (tail heaviness) and scale (base capability).
    Shape: lower = heavier tail = more extreme entrants.
    """
    beta_fn = sigmoid_beta()
    alpha = 1.0
    lam = 1.0

    # Vary scale (how capable entrants typically are)
    scales = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
    shapes = [1.5, 2.0, 3.0]  # heavy, medium, light tail

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG)
    style_ax(ax)

    palette = [ACCENT, '#2ca02c', '#1f77b4']
    print(f"\n  Lambda=1.0 — survival rate by entry scale and tail shape")
    print(f"  {'scale':>7}  {'shape=1.5':>12}  {'shape=2.0':>12}  {'shape=3.0':>12}")

    all_rows = []
    for shape, color in zip(shapes, palette):
        rates = []
        for scale in scales:
            rng = np.random.default_rng(int(scale * 100 + shape * 10))
            survived = sum(
                run_continuous_entry(1.0, alpha, beta_fn, lam, scale, shape,
                                     t_max=30.0, dt=0.01, rng=rng)[0]
                for _ in range(n_trials)
            )
            rates.append(survived / n_trials)
        all_rows.append(rates)
        ax.plot(scales, [r * 100 for r in rates], color=color, linewidth=1.8,
                marker='o', markersize=6, label=f'shape={shape}')

    ax.axhline(90, color='#555555', linestyle='--', linewidth=1, label='90%')
    ax.set_xlabel('Entry scale (Pareto scale parameter ~ mean entrant capability)')
    ax.set_ylabel('Incumbent survival rate (%)')
    ax.set_title(f'Continuous entry: survival vs entry capability\n(lambda=1.0, {n_trials} trials per point)')
    ax.set_ylim(0, 105)
    ax.legend(facecolor='#111111', labelcolor=FG, edgecolor='#333333', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIGURES, 'ce_capability_sweep.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {path}")

    for scale, r15, r20, r30 in zip(scales, all_rows[0], all_rows[1], all_rows[2]):
        print(f"  {scale:>7.1f}  {r15:>12.1%}  {r20:>12.1%}  {r30:>12.1%}")

    return scales, all_rows


# ── Experiment 3: phase diagram lambda vs scale ────────────────────────────────

def exp_phase_diagram(n_trials=60):
    beta_fn = sigmoid_beta()
    alpha = 1.0
    pareto_shape = 2.0

    lambdas = np.logspace(-1.5, 1, 12)
    scales = np.logspace(-0.3, 1.2, 10)

    phase = np.zeros((len(lambdas), len(scales)))

    for i, lam in enumerate(lambdas):
        for j, scale in enumerate(scales):
            rng = np.random.default_rng(i * 100 + j)
            survived = sum(
                run_continuous_entry(1.0, alpha, beta_fn, lam, scale, pareto_shape,
                                     t_max=30.0, dt=0.01, rng=rng)[0]
                for _ in range(n_trials)
            )
            phase[i, j] = survived / n_trials

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    im = ax.imshow(phase, aspect='auto', origin='lower', cmap='RdYlGn',
                   extent=[np.log10(scales[0]), np.log10(scales[-1]),
                           np.log10(lambdas[0]), np.log10(lambdas[-1])],
                   vmin=0, vmax=1)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Incumbent survival rate', color=FG)
    cbar.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)

    ax.set_xlabel('log10(entry scale)')
    ax.set_ylabel('log10(entry rate lambda)')
    ax.set_title('Continuous entry phase diagram\nGreen=incumbent survives, Red=incumbent loses')
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    ax.tick_params(colors=FG)

    # 90% contour
    try:
        cs = ax.contour(
            np.log10(scales), np.log10(lambdas), phase,
            levels=[0.9], colors=['white'], linewidths=[1.5]
        )
        ax.clabel(cs, fmt='90%%', colors='white', fontsize=9)
    except Exception:
        pass

    plt.tight_layout()
    path = os.path.join(FIGURES, 'ce_phase_diagram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"\n  Saved: {path}")

    return phase, lambdas, scales


if __name__ == '__main__':
    print("=== Continuous Entry Model ===\n")

    print("Experiment 1: Lambda sweep (100 trials per lambda)")
    lambdas, survival_rates, critical = exp_lambda_sweep()

    print("\nExperiment 2: Entry capability sweep")
    exp_capability_sweep()

    print("\nExperiment 3: Phase diagram lambda vs capability scale")
    exp_phase_diagram()

    print("\nDone.")
