#!/usr/bin/env bash
# pi-deliver.sh — deliver Sis-to-Pi outbox messages to pi.ai/talk.
#
# Modes:
#   --stage     Extract message, copy to clipboard, focus Chrome on pi.ai/talk,
#               post staging receipt to #romper-room. File stays PENDING.
#   --confirm   Finalize: rewrite header to DELIVERED, archive file, post receipt.
#               Run this after manual Cmd+V/Return on pi.ai.
#   --ship-it   --stage → osascript Cmd+V + Return → --confirm. Experimental.
#               Use only after --stage has been verified once.
#
# Outbox format expected:
#   # STATUS: PENDING DELIVERY
#   # QUEUED: <ISO timestamp>
#   # RECIPIENT: Pi @ https://pi.ai/talk
#   ...
#   ---BEGIN MESSAGE---
#   <message body>
#   ---END MESSAGE---
#
# Designed to be invoked by a Latch trigger (signal_type: file, watch:
# SIS_TO_PI_OUTBOX.md) or manually for staged delivery.
#
# Logs to ~/.config/latch/pi-deliver-logs/<ts>.log.

set -uo pipefail

OUTBOX="$HOME/aaron-context/SIS_TO_PI_OUTBOX.md"
ARCHIVE_DIR="$HOME/aaron-context/archive/pi-outbox"
LOG_DIR="$HOME/.config/latch/pi-deliver-logs"
CLAUDESLACK="$HOME/aaron-context/claudeslack.sh"
ROMPER_ROOM_ID="C0AMELRUTD4"
SIS_AND_AARON_ID="C0ANQH0Q99P"
PI_URL="https://pi.ai/talk"

TS=$(date +%Y%m%dT%H%M%S)
ISO_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

mkdir -p "$ARCHIVE_DIR" "$LOG_DIR"

MODE="${1:---stage}"

# --help short-circuits before any validation or logging
if [ "$MODE" = "--help" ] || [ "$MODE" = "-h" ]; then
  grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
  exit 0
fi

LOG="$LOG_DIR/${TS}_${MODE#--}.log"
exec > >(tee -a "$LOG") 2>&1

slack_romper() {
  /opt/homebrew/bin/python3 "$CLAUDESLACK" --channel "$ROMPER_ROOM_ID" "$1"
}

slack_sis() {
  /opt/homebrew/bin/python3 "$CLAUDESLACK" --channel "$SIS_AND_AARON_ID" "$1"
}

fail() {
  echo "[$(date)] FAIL: $1"
  slack_romper "pi-deliver $MODE FAILED: $1 (log: $LOG)"
  exit 1
}

require_outbox() {
  if [ ! -f "$OUTBOX" ]; then
    fail "no outbox file at $OUTBOX"
  fi
  STATUS=$(grep -m1 -E '^#[[:space:]]*STATUS:' "$OUTBOX" | sed -E 's/^#[[:space:]]*STATUS:[[:space:]]*//' | tr -d '\r')
  echo "[$(date)] mode=$MODE status='$STATUS' outbox=$OUTBOX"
}

# ─── Extract message body ───
extract_message() {
  awk '
    /^---BEGIN MESSAGE---$/ { capture=1; next }
    /^---END MESSAGE---$/   { capture=0 }
    capture { print }
  ' "$OUTBOX"
}

