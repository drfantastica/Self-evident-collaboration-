#!/bin/zsh
# aaron-context-sync.sh
# Syncs /Users/black/aaron-context/ to Google Drive
# Runs automatically via launchd every 5 minutes

SOURCE="/Users/black/aaron-context/"
DEST="/Users/black/Library/CloudStorage/GoogleDrive-aaronmellinger@gmail.com/My Drive/aaron-context/"
LOG="/Users/black/aaron-context/.sync-log.txt"

# Check Drive is mounted
if [ ! -d "/Users/black/Library/CloudStorage/GoogleDrive-aaronmellinger@gmail.com" ]; then
  echo "$(date): Google Drive not mounted, skipping sync" >> "$LOG"
  exit 0
fi

# Create dest if it doesn't exist
mkdir -p "$DEST"

# Sync
rsync -av --delete "$SOURCE" "$DEST" >> "$LOG" 2>&1
echo "$(date): Sync complete" >> "$LOG"
