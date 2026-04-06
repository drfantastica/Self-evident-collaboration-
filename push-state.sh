#!/bin/zsh
# push-state.sh — BroSis state handoff to a new Claude tab + auto-send
# Usage: push-state.sh [optional note]

CONTEXT_DIR="$HOME/aaron-context"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
NOTE=${1:-"Continuing session"}

STATE="🧠 BROESIS STATE HANDOFF — $TIMESTAMP
$NOTE

--- FRAMEWORK CORE ---
$(head -60 "$CONTEXT_DIR/FRAMEWORK_CORE.md" 2>/dev/null || echo "[not found]")

--- BROESIS PROTOCOL ---
$(head -60 "$CONTEXT_DIR/BROESIS_PROTOCOL.md" 2>/dev/null || echo "[not found]")

--- RECENT COMPLETIONS (closed loops) ---
$(cat "$CONTEXT_DIR/RECENT_COMPLETIONS.md" 2>/dev/null || echo "[not found]")

--- TRIAD LOG (last 80 lines) ---
$(tail -80 "$CONTEXT_DIR/TRIAD_LOG.md" 2>/dev/null || echo "[not found]")

---
May the best idea win."

echo "$STATE" | pbcopy
echo "✅ State copied to clipboard ($(echo "$STATE" | wc -c | tr -d ' ') chars)"

osascript << 'APPLESCRIPT'
tell application "Google Chrome"
  activate
  set newTab to make new tab at end of tabs of window 1
  set URL of newTab to "https://claude.ai/new"
end tell
APPLESCRIPT

echo "⏳ Waiting for Claude to load..."
sleep 4

osascript -e 'tell application "System Events" to keystroke "v" using command down'
sleep 1
osascript -e 'tell application "System Events" to key code 36'

echo "🚀 State pushed and sent to Claude tab"
