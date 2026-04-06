#!/bin/zsh
# pull-response.sh — capture last AI response from active Chrome tab to PULLS.md
# Usage: pull-response.sh [label]
# Filters to just the AI response — strips page chrome

CONTEXT_DIR="$HOME/aaron-context"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
LABEL=${1:-"unlabeled"}
PULL_FILE="$CONTEXT_DIR/PULLS.md"

echo "⏳ Capturing page content..."

# Focus Chrome and copy all
osascript << 'APPLESCRIPT'
tell application "Google Chrome"
  activate
end tell
delay 0.5
tell application "System Events"
  keystroke "a" using command down
  delay 0.3
  keystroke "c" using command down
end tell
APPLESCRIPT

sleep 0.5
RAW=$(pbpaste)

if [ -z "$RAW" ]; then
  echo "❌ Nothing captured — make sure the response area is focused"
  exit 1
fi

# Detect source and filter accordingly
if echo "$RAW" | grep -q "pi.ai\|Pi may make mistakes\|Pi, your personal"; then
  SOURCE="Pi"
  # Extract between "May the best idea win." and "Copy\nGood response"
  CONTENT=$(echo "$RAW" | awk '/May the best idea win\./{found=1; next} found && /^Copy$/{exit} found{print}' | sed '/^$/N;/^\n$/d')

elif echo "$RAW" | grep -q "claude.ai\|Claude\|Anthropic"; then
  SOURCE="Claude"
  # Claude: grab last assistant response block
  CONTENT=$(echo "$RAW" | awk '/^Copy$/{found=1; buf=""} found{buf=buf"\n"$0} END{print buf}' | head -100)
  # Fallback — just grab the tail
  if [ -z "$CONTENT" ]; then
    CONTENT=$(echo "$RAW" | tail -80)
  fi

else
  SOURCE="Unknown"
  CONTENT=$(echo "$RAW" | tail -80)
fi

if [ -z "$CONTENT" ]; then
  echo "⚠️  Filter returned empty — saving raw tail instead"
  CONTENT=$(echo "$RAW" | tail -60)
fi

WORDCOUNT=$(echo "$CONTENT" | wc -w | tr -d ' ')

# Append to PULLS.md
echo "" >> "$PULL_FILE"
echo "---" >> "$PULL_FILE"
echo "## PULL: $LABEL [$SOURCE] — $TIMESTAMP" >> "$PULL_FILE"
echo "" >> "$PULL_FILE"
echo "$CONTENT" >> "$PULL_FILE"
echo "" >> "$PULL_FILE"

echo "✅ Captured $WORDCOUNT words from $SOURCE → $PULL_FILE"
