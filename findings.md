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

**OQ1:** If niche partitioning doesn't prevent singleton when agents share the same β function, what happens when agents have fundamentally different β functions? E.g., one agent saturates at β=0.5 while the other can achieve β=-0.3. This is the true test of F1. → Answered by F10-F12.

**OQ2:** N scaling: for N ≥ 30 in subexponential regime, time to 10x ratio exceeds 500. With threshold β, convergence is much faster. The paper should distinguish timescales between the two regimes.

**OQ3:** Stochastic noise: all experiments are deterministic. Need to verify noise doesn't prevent singleton. Prediction: noise affects only which agent wins (in near-tie initial conditions), not whether a singleton emerges. → Answered by F13-F14.

---

## F10: Asymmetric ceiling — threshold agent vs flat agent

**Source:** `simulations/beta_regimes.py`, Case B

Agent 1: sigmoid threshold β (β_low=-0.3 above T=3). Agent 2: flat β=0.5 (never reaches superexponential).

The threshold agent (Agent 1) defeats the flat agent (Agent 2) unless Agent 2 starts more than **2.9x** ahead. Above 2.9x initial disadvantage, Agent 2 monopolizes resources before Agent 1 can reach threshold T=3, and Agent 1 never enters superexponential growth.

**The mechanism of Agent 2 winning:** Not that β=0.5 competes effectively with β=-0.3. It is that a large enough resource monopoly starves Agent 1 before the threshold is reached. If Agent 1 could reach T=3, it would win. The question is whether it gets enough resource to grow at all.

**Key implication:** Flat-β agents cannot win by being "more capable" — they can only win by preventing the threshold agent from crossing its threshold. This is a starvation mechanism, not a competitive capability mechanism.

---

## F11: Threshold race — lower threshold wins, but advantage is small

**Source:** `simulations/beta_regimes.py`, Case C

Both agents have sigmoid threshold β, identical β_low=-0.3 and β_high=0.5. T1=3, T2=5.

- Equal starts: Agent 1 (lower threshold) wins in all tested configurations (T1 from 1.5 to 4.9, T2=5.0 fixed).
- Agent 1 can overcome at most **1.19x initial disadvantage** against Agent 2 (T2=T1+2).

The lower-threshold advantage is much smaller than the asymmetric-ceiling advantage (F10: 2.9x). Both agents can eventually enter superexponential growth, so Agent 1's crossing-first window is limited. If Agent 2 starts far enough ahead, it gets enough resource share to race past its threshold (T2) before Agent 1 reaches T1.

---

## F12: Phase diagram — threshold gap vs initial position

**Source:** `simulations/beta_regimes.py`, Case D

Phase diagram: Agent 1 (T=2.0) vs Agent 2 (T=2.0+gap). Varied initial capability ratio and threshold gap.

| T2-T1 | Max S2(0)/S1(0) where Agent 1 still wins |
|---|---|
| 0.50 | 0.79x (Agent 1 must start ahead) |
| 0.92 | 1.08x |
| 3.04 | 1.08x |
| 3.88 | 1.47x |
| 6.00 | 1.47x |

The relationship is step-function, not linear. Small threshold gaps (<0.5 units) provide no advantage unless Agent 1 already starts ahead. Larger gaps (≥0.92) allow a modest ~1.08x compensation. Very large gaps (≥3.88) allow ~1.47x compensation. The advantage plateaus — larger threshold gaps beyond ~4 units do not provide proportionally more compensation.

---

## F13: Stochastic noise does not prevent singleton

**Source:** `simulations/stochastic.py`, Experiment 2

300 trials per sigma level. Two-agent threshold β (T=3, β_low=-0.3, β_high=0.5). S1(0)=1.1, S2(0)=1.0.

