# Findings

Running log of confirmed simulation results. Each entry includes the parameter values that produced it. Findings are numbered and not edited after confirmation — new entries append only.

---

## F1: Growth equation verification

**Source:** `simulations/intelligence_explosion.py`, Experiment 2

The analytical solution to dS/dt = S^(1-β) matches numerical integration across all tested β values.

Theoretical time to reach S=10^5 from S=1: t = (S_MAX^β - 1) / β.

| β | t* (theory) | t* (numerical) | error |
|---|---|---|---|
| -0.10 | 6.8377 | 6.8377 | 0.000% |
| -0.20 | 4.5000 | 4.5000 | 0.000% |
| -0.30 | 3.2279 | 3.2279 | 0.000% |
| -0.50 | 1.9937 | 1.9937 | 0.000% |
| -0.75 | 1.3331 | 1.3331 | 0.000% |
| -1.00 | 1.0000 | 1.0000 | 0.000% |

Max error: 0.000% at rtol=1e-9, atol=1e-11.

Growth regime transitions confirmed: β < 0 produces finite-time singularity, β = 0 produces exponential, β > 0 produces subexponential (power law).

---

## F2: Competitive exclusion from marginal advantage

**Source:** `simulations/competition.py`, Experiments 1-3

Two-agent system with shared resources. Initial advantage as small as 1% produces diverging ratio.

Parameters: α=1.0, β=0.5 (subexponential, no threshold).

| Initial gap | Ratio diverges? |
|---|---|
| +1% | Yes |
| +5% | Yes |
| +10% | Yes |
| +25% | Yes |
| +50% | Yes |
| +100% | Yes |

All initial gaps tested produce rho = S1/S2 → inf. Even in the subexponential regime (β=0.5), the ratio diverges given enough time. This confirms the Lotka-Volterra competitive exclusion mechanism holds in the capability dynamics model.

Alpha sensitivity: separation rate increases monotonically with α. Higher resource-capability coupling → faster divergence.

---

## F3: Beta-threshold accelerates separation

**Source:** `simulations/competition.py`, Experiment 4

Parameters: α=1.0, S1(0)=1.1, S2(0)=1.0, threshold T=5, β_high=0.5, β_low=-0.3.

Comparison at t=6.8:
- Flat β=0.5 (no threshold): ratio = 1.55
- Threshold β (β_low=-0.3 above T=5): ratio = 19,336,447

Threshold crossing accelerates separation by **12.4 million times** in the same time interval.

The mechanism: once agent 1 crosses T and enters β < 0 territory, its growth becomes superexponential. Agent 2, still below T, remains in subexponential growth. The ratio reaches near-infinity in finite time while it would take t → inf in the flat-β case.

---

## F4: Winner identity — N-agent

**Source:** `simulations/agents.py`, Experiments 1-2

N=10 agents, capabilities drawn from uniform [1, 3]. 200 independent trials.

**Winner = initial leader: 200/200 (100.0%)**

Parameters: α=1.0, β=0.5. The result is deterministic: initial conditions determine the winner. There is no observed case where a non-leading agent overtook the initial leader.

This holds at N=5 with verified examples as well.

---

## F5: Elimination order is weakest-first

**Source:** `simulations/agents.py`, Experiment 3

N=8 agents, threshold β (β_high=0.5, β_low=-0.2, T=3.0), α=1.0.

Elimination order by time of resource share dropping below 5%:

| Elimination order | Initial rank from weakest | S0 | Time |
|---|---|---|---|
| 1st eliminated | 1 (weakest) | 1.005 | t=7.82 |
| 2nd | 2 | 1.225 | t=9.16 |
| 3rd | 3 | 1.300 | t=9.52 |
| 4th | 4 | 1.625 | t=11.38 |
| 5th | 5 | 1.776 | t=12.38 |
| 6th | 6 | 1.821 | t=12.66 |
| 7th | 7 | 1.874 | t=13.08 |
| Winner | 8 (strongest) | 1.897 | — |

Elimination order is strictly weakest-first. This confirms the inductive argument in `derivations.md` Section 4: the system reduces sequentially from the bottom, not from random elimination.

---

## F6: Alpha-separation monotonicity

**Source:** `simulations/run_experiments.py`, Experiment 1

30 trials per alpha value. Two-agent threshold β. Separation measured at t=15.

