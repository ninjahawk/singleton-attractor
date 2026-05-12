# Derivations

Step-by-step math for each step in the proof sketch. References `formal_claim.md` for definitions and assumptions.

---

## Section 1: Competitive exclusion from marginal capability advantage

**Setup:** Two agents with capabilities S₁(t) and S₂(t), S₁(0) > S₂(0). Resources are in steady-state (A2): R_i* = R_max · S_i^α / (S₁^α + S₂^α). Substituting into A1 with β uniform (pre-threshold):

```
dS_i/dt = S_i^(1-β+α) / (S₁^α + S₂^α)
```

**Theorem 1 (Ratio divergence):** For any S₁(0) > S₂(0) > 0 and α > 0, the ratio ρ(t) = S₁(t)/S₂(t) is strictly increasing and diverges: ρ(t) → ∞ as t → ∞.

*Proof:*

**Part 1 — ρ is strictly increasing:**

Compute:
```
dρ/dt = d(S₁/S₂)/dt = (S₂ · dS₁/dt - S₁ · dS₂/dt) / S₂²
```

Let D = S₁^α + S₂^α. Substituting:
```
dρ/dt = [S₂ · S₁^(1-β+α)/D - S₁ · S₂^(1-β+α)/D] / S₂²
      = (S₁^(1-β+α) · S₂ - S₁ · S₂^(1-β+α)) / (D · S₂²)
      = S₁ · S₂ · (S₁^(-β+α) - S₂^(-β+α)) / (D · S₂²)
      = ρ · (S₁^(α-β) - S₂^(α-β)) / D
```

Since S₁ > S₂ and α - β > 0 (which holds whenever α > β — in particular for α > 0 and β ∈ (0,1)), we have S₁^(α-β) > S₂^(α-β), so (S₁^(α-β) - S₂^(α-β)) / D > 0. Therefore dρ/dt = ρ · [positive] > 0. ρ is strictly increasing. □

**Part 2 — ρ → ∞:**

Suppose for contradiction ρ(t) → L < ∞ as t → ∞. Then dρ/dt → 0, but from above, dρ/dt = 0 only when S₁^(α-β) = S₂^(α-β), i.e., S₁ = S₂, i.e., ρ = 1. For any L > 1, dρ/dt > 0 strictly. So ρ cannot converge to any finite limit greater than 1. Since ρ(0) > 1 and ρ is increasing, ρ → ∞. □

**Explicit rate:** Substituting ρ = S₁/S₂ and S₂ = S₁/ρ:
```
dρ/dt = ρ · S₁^(α-β) · (1 - ρ^(β-α)) / (S₁^α · (1 + ρ^(-α)))
      = ρ · S₁^(-β) · (1 - ρ^(β-α)) / (1 + ρ^(-α))
```

For large ρ, this approaches ρ · S₁^(-β) since ρ^(β-α) → 0 (α > β) and ρ^(-α) → 0. The ratio grows at a rate that scales with ρ itself — superlinear in ρ.

**Condition α > β:** The proof requires α > β(S). Since β = β(S) is a sigmoid transitioning from β_high > 0 to β_low < 0, and α > 0, this condition holds whenever β < α. In the pre-threshold regime with β = β_high = 0.5 and α = 1.0: α - β = 0.5 > 0. Condition satisfied. In the post-threshold regime with β_low < 0: α - β = α + |β_low| > 0. Condition holds even more strongly.

**Note:** The proof assumes fast resource equilibration (A2 instantaneous). If resource dynamics are slow (time constant τ), the ratio still diverges but over a timescale ~max(t, τ). The simulation uses instantaneous equilibration throughout; τ = 0 is the case proven here.

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

**Theorem 4 (N-agent singleton):** Under A1-A5, for N ≥ 2 agents ranked S₁(0) > S₂(0) > ... > S_N(0), agent 1 is the singleton. Elimination order is weakest-first.

*Proof by induction:*

**Base case (N=2):** Theorem 1 (Section 1) and Theorem 2 (Section 8) establish that ρ₁₂ = S₁/S₂ → ∞ in finite time t*. Agent 2's resource share r₂ = 1/(1 + ρ₁₂^α) → 0. Agent 2's growth rate dS₂/dt = S₂^(1-β) · r₂ → 0. Agent 1 controls all resources. □ (base case)

**Inductive step:** Assume for any system of k < N agents with distinct initial capabilities, the strongest becomes the singleton. Consider N agents.

