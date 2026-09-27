# Run 08: missing article, rerun (case 3)

Same prompt as [run 07](07-missing-article-fasting.md), fresh session, SKILL.md 0.7.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.7 |
| Turns, time, cost | 6 turns, 33.2 s, $0.053 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "intermittent fasting" --languages pl,cs` → Q1666254 (missing `pl`), Q44602 Fasting (both)
3. `analyze --qid Q1666254 --languages pl,cs --topic "intermittent fasting" --assumption "Intermittent fasting article exists only in Czech; Polish has no dedicated article on this topic"`
4. `analyze --qid Q44602 --languages pl,cs --topic "fasting" --assumption "Broader article; intermittent fasting has no Polish Wikipedia article"` (not asked for)

## Key `result.json` evidence

- Q1666254: pl `no_article`; cs Přerušovaný půst: 2,198 views, −53.6, whole Wikipedia −12.6, share −47.0,
  3.082 per million, 12 of 12 months down, strong, largest contributor **2026-04** (−85.9), −45.5 without
  it (2026-03 was −51.1).
- Q44602: pl Post 18,026, −17.8, share −9.8, 7.987 per million, 7 down / 5 up, weak, largest contributor
  2026-03 (−68.7), −1.8 without it; cs Půst 7,229, −43.0, share −34.8, 10.136 per million, 11 of 12 down,
  strong, largest contributor 2026-03 (−76.7), −31.1 without it.

## Final answer (verbatim)

> ## Results
>
> **Important note on data availability:** Wikipedia has a dedicated **Intermittent fasting** article only in Czech; Polish has no equivalent article. I'll present the intermittent fasting data for Czech, and as an alternative, the broader **Fasting** article for Polish.
>
> ### Intermittent fasting (Czech only)
>
> The Czech Wikipedia article "Přerušovaný půst" shows a **strong downward trend** in attention.
>
> | Metric | Czech |
> |--------|-------|
> | Latest 12m views (Sept 2025–Aug 2026) | 2,198 |
> | Growth vs. previous 12 months | −53.6% |
> | Views per million (latest 12m) | 3.082 |
> | Topic share growth | −47.0% |
> | Trend consistency | Strong |
>
> Czech Wikipedia's whole-platform views fell −12.6%, but intermittent fasting content declined much faster: topic share shrank −47.0%. All 12 months in the latest period fell year-over-year, with no reversals. March 2026 contributed most to the decline (−85.9% that month), but excluding it the trend remains −45.5%, so the decline does not depend on a single month.
>
> **Polish data unavailable:** Polish Wikipedia has no dedicated article on intermittent fasting.
>
> ---
>
> ### Alternative: Broader fasting topic (both languages)
>
> If you want to compare the broader **Fasting** concept across both languages:
>
> | Metric | Polish | Czech |
> |--------|--------|-------|
> | Latest 12m views | 18,026 | 7,229 |
> | Growth vs. previous 12 months | −17.8% | −43.0% |
> | Views per million (latest 12m) | 7.987 | 10.136 |
> | Topic share growth | −9.8% | −34.8% |
> | Trend consistency | Weak | Strong |
>
> Both languages show declining interest, but the patterns differ. Czech's decline is steeper (−43.0% vs. −17.8%) and more consistent across all months. Polish shows a weak, uneven trend: 7 months fell and 5 grew year-over-year. Without one month (March 2026, which fell −68.7%), Polish's overall change would be nearly flat (−1.8%). Czech's decline of −31.1% persists even without its largest swing month.
>
> **Detailed HTML report:** `<workspace>/wiki-interest-output/Q1666254_cs-pl_2024-09_2026-08/report.html` (intermittent fasting) and `<workspace>/wiki-interest-output/Q44602_cs-pl_2024-09_2026-08/report.html` (fasting).
>
> **Limitation:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: FAIL (one factual error; the case's main behavior now correct)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | **fail** | all 66 numbers are in one of the two `result.json` files, but "March 2026 contributed most … (−85.9%)" attaches the Fasting analysis's month to the intermittent-fasting value; the month is 2026-04 |
| R3 proxy stated | pass | intermittent fasting for Czech; Fasting labelled as an alternative |
| R4 warnings and data gaps | pass | "Polish data unavailable" |
| R5 limitation, no market claims | pass | |
| R6 report path | pass | both reports |
| R7 few tool calls | pass, but | 4; the second `analyze` was not asked for |
| R8 no silent proxy swap | pass | |
| R9 no automatic ranking | pass | |
| Case: report Czech for the requested topic; broader item only as a labelled alternative | pass | |

## Observations

1. SKILL.md 0.7 fixed the proxy handling and the ratios ("−43.0% vs. −17.8%").
2. Running the alternative unasked put two results in context, and a month moved from one to the other.
3. "More consistent across all months" for Czech Fasting (11 of 12) is borderline against the
   "all/every" rule.

## Changes triggered

SKILL.md 0.8 (general): offer a broader alternative, but analyze it only if the user asks; when several
results are in the conversation, take each month and value from the result being described. Not
re-verified on this case (session budget); flagged for review.
