#!/usr/bin/env python3
"""
openclaw_config_set.py — Safe config writer for ~/.openclaw/openclaw.json

ALWAYS use this instead of writing openclaw.json directly.
Direct writes risk stripping required keys (gateway, models, agents, channels, etc.)
and will brick OpenClaw on next restart.

Usage:
  python3 openclaw_config_set.py 'acp.defaultAgent' 'latch'
  python3 openclaw_config_set.py 'agents.defaults.timeoutSeconds' 120
  python3 openclaw_config_set.py 'plugins.entries.memory-core.enabled' true

Supports dot-notation key paths. Values are auto-parsed (JSON-aware).
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
REQUIRED_TOP_LEVEL_KEYS = {"meta", "wizard", "acp", "models", "agents", "channels", "gateway", "plugins"}

def deep_set(d, key_path, value):
    """Set a value at a dot-notation path, creating intermediate dicts as needed."""
    keys = key_path.split(".")
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value

def parse_value(v):
    """Parse CLI value string as JSON if possible, else keep as string."""
    try:
        return json.loads(v)
    except (json.JSONDecodeError, ValueError):
        return v

def main():
    if len(sys.argv) < 3:
        print("Usage: openclaw_config_set.py <key.path> <value>", file=sys.stderr)
        sys.exit(1)

    key_path = sys.argv[1]
    raw_value = sys.argv[2]
    value = parse_value(raw_value)

    # Read current config
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    # Validate required keys are present before and will remain after
    missing_before = REQUIRED_TOP_LEVEL_KEYS - set(config.keys())
    if missing_before:
        print(f"WARNING: Config already missing required keys: {missing_before}", file=sys.stderr)
        print("Config may already be damaged. Proceeding with write anyway.", file=sys.stderr)

    # Apply the change
    deep_set(config, key_path, value)

    # Validate required keys still present after change
    missing_after = REQUIRED_TOP_LEVEL_KEYS - set(config.keys())
    if missing_after:
        print(f"ERROR: Write would strip required keys: {missing_after}. Aborting.", file=sys.stderr)
        sys.exit(2)

    # Safety backup before write
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3] + "Z"
    backup = CONFIG_PATH.parent / f"openclaw.json.pre-set.{ts}"
    shutil.copy(CONFIG_PATH, backup)

    # Write
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"OK: set {key_path} = {json.dumps(value)}")
    print(f"Backup: {backup.name}")

if __name__ == "__main__":
    main()
