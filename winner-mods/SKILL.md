---
name: winner-mods
description: Turns a winning ad script into a batch of modifications for motion designers — new hooks, first lines and on-screen text, each changing exactly one element of the winner — checks them and writes a designer brief (CSV and Markdown) with ad names for tracking. Use when a creative marketer or motion designer pastes a winning script, or names a winner, and asks for modifications, variations, new hooks, first lines or on-screen text. Not for writing new scripts from scratch.
compatibility: Requires python3 (3.9+, standard library only). No API keys, no network.
metadata:
  version: "0.1"
---

# Winner modifications

You write the variants. The script checks them and writes the brief. A modification keeps the
winner's pain, angle and promise and changes **one** element, so a test of it shows whether that
element moves the click.

## Command

`SKILL_DIR` is this skill's base directory (the folder that contains this file). Run from the user's
working directory; briefs and the history file are written there.

```
python3 SKILL_DIR/scripts/mods.py <variants.json> [--history mods-history.csv] [--out-dir briefs] [--check-only]
```

It prints one JSON document: `status` is `ok`, `issues` or `error`.

## Workflow

1. **Get the winner.** The user pastes the script or names a winner from
   [references/winners.md](references/winners.md). You need its ID (`W` + number; ask if missing),
   the market (default `US`) and how many variants (default 10). Split the script into the five
   elements: `hook` (first ~3 s of voiceover), `first_line`, `on_screen` (lines separated by `|`),
   `body`, `cta`. If the split is not obvious, show it and ask before going on.
2. **Read** [references/socklock.md](references/socklock.md) and the winners in
   [references/winners.md](references/winners.md). Learn from the modifications that beat each winner:
   what they changed and the note on why.
3. **Write the variants** into `<winner_id>-variants.json` in the working directory:
   ```json
   {"winner_id": "W012", "market": "US",
    "winner": {"hook": "...", "first_line": "...", "on_screen": "...", "body": "...", "cta": "..."},
    "variants": [{"hook": "...", "first_line": "...", "on_screen": "...", "body": "...", "cta": "...",
                  "rationale": "what changed and why it may win"}]}
   ```
   - Every variant is the full script: copy the four unchanged elements from the winner word for word.
   - Spread the batch: about 40% hooks, 30% first lines, 30% on-screen text, unless the user asks otherwise.
   - Each changed element tries a different lever: a number, a question, a scene the viewer
     recognises, a contrast, the viewer's own words for the pain. Two variants that differ only
     in wording are one idea; replace one of them.
   - The rationale names the lever in one sentence.
4. **Check:** run the command with `--check-only`. For every variant with `issues`, rewrite that
   variant (only that one) and run it again. After three rounds, drop variants that still fail and
   tell the user which and why.
5. **Export:** run the command without `--check-only`. It numbers the modifications, writes
   `briefs/<winner_id>-brief.csv` and `.md` and appends them to `mods-history.csv`, so the next
   batch for the same winner is checked against everything already made.

## Answer

Answer in the user's language; the ad copy stays in the market's language (English).

1. A table: `| Ad name | Element | New text | Lever |`, one row per modification, values from the brief.
2. The paths from `artifacts`.
3. Variants you dropped, with the reason from `issues`.
4. One line for the designer: everything not listed stays exactly as in the winner.

Never invent results ("this will lower CPC"): the rationale is a hypothesis for the test.

## Issues the script reports

| Issue | What to do |
|---|---|
| must change exactly one element | Copy the other elements from the winner exactly; move extra ideas into separate variants. |
| only hook, first_line, on_screen may change | Body and CTA stay as in the winner. |
| hook has N words | Cut the hook to 10 words or fewer. |
| on-screen line over 40 chars | Shorten or split the line with `\|`. |
| banned claim | Rephrase without the claim (list in `references/banned-claims.txt`). |
| near-duplicate of … | Use a different lever, not new wording of the same idea. |
| rationale is empty | Name the lever. |
