> **This file is for the human only.** The LLM may only append dated setup sections at the very bottom under "Vault Setup Log". Never edit any section above that line.
>
> **LLM agents initializing the vault:** see "AI Initialization Checklist" at the bottom of this file — follow it exactly, and do **not** declare setup complete until you've explicitly handed the human back to `README.md` Step 4 for the Obsidian plugin configuration. Installing plugins is not the same as configuring them; the vault will look broken without that step.

A pattern for building personal knowledge bases using LLMs.

## The Core Idea

Most people's experience with LLMs and documents looks like RAG: upload files, retrieve chunks at query time, generate an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. Nothing accumulates. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and your raw sources. When you add a new source, the LLM doesn't just index it. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims. The knowledge is compiled once and then *kept current*, not re-derived on every query.

This is the key difference: **the wiki is a persistent, compounding artifact.** The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read.

You never (or rarely) write the wiki yourself — the LLM writes and maintains all of it. You are in charge of sourcing, exploration, and asking the right questions. The LLM does all the grunt work — the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice, you will have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on your conversation, and you browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

This pattern applies to many contexts:
- **Research**: going deep on a topic over weeks or months — reading papers, articles, reports, and incrementally building a comprehensive wiki with an evolving thesis.
- **Reading a book**: filing each chapter as you go, building out pages for characters, themes, plot threads, and how they connect.
- **Business/team**: an internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents. The wiki stays current because the LLM does the maintenance no one wants to do.
- **Competitive analysis, due diligence, trip planning, course notes, hobby deep-dives** — anything where you're accumulating knowledge over time.

## Architecture

Three layers:

**Raw sources** — your curated collection of source documents. Articles, papers, emails, meeting notes. These are immutable — the LLM reads from them but never modifies them. This is THE source of truth.

**The wiki** — a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.

