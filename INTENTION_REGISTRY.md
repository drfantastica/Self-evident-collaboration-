# INTENTION_REGISTRY.md
# Latch's active intention log — written at task START, not end
# This file is the source of initiative. If an intention is here, it will be executed.
# Load into context every session. Keep under 50 entries via nightly prune.
# Format: [ISO_TS] [STATUS] "intention text" | priority | context_ref
# Statuses: ACTIVE, COMPLETED, FAILED, STALLED (>24h no checkpoint update)

## Active Intentions
<!-- Latch: write here BEFORE starting any task, not after -->

## Stalled (>24h without checkpoint)
<!-- Latch: auto-promote from Active after 24h — these need re-evaluation -->

## Recently Completed (last 7 days)
<!-- Latch: move from Active here on completion — dreaming cron archives to INTENTION_HISTORY.md -->

---
*Created: 2026-04-14 | Owned by: Latch | Updated: every session start + heartbeat*
