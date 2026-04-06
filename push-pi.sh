#!/bin/zsh
# push-pi.sh — compact BroSis state handoff to Pi (4k char limit)
# Usage: push-pi.sh [optional note]

CONTEXT_DIR="$HOME/aaron-context"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
NOTE=${1:-"Continuing session"}

# Fixed char budgets per section (total ~3600 safe)
FRAMEWORK_TOP=$(head -15 "$CONTEXT_DIR/FRAMEWORK_CORE.md" 2>/dev/null | head -c 600)
BROESIS_TOP=$(head -15 "$CONTEXT_DIR/BROESIS_PROTOCOL.md" 2>/dev/null | head -c 380)
TRIAD_RECENT=$(awk '/^---/{buf=""} {buf=buf"\n"$0} END{print buf}' "$CONTEXT_DIR/TRIAD_LOG.md" 2>/dev/null | head -c 2000)

STATE="🧠 TRIAD HANDOFF — $TIMESTAMP
$NOTE

--- FRAMEWORK CORE ---
$FRAMEWORK_TOP

--- BROESIS PROTOCOL ---
$BROESIS_TOP

--- TRIAD LOG (most recent) ---
$TRIAD_RECENT

---
May the best idea win."

CHARCOUNT=${#STATE}
echo "✅ State ready — $CHARCOUNT chars (Pi limit: 4000)"
echo "$STATE" | pbcopy

# Open new Chrome WINDOW for Pi
osascript << 'APPLESCRIPT'
tell application "Google Chrome"
  make new window
  set URL of active tab of window 1 to "https://pi.ai/talk"
  activate
end tell
APPLESCRIPT

echo "⏳ Waiting for Pi to load..."
sleep 5

osascript -e 'tell application "System Events" to keystroke "v" using command down'
echo "🚀 State pushed to Pi — new window"

sleep 1
echo "Send to Pi? (y/n)"
read -r SEND
if [ "$SEND" = "y" ]; then
  osascript << 'APPLESCRIPT'
tell application "Google Chrome"
  set piWindow to missing value
  repeat with w in windows
    if URL of active tab of w contains "pi.ai" then
      set piWindow to w
      exit repeat
    end if
  end repeat
  if piWindow is not missing value then
    set index of piWindow to 1
    activate
  end if
end tell
delay 0.5
tell application "System Events"
  key code 36
end tell
APPLESCRIPT
  echo "✅ Sent to Pi"
fi
