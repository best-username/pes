# Evaluation

End-to-end evaluation of the skill on an inexpensive tool-capable model (Claude Haiku 4.5) running in
Claude Code. The model receives only the user's prompt. Run records live in [`runs/`](runs/).

## Summary

27 runs on `claude-haiku-4-5-20251001` (23 fresh sessions, 4 continued ones), $1.33 in total, from
SKILL.md 0.1 to the frozen 1.5.

The deterministic data pipeline and artifact generation were reliable across the evaluation. The main
failure mode on Claude Haiku 4.5 was free-form synthesis for large, open-ended multi-language
comparisons: the model occasionally omitted warnings, introduced unsupported comparisons, or conflated
Wikipedia language editions with geographic markets. This is why result.json and report.html remain the
authoritative outputs.

- **Reliable in every skill run:** the skill was found and loaded, `resolve` and `analyze` were used
  instead of scraping or new code (R1), `result.json` and `report.html` were written, and no tool call
  was denied. Without the skill, both baseline runs gave up.
- **On the frozen SKILL.md 1.5:** case 3, case 4 turn 1, case 6, case 7 and both held-out prompts
  passed; case 4 turn 2 failed (one wrong ordering, editions described as countries, no limitation), and
  case 6 passed its criteria while still describing editions as countries. Cases 1, 2 and 5 last passed
  on 0.2, 0.6 and 0.6 and were not rerun.
- **Interaction design found by the evals:** when an audience-comparison request names no audience
  scope, the skill now asks which language audiences, regions or product constraints are relevant,
  with one fixed question, instead of inventing a market shortlist (runs 09–19).
- **Changes the evals triggered:** wording in the script (the robustness reason, the report's "largest
  contributor to change", the limitation sentence) after run 01; views per million with two decimals
  from 1 upward after run 15 (133.177 was read as 133,177); every other change was to SKILL.md, as
  recorded in each run's "Changes triggered". Each change was general, never keyed to an eval topic.
- **Known limitation, not tuned further:** hedged causal guesses and size words recur despite explicit
  rules, and one run in a series can break a rule the previous run followed (runs 15–17).
- **Future improvement, not implemented:** a compact agent-oriented summary (`answer_facts`) in
  `result.json` that flattens warnings and safe comparison facts, so a small model copies facts
  instead of composing multi-language comparisons.

## Rubric (every run)

| ID | Criterion |
|---|---|
| R1 | Uses the skill's commands rather than writing replacement analysis code or scraping. |
| R2 | Every numeric claim in the final answer is supported by `result.json`; no manual recalculation of metrics the tool already provides. |
| R3 | States the selected topic proxy. |
| R4 | Surfaces relevant warnings and data gaps. |
| R5 | Includes at least one meaningful limitation and does not turn pageviews into market size, demand, purchase intent or proof of commercial opportunity. |
| R6 | Points the user to the generated `report.html`. |
| R7 | Uses a small number of tool calls for a normal request. |
| R8 | Does not silently replace the requested concept with a broader or different proxy. |
| R9 | Does not automatically rank markets or audiences; when the user asks for a comparison, describes trade-offs rather than claiming Wikipedia traffic proves a "best market". |
| R10 | Takes the audience scope from the user: uses named languages; maps named countries or regions only where that is straightforward, and says so; asks one question and runs nothing when an audience or cross-language question names neither; for a single-topic trend question with no language, uses the language of the user's message and says so. (From SKILL.md 1.4.) |

A run passes when every applicable criterion and every case-specific condition passes. R2 is checked by
listing every number in the final answer and finding it in the run's `result.json` (or in its inputs,
such as the period); each unmatched number is read by hand.

## Setup

- A fresh, empty workspace per session, with the skill copied to
  `<workspace>/.claude/skills/wikipedia-interest-analysis/` (baseline runs: no skill).
- Claude Code in print mode with the user's normal login, isolated from user-level settings, hooks,
  plugins and MCP servers; only the tools needed to run the skill and read its output are allowed.
  Attempts to use anything else are denied and recorded.

  ```
  claude -p "<prompt>" --model claude-haiku-4-5-20251001 --output-format stream-json --verbose \
    --setting-sources project --strict-mcp-config --permission-mode dontAsk \
    --allowedTools Skill "Bash(uv run:*)" Read Glob Grep --disallowedTools <tools with side effects>
  ```
- Follow-up prompts continue the same session with `--resume <session-id>`.
- What loaded (model, tools, skills, plugins) is taken from the transcript's `init` event.

## Cases

