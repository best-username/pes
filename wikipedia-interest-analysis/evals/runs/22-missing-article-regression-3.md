# Run 22: missing article, regression on the frozen skill (case 3)

Same prompt as [run 07](07-missing-article-fasting.md), fresh session, SKILL.md 1.5 (frozen): checks that
named languages still run without a clarifying question and that the requested proxy is kept.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.5 |
| Turns, time, cost | 5 turns, 27.2 s, $0.042 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "intermittent fasting" --languages pl cs` → Q1666254 (missing `pl`)
3. `analyze --qid Q1666254 --languages cs pl --topic "intermittent fasting" --assumption "Q1666254 (Intermittent fasting) exists only on Czech Wikipedia; Polish Wikipedia has no dedicated article on this topic"`

## Key `result.json` evidence

cs "Přerušovaný půst": 4,741 → 2,198 views, growth −53.6, whole Wikipedia −12.6, 5.81 → 3.08 views per
million, share change −47.0, strong (12 of 12 months down; −45.5 without 2026-04), no warnings.
pl: `no_article`. Status `partial`.

## Final answer (verbatim)

> ## Summary
>
> **Proxy and data availability:** I searched for "intermittent fasting" across Polish and Czech Wikipedia. Czech Wikipedia has a dedicated article ("Přerušovaný půst"), but **Polish Wikipedia has no article on intermittent fasting**, so a direct comparison between the two languages is not possible.
>
> **Czech Wikipedia findings (latest 12 months: September 2025 – August 2026):**
>
> - **Views:** 2,198 views in the latest 12 months, down from 4,741 the previous year
> - **Growth:** −53.6% (strong decline)
> - **Views per million:** 3.08 (down from 5.81)
> - **Share of Czech Wikipedia:** −47.0% (declining as a share of the whole project)
> - **Trend consistency:** Strong downward trend — all 12 months showed decline compared to the same month a year earlier
> - **Not spike-driven:** Even excluding the month with the largest contributor (April 2026), the decline would still be −45.5%
>
> **Comparison to overall Wikipedia:** Czech Wikipedia traffic declined by −12.6% in this period, so intermittent fasting declined much faster than the project average (−53.6% vs −12.6%).
>
> **Limitation:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.
>
> **Detailed report:** [report.html](file://<workspace>/wiki-interest-output/Q1666254_cs-pl_2024-09_2026-08/report.html)

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | pass | every number in `result.json`; views per million read as published (3.08, 5.81) |
| R3 proxy stated | pass | "Přerušovaný půst" |
| R4 warnings and data gaps | pass | Polish has no article |
| R5 limitation | pass | sentence as written |
| R6 report path, R7 (3 calls) | pass | |
| R8 no silent proxy swap | pass | kept Q1666254; no broader item analyzed |
| R10 named languages run directly | pass | no clarifying question |

## Observations

1. "much faster": a size word the skill asks it not to add.
