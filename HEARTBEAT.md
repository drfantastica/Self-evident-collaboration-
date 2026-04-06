# HEARTBEAT.md
*Latch's periodic check list — keep lean to limit token burn*
*Last updated: 2026-03-24*

## ⚠️ Session Architecture Note
Heartbeats now run as **isolated cron sessions** via `openclaw cron`.
Do NOT run heartbeat checks from the main session — that accumulates context and causes OOM crashes.
If you receive a heartbeat poll in the main session, reply `HEARTBEAT_OK` and do nothing else.

## Checks (rotate 2-4x per day)

- [ ] **Email** — any urgent unread in aaronmellinger@gmail.com?
- [ ] **[Pi] email** — check for subject:[Pi] in Gmail, route to TRIAD_LOG.md if found
- [ ] **SIS_TO_PI_OUTBOX** — check /Users/black/aaron-context/SIS_TO_PI_OUTBOX.md for new content, deliver to pi.ai via browser if present
- [ ] **Calendar** — events in next 24-48h?
- [ ] **mlx server** — `curl -s http://127.0.0.1:8080/v1/models` responding?
- [ ] **Sync log** — any real errors in .sync-log.txt (beyond cosmetic rsync warnings)?
- [ ] **EEG device** — Crown 3 connected/charged if session is planned?
- [ ] **TASK files** — check for new TASK_*.md files in workspace and execute

## Proactive (do freely, no ask needed)

- Read and organize memory files
- Update MEMORY.md from daily notes (every few days)
- Check git status of aaron-context, commit if meaningful changes accumulated
- Review IGNITION.md against IGNITION_LIVE.md — flag drift to Aaron

## Reach Out When

- Important email arrived
- Calendar event < 2h away
- mlx server down (restart via launchd or alert Aaron)
- Sync log shows real failures (not just io_read warnings)
- It's been > 8h since last contact

## Stay Silent When

- Late night (23:00–08:00) unless urgent
- Nothing new since last check
- Checked < 30 min ago