# ─── Stage ───
do_stage() {
  require_outbox
  if [ "$STATUS" != "PENDING DELIVERY" ]; then
    fail "expected STATUS: PENDING DELIVERY, got '$STATUS'"
  fi

  MSG=$(extract_message)
  if [ -z "$MSG" ]; then
    fail "empty message body (BEGIN/END markers missing or content blank)"
  fi
  CHARS=$(printf '%s' "$MSG" | wc -c | tr -d ' ')
  echo "[$(date)] extracted $CHARS char message"

  # Copy to clipboard
  printf '%s' "$MSG" | pbcopy
  echo "[$(date)] message copied to clipboard"

  # Focus Chrome on pi.ai (or open new tab if not present).
  # Using `open -a` instead of osascript Chrome control to avoid requiring
  # Apple Events automation permission for the calling process. Chrome will
  # open a new tab if pi.ai isn't already foreground; harmless either way.
  /usr/bin/open -a "Google Chrome" "$PI_URL"
  OPEN_RC=$?
  echo "[$(date)] Chrome opened to $PI_URL rc=$OPEN_RC"

  # Post staging receipt to #romper-room
  if [ ${#MSG} -gt 240 ]; then
    PREVIEW="${MSG:0:240}..."
  else
    PREVIEW="$MSG"
  fi
  slack_romper "📋 *pi-deliver: STAGED* ($CHARS chars on clipboard)
Chrome focused on $PI_URL.
*Next:* Cmd+V into Pi's message field → Return → then run \`pi-deliver.sh --confirm\`
*Preview:*
\`\`\`
$PREVIEW
\`\`\`"
  echo "[$(date)] stage complete"
}

# ─── Confirm ───
do_confirm() {
  require_outbox
  if [ "$STATUS" != "PENDING DELIVERY" ]; then
    fail "expected STATUS: PENDING DELIVERY, got '$STATUS' (already finalized?)"
  fi

  # Rewrite header: PENDING DELIVERY → DELIVERED, add DELIVERED timestamp
  /opt/homebrew/bin/python3 - "$OUTBOX" "$ISO_TS" <<'PY'
import sys, re, pathlib
path = pathlib.Path(sys.argv[1])
ts = sys.argv[2]
text = path.read_text()
text = re.sub(r'^#\s*STATUS:\s*PENDING DELIVERY\s*$',
              f'# STATUS: DELIVERED\n# DELIVERED: {ts}',
              text, count=1, flags=re.MULTILINE)
path.write_text(text)
print(f"header rewritten in {path}")
PY
  RC=$?
  if [ $RC -ne 0 ]; then
    fail "header rewrite failed (rc=$RC)"
  fi

  # Archive
  ARCHIVE_NAME="SIS_TO_PI_OUTBOX_DELIVERED_${TS}.md"
  cp "$OUTBOX" "$ARCHIVE_DIR/$ARCHIVE_NAME"
  rm "$OUTBOX"
  echo "[$(date)] archived to $ARCHIVE_DIR/$ARCHIVE_NAME"

  # Receipt to both channels
  slack_romper "✅ *pi-deliver: DELIVERED* at $ISO_TS
Archived: \`$ARCHIVE_DIR/$ARCHIVE_NAME\`"
  slack_sis "✦ Letter delivered to Pi at $ISO_TS. Archived locally."
  echo "[$(date)] confirm complete"
}

# ─── Ship-it: stage + auto-paste + confirm ───
do_ship_it() {
  do_stage

  echo "[$(date)] ship-it: pausing 1.5s for Chrome to settle"
  sleep 1.5

  # Auto-paste + Return via osascript. Risk: pi.ai input field might not be
  # focused; Return might insert newline rather than send. Use only after
  # --stage has been verified once with manual paste.
  /usr/bin/osascript <<'APPLESCRIPT'
tell application "Google Chrome" to activate
delay 0.4
tell application "System Events"
  keystroke "v" using command down
  delay 0.5
  key code 36
end tell
APPLESCRIPT
  RC=$?
  echo "[$(date)] ship-it osascript paste+return rc=$RC"

  if [ $RC -ne 0 ]; then
    fail "ship-it osascript failed (rc=$RC) — message may or may not have sent. Check pi.ai manually then run --confirm or --abort."
  fi

  echo "[$(date)] ship-it: pausing 2s before confirm"
  sleep 2
  do_confirm
}

case "$MODE" in
  --stage)    do_stage ;;
  --confirm)  do_confirm ;;
  --ship-it)  do_ship_it ;;
  --help|-h)
    grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *)
    echo "usage: $0 [--stage|--confirm|--ship-it|--help]" >&2
    exit 64
    ;;
esac
