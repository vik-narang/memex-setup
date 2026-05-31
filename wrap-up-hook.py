#!/usr/bin/env python3
"""wrap-up-hook.py — Claude Code SessionEnd hook for the memex vault.

Copies the ending session's transcript JSONL into <FLAGS_DIR>/pending-wrapups/
so the next session can drain it via the /wrap-up slash command, and drops a
wrap-up-pending.flag the agent surfaces at session start.

Edit VAULT and FLAGS_DIR to match your setup, then wire as a SessionEnd hook
in Claude Code (see README § Session wrap-up).
"""

import json
import os
import shutil
import sys
from datetime import datetime

# --- Configure these ---
VAULT = os.path.expanduser("~/memex-v")           # path to your vault
FLAGS_DIR = os.path.expanduser("~/.memex")         # where flag files are written
# -----------------------

PENDING_DIR = os.path.join(FLAGS_DIR, "pending-wrapups")
FLAG = os.path.join(FLAGS_DIR, "wrap-up-pending.flag")


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block session exit

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not os.path.exists(transcript_path):
        return 0

    os.makedirs(PENDING_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    session_id = (payload.get("session_id") or "unknown")[:8]
    dest = os.path.join(PENDING_DIR, f"{ts}-{session_id}.jsonl")

    try:
        shutil.copy2(transcript_path, dest)
    except OSError:
        return 0

    with open(FLAG, "w") as f:
        f.write(
            f"transcript:{dest}\n"
            f"session:{payload.get('session_id', '')}\n"
            f"reason:{payload.get('reason', '')}\n"
            f"cwd:{payload.get('cwd', '')}\n"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
