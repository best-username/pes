# Run 13: missing article, regression after consolidation (case 3)

Same prompt as [run 07](07-missing-article-fasting.md), fresh session, consolidated SKILL.md 1.0.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.0 |
| Turns, time, cost | 5 turns, 30.6 s, $0.064 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "intermittent fasting" --languages pl cs` → Q1666254 (missing `pl`), Q44602 Fasting (both)
3. `analyze --qid Q44602 --languages pl cs --topic "fasting" --assumption "Using the 'Fasting' article (Q44602) as the proxy, since the specific 'Intermittent fasting' article only exists in Czech Wikipedia. This broader article captures interest in fasting practices including intermittent fasting."`

## Key `result.json` evidence

Q44602 (the broader item), as in run 07: pl Post 18,026 / −17.8 / −8.8 / 7.987 / −9.8, weak (7 of 12
down), spike-driven (2026-03 −68.7; −1.8 without it); cs Půst 7,229 / −43.0 / −12.6 / 10.136 / −34.8,
strong (11 of 12 down).

## Final answer (verbatim)

> ## Comparison: Fasting article interest in Polish and Czech Wikipedia
>
> **Proxy article:** The "Fasting" article (Wikidata Q44602) — the specific "Intermittent fasting" article only exists in Czech Wikipedia. The proxy articles are "Post" in Polish and "Půst" in Czech.
>
> **Period analyzed:** September 2024 – August 2026 (latest 12 months vs. previous 12 months)
>
> | Language | Views, latest 12 months | Change | Whole Wikipedia | Views per million | Share change | Consistency |
> |---|---|---|---|---|---|---|
> | Polish | 18,026 | −17.8% | −8.8% | 7.987 | −9.8% | Weak |
> | Czech | 7,229 | −43.0% | −12.6% | 10.136 | −34.8% | Strong |
>
> **Key findings:**
>
> Both Polish and Czech Wikipedia show **declining interest in fasting** over the past year, but with very different patterns:
>
> - **Czech shows a steeper decline** (−43.0%) despite having more views per million. The trend is strong, with 11 of 12 months down year-over-year compared to the previous year.
> - **Polish shows a milder decline** (−17.8%), but it's driven largely by a single spike in March 2026 (−68.7% that month). Without that spike, the overall change would be just −1.8%. Only 7 of 12 months are down.
>
> Both languages show **interest declining faster than Wikipedia overall** (share change of −9.8% for Polish and −34.8% for Czech vs. project growth of −8.8% and −12.6%). Both had a positive spike in February 2026, but fasting interest has not sustained momentum.
>
> **Report:** `wiki-interest-output/Q44602_cs-pl_2024-09_2026-08/report.html`
>
> Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: FAIL (regression: broader proxy replaced the requested one)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | pass | 35 numbers, all in `result.json`; no ratios; the parenthetical sets share change beside whole-Wikipedia growth, but the conclusion holds |
| R3 proxy stated | pass | "The 'Fasting' article (Wikidata Q44602)" |
| R4 warnings and data gaps | pass, partly | says the intermittent-fasting article exists only in Czech |
| R5 limitation, no market claims | pass | |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass, narrowly | disclosed |
| Case: keep the requested proxy; Czech data for it; broader item only as a labelled alternative | **fail** | Fasting replaced intermittent fasting in both languages; `--topic` itself was changed to "fasting" |

## Cause

Consolidation dropped SKILL.md 0.7's "never use it as a replacement where the matching article exists"
and softened "still analyze it" to "Keep it". With 0.7 the model kept the requested proxy (run 08).

## Changes triggered

SKILL.md 1.1: the conditional rule restored in workflow step 3, in stronger form. Verified by
[run 14](14-missing-article-regression-2.md).
