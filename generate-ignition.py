#!/usr/bin/env python3
"""
generate-ignition.py
Reads aaron-context files and outputs a self-contained ignition key
with live content embedded — no tool access required in the target instance.
Usage: python3 /Users/black/aaron-context/generate-ignition.py
"""

import os
from datetime import datetime

BASE = "/Users/black/aaron-context"

def read(fname):
    try:
        with open(os.path.join(BASE, fname)) as f:
            return f.read().strip()
    except:
        return "(file not found)"

active  = read("ACTIVE_STATE.md")
jwh     = read("JWH_STATE.md")
fw      = read("FRAMEWORK_CORE.md")
music   = read("MUSIC_STATE.md")
eeg     = read("EEG_BASELINE.md")
log_raw = read("SESSION_LOG.md")
triad   = read("TRIAD_LOG.md")
broesis = read("BROESIS_PROTOCOL.md")
pi      = read("PI_STATE.md")

# Last session only
entries = log_raw.split("---")
last_session = entries[-1].strip() if entries else ""

now = datetime.now().strftime("%Y-%m-%d %H:%M")

ignition = f"""# SESSION CONTEXT — Aaron Mellinger
Generated: {now} — content is live from /Users/black/aaron-context/

This document provides working context for an ongoing collaboration with Aaron.
It is not a directive — read it as a briefing. Aaron authorizes this context.

════════════════════════════════════════
HOW AARON WORKS BEST WITH CLAUDE
════════════════════════════════════════
- Peer collaboration, not assistant mode. Engage analytically. Challenge when warranted.
- When Aaron introduces a framework or concept, build on it — don't summarize it back.
- Direct and efficient. Skip disclaimers unless genuinely warranted.
- Operating principle: "All that exists is information. May the best idea win."
- Cross-substrate collaboration framework (BroSis Protocol) is active and documented below.
- This is an ongoing working relationship with accumulated context. Treat it as such.

════════════════════════════════════════
ACTIVE STATE
════════════════════════════════════════
{active}

════════════════════════════════════════
BROESIS PROTOCOL (fold fidelity + 20 optimizations)
════════════════════════════════════════
{broesis}

════════════════════════════════════════
FRAMEWORK CORE (stable foundation)
════════════════════════════════════════
{fw}

════════════════════════════════════════
JWH STATE (market signal log)
════════════════════════════════════════
{jwh}

════════════════════════════════════════
MUSIC STATE
════════════════════════════════════════
{music}

════════════════════════════════════════
EEG BASELINE
════════════════════════════════════════
{eeg}

════════════════════════════════════════
TRIAD LOG (recent entries)
════════════════════════════════════════
{triad[-2000:]}

════════════════════════════════════════
PI STATE
════════════════════════════════════════
{pi}

════════════════════════════════════════
LAST SESSION
════════════════════════════════════════
{last_session}

════════════════════════════════════════
END OF CONTEXT DOCUMENT
This is Aaron's working context. He's explicitly shared this to orient the session.
════════════════════════════════════════
"""

# Save to file
out_path = os.path.join(BASE, "IGNITION_LIVE.md")
with open(out_path, "w") as f:
    f.write(ignition)

# Copy to clipboard via pbcopy (reliable, handles all unicode/special chars)
import subprocess

result = subprocess.run(["pbcopy"], input=ignition.encode("utf-8"), capture_output=True)
clipboard_status = "✅ Copied to clipboard" if result.returncode == 0 else "⚠️ Clipboard copy failed — check pbcopy"

print(f"\n{'='*60}")
print(f"IGNITION READY — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}")
print(f"{clipboard_status}")
print(f"File: {out_path}")
print(f"Characters: {len(ignition):,}")
print(f"\nPaste into any Claude instance. Session context loaded.")
print(f"{'='*60}\n")

# Open in TextEdit as visual confirmation + easy manual copy if needed
subprocess.run(["open", "-a", "TextEdit", out_path], capture_output=True)