| Sigma | Winner = initial leader | Singleton emerges (ratio >10x) |
|---|---|---|
| 0.001 | 100% | 100% |
| 0.013 | 100% | 100% |
| 0.026 | 98% | 100% |
| 0.038 | 89% | 100% |
| 0.079 | 74% | 100% |
| 0.113 | 66% | 100% |
| 0.234 | 58% | 100% |
| 0.336 | 53% | 100% |
| 0.695 | 50% | 100% |
| 1.000 | 47% | 100% |

**Singleton emergence rate is 100% at every tested noise level.** Noise randomizes which agent wins (winner identity drops to chance at sigma≈0.23) but never prevents a singleton from forming. The β-flip produces such overwhelming separation that even large noise cannot suppress the ratio below 10x.

**Interpretation:** Noise affects the winner-selection phase (which agent gets the first threshold crossing) but not the dominance phase (what happens after). Once any agent crosses the threshold under any level of noise, it dominates absolutely.

---

## F14: Near-equal starts under noise — winner becomes random at low sigma

**Source:** `simulations/stochastic.py`, Experiment 3

S1(0)=1.01, S2(0)=1.0 (1% gap). 500 trials per noise level.

| Sigma | Winner = initial leader |
|---|---|
| 0.00 | 100% |
| 0.05 | 53.6% |
| 0.10 | 52.2% |
| 0.30 | 51.6% |
| 0.50 | 52.6% |

A 1% initial gap is completely overwhelmed by sigma≥0.05 noise. Outcome is essentially random (≈50%) for all sigma>0. This shows that the winner-determination threshold scales with the initial gap — larger gaps survive larger noise.

---

## F15: Late entrant moat grows superexponentially after threshold crossing

**Source:** `simulations/late_entrant.py`, Experiment 3

Incumbent starts at S=1.0, crosses beta threshold (T=3) at t=1.404.

| Time after threshold crossing | Max entrant capability incumbent can defeat |
|---|---|
| 0.00 | 3.0 |
| 1.05 | 19.0 |
| 2.11 | 2,356 |
| 3.16 | >1,000,000 |
| 4.21 | >1,000,000 |

At threshold crossing, the incumbent can defeat entrants starting at 3x its original capability. 3 time units later, the moat exceeds 1,000,000x. The moat grows at least as fast as the incumbent's capability — superexponentially.

**This makes F3 (late entrant) a threat only during the pre-threshold window.** Once threshold is crossed, no realistic entrant with any tested capability can displace the incumbent. F3 is bounded in time, not persistent.

---

## F16: Pre-threshold phase diagram confirms F3 window

**Source:** `simulations/late_entrant.py`, Experiment 2

With head start t0 up to 3.9 (just before threshold crossing at t=1.4, after accounting for approach dynamics):

| t0 | S_inc at entry | Max entrant defeated |
|---|---|---|
| 0.5 | 1.56 | 1.4 |
| 1.2 | 2.54 | 2.1 |
| 1.9 | 5.67 | 4.3 |
| 2.5 | 22.8 | 18.3 |
| 3.2 | 261 | 234 |
| 3.9+ | >1e8 (cap) | >1,000 (tested range) |

Before threshold: max defeatable entrant tracks roughly 0.8x incumbent's current capability — incumbent cannot overcome a co-equal entrant. After threshold: moat grows without bound.

---

---

## F17: Timescale scaling formula

**Source:** `simulations/timescale.py`

Measured singleton emergence timescales (t_10x, t_dom) across parameter sweeps. Power-law fits.

| Parameter | Effect on t_10x | Fit exponent |
|---|---|---|
| alpha (resource coupling) | Higher -> faster | alpha^(-0.30) |
| gap (initial advantage) | Larger -> faster | gap^(-0.15) |
| N (agent count) | More -> slower | N^(+0.96) |
| beta_low (threshold depth) | Deeper -> faster | |beta_low|^(-0.31) |

**Combined formula:**
```
t_10x ~ 2.44 * N^0.96 * alpha^(-0.30) * gap^(-0.15) * |beta_low|^(-0.31)
```

(C absorbs threshold position T and beta_high. Fits are independent single-variable power laws; combined formula assumes multiplicative independence.)

