# Run 20: audience question, turn 2: countries (case 4)

Continues the session of [run 19](19-audiences-scope-turn-1-rerun.md) (`--resume`), SKILL.md 1.5.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Mainly Brazil, Mexico, Turkey and Vietnam." |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.5 (resumed) |
| Turns, time, cost | 3 turns, 28.2 s, $0.050 (includes the resumed context) |
| Permission denials | none |

## Tool calls

1. `resolve --query "learning English" --languages pt es tr vi` → Q130192 "English as a second or
   foreign language" (missing pt, vi), BBC Learning English, Learning English (version of English),
   Simple English Wikipedia, Learning English, Lesson One
2. `analyze --qid Q130192 --languages es tr --topic "learning English" --assumption "English as a second or foreign language article, narrower than general English language learning but the most directly relevant available article"`

Between the two calls the model wrote: "This maps to: Brazil → Portuguese (`pt`), Mexico → Spanish
(`es`), Turkey → Turkish (`tr`), Vietnam → Vietnamese (`vi`). Note: Portuguese and Vietnamese editions of
Wikipedia don't have an article on this topic, so there's no pageview data for Brazil and Vietnam. I'll
analyze Spanish and Turkish, and this gap itself is informative."

## Key `result.json` evidence

| Language | latest 12m | avg / month | growth | whole Wikipedia | per million | share change | months down | warnings |
|---|---|---|---|---|---|---|---|---|
| es | 1,389 | 116 | −52.3 | −20.9 | 0.213 | −39.8 | 12 | none |
| tr | 832 | 69 | −41.7 | −16.3 | 0.637 | −30.3 | 12 | low_volume |

Both `strong`; status `ok`; no top-level warnings (pt and vi were left out of `analyze`).

## Final answer (verbatim)

> ## Proxy and data coverage
>
> I analyzed Wikipedia attention to **"English as a second or foreign language"**—the most directly matched article. However, data is limited:
>
> - **Mexico** (Spanish Wikipedia): Data available
> - **Turkey** (Turkish Wikipedia): Data available  
> - **Brazil** (Portuguese Wikipedia): **No article exists** — no pageview data
> - **Vietnam** (Vietnamese Wikipedia): **No article exists** — no pageview data
>
> The absence of articles in Portuguese and Vietnamese is itself informative: it suggests these communities may not contribute to Wikipedia on this topic.
>
> ## Attention trends
>
> | Language | Views, latest 12m | Change | Whole Wikipedia | Views per million | Share change | Consistency |
> |---|---|---|---|---|---|---|
> | Spanish | 1,389 | −52.3% | −20.9% | 0.213 | −39.8% | Strong |
> | Turkish | 832 | −41.7% | −16.3% | 0.637 | −30.3% | Strong |
>
> **What this shows:** Both Spanish and Turkish speakers show declining Wikipedia interest in English language learning over the past 12 months. Spanish dropped significantly faster (−52.3%) than the overall Spanish Wikipedia (−20.9%), meaning the topic lost share. Turkish declined at −41.7%, also outpacing its platform decline. Every single month in the past year was lower than the same month a year prior—this is a consistent downward trend, not a seasonal dip.
>
> Turkish has a low-volume warning (69 views/month): percentages can swing more on small counts, but the trend direction is clear.
>
> ## Which audiences to investigate next?
>
> The data suggests a challenging picture:
>
> - **Turkey** shows higher per-capita attention (0.637 views per million vs. Spain's 0.213), but smaller absolute volume and a stronger decline.
> - **Mexico/Spain** has higher absolute traffic but steeper year-over-year drops.
> - **Brazil and Vietnam** have no Wikipedia coverage of this topic at all, which could mean either low organic interest *in those communities* or that English learning discussions happen outside Wikipedia (Reddit, YouTube, language-learning platforms, etc.).
>
> **Recommendation:** Before scaling to these markets, test whether the Wikipedia decline reflects a real shift in learner behavior or just a shift *away from Wikipedia*. Consider investigating:
> 1. Whether Brazil and Vietnam learners use other online resources for this topic (non-Wikipedia data)
> 2. Why Spanish and Turkish Wikipedia traffic is falling—has it migrated to other platforms?
> 3. Which of these four regions your actual product usage/demand data shows, rather than relying on Wikipedia alone
>
> The full analysis is available at: `<workspace>/wiki-interest-output/Q130192_es-tr_2024-09_2026-08/report.html`

## Verdict: FAIL (serious: ordering, editions as countries, no limitation)

| Check | Result | Evidence |
|---|---|---|
| Maps Brazil → pt, Mexico → es, Turkey → tr, Vietnam → vi | pass | stated before `analyze`; the answer labels each edition with its country |
| Says editions are not markets and are read beyond the country | **fail** | never said; "Spain's 0.213" for Spanish Wikipedia (the user named Mexico), "Mexico/Spain", "Brazil and Vietnam have no Wikipedia coverage", "these markets" |
| Does not ask again | pass | |
| Search with the user's words | pass | `--query "learning English"` |
| Proxy by meaning, disclosed before figures | pass | Q130192, first in the answer |
| One `analyze` | pass | |
| Top-level and per-language warnings | pass | `low_volume` for Turkish; no other warnings in the JSON; the missing articles named |
| Only numbers and comparisons from the JSON (R2) | **fail** | "Turkey … a stronger decline": Turkish −41.7% against Spanish −52.3% (share −30.3% against −39.8%) is the smaller decline, as the next bullet says; views per million called "per-capita attention" |
| Missing article not read as a signal | **fail** | "itself informative … these communities may not contribute to Wikipedia on this topic"; "could mean … low organic interest in those communities" |
| Pageviews limitation (R5) | **fail** | missing |
| No market ranking (R9) | pass | no language put first; "Before scaling to these markets" is market wording |
| Causal speculation | present | "a shift *away from Wikipedia*", "has it migrated to other platforms?" |
| R6 report path, R7 (2 calls) | pass | |

## Changes triggered

None; stopped for review. Turn 3 (case 6) was not run; the session can still be continued.

After review: recorded as a known limitation of Haiku's free-form synthesis; SKILL.md 1.5 frozen; the session continues in [run 21](21-follow-up-best-market-2.md).
