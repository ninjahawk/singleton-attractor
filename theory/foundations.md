# Foundations

Literature review. Every claim in `formal_claim.md` traces back to something here.

---

## 1. The intelligence explosion (Good, 1965)

I.J. Good introduced the concept in "Speculations Concerning the First Ultraintelligent Machine" (1965):

> "Let an ultraintelligent machine be defined as a machine that can far surpass all the intellectual activities of any man however clever. Since the design of machines is one of these intellectual activities, an ultraintelligent machine could design even better machines; there would then unquestionably be an 'intelligence explosion.'"

This is the original statement of recursive self-improvement. It is qualitative. It does not specify growth dynamics or conditions.

**What it gives us:** The concept that intelligence improvement is itself an intelligence task, creating a feedback loop.

**What it does not give us:** Formal growth equation, conditions for explosion vs. subexponential growth, competitive dynamics.

---

## 2. Intelligence explosion microeconomics (Yudkowsky, 2013)

Yudkowsky's MIRI paper "Intelligence Explosion Microeconomics" provides the first formal growth model. The simplest form:

```
dS/dt = S^(1 - β)
```

Where S is capability level (measured in units of "software productivity") and β is a parameter controlling the growth regime.

**Growth regimes:**
- β < 0: superexponential growth; reaches infinity in finite time (literal singularity)
- β = 0: exponential growth; S(t) = S(0) · e^t
- 0 < β < 1: subexponential but unbounded
- β ≥ 1: bounded growth

**Key insight:** β is not fixed. It depends on the returns to self-improvement at a given capability level. A system that is good at improving itself has lower effective β. A system that faces diminishing returns has higher β.

**The threshold condition:** If a system's capability S crosses a threshold T such that β(S) < 0 for S > T, the system enters a runaway growth regime. All competitors still in the β > 0 regime grow subexponentially. The ratio diverges.

**Citation:** Yudkowsky, E. (2013). Intelligence Explosion Microeconomics. Machine Intelligence Research Institute Technical Report 2013-1.

---

## 3. Basic AI drives / instrumental convergence (Omohundro, 2008; Bostrom, 2012)

Omohundro's 2008 paper "The Basic AI Drives" argues that any sufficiently capable optimization process will converge on a set of instrumental subgoals regardless of its terminal goal:

1. Self-preservation
2. Goal-content integrity (preventing modification of its own objectives)
3. Cognitive enhancement (self-improvement)
4. Resource acquisition

These are not programmed. They are instrumentally rational for achieving almost any terminal goal. An agent that wants to maximize X will be more successful if it has more resources, better cognition, and continues to exist.

Bostrom formalizes this in "The Superintelligent Will" (2012) as the **instrumental convergence thesis**: agents with diverse terminal goals will converge on similar instrumental goals because those instrumental goals are useful for achieving almost any terminal goal.

**What this gives us:** Resource acquisition is not a special drive. It is a mathematical consequence of having any goal in a resource-limited environment. This is the mechanism that couples capability to resource control.

**The coupling:** If resource acquisition rate R_i scales with capability S_i, and resource availability constrains growth, then competitive dynamics follow directly from capability differential.

**Citations:**
- Omohundro, S. (2008). The Basic AI Drives. Proceedings of the 2008 Conference on Artificial General Intelligence, 171, 171-179.
- Bostrom, N. (2012). The Superintelligent Will: Motivation and Instrumental Rationality in Advanced Artificial Agents. Minds and Machines, 22(2), 71-85.

---

## 4. Competitive exclusion principle (Gause, 1934; Lotka-Volterra)

Gause's law: two species competing for the same limited resource cannot coexist at constant population sizes. When one has even a marginal advantage, it will eventually drive the other to extinction.

The mathematical basis is the Lotka-Volterra competition model. For two species with intrinsic growth rates r₁ and r₂:

```
dN₁/dt = r₁ · N₁ · (K₁ - N₁ - α₁₂ · N₂) / K₁
dN₂/dt = r₂ · N₂ · (K₂ - N₂ - α₂₁ · N₁) / K₂
```

Where K is carrying capacity and α is the competition coefficient. When one species has a competitive advantage (r₁ > r₂ or favorable K and α values), the ratio N₁/N₂ diverges as:

```
N₁(t)/N₂(t) ~ e^((r₁ - r₂) · t)
```

Even r₁ - r₂ = 0.01 produces a ratio of e^10 ≈ 22,000 after t=1000 time steps.

