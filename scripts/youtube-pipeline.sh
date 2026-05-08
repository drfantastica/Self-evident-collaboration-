#!/usr/bin/env bash
# youtube-pipeline.sh — fire-and-forget YouTube transcription with Slack receipt.
#
# Usage: youtube-pipeline.sh <youtube-url>
#
# Workflow:
#   1. Extract video ID from URL.
#   2. Run ~/aaron-context/scripts/transcribe.py on the URL (writes to ~/aaron-context/transcripts/<slug>/).
#   3. Copy resulting transcript.txt to ~/Desktop/claude and me/youtube transcriptions/<vid>.txt.
#   4. Post a receipt + transcript contents to #sis-and-aaron via claudeslack.sh.
#   5. On failure, post the error and the log path.
#
# Designed to be invoked by the perception daemon's "shell" action type.
# Logs to ~/.config/latch/youtube-pipeline-logs/<vid>_<ts>.log.

set -uo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "usage: $0 <youtube-url>" >&2
  exit 1
fi

CLAUDESLACK="$HOME/aaron-context/claudeslack.sh"
TRANSCRIBE="$HOME/aaron-context/scripts/transcribe.py"
DEST_DIR="$HOME/Desktop/claude and me/youtube transcriptions"
LOG_DIR="$HOME/.config/latch/youtube-pipeline-logs"

mkdir -p "$LOG_DIR" "$DEST_DIR"

VID=$(/opt/homebrew/bin/python3 -c "
import sys, re
m = re.search(r'(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})', sys.argv[1])
print(m.group(1) if m else '')
" "$URL")

TS=$(date +%Y%m%dT%H%M%S)
if [ -z "$VID" ]; then
  /opt/homebrew/bin/python3 "$CLAUDESLACK" "youtube-pipeline: could not extract video ID from URL: $URL"
  exit 2
fi

LOG="$LOG_DIR/${VID}_${TS}.log"
exec >>"$LOG" 2>&1
echo "[$(date)] youtube-pipeline starting"
echo "URL=$URL"
echo "VID=$VID"
echo "DEST=$DEST_DIR/${VID}.txt"

# Run transcription synchronously inside this detached process
TR_OUT=$(/opt/homebrew/bin/python3 "$TRANSCRIBE" "$URL" 2>&1)
TR_RC=$?
echo "$TR_OUT"
echo "[$(date)] transcribe.py exit=$TR_RC"

if [ $TR_RC -ne 0 ]; then
  /opt/homebrew/bin/python3 "$CLAUDESLACK" "youtube-pipeline FAILED for $URL — transcribe.py exit $TR_RC. Log: $LOG"
  exit $TR_RC
fi

# transcribe.py prints "Done. Output: <abs_dir>" on success
OUT_DIR=$(echo "$TR_OUT" | awk -F'Output: ' '/Done\. Output: /{print $2; exit}')
SRC_TXT="$OUT_DIR/transcript.txt"

if [ -z "$OUT_DIR" ] || [ ! -f "$SRC_TXT" ]; then
  /opt/homebrew/bin/python3 "$CLAUDESLACK" "youtube-pipeline FAILED for $URL — transcript.txt not found (parsed OUT_DIR='$OUT_DIR'). Log: $LOG"
  exit 3
fi

DEST_TXT="$DEST_DIR/${VID}.txt"
cp "$SRC_TXT" "$DEST_TXT"
CHARS=$(wc -c < "$DEST_TXT" | tr -d ' ')

echo "[$(date)] copied $SRC_TXT → $DEST_TXT ($CHARS chars)"

# Post receipt with summary
/opt/homebrew/bin/python3 "$CLAUDESLACK" "transcribed: $URL → $DEST_TXT ($CHARS chars). Source dir: $OUT_DIR"
RECEIPT_RC=$?

# Post the transcript contents themselves so Sis can read them in the channel
/opt/homebrew/bin/python3 "$CLAUDESLACK" "$DEST_TXT" "Transcript: $VID"
CONTENTS_RC=$?

echo "[$(date)] receipt_rc=$RECEIPT_RC contents_rc=$CONTENTS_RC done"
