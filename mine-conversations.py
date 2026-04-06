#!/usr/bin/env python3
"""
mine-conversations.py
Extracts high-value moments from the Claude conversation archive.
Searches for framework keywords and outputs a HIGHLIGHTS.md

Usage: python3 /Users/black/aaron-context/mine-conversations.py
"""

import json, os
from datetime import datetime

BASE = "/Users/black/aaron-context"
ARCHIVE = f"{BASE}/memory-export-2026-03-17/conversations.json"
OUT = f"{BASE}/HIGHLIGHTS.md"

# Keywords that signal high-value framework moments
KEYWORDS = [
    "fold fidelity", "sympathetic resonance", "alien thought",
    "innostasis", "stagedrunkaholic", "diffusion alibi",
    "8-12-13", "foam", "coherence exploitation",
    "broesis", "brossis", "bro sis", "self-building staircase",
    "japanese whale", "forensic logic", "protection reflex",
    "game theory axis", "enabler axis", "doomed foam",
    "afcl", "agency-first", "deference signature",
    "time crystal", "substrate-independent", "fold architecture",
    "thirteenth note", "travel as reception", "angular shadows",
    "emergence principle", "synchronized forgetting",
    "wells fargo", "equal protection", "diamon stack",
]

print(f"Loading archive... ({os.path.getsize(ARCHIVE) // 1024 // 1024}MB)")

with open(ARCHIVE) as f:
    data = json.load(f)

print(f"Loaded. Processing conversations...")

hits = []

# Handle both list and dict structures
convos = data if isinstance(data, list) else data.get("conversations", [])

for convo in convos:
    title = convo.get("name", "") or convo.get("title", "") or "Untitled"
    created = convo.get("created_at", "") or convo.get("created", "")
    messages = convo.get("chat_messages", []) or convo.get("messages", [])

    for msg in messages:
        content = ""
        if isinstance(msg.get("content"), str):
            content = msg["content"]
        elif isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict) and block.get("type") == "text":
                    content += block.get("text", "")

        content_lower = content.lower()
        matched = [kw for kw in KEYWORDS if kw in content_lower]

        if matched:
            role = msg.get("role", "unknown")
            # Only capture substantial messages
            if len(content) > 200:
                hits.append({
                    "title": title,
                    "created": created,
                    "role": role,
                    "keywords": matched,
                    "excerpt": content[:600].replace("\n", " "),
                })

print(f"Found {len(hits)} high-value moments across {len(convos)} conversations.")

# Group by conversation title
from collections import defaultdict
by_convo = defaultdict(list)
for h in hits:
    by_convo[h["title"]].append(h)

# Write output
with open(OUT, "w") as f:
    f.write(f"# HIGHLIGHTS.md\n")
    f.write(f"# Mined from conversation archive — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"# {len(hits)} high-value moments across {len(by_convo)} conversations\n\n---\n\n")

    for title, entries in sorted(by_convo.items(), key=lambda x: -len(x[1])):
        f.write(f"## {title}\n")
        f.write(f"*{len(entries)} hits — keywords: {', '.join(set(kw for e in entries for kw in e['keywords']))}*\n\n")
        for e in entries[:3]:  # Top 3 per conversation
            f.write(f"**[{e['role']}]** {e['excerpt'][:400]}...\n\n")
        f.write("---\n\n")

print(f"\n✅ HIGHLIGHTS.md written to {OUT}")
print(f"Run: open {OUT}")
