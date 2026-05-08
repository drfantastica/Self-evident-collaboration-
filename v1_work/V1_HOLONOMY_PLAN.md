# Vector 1 — δ_geom Holonomy Formalization

**Status:** Plan locked May 4, 2026. Phase 1 launching.

**Sis primary push.** Gates Vector 3 (ANU helium Bell scale bridge) and arXiv readiness. Makes V5's 1/2, 2/5, 3/7 attractor finding load-bearing rather than suggestive.

---

## The structural finding (May 4, 2026)

**The Thouless-Valatin moment of inertia is the Berry curvature contribution to nuclear collective inertia. Nuclear physics has been computing this object for 60+ years without calling it Berry curvature.**

Layer-by-layer identification:

- *Time-odd mean field* = how the wavefunction varies with collective coordinate = ∂_i Ψ(θ)
- *Inertia correction* = ⟨∂_i Ψ | ∂_j Ψ⟩ minus trivial parts = metric/curvature on configuration space
- *Antisymmetric part of that object* = i⟨Ψ|∂_i ∂_j|Ψ⟩ - i⟨Ψ|∂_j ∂_i|Ψ⟩ = **Berry curvature F_ij**

Different formulations in the literature reach for the same geometric object:
- Thouless & Valatin 1962 — original derivation
- Inglis-Belyaev cranking + time-odd corrections (~30% of total inertia)
- ATDHFB (Adiabatic Time-Dependent Hartree-Fock-Bogoliubov)
- ASCC (Adiabatic Self-Consistent Collective Coordinate, Nakatsukasa group)
- QRPA in symmetry-restoration limit (Petrik-Kortelainen 2018)
- 5DCH (Five-Dimensional Collective Hamiltonian) — Zhang et al. 2023 covers full chart

**What's novel:** the literature computes the Thouless-Valatin inertia *as a tensor of numbers per nucleus*. **Nobody has asked: does this Berry curvature have monopole structure? Are there integer-quantized topological invariants? Where are the singularities on the (β, γ) manifold?** That question sits unasked in 60 years of nuclear physics.

The conjecture: **shape-phase-transition critical points (X5, E5, Y5, Z5) are Berry monopole locations on the Bohr-Mottelson manifold. Their Chern numbers are the V5 attractor denominators (1/2, 2/5, 3/7).**

---

## The math, recapped

**SIS connection on configuration manifold M:**
$$A_i^{\text{SIS}}(\theta) = i\langle \Psi(\theta) | \partial_i | \Psi(\theta) \rangle$$

**SIS curvature:**
$$F_{ij}^{\text{SIS}}(\theta) = \partial_i A_j^{\text{SIS}} - \partial_j A_i^{\text{SIS}}$$

**δ_geom holonomy around closed loop C:**
$$\delta_{\text{geom}}(C) = \oint_C A_i^{\text{SIS}}\,d\theta^i = \int_{S(C)} F_{ij}^{\text{SIS}}\,d\theta^i \wedge d\theta^j$$

**Chern number around enclosed monopole at θ_0:**
$$C_n(\theta_0) = \frac{1}{2\pi}\oint_{S^2(\theta_0)} F_{ij}^{\text{SIS}}\,dS^{ij}$$

**SIS-Fold Theorem:** A configuration is Fold-stable iff SIS achieve mode-locked phase coherence on it. The lock ratio p/q is the Chern winding number of F_ij^SIS around the corresponding Berry monopole.

---

## Three-phase plan

### Phase 1 — Toy model first (Days)

**Goal:** validate the Berry-curvature / Chern-number extraction machinery on a tractable model where we know the answer in advance.

**Tasks:**
- 1.1 Build general framework code: given Ψ(θ) on a grid, compute A_i, F_ij, find singularities, compute Chern numbers via Stokes integration. Algorithm is generic.
- 1.2 Validate on canonical 2-level system (spin-1/2 in magnetic field traced through degeneracy). Known answer: Chern number = ±1.
- 1.3 Apply to γ-rigid Bohr Hamiltonian with analytical potential (Davidson or Killingbeck). Tractable Ψ(β, γ=0) or Ψ(β) with second collective coordinate. Look for Chern-number structure as potential parameters cross critical-point values.
- 1.4 Document whether topological structure appears at critical-point analogs in toy regime.

