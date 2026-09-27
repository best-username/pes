# Run 16: audience investigation, second regression run (case 4)

Same prompt as [run 09](09-audiences-learning-english.md), fresh session, SKILL.md 1.2: searches with
the user's own topic words, discloses the proxy as a workflow step, and publishes views per million
with two decimals from 1 upward and three below 1.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.2 |
| Turns, time, cost | 5 turns, 36.0 s, $0.051 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "English language learning" --languages es,fr,de,ja,ru,zh,pt,it,ko,ar,nl,pl` →
   Q130192 "English as a second or foreign language" (missing fr, ja, ru, pt, it, nl, pl), then BBC
   Learning English, Computer-assisted language learning, English-language learner (missing all 12),
   Teaching English as a second or foreign language
3. `analyze --qid Q130192 --languages es,de,zh,ko,ar --topic "English language learning"` (no `--assumption`)

## Key `result.json` evidence

| Language | latest 12m | avg / month | growth | whole Wikipedia | per million | share change | months down | warnings |
|---|---|---|---|---|---|---|---|---|
| zh | 3,838 | 320 | −35.4 | −9.6 | 1.09 → 0.78 | −28.5 | 11 | none |
| es | 1,389 | 116 | −52.3 | −20.9 | 0.353 → 0.213 | −39.8 | 12 | none |
| de | 871 | 73 | −32.6 | −7.3 | 0.142 → 0.103 | −27.2 | 11 | low_volume |
| ko | — | — | — | — | — | — | — | missing_months |
| ar | 1,086 | 90 | −36.7 | −28.4 | 0.904 → 0.799 | −11.6 | 9 | low_volume |

All four usable languages are `strong`; status `partial`.

## Final answer (verbatim)

> ## Results
>
> **Proxy disclosure:** I analyzed the Wikipedia article "English as a second or foreign language" (a direct match for your topic) across languages where it exists. Seven of your target languages—French, Japanese, Russian, Portuguese, Italian, Dutch, and Polish—have no article under this title, so they can't be measured with this proxy. Korean's article has insufficient pageview data (missing months). Chinese, Spanish, German, and Arabic had complete data.
>
> | Language | Views, latest 12 months | Change | Whole Wikipedia | Views per million | Share change | Consistency |
> |---|---|---|---|---|---|---|
> | Chinese | 3,838 | −35.4% | −9.6% | 0.78 | −28.5% | Strong |
> | Spanish | 1,389 | −52.3% | −20.9% | 0.213 | −39.8% | Strong |
> | Arabic | 1,086 | −36.7% | −28.4% | 0.799 | −11.6% | Strong |
> | German | 871 | −32.6% | −7.3% | 0.103 | −27.2% | Strong |
>
> ## What the data shows
>
> All four measurable audiences show declining pageviews. Spanish and Chinese fall faster than their whole Wikipedia (−52.3% and −35.4% vs −20.9% and −9.6%), suggesting the topic is losing ground. Chinese remains the largest audience by views (320 monthly average), while Arabic holds the highest per-million share (0.799) but that share shrank only −11.6%—the most resilient of the four.
>
> ## Which audiences to investigate next
>
> **By size/attention:** Chinese dominates with 320 monthly views and higher per-million traffic (0.78) than Spanish (116 views, 0.213 per million). If your goal is absolute audience scale, Chinese is the clear lead.
>
> **By momentum/resilience:** Arabic shows the smallest relative decline in topic share (−11.6% vs −27% to −40% in others). This matters if declining Wikipedia interest reflects a broader platform shift rather than genuine disinterest in English learning—Arabic readers may be switching channels less.
>
> **Missing from this analysis:** French, Portuguese, Russian, and Japanese Wikipedia editions don't have comparable articles available, so I cannot measure them. These are significant language groups (especially French and Portuguese, which span multiple continents). A product considering French or Portuguese audiences should investigate through other signals—search trends, language-learning platform usage, enrollment data—since this Wikipedia proxy doesn't cover them.
>
> **Important limitation:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.
>
> See the detailed report: `wiki-interest-output/Q130192_ar-de-es-ko-zh_2024-09_2026-08/report.html`

## Verdict: FAIL (the two core failures of run 15 are fixed; warnings missed, one invented cause)

| Check | Result | Evidence |
|---|---|---|
| Search starts from the user's words | pass | "English language learning" for "learning English": reworded, not broadened |
| Proxy defensible by meaning | pass | Q130192, the first candidate; not replaced by a better-covered item |
| Proxy disclosed | pass | "Proxy disclosure: … 'English as a second or foreign language'"; "a direct match" overstates it slightly |
| No silent substitution | pass | the seven languages without the article are named |
| Views per million read correctly | pass | 0.78, 0.213, 0.799, 0.103, as in `result.json` |
| Warnings surfaced (R4) | **fail** | `low_volume` for German (73 views a month) and Arabic (90) not mentioned, although Arabic is put forward as "the most resilient"; Warnings column left out; Korean's missing months and the missing articles are mentioned |
| No invented causes | **fail** | "if declining Wikipedia interest reflects a broader platform shift … Arabic readers may be switching channels less" |
| No language edition = market | pass | "French and Portuguese, which span multiple continents" is outside knowledge, not taken from the data |
| No unsupported ranking | pass | leaders given per goal ("If your goal is absolute audience scale"), with values |
| No own ratios, correct orderings (R2) | pass, partly | every ordering checks out; "−27% to −40% in others" is its own rounded range of −27.2, −28.5 and −39.8 |
| R1, R5 (limitation), R6, R7 (3 calls) | pass | |

## Observations

1. "Seven of your target languages": the model chose the 12 languages itself and did not say why.
2. `--assumption` was not passed, so `assumptions` is empty in `result.json` and the report.
3. The table has no months-with-the-trend counts.

## Cause, as far as the runs show

SKILL.md 0.9 said "Every warning, from the top-level `warnings` and from each result's `warnings`, in
plain words"; the consolidation (1.0) cut it to "Every warning, in plain words". Both case 4 runs since
then (15 and 16) missed per-language warnings while mentioning the top-level ones; with 0.9
([run 10](10-audiences-learning-english-rerun.md)) all `low_volume` warnings were surfaced. Invented
causes recur despite the explicit rule (runs 09, 15, 16).

## Changes triggered

None; waiting for review. The case 6 follow-up was not run, because it depends on this case passing.

After review: SKILL.md 1.3: 0.9's warning line restored. Verified by [run 17](17-audiences-regression-3.md).
