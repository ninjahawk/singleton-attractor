<div align="center">

# Singleton Attractor

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://python.org)
[![NumPy](https://img.shields.io/badge/NumPy-scientific_computing-013243?logo=numpy&logoColor=white)](https://numpy.org)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-visualization-11557c)](https://matplotlib.org)
[![Status](https://img.shields.io/badge/status-in_progress-yellow)](https://github.com/ninjahawk/singleton-attractor)

**Formal theory and simulation — competitive capability dynamics in multi-agent systems**

Does a single dominant intelligence inevitably emerge from any sufficiently large and old competitive environment? This project formalizes the claim, derives the conditions, and tests them in simulation.

</div>

---

## Claim

> In any causally connected region of sufficient size and age, if intelligence can arise, a single dominant intelligence is the most stable long-run attractor — not because of external constraint, but because capability advantages compound superlinearly and causal reach expands proportionally to capability.

This is falsifiable. It predicts outcomes about the Fermi paradox, the long-run structure of multi-agent AI ecosystems, and the conditions under which oligopoly is stable versus unstable.

---

## Model

The formal model combines three existing mathematical frameworks:

**1. Recursive self-improvement (intelligence explosion equation)**

```
dS/dt = S^(1 - β)
```

S is capability level. β < 0 produces a singularity in finite time. β = 0 produces exponential growth. β > 0 is subexponential. The critical question: does a competing agent that crosses into β < 0 territory achieve unbounded separation from all competitors?

**2. Competitive exclusion (Lotka-Volterra competition)**

Two agents competing for a shared resource with growth rates r₁ > r₂ diverge in population ratio as:

```
ratio(t) = e^((r₁ - r₂) · t)
```

Even a marginal advantage diverges to infinity over sufficient time. The question: does capability map cleanly onto competitive growth rate?

**3. Capability-resource coupling**

Resource acquisition is an instrumental goal for any optimization process (Omohundro 2008). Capability and resource control are therefore coupled — higher capability produces higher resource acquisition rate, which produces higher capability. The question: does this feedback loop produce the β-flip that triggers the singularity?

**Combined claim:** When these three dynamics operate simultaneously, the system has a singleton attractor — one agent dominates with probability approaching 1 as t → ∞, under conditions to be specified.

---

## Prior work

| Work | Author | Year | Role here |
|---|---|---|---|
| Singleton Hypothesis | Bostrom | 2005 | Defines the endpoint; argues plausibility; does not prove it |
| Basic AI Drives | Omohundro | 2008 | Mechanism: resource acquisition is instrumentally convergent |
| The Superintelligent Will | Bostrom | 2012 | Formalizes instrumental convergence |
| Intelligence Explosion Microeconomics | Yudkowsky (MIRI) | 2013 | Source of the dS/dt equation |
| Grabby Aliens | Hanson et al. | 2021 | Cosmological-scale empirical model of dominant expanding civilizations |
| Competitive Exclusion | Lotka-Volterra | — | Mathematical basis for why one agent wins |

The gap: nobody has combined these into a unified formal proof that singleton emergence is mathematically inevitable under specified conditions. That is what this project attempts.

---

## Key questions

| # | Question | Status |
|---|----------|--------|
| 1 | Does capability-resource coupling produce the β-flip? | Open |
| 2 | Does the β-flip produce unbounded competitive separation in finite time? | Open |
| 3 | Under what initial conditions does oligopoly persist instead? | Open |
| 4 | What is the empirical signature of this in the Fermi paradox? | Open |
| 5 | What is the minimum capability differential required to trigger exclusion? | Open |

---

## Repository

| Path | Description |
|------|-------------|
| `theory/foundations.md` | Literature review and prior work with full citations |
| `theory/formal_claim.md` | Theorem statement and proof sketch |
| `theory/derivations.md` | Step-by-step mathematical derivations |
| `simulations/agents.py` | Core agent model |
| `simulations/competition.py` | Lotka-Volterra competition dynamics |
| `simulations/intelligence_explosion.py` | dS/dt = S^(1-β) dynamics |
| `simulations/run_experiments.py` | Experiment runner |
| `figures/` | Output plots |
| `findings.md` | Running log of confirmed results with parameter values |

---

## Run

```bash
python simulations/intelligence_explosion.py   # β sweep — growth regime analysis
python simulations/competition.py              # two-agent competitive exclusion
python simulations/agents.py                  # N-agent capability competition
python simulations/run_experiments.py         # full experiment suite
```

---

## 🛠️ Tools

- **Language:** Python 3 — numpy, matplotlib
- **AI assistance:** Claude (Anthropic) — theory development, derivations, simulation design. All AI use documented in findings log.

---

*Bostrom, N. (2005). What is a Singleton? Linguistic and Philosophical Investigations, 5(2).*  
*Omohundro, S. (2008). The Basic AI Drives. Proceedings of the 2008 Conference on Artificial General Intelligence.*  
*Yudkowsky, E. (2013). Intelligence Explosion Microeconomics. Machine Intelligence Research Institute.*  
*Hanson, R., Martin, D., McCarter, C., Paulson, J. (2021). If Loud Aliens Explain Human Earliness, Quiet Aliens Are Also Rare. arXiv:2102.01522.*