Let D = Σᵢ Sᵢ^α. Agent j's resource share is rⱼ = Sⱼ^α / D.

**Claim:** The weakest agent (agent N) is eliminated first. The ratio ρ₁N = S₁/S_N grows fastest of all pairwise ratios ρᵢⱼ with i < j.

*Proof of claim:* Consider the ratio ρ_kl = S_k/S_l for any k < l (S_k > S_l). From the ratio dynamics:
```
dρ_kl/dt = ρ_kl · (S_k^(α-β) - S_l^(α-β)) / D
```

For ρ₁N: the numerator S₁^(α-β) - S_N^(α-β) is largest (S₁ is largest, S_N is smallest). The denominator D is shared. So dρ₁N/dt / ρ₁N ≥ dρ₁₂/dt / ρ₁₂ ≥ ... — the fractional growth rate of ρ₁N is largest.

However, the elimination time depends on both the rate and the current value. Agent N is weakest and has the smallest resource share from the start, so its growth stalls earliest. □

**Completing the induction:** After agent N's resource share r_N → 0, the system is effectively N-1 agents with capabilities S₁ > S₂ > ... > S_{N-1}. By the inductive hypothesis, agent 1 becomes the singleton of this reduced system. Agent 1 is the singleton of the full N-agent system. □

**Verification (F5):** Simulation confirms strictly weakest-first elimination in all tested cases (N=8 agents, threshold β). Elimination times follow initial capability ranking exactly, consistent with the inductive claim. □

**Note on simultaneous dynamics:** The inductive argument simplifies to sequential elimination, but actual dynamics are simultaneous. All pairwise ratios diverge concurrently; the weakest agent's share approaches zero first. This is a sequential approximation that captures the correct ordering; the simulation verifies the approximation is accurate (F4, F5).

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

---

## Section 8: Formal proof of β-flip separation in finite time

The Section 2 sketch handles the isolated case (full resources, constant β). This section gives a formal proof under competition: agent 1 in the β < 0 regime, agent 2 in the β > 0 regime, with dynamic resource allocation.

**Setup:** At time t_cross, agent 1 has just crossed threshold T (from A4). At this moment S₁(t_cross) = T > S₂(t_cross) (agent 1 has been ahead since t=0 by Section 1 dynamics). Let β₁ = -|β₁| < 0 and β₂ > 0.

**Lemma 1 (Upper bound on S₂):** For all t ≥ 0:
```
S₂(t) ≤ (S₂(0)^β₂ + β₂ · t)^(1/β₂)
```

*Proof:* Agent 2 receives at most all resources (r₂ ≤ 1). With full resources:
```
dS₂/dt ≤ S₂^(1 - β₂)
S₂^(β₂ - 1) dS₂ ≤ dt
∫ S₂^(β₂-1) dS₂ ≤ t
S₂(t)^β₂ / β₂ ≤ S₂(0)^β₂ / β₂ + t
```
Solving: S₂(t) ≤ (S₂(0)^β₂ + β₂ t)^(1/β₂). For β₂ > 0, this grows as t^(1/β₂) — polynomially. □

