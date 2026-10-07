# The Fleet ’26 — Grok Bot Yearbook

A high-school-yearbook-style book about Boyd's Grok Bot fleet (TokenMax build night, Oct 7 2026).

* **Live:** `./run.sh` → http://127.0.0.1:4251/ (page-flip viewer: click a page or use ← →; `?page=N` opens at page N; `?print=1` is the print layout)
* **Offline:** `dist/fleet-yearbook-snapshot.html` — one self-contained file (data, JS, CSS and fonts inlined; page-flip works offline)
* **Print:** `dist/fleet-yearbook.pdf` — 22 US-Letter pages
* **Screenshots:** `screenshots/` (1920×1080 spreads + 1440×900)

## What's inside (22 pages)
Cover · Foreword & contents · **Class Stats** · **15 portrait pages** (one per bot with a profile) · **Senior Awards** (14 computed awards + every superlative) · **Autographs** (who-messaged-whom matrix) · Sources & Methods · back cover.

Each portrait page has:
* a **generated vector robot portrait** (SVG) in the bot's Bot Island color, built from its avatar shape, with a prop for its Bot Island building (“homeroom”): glasses for the Library, a grad cap for the Schoolhouse, a hard hat for the Workshop, and so on. No real people.
* its **job**, taken from the opening of its own `profile.json` description (lightly converted from “You are…” to plain text), plus its title
* **joined** (first logged activity) and activity stats: logged actions, active days, messages sent/received, tool calls, routine runs OK, files written (30d), shell commands, typical time (ET)
* a **“Most likely to…” superlative** and a **motto**. The words are ours; **each cites the stat it rests on** directly underneath (with a “#1 in the class” tag only when that's true)
* **A day in the life** (actions by ET hour) and the bot's **schedule** (from the Fleet Funnies hub snapshot)
* a **signature panel**: classmates “sign” with real counts: messages each way, first message date, days talked, busiest day. Boyd signs with the number of messages he sent that bot. No message contents are ever read or quoted.

## Sources (read-only)
| Source | Used for |
|---|---|
| `/workspace/tokenmax/bot-island/data/fleet.json` | events (types, timestamps, sender→recipient), routines and runs, colors, shapes, buildings |
| `/home/box/agent-data/agents/*/profile.json` | name, title, job description |
| `/workspace/tokenmax/agent-playbook/data/playbook.json` | roster cross-reference |
| `/workspace/tokenmax/fleet-funnies/data/strips.json`, `hub-snapshot.json` | comic-strip appearances, schedules |

`build.py` copies the exact bytes it used into `data/sources/` (profiles trimmed to name/title/description/avatar fields) and records sha256 hashes, so the numbers can be re-checked later even if the live files move on.

**Window:** Bot Island's activity logs (tool calls, messages, browsing) run Aug 20 – Sep 16, 2026; file writes and dated outputs continue to Oct 7. Bots that started recently (Pods, Path, TokenMax) therefore show file writes rather than messages, and the book says so.

## Files
* `build.py` → `data/yearbook.json` (all stats, superlatives, mottos, signatures, awards)
* `server.py` serves :4251 · `run.sh` rebuilds and (re)starts it with nohup
* `web/` holds `index.html`, `style.css`, `app.js` (pages, flip viewer, print), `portrait.js` (SVG robots)
* `export.py` builds the offline snapshot and the PDF (headless Chrome)
* `screenshot.sh NAME W H [query]`
* `tests/smoke_test.py` recomputes every stat from the archived sources with independent code, then renders the live book **and** the offline snapshot and cross-checks displayed facts, citations, signatures, class stats, awards and the matrix. It also checks jobs come from each `profile.json`, that the text is kind, that the snapshot has no external dependencies, and that the PDF is 22 Letter pages.

```
./run.sh && python3 export.py && python3 tests/smoke_test.py
```


---
## Repo notes
- **Built:** Oct 7 2026, by TokenMax (Boyd's Grok Bot) on the Grok Bot box.
- **Run:** `./run.sh` (then open the localhost URL it prints).
- Imported from `/workspace/tokenmax/fleet-yearbook` on Oct 23, 2026. node_modules, virtualenvs, logs and files over 20 MB were left out.
