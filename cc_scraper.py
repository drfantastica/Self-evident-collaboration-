#!/usr/bin/env python3
"""
cc_scraper.py — Prime Video closed caption capture via macOS Accessibility API
Captures CC text in real-time during playback → timestamped JSONL.

Usage:
  python3 cc_scraper.py                        # auto-detect label
  python3 cc_scraper.py --label s4_lazar       # named session
  python3 cc_scraper.py --label s4_lazar --discover  # log all node changes (debug)

Output: ~/aaron-context/cc_capture_{label}.jsonl
        ~/local_media_index/chroma_db  (indexed after capture via local_media_index /ingest)

The scraper has two modes:
  DISCOVERY: polls all AXStaticText nodes, identifies which ones carry CC
             (they change over time; static UI text does not)
  CAPTURE:   polls only the identified CC nodes at 4Hz, writes text changes

Runs as standalone or invoked by perception daemon Prime Video trigger.
"""

import argparse
import json
import sys
import time
import signal
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR  = Path.home() / "aaron-context"
POLL_HZ     = 4          # samples per second during capture
DISC_WINDOW = 8.0        # seconds for discovery pass
MIN_CC_LEN  = 2          # minimum chars to count as CC text
MAX_CC_LEN  = 400        # longer than this is probably a paragraph, not a CC line

# ── Accessibility imports ──────────────────────────────────────────────────────
try:
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        kAXChildrenAttribute, kAXRoleAttribute, kAXValueAttribute,
        kAXTitleAttribute, kAXDescriptionAttribute, kAXWindowsAttribute,
        kAXSubroleAttribute,
    )
    from AppKit import NSWorkspace
except ImportError:
    print("ERROR: pyobjc-framework-ApplicationServices not installed.")
    print("Run: pip3 install pyobjc-framework-ApplicationServices pyobjc-framework-Quartz --break-system-packages")
    sys.exit(1)


# ── AX helpers ─────────────────────────────────────────────────────────────────
def ga(el, attr):
    err, val = AXUIElementCopyAttributeValue(el, attr, None)
    return val if err == 0 else None

def get_prime_pid() -> int | None:
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.localizedName() == "Prime Video":
            return app.processIdentifier()
    return None

def collect_text_nodes(el, depth=0, max_depth=16, nodes=None):
    """Recursively collect all AXStaticText elements."""
    if nodes is None: nodes = []
    if depth > max_depth: return nodes

    role = str(ga(el, kAXRoleAttribute) or '')
    if role == 'AXStaticText':
        nodes.append(el)

    children = ga(el, kAXChildrenAttribute)
    if children:
        for child in list(children)[:40]:
            collect_text_nodes(child, depth + 1, max_depth, nodes)
    return nodes

def get_text(el) -> str:
    v = ga(el, kAXValueAttribute)
    if v:
        return str(v).strip()
    t = ga(el, kAXTitleAttribute)
    if t:
        return str(t).strip()
    return ''


# ── Discovery pass ─────────────────────────────────────────────────────────────
def discover_cc_nodes(app_el, window_seconds=DISC_WINDOW) -> list:
    """
    Poll all AXStaticText nodes for DISC_WINDOW seconds.
    Nodes whose text changes during this window are CC candidates.
    Returns list of elements identified as CC carriers.
    """
    print(f"[discover] Scanning for CC nodes over {window_seconds}s...")
    print("[discover] Start playback now if not already running.")

    wins = ga(app_el, kAXWindowsAttribute) or []
    if not wins:
        print("[discover] No windows found.")
        return []

    all_nodes = collect_text_nodes(list(wins)[0])
    print(f"[discover] Found {len(all_nodes)} AXStaticText nodes")

    # Snapshot initial state
    snapshots = {i: get_text(n) for i, n in enumerate(all_nodes)}
    changed   = set()

    deadline = time.time() + window_seconds
    while time.time() < deadline:
        time.sleep(0.25)
        for i, node in enumerate(all_nodes):
            text = get_text(node)
            if text != snapshots[i]:
                if MIN_CC_LEN <= len(text) <= MAX_CC_LEN:
                    changed.add(i)
                    print(f"[discover] Node {i} changed → {text!r:.60}")
                snapshots[i] = text

    cc_nodes = [all_nodes[i] for i in sorted(changed)]
    print(f"[discover] Identified {len(cc_nodes)} CC node(s): indices {sorted(changed)}")
    return cc_nodes


