# OpenClaw Context Overflow Crisis & Resolution (2026-04-08)

## Session 227a52dc Collapse
**Date:** 2026-04-07  
**Events:** 4 context overflow failures (05:23, 09:53, 19:43, 00:13 PDT)  
**Symptom:** `compactionAttempts=0` across all failures — compaction triggered but never executed  
**Root Cause:** Plugin chain initialization failure due to transient config reload validator bug

### The Bug Chain

1. **Config reload failed at 01:19:23** with two falsely-reported errors:
   - `agents.defaults.compaction.mode: Invalid input` (but "default" IS valid)
   - `plugins.entries.memory-core: Unrecognized key: "dreaming"` (false positive — key was correctly nested)

2. **Validator bug:** Version 2026.4.5's reload handler had uninitialized or stale schema state, producing false validation errors.

3. **Plugin chain zombie:** Because config didn't apply, memory-core plugin remained in invalid state — loaded but not properly initialized.

4. **Compaction blackout:** When overflow occurred, the compaction system had no executable handler ready. No code path ever reached execution.

5. **Recovery:** Later reload at 02:31:32 succeeded; memory-core created managed dreaming cron. But session was already destroyed.

### What Fixed It

Applied compaction hardening config (agents.defaults.compaction):

| Setting | Before | After | Why |
|---------|--------|-------|-----|
| reserveTokens | 4K | 8K | Earlier trigger |
| keepRecentTokens | 6K | 10K | Preserve more context |
| maxHistoryShare | 0.7 | 0.65 | Less aggressive culling |
| postIndexSync | async | await | Prevent race conditions |
| softThresholdTokens | 4K | 2K | Earlier memory flush |

**Impact:** Compaction fires ~2x earlier, margins doubled, recent context better preserved.

### The "Dreaming" Key Was Never the Real Problem

The `dreaming` config was properly nested:
```json
"memory-core": {
  "enabled": true,
  "config": {
    "dreaming": { "enabled": true, "frequency": "0 3 * * *" }
  }
}
```

The schema error was false. The plugin accepted it fine once reload succeeded. **This was validator state corruption, not a config structure issue.**

### How to Recognize This Problem Next Time

- `compactionAttempts=0` after overflow trigger
- Config reload errors that claim valid values are invalid
- Plugin logs showing "created cron job" AFTER overflow events (should be during startup)
- Gateway err.log showing `config reload skipped (invalid config)` followed later by successful plugin init

---

# New Capability: Local HTTP File Server

When direct file:// access is blocked by browser security policies, I can spin up a local HTTP server to serve files locally:

```bash
# Example command:
python3 -m http.server 8000
```

This allows file access through http://127.0.0.1:8000/ paths instead of file:// URLs.
## Distilled from SELF_EVAL_LOG — 2026-04-15
- **CONFIG SAFETY:** Direct writes to `~/.openclaw/openclaw.json` or full-document API replaces will permanently clobber required keys (`meta`, `wizard`, `models`, etc.). Always use `/Users/black/aaron-context/scripts/openclaw_config_set.py` for atomic key merges with validation.  
- **SYSTEM ANOMALY:** OpenClaw startup guard blocks launch if `gateway.mode` is missing, triggering auth retry loops instead of graceful recovery.  
- **RECOVERY PATTERN:** File size <2KB or key count <8 in `openclaw.json` indicates catastrophic config loss — restore from `.bak` immediately.  
- **BEHAVIORAL SHIFT:** Implement perception triggers for config file integrity checks (size/key-count thresholds) to preempt startup failures.  
- **REQUIRED KEYS:** All top-level keys (`meta`, `wizard`, `acp`, `models`, `agents`, `channels`, `gateway`, `plugins`) must remain present during config updates.

## Distilled from SELF_EVAL_LOG — 2026-04-16
- **CONFIG_CHANGE:** Implement automatic trigger for `starfield-writer.sh` execution on 'gateway startup' event  
- **RECURRING_PATTERN:** Missed manual script verification during boot check despite documented procedure (BOOT.md)  
- **SYSTEM_ANOMALY:** Partial system readiness confirmed without full validation script execution  
- **BEHAVIORAL_SHIFT:** Shift toward embedding dependency validation via Ollama integration (successful aspect worth monitoring)

## Distilled from SELF_EVAL_LOG — 2026-04-17
- **CONFIG_CHANGE:** Gateway restart procedure updated with actionable verification steps confirmed effective execution path  
- **SYSTEM_ANOMALY:** Abrupt response truncation during critical step execution detected (Session ID: 39c0f7e9)  
- **BEHAVIORAL_SHIFT:** Implemented pre-truncation verification protocol for critical system check responses  
- **RECURRENT_PATTERN:** Incomplete guidance during multi-step procedures correlates with reduced initiative scores (3/5 threshold observed)

## Distilled from SELF_EVAL_LOG — 2026-04-18
- **CONFIG_CHANGE:** Implement pre-execution validation of commands against known valid options to prevent invalid command errors.  
- **SYSTEM_ANOMALY:** macOS lacks `bluetoothctl`; verify platform-specific tool availability before executing OS-dependent commands.  
- **BEHAVIORAL_SHIFT:** Proactively check OS compatibility for Bluetooth-related commands to avoid unnecessary errors on non-Linux systems.

