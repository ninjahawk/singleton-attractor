"""
make_hero_gif.py

Generate the README hero animation: two agents under the threshold-beta
dynamics, one crossing T and entering finite-time blow-up, the other
remaining sub-exponential. Saved as figures/hero.gif.
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

# parameters
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
FRAME_STRIDE = 8  # downsample for gif


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
    for i in range(n - 1):
        t[i + 1] = t[i] + DT
        denom = max(s1[i], 1e-12) ** ALPHA + max(s2[i], 1e-12) ** ALPHA
        r1 = max(s1[i], 1e-12) ** ALPHA / denom
        r2 = max(s2[i], 1e-12) ** ALPHA / denom
        b1 = beta_fn(s1[i])
        b2 = beta_fn(s2[i])
        s1_new = s1[i] + DT * (s1[i] ** (1 - b1) * r1)
        s2_new = s2[i] + DT * (s2[i] ** (1 - b2) * r2)
        if s1_new > S_CAP or not np.isfinite(s1_new):
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
    return t, s1, s2


def main():
    t, s1, s2 = integrate()
    idx = np.arange(0, len(t), FRAME_STRIDE)

    fig, ax = plt.subplots(figsize=(7.2, 4.0), facecolor="white")
    ax.set_facecolor("white")
    ax.set_yscale("log")
    ax.set_xlim(0, T_MAX)
    ax.set_ylim(0.5, S_CAP * 2)
    ax.axhline(T_THRESH, color="#888", lw=0.8, ls="--", alpha=0.7)
    ax.text(
        T_MAX * 0.02,
        T_THRESH * 1.15,
        f"capability threshold T = {T_THRESH:.0f}",
        color="#555",
        fontsize=8,
    )
    ax.set_xlabel("time")
    ax.set_ylabel("capability $S(t)$ (log scale)")
    ax.set_title(
        r"Finite-time separation under the $\beta$-threshold mechanism",
        fontsize=10,
    )
    ax.grid(alpha=0.3)

    (line1,) = ax.plot([], [], color="#ff6b35", lw=2.2, label="leader")
    (line2,) = ax.plot([], [], color="#1f77b4", lw=2.2, label="follower")
    (dot1,) = ax.plot([], [], "o", color="#ff6b35", ms=6)
    (dot2,) = ax.plot([], [], "o", color="#1f77b4", ms=6)
    text = ax.text(
        0.98,
        0.04,
        "",
        ha="right",
        va="bottom",
        transform=ax.transAxes,
        fontsize=9,
        color="#333",
        bbox=dict(facecolor="white", edgecolor="#ccc", boxstyle="round,pad=0.3"),
    )
    ax.legend(loc="upper left", fontsize=9, frameon=True)

    def update(k):
        i = idx[k]
        line1.set_data(t[: i + 1], s1[: i + 1])
        line2.set_data(t[: i + 1], s2[: i + 1])
        dot1.set_data([t[i]], [s1[i]])
        dot2.set_data([t[i]], [s2[i]])
        ratio = s1[i] / max(s2[i], 1e-12)
        text.set_text(f"t = {t[i]:5.2f}    ratio = {ratio:,.1f}×")
        return line1, line2, dot1, dot2, text

    anim = FuncAnimation(fig, update, frames=len(idx), interval=50, blit=True)
    writer = PillowWriter(fps=18)
    anim.save(OUT, writer=writer, dpi=110)
    print(f"Wrote {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
