# Derivations

Step-by-step math for each step in the proof sketch. References `formal_claim.md` for definitions and assumptions.

---

## Section 1: Competitive exclusion from marginal capability advantage

**Setup:** Two agents, capability S₁(t) and S₂(t), with S₁(0) > S₂(0). Resources R₁ + R₂ = R_max (conserved). From A1 and A2:

```
dS_i/dt = S_i^(1 - β) · (R_i / R_max)
dR_i/dt = S_i^α · R_max / (S₁^α + S₂^α) - R_i
```

The second equation: agent i's resource share at steady state equals its proportional acquisition strength.

**Steady-state resource allocation:**

At resource equilibrium (dR_i/dt = 0):

```
R_i* = R_max · S_i^α / (S₁^α + S₂^α)
```

Resource share is proportional to S_i^α. Higher capability → larger resource share. This is the key coupling.

**Effective growth rates:**

Substituting R_i* into the capability equation:

```
dS_i/dt = S_i^(1 - β) · S_i^α / (S₁^α + S₂^α)
         = S_i^(1 - β + α) / (S₁^α + S₂^α)
```

Define effective growth rate r_i = S_i^(1 - β + α) / (S₁^α + S₂^α).

When S₁ > S₂ and α > 0: r₁ > r₂. The leading agent grows faster.

**Ratio dynamics:**

Let ρ = S₁/S₂. Then:

```
dρ/dt = (1/S₂) · dS₁/dt - (S₁/S₂²) · dS₂/dt
      = (r₁ - r₂) · ρ
```

So ρ(t) = ρ(0) · e^(∫(r₁ - r₂)dt).

Since r₁ - r₂ > 0 whenever S₁ > S₂ (from α > 0), the integral diverges and ρ → ∞.

**Result:** Any initial advantage S₁(0) > S₂(0), however small, produces ρ(t) → ∞ as t → ∞. This is the Lotka-Volterra competitive exclusion result applied to capability dynamics.

**Note on the approximation:** The derivation above assumes resource equilibration is fast relative to capability growth. If resource dynamics are slow, the result still holds but the timescale is longer. The simulation will test whether slow resource equilibration materially delays singleton emergence.

---

## Section 2: Superexponential separation at the β-threshold

**Setup:** Agent 1 crosses threshold T (A4), entering β₁ < 0 regime. Agent 2 remains at β₂ > 0.

**Agent 1 in β < 0 regime:**

```
dS₁/dt = S₁^(1 - β₁) · (R₁/R_max)
```

With β₁ < 0, the exponent 1 - β₁ > 1. This is superlinear: growth rate grows faster than capability itself.

Solving the ODE for constant R₁ (upper bound on growth speed):

```
dS₁/dt = S₁^(1 - β₁)
S₁^(β₁ - 1) · dS₁ = dt
S₁^β₁ / β₁ = t + C
S₁(t) = (β₁ · (t + C))^(1/β₁)
```

With β₁ < 0, as t → t* = -C = 1/(β₁ · S₁(0)^β₁), S₁ → ∞. Finite-time singularity.

**Agent 2 in β > 0 regime:**

```
dS₂/dt = S₂^(1 - β₂)
```

With β₂ > 0 and β₂ < 1, this is sublinear. S₂ grows as a power law in t: S₂(t) ~ t^(1/β₂). This is bounded for all finite t.

**Ratio at the singularity:**

As t → t*, S₁(t) → ∞ while S₂(t) remains finite. ρ = S₁/S₂ → ∞ in finite time.

**Result:** The β-flip does not just accelerate separation — it makes the separation happen in finite time. Before the threshold, separation requires t → ∞. After the threshold, separation happens at t = t*.

**The threshold crossing:**

Agent 1 crosses T when S₁(t) = T. From Section 1, this happens at:

```
t_cross ≈ T^β₂ / β₂  (for β₂ > 0 regime)
```

For large T, this can be a long time. But once crossed, the singularity follows at t* = t_cross + 1/(|β₁| · T^|β₁|). The time from threshold crossing to effective dominance is finite and determined by β₁ and T.

---

## Section 3: Resource monopoly as the stable endpoint

**Setup:** As ρ = S₁/S₂ → ∞, what happens to resource allocation?

From Section 1:

```
R₁* = R_max · S₁^α / (S₁^α + S₂^α)
    = R_max / (1 + (S₂/S₁)^α)
    = R_max / (1 + ρ^(-α))
```

As ρ → ∞: ρ^(-α) → 0, so R₁* → R_max. Agent 1 absorbs all resources.