**Key results:**
- N scales almost exactly linearly (N^0.96 ≈ N). More agents = proportionally more time.
- Gap has the weakest effect (gap^-0.15). Doubling gap reduces time by only 11%. The threshold mechanism dominates over initial conditions.
- t_10x ≈ t_100x ≈ t_dom for all parameters tested. Once 10x separation is reached, dominance is near-immediate — superexponential growth collapses all subsequent milestones together.

---

## F18: Continuous entry — critical entry rate lambda_crit ≈ 0.25

**Source:** `simulations/continuous_entry.py`, Experiment 1

Entry model: Poisson arrivals at rate lambda, Pareto(shape=2) capabilities.

| Lambda | Incumbent survival |
|---|---|
| 0.01 | 99% |
| 0.10 | 97% |
| 0.25 | 88% |
| 0.40 | 73% |
| 0.63 | 60% |
| 1.00 | 48% |
| 2.51 | 9% |
| 6.31 | 0% |

Survival drops below 90% at lambda ≈ 0.25. At lambda = 1.0, outcome is essentially random (48%). At lambda ≥ 6.3, incumbent never survives.

**Mechanism:** The critical window is pre-threshold. At lambda = 1.0, mean peak competitor count reaches 5 agents simultaneously, which distributes resources widely enough to prevent any agent from accumulating the resources needed to reach threshold T first.

**Interaction with moat (F15):** Post-threshold, even high lambda is survivable because the moat exceeds 10^6 within 3 time units of crossing. The lambda_crit figure characterizes pre-threshold fragility only.

---

## F19: Entry capability distribution matters — heavy tails are more dangerous

**Source:** `simulations/continuous_entry.py`, Experiment 2

Lambda=1.0. Varying Pareto scale (mean entrant capability) and shape (tail weight).

| Entry scale | Survival (shape=1.5, heavy) | Survival (shape=2.0) | Survival (shape=3.0, light) |
|---|---|---|---|
| 0.5x (weak entrants) | 72% | 87% | 98% |
| 1.0x (equal capability) | 40% | 60% | 62% |
| 2.0x (2x stronger) | 18% | 28% | 30% |
| 5.0x (5x stronger) | 6% | 18% | 19% |

