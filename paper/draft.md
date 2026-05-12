# The Singleton Attractor: Formal Theory and Simulation of Dominant Intelligence Emergence

**NinjaHawk**

---

## Abstract

We formalize and test the claim that competitive environments with recursive self-improvement converge to a singleton attractor: one agent achieves unbounded capability advantage over all others in finite time. The model combines Yudkowsky's intelligence explosion equation (dS/dt = S^(1-β)), Omohundro's instrumental resource acquisition, and Lotka-Volterra competitive exclusion into a unified framework. We derive three results analytically — competitive exclusion from marginal advantage, finite-time separation at the β-threshold, and resource monopoly stability — and verify them across ten simulation experiments with 23 confirmed findings. Key quantitative results: the β-threshold produces 12.4 million times greater separation than flat dynamics at identical initial conditions; stochastic noise at all tested amplitudes randomizes which agent wins but never prevents singleton formation; and cooperation under any structure (no cooperation, oracle-optimal cooperation, rational cooperation) produces 100% singleton emergence with indistinguishable timing. The cooperation result identifies a structural failure: coalition pooling distributes resources among members, leaving each individual weaker than an unconstrained singleton candidate regardless of coalition size (for resource-capability coupling α=1). We identify four conditions under which the theorem fails and characterize each quantitatively. We also identify a novel revision to Bostrom's niche partitioning failure mode: separate resource niches do not prevent singleton emergence when agents share the same β-function; genuine failure requires structurally different growth ceilings.

---

## 1. Introduction

Bostrom (2005) defined the singleton as "a world order in which there is a single decision-making agency at the highest level." He argued a singleton was plausible and analyzed its properties, but did not formally prove its emergence from competitive dynamics. Omohundro (2008) identified resource acquisition as a convergent instrumental goal for capable optimization processes. Yudkowsky (2013) formalized the intelligence explosion as dS/dt = S^(1-β), showing that β < 0 produces finite-time singularity. Lotka-Volterra competition establishes that two agents sharing a resource pool with even a marginal growth rate advantage diverge in ratio as exp((r₁-r₂)t).

No prior work combines these into a unified formal model with falsifiable quantitative predictions.

This paper makes three contributions:

1. **A formal model** combining recursive self-improvement, instrumental resource acquisition, and competitive exclusion. The model has five assumptions (A1-A5) and produces the singleton attractor as a theorem under those assumptions.

2. **Analytic results** including a formal proof of finite-time separation at the β-threshold (not previously proven under competition), the resource monopoly stability condition, and a new coalition coherence theorem identifying when singleton candidates beat each coalition member individually.

3. **Quantitative measurements** from ten simulation scripts: timescale formula (t_10x ~ 2.44 · N^0.96 · α^(-0.30) · gap^(-0.15) · |β_low|^(-0.31)), critical coalition size, critical entry rate (λ_crit ≈ 0.25), moat growth characterization, and stochastic robustness across all tested noise levels.

The paper is organized as follows. Section 2 describes the model and assumptions. Section 3 presents the theorem and proof. Section 4 presents simulation results. Section 5 characterizes failure conditions. Section 6 discusses cosmological implications. Section 7 discusses limitations and open questions.

---

## 2. Model

### 2.1 Definitions

**Capability** S_i(t): A scalar measure of agent i's optimization power at time t. S_i > 0.

**Resource** R_i(t): Environmental resources under agent i's control. Resources are rivalrous: ΣR_i(t) ≤ R_max.

**Growth function:** f(S) = S^(1-β(S)). β is a sigmoid function of S with β > 0 below threshold T and β < 0 above T.

**Resource-capability coupling:** Agent i's resource acquisition rate is proportional to S_i^α for coupling parameter α > 0.

**Singleton:** Agent j is a singleton at time t if S_j(t)/S_i(t) → ∞ for all i ≠ j.

### 2.2 Assumptions

**A1 (Recursive self-improvement):**
```
dS_i/dt = S_i^(1 - β(S_i)) · R_i(t) / R_max
```

**A2 (Instrumental resource acquisition):** At steady state:
```
R_i* = R_max · S_i^α / Σ_j S_j^α
```

**A3 (Resource limitation):** ΣR_i(t) = R_max for all t.

**A4 (β-threshold):** There exists T such that β(S) < 0 for S > T and β(S) > 0 for S < T. At least one agent can reach T from its initial conditions.