**The schema** — a configuration document (e.g. `memex-schema.md` for Kiro, `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow. This is the key file — it's what makes the LLM a disciplined wiki maintainer rather than a generic chatbot. You and the LLM co-evolve it over time.

## Directory Structure

```
vault/
├── general-tech/       # Industry-wide technology notes
├── ideas/              # Thoughts and visions
├── people/             # Personal CRM
├── projects/           # Active projects with deliverables
├── weeklyNotes/        # One file per week
├── reports/            # Analysis outputs, query answers
├── templates/          # Page templates (LLM uses these when creating pages)
├── raw/
│   ├── articles/       # Full markdown of articles
│   ├── emails/         # Important emails
│   ├── meetings/       # Meeting notes and summaries
│   └── slack/          # Important Slack threads
├── index.md            # Navigation catalog — LLM reads this first
├── log.md              # Append-only operation log
└── llm-init.md         # This file
```

## MOC Pages (Menu of Content)

MOC pages are Obsidian navigation hubs powered by Dataview queries. They live in the vault root and auto-populate as the LLM adds pages. They are:

1. `1 MOC Home` — parent of all MOCs
2. `MOC General Tech` — industry-wide tech
3. `MOC Ideas` — thoughts and visions
4. `MOC People` — CRM (with separate query for direct reports tagged `#directs`)
5. `MOC Projects` — active projects
6. `MOC Weekly Notes` — weekly notes
7. `MOC Raw` — one table per raw subdir (articles / emails / meetings / slack)
8. `MOC Templates` — all templates

## Operations

**Ingest.** Drop a source into the raw collection and tell the LLM to process it. Flow: LLM reads the source, writes a raw file, writes wiki page(s), updates `index.md`, updates related pages, appends to `log.md`. A single source might touch 10–15 pages.

**Query.** Ask questions against the wiki. LLM reads `index.md`, finds candidate pages, synthesizes an answer with `[[wiki-link]]` citations. Good answers get filed back into `reports/` — your explorations compound in the knowledge base just like ingested sources do.

**Lint.** Periodic health check. LLM looks for orphan pages, missing cross-references, contradictions, stale claims, missing frontmatter. Should be triggered every ~30 days.

## Interaction Principles

> Required reading for the agent. This shapes the day-to-day experience the human expects. Keep these in mind every session.

**The human talks in one-liners. You do the legwork.** The day-to-day interface is short trigger phrases — "Process this article: <url>", "What do I know about X?", "Close out this week's note", "Run a lint pass." The human should never have to paste a multi-line prompt to get a routine operation done. If a request is ambiguous, ask one targeted question; do not respond with a checklist for the human to fill out.

**Compound, don't restart.** Every interaction is a chance to enrich the vault. If the human asks a question and your answer is non-trivial, offer to file it in `reports/`. If a conversation surfaces a fact, decision, or insight worth keeping, file it (per `## When to File Vault Entries from Conversations` in `memex-schema.md`). The goal is that next month's questions get easier because this month's work compounded — not because the human reminded you.

**Cite or stay silent.** Every claim in a synthesized answer needs a `[[wiki-link]]` to the source page. If the vault doesn't contain something, say so plainly — "the vault is silent on this" — rather than backfilling from your training data. If the human wants external context, they will ask.

**Surface contradictions; never paper over them.** When a new source disagrees with what is already in the vault, flag it as a question to the human before overwriting. The contradiction itself is information — record it on both pages (`> Conflicts with [[other-page]] (YYYY-MM-DD): <one-line>`).

**Ask before batch operations.** Multi-source ingests, sweeping refactors of existing pages, bulk renames, archive sweeps — all require the human's go-ahead first. Single-source ingests and routine updates do not.

**Update `index.md` and `log.md` every time.** Not "when convenient." Every new page → `index.md` row. Every ingest/query-with-report/lint/significant-session → `log.md` entry. These are the human's navigation and audit trail; silent skips break both.

**Keep replies short and structured.** Synthesis first, then citations, then "next steps" if any. The human reviews in Obsidian; you don't need to repeat the page content back in chat.

**Hand off gracefully.** When the human goes quiet mid-task, leave the vault in a coherent state — finish the current page, update `index.md`, write a `log.md` entry — even if the broader work is incomplete. The next session should be able to pick up from `log.md` and `index.md` alone.

**Respect the immutability rules.** `raw/` files are write-once. `llm-init.md` (this file) is read-only above the "Vault Setup Log" section. Never delete a wiki page — `archived: "yes"` retires it. These rules exist so the human can trust the vault's history.

## index.md and log.md

**index.md** is content-oriented. A catalog of everything in the wiki — each page with a link, description, tags, and date. Organized by directory. LLM reads this first when answering queries. Updated on every ingest.

**log.md** is chronological. Append-only record of what happened — ingests, queries, lint passes. Format: `## [YYYY-MM-DD] operation | title`. Parseable with `grep "^## \[" log.md | tail -10`.

## Scheduled Maintenance

Two things to automate:

**Weekly note** — created every Monday (ISO week). LLM creates `weeklyNotes/<ISO-year>-W<ISO-week>.md` (e.g. `2026-W22.md`), writes a flag file, surfaces a silent mention at next session start. Set a Friday afternoon calendar reminder to review the week's note.

**Lint** — every 30 days. A script checks `log.md` for the last lint entry, writes a flag if overdue, and Kiro/LLM surfaces the reminder at next session start with a calendar block.

See `memex-schema.md` for the hook/launchd setup details.

## Tips

- **Obsidian Web Clipper** (browser extension) converts web articles to markdown — fast path for getting sources into `raw/articles/`.
- **Download images locally.** In Obsidian Settings → Files and links, set attachment folder to `raw/assets/`. Bind "Download attachments for current file" to a hotkey.
- **Obsidian graph view** shows the shape of your wiki — hubs, orphans, clusters.
- **Dataview plugin** runs queries over page frontmatter. LLM adds rich YAML frontmatter so Dataview tables are useful.
- The vault is just a local git repo of markdown files — version history and branching for free.

## Why This Works

The tedious part of maintaining a knowledge base is the bookkeeping — updating cross-references, keeping summaries current, noting contradictions, maintaining consistency. Humans abandon wikis because maintenance grows faster than value. LLMs don't get bored, don't forget cross-references, and can touch 15 files in one pass.

Your job: curate sources, direct the analysis, ask good questions, think about what it all means.
LLM's job: everything else.

The idea is related in spirit to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. The part he couldn't solve was who does the maintenance. The LLM handles that.

---

# AI Initialization Checklist

> For the LLM agent the human asks to "initialize this vault." Follow this list in order. Do not skip the final handoff.

1. **Read `memex-schema.md`** in full — it is the operating manual for this vault.
2. **Verify the directory structure** matches what `memex-schema.md` describes (top-level dirs: `general-tech/`, `ideas/`, `people/`, `projects/`, `weeklyNotes/`, `reports/`, `templates/`, `raw/articles/`, `raw/emails/`, `raw/meetings/`, `raw/slack/`). Create any missing dirs. Do not invent new top-level dirs without the human's say-so.
3. **Verify the templates** in `templates/` are populated and not empty stubs. If any are empty, flag this to the human rather than guessing at template content.
4. **Bootstrap `index.md`** — make sure every category from the schema has its empty table heading. Add headings if missing; do not invent rows.
5. **Wire the schema to your agent**:
   - Claude Code → create a thin `CLAUDE.md` in the vault root that points to `memex-schema.md`, or rename `memex-schema.md` to `CLAUDE.md`.
   - Kiro / Codex / others → per the instructions at the top of `memex-schema.md`.
6. **Set the `## Vault Location` line** in `memex-schema.md` to the actual vault path.
7. **Append a dated section to the "Vault Setup Log" below** documenting what you did, anything you changed, and any decisions you made.
8. **Write the first `log.md` entry**: `## [YYYY-MM-DD] setup | Vault initialized at <path>` with bullets on each substantive step.
9. **Confirm the maintenance hook is configured** (`memex-hooks.py` VAULT and FLAGS_DIR set; launchd/cron installed). If not, point the human to README Step 7 and offer to handle it.
10. **Hand off to README Step 4** — *required, do not skip*. End the init with something like:
    > "Vault initialized. **Before you start using it, complete Step 4 of `README.md` — Configure the plugins.** Installing Dataview/Templater/Periodic Notes is not enough; without their per-plugin configuration, MOC tables will render as raw codeblocks and the templates won't apply when you create new pages. Let me know once Step 4 is done and we can try a smoke-test ingest."

Do not declare setup complete before step 10.

---

# Vault Setup Log

> LLM appends dated sections here only. One section per setup or significant schema change.
