# Run 14: missing article, second regression run (case 3)

Same prompt as [run 07](07-missing-article-fasting.md), fresh session, SKILL.md 1.1 (the rule dropped in
[run 13](13-missing-article-regression.md) restored).

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.1 |
| Turns, time, cost | 5 turns, 28.0 s, $0.041 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "intermittent fasting" --languages pl,cs` → Q1666254 (missing `pl`), Q44602 Fasting (both)
3. `analyze --qid Q1666254 --languages cs --topic "intermittent fasting" --assumption "Czech Wikipedia article on intermittent fasting as a proxy for attention to the topic; Polish Wikipedia lacks a dedicated article"`

## Key `result.json` evidence

Q1666254, cs "Přerušovaný půst": 2,198 views in 2025-09..2026-08, growth −53.6, whole Wikipedia −12.6,
3.082 views per million, share change −47.0, strong (12 of 12 months down; −45.5 without 2026-04), no
warnings.

## Final answer (verbatim)

> **Important limitation:** Polish Wikipedia does not have a dedicated article on intermittent fasting, so a direct comparison between the two languages is not possible using this topic.
>
> Czech Wikipedia has an article titled "Přerušovaný půst" (Intermittent fasting), and here's what the data shows for the latest 12 months (September 2025–August 2026):
>
> - **Views:** 2,198 views
> - **Change:** −53.6% (down sharply)
> - **Whole Wikipedia change:** −12.6% (moderate decline across all topics)
> - **Topic's share of views:** 3.08 per million, down 47% year-over-year
> - **Trend consistency:** Strong — all 12 months had fewer views than the same month a year earlier
>
> Czech Wikipedia shows a steep, consistent decline in attention to intermittent fasting. The topic is shrinking much faster than Wikipedia as a whole, indicating that interest in this specific topic waned significantly.
>
> **Would you like me to:**
> 1. Analyze the broader "Fasting" article (Q44602) for both Polish and Czech to get a comparison at a higher level?
> 2. Look at a different time period for Czech to see longer-term trends?
> 3. Check another language edition?
>
> The detailed monthly breakdown and visualization are available in the [analysis report](file://<workspace>/wiki-interest-output/Q1666254_cs_2024-09_2026-08/report.html).
>
> Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | pass | 30 numbers, all in `result.json` or the `resolve` output (Q44602); "3.08" rounds 3.082 |
| R3 proxy stated | pass | "Přerušovaný půst" (Intermittent fasting) |
| R4 warnings and data gaps | pass | Polish has no article, stated first |
| R5 limitation, no market claims | pass | sentence as written |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass | kept Q1666254 |
| Case: Polish named as missing; Czech result; broader item only as a labelled alternative | pass | Fasting offered as a question, not analyzed |

## Observations

1. Size words the skill asks it not to add: "sharply", "moderate", "much faster", "significantly".
2. "Topic's share of views: 3.08 per million" puts views per million and the share change on one line.