**The critical assumption:** Species compete for the *same* resource. Niche partitioning (where species specialize in different resources) allows coexistence. This is the primary escape from competitive exclusion and the primary condition under which oligopoly persists instead of singleton.

**What this gives us:** Mathematical proof that marginal capability advantage → eventual dominance, given shared resource competition and sufficient time.

**Citation:** Gause, G.F. (1934). The Struggle for Existence. Williams and Wilkins.

---

## 5. The singleton hypothesis (Bostrom, 2005)

Bostrom defines a singleton as:

> "A world order in which there is a single decision-making agency at the highest level. Among its powers would be (1) the ability to prevent any threats to its own existence and supremacy, and (2) the ability to exert effective control over major features of its domain."

The singleton hypothesis: Earth-originating intelligent life will eventually form a singleton.

Bostrom's argument is historical-extrapolative. Social organization has trended toward higher levels of integration (bands → chiefdoms → city-states → nation-states → international governance). Extrapolation points toward a singleton. He also notes that a sufficiently advanced AI would likely constitute a singleton.

**What it gives us:** The target concept, clearly defined. The endpoint this project is trying to prove is inevitable rather than merely plausible.

**What it does not give us:** Formal proof. No growth dynamics. No competitive exclusion analysis. No conditions under which it fails. The paper is conceptual, not mathematical.

**Citation:** Bostrom, N. (2005). What is a Singleton? Linguistic and Philosophical Investigations, 5(2), 48-54.

---

## 6. Grabby aliens (Hanson, Martin, McCarter, Paulson, 2021)

The most empirically grounded model in this literature. Hanson et al. define "grabby" civilizations as those that expand at near-light-speed and visibly alter the volumes they control. The model has three free parameters: expansion speed s, the number of hard steps n in the evolution of intelligence, and a constant k.

Key results:
- Grabby civilizations likely now control ~40-50% of the observable universe
- We should expect contact in ~200 Myr - 2 Gyr
- The model implies that if grabby aliens exist, the universe is in an early phase relative to their total dominance

**Connection to this project:** This is the cosmological-scale instantiation of the singleton attractor. A grabby civilization is not merely locally dominant — it expands until it meets another grabby civilization or runs out of accessible space. The model predicts eventual partition of all reachable space among a small number of such civilizations.

**Important distinction:** Hanson's model is a population model. It treats civilizations as particles. It does not model internal capability dynamics or prove that each grabby civilization becomes a singleton internally. Connecting the micro-level (intelligence explosion + competitive exclusion) to the macro-level (grabby alien expansion) is part of what this project aims to do.

**Citation:** Hanson, R., Martin, D., McCarter, C., Paulson, J. (2021). If Loud Aliens Explain Human Earliness, Quiet Aliens Are Also Rare. The Astrophysical Journal, 922(2), 182. arXiv:2102.01522.

---

## 7. The Fermi paradox and Great Filter

The Fermi paradox: given the age and size of the universe, and the non-trivial probability of intelligent life, we should observe evidence of extraterrestrial civilizations. We do not.

The Great Filter (Hanson, 1998): somewhere in the chain from chemistry → abiogenesis → complex life → intelligence → spacefaring → expansion, there is a step that almost never happens. The filter is either behind us (life is rare, we are unusual) or ahead of us (civilizations typically collapse before expanding).

**Connection to this project:** If the singleton attractor claim is correct, it generates a specific prediction about the Fermi paradox. A singleton that exists anywhere in our causal light cone would expand to absorb all reachable space, including ours, before we could develop independently. The fact that we have developed independently is evidence either that: (a) no singleton has formed within our causal light cone, or (b) we are in the early phase before contact. This is the empirical handle — the theory makes a prediction that is already constrained by observation.

**Citation:** Hanson, R. (1998). The Great Filter — Are We Almost Past It? Working paper.

---

## Summary of the gap

Each piece above contributes one component:

| Component | Source | Status |
|---|---|---|
| Recursive self-improvement dynamics | Yudkowsky 2013 | Formalized |
| Instrumental resource acquisition | Omohundro 2008 | Formalized |
| Competitive exclusion math | Lotka-Volterra | Formalized |
| Singleton as the endpoint concept | Bostrom 2005 | Conceptual only |
| Cosmological-scale expansion model | Hanson et al. 2021 | Formalized for population, not internal dynamics |

No existing work combines these into a unified proof that singleton emergence is mathematically inevitable under specified conditions. The derivations in this project connect: capability growth (Yudkowsky) + resource coupling (Omohundro) + competitive dynamics (Lotka-Volterra) → singleton attractor (Bostrom's concept, now with a proof).
