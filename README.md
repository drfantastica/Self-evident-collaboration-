# CLAUDE SESSION CONTEXT
*How to use this directory*

## For Claude — read at session start:
1. Read ACTIVE_STATE.md first (open threads, current project status)
2. Pull specific state files as needed (JWH_STATE, EEG_BASELINE, MUSIC_STATE)
3. FRAMEWORK_CORE.md only needed if framework questions arise
4. SESSION_LOG.md for historical context if needed

## At session end, update:
- ACTIVE_STATE.md → update open threads, project status, next priorities
- Relevant state file if that domain was touched
- SESSION_LOG.md → append new entry

## Directory
/Users/black/aaron-context/
  README.md                   ← this file
  ACTIVE_STATE.md             ← read FIRST every session
  FRAMEWORK_CORE.md           ← stable foundation, Innostasis + Lens Palette
  EEG_BASELINE.md             ← Crown 3 protocol, channel mapping, session log
  JWH_STATE.md                ← active positions, signal log, recycling log
  MUSIC_STATE.md              ← Galaxies/Ghost Particle + studio setup
  SESSION_LOG.md              ← append-only historical record
  TRIAD_LOG.md                ← shared memory: Aaron + Sis + Pi messages
  BroSis_Continuity_State_v01.docx ← fold fidelity markers, open tensions, committed conclusions
  SelfEvidentCollaboration_README.md ← sympathetic resonance protocol origin doc
  optimizations-comprehensive.md ← 20 cross-substrate collaboration optimizations
  JWH_Detection_Rubric.pdf    ← full JWH methodology PDF
  memory-export-2026-03-17/   ← full Claude memory export (conversations.json 38MB + memories.json)
  aaron-context-sync.sh       ← sync script (auto-runs via launchd)
  .sync-log.txt               ← sync history log

## Google Drive Sync
Mirror: ~/Google Drive/My Drive/aaron-context/
Frequency: every 5 minutes automatically (via launchd)
Status: PENDING — requires Google Drive for Desktop install

### To activate (one time):
1. Install Google Drive for Desktop:
   https://www.google.com/drive/download/
2. Sign in with your Google account
3. Run once in Terminal to register the launchd agent:
   launchctl load ~/Library/LaunchAgents/com.aaron.context-sync.plist
4. Done — syncs automatically from that point forward

### To check sync status:
   cat /Users/black/aaron-context/.sync-log.txt

### To manually force a sync:
   /Users/black/aaron-context/aaron-context-sync.sh