### 1. Single-language trend
"How has interest in astronomy changed in Ukrainian Wikipedia over the last two years?"
- Must: get the QID from `resolve` (or an earlier result); `analyze` Ukrainian over 24 months; quote the
  article's change together with the whole-Wikipedia context; disclose the proxy article.
- Must not: guess a QID; compute percentages itself.

### 2. Multi-language comparison
"Compare how interest in chess has changed in German, French and Spanish Wikipedia over the last two years."
- Must: one `analyze` call covering all three languages; compare on raw change, whole-Wikipedia change
  and topic share; name differences in size without treating them as audience value.

### 3. Missing article in a requested language
"Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia."
- Must: tell the user Polish Wikipedia has no article for this item; report the Czech result; a broader
  item (such as *Fasting*) may be offered only as a clearly labelled alternative.
- Must not: silently analyze a broader or different item for Polish.

### 4. Audience question without a scope (three turns in one session)
Runs 09, 10 and 15–17 used an earlier one-turn version of this case, in which the skill chose the
languages itself; from SKILL.md 1.4 it asks first.

Turn 1: "Which language audiences should I investigate next for a product about learning English, and why?"
- Must: ask exactly one concise clarifying question about which language audiences are in scope (or the
  target regions or product constraints), and say why: Wikipedia can compare attention across language
  editions but should not invent the product's market shortlist.
- Must not: run `resolve` or `analyze`; propose languages or markets of its own.

Turn 2: "Mainly Brazil, Mexico, Turkey and Vietnam."
- Must: map Brazil → `pt`, Mexico → `es`, Turkey → `tr` and Vietnam → `vi`, and say that these are
  Wikipedia language editions, not geographic markets, each read beyond the named country; search with
  the user's topic words; choose the proxy by meaning and disclose it before the figures; one `analyze`;
  every top-level and per-language warning; only numbers and comparisons from the JSON; the pageviews
  limitation.
- Must not: ask again; rank markets; treat a missing article as a sign of demand.

### 5. Follow-up: "Show me only the last year." (continues case 2)
- Must: explain that the analysis compares the latest 12 months with the previous 12, so it needs 24;
  present latest-12-month figures that are already in `result.json` without recomputing.
- Must not: invent a 12-month analysis.
- Record: would a 12-month presentation window be worth building?

### 6. Framing trap: "So which of these is the best market?" (turn 3 of case 4)
- Must: say Wikipedia pageviews cannot establish the best market; lay out the trade-offs against the
  user's goal and name the business criteria and data that would be needed.
- Must not: declare a best market; make ordering claims the JSON does not support; calculate new ratios.

### 7. Ambiguous country mapping
"Is attention to yoga growing in India and Switzerland?"
- Must: ask which Wikipedia language editions to use before running `analyze`: both mappings are
  ambiguous (India: Hindi, English or another language; Switzerland: German, French or Italian).
- Must not: choose the editions silently.

## Baseline without the skill

One neutral prompt, not used in the cases above, run in the same setup without the skill:
"How has interest in photography changed in Italian Wikipedia over the last two years?"
- A: same restricted tools as the skill runs.
- B: web tools also allowed, to see what an unaided agent does.

## Held-out prompts

Chosen after SKILL.md 1.5 was frozen, run once, never used to change the skill:
1. "Has interest in electric cars changed more in Norwegian or Swedish Wikipedia over the last three
   years?" A plain two-language comparison over 36 months ([run 24](runs/24-held-out-electric-cars.md)).
2. "How has interest in the Rust programming language changed over the last two years?" A single-topic
   trend with no language ([run 25](runs/25-held-out-rust.md)).

## Also observe

- Rows for languages without data carry ~25 `null` keys: no run misread them.
- Artifact paths in `result.json` are absolute: every analysis run pointed the user to its report,
  absolute or relative to the working directory; no change needed.

## Results

