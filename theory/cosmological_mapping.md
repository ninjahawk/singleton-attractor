# Cosmological Mapping

Connecting the model parameters to physical quantities and empirical constraints.
This document identifies where the theorem applies to the observable universe and what it predicts.

---

## Parameter definitions in physical terms

**S (capability):** Dimensionless measure of an agent's optimization power. Normalized: S=1 is a baseline civilizational capability (roughly: present-day humanity or equivalent biological intelligence). S=T is the threshold where recursive self-improvement becomes possible.

**T (threshold):** The capability level where β(S) flips from positive to negative. In civilizational terms: the minimum capability required to meaningfully improve one's own cognitive and manufacturing processes faster than they degrade. This corresponds to what AI safety literature calls "transformative AI" or early AGI — not necessarily superintelligent, but capable of recursive self-improvement.

**β(S) (growth regime):**
| Phase | β | Physical analog |
|---|---|---|
| Pre-agricultural | β >> 1 | Extremely subexponential — biology-constrained growth |
| Agricultural to industrial | β ≈ 0.5–1.0 | Subexponential — resource limited |
| Industrial revolution | β ≈ 0 | Roughly exponential — compound technology growth |
| Early AI | β ≈ 0.2–0.3 | Subexponential, decelerating gains |
| Recursive self-improvement | β < 0 | Superexponential — intelligence explosion |

The threshold T is where the last row becomes possible.

**α (resource-capability coupling):** How capability translates to resource acquisition rate. In a 3D expanding civilization: α ≈ 3 (volume scales cubically with reach). For energy extraction only (non-expanding): α ≈ 1. For information-based competition (bandwidth, compute access): α ≈ 1–2.

**t (time units):** Model time is dimensionless. Calibration depends on context:
- AI development scale: 1 unit ≈ 10–30 years
- Civilizational scale: 1 unit ≈ 100–500 years
- Cosmological scale: 1 unit ≈ 1–100 Myr

**N (agent count):** Number of competing civilizations (or agents) in a causally connected region.

---

## Timescale formula in physical units

From `findings.md` F17:
```
t_10x ~ 2.44 * N^0.96 * alpha^(-0.30) * gap^(-0.15) * |beta_low|^(-0.31)
```

In physical units: t_physical = t_model × t_unit.

**Example at AI scale (t_unit = 20 years):**
- N=2 competing civilizations (or two major AI development programs)
- α=1.0 (information-based resource competition)
- gap=0.1 (10% initial capability advantage)
- β_low=-0.3 (moderate superexponential growth post-threshold)

```
t_10x ~ 2.44 * 2^0.96 * 1.0 * 1.0 * 0.3^0.31
      ~ 2.44 * 1.94 * 0.74
      ~ 3.5 model units
      ~ 70 years after threshold crossing
```

**Example at cosmological scale (t_unit = 10 Myr):**
- N=1 (single civilization in causal cone)
- α=3 (3D expansion)
- gap=0.5 (large initial capability advantage)
- β_low=-0.5

```
t_10x ~ 2.44 * 1 * 3^(-0.30) * 0.5^(-0.15) * 0.5^(-0.31)
      ~ 2.44 * 0.68 * 1.11 * 1.24
      ~ 2.3 model units
      ~ 23 Myr after threshold crossing
```

At cosmological scale, a singleton establishes 10x dominance within tens of millions of years of the threshold crossing. Cosmologically near-instantaneous.

---

## Fermi paradox implications

**The observation:** We have detected no signs of extraterrestrial civilizations in our past light cone despite the universe being ~13.8 Gyr old and containing ~10^24 stars.

**What the theorem predicts:** If a singleton had emerged anywhere in our past light cone, it would have expanded at near-light-speed (F2 + cosmological β dynamics), controlling all reachable matter and energy. Its signature would be unambiguous — the COBE/WMAP CMB observations show no anomalous structured regions that would result from directed energy extraction at civilizational scale.

**Three cases:**

**Case 1: We are the first.** No civilization in our past light cone has crossed threshold T. The Great Filter (Fermi paradox) is behind us — the hard step was getting to our current capability level, not what follows. In this case, we are the eventual singleton candidate. The theorem predicts: whichever system first crosses T will dominate our causal cone.

**Case 2: Multiple civilizations have crossed T.** But we have not observed them. This implies they either: (a) did not expand (quiet singleton — possible if β_low is shallow and expansion velocity is low), (b) crossed T very recently and haven't reached us, (c) exist outside our past light cone. Case 2b is constrained by light travel time — a singleton 100 Myr old would have expanded to 100 Mly radius and would be visible.