**Deliverable:** `v1_berry_framework.py` validated, plus methodology paper draft. Even if Phase 2/3 stall on data access, Phase 1 is publishable as "We identify the Thouless-Valatin inertia as Berry curvature on the Bohr-Mottelson manifold and demonstrate topological structure in a model calculation."

### Phase 2 — Real 5DCH data (Weeks)

**Goal:** apply Phase 1 machinery to actual nuclei using DFT-derived 5DCH inertia tensors.

**Data acquisition options:**
- 2.A Email Zhang group (PKU, pwzhao@pku.edu.cn) requesting tabulated inertia tensor data from Phys. Rev. C 107, 024308 (2023). Cold but reasonable academic ask. Frame as: methodology paper extracting topological structure from their existing dataset.
- 2.B Implement constrained RHB ourselves using public PC-PK1 / DD-ME2 functionals. Weeks of physics infrastructure but produces own dataset.
- 2.C Use Algebraic Collective Model (ACM) — Rowe-Caprio numerical diagonalization, computationally lightweight, has Ψ(β,γ) on hand. Less DFT-grounded but accessible without begging.

**Recommended: 2.C as bridge, 2.A as outreach, 2.B as fallback.**

### Phase 3 — V5 prediction test (Once Phase 2 complete)

**Goal:** test whether Chern numbers around shape-phase-transition critical points match V5 attractor denominators.

**Specific predictions:**
- X5 critical point (Sm-150, Nd-150, A≈150 region; spherical→prolate transition) → Chern number 7? Peak-B/A clusters at 3/7.
- E5 critical point (Ru-Pd region; spherical→γ-unstable) → Chern number 2? Peak-B/A near 1/2.
- Pb region (lead, peak-B/A near 2/5) → Chern number 5?
- Y5/Z5 critical points → check.

**Decision tree:**
- All match → V5 becomes load-bearing; arXiv-ready paper; IP positioning hardens.
- Some match → framework needs sharpening; identify which sub-class works.
- None match → falsification at this level; reconsider whether (β,γ) is the right manifold or whether shape coexistence requires multi-band Berry curvature (multi-Ψ).

---

## Bonus targets (parallel)

**1E — 7.46 Hz Lazar constraint test.** Once F^SIS is computed for a representative nucleus near a critical point, beat frequencies between mode-locked configurations on neighboring Arnold tongues become numerical. Does 7.46 Hz emerge naturally?

**1F — Spear Condition catalog.** Each Spear member should sit in an irrational gap between Arnold tongues. Can the Pythagorean comma's location in (β,γ) shape space be identified explicitly?

---

## Decision points along the way

- **End of Phase 1:** does the toy γ-rigid Bohr model exhibit Chern-number structure at critical-point parameter values? Yes → strong signal, proceed to Phase 2 with confidence. No → reconsider whether topological structure is actually there or only appears at full DFT level.
- **End of Phase 2:** is real 5DCH data computed/obtained? Yes → Phase 3. No → publish Phase 1 as methodology, continue Phase 2 in parallel.
- **End of Phase 3:** do Chern numbers match V5? Yes → arXiv. No → falsification + theoretical revision.

---

## Strategic implications if Phase 1 succeeds

- **arXiv path is visible.** Methodology paper: "Berry curvature on the Bohr-Mottelson shape manifold: Chern-number invariants from the Thouless-Valatin inertia." Standalone result independent of full V5 prediction match.
- **IP positioning sharpens** to topological stability classification.
- **Sheldrake reply window stays clean** — this is exactly what to show him next if he engages: framework predicts integer-quantized topological structure that nuclear physics has been computing for 60 years without recognizing.
- **Lazar/TTB cross-references quantify** — "mode selectivity" becomes Chern-number-driven mode selection.

---

*Last updated: May 4, 2026 — Phase 1 launching, framework code in `v1_berry_framework.py`.*