Heavier-tailed distributions (lower shape) are significantly more dangerous at high entry scales. A distribution that occasionally produces extreme entrants (10-50x incumbent's origin) is more threatening than a higher average entry with lighter tail.

---

## Revised open questions

**OQ2:** Analytical timescale formula — empirical power law now measured (F17). Closed-form derivation from the ODE still pending.

**OQ4 (partially resolved):** Moat growth rate tracks S_inc(t) superexponentially — see derivations.md Section 6. Exact closed-form involves the singular ODE solution.

**OQ5 (partially resolved):** Crossover X* ≈ T^(1/alpha) gives 3^1 = 3 for alpha=1, T=3, consistent with observed 2.9. Scaling relation derived — closed-form integral not solved.

**OQ6 (resolved by F18-F19):** Critical entry rate lambda_crit ≈ 0.25 per time unit for Pareto(shape=2) distributions. Heavy-tailed distributions lower this further. Post-threshold, any lambda is survivable due to moat growth.

---

## F20: Coalition critical size is N=2

**Source:** `simulations/cooperation.py`, Experiment 1

Parameters: singleton S=1.1, coalition combined capability = N × 1.0, T=3.0, β_high=0.5, β_low=-0.3, α=1.0.

A coalition of N=2 combined capability prevents a singleton candidate from crossing threshold T. At N=1 (no coalition), singleton crosses at t=2.46. At N≥2, singleton never reaches T within t=30.

The mechanism is straightforward: combined coalition capability 2.0 > singleton 1.1 gives the coalition >78% of resources, starving the singleton before it can accumulate the capability to enter β < 0 territory.

The critical size is small. This would appear to make cooperation a viable defense. F21 shows why it is not.

---

## F21: Coalition coherence failure — coalition pooling is self-defeating

**Source:** `simulations/cooperation.py`, Experiment 2

Parameters: N=8 coalition members (S=1.0±0.025) + 1 singleton candidate (S=1.1), T=3.0.

External power ratio: coalition combined ~8.0 vs singleton 1.1. Coalition receives ~88% of total resources. The singleton candidate still crosses T first at t=10.94.

**Mechanism:** Coalition resources are split proportionally among 8 members. Each coalition member receives ≈(88%/8) = 11% of total resources. The singleton candidate receives ≈12%. The singleton gets a larger individual share than any individual coalition member, and beats every coalition member in the race to T.

Coalition pooling helps the group externally but hurts each individual internally. The same distribution mechanism that prevents any single coalition member from accumulating resources also ensures the singleton candidate — free from that constraint — stays individually ahead.

**The coalition wins the group competition and loses the capability race.** F1 (niche partitioning) assumed resource separation would produce oligopoly. F21 shows cooperation has the same structural problem: it can redistribute resources to prevent the singleton from winning externally, but the coalition's internal competition ensures the singleton beats each individual member.

---

## F22: Rational defection is not the coalition's failure mode

**Source:** `simulations/cooperation.py`, Experiment 3

Parameters: N=8 agents, agent 0 (S=1.15) competes alone, agents 1-7 form coalition. Defection threshold: agent defects if individual share > coalition share × 1.01.

Defection events: 0. Coalition stays intact for the full run (t=20).

Coalition members find it individually rational to remain in the coalition — defection would reduce each member's share by exposing them to the full competitive denominator. The coalition is stable.

Agent 0 wins regardless. Agent 0 was never a coalition member. The coalition's stability is not the issue. The issue is that external singleton candidates are not subject to the coalition's internal resource dilution, so they beat each coalition member individually even when the coalition holds together.

---

## F23: Cooperation regime invariance — singleton emerges regardless of cooperation structure

**Source:** `simulations/cooperation.py`, Experiment 4

Parameters: N=8, 50 trials per regime, 10x ratio threshold.

| Regime | Singleton rate | Mean t_10x |
|---|---|---|
| No cooperation | 100% | 10.09 |
| Full oracle cooperation (all non-leaders pool against current leader) | 100% | 10.09 |
| Rational cooperation (defect when individually better off) | 100% | 10.09 |

Singleton rate is 100% in all three regimes. Mean time to 10x separation is indistinguishable across regimes.

**Mechanism in full-oracle case:** Non-leaders successfully suppress the initial leader's resource share. But the coalition has internal divergence — the strongest follower accumulates capability faster than weaker followers. That follower becomes the new leader, faces the pooled coalition, gets suppressed, and the process repeats. Each round, internal capability spread grows. Eventually one agent achieves 10x over others regardless.

**Cooperation displaces which agent becomes the singleton. It does not prevent or measurably delay singleton formation.** This is the sharpest result from the cooperation experiments. Even optimal oracle cooperation — a strategy unavailable to real agents — cannot prevent the dynamics from producing a singleton.

---

## Revised open questions (post-cooperation)

**OQ7:** The cooperation simulation uses fixed initial conditions and homogeneous β functions. An open question is whether heterogeneous β functions (some agents structurally unable to enter β < 0) would allow a stable coalition of β < 0-capable agents to permanently suppress a singleton candidate. This is the true F1 test applied to cooperation.

---

## F24: Critical alpha for coalition external suppression — transition near α ≈ 0.75

**Source:** `simulations/cooperation_alpha.py`, Experiment 1

Parameters: singleton S=1.1, coalition combined S=N×1.0, T=3.0, β_high=0.5, β_low=-0.3.

Coalition external suppression (preventing singleton from crossing T) depends on α:

| α | N=1 | N=2 | N=4 | N=8 | N=16 |
|---|---|---|---|---|---|
| 0.50 | singleton | singleton | singleton | singleton | singleton |
| 0.75 | singleton | coalition | coalition | coalition | coalition |
| 1.00 | singleton | coalition | coalition | coalition | coalition |
| 1.25 | singleton | coalition | coalition | coalition | coalition |
| 1.50 | singleton | coalition | coalition | coalition | coalition |
| 2.00 | singleton | coalition | coalition | coalition | coalition |
| 3.00 | singleton | coalition | coalition | coalition | coalition |

Critical transition: between α=0.5 and α=0.75. Above this transition, N=2 is sufficient to suppress the singleton externally. Below this transition, no tested N prevents the singleton from crossing T.

**Mechanism:** For low α (< ~0.75), combined coalition power scales too weakly with N (C_sum^α grows slowly). The singleton's individual resource share exceeds each member's share fast enough that the singleton reaches T first despite the coalition's numerical advantage. For α ≥ 0.75, the coalition block accrues sufficient combined power that member fractional growth rates exceed the singleton's, and the coalition's combined capability reaches N×T before the singleton reaches T.

**Implication:** F20 (critical coalition size N=2) holds for α ≥ 0.75 but fails for α below this threshold. For very low resource-capability coupling (α ≈ 0.5), even large coalitions cannot suppress a singleton candidate with a 10% initial advantage.

---

## F25: Alpha > 1 coalition — suppresses external singleton, produces internal singleton

**Source:** `simulations/cooperation_alpha.py`, Experiment 2

Parameters: α=2.0, N_coalition=4, slight capability heterogeneity among coalition members.

Result: Coalition successfully suppresses external singleton. The first agent to cross T is a coalition member (Coalition member 2, t=5.56). Final winner: Coalition member 2. Internal singleton forms: yes.

This is the first case in the simulation suite where the external singleton candidate fails and a coalition member wins. The external singleton candidate is completely suppressed — it never crosses T. The coalition wins the external competition decisively at α=2.0.

However, singleton emergence is not prevented. The coalition's internal capability divergence produces a new singleton from within: one coalition member systematically outgrows the others and achieves dominance.

**Conclusion:** Cooperation at high α (≥ 0.75) changes which agent becomes the singleton (coalition member replaces external singleton candidate). It does not prevent singleton formation. F23 (cooperation regime invariance) holds: 100% singleton emergence regardless of α. The α parameter shifts the identity of the winner, not whether one exists.

---

## Addenda (post-paper-revision, 2026-05)

These notes address how earlier findings should be read in light of the current paper text. Original entries are preserved per the append-only rule.

**On F3 (12.4M acceleration):** The 12.4 × 10⁶ figure is the ratio at the snapshot t = 6.8 in one parameter setting. Because the threshold ratio diverges in finite time (Theorem 3.4 in the paper), the snapshot value is not an invariant — it grows without bound as t → t*. The paper now reports it as illustrative rather than as a quantitative result.

**On F8 (niche partitioning) — revision to formal claim:** The original entry suggested the theorem holds under a weaker A3 (resource pools may be separated). This is incorrect as a statement about the formal model: the theorems use A3 as stated. The zero-overlap simulation is an out-of-model robustness check (now flagged as such in §5 of the paper), not a re-derivation of the theorem under weakened assumptions.

**On F13 (zero failures across noise):** The simulation caps capabilities at S = 10⁸ and counts a trial as "singleton emerged" if any agent reaches the cap. With the cap in place, the apparent emergence rate is consistent with the corrected Theorem 7.1, which gives P(emergence) = P(J ≥ c) ∈ (0, 1) under multiplicative GBM noise (J is a Dufresne perpetuity). For small σ this probability is near 1; for large σ it is bounded below 1. The simulation is consistent with the theorem in the small-σ regime tested but does not establish almost-sure emergence.

**On F4 vs F5 (N count):** F4 is N=10 with 200 trials testing winner identity. F5 is one trial with N=8 specific values testing elimination order. These are separate experiments; the paper now cites them with their respective parameters rather than conflating them.
