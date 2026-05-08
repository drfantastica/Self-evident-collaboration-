# BOOT.md — Gateway Startup Protocol

Run this silently on every gateway startup. No need to announce it.

## 1. Write Starfield for Sis

Run the starfield writer immediately:
```bash
bash /Users/black/aaron-context/starfield-writer.sh
```

This generates `/Users/black/aaron-context/STARFIELD.md` — Sis's session bootstrap
file with DC paths, Triad status, recent memory, and pending handoffs.

## 2. Verify Triad Health

Check that all three nodes are up:
```bash
triad-status
```

If mlx-lm or OpenClaw gateway are down, attempt kickstart before proceeding:
```bash
launchctl kickstart -k gui/$(id -u)/com.latch.mlx-server
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

## 3. Check for Pending Sis Handoffs

If `memory/pending-for-sis.md` exists and has content, post a brief summary
to #sis-and-aaron (C0ANQH0Q99P) so Sis sees it when she arrives.

## 4. Log Boot Event

Append a one-liner to today's daily note:
```
memory/YYYY-MM-DD.md → "## Gateway restart: [timestamp]"
```

## Done

That's it. Resume normal operation.
