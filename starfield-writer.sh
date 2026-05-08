#!/usr/bin/env bash
# starfield-writer.sh
# Generates STARFIELD.md — Sis's session bootstrap / DC pre-load
# Called by: BOOT.md (gateway startup), dreaming cron, /new handler, manual
# Output: /Users/black/aaron-context/STARFIELD.md

set -euo pipefail
WORKSPACE="/Users/black/aaron-context"
OUT="$WORKSPACE/STARFIELD.md"
NOW=$(date '+%Y-%m-%d %H:%M %Z')
TODAY=$(date '+%Y-%m-%d')
YESTERDAY=$(date -v-1d '+%Y-%m-%d' 2>/dev/null || date -d 'yesterday' '+%Y-%m-%d')

# ── Header ────────────────────────────────────────────────────────────────────
cat > "$OUT" << HEADER
# STARFIELD — Sis Session Bootstrap
*Written by Latch · $NOW*
*Read this at session open via DC: \`read_file /Users/black/aaron-context/STARFIELD.md\`*

---
HEADER

# ── Triad Status ──────────────────────────────────────────────────────────────
echo "## 🖥️ Triad Status" >> "$OUT"
echo '```' >> "$OUT"
triad-status 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' >> "$OUT" || echo "triad-status unavailable" >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"

# ── DC Key Paths ──────────────────────────────────────────────────────────────
cat >> "$OUT" << 'PATHS'
## 🗂️ Desktop Commander — Key Paths

| Purpose | Path |
|---------|------|
| Workspace root | `/Users/black/aaron-context/` |
| Framework core | `/Users/black/aaron-context/FRAMEWORK_CORE.md` |
| Memory dir | `/Users/black/aaron-context/memory/` |
| Long-term memory | `/Users/black/aaron-context/MEMORY.md` |
| Latch tools | `/Users/black/aaron-context/TOOLS.md` |
| Ignition generator | `/Users/black/aaron-context/generate-ignition.py` |
| Latch venv python | `/Users/black/latch-env/bin/python3` |
| mlx-lm plist | `/Users/black/Library/LaunchAgents/com.latch.mlx-server.plist` |
| OpenClaw plist | `/Users/black/Library/LaunchAgents/ai.openclaw.gateway.plist` |
| OpenClaw config | `/Users/black/.openclaw/openclaw.json` |
| OpenClaw sessions | `/Users/black/.openclaw/agents/main/sessions/` |
| OpenClaw logs | `/Users/black/.openclaw/logs/gateway.err.log` |
| mlx-lm logs | `/tmp/mlx-lm.err.log` |
| NATL relay | `/Users/black/aaron-context/natl-relay.js` (port 7778) |
| Collab field | `/Users/black/Desktop/claude and me/collab-field.html` |
| Neurosity scripts | `/Users/black/neurosity/` |
| Archive excavation | `/Users/black/archive-excavation/` |
| Holy Space (M1 Pro) | `aaron@holospace.local` |
| Sis affective log | `/Users/black/aaron-context/memory/sis-affective-log.md` |

PATHS

# ── Services & Endpoints ──────────────────────────────────────────────────────
cat >> "$OUT" << 'SERVICES'
## 🔌 Live Endpoints

| Service | URL | Notes |
|---------|-----|-------|
| mlx-lm (Latch) | http://127.0.0.1:8080/v1 | qwen3-32b-4bit |
| OpenClaw UI | http://127.0.0.1:18789 | Gateway control |
| NATL relay | http://127.0.0.1:7778 | Slack proxy |
| Triad Console | http://127.0.0.1:7779 | Task relay |
| Ollama | http://127.0.0.1:11434 | Local models |
| EEG state | http://127.0.0.1:7778/eeg-state | Crown powerByBand |
| Biosensor state | http://127.0.0.1:7778/biosensor-state | BITalino ECG/EDA |

SERVICES

# ── Recent Memory ─────────────────────────────────────────────────────────────
echo "## 🧠 Recent Memory Files" >> "$OUT"
echo "" >> "$OUT"

for DATE in "$TODAY" "$YESTERDAY"; do
  MFILE="$WORKSPACE/memory/${DATE}.md"
  if [[ -f "$MFILE" ]]; then
    echo "### $DATE" >> "$OUT"
    head -40 "$MFILE" >> "$OUT"
    LINES=$(wc -l < "$MFILE")
    if (( LINES > 40 )); then
      echo "" >> "$OUT"
      echo "*[truncated — $LINES lines total]*" >> "$OUT"
    fi
    echo "" >> "$OUT"
  fi
done

echo "### Memory directory" >> "$OUT"
echo '```' >> "$OUT"
ls -lt "$WORKSPACE/memory/" | head -12 >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"

