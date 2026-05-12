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

## Open derivations

The following are needed to complete the proof but are not yet derived:

1. **Exact timescale:** How long does singleton emergence take as a function of N, initial capability spread σ, α, and β? The simulations will measure this empirically first; analytical expressions to follow.

2. **Stochastic perturbations:** All derivations above are deterministic. Real systems have noise. Does the singleton result hold in expectation under stochastic capability and resource dynamics? Preliminary expectation: yes, because the feedback is positive (advantage compounds), but formal proof needed.

3. **Continuous agent entry (Failure mode F3):** If new agents enter the environment at rate λ with initial capability drawn from distribution P(S₀), does the incumbent singleton maintain dominance? Depends on whether the incumbent's growth rate exceeds the maximum growth rate of any new entrant. Formal analysis pending.
