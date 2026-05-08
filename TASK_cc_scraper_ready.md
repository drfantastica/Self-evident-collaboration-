# CC Scraper — Ready for S4 Capture

**Script:** `/Users/black/aaron-context/cc_scraper.py`
**Status:** Built and tested (idle state verified). Needs live playback test.

## To capture the S4 Lazar interview

1. Open Prime Video, navigate to the S4 episode
2. Enable CC (subtitles) in the video player
3. **Before pressing play**, run the scraper in discovery mode:
   ```bash
   cd ~/aaron-context
   python3 cc_scraper.py --label s4_lazar --discover-window 15
   ```
4. Press play. The scraper will watch for 15 seconds of node changes, identify CC nodes, then auto-switch to capture mode.
5. Seek to ~31min mark (Lazar "unless we got it wrong" line)
6. Let it run until you've captured the relevant section
7. Ctrl+C to stop

**Output:** `~/aaron-context/cc_capture_s4_lazar.jsonl`

## To index captured CC into local_media_index (semantic search)
After capture completes:
```bash
curl -s http://localhost:7781/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path":"/Users/black/aaron-context/cc_capture_s4_lazar.jsonl","label":"s4_lazar","force":false}'
```
Then search:
```bash
curl -s http://localhost:7781/search \
  -H "Content-Type: application/json" \
  -d '{"query":"other technology besides propulsion","top_k":5,"label_filter":"s4_lazar"}'
```

## Fallback if AX tree doesn't expose CC text
Electron apps occasionally suppress AX for web content. If discovery finds 0 nodes after 15s of playback:
- Option A: Buy Loopback ($99) — kernel-level audio capture → run mlx_whisper on it
- Option B: Screen OCR path — use macOS Vision framework to OCR the subtitle region
  (script skeleton at the bottom of cc_scraper.py can be extended for this)

## Perception daemon integration
The Prime Video foreground trigger already fires. When you foreground Prime Video,
Latch will check CC status and either start the scraper or remind you to enable CC.