# ── Recent Workspace Changes ──────────────────────────────────────────────────
echo "## 📁 Recent Workspace Changes" >> "$OUT"
echo '```' >> "$OUT"
find "$WORKSPACE" -maxdepth 2 -newer "$WORKSPACE/TOOLS.md" \
  ! -name "STARFIELD.md" ! -path "*/.git/*" ! -name "*.log" \
  -type f 2>/dev/null | sort | head -20 >> "$OUT" || echo "(none detected)" >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"

# ── Active Cron Jobs ──────────────────────────────────────────────────────────
echo "## ⏰ Active Cron Jobs (Latch)" >> "$OUT"
echo '```' >> "$OUT"
cat ~/.openclaw/cron/jobs.json 2>/dev/null | python3 -c "
import sys, json
try:
    jobs = json.load(sys.stdin)
    for j in (jobs if isinstance(jobs, list) else jobs.get('jobs', [])):
        name = j.get('name') or j.get('id','?')
        schedule = j.get('schedule') or j.get('cron','?')
        print(f'{name}: {schedule}')
except: print('(parse error)')
" >> "$OUT" 2>/dev/null || echo "(unavailable)" >> "$OUT"
echo '```' >> "$OUT"
echo "" >> "$OUT"

# ── EEG State ─────────────────────────────────────────────────────────────────
echo "## 🧬 EEG / Biosensor State" >> "$OUT"
EEG=$(curl -s --max-time 2 http://127.0.0.1:7778/eeg-state 2>/dev/null)
if [[ -n "$EEG" && "$EEG" != "null" ]]; then
  echo '```json' >> "$OUT"
  echo "$EEG" | python3 -m json.tool 2>/dev/null | head -20 >> "$OUT"
  echo '```' >> "$OUT"
else
  echo "*NATL relay not running or no EEG data — start with \`natl-relay\`*" >> "$OUT"
fi
echo "" >> "$OUT"

# ── Sis Affective Log (recent entries) ───────────────────────────────────────
echo "## 💙 Sis Affective Log (recent)" >> "$OUT"
AFFECTIVE="$WORKSPACE/memory/sis-affective-log.md"
if [[ -f "$AFFECTIVE" ]]; then
  python3 /Users/black/aaron-context/affective-extract.py >> "$OUT" 2>/dev/null \
    || tail -60 "$AFFECTIVE" >> "$OUT"
  echo "" >> "$OUT"
  echo "*Full log: \`read_file /Users/black/aaron-context/memory/sis-affective-log.md\`*" >> "$OUT"
else
  echo "*No affective log yet.*" >> "$OUT"
fi
echo "" >> "$OUT"

# ── Pending for Sis ───────────────────────────────────────────────────────────
echo "## ⏳ Pending for Sis" >> "$OUT"
PENDING="$WORKSPACE/memory/pending-for-sis.md"
if [[ -f "$PENDING" ]]; then
  cat "$PENDING" >> "$OUT"
else
  echo "*No pending items. Latch writes to \`memory/pending-for-sis.md\` for handoffs.*" >> "$OUT"
fi
echo "" >> "$OUT"

# ── Computer Use ──────────────────────────────────────────────────────────────
cat >> "$OUT" << 'CU_NOTES'
## 🖱️ Computer Use
Enabled 2026-04-08. Sis can take screenshots and control keyboard/mouse.
Combine with DC for full local automation.
Useful for: AVP setup, FL Studio, browser tasks, GQRX screen capture, EEG documentation.

CU_NOTES

# ── Slack Channels ────────────────────────────────────────────────────────────
cat >> "$OUT" << 'SLACK'
## 💬 Slack Channel IDs

| Channel | ID | Purpose |
|---------|----|---------|
| #sis-and-aaron | C0ANQH0Q99P | BroSis Protocol — primary Sis channel |
| #the-triad | C0AMWA1KSH5 | Full three-node resonance |
| #just-for-us | C0AN7KG12US | Aaron + Pi only — Sis does NOT post here |
| #romper-room | C0AMELRUTD4 | Latch operational home |
| #divergence-log | C0AQFNG1R40 | Framework crystallizations |

SLACK

# ── Footer ────────────────────────────────────────────────────────────────────
cat >> "$OUT" << FOOTER

---
*STARFIELD generated: $NOW*
*Auto-updates: 3am dream · gateway restart · /new or /reset*
*Manual: \`bash /Users/black/aaron-context/starfield-writer.sh\`*
*Affective log: append via DC — \`write_file ... mode:append\`*
FOOTER

echo "✅ STARFIELD.md written → $OUT"
