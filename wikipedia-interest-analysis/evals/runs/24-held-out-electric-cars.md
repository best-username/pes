# Run 24: held-out prompt 1, two-language comparison over three years

Chosen after SKILL.md 1.5 was frozen and never used for tuning. Fresh session.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Has interest in electric cars changed more in Norwegian or Swedish Wikipedia over the last three years?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.5 (frozen) |
| Turns, time, cost | 5 turns, 28.5 s, $0.042 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "electric cars" --languages no,sv` → Q193692 "Electric car"
3. `analyze --qid Q193692 --languages no,sv --topic "electric cars" --months 36` (no `--assumption`)

## Key `result.json` evidence

Window 2023-09..2026-08.

| Language | first 12m → latest 12m | growth | whole Wikipedia | per million | share change | consistency | warnings |
|---|---|---|---|---|---|---|---|
| no "Elbil" | 4,981 → 2,451 (−50.8) | −21.8 (3,133 → 2,451) | +3.5 | 10.62 → 8.03 | −24.4 | mixed: 8 of 12 down | none |
| sv "Elbil" | 5,183 → 4,704 (−9.2) | −5.2 (4,960 → 4,704) | −1.8 | 6.0 → 5.79 | −3.4 | weak: 5 of 12 down; −0.5 without 2026-03, spike-driven | tracks_platform_trend |

## Final answer (verbatim)

> Based on the analysis of Wikipedia pageviews from September 2023 to August 2026:
>
> **Interest in electric cars has changed much more in Norwegian Wikipedia than in Swedish Wikipedia.**
>
> I analyzed the "Elbil" (Electric car) article available in both languages.
>
> | Language | Views, latest 12 months | Change | Whole Wikipedia | Views per million | Share change | Consistency |
> |---|---|---|---|---|---|---|
> | Norwegian | 2,451 | −21.8% | +3.5% | 8.03 | −24.4% | Mixed |
> | Swedish | 4,704 | −5.2% | −1.8% | 5.79 | −3.4% | Weak |
>
> **What this shows:**
>
> Norwegian Wikipedia saw interest decline substantially: views fell 21.8% in the most recent year compared to the previous year, and 50.8% compared to the first year of the 3-year period. Swedish Wikipedia's attention was relatively stable, declining only 5.2% over the latest year and 9.2% over the full 3-year span. 
>
> In Norwegian, the decline was driven by a consistent pattern—8 of the last 12 months saw fewer views than the same month a year earlier. In Swedish, the trend was much weaker: only 5 of 12 months declined, and the overall decline largely depends on March 2026's sharp drop. Without that one month, Swedish would show virtually no change (−0.5%).
>
> **Warning:** Swedish Wikipedia's traffic mirrors platform-wide trends; the decline in electric car attention aligns with a broader 1.8% decline in Swedish Wikipedia overall.
>
> **Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.**
>
> A detailed breakdown by month is available in the report: `wiki-interest-output/Q193692_no-sv_2023-09_2026-08/report.html`

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | `--months 36` for "three years"; `no` as the Norwegian code |
| R2 numbers supported | pass | every number in `result.json`, including the three-year changes (−50.8, −9.2) and views per million above 1 (8.03, 5.79) |
| R3 proxy stated | pass | "Elbil" (Electric car) |
| R4 warnings | pass | `tracks_platform_trend` for Swedish; spike dependence explained; no other warnings |
| R5 limitation, no market claims | pass | sentence as written |
| R6 report path, R7 (3 calls) | pass | |
| R8, R9, R10 | pass | named languages used directly |

## Observations

1. Size words: "much more", "substantially", "much weaker", "sharp drop"; "relatively stable" for a
   −5.2% change.
2. "a consistent pattern" for a `mixed` label (8 of 12 months down).
3. No `--assumption`, so the report lists no assumptions.
