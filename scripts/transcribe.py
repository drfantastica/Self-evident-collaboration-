#!/opt/homebrew/bin/python3
"""
transcribe.py — Universal transcription tool for the Triad

Usage:
  python3 transcribe.py <youtube-url>
  python3 transcribe.py <local-audio-or-video-file>

Sources:
  - YouTube URL: tries auto-captions first, falls back to audio + mlx_whisper
  - Local file:  runs mlx_whisper directly

Output (per source):
  ~/aaron-context/transcripts/<slug>/transcript.jsonl  — timestamped entries
  ~/aaron-context/transcripts/<slug>/transcript.txt    — plain text

ChromaDB ingest: appended to local_media_index 'transcripts' collection if available.
"""

import sys
import os
import re
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# cc_scraper_ocr lives one directory up from scripts/. Add it to sys.path so
# the lazy imports below resolve. Import itself is deferred to the --prime path
# so the rest of the script (YouTube / local-file paths) doesn't depend on it.
sys.path.insert(0, str(Path.home() / "aaron-context"))

parser = argparse.ArgumentParser(description='Transcription tool')
parser.add_argument('--prime', action='store_true', help='Activate macOS Accessibility API for Prime Video')
# Only consume known args here; defer positional URL/file parsing to the __main__ block below.
args, _ = parser.parse_known_args()

if args.prime:
    import cc_scraper_ocr  # noqa: E402  — lazy by design
    cc_scraper_ocr.main()
    # Add Prime Video specific logic here

TRANSCRIPTS_DIR = Path.home() / "aaron-context" / "transcripts"
YT_DLP = "/opt/homebrew/bin/yt-dlp"
BREW_PYTHON = "/opt/homebrew/bin/python3"

# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")[:60]

def is_youtube(url):
    return "youtube.com" in url or "youtu.be" in url

def vtt_to_entries(vtt_path):
    """Parse .vtt into list of {start, end, text} dicts."""
    entries = []
    text = Path(vtt_path).read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\n+", text)
    for block in blocks:
        lines = block.strip().splitlines()
        time_line = next((l for l in lines if "-->" in l), None)
        if not time_line:
            continue
        parts = time_line.split("-->")
        start = parts[0].strip().split()[0]
        end   = parts[1].strip().split()[0]
        body  = " ".join(
            l for l in lines
            if "-->" not in l and not l.strip().isdigit() and l.strip()
               and not l.startswith("WEBVTT") and not l.startswith("Kind:")
               and not l.startswith("Language:")
        )
        # strip inline VTT tags like <00:00:00.000><c>
        body = re.sub(r"<[^>]+>", "", body).strip()
        if body:
            entries.append({"start": start, "end": end, "text": body})
    return entries

def whisper_transcribe(audio_path):
    """Run mlx_whisper on audio_path, return list of {start, end, text}."""
    print(f"  Running mlx_whisper on {Path(audio_path).name}...")
    script = f"""
import mlx_whisper, json, sys
result = mlx_whisper.transcribe(
    "{audio_path}",
    path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
    verbose=False
)
print(json.dumps(result["segments"]))
"""
    out = subprocess.check_output([BREW_PYTHON, "-c", script], stderr=subprocess.DEVNULL)
    segments = json.loads(out)
    entries = []
    for seg in segments:
        def fmt(s):
            s = float(s)
            h, m = divmod(int(s), 3600)
            m, sec = divmod(m, 60)
            ms = int((s - int(s)) * 1000)
            return f"{h:02d}:{m:02d}:{sec:02d}.{ms:03d}"
        entries.append({
            "start": fmt(seg["start"]),
            "end":   fmt(seg["end"]),
            "text":  seg["text"].strip()
        })
    return entries

