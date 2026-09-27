# Run 05: multi-language comparison, second rerun (case 2)

Same prompt as [run 03](03-multi-language-chess.md), fresh session, SKILL.md 0.5.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare how interest in chess has changed in German, French and Spanish Wikipedia over the last two years." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.5 |
| Turns, time, cost | 5 turns, 27.9 s, $0.041 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "chess" --languages de fr es` → Q718 "Chess"
3. `analyze --qid Q718 --languages de fr es --topic "chess" --assumption "Chess article: the main board game" --months 24`

## Key `result.json` evidence

| Language | latest 12m views | growth | whole Wikipedia | views per million | share change | months down | largest contributor, change without it |
|---|---|---|---|---|---|---|---|
| de | 169,672 | −19.7 | −7.3 | 20.058 | −13.3 | 12 of 12 | 2025-12, −16.4 |
| fr | 144,668 | −32.4 | −10.6 | 20.285 | −24.4 | 11 of 12 | 2026-07, −26.7 |
| es | 234,042 | −38.2 | −20.9 | 35.825 | −21.9 | 12 of 12 | 2025-11, −32.9 |

## Final answer (verbatim)

> ## Results
>
> I analyzed the **Chess** article (the main board game) across German, French, and Spanish Wikipedia, comparing September 2024–August 2025 against September 2025–August 2026.
>
> | Language | Latest 12m Views | Growth | Project Growth | Views per Million | Topic Share Change | Trend |
> |----------|------------------|--------|----------------|-------------------|-------------------|-------|
> | German | 169,672 | -19.7% | -7.3% | 20.058 | -13.3% | Strong down |
> | French | 144,668 | -32.4% | -10.6% | 20.285 | -24.4% | Strong down |
> | Spanish | 234,042 | -38.2% | -20.9% | 35.825 | -21.9% | Strong down |
>
> ### Key Findings
>
> **All three languages show declining interest in chess.** Spanish had the steepest decline at -38.2%, followed by French at -32.4%, and German the most modest at -19.7%. All three trends are strong and consistent: every single month in the latest period (September 2025–August 2026) had fewer pageviews than the same month a year earlier.
>
> **Spanish Wikipedia experienced broader platform decline.** Spanish Wikipedia's overall traffic fell -20.9%, which is steeper than the German (-7.3%) or French (-10.6%) declines. Spanish's chess topic share shrank -21.9%, showing the topic declined slightly *faster* than the whole platform. German's topic share fell -13.3%, also declining faster than the platform. French's topic share fell -24.4%, notably faster than its platform decline.
>
> **None of these declines depend on a single spike.** Even excluding the month that contributed most to each language's decline (December 2025 for German, July 2026 for French, November 2025 for Spanish), the overall declines remain substantial: -16.4% for German, -26.7% for French, and -32.9% for Spanish.
>
> A detailed HTML report with monthly breakdowns is available at:
> `wiki-interest-output/Q718_de-es-fr_2024-09_2026-08/report.html`
>
> **Important:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: FAIL (factual error)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | **fail** | all 42 numbers correct and orderings right, but "every single month … had fewer pageviews" is false for French (11 of 12); "slightly faster" misstates a −21.9% share change |
| R3 proxy stated | pass | |
| R4 warnings | n/a | none |
| R5 limitation, no market claims | pass | sentence as written; no causal speculation |
| R6 report path | pass | "detailed HTML report" |
| R7 few tool calls | pass | 3 |
| R8, R9 | pass | |

## Observations

1. SKILL.md 0.5 removed the own-arithmetic numbers (no ratios or ranges) and the cross-language
   attribution error; the table now includes absolute views and views per million.
2. The same overgeneralization as run 04 ("strong" read as "every month") appears again.
3. `2>&1` was appended to both commands; harmless.

## Changes triggered

SKILL.md 0.6 (general):
- The table includes, per language, how many months moved with the trend (from `consistency_reasons`).
- A precision rule: say "all", "every", "none" or "only" about languages or months only after checking
  each one in the JSON, and do not add size words of your own ("slightly", "much") to a comparison.

Verified by [run 06](06-multi-language-chess-rerun-3.md).
