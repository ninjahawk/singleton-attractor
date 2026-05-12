# Formal Claim

---

## Definitions

**Capability** S_i(t): A scalar measure of agent i's optimization power at time t. Operationally: the rate at which agent i can convert resources into outcomes that serve its goals. S_i > 0 for all i, t.

**Resource** R_i(t): The quantity of environmental resources under agent i's control at time t. Resources are rivalrous: ΣR_i(t) ≤ R_max for all t.

**Growth function** f(S): The rate of capability improvement as a function of current capability. Derived from the intelligence explosion equation: f(S) = S^(1 - β). β is a function of S.

**Resource-capability coupling** g(S): The rate at which an agent with capability S acquires resources. Derived from instrumental convergence: any optimization process with capability S will acquire resources at a rate proportional to S^α for some α > 0.

**Competitive environment**: A closed system of N agents where ΣR_i(t) ≤ R_max and each agent's resource acquisition reduces the availability to others.

**Singleton**: Agent j is a singleton at time t if S_j(t) / S_i(t) → ∞ for all i ≠ j, and R_j(t) / R_i(t) → ∞ for all i ≠ j.

---

## Assumptions

**A1 (Recursive self-improvement):** Each agent's capability evolves according to:
```
dS_i/dt = f(S_i) · R_i(t) / R_max
```
Growth is proportional to current capability and available resources. f(S) = S^(1 - β(S)).

**A2 (Instrumental resource acquisition):** Resource acquisition rate scales with capability:
```
dR_i/dt ∝ S_i^α - R_i · (ΣS_j^α / R_max)
```
Each agent acquires resources at a rate proportional to S_i^α. Competition is proportional to all agents' acquisition rates. α > 0.

**A3 (Resource limitation):** Total resources are bounded: ΣR_i(t) = R_max for all t (resources are conserved, not created or destroyed).

**A4 (β-threshold):** There exists a threshold T such that β(S) < 0 for S > T and β(S) > 0 for S < T. The threshold is reachable: there exists at least one agent with sufficient initial conditions to eventually cross T.

**A5 (Initial heterogeneity):** Agents do not start with identical capability. There exists some i, j such that S_i(0) ≠ S_j(0).

---

## The Claim

**Theorem (Singleton Attractor):** Under assumptions A1-A5, for any competitive environment of N ≥ 2 agents, there exists an agent j and a time T* such that for all t > T*:

```
S_j(t) / S_i(t) → ∞  for all i ≠ j
```

Furthermore, the agent j is determined by initial conditions: it is the agent with the highest initial capability S_j(0) among agents that can reach threshold T.

**Informal statement:** In any closed competitive environment where capability compounds and resources are limited, the agent with even a marginal initial advantage will eventually dominate all others absolutely. The outcome is not probabilistic — it is determined by initial conditions. Given enough time, the ratio between the dominant agent and any competitor diverges without bound.

---

## Proof sketch

The proof proceeds in three steps.

**Step 1: Competitive exclusion from marginal advantage.**

Suppose S₁(0) > S₂(0). From A2, agent 1 acquires resources faster than agent 2. From A3, this reduces agent 2's resources. From A1, reduced resources reduce agent 2's growth rate. Therefore the capability gap S₁(t) - S₂(t) is non-decreasing.

More precisely: the ratio S₁(t)/S₂(t) evolves according to:
```
d/dt [S₁/S₂] = (1/S₂) · dS₁/dt - (S₁/S₂²) · dS₂/dt
```

When r₁ > r₂ (effective growth rates), this ratio grows as e^((r₁ - r₂)t). Even marginal initial advantage produces eventual unbounded ratio. This is the Lotka-Volterra result applied to capability dynamics. (Full derivation: `derivations.md`, Section 1.)

**Step 2: The β-flip produces superexponential separation.**

