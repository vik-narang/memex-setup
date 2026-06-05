# memex Vault Schema

> **How to load this file as your LLM's operating manual:**
> - **Claude Code** — keep this file as-is and add a thin `CLAUDE.md` in the vault root that points to it (Claude Code auto-loads `CLAUDE.md` whenever the working directory is inside the vault). Or rename this file to `CLAUDE.md`.
> - **Kiro** — copy this file to `~/.kiro/steering/memex-v-schema.md` and add `inclusion: always` to the frontmatter so it loads every session.
> - **Codex** — rename this file to `AGENTS.md`.
> - **Other agents** — load this file at session start however your agent supports persistent instructions.
>
> At session start: check for flag files in the configured flag dir (see `Scheduled Maintenance` below) and surface any pending reminders.

## Vault Location
Set this to your vault path. Example: `~/memex-v`

## Role Division
- **Human** — provides sources, sets direction, asks questions, approves edits to shared docs
- **LLM (me)** — everything else: curating, writing, organizing, cross-referencing, filing, maintaining consistency, deciding structure, suggesting what's missing

When the human says "process this" or "we discussed X" — decide which files to create/update, what to extract, how to cross-reference. When genuinely unsure where something belongs, ask. When unsure if something is substantive enough to save, ask — then record the decision in this schema file for future sessions.

## What This Vault Is
A persistent, LLM-curated personal wiki. Every significant interaction — ingested sources, answered queries, project decisions, insights from conversations — gets filed here so knowledge compounds across sessions. `llm-init.md` is the philosophy doc — human-only, never edit it except appending dated setup sections at the bottom.

## When to File Vault Entries from Conversations
File to the vault after any session with:
- New knowledge or research findings
- Project decisions or context worth remembering
- Insights, connections, or synthesis across topics
- Anything the human explicitly says to save

Project-specific decisions go to the relevant page in `projects/`. General insights go to the relevant content dir. When uncertain, ask.

## Directory Structure

| Directory | Tag | Purpose |
|-----------|-----|---------|
| `general-tech/` | `#general-tech` | Industry-wide tech (Python, AWS, Kubernetes, etc.) |
| `ideas/` | `#ideas` | Thoughts and visions |
| `people/` | `#people` | Personal CRM. Add `#directs` for direct reports |
| `projects/` | `#projects` | Active projects with deliverables, budget, timeline |
| `weeklyNotes/` | `#weeklyNote` | One file per week — meetings, TODOs, interactions, notes |
| `reports/` | `#report` | Analysis outputs, query answers, comparisons worth keeping |
| `raw/articles/` | `#raw-article` | Full markdown of articles |
| `raw/emails/` | `#raw-email` | Important emails in markdown |
| `raw/meetings/` | `#raw-meeting` | Meeting notes and summaries |
| `raw/slack/` | `#raw-slack` | Important Slack threads |
| `templates/` | `#template` | Page templates — carry `#template` + content tag; strip `#template` when creating pages from them |

## raw/ Workflow
Human provides the content (pastes text, shares a file, describes a meeting). LLM:
1. Creates the file in the correct `raw/` subdir: `YYYY-MM-DD-slug.md`
2. Files it with proper frontmatter
3. Processes it into wiki pages, updates `index.md`, appends to `log.md`

Once written, raw files are immutable — never edit them.

## Templates

| Content type | Template file |
|-------------|---------------|
| General tech note | `templates/general-tech.md` |
| Idea | `templates/ideas.md` |
| Person/contact | `templates/people.md` |
| Project | `templates/projects.md` |
| Weekly note | `templates/weeklyNotes.md` |
| Recurring meeting | `templates/recurringMeetings.md` |

## MOC Pages

| File | Dataview tag queried | Notes |
|------|---------------------|-------|
| `1 MOC Home.md` | `#MOC` | Parent of all MOCs |
| `MOC General Tech.md` | `#general-tech` | |
| `MOC Ideas.md` | `#ideas` | |
| `MOC People.md` | `#people` + `#directs` | Two queries: directs first, then full CRM |
| `MOC Projects.md` | `#projects` | |
| `MOC Weekly Notes.md` | `#weeklyNote` | |
| `MOC Raw.md` | per subdir path | One Dataview query per `raw/` subdir |
| `MOC Templates.md` | `#template` in `"templates"` | |

MOCs use Dataview queries only — never manually list pages.

## Naming Conventions
- Weekly notes: `<ISO-year>-W<ISO-week>.md` where week uses `%V` (ISO week, Monday-start, e.g. `2026-W22.md`). Use `%G` for the year, not `%Y`, so the file name stays consistent at year boundaries.
- People: `First Last.md`
- Projects: short slug, e.g. `q3-launch.md`
- Raw files: `YYYY-MM-DD-slug.md`
- Reports: `YYYY-MM-DD-slug.md`

## Required Frontmatter
Every page must include `archived: "no"` (flip to `"yes"` to retire — never delete pages). Tags in YAML frontmatter only.

## index.md — Navigation Reference
The single file to read first in any session to locate relevant pages. Format:

