"""
make_hero_gif.py

README hero animation. Two-panel dark-theme animation:
  Left:  capability S(t) on log scale, with glow-effect lines and a
         pulsing threshold marker that fires when an agent crosses T.
  Right: live ratio rho(t) = S1/S2, log scale, with a counter readout.

Designed to render well on GitHub dark mode (background #0d1117).
"""

from __future__ import annotations
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIG_DIR, exist_ok=True)
OUT = os.path.join(FIG_DIR, "hero.gif")

# ---------- model parameters ----------
ALPHA = 1.0
BETA_HIGH = 0.5
BETA_LOW = -0.3
T_THRESH = 5.0
STEEP = 5.0
S1_0 = 1.10
S2_0 = 1.00
S_CAP = 1e7
DT = 0.005
T_MAX = 7.0
FRAME_STRIDE = 7

# ---------- palette (GitHub dark mode friendly) ----------
BG = "#0d1117"          # GitHub dark canvas
PANEL = "#0d1117"
GRID = "#1f2731"
FG = "#c9d1d9"
MUTED = "#7d8590"
LEADER = "#ff7b35"      # warm orange for the agent that crosses
FOLLOWER = "#58a6ff"    # blue for the bounded agent
ACCENT = "#bc8cff"      # violet accent for ratio + flash


def beta_fn(S):
    return BETA_HIGH + (BETA_LOW - BETA_HIGH) / (1.0 + np.exp(-STEEP * (S - T_THRESH)))


def integrate():
    n = int(T_MAX / DT) + 1
    t = np.zeros(n)
    s1 = np.zeros(n)
    s2 = np.zeros(n)
    s1[0] = S1_0
    s2[0] = S2_0
    capped = False
    cross_idx = None
    for i in range(n - 1):
        t[i + 1] = t[i] + DT
        denom = max(s1[i], 1e-12) ** ALPHA + max(s2[i], 1e-12) ** ALPHA
        r1 = max(s1[i], 1e-12) ** ALPHA / denom
        r2 = max(s2[i], 1e-12) ** ALPHA / denom
        b1 = beta_fn(s1[i])
        b2 = beta_fn(s2[i])
        s1_new = s1[i] + DT * (s1[i] ** (1 - b1) * r1)
        s2_new = s2[i] + DT * (s2[i] ** (1 - b2) * r2)
        if cross_idx is None and s1[i] < T_THRESH <= s1_new:
            cross_idx = i + 1
        if not np.isfinite(s1_new) or s1_new > S_CAP:
            s1_new = S_CAP
            capped = True
        s1[i + 1] = s1_new
        s2[i + 1] = s2_new
        if capped:
            for j in range(i + 1, n):
                t[j] = t[j - 1] + DT
                s1[j] = S_CAP
                s2[j] = s2[i + 1]
            break
    return t, s1, s2, cross_idx


def style_axes(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=FG, labelsize=8)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.grid(True, color=GRID, lw=0.6, alpha=0.85)


def glow_plot(ax, x, y, color, lw=2.4, layers=4):
    """Return a list of line objects forming a glow-style trace."""
    lines = []
    for k in range(layers, 0, -1):
        ln, = ax.plot(x, y, color=color, lw=lw * k, alpha=0.06 if k > 1 else 0.0,
                      solid_capstyle="round")
        lines.append(ln)
    core, = ax.plot(x, y, color=color, lw=lw, alpha=1.0, solid_capstyle="round")
    lines.append(core)
    return lines


def update_glow(lines, x, y):
    for ln in lines:
        ln.set_data(x, y)