Correspondingly: R₂* = R_max · ρ^(-α) / (1 + ρ^(-α)) → 0.

**Agent 2's growth halts:**

```
dS₂/dt = S₂^(1 - β₂) · (R₂/R_max) → 0
```

Agent 2's capability growth approaches zero as its resources approach zero.

**The stable endpoint:**

The system has two equilibria:
1. Agent 1 controls all resources, agent 2 has none. This is stable: any perturbation is damped by the feedback (more resources → more capability → more resources).
2. Equal resource split. This is unstable: any perturbation (S₁ ≠ S₂) is amplified.

The singleton is the stable equilibrium. Equal distribution is unstable. Under A5 (initial heterogeneity), the system will always evolve to the singleton equilibrium.

**Formal stability check:**

Linearize around the equal-resource fixed point R₁ = R₂ = R_max/2, S₁ = S₂ = S*:

```
δR₁ = -δR₂ (conservation)
δS₁ = ε, δS₂ = -ε (small perturbation)
```

The Jacobian has eigenvalue λ = α(r₁ - r₂)|_{S₁=S₂} = 2αS*^(α-1) · ε > 0.

Positive eigenvalue → unstable equilibrium. Perturbations grow. The system leaves the equal-distribution fixed point and evolves toward the singleton.

---

## Section 4: N-agent generalization

The two-agent result extends to N agents by induction.

**Step 1:** Among N agents, rank by initial capability: S₁(0) > S₂(0) > ... > S_N(0).

**Step 2:** From Section 1, agent 1 grows faster than agent 2, which grows faster than agent 3, etc. The pairwise ratios S_i/S_{i+1} all increase.

**Step 3:** The fastest-growing divergence is ρ₁N = S₁/S_N (leader vs. last). But ρ₁₂ = S₁/S₂ also diverges, and does so first (smallest initial ratio, but largest r₁ - r₂ differential).

**Step 4:** Once ρ₁₂ → ∞, agent 2 has no effective resource share. The system reduces to N-1 agents. By induction, the N-1 agent system produces a singleton among agents {1, 3, 4, ..., N}, which is still agent 1.

**Result:** For any N, the agent with highest initial capability becomes the singleton. The order of elimination is from the bottom: weakest agents are excluded first.

**Caveat:** This inductive argument assumes agents are eliminated sequentially. In practice, all exclusion dynamics run simultaneously and faster agents may accelerate the exclusion of slower ones. The simulation will measure whether the sequential approximation holds.

---

## Section 5: Conditions for stable oligopoly (Failure mode F1)

If the resource pool is partitioned into non-overlapping niches R = R_a ∪ R_b, with agents 1 and 2 specializing in different niches:

```
dR_1/dt = S₁^α · R_a - R₁   (agent 1 only competes in niche a)
dR_2/dt = S₂^α · R_b - R₂   (agent 2 only competes in niche b)
```

The two agents no longer compete directly. Their capability growth equations decouple:

```
dS₁/dt = S₁^(1 - β) · R₁/R_a
dS₂/dt = S₂^(1 - β) · R₂/R_b
```

These are independent. Both agents can enter the β < 0 regime. Both can reach unbounded capability. There is no competitive exclusion.

**Oligopoly stability condition:** Oligopoly is stable if and only if agents occupy non-overlapping resource niches. The stability is not about capability level — it is purely about resource competition structure.

**Implication:** The singleton attractor theorem requires that there exists some shared resource that all agents compete for. If such a resource exists and is limiting, the theorem applies. If agents can fully partition the resource space, the theorem does not apply.

In practice: what is the resource that advanced intelligences all compete for? Candidates are energy, matter, space, and computation. All of these are finite in any causally connected region. The question of whether agents can specialize without competing for these base-level resources is an empirical one, not a mathematical one.

---

## Section 6: Moat growth rate (OQ4)

**Setup:** Incumbent has crossed threshold T at time t_cross with capability S_cross = T. Post-threshold dynamics with no competitor:

```
dS_inc/dt = S_inc^(1 - β_low)   with β_low < 0
```

From Section 2: S_inc(t) = (β_low * (t - t_cross) + T^β_low)^(1/β_low)

A late entrant entering at time t0 > t_cross with capability S_new can defeat the incumbent only if it can reach S_inc's capability level before S_inc dominates the resource pool.

**Moat at time t0:** The incumbent's capability at t0 is:

```
S_inc(t0) = (β_low * (t0 - t_cross) + T^β_low)^(1/β_low)
```

With β_low < 0, as (t0 - t_cross) increases, S_inc grows without bound toward the finite-time singularity.