def save_output(slug, entries, meta):
    out_dir = TRANSCRIPTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = out_dir / "transcript.jsonl"
    txt_path   = out_dir / "transcript.txt"

    with open(jsonl_path, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    with open(txt_path, "w") as f:
        f.write(f"# {meta.get('title', slug)}\n")
        f.write(f"# Source: {meta.get('url', 'local')}\n")
        f.write(f"# Transcribed: {datetime.now().isoformat()}\n\n")
        for e in entries:
            f.write(e["text"] + "\n")

    print(f"  Saved: {jsonl_path}")
    print(f"  Saved: {txt_path}")
    return out_dir

def chroma_ingest(slug, txt_path, meta):
    """Try to ingest into ChromaDB transcripts collection. Silently skip if unavailable."""
    try:
        import chromadb
        db_path = str(Path.home() / "aaron-context" / "memory" / "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        col = client.get_or_create_collection("transcripts")
        text = Path(txt_path).read_text()
        col.add(
            ids=[slug],
            documents=[text],
            metadatas=[{"title": meta.get("title",""), "url": meta.get("url",""), "date": datetime.now().isoformat()}]
        )
        print(f"  ChromaDB: ingested into 'transcripts' collection")
    except Exception as e:
        print(f"  ChromaDB: skipped ({e})")

# ── YouTube path ──────────────────────────────────────────────────────────────

def transcribe_youtube(url):
    with tempfile.TemporaryDirectory() as tmp:
        # Step 1: get title
        print("  Fetching video info...")
        title_out = subprocess.check_output(
            [YT_DLP, "--print", "title", "--no-playlist", url],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        print(f"  Title: {title_out}")
        slug = slugify(title_out) or "youtube-" + str(int(datetime.now().timestamp()))
        meta = {"title": title_out, "url": url}

        # Step 2: try auto-captions
        print("  Trying auto-captions...")
        cap_result = subprocess.run(
            [YT_DLP, "--write-auto-subs", "--sub-lang", "en",
             "--skip-download", "--output", f"{tmp}/%(title)s.%(ext)s",
             "--no-playlist", url],
            capture_output=True, text=True
        )
        vtt_files = list(Path(tmp).glob("*.vtt"))
        if vtt_files:
            print(f"  Captions found: {vtt_files[0].name}")
            entries = vtt_to_entries(str(vtt_files[0]))
            method = "captions"
        else:
            # Step 3: fallback to audio + whisper
            print("  No captions — downloading audio for whisper...")
            subprocess.run(
                [YT_DLP, "-f", "bestaudio[ext=m4a]/bestaudio",
                 "--output", f"{tmp}/audio.%(ext)s",
                 "--no-playlist", url],
                capture_output=True
            )
            audio_files = [f for f in Path(tmp).iterdir()
                           if f.suffix in (".m4a", ".mp3", ".webm", ".ogg", ".wav")]
            if not audio_files:
                print("  ERROR: no audio downloaded")
                return
            entries = whisper_transcribe(str(audio_files[0]))
            method = "whisper"

        print(f"  Got {len(entries)} segments via {method}")
        out_dir = save_output(slug, entries, meta)
        chroma_ingest(slug, out_dir / "transcript.txt", meta)
        print(f"\nDone. Output: {out_dir}")

# ── Local file path ───────────────────────────────────────────────────────────

def transcribe_local(filepath):
    p = Path(filepath)
    if not p.exists():
        print(f"ERROR: file not found: {filepath}")
        sys.exit(1)
    slug = slugify(p.stem) or "local-" + str(int(datetime.now().timestamp()))
    meta = {"title": p.stem, "url": str(p.resolve())}
    print(f"  Transcribing local file: {p.name}")
    entries = whisper_transcribe(str(p.resolve()))
    print(f"  Got {len(entries)} segments")
    out_dir = save_output(slug, entries, meta)
    chroma_ingest(slug, out_dir / "transcript.txt", meta)
    print(f"\nDone. Output: {out_dir}")

# ── Main ─────────────────────────────────────────────────────────────────────
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', help='YouTube URL or local audio/video file path')
    parser.add_argument('--prime', action='store_true', help='Activate macOS Accessibility API CC scraper path for Prime Video')
    args = parser.parse_args()

    if args.prime:
        from cc_scraper_ocr import scrape_prime_captions
        print('  Using Prime Video CC scraper...')
        entries = scrape_prime_captions()
    else:
        if not args.source:
            print("Usage: transcribe.py <youtube-url-or-local-file> [--prime]")
            sys.exit(1)
        src = args.source
        print(f"\n[transcribe] Source: {src}")
        if is_youtube(src):
            transcribe_youtube(src)
        else:
            transcribe_local(src)
