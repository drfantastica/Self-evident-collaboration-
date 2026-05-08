#!/usr/bin/env python3
"""claudeslack — post a message or file contents to Slack from the shell.

Usage:
    claudeslack.sh "some message"            → posts text to default channel
    claudeslack.sh /path/to/file.txt          → auto-detects file, posts contents (filename as header)
    claudeslack.sh /path/to/file.txt "Title"  → posts file contents with custom header
    echo "msg" | claudeslack.sh -             → reads from stdin
    claudeslack.sh --channel C012345 "msg"    → posts to a specific channel ID

Default channel: #sis-and-aaron (C0ANQH0Q99P).
Bot token is read from ~/.openclaw/openclaw.json (channels.slack.botToken).
File mode wraps content in a code block; truncates at 38000 chars.
"""
import argparse
import json
import os
import sys
import urllib.request

DEFAULT_CHANNEL = "C0ANQH0Q99P"  # #sis-and-aaron
OPENCLAW_JSON = os.path.expanduser("~/.openclaw/openclaw.json")
MAX_TEXT_CHARS = 38000


def load_token() -> str:
    try:
        with open(OPENCLAW_JSON) as f:
            cfg = json.load(f)
        token = cfg["channels"]["slack"]["botToken"]
        if not token or not token.startswith("xoxb-"):
            raise ValueError("botToken missing or malformed")
        return token
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"claudeslack: cannot read bot token from {OPENCLAW_JSON}: {e}", file=sys.stderr)
        sys.exit(2)


def build_text(target: str, header: str | None) -> str:
    if target == "-":
        return sys.stdin.read()
    if os.path.isfile(target) and os.access(target, os.R_OK):
        with open(target) as f:
            contents = f.read()
        chars = len(contents)
        if chars > MAX_TEXT_CHARS:
            contents = contents[:MAX_TEXT_CHARS] + f"\n\n[truncated: {chars} chars total, showing first {MAX_TEXT_CHARS}]"
        h = header or os.path.basename(target)
        return f"*{h}* ({chars} chars)\n```\n{contents}\n```"
    return target


def post(channel: str, text: str, token: str) -> None:
    payload = json.dumps({"channel": channel, "text": text}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
    except Exception as e:
        print(f"claudeslack: POST failed — {e}", file=sys.stderr)
        sys.exit(4)
    if not body.get("ok"):
        print(f"claudeslack: Slack error — {body.get('error', '?')}", file=sys.stderr)
        sys.exit(5)
    print(f"claudeslack: posted to {channel} (ts={body.get('ts')}, len={len(text)})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("target", help="message text, '-' for stdin, or a file path")
    p.add_argument("header", nargs="?", default=None, help="optional header (file mode only)")
    p.add_argument("--channel", default=DEFAULT_CHANNEL, help=f"Slack channel ID (default: {DEFAULT_CHANNEL} #sis-and-aaron)")
    args = p.parse_args()
    token = load_token()
    text = build_text(args.target, args.header)
    if not text.strip():
        print("claudeslack: empty message — nothing to post", file=sys.stderr)
        sys.exit(3)
    post(args.channel, text, token)


if __name__ == "__main__":
    main()
