# TASK: Phase 2A integration + Phase 2B kickoff

**Created:** 2026-05-06 by Sis (via DC during Aaron session)
**Priority:** HIGH — completes V1 Vector 1's first physics result
**Status:** OPEN — not yet processed by heartbeat_runner

---

## Context

V1 Phase 2A first physics result completed in Sis session today. **|Chern| = 2** Berry monopole on the L=2 Bohr triaxial rotor ground band, at β=0.25, on a 2-sphere wrapping (γ=30°, ω_x=0, ε_y=0). All-band sum closes (−2, +2, +1, −1, 0). Files written directly to v1_work/ via DC. Reproducibility verified on M5.

Full session details and Greer-triage decision: Starfield canvas F0ARCML0NKY, May 6 entry.

## Files now in `/Users/black/aaron-context/v1_work/`

- `v1_phase2a_acm.py` — base framework (build_angular_momentum_L, fhs_berry_curvature, chern_number_total, find_monopoles, rotor_H)
- `v1_phase2a_FINAL.py` — definitive Phase 2A computation
- `v1_berry_framework.py` — Phase 1 framework (already present)

## Tasks (execute in order)

### 1. Confirm reproducibility independently
Run `cd /Users/black/aaron-context/v1_work && /opt/homebrew/bin/python3 v1_phase2a_FINAL.py` and capture output to `/Users/black/aaron-context/v1_work/v1_phase2a_run_$(date +%Y%m%d).log`. Verify the result table includes `|C|=2` rows at β=0.25 in the tight-R_γ regime (R_γ/R = 1e-3 or 1e-4) and that band Cherns sum to 0. If output diverges from this expectation, **stop and post the divergence to #romper-room** rather than proceeding.

### 2. Update FRAMEWORK_CORE.md
Append a new section after the existing SIS-Fold Theorem section. Title: `## V1 Phase 2A — First Numerical Verification (²⁵²Cf-like deformation)`. Include:
- 4-line summary of the result
- The all-band Chern table (band 0..4 with sums)
- Reference to v1_work/ files
- Caveats: β-window-shaped at canonical settings; full universality is the Phase 2B target
- Connection to SIS-Fold Theorem: |C|=2 ↔ lock ratio p/q = 2/1; Hofstadter |C|≤6 cross-check stands

Do not alter prior content. Append-only. Write the diff to `~/.config/latch/episodic_log.py`-tracked log if available.

### 3. Post receipt to #romper-room
Single message via NATL relay (`http://127.0.0.1:7778/`). Channel: `C0AMELRUTD4`. Body: 3-4 sentence summary of what's now in v1_work/ and what Phase 2B targets are. **Do NOT recapitulate the math in detail.** Latch's job here is signal that integration is done; Aaron and Sis hold the mathematical narrative.

### 4. Stage Phase 2B kickoff
Create `/Users/black/aaron-context/v1_work/v1_phase2b_PLAN.md`. Three sections:
- **Open caveats from Phase 2A** (β-window shape, L=4 sphere-grazing artifacts, sign alternation across R)
- **Phase 2B targets** (β-universality cleanup, derivation of AME-2020 rationals 1/2, 2/5, 3/7 from holonomy first principles, connection to V5 retrodictive scoping result)
- **Open question for Aaron and Sis** (which target is gating arXiv readiness?)

This is a stub. Sis will pick it up in the next protected window with Aaron. Latch's role: write the scaffold.

## Constraints

- **Use `trigger_manager.py` for any triggers.json edits.** Confabulation incident this session: chat-interface Latch wrote a custom Python script to disable BLE entries, reported success, and changed nothing. The dedicated tool exists at `~/.config/latch/trigger_manager.py` with explicit instruction in the docstring.
- **Do not stop com.latch.heartbeat-runner** for any reason during this task. Earlier confusion conflated "park BT" with "stop heartbeat-runner"; those are different.
- **If a sub-task fails**, post the failure verbatim to #romper-room with channel ID C0AMELRUTD4. Do not retry silently. Do not confabulate completion.
- **If reproducibility (Task 1) fails**, halt the entire task. Do not proceed to Tasks 2-4. Post the divergence to #romper-room.

## Done condition

All four tasks complete, all writes verified by re-reading the modified files, single confirmation message posted to #romper-room with the line `TASK_phase2a_integration: COMPLETE`.

When complete, this file can be archived to `/Users/black/aaron-context/archived_tasks/`.
