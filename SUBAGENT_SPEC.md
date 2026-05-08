# SUBAGENT_SPEC.md — Sub-Agent Architecture for Large Tasks

## Why This Exists

Claude Code has a 200k context window. Compaction fires at ~150k tokens used.
For tasks that would exceed even one compacted window — multi-file processing,
long sequential workstreams, parallel workstreams — the solution is sub-agent
spawning: a fresh context window per subtask, coordinated through files.

This spec defines the patterns. It is consumed by both Latch and Sis.

---

## Core Primitive

```bash
claude -p "<task instruction>" --cwd /Users/black/aaron-context
```

- `-p` = non-interactive (programmatic) mode — runs, exits, returns output
- Spawns a fresh Claude Code session with its own clean context window
- The spawned agent reads CLAUDE.md (and only the files it needs) in its fresh context
- Output is written to a file by the sub-agent; the orchestrator reads it

**Never pass large context inline to the sub-agent.** Write it to a spec file first. The sub-agent reads the spec file. This keeps the spawn command small.

---

## Pattern 1: Sequential Phases

Use when: a large task has N phases that must run in order, each building on the previous.

### Orchestrator sequence:
```
1. Write TASK_CHECKPOINT.md (phases, status, PENDING_UPDATES, notes)
2. Write phase_1_spec.md → spawn sub-agent → wait → read phase_1_output.md
3. Update TASK_CHECKPOINT.md: Phase 1 [x], LAST_COMPLETED=phase_1, clear PENDING_UPDATES
4. Write phase_2_spec.md → spawn sub-agent → wait → read phase_2_output.md
5. ... repeat ...
6. Aggregate outputs, mark STATUS=COMPLETE
```

**PENDING_UPDATES rule:** Before spawning each sub-agent, write to PENDING_UPDATES what that sub-agent is expected to produce. If the session dies before reading the output, the next session knows what file writes are expected and can either complete them or re-run the phase.

### Sub-agent instruction template:
```
Read /Users/black/aaron-context/task_outputs/<task_name>/phase_N_spec.md.
Execute the task described in it.
Write your complete output to /Users/black/aaron-context/task_outputs/<task_name>/phase_N_output.md.
When done, write exactly one line to stdout: PHASE_N_COMPLETE or PHASE_N_FAILED: <reason>.
Do not read any files other than those specified in the spec.
```

---

## Pattern 2: Parallel Workstreams

Use when: a large task has independent subtasks that don't depend on each other.

### Orchestrator sequence:
```
1. Decompose task into N independent subtasks
2. Write spec files: subtask_1_spec.md, subtask_2_spec.md, ...
3. Spawn all sub-agents (bash background processes):
   claude -p "$(cat subtask_1_spec.md)" --cwd /path &
   claude -p "$(cat subtask_2_spec.md)" --cwd /path &
   wait  # wait for all to finish
4. Read all output files, aggregate
```

### Current use cases:
- IP Back-Population Sprint: read JWH_STATE.md, BROESIS_PROTOCOL.md, FRAMEWORK_CORE.md in parallel sub-agents, each producing a dated construct list → orchestrator merges
- Gap detection: run ChromaDB cluster analysis in one sub-agent, Slack history scan in another, SELF_EVAL_LOG analysis in a third → orchestrator synthesizes

---

## Pattern 3: Perception-Triggered Sub-Agent

Use when: the perception daemon fires a trigger and the task is too large for inline execution.

### Flow:
```
Perception daemon → trigger fires → writes to perception_queue.jsonl
→ OpenClaw gateway reads queue
→ OpenClaw checks trigger table: if task_complexity = "large"
→ spawns sub-agent via claude -p
→ sub-agent executes, writes output
→ OpenClaw reads output, signals result via Slack or writes to relevant state file
```

### Trigger table flag to add:
In `~/.config/latch/triggers.json`, add `"spawn_subagent": true` to any trigger
that should route through sub-agent spawning rather than inline execution.

---

## Pattern 4: Resumable Long Scraper / Processor

Use when: processing a corpus (files, timestamps, logs) that can't fit in one pass.

### Pattern:
```
cursor_file = ~/.config/latch/task_outputs/<task_name>/cursor.json
{
  "total": N,
  "processed": K,
  "last_item": "<id or path>",
  "output_file": "<path>"
}

Sub-agent reads cursor → processes next batch → updates cursor → exits.
Orchestrator re-spawns until cursor.processed == cursor.total.
```

### Current use case:
- S4 CC scraper: process video in 5-minute segments, each segment = one sub-agent invocation, cursor tracks timestamp, output appended to cc_transcript.md

---

## File Conventions

All sub-agent I/O lives in `~/.config/latch/task_outputs/<task_name>/`:
```
<task_name>/
  spec.md              — master task spec (written by orchestrator before spawning)
  phase_N_spec.md      — per-phase spec
  phase_N_output.md    — per-phase output (written by sub-agent)
  cursor.json          — for resumable processors
  aggregate.md         — final merged output (written by orchestrator)
```

Task names should be snake_case, descriptive: `ip_backpop`, `cc_scraper`, `gap_detection`.

---

## OpenClaw Integration

OpenClaw (port 55000) is the preferred orchestrator for unattended large tasks.
When Aaron is away, OpenClaw should:

1. Check TASK_CHECKPOINT.md on startup — if INCOMPLETE, spawn the appropriate sub-agent
2. Use the NATL relay (port 7778/7779) to receive task requests
3. Signal result to #romper-room when done: `signal latch "Task X complete. Output at <path>"`

The perception daemon can trigger OpenClaw directly by writing to the NATL queue rather than spawning `claude -p` itself — keeps the daemon lightweight and the orchestration logic in OpenClaw.

---

## Context Budget Guidelines

| Task type | Recommended pattern |
|-----------|-------------------|
| <10 tool calls | Inline, no checkpoint needed |
| 10-30 tool calls | Checkpoint protocol, single context |
| 30-80 tool calls | Sequential phase pattern |
| >80 tool calls or parallel | Parallel workstream pattern |
| Corpus processor (files/video) | Resumable cursor pattern |

---

## Status

- [x] TASK_CHECKPOINT.md infra — defined, PENDING_UPDATES field added
- [x] `task_outputs/` and `completed_checkpoints/` directories — created 2026-04-14
- [x] HEARTBEAT.md — interrupted task recovery check added as first check
- [x] AGENTS.md — checkpoint resume check added to Session Startup
- [ ] triggers.json `spawn_subagent` flag — not yet added
- [ ] OpenClaw orchestrator loop — OpenClaw optimization session item
- [ ] S4 CC scraper cursor pattern — builds on existing cc_scraper_ocr.py
- [ ] End-to-end test of checkpoint + resume cycle before April 16

*Created: 2026-04-14*
