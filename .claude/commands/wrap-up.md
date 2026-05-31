---
description: Synthesize this session's learnings and file them to the vault per the schema.
---

Wrap up the current session. Use the rules in `memex-schema.md` — specifically `## When to File Vault Entries from Conversations` for what to file and `## Order of Operations for Updates` for how.

Steps:

1. **Drain any pending transcripts.** The flag dir is configured in `memex-schema.md` § Scheduled Maintenance (default `~/.memex/`). For each `.jsonl` file in `<FLAGS_DIR>/pending-wrapups/`:
   - Read it. Each line is one turn from a prior session that ended without `/wrap-up` being run.
   - Extract substantive material per the same rules used for this session in step 2.
   - Roll any findings into the proposal in step 3.
   - Delete the transcript file once it has been processed.

2. **Scan this session** for material worth filing:
   - New knowledge, research findings, or facts about tools/systems
   - Project decisions, context, or follow-ups
   - Insights, connections, or synthesis across topics
   - Anything I explicitly asked to save
   - Schema or process changes worth recording
   - Corrections I gave you that would help future-you (consider whether this belongs in the schema's rules section rather than a regular page)

3. **Propose, don't write yet.** Reply with a short list — for each item: destination file, a one-line summary, and whether it's a new page or an update to an existing one. Group by source (current session vs. each drained transcript). Wait for my confirmation before writing.

4. **On confirm**, write or update the pages, refresh cross-references on related pages, update `index.md`, and append a single `## [YYYY-MM-DD] wrapup | <one-line session theme>` entry to `log.md` with the filed items as bullets.

5. **Clear flags.** Delete `<FLAGS_DIR>/wrap-up-pending.flag` if present.

If nothing in this session or the pending transcripts is substantive enough to file, say so plainly, still append a single `## [YYYY-MM-DD] wrapup | no-op` line to `log.md` (so the next session can see wrap-up ran), and clear the flag.
