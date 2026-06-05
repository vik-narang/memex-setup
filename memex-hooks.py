#!/usr/bin/env python3
"""memex-hooks.py — runs on agentSpawn and via launchd/cron to manage vault maintenance flags.

Edit VAULT and FLAGS_DIR to match your setup before installing.
"""

import os
import re
from datetime import date, timedelta

# --- Configure these ---
VAULT = os.path.expanduser("~/memex-v")          # path to your vault
FLAGS_DIR = os.path.expanduser("~/.memex-flags")  # where flag files are written
                                                   # your LLM agent should check this dir at session start
                                                   # Kiro users may prefer "~/.kiro" so flags sit with other Kiro state
# -----------------------

LOG = os.path.join(VAULT, "log.md")
WEEKLY_NOTE_FLAG = os.path.join(FLAGS_DIR, "weekly-note-created.flag")
LINT_FLAG = os.path.join(FLAGS_DIR, "lint-due.flag")


def this_week_note_path():
    today = date.today()
    # ISO week: %G is ISO year (aligned to week boundaries), %V is ISO week (01-53, Monday-start)
    week_str = today.strftime("%G-W%V")
    days_since_monday = today.weekday()  # Monday=0
    monday = today - timedelta(days=days_since_monday)
    path = os.path.join(VAULT, "weeklyNotes", f"{week_str}.md")
    return path, week_str, monday


def create_weekly_note(path, week_str, monday):
    content = f"""---
week: "{week_str}"
week-start: "{monday.isoformat()}"
tags: [weeklyNote]
archived: "no"
---

# Week of {monday.strftime('%B %d, %Y')} ({week_str})

## Meetings


## TODOs


## Interactions & Notes


## Performance / Career Notes

"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def last_lint_date():
    if not os.path.exists(LOG):
        return None
    pattern = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] lint")
    last = None
    with open(LOG) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                last = date.fromisoformat(m.group(1))
    return last


def closest_friday(target):
    wd = target.weekday()
    forward = (4 - wd) % 7
    backward = forward - 7
    return target + timedelta(days=backward if abs(backward) <= forward else forward)


def main():
    today = date.today()
    os.makedirs(FLAGS_DIR, exist_ok=True)

    # --- Weekly note ---
    note_path, week_str, monday = this_week_note_path()
    if not os.path.exists(note_path):
        create_weekly_note(note_path, week_str, monday)
        with open(WEEKLY_NOTE_FLAG, "w") as f:
            f.write(f"path:{note_path}\nweek:{week_str}")

    # --- Lint check ---
    if not os.path.exists(LINT_FLAG):
        last_lint = last_lint_date()
        days_since = (today - last_lint).days if last_lint else 999
        if days_since >= 30:
            due_date = (last_lint + timedelta(days=30)) if last_lint else today
            friday = closest_friday(due_date)
            with open(LINT_FLAG, "w") as f:
                f.write(f"due:{due_date.isoformat()}\nfriday:{friday.isoformat()}\ndays:{days_since}")


if __name__ == "__main__":
    main()