| α | Mean separation ratio |
|---|---|
| 0.25 | 36,448x |
| 0.64 | 178,818x |
| 1.04 | 299,515x |
| 1.43 | 364,163x |
| 1.82 | 449,366x |
| 2.21 | 492,384x |
| 3.00 | 541,016x |

Separation ratio increases monotonically with α across all tested values. Higher resource-capability coupling always produces faster singleton emergence. No evidence of a saturation ceiling within the tested range (α up to 3.0).

---

## F7: Winner identity is robust to initial spread

**Source:** `simulations/run_experiments.py`, Experiment 3

N=5, threshold β, α=1.0, 50 trials per sigma value.

| Sigma (initial spread) | Winner = initial leader | Mean time to 10x ratio |
|---|---|---|
| 0.001 (nearly identical) | 100% | 15.43 |
| 0.005 | 100% | 14.13 |
| 0.010 | 100% | 13.23 |
| 0.050 | 100% | 10.58 |
| 0.100 | 100% | 9.69 |
| 0.250 | 100% | 7.46 |
| 0.500 | 100% | 5.38 |

Winner identity holds at 100% for all tested spreads, including near-identical initial capabilities (sigma=0.001). Tighter initial spread slows convergence but does not prevent it.

This is the closest test of Assumption A5 (initial heterogeneity). Even vanishingly small initial differences produce eventual singleton. In a physical system with any noise, A5 will always hold.

---

## F8: Niche partitioning does not prevent singleton — unexpected result

**Source:** `simulations/run_experiments.py`, Experiment 4

**Prediction from derivations.md Section 5:** Niche partitioning should produce stable oligopoly when agents compete for non-overlapping resources.

**Result:** Singleton persists at ALL tested overlap levels, including overlap=0.0 (fully separate niches).

| Resource overlap | Mean separation ratio at t=15 |
|---|---|
| 0.00 (no shared resource) | 1,103x |
| 0.10 | 3,612x |
| 0.20 | 15,357x |
| 0.50 | 85,290x |
| 1.00 (fully shared) | 265,477x |

At zero overlap, separation reaches 1,103x — less than full competition but still enormous. No oligopoly threshold found.

**Explanation:** Failure mode F1 assumed separate niches prevent competitive exclusion. This holds for the Lotka-Volterra mechanism alone (resource competition). However, with the β-threshold present, niche separation doesn't prevent singleton because: the agent with higher initial capability crosses threshold T first and enters superexponential growth regardless of whether resources are shared. Once in the β < 0 regime, capability diverges in finite time independent of resource competition.

**Implication:** Failure mode F1 requires more than separate resource pools. It requires that agents operate in genuinely different β regimes — i.e., different fundamental limits on self-improvement. If two agents share the same β function (same growth ceiling), the one that crosses the threshold first becomes the singleton even without resource competition.

**Revision to formal claim:** The theorem holds under a weaker version of A3. Full resource competition is not required. Sufficient conditions are: (1) A1 (recursive self-improvement), (2) A4 (β-threshold exists and is reachable), (3) A5 (initial heterogeneity). A2 and A3 accelerate singleton emergence but are not the primary driver.

This is the most significant finding from the sweep.

---

## F9: Beta threshold position and depth

**Source:** `simulations/run_experiments.py`, Experiment 2

Heatmap sweep over β_low in [-0.05, -1.0] and threshold T in [2.0, 8.0].

- Maximum separation: 591,065x at β_low=-1.0, T=2.0 (lowest threshold, deepest flip)
- Minimum separation: 1,179x at β_low=-0.05, T=8.0 (highest threshold, shallowest flip)

The minimum (1,179x) is still substantial. Even the weakest β-flip tested produces >1000x separation.

Lower threshold position (T closer to initial capability) accelerates onset. Deeper β_low (more negative) accelerates growth once past threshold. Both parameters increase separation independently.

---

## Open questions from findings

**OQ1:** If niche partitioning doesn't prevent singleton when agents share the same β function, what happens when agents have fundamentally different β functions? E.g., one agent saturates at β=0.5 while the other can achieve β=-0.3. This is the true test of F1.

**OQ2:** N scaling: for N ≥ 30 in subexponential regime, time to 10x ratio exceeds 500. With threshold β, convergence is much faster. The paper should distinguish timescales between the two regimes.

**OQ3:** Stochastic noise: all experiments are deterministic. Need to verify noise doesn't prevent singleton. Prediction: noise affects only which agent wins (in near-tie initial conditions), not whether a singleton emerges.