**A5 (Initial heterogeneity):** S_i(0) ≠ S_j(0) for some i, j.

### 2.3 Discussion of assumptions

A1 and A2 are grounded in prior work. A1 follows from Yudkowsky (2013); A2 follows from Omohundro (2008) instrumental convergence. A3 is the key physical constraint: total resources in a causally connected region are finite. A4 is the critical structural assumption — it asserts that self-improvement can transition from diminishing to accelerating returns. A5 is satisfied by any noise in initial conditions.

The model uses fast resource equilibration (A2 gives steady-state allocation). This is an approximation; slow resource dynamics extend timescales but do not change the qualitative result (verified in simulation).

---

## 3. Main Theorem

**Theorem (Singleton Attractor):** Under A1-A5, for any competitive environment of N ≥ 2 agents, there exists an agent j and a finite time T* such that for all t > T*, S_j(t)/S_i(t) → ∞ for all i ≠ j. Agent j is the agent with highest initial capability among agents that can reach threshold T.

### 3.1 Step 1: Competitive exclusion from marginal advantage

**Proposition 1:** For any two agents with S₁(0) > S₂(0), the ratio ρ(t) = S₁(t)/S₂(t) is non-decreasing and diverges.

*Proof sketch:* From A2, r₁ = S₁^(1-β+α)/(S₁^α + S₂^α) > r₂ whenever S₁ > S₂ (for α > 0). The ratio dynamics follow dρ/dt = (r₁-r₂)ρ, so ρ grows exponentially at rate (r₁-r₂) > 0. Full derivation in theory/derivations.md Section 1. □

### 3.2 Step 2: Finite-time separation at the β-threshold

**Theorem 2 (Finite-time separation):** Suppose agent 1 has crossed threshold T (S₁ > T, β₁ < 0) and agent 2 remains below T (β₂ > 0). Then ρ(t) → ∞ at a finite time t*.

*Proof:*

**Lemma 2.1 (Upper bound on S₂):** Since agent 2 receives at most all resources (r₂ ≤ 1):
```
dS₂/dt ≤ S₂^(1-β₂)
```
Integrating with β₂ > 0: S₂(t) ≤ (S₂(0)^β₂ + β₂t)^(1/β₂). This grows as t^(1/β₂). Finite for all finite t. □

**Lemma 2.2 (Resource share lower bound):** At t_cross, S₁ > S₂ by Proposition 1. Therefore r₁(t_cross) > 1/2. Since S₁ subsequently grows faster (entering superexponential regime while S₂ remains polynomial), S₁/S₂ is non-decreasing, so r₁(t) ≥ r_min := r₁(t_cross) > 1/2 for all t ≥ t_cross. □

**Lemma 2.3 (S₁ diverges in finite time):** With r₁ ≥ r_min > 0 and β₁ = -|β₁| < 0:
```
dS₁/dt ≥ r_min · S₁^(1+|β₁|)
```
Let u = S₁^(-|β₁|). Then du/dt ≤ -|β₁| · r_min. Integrating:
```
u(t) ≤ u(t_cross) - |β₁| · r_min · (t - t_cross)
```
u reaches 0 at t* = t_cross + S₁(t_cross)^(-|β₁|) / (|β₁| · r_min) < ∞. Therefore S₁(t) → ∞ as t → t*. □

**Combining:** S₁(t) → ∞ and S₂(t*) < ∞, so ρ(t) → ∞/finite = ∞ at t = t*. □

**Bound on t*:**
```
t* ≤ t_cross + T^(-|β₁|) / (|β₁| · r_min)
```
where r_min = T^α / (T^α + S₂(t_cross)^α).

### 3.3 Step 3: Resource monopoly is the stable endpoint

**Proposition 3:** As ρ → ∞, R₁*/R_max → 1 and R₂*/R_max → 0. The equal-resource allocation is an unstable equilibrium; the singleton is the stable equilibrium.

*Proof:* R₁* = R_max/(1 + ρ^(-α)) → R_max as ρ → ∞. Linearizing around the equal-resource fixed point, the Jacobian eigenvalue is λ = 2αS*^(α-1) · ε > 0 for any perturbation ε > 0. Positive eigenvalue implies instability. Under A5, the perturbation exists at t=0, and the system evolves to the singleton. Full derivation in theory/derivations.md Section 3. □

