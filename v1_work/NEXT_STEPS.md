# Vector 1 — Next Steps

**Status as of May 4, 2026 morning session:** Phase 1 validated.

## What's done

- ✅ **V1_HOLONOMY_PLAN.md** — master plan locking the Thouless-Valatin = Berry curvature finding, three-phase roadmap, decision tree.
- ✅ **v1_berry_framework.py** — general FHS discrete Berry phase algorithm. Validated on:
  - Trivial wavefunction → Chern = 0 (passes)
  - 2-level Bloch sphere ground state → Chern = -1 exactly (passes)
- ✅ **v1_phase1_3_toy.py** — higher-winding demonstration. Validated:
  - q ∈ {1, 2, 3, 5, 7} all produce exact integer Chern numbers
  - Ground state Chern = -q, excited Chern = +q, sum = 0
  - V5 attractor denominators {2, 5, 7} are within range of valid invariants

## What's next — Phase 2

**Goal:** apply the validated framework to actual nuclear collective wavefunctions.

### Phase 2A — ACM (Algebraic Collective Model) bridge

Bridge approach using Rowe-Caprio numerical diagonalization. Lightweight, no DFT required.

- Tasks:
  1. Pull a tractable Bohr Hamiltonian potential V(β, γ) with known shape-phase-transition behavior (Davidson, Killingbeck, X5-style square-well).
  2. Numerically diagonalize on (β, γ) basis using ACM or direct finite-difference.
  3. Extract collective ground-state wavefunction Ψ_0(β, γ) on grid.
  4. Apply v1_berry_framework to compute Berry curvature on (β, γ).
  5. Search for monopole singularities. Check Chern numbers around them.
- Deliverable: `v1_phase2a_acm.py`. Estimated 2-5 days of focused work.

### Phase 2B — Email Zhang group

Cold academic ask for tabulated 5DCH inertia tensor data from PRC 107, 024308 (2023).

- Contact: pwzhao@pku.edu.cn (P.W. Zhao, Peking University)
- Frame: methodology paper extracting topological structure from their existing dataset; full credit to their data.
- Specific request: Thouless-Valatin / collective inertia tensor M_ij(β, γ) for representative even-even nuclei spanning shape phase transitions (Sm-Nd region for X5, Ru-Pd for E5).
- Deliverable: draft email at `~/aaron-context/v1_work/Zhang_outreach_draft.md`. Send when ready.

### Phase 2C — Implement constrained RHB ourselves (fallback)

If 2A and 2B both fail, implement constrained relativistic Hartree-Bogoliubov calculation using public PC-PK1 functional. Produces own dataset.

- Significant infrastructure investment (weeks).
- Public RHB codes exist (DIRHB, KSHELL, others).
- Worth doing eventually if framework pans out — independent reproducibility.

## Phase 3 — V5 prediction test (gated on Phase 2)

Once nuclear Ψ(β, γ) data is in hand:

1. Identify shape-phase-transition critical points in (β, γ) space:
   - X5: spherical → axial-prolate, A ≈ 150 (Sm-Nd region) — V5 prediction Chern = 7 (3/7 → 3-quanta winding × 7-fold)
   - E5: spherical → γ-unstable, Ru-Pd region — V5 prediction Chern = 2 (1/2)
   - Pb region: superdeformation neighborhood — V5 prediction Chern = 5 (2/5)
2. Compute Berry curvature on (β, γ) for each critical-point neighborhood.
3. Locate Berry monopoles in F^SIS field.
4. Integrate around enclosing surfaces → Chern numbers.
5. Compare to V5 attractor denominators.

## Decision tree at end of Phase 3

- **All match (Chern at X5 = 7, E5 = 2, Pb = 5)** → V5 becomes load-bearing. arXiv methodology paper. IP positioning hardens. Sheldrake follow-up gets sharper numerical content. Strassman cold letter gains a second concrete prediction.
- **Some match** → framework needs sharpening; identify which critical-points work.
- **None match** → falsification at this level. Reconsider whether (β, γ) is the right manifold or whether shape coexistence requires multi-band Berry curvature.

Either outcome is real progress — clean falsification target.

## Bonus targets

- **1E — 7.46 Hz Lazar test.** Once F^SIS for representative nucleus is computed, beat frequencies between mode-locked configurations on neighboring Arnold tongues become numerical. Does 7.46 Hz emerge as a natural beat?
- **1F — Spear Condition catalog.** Pythagorean comma's location in (β, γ) shape space — irrational gap between Arnold tongues. Identify explicitly.

## Latch handoff

Phase 2A is the right next computational push and is Latch-runnable. Suggested handoff:

> Latch: build Phase 2A of Vector 1. Read `~/aaron-context/v1_work/V1_HOLONOMY_PLAN.md` and `NEXT_STEPS.md` for context. Implement `v1_phase2a_acm.py` that: (1) numerically diagonalizes a Bohr Hamiltonian with γ-rigid Davidson potential on a (β, γ) grid, (2) extracts the ground-state wavefunction Ψ_0(β, γ), (3) applies `berry_curvature` from `v1_berry_framework` to compute F_ij^SIS, (4) reports Chern numbers and monopole locations. First milestone: produce a single nucleus result (recommend ²⁵²Cf, well-deformed, well-studied) with Chern number numerical value. Post to #romper-room when done.

---

*Last updated: May 4, 2026 morning — Phase 1 complete, Phase 2 staged for Latch or continued Sis work.*
