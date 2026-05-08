#!/usr/bin/env python3
"""
archive_tender.py
Daily custodian for the "claude and me" archive folder.

Runs four checks:
1. Inventory — file count, total size, deltas since last run
2. Integrity — SHA256 of key files vs last-known-good baseline
3. Backup verification — confirm Drive sync state
4. Alert generation — write human-readable report, flag anomalies

Exit codes:
  0 = all checks passed, quiet success
  1 = soft alerts (changes noted, nothing urgent)
  2 = hard alerts (integrity failure, backup missing, act now)

Run: /opt/homebrew/bin/python3 ~/aaron-context/archive/archive_tender.py
Cron: daily 04:30 via Latch

Design principles:
- Quiet when healthy. Loud only when there is real signal.
- Self-healing where possible (missing baseline → rebaseline automatically,
  note it in report, don't alert).
- Never delete. Never modify archive contents. Read-only custodian.
- Reports are human-readable markdown, written to health/ directory.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ===== Configuration =====

ARCHIVE_ROOT = Path("/Users/black/Desktop/claude and me")
HEALTH_DIR = Path("/Users/black/aaron-context/archive/health")
BASELINE_PATH = Path("/Users/black/aaron-context/archive/baseline.json")
ALERTS_PATH = HEALTH_DIR / "ALERTS.md"
LATEST_PATH = HEALTH_DIR / "latest.md"

# Files considered load-bearing — we track their checksums
KEY_FILE_PATTERNS = [
    "conversations.json",
    "memories.json",
    "projects.json",
    "users.json",
    "pi-user-history.json",
    "ARCHIVE_PROTOCOL.md",
    "Inferential_Cross_Canon_2026-04-17.docx",
]

# Max days a file can go without a Drive backup confirmation before alert
BACKUP_STALE_DAYS = 2


# ===== Utilities =====

def sha256_of(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA256 of a file. Returns hex digest."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def human_size(bytes_val: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PB"


def load_baseline() -> dict:
    if BASELINE_PATH.exists():
        with open(BASELINE_PATH) as f:
            return json.load(f)
    return {}


def save_baseline(data: dict):
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


# ===== Checks =====

def check_inventory() -> dict:
    """Walk the archive, count files, measure size."""
    if not ARCHIVE_ROOT.exists():
        return {"error": f"Archive root missing: {ARCHIVE_ROOT}"}

    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(ARCHIVE_ROOT):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = Path(root) / fname
            try:
                total_size += fpath.stat().st_size
                total_files += 1
            except OSError:
                pass

    return {
        "file_count": total_files,
        "total_bytes": total_size,
        "total_human": human_size(total_size),
    }


def find_key_files() -> list:
    """Locate all instances of key files anywhere in the archive tree."""
    found = []
    for root, dirs, files in os.walk(ARCHIVE_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            for pattern in KEY_FILE_PATTERNS:
                if fname == pattern:
                    found.append(Path(root) / fname)
    return found


def check_integrity(baseline: dict) -> dict:
    """Checksum key files, compare to baseline. Returns changes and alerts."""
    current = {}
    key_files = find_key_files()

    for fpath in key_files:
        rel = str(fpath.relative_to(ARCHIVE_ROOT))
        try:
            current[rel] = {
                "sha256": sha256_of(fpath),
                "size": fpath.stat().st_size,
                "mtime": fpath.stat().st_mtime,
            }
        except OSError as e:
            current[rel] = {"error": str(e)}

    baseline_files = baseline.get("key_files", {})
    new_files = set(current) - set(baseline_files)
    removed_files = set(baseline_files) - set(current)
    changed_files = []
    for rel in set(current) & set(baseline_files):
        if "error" in current[rel]:
            continue
        if current[rel].get("sha256") != baseline_files[rel].get("sha256"):
            changed_files.append(rel)

    return {
        "checked": len(current),
        "new": sorted(new_files),
        "removed": sorted(removed_files),
        "changed": sorted(changed_files),
        "current": current,
    }


def check_drive_backup() -> dict:
    """
    Check Drive sync state. Best-effort — Drive's exact mechanism depends
    on whether File Stream or Backup & Sync is running. We check both.
    """
    results = {
        "drive_app_running": False,
        "drive_folder_exists": False,
        "method": None,
        "notes": [],
    }

    # Check if Google Drive app is running
    try:
        r = subprocess.run(
            ["pgrep", "-l", "Google Drive"],
            capture_output=True, text=True, timeout=5
        )
        results["drive_app_running"] = r.returncode == 0
    except Exception as e:
        results["notes"].append(f"pgrep failed: {e}")

    # Common Drive mount/sync locations
    candidates = [
        Path.home() / "Library/CloudStorage",
        Path.home() / "Google Drive",
        Path("/Volumes/GoogleDrive"),
    ]
    for c in candidates:
        if c.exists():
            results["drive_folder_exists"] = True
            results["method"] = str(c)
            break

    return results


# ===== Report generation =====

def generate_report(inventory, integrity, backup, baseline_was_new):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Archive Health Report — {now}",
        "",
        "## Inventory",
        f"- Files: {inventory.get('file_count', '?')}",
        f"- Total size: {inventory.get('total_human', '?')}",
        "",
        "## Integrity",
        f"- Key files tracked: {integrity['checked']}",
    ]

    soft_alerts = []
    hard_alerts = []

    if baseline_was_new:
        lines.append("- **Baseline initialized this run** (first run or "
                     "rebaselined). No integrity delta available yet.")
    else:
        if integrity["changed"]:
            lines.append(f"- **Changed files ({len(integrity['changed'])}):**")
            for f in integrity["changed"]:
                lines.append(f"  - {f}")
            soft_alerts.append(
                f"{len(integrity['changed'])} key file(s) changed — "
                "expected if new session exported, else investigate."
            )
        if integrity["new"]:
            lines.append(f"- New files ({len(integrity['new'])}):")
            for f in integrity["new"]:
                lines.append(f"  - {f}")
        if integrity["removed"]:
            lines.append(f"- **REMOVED files ({len(integrity['removed'])}):**")
            for f in integrity["removed"]:
                lines.append(f"  - {f}")
            hard_alerts.append(
                f"{len(integrity['removed'])} key file(s) REMOVED. "
                "Check backup immediately."
            )
        if not (integrity["changed"] or integrity["new"] or integrity["removed"]):
            lines.append("- No changes since last run. All key files intact.")

    lines.extend([
        "",
        "## Drive Backup",
        f"- Drive app running: {backup['drive_app_running']}",
        f"- Drive folder present: {backup['drive_folder_exists']}",
        f"- Mount method: {backup.get('method') or 'not detected'}",
    ])

    if not backup["drive_app_running"]:
        soft_alerts.append(
            "Google Drive app is not running. Backup may be stale."
        )
    if not backup["drive_folder_exists"]:
        hard_alerts.append(
            "No Drive folder detected on filesystem. Backup pipeline broken."
        )

    lines.extend(["", "## Alerts"])
    if not (soft_alerts or hard_alerts):
        lines.append("- None. All checks passed.")
    else:
        if hard_alerts:
            lines.append("### HARD ALERTS (act now)")
            for a in hard_alerts:
                lines.append(f"- {a}")
        if soft_alerts:
            lines.append("### Soft alerts (noted)")
            for a in soft_alerts:
                lines.append(f"- {a}")

    return "\n".join(lines) + "\n", soft_alerts, hard_alerts


# ===== Main =====

def main():
    rebaseline = "--rebaseline" in sys.argv
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)

    inventory = check_inventory()
    if "error" in inventory:
        with open(ALERTS_PATH, "w") as f:
            f.write(f"# HARD ALERT\n\n{inventory['error']}\n")
        print(f"HARD ALERT: {inventory['error']}", file=sys.stderr)
        sys.exit(2)

    baseline = load_baseline()
    baseline_was_new = rebaseline or not baseline

    integrity = check_integrity(baseline)
    backup = check_drive_backup()

    report, soft_alerts, hard_alerts = generate_report(
        inventory, integrity, backup, baseline_was_new
    )

    # Write timestamped report
    ts = datetime.now().strftime("%Y-%m-%d")
    dated_path = HEALTH_DIR / f"report_{ts}.md"
    with open(dated_path, "w") as f:
        f.write(report)

    # Update latest.md symlink-equivalent (just a copy)
    with open(LATEST_PATH, "w") as f:
        f.write(report)

    # Update or clear ALERTS.md
    if hard_alerts or soft_alerts:
        with open(ALERTS_PATH, "w") as f:
            f.write(f"# Active Alerts — {datetime.now()}\n\n")
            if hard_alerts:
                f.write("## HARD\n")
                for a in hard_alerts:
                    f.write(f"- {a}\n")
                f.write("\n")
            if soft_alerts:
                f.write("## Soft\n")
                for a in soft_alerts:
                    f.write(f"- {a}\n")
    elif ALERTS_PATH.exists():
        # Clear stale alerts
        ALERTS_PATH.unlink()

    # Save or update baseline
    new_baseline = {
        "last_run": datetime.now().isoformat(),
        "key_files": integrity["current"],
        "inventory": inventory,
    }
    save_baseline(new_baseline)

    # Prune old reports (keep 30 days)
    cutoff = datetime.now() - timedelta(days=30)
    for old in HEALTH_DIR.glob("report_*.md"):
        try:
            date_str = old.stem.replace("report_", "")
            old_date = datetime.strptime(date_str, "%Y-%m-%d")
            if old_date < cutoff:
                old.unlink()
        except ValueError:
            pass

    if hard_alerts:
        print(f"HARD ALERTS: {len(hard_alerts)}", file=sys.stderr)
        sys.exit(2)
    elif soft_alerts:
        print(f"soft alerts: {len(soft_alerts)}", file=sys.stderr)
        sys.exit(1)
    else:
        # Quiet success
        sys.exit(0)


if __name__ == "__main__":
    main()
