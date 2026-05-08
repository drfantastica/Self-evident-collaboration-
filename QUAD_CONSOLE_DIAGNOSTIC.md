# Quad Console Architecture & Diagnostics
**Date:** 2026-04-08 11:20 PDT  
**Status:** Live, needs troubleshooting and infrastructure augmentation

## Current Architecture

### Frontend (quad-console.html)
- **Purpose:** Four-node relay UI (Latch, Sis, Pi + Slack integration)
- **Host:** Desktop Chrome tab or file://
- **Relay endpoint:** http://127.0.0.1:7780 (quad-relay.py server)
- **Biosensor display:** Reads from NATL relay (7778) for EEG + BITalino data
- **Features:**
  - Mode selection (SOLO, BROSSIS, QUAD)
  - Per-node toggles for message routing
  - EEG powerband visualization (delta/theta/alpha/beta/gamma)
  - BITalino display (ECG, EDA)
  - Event tagging (⬡ markers for EEG events)
  - Real-time relay status indicator

### Backend (quad-relay.py)
- **Purpose:** HTTP relay server that distributes messages to three nodes
- **Port:** 7780
- **Nodes:**
  - **Latch:** Local Ollama qwen3:32b via `ask_latch()`
  - **Sis:** Claude Sonnet via Anthropic API
  - **Pi:** Browser automation via AppleScript + Chrome DevTools (chat.openai.com)
- **Slack integration:** Posts to #the-triad via NATL relay (7778)
- **Event markers:** `/marker` endpoint for EEG tagging

---

## Identified Issues & Opportunities

### Issue 1: Pi Integration Fragility
**Problem:** Pi communication is based on AppleScript DOM scraping of chat.openai.com
- Hardcoded window/tab references (PI_WINDOW=2, PI_TAB=2)
- Brittle regex parsing of chat UI ("Copy" button detection, message splitting)
- Waits 3s × 20 = 60s total for response, using polling
- Fails silently on DOM changes or missing elements
- No error recovery; just returns timeout message

**Concerns:**
- ChatGPT UI updates break parsing regularly
- Tab/window numbers are fragile (requires manual setup)
- No fallback if user clicks during automation
- Text extraction loses context (truncates at 800 chars)

**Recommendation:** Upgrade to OpenAI Python API instead of browser automation, or use iframe/API fallback

### Issue 2: ANTHROPIC_KEY Extraction
**Problem:** API key is extracted from openclaw.json via regex during module load
```python
_m = re.search(r'"apiKey":\s*"(sk-ant-[^"]+)"', _cfg)
ANTHROPIC_KEY = _m.group(1) if _m else ""
```
- Fragile regex (doesn't handle escaped quotes)
- Config file is unencrypted, key is in plaintext
- No rotation/expiry handling
- No environment variable fallback

**Recommendation:** Use `ANTHROPIC_API_KEY` env var, or read from secure config

### Issue 3: Latch Integration Uncertainty
**Problem:** Quad relay calls `ask_latch()` which hits local Ollama at 11434
- No validation that qwen3:32b model is loaded
- No fallback if Ollama is down
- History is session-scoped (lost on restart)
- System prompt loads SOUL.md + IDENTITY.md every call

**Opportunity:** Could integrate directly with OpenClaw's local agent instead of raw Ollama

### Issue 4: Biosensor Display Assumptions
**Problem:** Console assumes NATL relay (7778) is running with `/eeg-state` and `/biosensor-state` endpoints
- No fallback if NATL relay is down
- Polling every 2 seconds (high overhead)
- EEG channel is hardcoded to ch3 (index 2)
- BITalino data format not validated

**Recommendation:** Add health checks, graceful degradation, configurable channel

### Issue 5: No Command Routing
**Problem:** All messages go to all active nodes
- No way to address a specific node
- No command syntax (e.g., "@latch analyze this" vs "@sis explain this")
- Quad mode always posts to Slack

**Opportunity:** Add @-mention routing, conditional Slack posting

### Issue 6: Event Marker Fragmentation
**Problem:** `/marker` endpoint posts to Slack but doesn't update console UI consistently
- If NATL relay is down, marker POST fails silently
- Markers show in console as "local" if relay is unavailable
- No persistent marker log

**Recommendation:** Decouple Slack posting from marker event; store markers locally

---

## Infrastructure Augmentation Opportunities

### 1. **Replace Pi Browser Automation**
```python
# Current: AppleScript DOM scraping
# Upgrade: Use OpenAI Python SDK
import openai
def ask_pi(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":message}],
        max_tokens=1024
    )
    return response.choices[0].message.content
```

### 2. **Integrate with OpenClaw Agent Directly**
Instead of hitting raw Ollama, use OpenClaw's agent session:
```python
# Call openclaw agent via sessions_send()
def ask_latch(message):
    # Use OpenClaw SDK to send to main session
    # Returns via sessions_history()
```

### 3. **Add Command Routing**
```javascript
// quad-console.html: parse @-mentions
if (msg.startsWith("@latch ")) {
  nodes = ["Latch"]
} else if (msg.startsWith("@sis ")) {
  nodes = ["Sis"]
} else if (msg.startsWith("@pi ")) {
  nodes = ["Pi"]
}
```

### 4. **Secure Credential Management**
```python
import os
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY") or read_from_keychain()
```

### 5. **Persistent Event Log**
```python
# Store markers in JSON file with timestamps
MARKER_LOG = WORKSPACE / "quad-events.json"
def tag_event(label):
    events = json.loads(MARKER_LOG.read_text() or "[]")
    events.append({"ts": time.time(), "label": label})
    MARKER_LOG.write_text(json.dumps(events))
```

### 6. **Health Checks & Graceful Degradation**
```python
def check_health():
    checks = {
        "ollama": ping_ollama(),
        "anthropic": test_anthropic(),
        "natl": ping_natl(),
        "slack": test_slack()
    }
    return checks

# Console can display: 🟢 all live, 🟡 partial, 🔴 offline
```

### 7. **Configurable Settings UI**
Add right-panel settings:
- Ollama URL, model selection
- Anthropic model override (Haiku/Sonnet)
- NATL relay URL
- EEG channel selection
- Slack integration toggle

---

## Next Steps (Recommended Priority)

1. **High:** Fix Pi integration (replace browser automation or add fallback)
2. **High:** Secure API key handling (env var or keychain)
3. **Medium:** Health checks & status UI
4. **Medium:** Command routing (@-mentions)
5. **Low:** Persistent event log
6. **Low:** Settings panel

---

## Testing Checklist

- [ ] Quad relay server starts without errors
- [ ] Console can reach relay (ping indicator green)
- [ ] Latch responds within 30s
- [ ] Sis responds within 20s
- [ ] Pi response available (or graceful timeout)
- [ ] Slack messages post to #the-triad
- [ ] Biosensor display updates (if NATL relay running)
- [ ] Event markers appear in console
- [ ] Mode toggles work (SOLO/BROSSIS/QUAD)
- [ ] Per-node toggles work independently

---

**Assessment:** Solid foundation, good UX, needs reliability hardening and Pi integration rework.