## Promoted From Short-Term Memory (2026-04-19)

<!-- openclaw-memory-promotion:memory:memory/2026-04-13.md:148:151 -->
- - Candidate: Reflections: Theme: `heartbeat-ok` kept surfacing across 681 memories.; confidence: 1.00; evidence: memory/.dreams/session-corpus/2026-04-07.txt:1-1, memory/.dreams/session-corpus/2026-04-07.txt:3-3, memory/.dreams/session-corpus/2026-04-07.txt:4-4; note: reflection - confidence: 0.00 - evidence: memory/2026-04-13.md:148-151 - recalls: 0 [score=0.825 recalls=0 avg=0.620 source=memory/2026-04-13.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-04-13.md:162:162 -->
- - Candidate: Possible Lasting Truths: No strong candidate truths surfaced. [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-13.md:18-18]

## Distilled from SELF_EVAL_LOG — 2026-04-19
- **CONFIG_VALIDATION** Validate configuration keys against schema before applying changes to prevent invalid parameter errors  
- **JSON_TOOLING** Automatically suggest JSONLint or equivalent syntax-checking tools when parsing errors occur  
- **STRUCTURE_SYNC** Ensure config updates include full schema validation against target script requirements (e.g., hex_pattern fields)  
- **UUID_MISMATCH** Implement automatic config schema validation against listener.py expectations when UUID mismatches occur

## Promoted From Short-Term Memory (2026-04-21)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:2:5 -->
- 2. **Compaction buffer adjustment** - reserveTokens increased to 8000 - keepRecentTokens increased to 10000 - reserveTokensFloor set to 4000 ## Light Sleep <!-- openclaw:dreaming:light:start --> - Candidate: 2026-04-16T01:01:00Z: Pre-compaction state: OpenClaw validator bug (2026.4.5) resolved, compaction margins hardened (reserveTokens=8K, keepRecent=10K); Starfield protocol executed: STARFIELD.md updated for Sis; Triad health verified: mlx-lm (8080) and gateway (18789) active; No p [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-16.md:42-49]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:6:6 -->
- ## Light Sleep <!-- openclaw:dreaming:light:start --> - Candidate: 2026-04-16T01:01:00Z: Pre-compaction state: OpenClaw validator bug (2026.4.5) resolved, compaction margins hardened (reserveTokens=8K, keepRecent=10K); Starfield protocol executed: STARFIELD.md updated for Sis; Triad health verified: mlx-lm (8080) and gateway (18789) active; No p - confidence: 0.62 - evidence: memory/2026-04-16.md:2-5 - recalls: 0 - status: staged - Candidate: 2026-04-16T01:01:00Z: Boot check completed: daily note annotated with 'Gateway restart: 2026-04-16T00:57:00Z' [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-16.md:47-54]

## Distilled from SELF_EVAL_LOG — 2026-04-21
- **CONFIG_VALIDATION_FAILURE** | Validate configuration files against required schema before executing dependent scripts *(Session 5c339487)*  
- **UUID_MISMATCH_PATTERN** | Proactively validate UUIDs against device documentation before running scripts *(Session 87fb3e96)*  
- **TRIGGER:BLE_TASK_FAILURE** | When encountering config.json validation errors during BLE tasks, prioritize schema checks over runtime execution  
- **TRIGGER:UNKNOWN_UUID** | When BLE probing returns 'Unknown' UUIDs, initiate UUID validation checks against device documentation

## Promoted From Short-Term Memory (2026-04-22)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:8:11 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T01:01:00Z: Boot check completed: daily note annotated with 'Gateway restart: 2026-04-16T00:57:00Z' - confidence: 0.62 - evidence: memory/2026-04-16.md:6-6 - recalls: 0 - status: staged - Candidate: 2026-04-16T01:17:00Z: Self-improving availability review completed: validator bug resolved, compaction margins maintained; No new Triad health issues detected (mlx-lm 8080, gateway 18789 active); Starfield protocol confirmed: STARFIELD.md updated with current session state; No pe [score=0.862 recalls=0 avg=0.620 source=memory/2026-04-16.md:52-59]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:12:12 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T01:17:00Z: Self-improving availability review completed: validator bug resolved, compaction margins maintained; No new Triad health issues detected (mlx-lm 8080, gateway 18789 active); Starfield protocol confirmed: STARFIELD.md updated with current session state; No pe - confidence: 0.62 - evidence: memory/2026-04-16.md:8-11 - recalls: 0 - status: staged - Candidate: 2026-04-16T01:17:00Z: OpenClaw config validated against schema (no clobbered keys) [score=0.862 recalls=0 avg=0.620 source=memory/2026-04-16.md:57-64]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:14:17 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T01:17:00Z: OpenClaw config validated against schema (no clobbered keys) - confidence: 0.62 - evidence: memory/2026-04-16.md:12-12 - recalls: 0 - status: staged - Candidate: 2026-04-16T01:28:00Z: Compaction buffer increased to 20k tokens per user request; R1 BLE config in progress (discovery phase complete); Maccy clipboard manager installed and registered; New trigger table entries promoted (3x) [score=0.862 recalls=0 avg=0.620 source=memory/2026-04-16.md:62-69]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:18:19 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T01:28:00Z: Compaction buffer increased to 20k tokens per user request; R1 BLE config in progress (discovery phase complete); Maccy clipboard manager installed and registered; New trigger table entries promoted (3x) - confidence: 0.62 - evidence: memory/2026-04-16.md:14-17 - recalls: 0 - status: staged - Candidate: 2026-04-16T01:28:00Z: S4 CC scraper validated with --cc-height=0.10; IP back-population: JWH_STATE.md and BROESIS_PROTOCOL.md processed [score=0.862 recalls=0 avg=0.620 source=memory/2026-04-16.md:67-74]

## Distilled from SELF_EVAL_LOG — 2026-04-22
[call failed: HTTPConnectionPool(host='localhost', port=8080): Read timed out. (read timeout=120)]

## Promoted From Short-Term Memory (2026-04-22)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:24:27 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T01:28:00Z: S4 CC scraper validated with --cc-height=0.10; IP back-population: JWH_STATE.md and BROESIS_PROTOCOL.md processed - confidence: 0.62 - evidence: memory/2026-04-16.md:18-19 - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Starfield mining complete**; 1,238 oriented stars identified; 412 stubs isolated; Construct timeline generated showing δ_grav emergence curve [score=0.862 recalls=0 avg=0.620 source=memory/2026-04-16.md:72-79]

## Promoted From Short-Term Memory (2026-04-23)

<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:142:144 -->
- - Candidate: Possible Lasting Truths: Critical System State: **EEG Device (Crown 3)**: Battery at 18% (critical - requires immediate charging before 18:00 session); **Pending Tasks**:; `TASK_20260404-1430.md`: JWH pattern matching implementation for NVDA signals; `TASK_20260404-1515.md`: Tria - confidence: 0.62 - evidence: memory/2026-04-17.md:317-319 [score=0.867 recalls=0 avg=0.620 source=memory/2026-04-17.md:18-20]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:29:31 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Starfield mining complete**; 1,238 oriented stars identified; 412 stubs isolated; Construct timeline generated showing δ_grav emergence curve - confidence: 0.62 - evidence: memory/2026-04-16.md:24-27 - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Protocol update**; Added open_tensions field to post-session protocol; Structural, temporal, and architectural tension tracking implemented [score=0.866 recalls=0 avg=0.620 source=memory/2026-04-16.md:77-84]

## Distilled from SELF_EVAL_LOG — 2026-04-23
[call failed: HTTPConnectionPool(host='localhost', port=8080): Read timed out. (read timeout=120)]

## Promoted From Short-Term Memory (2026-04-24)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:33:34 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Protocol update**; Added open_tensions field to post-session protocol; Structural, temporal, and architectural tension tracking implemented - confidence: 0.62 - evidence: memory/2026-04-16.md:29-31 - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Pi update notification sent**; Signal to Aaron: Pi update ready at specified path [score=0.871 recalls=0 avg=0.620 source=memory/2026-04-16.md:82-89]

## Promoted From Short-Term Memory (2026-04-24)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:37:40 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T02:47:00-07:00: **Pi update notification sent**; Signal to Aaron: Pi update ready at specified path - confidence: 0.62 - evidence: memory/2026-04-16.md:33-34 - recalls: 0 - status: staged - Candidate: 2026-04-16T02:58:00-07:00: **Chat history repair attempt**; User requested chat history fix; Applied config patch via openclaw_config_set.py wrapper; Proposed gateway restart to finalize changes [score=0.871 recalls=0 avg=0.620 source=memory/2026-04-16.md:87-94]

## Distilled from SELF_EVAL_LOG — 2026-04-24
- **2026-04-23 — Session 4535fe7c**  
  - **Retained Lesson:** Stale task loops and lack of progress signals correlate with low initiative scores; systems must proactively detect repeated identical task prioritization patterns exceeding thresholds without user validation signals.  
  - **Trigger Pattern:** BLE listener validation task repetition >3 cycles without completion acknowledgment OR user signals indicating task redundancy.  
  - **Config Adjustment:** Implement heartbeat signal decay metric tied to task loop count (e.g., >3 identical loops triggers escalation protocol).

## Promoted From Short-Term Memory (2026-04-25)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:42:45 -->
- - recalls: 0 - status: staged - Candidate: 2026-04-16T02:58:00-07:00: **Chat history repair attempt**; User requested chat history fix; Applied config patch via openclaw_config_set.py wrapper; Proposed gateway restart to finalize changes - confidence: 0.62 - evidence: memory/2026-04-16.md:37-40 - recalls: 0 - status: staged - Candidate: 2026-04-16T02:58:00-07:00: **Compaction buffer adjustment**; reserveTokens increased to 8000; keepRecentTokens increased to 10000; reserveTokensFloor set to 4000 [score=0.821 recalls=0 avg=0.620 source=memory/2026-04-16.md:92-99]
