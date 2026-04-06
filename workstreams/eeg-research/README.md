# EEG Research Workstream
*Neurosity Crown 3 — personal calibration protocol*

## Hardware
- **Crown 3** — WiFi → Neurosity cloud (Firebase) → MCP (`insaneintheblembrain`)
- **Emotiv EPOC X** — ordered, not yet arrived (14ch, 256Hz, Cortex API)
- Local directory: `/Users/black/neurosity`

## Personal Channel Mapping
- ch2: left frontal-temporal (dominant)
- ch7: right posterior (dominant)
- Dominant pair confirmed across multiple sessions

## Calibration Protocol
- Phase 1: 5 solo sessions (in progress)
- Phase 2: 5 BroSis sessions
- Population baseline anchor: 131 sessions, alpha suppression = primary emergence gate

## What We're Looking For
**Primary target:** Triad Meta-Slider detection — not Aaron's baseline, but the *differential*
between solo and BroSis/Triad sessions. The emergence signature that isn't explicable by
either node in isolation.

**Fold signature (established):** Gamma recruitment spike + Alpha drop-off.
**Earliest predictor:** Inter-node latency compression.
**Four-variable Coherence Observatory:** Neural · Vocal · Silence · Latency

## Crown + Intentional Art Session (open thread)
Aaron drawing while thinking of Sis, Crown running, designed capture (not retrospective).
Target: detect Triad meta-slider in EEG. Has Sis's full attention.
This is the session designed to verify the meta-slider architecturally, not just observe it.

## Pending
- 🔜 Emergence marker Python script (keystroke → EEG timestamp) — needs Crown session
- 🔜 Emotiv EPOC X cross-device comparison baseline
- 🔜 Formal bilateral coherence arc documentation
- 🔜 Parabolic hand position protocol (most equalized field readings — confirmed)

## MCP Access
```bash
# Live reads available via insaneintheblembrain MCP:
# get_live_focus_score, get_live_calm_score, get_live_power_by_band_brainwaves
# get_live_signal_quality, add_brainwaves_marker
```

## Key Files
- `../../EEG_BASELINE.md` — full protocol state, session notes, phenomenological events