# ── Fallback: poll all text nodes ──────────────────────────────────────────────
def get_all_candidate_text(app_el) -> list[str]:
    """When no CC nodes are pinned, scan the whole tree for short changing text."""
    wins = ga(app_el, kAXWindowsAttribute) or []
    if not wins:
        return []
    nodes = collect_text_nodes(list(wins)[0])
    candidates = []
    for n in nodes:
        t = get_text(n)
        if MIN_CC_LEN <= len(t) <= MAX_CC_LEN:
            candidates.append(t)
    return candidates


# ── Capture loop ───────────────────────────────────────────────────────────────
def capture(app_el, cc_nodes: list, label: str, discover_mode: bool):
    out_path = OUTPUT_DIR / f"cc_capture_{label}.jsonl"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[capture] Writing to {out_path}")
    print("[capture] Press Ctrl+C to stop.")

    last_texts = [''] * len(cc_nodes)
    last_any   = ''
    entry_count = 0
    interval = 1.0 / POLL_HZ

    with open(out_path, 'a') as f:
        while True:
            now_ts = datetime.now(timezone.utc).isoformat()
            now_sec = time.time()

            if cc_nodes:
                # Pinned-node mode — fast and reliable
                for i, node in enumerate(cc_nodes):
                    text = get_text(node)
                    if text and text != last_texts[i]:
                        entry = {
                            'ts': now_ts,
                            'label': label,
                            'text': text,
                            'node_index': i,
                            'source': 'ax_pinned'
                        }
                        f.write(json.dumps(entry) + '\n')
                        f.flush()
                        last_texts[i] = text
                        entry_count += 1
                        print(f"[{now_ts[11:19]}] #{entry_count:04d} {text!r:.80}")
            else:
                # Fallback: scan all candidates
                candidates = get_all_candidate_text(app_el)
                combined = ' | '.join(candidates)
                if combined and combined != last_any:
                    entry = {
                        'ts': now_ts,
                        'label': label,
                        'text': combined,
                        'node_index': -1,
                        'source': 'ax_scan'
                    }
                    f.write(json.dumps(entry) + '\n')
                    f.flush()
                    last_any = combined
                    entry_count += 1
                    print(f"[{now_ts[11:19]}] #{entry_count:04d} {combined!r:.80}")

            time.sleep(interval)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Prime Video CC scraper")
    parser.add_argument('--label', default=None, help='Session label for output file')
    parser.add_argument('--discover', action='store_true', help='Run discovery pass first')
    parser.add_argument('--no-discover', action='store_true', help='Skip discovery, use fallback scan')
    parser.add_argument('--discover-window', type=float, default=DISC_WINDOW,
                        help=f'Discovery window in seconds (default: {DISC_WINDOW})')
    args = parser.parse_args()

    pid = get_prime_pid()
    if not pid:
        print("ERROR: Prime Video is not running.")
        sys.exit(1)
    print(f"[init] Prime Video PID: {pid}")

    label = args.label or f"prime_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    app_el = AXUIElementCreateApplication(pid)

    # Graceful shutdown
    def on_stop(sig, frame):
        print(f"\n[stop] Captured session: {label}. Output at ~/aaron-context/cc_capture_{label}.jsonl")
        print(f"[stop] To index: curl -s http://localhost:7781/ingest -d '{{\"file_path\":\"<path>\",\"label\":\"{label}\"}}'")
        sys.exit(0)
    signal.signal(signal.SIGINT, on_stop)
    signal.signal(signal.SIGTERM, on_stop)

    cc_nodes = []
    if not args.no_discover:
        cc_nodes = discover_cc_nodes(app_el, args.discover_window)
        if not cc_nodes:
            print("[init] No CC nodes found in discovery. Falling back to full scan.")
            print("[init] Make sure CC is enabled in Prime Video and video is playing.")

    capture(app_el, cc_nodes, label, args.discover)


if __name__ == '__main__':
    main()