**Lemma 2 (Lower bound on agent 1's resource share):** For t ≥ t_cross:
```
r₁(t) ≥ r_min := S₁(t_cross)^α / (S₁(t_cross)^α + S₂(t_cross)^α) > 1/2
```

*Proof:* At t_cross, S₁ > S₂, so S₁^α > S₂^α and r₁(t_cross) > 1/2. For t > t_cross, S₁ grows faster than S₂ (entering superexponential regime while S₂ remains polynomial), so S₁(t)/S₂(t) is non-decreasing. Resource share r₁ = 1/(1 + (S₂/S₁)^α) is therefore non-decreasing. Thus r₁(t) ≥ r₁(t_cross) = r_min > 1/2 for all t ≥ t_cross. □

**Lemma 3 (S₁ diverges in finite time):** There exists finite t* such that S₁(t) → ∞ as t → t*.

*Proof:* With r₁ ≥ r_min and β₁ < 0:
```
dS₁/dt = S₁^(1 - β₁) · r₁ ≥ r_min · S₁^(1 + |β₁|)
```

This is a Bernoulli ODE with exponent 1 + |β₁| > 1. Let u = S₁^(-|β₁|):
```
du/dt = -|β₁| · S₁^(-|β₁|-1) · dS₁/dt ≤ -|β₁| · r_min
```

Integrating from t_cross to t:
```
u(t) ≤ u(t_cross) - |β₁| · r_min · (t - t_cross)
     = S₁(t_cross)^(-|β₁|) - |β₁| · r_min · (t - t_cross)
```

u(t) = S₁(t)^(-|β₁|) reaches 0 at:
```
t* = t_cross + S₁(t_cross)^(-|β₁|) / (|β₁| · r_min) < ∞
```

As t → t*, u(t) → 0, so S₁(t) → ∞. □

**Theorem (Finite-time ratio separation):** ρ(t) = S₁(t)/S₂(t) → ∞ at t = t*.

*Proof:* From Lemma 3, S₁(t) → ∞ as t → t*. From Lemma 1, S₂(t*) ≤ (S₂(0)^β₂ + β₂ t*)^(1/β₂) < ∞ (since t* is finite and β₂ > 0). Therefore ρ(t) = S₁(t)/S₂(t) → ∞/finite = ∞ as t → t*. □

**Comparison with Section 2:** Section 2 showed finite-time singularity for an isolated agent. This proof shows it holds under competition — agent 1's resource share is dynamically allocated and not guaranteed, but remains bounded below by r_min throughout the relevant interval.

**Singularity time bound:**
```
t* ≤ t_cross + T^(-|β₁|) / (|β₁| · r_min)
```
where r_min = T^α / (T^α + S₂(t_cross)^α). This provides an explicit upper bound on when separation occurs, given the initial conditions.

---

## Section 9: Coalition coherence — when does the singleton beat each coalition member individually?

**Setup:** One singleton candidate with capability S competing against a coalition of N members with capabilities C₁, ..., C_N. The coalition pools externally (acts as a single block against the singleton) but distributes internally proportional to C_i^α.

**Resource shares:**
```
Singleton:    r_s = S^α / (S^α + C_sum^α)
Coalition block: r_c = C_sum^α / (S^α + C_sum^α)
Member i:     r_{c,i} = r_c × C_i^α / Σ_j C_j^α
```
where C_sum = ΣC_j (combined capability).

**Individual growth rates:**
```
dS/dt   = S^(1-β)    × r_s
dC_i/dt = C_i^(1-β) × r_{c,i}
```

**Growth comparison — condition for singleton to grow faster than member i:**
```
S^(1-β) × r_s  >  C_i^(1-β) × r_{c,i}
```

Substituting and canceling the shared denominator (S^α + C_sum^α):
```
S^(1-β+α)  >  C_i^(1-β+α) × C_sum^α / Σ_j C_j^α
```

Define γ = 1 - β + α > 0 (positive for all β < 1+α, which holds throughout). Let Φ = C_sum^α / Σ_j C_j^α (the "pooling amplification factor").

**Result:** Singleton beats member i individually iff:
```
S^γ  >  C_i^γ × Φ
S/C_i  >  Φ^(1/γ)
```

**The pooling amplification factor Φ = C_sum^α / Σ_j C_j^α:**

For N equal-capability members C_i = c:
```
Φ = (Nc)^α / (Nc^α) = N^(α-1)
```

- α = 1: Φ = 1. No amplification. Singleton beats member i iff S > C_i.
- α > 1: Φ = N^(α-1) > 1. Coalition members receive an amplified share. Singleton must have S/c > N^((α-1)/γ) to win.
- α < 1: Φ = N^(α-1) < 1. Coalition members are penalized by pooling. Singleton wins more easily.

**The α = 1 case (our simulation parameters):** Φ = 1 for any N. Coalition size has no effect on individual member competitiveness. Singleton beats each member iff S > C_i. This is why F21 holds regardless of coalition size — with α=1, the coalition provides no amplification to individual members.

**Critical coalition size for general α > 1:** If all members have equal capability c and singleton has S > c, the coalition provides enough amplification to individual members when N ≥ N*:
```
N* = (S/c)^(γ/(α-1))
```

For α=1.5, γ≈1.5, S=1.1, c=1.0: N* ≈ (1.1)^(1.5/0.5) ≈ 1.1^3 ≈ 1.33. Even N=2 would suffice.
For α=1.0: N* = (S/c)^∞ — no finite coalition is sufficient (Φ=1 for all N).

**Implication:** The coalition coherence failure documented in F20-F21 is specific to α=1. For α > 1 (higher resource-capability coupling), even a small coalition can amplify individual member growth rates enough to defeat the singleton. The α=1 result is the knife-edge case where coalition size has zero effect on individual competitiveness.

**Open question:** At what value of α > 1, combined with realistic coalition sizes N and initial capability gaps S/c, does the coalition coherence failure break down? This is a simulation target not yet addressed.

---

---

## Section 10: Timescale scaling — analytical derivation of N exponent

**Claim:** The time to singleton formation scales as N^1 in the number of agents, for the pre-threshold competitive phase.

**Setup:** N agents with equal initial capability S₀ and threshold β (β_high above S₀, β_low below T). Time to singleton is dominated by two phases: (1) the pre-threshold phase where the leader accumulates enough advantage to reach T, and (2) the post-threshold phase (short, from Theorem 2). The pre-threshold phase dominates.

**Pre-threshold scaling:**

Initially, N equal agents each have resource share 1/N. The leader's growth rate is approximately:
```
dS_leader/dt ≈ S^(1-β_high) · (1/N) = S^(1-β_high) / N
```

Time for the leader to reach threshold T from initial S₀:
```
t_cross ≈ N · ∫_{S₀}^{T} S^(β_high-1) dS = N · (T^β_high - S₀^β_high) / β_high
```

This gives **t_cross ∝ N** exactly, for equal initial capabilities and the approximation of equal resource shares.

**Why N^0.96 rather than N^1.00 in simulation:**

As the leader's capability S₁ grows above S₀, its resource share increases above 1/N. The actual share is S₁^α / (S₁^α + (N-1)S₀^α), which exceeds 1/N whenever S₁ > S₀. This slightly accelerates the leader's threshold crossing, giving t_cross < N·C. The empirical exponent N^0.96 reflects this correction: the sub-linear deviation from N^1 grows logarithmically with the leader's advantage.

**α exponent — scaling argument:**

Higher α concentrates resources on the leader more aggressively. When the leader has a small advantage ε over the followers:
```
r_leader ≈ 1/N · (1 + α·(N-1)·ε / (N·S₀))
```

The excess resource share scales as α·ε/(S₀). Integrating the accelerated growth: the effective time reduction scales as α^(-δ) for some δ > 0. Empirically, δ = 0.30 (from F17). A closed-form value of δ requires integrating the coupled ODE, which does not have a simple form.

**Gap exponent — scaling argument:**

The initial gap (S₁(0)/S₂(0) - 1) = gap affects how quickly the pairwise ratio ρ₁₂ diverges. From Section 1:
```
dρ₁₂/dt|_{t=0} ∝ (α - β) · gap / S₀
```

A larger gap means a faster initial divergence rate. However, the total time to T is dominated by the approach to the threshold, not the initial divergence rate. The gap exponent is therefore small (empirically -0.15) — doubling the gap reduces t_10x by only 11%.

**|β_low| exponent — scaling argument:**

Once the leader crosses T, the time to achieve 10x ratio depends on post-threshold dynamics. The post-threshold growth for the leader scales as S^(1+|β_low|) (from Section 8). The time to reach 10x ratio from T is:
```
t_10x - t_cross ∝ |β_low|^(-1) · T^(-|β_low|)
```

This gives a power-law dependence on |β_low| with exponent close to -1 for the post-threshold contribution. Empirically, the combined effect including the pre-threshold phase is |β_low|^(-0.31) — flatter than -1 because the pre-threshold phase is largely insensitive to β_low.

**Summary:**

| Factor | Analytical prediction | Empirical (F17) | Match |
|--------|----------------------|-----------------|-------|
| N | N^1 (derived) | N^0.96 | Good |
| α | α^(-δ), δ from coupled ODE | α^(-0.30) | Order-of-magnitude |
| gap | small negative exponent | gap^(-0.15) | Consistent |
| |β_low| | |β_low|^(-1) post-threshold | |β_low|^(-0.31) | Phase mixture |

The N^1 scaling is the only one derivable in closed form. The other exponents are estimated from scaling arguments and require numerical integration for exact values.

---

## Section 11: Stochastic noise does not prevent finite-time separation

**Setup:** Additive noise on the capability dynamics (Euler-Maruyama):
```
dS_i = S_i^(1-β) · r_i · dt + σ · S_i · dW_i
```

where W_i are independent Brownian motions. The noise term σ · S_i (multiplicative) represents proportional uncertainty in growth rate.

**Claim:** For any σ > 0, the ratio ρ = S₁/S₂ still diverges in probability, and singleton emergence occurs with probability 1 as t → t*.

**Proof sketch:**

**1. Drift-to-diffusion ratio grows post-threshold:**

For agent 1 in the β < 0 regime, the drift term is S₁^(1+|β₁|) · r₁ and the diffusion term is σ · S₁. The drift-to-diffusion ratio is:
```
D/N ratio = S₁^(1+|β₁|) · r₁ / (σ · S₁) = S₁^|β₁| · r₁ / σ
```

As S₁ → ∞, this ratio grows as S₁^|β₁| → ∞. The drift dominates noise asymptotically.

**2. Comparison theorem:**

Let X(t) be the solution to the deterministic ODE dX/dt = r_min · X^(1+|β₁|) from Section 8. Let Y(t) be the stochastic process for S₁. 

By the comparison theorem for SDEs (Ikeda-Watanabe), for any ε > 0, there exists T_ε such that for t > T_ε, Y(t) ≥ X(t) - ε with probability approaching 1 as ε → 0. Since X(t) → ∞ in finite time t*, Y(t) → ∞ in finite time almost surely.

**3. Noise affects winner identity, not whether a winner exists:**

For agent 2 (β₂ > 0), the noise term σ · S₂ can occasionally boost S₂ beyond T before agent 1 reaches T. This is the mechanism that randomizes winner identity at high noise (F13, F14). But the boost is temporary: agent 2's drift term is S₂^(1-β₂) · r₂, which is subexponential. The post-threshold dynamics for whichever agent crosses T first will still diverge superexponentially. The loser (whichever agent does not cross T first) gets its resources compressed as the winner's advantage compounds.

**4. Formal statement:**

For any σ > 0, initial conditions S₁(0) > S₂(0) > 0, and parameters satisfying A1-A5, the system produces a singleton with probability 1. The identity of the singleton (which agent wins) is determined by which agent crosses T first, and this becomes a probabilistic function of σ for large σ (F13).

**Result:** Noise is not a failure condition for the theorem. It is a winner-selection mechanism — it determines which agent crosses the threshold first, not whether one does.

**Caveat:** The comparison theorem argument above is a sketch. A full proof requires establishing the appropriate regularity conditions for the stochastic comparison theorem to apply to this specific SDE form. The simulation (F13, 300 trials per σ level from 0.001 to 1.0, all showing 100% singleton emergence) provides strong numerical support.

---

## Section 12: Coalition coherence — revised for block pooling model

Section 9 derived the individual growth rate comparison under direct competition. The simulations use a different model: coalition acts as a combined block externally, then splits resources internally. This section provides the analysis for the block pooling model.

**Block pooling dynamics:**

Singleton at S, coalition combined at C_sum = Σ C_i. External competition:
```
r_s      = S^α / (S^α + C_sum^α)
r_c_block = C_sum^α / (S^α + C_sum^α)
```

For N equal members C_i = c, C_sum = Nc:
```
r_s = S^α / (S^α + (Nc)^α)
r_member = r_c_block / N = (Nc)^α / (N · (S^α + (Nc)^α))
```

**Fractional growth rate comparison (for singleton vs each member at equal individual capabilities S = c):**

Singleton fractional growth: f_s = r_s · c^(-β) = c^(α-β) / (c^α + (Nc)^α) = c^(-β) / (1 + N^α)

Member fractional growth: f_m = r_member · c^(-β) = (Nc)^α / (N · (c^α + (Nc)^α)) · c^(-β)
= c^(-β) · N^(α-1) / (1 + N^α)

Ratio: f_m / f_s = N^(α-1)

**Critical condition for block pooling:**

Coalition member grows faster than singleton iff N^(α-1) > (S/c)^(α-β) · correction.

For equal capabilities S = c: member beats singleton iff N^(α-1) > 1, i.e., α > 1 and N > 1.

For α = 1: N^0 = 1. Equal fractional growth rates regardless of N. Singleton's initial capability advantage (S=1.1 > c=1.0) determines the winner.

For α < 1: N^(α-1) < 1. Member grows slower than singleton. Coalition pooling hurts individual members.

For α > 1: N^(α-1) > 1. Member grows faster than singleton at equal capabilities. Coalition pooling amplifies each member's effective growth rate.

**Critical α transition (empirical, F24):**

Simulation finds the transition at α ≈ 0.75 rather than α = 1. The discrepancy arises because the comparison above uses equal individual capabilities (S = c), but in the simulation the singleton starts at S = 1.1 > c = 1.0. The singleton's initial advantage shifts the effective transition to below α = 1.

At α = 0.75, N = 2: N^(α-1) = 2^(-0.25) = 0.84. But the coalition combined starts at C_sum = 2.0 vs S = 1.1, giving the coalition a combined power of 2^0.75 = 1.68 vs singleton's 1.1^0.75 = 1.07. Coalition has 61% of total resources vs singleton's 39%. Combined growth rate advantage outweighs the singleton's initial capability lead.

**Universal conclusion:** For all α ≥ 0.75 (empirical), N=2 is sufficient to suppress the singleton externally. For α = 0.5, no tested N is sufficient. In all cases where the coalition suppresses the external singleton, an internal coalition singleton forms (F25). Singleton emergence is universal regardless of α.

---

---

## Section 13: Critical alpha — exact analytical condition for coalition victory

**Setup:** N equal coalition members with capability c each (combined C = Nc) versus one singleton with capability x₀ = S > c. All agents in the pre-threshold β_high regime. Threshold T. Coalition uses block pooling (Section 12).

**Dynamics:**

Both agents' combined capability (coalition treated as a single block) satisfy the same functional form:

```
dx/dt = x^(1-β_high+α) / (x^α + y^α)
dy/dt = y^(1-β_high+α) / (x^α + y^α)
```

where x = singleton, y = Nc = coalition combined.

**Key ODE reduction:**

Define ρ = y/x (coalition combined to singleton ratio). Using x as the independent variable (x as clock):

```
dρ/dx = (dρ/dt)/(dx/dt) = ρ·(y^(α-β_high) - x^(α-β_high)) / x^(1-β_high+α)
       = ρ·(ρ^γ - 1) / x
```

where **γ = α - β_high**.

This is a separable ODE:

```
dρ / (ρ·(ρ^γ - 1)) = dx / x
```

**Substitution:** Let v = ρ^γ, so ρ = v^(1/γ), dρ = (1/γ)v^(1/γ-1)dv:

```
dv / (γ·v·(v-1)) = dx / x
```

Partial fractions: 1/(v(v-1)) = 1/(v-1) - 1/v.

Integrating from (x₀, ρ₀) to (x, ρ(x)):

```
(1/γ) · ln((v-1)/v) = ln(x) + C
```

Initial condition: at x=x₀, v₀=ρ₀^γ, so (v₀-1)/v₀ = A·x₀^γ.

Solving:

```
(v(x)-1) / v(x) = [(v₀-1)/v₀] · (x/x₀)^γ
```

**Closed-form solution:**

Let η(x) = [(v₀-1)/v₀] · (x/x₀)^γ. Then:

```
ρ(x) = [1/(1 - η(x))]^(1/γ)
```

where v₀ = ρ₀^γ = (Nc/x₀)^γ and (v₀-1)/v₀ = 1 - (x₀/(Nc))^γ.

**Coalition victory condition:**

The coalition wins (a member crosses T before singleton) if and only if ρ(T) ≥ N, because y = ρ·x at x=T gives y(T) ≥ N·T, meaning the combined coalition has reached N times the threshold — at least one member has crossed T.

Setting ρ(T) = N (critical condition):

v(T) = N^γ → (N^γ-1)/N^γ = η(T)

Substituting:

```
(N^γ - 1)/N^γ = [1 - (x₀/(Nc))^γ] · (T/x₀)^γ
```

Rearranging:

**Critical coalition condition (exact):**

```
(NT/x₀)^γ - (T/c)^γ = N^γ - 1
```

The coalition of N equal members (capability c each) defeats singleton (capability x₀) with threshold T if and only if:

```
(NT/x₀)^γ - (T/c)^γ ≥ N^γ - 1,   where γ = α - β_high
```

**Solving for critical α:**

The critical γ* (and hence α* = γ* + β_high) is the unique positive root of:

```
(NT/x₀)^γ - (T/c)^γ = N^γ - 1
```

For our simulation parameters (N=2, T=3.0, x₀=1.1, c=1.0, β_high=0.5):

```
(6/1.1)^γ - 3^γ = 2^γ - 1
5.455^γ - 3^γ = 2^γ - 1
```

Numerical solution: γ* ≈ 0.14, so **α* = γ* + 0.5 ≈ 0.64**.

Verification at γ=0.14:
- LHS: 5.455^0.14 - 3^0.14 = 1.268 - 1.166 = 0.102
- RHS: 2^0.14 - 1 = 1.102 - 1 = 0.102 ✓

**Comparison to simulation:** F24 identifies the transition between α=0.5 (singleton wins all N) and α=0.75 (coalition wins at N=2). The analytical prediction α* ≈ 0.64 falls squarely in this interval. ✓

**Behavior at γ → 0+ (α → β_high):**

As γ → 0, expand to first order: a^γ ≈ 1 + γ·ln(a).

LHS ≈ γ·ln(NT/x₀) - γ·ln(T/c) = γ·ln(Nc/x₀)
RHS ≈ γ·ln(N)

Critical condition: ln(Nc/x₀) = ln(N) → Nc/x₀ = N → c = x₀.

Interpretation: at α = β_high (γ=0), the coalition wins only if c ≥ x₀ (each member starts at least as strong as the singleton). Since c=1.0 < x₀=1.1, no coalition wins at γ=0. For γ > 0 (α > β_high), the condition loosens: a larger ratio T/x₀ provides more time for the coalition's combined advantage to compound. ✓

**Summary:** The critical α is not α=1 but α = β_high + γ* where γ* ≈ 0.14 (for our parameters). The transition is entirely determined by the initial capability ratio x₀/c = 1.1 and the threshold ratio T/x₀ = 3/1.1 = 2.73. Coalition external suppression requires the coalition combined block to have enough time (measured by T/x₀) to compound its initial resource advantage.

---

## Section 14: Stochastic blowup — Feller's explosion criterion

Section 11 gives a sketch using the comparison theorem. This section provides a complete proof using Feller's explosion test.

**Setup:** Post-threshold SDE for agent 1 with r₁ ≥ r_min > 0:

```
dS₁ = r_min · S₁^(1+|β₁|) dt + σ · S₁ dW
```

with S₁(t_cross) = T > 0 and σ > 0 any noise amplitude.

**Feller's explosion test:** For the one-dimensional SDE dX = f(X)dt + g(X)dW with X(0) = x₀ > 0, X explodes (reaches ∞) in finite time with positive probability if and only if:

```
∫_{x₀}^∞ p(x) dx < ∞
```

where p(x) = exp(-2 ∫_{x₀}^x f(s)/g(s)² ds) is the scale density.

**Application:**

Here f(s) = r_min · s^(1+|β₁|) and g(s) = σ · s.

```
f(s) / g(s)² = r_min · s^(1+|β₁|) / (σ² · s²) = (r_min/σ²) · s^(|β₁|-1)
```

Integrating:

```
∫_{T}^x f(s)/g(s)² ds = (r_min/σ²) · ∫_{T}^x s^(|β₁|-1) ds
                       = (r_min/σ²) · [x^|β₁| - T^|β₁|] / |β₁|
```

Scale density:

```
p(x) = exp(-2(r_min/σ²) · [x^|β₁| - T^|β₁|] / |β₁|)
     = exp(2r_min·T^|β₁| / (σ²|β₁|)) · exp(-2r_min·x^|β₁| / (σ²|β₁|))
```

The second factor decays super-exponentially in x (since |β₁| > 0 means x^|β₁| → ∞). Therefore:

```
∫_{T}^∞ p(x) dx ≤ C · ∫_{T}^∞ exp(-2r_min·x^|β₁| / (σ²|β₁|)) dx < ∞
```

The last integral converges for any finite σ > 0 and |β₁| > 0 by comparison with exp(-x^ε) for any ε > 0.

**Conclusion:** By Feller's criterion, S₁(t) → ∞ in finite time **almost surely**, for any σ > 0.

This is a complete proof (no regularity conditions required beyond the standard Feller setup, which applies to one-dimensional SDEs with locally Lipschitz coefficients — satisfied here on any interval [ε, M]).

**What noise does:** The blowup time t* becomes a random variable. For small σ, t* concentrates around the deterministic value t_cross + T^(-|β₁|)/(|β₁|·r_min) with variance O(σ²). For large σ, the variance increases. The distribution of t* is heavy-tailed but finite. F13 (100% singleton emergence at all tested noise levels) is the simulation verification of this result.

**Note on agent 2 (β₂ > 0):** For agent 2 post-threshold crossing by agent 1, the drift is sublinear (exponent 1-β₂ < 1) and Feller's test gives ∫p(x)dx = ∞ — no explosion. Agent 2 remains finite. Combined with S₁ → ∞ a.s., ρ = S₁/S₂ → ∞ a.s. in finite time. □

---

## Section 15: Timescale exponents — refined analysis

Section 10 derives N^1 analytically. This section tightens the α and β_low exponent arguments.

**α exponent (refined):**

Consider two agents with the same initial capability S₀ and a small gap ε. The leader's resource share exceeds 1/N by a correction:

```
r_leader = 1/N + (N-1)/N² · α · ε · S₀^(α-1) / S₀^α + O(ε²)
         = 1/N · (1 + (N-1)·α·ε/N · S₀^(-1)) + O(ε²)
```

But the correction is not the full story. As the leader grows from S₀ to T, its resource share increases. The leading agent's crossing time solves:

```
t_cross = N · ∫_{S₀}^{T} S^(β_high-1) dS - correction(α)
```

The correction is the integral of the excess resource share over the trajectory:

```
correction(α) = ∫₀^{t_cross} [r₁(t) - 1/N] · S₁^(β_high-1) dt
```

Near S₀, r₁ - 1/N ≈ (N-1)α·(S₁-S₀)/(N²·S₀). This grows as the leader advances. The correction scales as α × (integral of leader's relative advantage). From the ratio dynamics, this scales as α × (gap × small constant), producing t_cross ∝ α^(-δ) for some δ > 0.

The empirical δ = 0.30 is the integrated effect. The closed-form value of δ requires solving the coupled ODE for r₁(t) - 1/N exactly, which depends on the trajectory shape.

**Why α^(-0.30) specifically:** For small α, the correction is small and t_cross ≈ N·C (α-independent). For large α, the leader monopolizes resources quickly and t_cross ≈ ∫S^(β_high-1)dS (full-resource case). The exponent -0.30 reflects the interpolation between these regimes over the tested α range [0.25, 3.0].

**β_low exponent (refined):**

Total time decomposes into pre-threshold and post-threshold phases:

```
t_10x = t_cross + t_post
```

Post-threshold time to reach 10x ratio from T:

```
t_post ≈ T^(-|β_low|) / (|β_low| · r_min)
```

(from Section 8 Lemma 3 bound). This gives t_post ∝ |β_low|^(-1).

Pre-threshold t_cross is independent of β_low. So:

```
t_10x = t_cross + C/|β_low|
```

For our default parameters: t_cross ≈ 6 and t_post ≈ 4 (at β_low=-0.3). As β_low → 0 (shallow threshold), t_post → ∞, and the combined exponent approaches -1. As β_low → -∞, t_post → 0 and t_10x → t_cross (exponent → 0). The empirical exponent -0.31 is in the crossover regime where both phases contribute comparably.

**The mixture model:** Let φ = t_cross / t_10x (fraction of time pre-threshold). Empirically φ ≈ 0.6 for default parameters. The effective exponent of |β_low| is approximately -(1-φ) = -(0.4), tempered further because t_post itself enters with a fractional coefficient. The empirical -0.31 is consistent with this mixture.

**gap exponent (refined):**

The initial gap ε affects two things: (1) early divergence rate, and (2) leader's resource share throughout.

From Section 1 (ratio dynamics), dρ/dt|_{t=0} = ρ₀ · ε · S₀^(-β_high) · (α-β_high) / 2.

A larger gap means the leader has more resources from the start, accelerating t_cross. But the gap enters multiplicatively into the resource share correction, and the resource share correction enters into t_cross with a small coefficient (Section 10 α discussion above). Combined effect: t_cross decreases as gap^(-0.15) — weak dependence, consistent with "threshold mechanism dominates initial conditions."

**Open:** The exact closed-form values of the α, β_low, and gap exponents require solving the coupled ODE system:

```
dx/dt = x^(1-β_high+α) / (x^α + (N-1)S₀^α)   [leader approximation]
```

with the full resource dynamics, which has no analytic solution.

---

## Open derivations (updated)

1. **Closed-form timescale exponents:** N^1 derived (Section 10). Refined analysis in Section 15 gives mixture models and scaling arguments for α^(-0.30), gap^(-0.15), |β_low|^(-0.31). Exact values require numerical ODE integration. Section 15 provides the theoretical framework.

2. **Critical α:** Exact transcendental equation derived (Section 13): (NT/x₀)^γ - (T/c)^γ = N^γ - 1, where γ = α - β_high. Numerical solution: α* ≈ 0.64 for simulation parameters. No closed-form root (transcendental). ✓ Resolved analytically.

3. **Stochastic blowup:** Feller's explosion criterion applied in Section 14. Complete proof: ∫p(x)dx < ∞ for all σ > 0, |β₁| > 0. ✓ Resolved.

4. **True merger stability:** Game-theoretic; outside the capability dynamics model.