def main():
    t, s1, s2, cross_idx = integrate()
    rho = s1 / np.maximum(s2, 1e-12)
    idx = np.arange(0, len(t), FRAME_STRIDE)

    fig = plt.figure(figsize=(9.6, 4.6), facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.28,
                          left=0.08, right=0.97, top=0.86, bottom=0.16)
    ax_cap = fig.add_subplot(gs[0, 0])
    ax_rho = fig.add_subplot(gs[0, 1])

    fig.suptitle(
        r"Singleton attractor:  finite-time separation under the $\beta$-threshold",
        color=FG, fontsize=12.5, y=0.965,
    )

    # capability panel
    style_axes(ax_cap)
    ax_cap.set_yscale("log")
    ax_cap.set_xlim(0, T_MAX)
    ax_cap.set_ylim(0.5, S_CAP * 2)
    ax_cap.set_xlabel("time")
    ax_cap.set_ylabel("capability $S(t)$  (log)")
    ax_cap.axhline(T_THRESH, color=MUTED, lw=0.8, ls="--", alpha=0.7)
    ax_cap.text(T_MAX * 0.015, T_THRESH * 1.18, "threshold T",
                color=MUTED, fontsize=8.5)

    leader_lines = glow_plot(ax_cap, [], [], LEADER)
    follower_lines = glow_plot(ax_cap, [], [], FOLLOWER)
    leader_dot, = ax_cap.plot([], [], "o", color=LEADER, ms=8,
                              markeredgecolor=BG, mew=1.0, zorder=5)
    follower_dot, = ax_cap.plot([], [], "o", color=FOLLOWER, ms=8,
                                markeredgecolor=BG, mew=1.0, zorder=5)
    flash, = ax_cap.plot([], [], "o", color=ACCENT, ms=20,
                         alpha=0.0, markeredgewidth=0, zorder=4)
    cross_label = ax_cap.text(0, 0, "", color=ACCENT, fontsize=9.5,
                              ha="center", va="bottom", alpha=0.0,
                              fontweight="bold")

    legend = ax_cap.legend([leader_lines[-1], follower_lines[-1]],
                           ["leader  ($S_1$, crosses $T$)",
                            "follower ($S_2$, bounded)"],
                           loc="upper left", fontsize=8.5,
                           facecolor="#161b22", edgecolor="#30363d",
                           labelcolor=FG, framealpha=0.95)

    # ratio panel
    style_axes(ax_rho)
    ax_rho.set_yscale("log")
    ax_rho.set_xlim(0, T_MAX)
    ax_rho.set_ylim(1.0, S_CAP * 2)
    ax_rho.set_xlabel("time")
    ax_rho.set_ylabel(r"$\rho(t) = S_1 / S_2$")
    ax_rho.set_title("Capability ratio  (diverges in finite time)",
                     fontsize=10.5, pad=8)
    ratio_lines = glow_plot(ax_rho, [], [], ACCENT, lw=2.6)
    ratio_dot, = ax_rho.plot([], [], "o", color=ACCENT, ms=8,
                             markeredgecolor=BG, mew=1.0, zorder=5)

    counter = fig.text(
        0.97, 0.04, "",
        ha="right", va="bottom",
        color=FG, fontsize=10.5, fontfamily="monospace",
        bbox=dict(facecolor="#161b22", edgecolor="#30363d",
                  boxstyle="round,pad=0.4", alpha=0.95),
    )

    cross_t = t[cross_idx] if cross_idx is not None else None

    def update(k):
        i = idx[k]
        update_glow(leader_lines, t[: i + 1], s1[: i + 1])
        update_glow(follower_lines, t[: i + 1], s2[: i + 1])
        update_glow(ratio_lines, t[: i + 1], rho[: i + 1])
        leader_dot.set_data([t[i]], [s1[i]])
        follower_dot.set_data([t[i]], [s2[i]])
        ratio_dot.set_data([t[i]], [rho[i]])

        # threshold-cross flash + label
        if cross_t is not None:
            dt_since_cross = t[i] - cross_t
            if 0.0 <= dt_since_cross <= 1.2:
                fade = max(0.0, 1.0 - dt_since_cross / 1.2)
                flash.set_data([cross_t], [T_THRESH])
                flash.set_alpha(fade * 0.9)
                cross_label.set_position((cross_t, T_THRESH * 1.6))
                cross_label.set_text("β flips negative")
                cross_label.set_alpha(min(1.0, fade * 1.3))
            else:
                flash.set_alpha(0.0)
                cross_label.set_alpha(0.0)
        counter.set_text(
            f"t = {t[i]:5.2f}     S1 = {s1[i]:9.2e}     "
            f"S2 = {s2[i]:6.3f}     ρ = {rho[i]:9.2e}"
        )
        return (*leader_lines, *follower_lines, *ratio_lines,
                leader_dot, follower_dot, ratio_dot, flash, cross_label, counter)

    anim = FuncAnimation(fig, update, frames=len(idx), interval=55, blit=False)
    writer = PillowWriter(fps=18)
    anim.save(OUT, writer=writer, dpi=110, savefig_kwargs={"facecolor": BG})
    print(f"Wrote {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
