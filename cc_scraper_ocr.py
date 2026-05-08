#!/usr/bin/env python3
"""
cc_scraper_ocr.py — Prime Video CC capture via Vision framework OCR
Captures the bottom strip of the Prime Video window at 2Hz, runs Apple Vision OCR,
deduplicates, and writes timestamped JSONL.

No accessibility permissions needed beyond Screen Recording.
macOS will prompt for Screen Recording access on first run.

Usage:
  python3 cc_scraper_ocr.py --label s4_lazar
  python3 cc_scraper_ocr.py --label s4_lazar --cc-height 0.22  # taller CC strip
"""

import argparse
import json
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path.home() / "aaron-context"
POLL_HZ    = 2      # OCR passes per second (Vision is fast on M5)
CC_STRIP   = 0.22   # fraction of window height to scan from bottom (CC zone)
MIN_LEN    = 3      # minimum text length to log

try:
    import Quartz
    from Quartz import (
        CGWindowListCopyWindowInfo, CGWindowListCreateImage,
        kCGWindowListOptionOnScreenOnly, kCGWindowListOptionIncludingWindow,
        kCGNullWindowID, kCGWindowImageDefault, kCGWindowImageShouldBeOpaque,
        CGRectMake,
    )
    import Vision
    from Foundation import NSData
    import objc
except ImportError as e:
    print(f"ERROR: Missing framework — {e}")
    print("Run: pip3 install pyobjc-framework-Vision pyobjc-framework-Quartz --break-system-packages")
    sys.exit(1)


# ── Window capture ─────────────────────────────────────────────────────────────
def get_prime_window() -> dict | None:
    wins = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for w in wins:
        if w.get('kCGWindowOwnerName', '') == 'Prime Video':
            return w
    return None

def capture_cc_strip(window_info: dict, cc_height_frac: float):
    """Capture only the bottom strip of the Prime Video window — where CC lives."""
    bounds = window_info['kCGWindowBounds']
    win_x  = float(bounds['X'])
    win_y  = float(bounds['Y'])
    win_w  = float(bounds['Width'])
    win_h  = float(bounds['Height'])

    strip_h = win_h * cc_height_frac
    strip_y = win_y + win_h - strip_h   # bottom of window

    rect = CGRectMake(win_x, strip_y, win_w, strip_h)
    wid  = window_info.get('kCGWindowNumber', 0)

    img = CGWindowListCreateImage(
        rect,
        kCGWindowListOptionIncludingWindow,
        wid,
        kCGWindowImageDefault | kCGWindowImageShouldBeOpaque
    )
    return img


# ── Vision OCR ─────────────────────────────────────────────────────────────────
def ocr_cgimage(cg_image) -> list[str]:
    """Run Apple Vision text recognition on a CGImage. Returns list of text strings."""
    if cg_image is None:
        return []

    results = []
    done    = [False]

    def handler(request, error):
        if error:
            done[0] = True
            return
        observations = request.results()
        if observations:
            for obs in observations:
                candidate = obs.topCandidates_(1)
                if candidate and len(candidate) > 0:
                    text = str(candidate[0].string())
                    conf = float(candidate[0].confidence())
                    if conf > 0.3 and len(text.strip()) >= MIN_LEN:
                        results.append(text.strip())
        done[0] = True

    req     = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelFast)
    req.setUsesLanguageCorrection_(True)

    handler_obj = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
        cg_image, {}
    )
    err = handler_obj.performRequests_error_([req], None)

    return results


# ── Main capture loop ──────────────────────────────────────────────────────────
def run(label: str, cc_height: float):
    out_path = OUTPUT_DIR / f"cc_capture_{label}.jsonl"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    win_info = get_prime_window()
    if not win_info:
        print("ERROR: Prime Video window not found. Is it running?")
        sys.exit(1)

    bounds = win_info['kCGWindowBounds']
    print(f"[init] Prime Video window: {float(bounds['Width']):.0f}x{float(bounds['Height']):.0f}"
          f" at ({float(bounds['X']):.0f}, {float(bounds['Y']):.0f})")
    print(f"[init] CC strip: bottom {cc_height*100:.0f}% of window")
    print(f"[init] Output: {out_path}")
    print(f"[init] Press Ctrl+C to stop.\n")

    last_text  = ''
    count      = 0
    interval   = 1.0 / POLL_HZ

    def on_stop(sig, frame):
        print(f"\n[stop] {count} entries captured → {out_path}")
        print(f"[index] curl -s http://localhost:7781/ingest "
              f"-H 'Content-Type: application/json' "
              f"-d '{{\"file_path\":\"{out_path}\",\"label\":\"{label}\"}}'")
        sys.exit(0)

    signal.signal(signal.SIGINT, on_stop)
    signal.signal(signal.SIGTERM, on_stop)

    with open(out_path, 'a') as f:
        while True:
            t0 = time.time()

            # Re-fetch window position each cycle (user may move window)
            win_info = get_prime_window()
            if not win_info:
                time.sleep(1.0)
                continue

            img   = capture_cc_strip(win_info, cc_height)
            texts = ocr_cgimage(img)

            if texts:
                combined = ' '.join(texts)
                # Deduplicate — only log when text changes
                if combined != last_text:
                    ts    = datetime.now(timezone.utc).isoformat()
                    entry = {
                        'ts':     ts,
                        'label':  label,
                        'text':   combined,
                        'source': 'vision_ocr',
                        'lines':  texts,
                    }
                    f.write(json.dumps(entry) + '\n')
                    f.flush()
                    last_text = combined
                    count += 1
                    print(f"[{ts[11:19]}] #{count:04d} {combined!r:.90}")

            elapsed = time.time() - t0
            sleep_t = max(0.0, interval - elapsed)
            time.sleep(sleep_t)


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Prime Video CC scraper (Vision OCR)')
    parser.add_argument('--label',     default=None,       help='Session label')
    parser.add_argument('--cc-height', type=float, default=CC_STRIP,
                        help=f'CC strip height as fraction of window (default {CC_STRIP})')
    args = parser.parse_args()

    label = args.label or f"prime_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run(label, args.cc_height)


if __name__ == '__main__':
    main()
