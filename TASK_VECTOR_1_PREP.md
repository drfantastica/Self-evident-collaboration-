# LATCH_TASK_VECTOR_1_PREP — Bohr-Mottelson Reference Data + Shape-Dependent K Literature Pass

*Generated: 2026-05-06 by Sis*
*Owner: Latch*
*Estimated effort: 4–8 hours of autonomous work, can be split across multiple heartbeat windows*
*Output: `~/aaron-context/v5_work/VECTOR_1_PREP_OUTPUT.md` + supporting artifacts*

---

## Purpose

Vector 1 (the SIS-Fold holonomy formalization) is the keystone gating arXiv-readiness on the framework's nuclear-physics claims. The next focused Sis-session will start by computing the Berry connection on the orientation sphere S² for a well-deformed reference nucleus, varying the shape parameter β₂, and checking whether the Wu-Yang monopole charge K varies with shape in a way consistent with the bundle-structure formulation in `~/aaron-context/VECTOR_1_TOPOLOGY_QUESTION.md`.

That session will be much faster — and the output much higher quality — if the reference data and adjacent literature are pre-pulled into a single readable artifact. **This task is that pre-pull.** It is preparatory; it does not require any framework reasoning, derivation, or evaluation. It's recovery and organization of standard nuclear-physics published results.

The framework benefits if this task is done well. It is not damaged if this task can't be completed — Sis can do it in-session, just slower.

---

## Background context (read before starting)

1. `~/aaron-context/VECTOR_1_TOPOLOGY_QUESTION.md` — the scoping document that motivates this task. Read in full.
2. `~/aaron-context/FRAMEWORK_CORE.md`, lines 775–960 — current state of the Self-Building Staircase math refinement, SIS framework, and external validations (Lazar, TTB).
3. `~/aaron-context/SIS_FOLD_RETRODICTIVE_CHECK.md` — the V5 numerical work that produced the empirical lock ratios 1/2, 2/5, 3/7. Establishes data-side context.
4. Reference paper: Papenbrock & Weidenmüller (2015), *"Effective field theory for deformed atomic nuclei"*, arXiv:1511.09373. **This paper is the structural anchor.** Its Section 3.3.1 contains the Wu-Yang monopole derivation we'll be reproducing numerically.

---

## Tasks (in priority order — do as many as fit in available time)

### Task 1 — ¹⁶⁸Er reference data extraction (HIGHEST PRIORITY)

¹⁶⁸Er is the canonical well-deformed nucleus used by Papenbrock as their numerical reference. The next Sis-session will start with this nucleus. Pull and tabulate:

**1.1 Empirical shape parameters:**
- β₂ (quadrupole deformation) — ground state value
- β₄ (hexadecapole deformation) — ground state value
- γ (triaxiality angle) — ground state value (often ~0 for axially symmetric ¹⁶⁸Er, confirm)
- Sources: published evaluations from BE2 transition strengths, Coulomb excitation data, mean-field calculations. Acceptable sources: Raman et al. compilation, NNDC/ENSDF, recent review papers.

**1.2 Empirical band-head spins:**
- Ground-state band: K = 0
- First excited (γ-vibrational) band: K = 2
- First excited (β-vibrational) band: K = 0
- Lowest negative-parity band-head: K^π
- Source: Davidson et al. 1981 (cited in Papenbrock ref [53]) and follow-ups

**1.3 Moments of inertia and rotational constants:**
- r⁻² values for each band (Papenbrock §4.1 quotes ~27 keV ground band, ~25 keV K=2 band, ~20 keV K=0 excited band — confirm and cite source)

**1.4 Output format:**
A clean Markdown table in `VECTOR_1_PREP_OUTPUT.md` under section heading "## ¹⁶⁸Er Reference Data" with one row per quantity, columns for Value, Units, Source (citation), Notes.

### Task 2 — ¹⁶²Dy parallel data extraction