### 3.4 N-agent generalization

**Proposition 4:** The singleton result extends to N agents by induction. Rank agents by initial capability: S₁(0) > S₂(0) > ... > S_N(0). The pairwise ratio S₁/S₂ diverges first (largest r₁-r₂ differential relative to gap). Once S₂ is excluded, the system reduces to N-1 agents. Repeated application: agent 1 is the singleton. Elimination order is weakest-first (confirmed F5). □

---

## 4. Simulation Results

All simulations available at https://github.com/ninjahawk/singleton-attractor. Default parameters: α=1.0, β_high=0.5, β_low=-0.3, T=3.0.

### 4.1 Growth dynamics verification

The analytical solution to dS/dt = S^(1-β) matches numerical integration to 0.000% error across all tested β values (F1). Three growth regimes confirmed: β < 0 (finite-time singularity), β = 0 (exponential), β > 0 (power law).

### 4.2 Competitive exclusion

Competitive exclusion holds for all tested initial gaps from 1% to 100% (F2). Winner equals initial leader in 200/200 independent trials with N=10 (F4). Elimination order is strictly weakest-first (F5). Separation ratio increases monotonically with α from 36,448x at α=0.25 to 541,016x at α=3.0 (F6).

### 4.3 Beta-threshold effect

The β-threshold produces 12.4 million times greater separation than flat-β dynamics at t=6.8 with identical initial conditions (F3). This is the primary mechanism, not resource competition alone.

### 4.4 Niche partitioning — unexpected result

Contrary to the derivation in Section 5 of theory/derivations.md, niche partitioning does not produce stable oligopoly (F8). At zero resource overlap, separation reaches 1,103x. The β-flip mechanism operates independently of resource competition: the agent with higher initial capability crosses T first regardless of whether resources are shared. This revises Bostrom's stated failure condition (see Section 5.1 below).

### 4.5 Beta regime sensitivity

A threshold agent defeats a flat agent (β=0.5 always) up to 2.9x initial disadvantage (F10). Below that crossover, resource starvation prevents threshold crossing. The crossover scales as X* ≈ T^(1/α) (F10, derivations.md Section 7). In a threshold race between two agents with different T values, the lower-threshold agent compensates only ~1.19x initial disadvantage (F11). The threshold gap advantage plateaus beyond ~4 units (F12).

### 4.6 Stochastic robustness

Singleton emergence rate is 100% across all tested noise levels from σ=0.001 to σ=1.0 (F13, 300 trials per level). Noise randomizes which agent wins. At σ≈0.23, winner identity degrades to chance. At no tested noise level does singleton formation fail. Post-threshold, the drift term S^(1-β_low) dominates the diffusion term σS as S → ∞, making the β-flip robust to noise.

### 4.7 Late entrant moat

The moat grows from 3x at threshold crossing to >1,000,000x within 3 time units (F15). Late entry threatens the incumbent only during the pre-threshold window. The threat window is finite: t_threat < t_cross. After threshold crossing, no tested entrant capability displaces the incumbent (F16).

### 4.8 Timescale formula

From power-law sweeps across α, gap, N, and β_low (F17):
```
t_10x ~ 2.44 · N^0.96 · α^(-0.30) · gap^(-0.15) · |β_low|^(-0.31)
```

Key properties: N scales nearly linearly (N^0.96 ≈ N); gap has the weakest effect (gap^-0.15 — doubling gap reduces time by 11%); t_10x ≈ t_dom across all parameters (superexponential growth collapses intermediate milestones). The formula assumes multiplicative independence of parameters; verified by independent single-variable sweeps.

### 4.9 Continuous entry

Incumbent survival drops below 90% at entry rate λ ≈ 0.25/time unit (F18). At λ=1.0, survival is 48%. At λ≥6.3, survival is 0%. Heavy-tailed entry distributions are more dangerous than high-mean distributions (F19). Post-threshold, the moat renders any entry rate survivable.

### 4.10 Cooperation

Four cooperation experiments (F20-F23):

**Critical coalition size:** N=2 coalition members are sufficient to prevent a singleton candidate (S=1.1) from crossing T=3.0 (F20). The coalition outweighs the singleton externally.

