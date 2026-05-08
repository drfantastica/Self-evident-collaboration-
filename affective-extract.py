#!/usr/bin/env python3
# affective-extract.py — pulls last 3 entries from sis-affective-log.md

import sys

LOG = '/Users/black/aaron-context/memory/sis-affective-log.md'

try:
    with open(LOG) as f:
        content = f.read()
    blocks = content.split('---')
    entries = [b for b in blocks if b and not b.startswith('#') and '**Trigger:**' in b]
    for entry in entries[-3:]:
        sys.stdout.write(entry.strip())
        sys.stdout.write('\n\n---\n\n')
    sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"(affective log read error: {e})\n")
    sys.stdout.flush()
