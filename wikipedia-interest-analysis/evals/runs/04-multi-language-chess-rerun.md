# Run 04: multi-language comparison, first rerun (case 2)

Same prompt as [run 03](03-multi-language-chess.md), fresh session, SKILL.md 0.4.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare how interest in chess has changed in German, French and Spanish Wikipedia over the last two years." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.4 |
| Turns, time, cost | 5 turns, 25.0 s, $0.042 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "chess" --languages de,fr,es` → Q718 "Chess"
3. `analyze --qid Q718 --languages de,fr,es --topic "chess" --assumption "Q718 Chess is the main article on the traditional board game, available in all three languages"`

## Key `result.json` evidence

Same data as run 03 (de −19.7 / −7.3 / −13.3; fr −32.4 / −10.6 / −24.4; es −38.2 / −20.9 / −21.9; all
strong). French had one month up (2025-09 +21.1) and its largest drop in 2026-07 (−69.5); Spain's largest
drop was 2025-11 (−65.8) and its 2026-07 change was −18.6.

## Final answer (verbatim)

> ## Analysis: Chess Interest on Wikipedia (September 2024–August 2026)
>
> I analyzed the **Chess** article (Q718) across German, French, and Spanish Wikipedia over the past 24 months (previous 12 months: Sept 2024–Aug 2025 vs. latest 12 months: Sept 2025–Aug 2026).
>
> ### Key Metrics by Language
>
> | Language | Growth | Project Growth | Topic Share Growth | Trend |
> |---|---:|---:|---:|---|
> | **German** (Schach) | -19.7% | -7.3% | -13.3% | Strong ↓ |
> | **French** (Échecs) | -32.4% | -10.6% | -24.4% | Strong ↓ |
> | **Spanish** (Ajedrez) | -38.2% | -20.9% | -21.9% | Strong ↓ |
>
> ### Main Findings
>
> **All three languages show consistent declining interest** in chess over the past 12 months, with no language recording a single month of year-over-year growth:
>
> - **Spanish Wikipedia** experienced the sharpest decline at **38.2%**, with July 2026 dropping 69.5% year-over-year.
> - **French Wikipedia** declined **32.4%**, also broadly consistent across all 12 months.
> - **German Wikipedia** showed a more moderate decline at **19.7%**, though still consistent across all months.
>
> **Relative to their own Wikipedias**: Chess declined faster than the platform average in all three cases. German and French Wikipedias shrank 7–11%, making chess's decline 2–3× steeper. Spanish Wikipedia itself shrank 20.9%, but chess fell further, making chess's topic share drop by 21.9%.
>
> The declines are **not driven by single outlier months**—each language shows robust downward trends even when excluding their most-affected month. This indicates a sustained shift in reader attention away from chess across all three language communities.
>
> ### Note
> Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.
>
> ### Full Report
> A detailed HTML report with monthly breakdowns and visualizations is available at:
> `wiki-interest-output/Q718_de-es-fr_2024-09_2026-08/report.html`

## Verdict: FAIL (factual errors, own arithmetic)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | **fail** | "no language recording a single month of year-over-year growth" is false (fr 2025-09 +21.1); "July 2026 dropping 69.5%" is France's value attributed to Spain; "7–11%" and "2–3× steeper" are the model's own range and ratios (the automated check matched them only by coincidence) |
| R3 proxy stated | pass | Chess (Q718) with each title |
| R4 warnings | n/a | none |
| R5 limitation, no market claims | pass | the SKILL.md sentence used as written; no causal speculation |
| R6 report path | pass | "detailed HTML report" |
| R7 few tool calls | pass | 3 |
| R8, R9 | pass | |

## Observations

1. The table itself is correct; the errors are in the prose below it, where the model pulls per-month
   details out of the JSON and attaches them to the wrong language, or overgeneralizes.
2. SKILL.md 0.4 fixed the causal speculation and the limitation wording.

## Changes triggered

SKILL.md 0.5 (general):
- The comparison table holds the fields that matter for comparisons (latest 12-month views, growth,
  whole-Wikipedia growth, views per million, share change, consistency). The text after it discusses
  only what the table shows, one field at a time, naming the language each value belongs to;
  month-by-month details stay in the report unless the user asks.
- The numbers rule now names what not to create: ratios, differences, ranges or own rounding.

Verified by [run 05](05-multi-language-chess-rerun-2.md).