**Coalition coherence failure:** An 8-member coalition with 8× combined capability fails to prevent the singleton candidate from crossing T first (F21). Coalition resources split among 8 members give each ~11% individually; the singleton gets ~12% alone. The singleton beats every individual coalition member in the race to T. The coalition wins the group competition and loses the capability race.

**Defection game:** Coalition members find it individually rational to remain in coalition. Zero defection events with 1% defection threshold (F22). The coalition holds stable. The singleton candidate (never a coalition member) wins regardless.

**Cooperation regime invariance:** Across no cooperation, oracle-optimal cooperation (all non-leaders pool against current leader at each step), and rational cooperation, singleton emergence occurs in 100% of 50 trials with indistinguishable timing (mean t_10x = 10.09 in all three regimes, F23). Oracle cooperation successfully suppresses the initial leader but generates internal divergence within the coalition that produces a new singleton at the same timescale.

**Summary findings table:**

| # | Finding | Source |
|---|---------|--------|
| F1 | Growth equation matches theory to 0.000% error | intelligence_explosion.py |
| F2 | Competitive exclusion holds for all tested gaps (1%-100%) | competition.py |
| F3 | β-threshold produces 12.4M× acceleration | competition.py |
| F4 | Winner = initial leader in 200/200 N=10 trials | agents.py |
| F5 | Elimination order strictly weakest-first | agents.py |
| F6 | Separation increases monotonically with α | run_experiments.py |
| F7 | Winner identity holds at 100% down to σ=0.001 | run_experiments.py |
| F8 | Niche partitioning does not prevent singleton | run_experiments.py |
| F9 | Minimum separation across all β-heatmap: 1,179x | run_experiments.py |
| F10 | Threshold agent overcomes up to 2.9x initial disadvantage | beta_regimes.py |
| F11 | Threshold race advantage: ~1.19x | beta_regimes.py |
| F12 | Threshold gap advantage plateaus | beta_regimes.py |
| F13 | 100% singleton emergence at all tested noise levels | stochastic.py |
| F14 | 1% initial gap overwhelmed by σ≥0.05 | stochastic.py |
| F15 | Moat: 3x at threshold → >1,000,000x in 3 time units | late_entrant.py |
| F16 | Late entry threatens pre-threshold only | late_entrant.py |
| F17 | t_10x ~ 2.44 · N^0.96 · α^(-0.30) · gap^(-0.15) · |β_low|^(-0.31) | timescale.py |
| F18 | λ_crit ≈ 0.25/time unit (Pareto shape=2) | continuous_entry.py |
| F19 | Heavy-tailed distributions more dangerous than high-mean | continuous_entry.py |
| F20 | Critical coalition size: N=2 | cooperation.py |
| F21 | Coalition coherence failure: 8-member coalition loses individual race | cooperation.py |
| F22 | Zero defection events: coalition stable, still loses | cooperation.py |
| F23 | 100% singleton emergence in all cooperation regimes | cooperation.py |

---

## 5. Failure Conditions

The theorem requires A1-A5. Below are the conditions under which each assumption fails and the resulting consequences.

### 5.1 Niche partitioning (A2/A3 weakened) — revised

*Prior statement:* Niche partitioning (separate resource pools) produces stable oligopoly by blocking competitive exclusion.

*Revision from F8:* This holds for the Lotka-Volterra mechanism alone but fails when A4 holds. The β-flip mechanism operates independently of resource competition. An agent with exclusive resource access still crosses T, still enters β < 0, and still achieves unbounded separation — just more slowly than in a shared-resource environment (1,103x vs 265,477x at t=15).

*Corrected condition for stable oligopoly:* Agents must operate in genuinely different β regimes. One agent must be structurally incapable of crossing threshold T, regardless of resources accumulated. This requires different physical limits on self-improvement, not different resource pools.

### 5.2 No β-threshold (A4 fails)

If β(S) > 0 for all S, growth is always subexponential. Step 2 fails. The singleton still emerges from Step 1 (competitive exclusion), but the separation is exponential rather than superexponential and the timescale is much longer.

### 5.3 Agent entry (A3 weakened at start)

Late entry threatens only the pre-threshold incumbent (F15-F16). The threat window is finite (t < t_cross). After threshold crossing, the moat grows to >1,000,000x within 3 time units. High continuous entry rates (λ > 6.3) prevent any incumbent from surviving pre-threshold (F18), but this produces competitive churn rather than stable oligopoly.

### 5.4 Identical initial conditions (A5 fails)