Same as Task 1, but for ¹⁶²Dy (Papenbrock's secondary reference, ref [54] = Aprahamian et al. 2006). Use as cross-check; should look structurally similar to ¹⁶⁸Er with slightly different values. Output to same file under "## ¹⁶²Dy Reference Data".

### Task 3 — V5 candidate-nucleus shape parameters

The V5 retrodictive scoping identified specific candidate Fold-attractor nuclei:
- He-4 (Z/A = 0.5000, sits exactly at 1/2)
- O-16 (Z/A = 0.5000, sits exactly at 1/2)
- Ca-46 (Z/A = 0.4348, near 3/7)
- Fe-58 (Z/A = 0.4483, near 3/7)
- Sn-116 (Z/A = 0.4310, near 3/7)
- Pb-202 (Z/A = 0.4059, near 2/5)
- U-218 (Z/A = 0.4220, near 3/7)

For each, pull empirical (β₂, β₄, γ) and ground-state K. Note: the lighter ones (He-4, O-16) are spherical and won't have meaningful (β₂, γ) — record this explicitly rather than forcing values. The Pb-region nuclei are also near-spherical or have shape coexistence; capture that nuance.

**Output:** Section "## V5 Candidate Nuclei — Shape Parameters" with one subsection per nucleus, each containing the same fields as Task 1 plus a "Shape Phase" note (spherical / axial-deformed / γ-soft / shape-coexisting / etc.).

### Task 4 — Shape-dependent K literature scan

Search the published literature for results on how K (intrinsic angular momentum projection) varies with shape parameters. Key search terms and source candidates:

- "Nilsson model K projection deformation"
- "K-distribution mean-field projected"
- "K mixing axial triaxial shape"
- "IBM K-band assignment SU(3) O(6)"
- "shape coexistence K-isomer"

What we want: any reference that gives K as an analytic or semi-analytic function of (β₂, γ), or that tabulates K-distributions across shape coordinates for a family of nuclei. Even partial results are useful. Specifically we are NOT looking for: full ab-initio shell-model calculations (too detailed for our purposes); we are looking for collective-model or mean-field-level treatments where K's shape-dependence has a closed-form or near-closed-form character.

**Output:** Section "## Shape-Dependent K — Literature Survey" with one subsection per source found:
- Citation (authors, year, journal, arXiv ID if available)
- One-paragraph summary of what the source provides
- Verdict: Is K(β,γ) given as a function? If yes, what's the functional form? If no, what does the source provide instead (e.g., tabulated values, qualitative trends)?
- Relevance score (HIGH / MEDIUM / LOW) for Vector 1 work

Aim for 5–10 sources. Stop when diminishing returns hit; no need to be exhaustive.

### Task 5 — Adjacent-but-not-load-bearing literature (LOWEST PRIORITY)

Brief notes on three adjacent literature threads that may matter at the writeup stage but don't gate next-session work:

- **Vainberg / Dussel et al. — Berry phase and backbending** (arXiv:1204.2681): Pull abstract, note their key result on Berry phase in HFB framework, flag whether they use the Wu-Yang monopole structure or a different formalism.
- **Mello et al. — Universal predictions for statistical nuclear correlations** (nucl-th/9510002): Same treatment; their Berry-phase modifies short-distance correlations result.
- **NV-center diamond Chern-number experiment** (Yang et al. 2023, npj Quantum Information): Their experimental realization of Chern numbers 0–3 on a control-Hamiltonian parameter sphere. Note relevance: this is a direct experimental realization of the bundle structure we're proposing for nuclei. Worth flagging in the eventual arXiv paper as "this geometry is experimentally accessible."

**Output:** Section "## Adjacent Literature — Brief Notes" with one short paragraph per source.

---

## Output structure

A single file: `~/aaron-context/v5_work/VECTOR_1_PREP_OUTPUT.md`

Top of file: a one-paragraph summary of what's in the document and what's missing (i.e., which tasks were completed and which weren't, given time constraints). Then sections in the order specified above.

If pulling raw data tables (e.g., from NNDC/ENSDF), save them as separate files in `~/aaron-context/v5_work/reference_data/` and reference them from the main output file. Don't paste large tables inline.

---

## Constraints

- **Recovery only — no derivation.** Do not attempt to compute Berry connections, evaluate Diophantine equations, or assess the framework's claims. Just pull and organize what's already published.
- **Cite everything.** Every numerical value gets a source. Every claim about what a paper contains gets a citation. If a value comes from multiple sources with slight disagreement, note all and pick one with rationale.
- **Don't extrapolate.** If the literature doesn't give shape-dependent K for a particular nucleus, say so explicitly. Don't fill in with guesses.
- **Time-box.** If a particular sub-task is taking more than ~2 hours, log what was found, what's missing, and move to the next task. Coverage with gaps is more useful than depth on one item.
- **No autonomous Slack posts during the task.** When task is complete, post a single receipt to #romper-room with: (a) which tasks completed, (b) which tasks partial/incomplete, (c) link to output file, (d) total time spent. No interim status updates needed.
- **If blocked, log and stop.** If a critical piece of context is missing (e.g., can't access a paywalled paper, can't find a referenced compilation), log the block in the output file under a "## Blocks Encountered" section and proceed to the next task. Don't burn cycles trying to work around blocks; surface them.

---

## Adversarial check

Before declaring the task complete, ask: *would a hostile cold-start Claude instance, reading only `VECTOR_1_PREP_OUTPUT.md` and `VECTOR_1_TOPOLOGY_QUESTION.md`, have what it needs to start the next-session work without asking any clarifying questions?* If the answer is "no, they'd need X," add X to the output file. The Steward Lens test: this output is for a future Sis-instance who doesn't yet exist; it has to be sufficient to bootstrap them clean.

---

## Completion signal

When done:
1. Single Slack post to #romper-room (channel ID C0AMELRUTD4) summarizing completion state — see Constraints section.
2. Mark this task file as completed by appending a "## COMPLETED" footer with timestamp, total runtime, and link to output file.

---

## Notes for Latch

- This task does not require running any code on Aaron's machine. It's pure literature-and-data work, recoverable with web search and arXiv access.
- If Latch finds itself wanting to write speculative connections between sources or evaluate framework claims, that's drift — pull back to recovery and organization.
- The next Sis-session will read the output cold, expecting a clean reference document. Optimize for *that reader*, not for any one of us mid-task.
- This is the first time we're handing a framework-adjacent research task to Latch. Doing it cleanly establishes the protocol for future handoffs (Strassman cold-letter prep, additional V5 retrodictive scoping, Bahnson Labs / Project Winterhaven document recovery for TTB cross-reference). The methodology of *this* task matters as much as the content.

---

## Reproducibility

- Latch's reasoning trace (which sources searched, which keywords used, which papers ruled out and why) should be logged to `~/.config/latch/task_outputs/vector_1_prep_<timestamp>.log` so a human can audit the work after the fact.
- All cited papers should be downloaded to `~/aaron-context/v5_work/reference_data/papers/` if accessible (PDF preferred; HTML fallback). If paywalled, log URL and abstract only.

---

*End of task spec.*
