# memex-setup

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Obsidian](https://img.shields.io/badge/obsidian-vault-7c3aed.svg)](https://obsidian.md)
[![Agent-agnostic](https://img.shields.io/badge/agent-Claude%20Code%20%7C%20Kiro%20%7C%20Codex%20%7C%20Cursor-success.svg)](#5-point-your-llm-at-the-schema)

**An LLM-maintained personal wiki.** You provide the sources and the direction; the LLM writes and maintains the wiki — pages, cross-references, summaries, indexes, logs. Knowledge compounds across sessions instead of being rediscovered every time.

Bring your own LLM (Claude Code, Kiro, Codex, Cursor, or any agent that can read and write local files), point it at the schema, and let it do the bookkeeping.

This is a concrete, opinionated implementation of the "LLM Wiki" pattern described by [@karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Obsidian as the IDE, a schema file as the operating manual, a hook script for scheduled maintenance, and a working setup you can clone and use today.

### How is this different from RAG?

RAG retrieves chunks from raw documents at query time and re-synthesizes an answer from scratch every time. Nothing accumulates. Ask the same subtle question next week and the LLM does the same work over again.

**memex compiles knowledge once and keeps it current.** The LLM reads each new source, integrates it into a persistent wiki — updating entity pages, revising summaries, flagging contradictions, threading cross-references. At query time, the synthesis is already done. The wiki is the compounding artifact; raw sources are just the input.

You are in charge of sourcing, exploration, and asking the right questions. The LLM does the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice: LLM agent on one side, Obsidian on the other — the LLM edits, you browse the graph in real time.

Read `llm-init.md` for the full philosophy. This README covers setup, configuration, and day-to-day usage.

---

## Quickstart (for the impatient)

```bash
git clone https://github.com/vik-narang/memex-setup ~/memex-v
cd ~/memex-v
# 1. Open ~/memex-v in Obsidian (File → Open Vault → Open folder as vault → trust author)
# 2. Install Dataview, Templater, Periodic Notes — then configure them per Step 4 below (most-skipped step)
# 3. In your LLM agent, with ~/memex-v as the working directory:
#    > "Read llm-init.md and initialize this vault according to the schema."
# 4. (Optional) Wire the daily launchd hook for the weekly note + lint reminder (Step 7)
```

Full walkthrough below.

---

## What You Need

- **Obsidian** — [obsidian.md](https://obsidian.md) (free). Your interface for browsing and reviewing the vault.
- **An LLM agent with local file access** — Claude Code, Kiro, Codex, Cursor, or any agent that can read and write local files.
- **Python 3** — for the maintenance hook (weekly note + lint reminder).

---

## Setup: Step by Step

The setup has two halves: **install and configure Obsidian + plugins** (Steps 1–4 below), then **point your LLM at the schema and ask it to initialize** (Steps 5–6). Do them in that order — the LLM init writes files that Obsidian will index when you open the vault, and the templates rely on plugin features.

### 1. Clone the repo to your vault location

```bash
git clone https://github.com/vik-narang/memex-setup ~/memex-v
```

Pick any path you like — `~/memex-v` is the default referenced by the schema and hook script. If you choose a different path, you'll edit one line in `memex-schema.md` (Step 5) and two in `memex-hooks.py` (Step 7).

### 2. Open the vault in Obsidian

File → Open Vault → "Open folder as vault" → select your vault folder.

When prompted about "Trust author and enable plugins?" — say **Trust**. Without trust, community plugins won't load.

### 3. Install the required Obsidian plugins

Settings → Community plugins → **Turn on community plugins** (first time only) → Browse, then install:

- **Dataview** — powers the MOC pages (auto-populated tables of contents).
- **Templater** — applies templates when creating new pages.
- **Periodic Notes** — optional but recommended; manages the weekly note.

After install, click **Enable** on each one (install ≠ enable).

### 4. Configure the plugins ← *this is the step most people skip*

Without this step, MOCs stay empty, templates don't apply, and the weekly note doesn't open automatically. Do all of these:

#### Dataview

Settings → Community plugins → Dataview → cog icon:

- **Enable JavaScript Queries** → ON (some MOCs use `dataviewjs` blocks; even if your current MOCs don't, leave it on for future flexibility).
- **Enable Inline JavaScript Queries** → ON.
- Leave the rest at defaults.

Verify: open `MOC General Tech.md`. You should see a Dataview-rendered table header (empty until you add content). If you see the raw ```` ```dataview ```` codeblock instead, Dataview isn't enabled — go back to Settings → Community plugins and toggle it on.

#### Templater

Settings → Community plugins → Templater → cog icon:

- **Template folder location** → `templates`
- **Trigger Templater on new file creation** → ON
- **Folder Templates** → click "Add new folder template" and pair each content directory with its template:

  | Folder | Template |
  |--------|----------|
  | `general-tech` | `templates/general-tech.md` |
  | `ideas` | `templates/ideas.md` |
  | `people` | `templates/people.md` |
  | `projects` | `templates/projects.md` |
  | `weeklyNotes` | `templates/weeklyNotes.md` |

  Now whenever you (or the LLM) create a new file in those folders, the template fills in automatically.

- **Hotkey for "Insert template"** (optional but useful): Settings → Hotkeys → search "Templater: Open insert template modal" → bind to `Cmd+Shift+T` (or whatever you like).

#### Periodic Notes (optional)

Settings → Community plugins → Periodic Notes → cog icon:

- **Weekly Notes** → toggle ON.
- **Weekly format** → `gggg-[W]WW` (ISO year + ISO week; matches the format the hook script writes — e.g. `2026-W22`).
- **Weekly template** → `templates/weeklyNotes.md`
- **Weekly note folder** → `weeklyNotes`

If you skip Periodic Notes, the daily hook (`memex-hooks.py`, set up in Step 7) still creates the weekly note for you on Monday — Periodic Notes just gives you a "Open this week's note" command for quick access.

### 5. Point your LLM at the schema

**Claude Code:** keep `memex-schema.md` as the operating manual and create a `CLAUDE.md` in the vault root that points to it. Claude Code auto-loads `CLAUDE.md` whenever the working directory is inside the vault. Alternative: rename `memex-schema.md` itself to `CLAUDE.md`. (When you run the init in Step 6, the LLM can do this for you.)

**Kiro:** copy `memex-schema.md` to `~/.kiro/steering/memex-v-schema.md` and add `inclusion: always` to the frontmatter. It will load every session.

**Codex:** rename `memex-schema.md` to `AGENTS.md` and place it in the vault root.

**Other agents:** load `memex-schema.md` however your agent supports persistent system instructions.

Then edit the `## Vault Location` line in the schema to your vault path (if different from `~/memex-v`).

### 6. Tell the LLM to initialize the vault

Open a new session with your LLM, with the vault as the working directory, and say:

> "Read `llm-init.md` and initialize this vault according to the schema. When you're done, point me back to the README for the Obsidian plugin configuration step."

The LLM will:
- Verify the directory structure exists and is correct.
- Bootstrap `index.md` with the category structure (if not already done).
- Write the first entry to `log.md`.
- Append a dated setup section to `llm-init.md`.
- **Confirm that you've completed Steps 3 and 4 above** — installing plugins isn't enough; they need to be configured. The LLM should not declare setup complete until you've confirmed that Dataview, Templater, and Periodic Notes are configured per Step 4.

### 7. Set up scheduled maintenance (recommended)

The hook script does two things:
- Creates `weeklyNotes/<ISO-year>-W<ISO-week>.md` every Monday if it doesn't exist (e.g. `2026-W22.md`).
- Writes a `lint-due.flag` file if it's been 30+ days since the last lint pass.

Both write flag files into `~/.memex/` (the default — change `FLAGS_DIR` in `memex-hooks.py` if you prefer somewhere else, e.g. `~/.kiro/` for Kiro users). Your LLM checks the flag dir at session start.

If you cloned the repo into `~/memex-v` (Quickstart default), `memex-hooks.py` is already in place. Otherwise, move it somewhere stable and edit `VAULT` + `FLAGS_DIR` at the top of the script to match your paths.

**macOS (launchd):**
```bash
# Edit com.memex.daily.plist — replace /path/to/your/scripts/memex-hooks.py with the real path
cp com.memex.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.memex.daily.plist
# Verify:
launchctl list | grep com.memex.daily
```

**Linux (cron):**
```bash
crontab -e
# Add: 0 9 * * * /usr/bin/python3 /path/to/memex-hooks.py
```

Logs (macOS): `/tmp/memex-hooks.log`, `/tmp/memex-hooks.err`.

### 8. Set up calendar reminders

- **Weekly review:** recurring private calendar block, Fridays ~3pm, 30 min — to review the week's note before the LLM closes it out.
- **Lint:** the LLM will offer to schedule one when the `lint-due.flag` appears (roughly monthly). Or create a recurring monthly block manually.

---

## Day-to-Day Usage

Everything is one-line triggers. The schema (`memex-schema.md`, section `## Operations`) already tells the agent how to handle each one — you don't need canned multi-line prompts.

**Add a source** — paste a URL, paste text, attach a file, or describe a meeting:
> "Process this article: <url>"
> "File this meeting: <paste notes>"
> "Save this Slack thread: <paste>"

**Ask a question** — agent reads `index.md`, pulls the relevant pages, answers with `[[wiki-link]]` citations:
> "What do I know about <topic>?"
> "Compare <X> and <Y>."
> "What did <person> say about <topic>?"

After the answer, the agent will ask whether to file the synthesis as a report in `reports/`. Say yes for anything worth keeping.

**Weekly review** — open the current week's note (e.g. `weeklyNotes/2026-W22.md`) in Obsidian. The LLM updates it through the week; on Friday:
> "Close out this week's note."

The agent will fill in missing context, surface decisions, link to anything created during the week, and prompt you for anything ambiguous.

**Lint** (roughly monthly, prompted by the `lint-due.flag`):
> "Run a lint pass."

**Pull a thread** — useful between major operations:
> "What's missing from <page>?"
> "Find contradictions in <topic>."
> "List orphan pages."

---

## Directory Structure

```
vault/
├── 1 MOC Home.md           # Entry point — links to all other MOCs
├── MOC General Tech.md     # Auto-table of general tech notes
├── MOC Ideas.md            # Auto-table of ideas
├── MOC People.md           # CRM tables (direct reports + everyone else)
├── MOC Projects.md         # Auto-table of active projects
├── MOC Weekly Notes.md     # Auto-table of weekly notes
├── MOC Raw.md              # Tables for each raw/ subdir
├── MOC Templates.md        # Auto-table of templates
│
├── general-tech/           # Industry-wide tech notes (#general-tech)
├── ideas/                  # Thoughts and visions (#ideas)
├── people/                 # Personal CRM (#people, #directs for reports)
├── projects/               # Active projects (#projects)
├── weeklyNotes/            # One file per week (#weeklyNote)
├── reports/                # Analysis outputs, query answers (#report)
│
├── templates/              # Page templates (all carry #template tag)
│   ├── general-tech.md
│   ├── ideas.md
│   ├── people.md
│   ├── projects.md
│   ├── weeklyNotes.md
│   └── recurringMeetings.md
│
├── raw/                    # Immutable source files — LLM writes, never edits
│   ├── articles/           # Full markdown of articles (#raw-article)
│   ├── emails/             # Important emails (#raw-email)
│   ├── meetings/           # Meeting notes and summaries (#raw-meeting)
│   └── slack/              # Slack threads (#raw-slack)
│
├── index.md                # Navigation catalog — LLM reads this first
├── log.md                  # Append-only operation log
├── llm-init.md             # Philosophy doc + setup log (human-owned)
└── memex-schema.md         # LLM operating manual → load per Step 5
```

---

## Adapting This for Your Domain

This starter has placeholder directories that you should adapt:

- **Add an `<employer>-tech/` directory** if you want a separate space for employer-internal notes (proprietary tooling, internal systems). Pick a tag like `#work-internal`, create a matching `MOC <Employer> Tech.md` and a `templates/<employer>-tech.md` template, and add a row to the schema's Directory Structure and Templates tables.
- **`people/`** assumes a CRM use case with `#directs` for direct reports. Remove that tag if you don't manage people.
- **`projects/`** template has an `email-folder` field and **`recurringMeetings/`** has a `calendar-event` field — both are tool-neutral; populate with whatever your email/calendar app provides (Outlook folder URL, Gmail label, Google Calendar event ID, etc.).

---

## Files to Take With You (Export Checklist)

If you move machines or share the vault:

| File | Where |
|------|-------|
| Vault directory | wherever you put it |
| `memex-schema.md` (or its renamed form) | loaded by your LLM agent |
| `memex-hooks.py` | path of your choice (matches `FLAGS_DIR` setting) |
| `com.memex.daily.plist` | `~/Library/LaunchAgents/` (macOS) |

---

## Credits

This starter is a concrete implementation of the "LLM Wiki" pattern proposed by Andrej Karpathy in [this gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The three-layer architecture (raw sources / LLM-maintained wiki / schema document), the `index.md` + `log.md` convention, the schema-as-operating-manual idea, and the framing of the wiki as a compounding artifact rather than a RAG-time lookup all come from there. What this repo adds is a working, opinionated implementation: Obsidian as the browsing layer, Dataview-powered MOCs, Templater wiring, a launchd hook for scheduled maintenance, and an agent-agnostic schema you can load into Claude Code, Kiro, Codex, Cursor, or any other agent with local file access.

If you use this and improve it — schema tweaks, new template types, better hook patterns — PRs welcome. (GitHub Issues are disabled on this repo to keep maintenance overhead low. To flag a bug or propose a change, open a PR with the fix or use a draft PR as a discussion thread.)