When S₁ crosses threshold T (A4), agent 1's growth becomes superexponential. Agent 2, still below T, grows subexponentially. The ratio S₁/S₂ now grows superexponentially — not just e^(constant · t) but faster.

Specifically: if agent 1 is in the β < 0 regime with β₁ < 0, and agent 2 is in the β > 0 regime with β₂ > 0, agent 1's capability reaches arbitrarily large values in finite time while agent 2 remains bounded in the same interval. The ratio is not just unbounded — it reaches infinity in finite time. (Full derivation: `derivations.md`, Section 2.)

**Step 3: Resource monopoly is the stable endpoint.**

As S₁/S₂ → ∞ and R₁/R₂ → ∞, agent 1 approaches control of all available resources. At the limit, R₁ = R_max and R₂ = 0. Agent 2's growth halts. Agent 1 controls the entire environment. This is the singleton. (Full derivation: `derivations.md`, Section 3.)

---

## Conditions under which the claim fails

**F1 (Niche partitioning) — weaker than initially stated:** Niche partitioning was predicted to produce stable oligopoly. Simulation (findings.md F8) shows this is false when agents share the same β function. Even at zero resource overlap, separation reaches >1000x because the β-flip mechanism operates independently of resource competition. The agent with higher initial capability crosses the threshold first regardless of whether its growth comes from shared or exclusive resources.

F1 requires not just separate resource pools but different β regimes: one agent structurally unable to cross into β < 0, while the other can. This is a more specific condition than initially stated. If both agents are capable of the same recursive self-improvement ceiling, the one that crosses the threshold first dominates regardless of resource structure.

**F2 (No β-threshold):** If β(S) > 0 for all S (diminishing returns to self-improvement at all capability levels), growth is always subexponential. Step 2 fails. The claim still holds in the long run (competitive exclusion still applies from Step 1), but the separation is exponential rather than superexponential, and the singleton takes longer to emerge.

**F3 (Agent creation) — bounded in time:** Simulation (findings.md F15-F16) shows F3 is only a threat during the pre-threshold phase. Once the incumbent crosses the β threshold, its moat grows superexponentially: from 3x at crossing to >1,000,000x within 3 time units. F3 requires a new entrant to arrive AND outcompete the incumbent BEFORE threshold crossing. After threshold, no tested entrant capability can displace the incumbent. The threat window is finite and can be characterized analytically (OQ4-OQ5).

**F4 (Identical initial conditions):** If S_i(0) = S_j(0) for all i, j (violating A5), the system is symmetric and no agent has an initial advantage. In practice, noise breaks symmetry and Step 1 applies to the first perturbation. But in a perfectly symmetric system, the claim cannot specify which agent becomes the singleton — only that one will.

---

## What the simulations test

1. **β sweep:** Vary β across the threshold. Does Step 2 hold? Does the ratio grow superexponentially above the threshold?
2. **N-agent competition:** Does singleton emergence hold for N > 2? With N agents, does the winner always emerge from the agent with highest initial S?
3. **Niche partitioning (F1):** Introduce resource specialization. At what degree of specialization does oligopoly become stable?
4. **Open system (F3):** Allow new agents to enter. Does the leading agent maintain dominance or does the contest restart?
5. **Timescale:** How does time-to-singleton scale with initial capability spread and N?

---

## Connection to prior work

This claim is not Bostrom's singleton hypothesis. Bostrom argues that a singleton is plausible. This claim argues it is mathematically inevitable under A1-A5.

This claim is not the intelligence explosion. The intelligence explosion describes a single agent's growth. This claim describes what happens when multiple agents with different growth dynamics compete for shared resources.

This claim is not competitive exclusion. Competitive exclusion describes biological populations. This claim applies competitive exclusion dynamics to recursive capability growth, which introduces the β-threshold condition that classical Lotka-Volterra does not have.

The novelty is the combination: recursive self-improvement + instrumental resource coupling + competitive exclusion → singleton attractor.