**Condition for entrant to win:** The entrant needs enough resources to eventually outpace the incumbent. From the resource allocation formula (fast equilibration), the entrant's resource share is:

```
R_new / R_max = S_new^α / (S_inc^α + S_new^α) = 1 / (1 + (S_inc/S_new)^α)
```

If S_inc >> S_new, the entrant gets resource share ≈ (S_new/S_inc)^α ≈ 0.

**Critical threshold for entrant viability:** The entrant can sustain growth only if its resource share is above some minimum threshold ε:

```
(S_new/S_inc)^α > ε
S_new > S_inc * ε^(1/α)
```

For the entrant to have any chance, it needs S_new ≥ S_inc(t0) * ε^(1/α). But S_inc(t0) is growing superexponentially. The minimum viable S_new therefore grows at the same rate as S_inc — superexponentially.

**Moat growth rate:** The moat (max S_new that still loses) scales as:

```
M(t0) ~ S_inc(t0)^κ   for some κ > 0
```

From simulation F15: M(t0) grows from 3 to >1,000,000 in 3 time units. Over that same interval, S_inc grows from T=3 to >1e8. The ratio M/S_inc is roughly 0.8 before threshold and grows post-threshold. This is consistent with the derivation: M tracks S_inc, which is growing toward its singularity.

**Conclusion:** The moat becomes effectively infinite at the same time S_inc reaches its singularity t*. The time window for F3 to threaten the singleton is t < t* — which is finite and determined by the parameters.

---

## Section 7: Asymmetric ceiling crossover (OQ5)

**Setup:** Agent 1 has threshold β (β_low=-0.3 above T=3). Agent 2 has flat β=0.5 always. S1(0)=1, S2(0)=X. Find the critical X* where Agent 1 transitions from winning to losing.

**Agent 1's condition to reach threshold:** Agent 1 must accumulate enough capability to cross T=3. Its growth rate is determined by its resource share, which depends on X.

At resource equilibrium with S1 and S2:
```
Resource share for Agent 1 = S1^α / (S1^α + S2^α)
dS1/dt = S1^(1-β_high) * S1^α / (S1^α + S2^α)
```

When S1 << S2 (Agent 2 far ahead), resource share for Agent 1 ≈ (S1/S2)^α.

**Simplified dynamics when S2 >> S1:** Agent 2 grows approximately as:
```
dS2/dt ≈ S2^(1 - β_high)   (gets ≈ all resources)
```

Agent 1 grows approximately as:
```
dS1/dt ≈ S1^(1 - β_high + α) * S2^(-α)
```

For Agent 1 to reach T before Agent 2 monopolizes, we need S1 to cross T before Agent 2 gets so large that Agent 1's resource share → 0.

**The condition:** Agent 1 survives if ∫₀^∞ dS1/dt dt ≥ T - 1. With the approximate dynamics:

```
dS1/dt = S1^(1 + α - β_high) / S2(t)^α
```

where S2(t) grows as a power law (β_high=0.5, so S2 ~ t^2). As t → ∞, S2^α → ∞ and dS1/dt → 0. Agent 1's total accumulated growth is bounded.

**Crossover condition:** The crossover X* occurs when Agent 1's total growth (summed over all time) just barely reaches T. For α=1, β_high=0.5:

This is an integral equation in X. The simulation found X*≈2.9. An exact analytical form requires computing ∫₀^∞ S1^(1.5) / S2(t) dt = T - 1 under coupled dynamics, which does not have a closed form but can be approximated.

**Asymptotic bound:** The crossover X* scales approximately as T^(1/α) (threshold capability per unit of coupling), which gives T^1 = 3 for α=1, T=3 — consistent with the observed 2.9. This is an approximation, not a proof, but it provides a useful scaling relation: X* ≈ T^(1/α).

---

## Open derivations

1. **Exact timescale:** Analytical expression for time to singleton as function of N, σ, α, β. Simulations provide empirical measurements; closed-form expressions not yet derived.

2. **Stochastic perturbations:** Formal proof that singleton emergence holds in expectation under multiplicative noise. Simulation (F13) confirms 100% singleton rate across all tested noise levels. Analytical proof: the positive feedback in β < 0 regime dominates noise when S > T, because the drift term S^(1-β_low) grows faster than the noise term σS as S → ∞.

3. **Continuous entry (OQ6):** At what entry rate λ and capability distribution P(S) does the incumbent fail to maintain dominance? Prediction: if max(P(S)) < M(t) for all t after threshold crossing, incumbent is safe. Since M(t) → ∞, incumbent is safe for any fixed entry capability distribution.