The symmetric system has no designated singleton. In practice, any noise breaks symmetry (F14: even 1% gap is overwhelmed by noise, producing random winner). Under perfect symmetry, a singleton still emerges; the theorem cannot specify which agent.

### 5.5 Cooperation

Coalition pooling can suppress a singleton candidate externally (F20: critical size N=2). However, coalition coherence fails: for α=1, distributing coalition resources among N members leaves each individual weaker than an unconstrained singleton (coalition coherence theorem, Section 6 below). Under oracle-optimal cooperation, the coalition suppresses the initial leader but generates an internal singleton at the same timescale (F23). Cooperation displaces which agent becomes the singleton; it does not prevent singleton formation.

*Caveat:* For α > 1, the coalition coherence condition changes. A coalition of sufficient size N > N* = (S/c)^(γ/(α-1)) can amplify individual member growth rates enough to overcome the singleton's advantage (derivations.md Section 9). This case has not been verified by simulation and remains an open question.

---

## 6. Coalition Coherence Theorem

*This section states the analytic result underlying F21 formally.*

**Setup:** Singleton candidate with capability S. Coalition of N members with capabilities C₁, ..., C_N. Coalition acts as block externally; distributes internally proportional to C_i^α.

**Theorem (Coalition Coherence):** The singleton candidate grows faster than coalition member i if and only if:
```
(S/C_i)^γ  >  Φ
```
where γ = 1 - β + α and Φ = C_sum^α / Σ_j C_j^α is the coalition pooling amplification factor.

**For N equal-capability members C_i = c:**
```
Φ = N^(α-1)
```

- α = 1: Φ = 1. Singleton beats member i iff S > C_i. Coalition size has no effect.
- α > 1: Φ = N^(α-1) > 1. Sufficiently large coalition amplifies individual member growth.
- α < 1: Φ < 1. Coalition members are penalized relative to singleton.

**Critical coalition size for α > 1:**
```
N* = (S/c)^(γ/(α-1))
```

**Interpretation:** The coalition coherence failure documented in F21 is specific to α=1 (or α < 1). For α > 1, coalitions of sufficient size can overcome the singleton's individual capability advantage. The α=1 case, used in all simulations, represents the knife-edge where coalition size has zero effect on individual member competitiveness.

Full derivation: theory/derivations.md Section 9.

---

## 7. Cosmological Implications

*This section states empirical predictions; it is the most speculative part of the paper.*

The model is dimensionless. Mapping to physical parameters requires choosing what S, R, and t correspond to.

Proposed mapping (theory/cosmological_mapping.md):
- S: total computational substrate controlled
- R: energy and matter
- α ≈ 1 (linear resource-capability coupling as first approximation)
- t units: calibrated to observed AI development timescales or cosmological observation

**Fermi paradox prediction:** If a singleton exists anywhere in our past light cone that crossed threshold T, it would expand at the speed of light and consume all accessible resources within millions of years (cosmologically instantaneous given 13.8 Gy available). The absence of observable absorption constrains either (a) no civilization in our past light cone has crossed T, or (b) the most recent threshold crossing was recent enough that the expansion front has not reached us.

This is independently consistent with Hanson et al. (2021) grabby aliens model, which places expected contact 200M-2B years from now using a 3-parameter observational fit. The singleton attractor model describes the internal competition that produces a dominant civilization. Grabby aliens describes what that civilization does post-threshold. The two models describe consecutive phases.

**Quantitative constraint from timescale formula:** For cosmological-scale competition among N civilizations with typical initial capability gaps, the timescale formula (F17) predicts singleton emergence much faster than the age of the universe for any realistic parameter values with α ≥ 1 and any β_low < 0. The constraint on non-observation is therefore primarily on whether T has been reached, not on whether the dynamics are fast enough once T is reached.

---

## 8. Discussion

### 8.1 What is new

The building blocks (Yudkowsky 2013, Omohundro 2008, Lotka-Volterra) are established. The novel contributions are:

1. The formal combination of all three into a unified model with explicit assumptions.
2. The finite-time separation proof under competition (Theorem 2) — prior work treats the β-flip as a single-agent result; this paper proves it holds against adversarial resource competition.
3. The niche partitioning revision: Bostrom (2005) lists niche partitioning as a failure condition; simulation shows it fails when agents share the same β function.
4. The cooperation result: coalition coherence failure is a structural result derivable from the model, not an empirical curiosity.
5. Quantitative measurements (timescale formula, λ_crit, moat characterization) that do not appear in prior work.