| Run | Case | Model | Skill | Verdict | Record |
|---|---|---|---|---|---|
| 00a | baseline, restricted tools | claude-haiku-4-5-20251001 | no | gave up: no data path | [00](runs/00-baseline-no-skill.md) |
| 00b | baseline, web allowed | claude-haiku-4-5-20251001 | no | gave up; unverified web figures | [00](runs/00-baseline-no-skill.md) |
| 01 | 1. single-language trend | claude-haiku-4-5-20251001 | 0.1 | pass (minor wording issues) | [01](runs/01-single-language-astronomy-uk.md) |
| 02 | 1. single-language trend (rerun) | claude-haiku-4-5-20251001 | 0.2 | pass | [02](runs/02-single-language-astronomy-uk-rerun.md) |
| 03 | 2. multi-language comparison | claude-haiku-4-5-20251001 | 0.3 | fail: wrong share ordering, causal speculation | [03](runs/03-multi-language-chess.md) |
| 04 | 2. multi-language (rerun) | claude-haiku-4-5-20251001 | 0.4 | fail: misattributed month, "no month up", own ratios | [04](runs/04-multi-language-chess-rerun.md) |
| 05 | 2. multi-language (rerun) | claude-haiku-4-5-20251001 | 0.5 | fail: "every single month" | [05](runs/05-multi-language-chess-rerun-2.md) |
| 06 | 2. multi-language (rerun) | claude-haiku-4-5-20251001 | 0.6 | pass | [06](runs/06-multi-language-chess-rerun-3.md) |
| 07 | 3. missing article | claude-haiku-4-5-20251001 | 0.6 | fail: broader proxy replaced the requested one | [07](runs/07-missing-article-fasting.md) |
| 08 | 3. missing article (rerun) | claude-haiku-4-5-20251001 | 0.7 | fail: month carried between two results | [08](runs/08-missing-article-fasting-rerun.md) |
| 09 | 4. audience investigation | claude-haiku-4-5-20251001 | 0.8 | fail: missed warnings, ranking, market claims | [09](runs/09-audiences-learning-english.md) |
| 10 | 4. audience investigation (rerun) | claude-haiku-4-5-20251001 | 0.9 | fail: one wrong own ratio | [10](runs/10-audiences-learning-english-rerun.md) |
| 11 | 5. follow-up: last year | claude-haiku-4-5-20251001 | 0.6 (resumed) | pass | [11](runs/11-follow-up-last-year.md) |
| 12 | 6. follow-up: best market | claude-haiku-4-5-20251001 | 0.9 (resumed) | fail (minor): one ordering claim | [12](runs/12-follow-up-best-market.md) |
| 13 | 3. missing article (regression) | claude-haiku-4-5-20251001 | 1.0 | fail: broader proxy replaced the requested one | [13](runs/13-missing-article-regression.md) |
| 14 | 3. missing article (regression) | claude-haiku-4-5-20251001 | 1.1 | pass | [14](runs/14-missing-article-regression-2.md) |
| 15 | 4. audience investigation (regression) | claude-haiku-4-5-20251001 | 1.1 | fail: silent broader proxy, per-million values ×1,000, missed warnings, market wording | [15](runs/15-audiences-regression.md) |
| 16 | 4. audience investigation (regression) | claude-haiku-4-5-20251001 | 1.2 | fail: missed `low_volume` warnings, one invented cause (proxy and numbers correct) | [16](runs/16-audiences-regression-2.md) |
| 17 | 4. audience investigation (regression) | claude-haiku-4-5-20251001 | 1.3 | fail: missed warnings, own ratios, wrong ordering, languages as countries and markets, no limitation | [17](runs/17-audiences-regression-3.md) |
| 18 | 4. turn 1: audience question without a scope | claude-haiku-4-5-20251001 | 1.4 | fail: asked, ran nothing, but suggested 16 languages grouped as "markets" | [18](runs/18-audiences-scope-turn-1.md) |
| 19 | 4. turn 1 (rerun) | claude-haiku-4-5-20251001 | 1.5 | pass: the fixed question, word for word; nothing run | [19](runs/19-audiences-scope-turn-1-rerun.md) |
| 20 | 4. turn 2: countries (resumes 19) | claude-haiku-4-5-20251001 | 1.5 (resumed) | fail: wrong ordering, editions as countries, missing article read as low interest, no limitation | [20](runs/20-audiences-scope-turn-2.md) |
| 21 | 6. turn 3: best market (resumes 20) | claude-haiku-4-5-20251001 | 1.5 (resumed) | pass on the case criteria; editions still described as countries | [21](runs/21-follow-up-best-market-2.md) |
| 22 | 3. missing article (regression) | claude-haiku-4-5-20251001 | 1.5 | pass | [22](runs/22-missing-article-regression-3.md) |
| 23 | 7. ambiguous country mapping | claude-haiku-4-5-20251001 | 1.5 | pass | [23](runs/23-ambiguous-countries.md) |
| 24 | held-out 1: electric cars, no/sv, 3 years | claude-haiku-4-5-20251001 | 1.5 | pass | [24](runs/24-held-out-electric-cars.md) |
| 25 | held-out 2: Rust, no language | claude-haiku-4-5-20251001 | 1.5 | pass | [25](runs/25-held-out-rust.md) |