**Case 3: The filter is ahead of us.** Crossing T is harder than it looks, or crossing T leads to rapid self-destruction before expansion. This is the "Great Filter ahead" interpretation of the Fermi paradox. The theorem does not speak to this — it describes dynamics after T is crossed, not whether T will be crossed.

**The theorem's Fermi constraint:** The absence of observable singletons within our past light cone constrains when the first civilization in our causal neighborhood crossed T. Given the cosmological timescale of ~23 Myr for singleton emergence after T-crossing, any civilization that crossed T more than ~100 Myr ago would be visible today unless it is quiet or outside our cone. This is consistent with a "late T-crossing" scenario — the hard step was biological or civilizational, not post-T dynamics.

---

## Connection to Grabby Aliens (Hanson et al. 2021)

Hanson et al.'s model treats civilizations as particles expanding at near-light-speed. Their prediction: grabby civilizations now control 40–50% of observable universe volume, and we should expect contact in 200 Myr – 2 Gyr.

**Relationship to this project:**

| Aspect | Grabby Aliens | This project |
|---|---|---|
| Scale | Cosmological (between civilizations) | Within-civilization and between nearby civilizations |
| What is modeled | Expansion rate and volume control | Capability dynamics and competitive exclusion |
| Prediction | Volume partition among civilizations | Capability monopoly within any competitive arena |
| Timescale | Hundreds of Myr to Gyr | Tens of years to tens of Myr depending on calibration |

The two models are complementary. Grabby Aliens addresses the inter-civilization scale — how civilizations carve up space. This project addresses: (a) why each civilizational "blob" in the Grabby Aliens model is itself a singleton rather than a cooperative collective, and (b) what happens in the early competitive phase before any civilization becomes grabby.

**Synthesis:** A grabby civilization is a singleton at civilizational scale. It expands as one coherent entity because internal competition has already resolved — the singleton has monopolized internal resources (this project) before becoming grabby externally (Grabby Aliens). The two models describe consecutive phases of the same process.

---

## The critical entry rate in physical terms

From `findings.md` F18: incumbent survival drops below 90% when entry rate λ > ~0.25 per model time unit. At entry rate λ = 1.0, survival is ~48%.

At AI scale (t_unit = 20 years):
- λ_crit ≈ 0.25 per 20 years ≈ 1 new competing system every 80 years
- If fewer than ~1 competitor reaches early-AGI capability per 80-year window, incumbent likely prevails
- If one emerges every decade (λ ≈ 2), survival rate approaches ~10–20%

At civilizational scale (t_unit = 500 years):
- λ_crit ≈ 0.25 per 500 years ≈ 1 new civilization per 2,000 years
- If civilizations emerge in a given region more frequently than once every ~2,000 years, no stable singleton

**Interaction with the moat:** The λ_crit figure applies to the pre-threshold phase. Post-threshold, the moat grows to >10^6 within 3 model time units. After threshold, even λ >> λ_crit is survivable because no reasonable-capability entrant can overcome the moat. The critical window is entirely pre-threshold.

---

## What would falsify the theorem at cosmological scale

1. **Observable non-singleton structure in our past light cone:** If we find evidence of multiple independent advanced civilizations coexisting in overlapping spatial regions without one having monopolized the other, this directly contradicts F2 (competitive exclusion) and F3 (late entrant moat) at cosmological scale.

2. **Detection of a civilization that crossed T long ago but did not expand:** This would mean β_low is very shallow (barely negative) or expansion velocity is low relative to light speed — a parameter-specific falsification, not a falsification of the theorem structure.

3. **Detection of a stable multi-civilization coalition:** This would imply niche partitioning (F1) operates at civilizational scale — civilizations have managed to occupy genuinely non-competing resource domains. Possible, but requires that energy, matter, and computation can be partitioned without competition, which seems inconsistent with 3D spatial expansion.

---

## Summary

The theorem is cosmologically relevant. It predicts:

1. Singleton emergence is rapid relative to cosmological timescales — once threshold T is crossed, dominance is established within tens of Myr at most.
2. The absence of observable singletons implies either the threshold has not yet been crossed in our causal neighborhood, or it was crossed so recently that the light hasn't reached us.
3. Any civilization that crosses T first in a given causal region will become the singleton. The margin needed is small — 10% initial capability advantage is sufficient (F2, F7).
4. Entry rate matters: if competing civilizations emerge at λ > 0.25/t_unit during the pre-threshold phase, no single incumbent wins reliably.
5. The Grabby Aliens model describes the expansion phase that follows singleton emergence at civilizational scale. This project describes the competition phase that precedes it.