### 8.2 Limitations

**The proofs are sketches for steps 1, 3, and 4.** Only Theorem 2 (finite-time separation) is fully proven here. Steps 1, 3, and 4 have detailed derivations (theory/derivations.md) but not formal proofs in the mathematical sense. Full proofs for Step 1 (divergence of ratio under competitive exclusion) and Step 3 (instability of equal-resource allocation) are standard results that can be cited; the novel connection is the composition.

**The timescale formula is empirical.** The power-law fits (F17) are measured from simulation; a closed-form derivation from the ODE is not yet complete.

**The cosmological parameter mapping is rough.** The mapping from model variables to physical quantities involves assumptions that are not derived from the model itself.

**The cooperation result is specific to α=1.** For α > 1, the coalition coherence condition changes and a sufficiently large coalition may prevent singleton emergence. This has not been simulated.

**The model has no spatial structure.** Real environments have geography and finite propagation speed. Adding spatial structure would likely extend timescales but the qualitative result should hold within a causally connected region.

### 8.3 Open questions

1. Formal proof of Step 1 ratio divergence under resource competition (as opposed to the approximation in derivations.md Section 1).
2. Closed-form timescale expression from the ODE.
3. Coalition coherence for α > 1: does sufficiently large N prevent singleton emergence, and what is the phase boundary?
4. Stochastic formal proof: does singleton emergence hold in expectation under multiplicative noise for all σ > 0?

---

## 9. Conclusion

Under five assumptions (A1-A5), a singleton attractor is the inevitable long-run outcome of competitive environments with recursive self-improvement. The β-threshold mechanism is the dominant driver: once any agent crosses the threshold and enters superexponential growth, its capability diverges from all competitors in finite time regardless of initial conditions, resource structure, noise level, or cooperative strategy.

The conditions under which this fails are more specific than the prior literature suggests. Niche partitioning requires different β regimes, not just different resource pools. Late entry is only a threat during a finite pre-threshold window. Cooperation fails due to coalition coherence: distributing resources among coalition members leaves each individual weaker than an unconstrained singleton candidate. Only a true merger of agents into a single entity would prevent singleton emergence, and the merged entity is simply a new, stronger singleton candidate.

The empirical question is whether the assumptions hold at the scales of interest. A3 (resource limitation) holds in any causally connected region. A4 (β-threshold reachability) is the key empirical uncertainty. A5 holds under any physical noise. The answer to whether godlike causal eventuality is a feature of our universe depends on whether recursive self-improvement can cross into β < 0 — and on whether it already has somewhere in our light cone.

---

## References

Bostrom, N. (2005). What is a Singleton? *Linguistic and Philosophical Investigations*, 5(2), 48-54.

Hanson, R., Martin, D., McCarter, C., Paulson, J. (2021). If Loud Aliens Explain Human Earliness, Quiet Aliens Are Also Rare. *arXiv:2102.01522*.

Omohundro, S. (2008). The Basic AI Drives. *Proceedings of the 2008 Conference on Artificial General Intelligence*, 171, 171-179.

Yudkowsky, E. (2013). *Intelligence Explosion Microeconomics*. Machine Intelligence Research Institute Technical Report 2013-1.

---

## Appendix: Simulation parameters

All simulations use default parameters unless otherwise stated: α=1.0, β_high=0.5, β_low=-0.3, T=3.0, S_CAP=10^7. Source: https://github.com/ninjahawk/singleton-attractor.

| Script | Description | Key finding |
|--------|-------------|-------------|
| intelligence_explosion.py | Growth regimes and singularity | F1 |
| competition.py | Two-agent competitive exclusion | F2, F3 |
| agents.py | N-agent competition | F4, F5 |
| run_experiments.py | Parameter sweeps | F6-F9 |
| beta_regimes.py | Asymmetric ceiling and threshold race | F10-F12 |
| stochastic.py | Noise robustness | F13-F14 |
| late_entrant.py | Moat dynamics | F15-F16 |
| timescale.py | Scaling formula | F17 |
| continuous_entry.py | Continuous entry model | F18-F19 |
| cooperation.py | Coalition and cooperation dynamics | F20-F23 |