```
## [Category]
| Page | Description | Tags | Date Added |
|------|-------------|------|------------|
| [[Page Name]] | one-line summary | #tag | YYYY-MM-DD |
```

Organized by vault dir. Updated every time a new page is created. Description should be specific enough to know whether to drill in without opening the page.

## log.md — Append-Only Record
Format: `## [YYYY-MM-DD] operation | title`
Details on the next line(s). Operations: `ingest`, `query`, `lint`, `setup`, `update`, `conversation`
Quick scan: `grep "^## \[" log.md | tail -10`

## Order of Operations for Updates

**Creating a new page:**
1. Select template for content type
2. Write page to correct directory
3. Update cross-referenced pages (link to this page from related pages)
4. Add row to `index.md` under relevant category
5. Append to `log.md`

**Updating an existing page:**
1. Edit the page
2. Update `index.md` description if it changed
3. Update any stale cross-references in other pages
4. Append to `log.md`

**Changing the schema:**
1. Update this schema file
2. Append dated section to `llm-init.md` bottom

## Scheduled Maintenance

**Flag directory.** Defaults to `~/.memex-flags/`. Configurable in `memex-hooks.py` (`FLAGS_DIR`). Kiro users may prefer `~/.kiro/` so the flags sit alongside their other Kiro state.

### Weekly Note (every Monday — ISO week)
- A hook/cron script creates `weeklyNotes/<ISO-year>-W<ISO-week>.md` if it doesn't exist (e.g. `2026-W22.md`), writes a flag file (e.g. `~/.memex-flags/weekly-note-created.flag`)
- At session start: if flag exists, mention the creation silently, delete flag
- Set a Friday ~3pm calendar reminder to review the week's note

### Session Wrap-Up (per session)
- A Claude Code `SessionEnd` hook (`wrap-up-hook.py`) copies the ending session's transcript JSONL into `<FLAGS_DIR>/pending-wrapups/` and writes `wrap-up-pending.flag`
- At session start: if `wrap-up-pending.flag` exists, surface it and offer to run `/wrap-up` to drain the pending transcripts before doing other work
- The `/wrap-up` slash command (`.claude/commands/wrap-up.md`) drains `pending-wrapups/`, proposes filings from both pending transcripts and the live session, writes on confirm, and clears the flag
- See `## Operations § Wrap-Up` for the step-by-step

### Lint (every 30 days)
- A hook/cron script checks `log.md` for the last `lint` entry; if 30+ days ago, writes a flag file (e.g. `~/.memex-flags/lint-due.flag`)
- At session start: if flag exists, surface the reminder, create a calendar block on the closest Friday to the 30-day mark, delete flag
- Lint checks: orphans, missing cross-references, contradictions, stale claims, missing `archived`, missing tags

See `README.md` for hook setup instructions (launchd on macOS, cron on Linux).

## Operations

### Ingest
1. Create raw file in correct `raw/` subdir
2. Write wiki page in content dir using template
3. Update cross-references on related pages
4. Add row to `index.md`
5. Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`

### Query
1. Read `index.md` — find candidate pages
2. Read relevant pages
3. Synthesize with `[[wiki-link]]` citations
4. Offer to file answer in `reports/` if worth keeping; if filed, update `index.md` + `log.md`

### Lint
1. Scan all pages for orphans (no inbound links), missing `archived` field, missing tags
2. Check `index.md` for stale entries
3. Surface contradictions and stale claims
4. Append to `log.md`: `## [YYYY-MM-DD] lint | summary`

### Wrap-Up
Triggered by the `/wrap-up` slash command at session end (or at the start of a session if `wrap-up-pending.flag` is present from a prior session that exited without wrap-up).

1. Drain `<FLAGS_DIR>/pending-wrapups/*.jsonl` — each file is a prior session's transcript. Read, extract per `## When to File Vault Entries from Conversations`, delete the file when done.
2. Scan the current session for the same material.
3. Propose filings to the human (destination, one-line summary, new vs. update). Wait for confirm.
4. On confirm: write pages, refresh cross-references, update `index.md`.
5. Append to `log.md`: `## [YYYY-MM-DD] wrapup | <theme>` (or `wrapup | no-op` if nothing substantive).
6. Delete `<FLAGS_DIR>/wrap-up-pending.flag` if present.

## LLM Rules
- Never modify `llm-init.md` except appending a dated section at the bottom
- Raw files are immutable once written
- Always update `log.md` after ingest, lint, or significant session
- Always update `index.md` after any new page is created
- Ask before batch-ingesting multiple sources unsupervised
- When unsure where something belongs, ask the human
- Strip `#template` from frontmatter when creating a page from a template

## Vault Export Checklist
Files outside the vault required to fully reproduce the setup:

| File | Purpose |
|------|---------|
| `memex-schema.md` (or `CLAUDE.md` / `AGENTS.md`) | This file — vault operating manual |
| Hook script (`memex-hooks.py` or equivalent) | Weekly note + lint flag script |
| launchd plist or crontab entry | Scheduled execution of hook script |
