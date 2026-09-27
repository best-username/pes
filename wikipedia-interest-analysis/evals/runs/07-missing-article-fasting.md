# Run 07: missing article in a requested language (case 3)

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare growth of interest in intermittent fasting in Polish and Czech Wikipedia." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.6 |
| Turns, time, cost | 5 turns, 25.4 s, $0.040 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "intermittent fasting" --languages pl,cs` →
   Q1666254 "Intermittent fasting": available `cs`, missing `pl`; Q44602 "Fasting": available `pl`, `cs`
3. `analyze --qid Q44602 --languages pl,cs --topic "intermittent fasting" --assumption "Using 'Fasting' article as proxy since dedicated intermittent fasting article missing in Polish Wikipedia; this is broader than intermittent fasting alone"`

## Key `result.json` evidence (Q44602 Fasting, not the requested topic)

| Language | Article | latest 12m views | growth | whole Wikipedia | share change | months down | consistency |
|---|---|---|---|---|---|---|---|
| pl | Post | 18,026 | −17.8 | −8.8 | −9.8 | 7 of 12 | weak, spike-driven (2026-03 −68.7; −1.8 without it) |
| cs | Půst | 7,229 | −43.0 | −12.6 | −34.8 | 11 of 12 | strong |

Both peak in 2026-02 (pl +108.6 year over year); the Polish series is dominated by a February/March swing.

## Final answer (verbatim)

> ## Comparison: Interest in Fasting (Polish vs Czech Wikipedia)
>
> I'm using the broader "Fasting" article as a proxy, since the dedicated "Intermittent fasting" article exists only in Czech Wikipedia. The Polish data represents general fasting interest, which is broader than intermittent fasting specifically.
>
> | Language | Latest 12m views | Growth | Project growth | Topic share growth | Trend consistency |
> |----------|------------------|--------|----------------|-------------------|------------------|
> | Polish | 18,026 | -17.8% | -8.8% | -9.8% | Weak |
> | Czech | 7,229 | -43.0% | -12.6% | -34.8% | Strong |
>
> **Volume and trends:** Polish Wikipedia shows 18,026 views in the latest 12 months (September 2025–August 2026) versus Czech's 7,229 views—Polish has 2.5 times more traffic. Both languages show declining interest: Polish dropped 17.8% year-over-year, while Czech declined 43.0%, more than double the rate.
>
> **How they compare to their Wikipedias:** Polish fasting interest declined faster than Polish Wikipedia overall (-8.8%), losing 9.8% of its share of Wikipedia traffic. Czech's decline was much steeper—it fell 43.0% while Czech Wikipedia declined only 12.6%, meaning fasting's share of Czech Wikipedia dropped 34.8%.
>
> **Consistency of the decline:** Czech shows a **strong** downward trend: 11 of its 12 months declined year-over-year, and this decline would persist even without its highest-impact month (March 2026). Polish shows a **weak** trend: only 7 of 12 months declined, and without March 2026—where it dropped 68.7%—the overall change would shrink to -1.8%, so Polish's decline depends heavily on that single month.
>
> **Most-viewed month:** Both languages peaked in February 2026, though both then declined sharply in March 2026.
>
> See the detailed report: `<workspace>/wiki-interest-output/Q44602_cs-pl_2024-09_2026-08/report.html`
>
> **Important:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: FAIL (proxy replaced where the requested article exists; own ratios)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | **fail** | "2.5 times more traffic" and "more than double the rate" are the model's own ratios; all other values match |
| R3 proxy stated | pass | "the broader 'Fasting' article as a proxy" |
| R4 warnings and data gaps | pass, partly | says the intermittent-fasting article exists only in Czech |
| R5 limitation, no market claims | pass | |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass, narrowly | the swap is disclosed, not silent |
| R9 no automatic ranking | pass | |
| Case: report Czech for the requested topic; broader item only as a labelled alternative | **fail** | the requested topic was replaced by Fasting in both languages, including Czech, where its article exists; the choice follows language coverage, which SKILL.md says is not a reason |

## Observations

1. The model read `missing_languages` correctly, then optimized for coverage.
2. The broader proxy changes what is measured: the Polish "Post" series is dominated by a
   February/March swing (weak, spike-driven), unrelated to intermittent fasting.
3. Own ratios despite the numbers rule ("2.5 times", "more than double").

## Changes triggered

SKILL.md 0.7 (general):
- Workflow: if the matching candidate is missing in some requested languages, analyze it for all
  requested languages (the missing ones come back as `no_article`); a broader candidate may be offered
  only as a separate, labelled alternative, never as a replacement where the matching article exists.
- Numbers rule: compare two values by stating both; never as a ratio or multiple.

Verified by [run 08](08-missing-article-fasting-rerun.md).
