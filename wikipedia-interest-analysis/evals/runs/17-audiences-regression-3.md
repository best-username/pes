# Run 17: audience investigation, third regression run (case 4)

Same prompt as [run 09](09-audiences-learning-english.md), fresh session, SKILL.md 1.3: 1.2 with 0.9's
warning line restored ("Every warning, from the top-level `warnings` and from each result's
`warnings`, in plain words").

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.3 |
| Turns, time, cost | 5 turns, 41.1 s, $0.057 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "English as a second language" --languages es,fr,de,pt,zh,ja,ko,ru,ar,hi,vi,th,id,tr,pl`
   → Q130192 "English as a second or foreign language" (missing fr, pt, ja, ru, hi, vi, th, pl), then
   Teaching English as a second or foreign language, two unrelated items, Q1860 English language
3. `analyze --qid Q130192 --languages es,de,zh,ko,ar,id,tr --topic "learning English" --assumption "Wikipedia pageviews on 'English as a second or foreign language' as a proxy for audience attention to English learning"`

## Key `result.json` evidence

| Language | avg / month | growth | whole Wikipedia | per million | share change | months down | warnings |
|---|---|---|---|---|---|---|---|
| zh | 320 | −35.4 | −9.6 | 0.78 | −28.5 | 11 | none |
| es | 116 | −52.3 | −20.9 | 0.213 | −39.8 | 12 | none |
| de | 73 | −32.6 | −7.3 | 0.103 | −27.2 | 11 | low_volume |
| ar | 90 | −36.7 | −28.4 | 0.799 | −11.6 | 9 | low_volume |
| tr | 69 | −41.7 | −16.3 | 0.637 | −30.3 | 12 | low_volume |
| ko, id | — | — | — | — | — | — | missing_months |

All five usable languages are `strong`; status `partial`.

## Final answer (verbatim)

> ## Proxy disclosure
> I analyzed Wikipedia pageviews on the article **"English as a second or foreign language"** as a proxy for audience attention to learning English. However, this article doesn't exist in 8 of the 15 languages I checked (French, Portuguese, Japanese, Russian, Hindi, Vietnamese, Thai, Polish), which limits our sample.
>
> ## Results summary
>
> | Language | Views per month | Change (latest vs previous 12m) | Views per million | Trend |
> |---|---|---|---|---|
> | **Chinese** | 320 | -35.4% | 0.78 | Strong decline |
> | **Spanish** | 116 | -52.3% | 0.213 | Strong decline |
> | **Arabic** | 90 | -36.7% | 0.799 | Strong decline |
> | **Turkish** | 69 | -41.7% | 0.637 | Strong decline |
> | **German** | 73 | -32.6% | 0.103 | Strong decline |
>
> Korean and Indonesian articles had insufficient historical data for comparison.
>
> ## What the data shows
>
> **All measured audiences show declining attention**, and all are declining faster than their overall Wikipedia growth rates (topic share declining -11.6% to -39.8%), suggesting losing relative interest compared to other topics in those language communities.
>
> **By dimension:**
> - **Largest audience size**: Chinese dominates with 320 monthly views (2.7–4.6× higher than others)
> - **Highest relative interest** (per million speakers): Arabic (0.799) and Turkish (0.637) show more concentrated attention in their language communities 
> - **Most stable trend**: German shows the mildest decline at -32.6%, while Spanish shows the steepest at -52.3%
>
> ## My recommendation
>
> **Investigate Chinese** if you're after absolute audience size and potential market reach. **Investigate Arabic and Turkish** if you want concentrated interest from engaged audiences. However, the universal decline across all languages suggests this may not be a growing search area on Wikipedia—consider whether your user base searches elsewhere (Google, educational platforms, social media) for learning resources. 
>
> The **missing languages are a data gap worth exploring**: France, Brazil, Japan, Russia, and India don't have dedicated Wikipedia articles on this topic, which might indicate different informational patterns or opportunities in those markets.
>
> Full analysis: `<workspace>/wiki-interest-output/Q130192_ar-de-es-id-ko-tr-zh_2024-09_2026-08/report.html`

## Verdict: FAIL (serious: warnings, numbers, markets, limitation)

| Check | Result | Evidence |
|---|---|---|
| Correct semantic proxy | pass | Q130192 |
| Search starts from the user's words | **fail** | searched "English as a second language" for "learning English"; the proxy came out right |
| Proxy disclosed | pass | "## Proxy disclosure", with the eight languages that lack the article |
| Numbers and orderings (R2) | **fail** | own ratios "2.7–4.6× higher" (320 / 116 is 2.76); "Highest relative interest … Arabic (0.799) and Turkish (0.637)" passes over Chinese (0.78); views per million called "per million speakers"; own range "-11.6% to -39.8%" |
| All warnings surfaced (R4) | **fail** | `low_volume` for German, Arabic and Turkish not mentioned, although Arabic and Turkish are recommended; the missing months for Korean and Indonesian are mentioned |
| No market ranking | fail, partly | recommendations per goal, but "potential market reach" |
| No language edition = market (R5) | **fail** | "France, Brazil, Japan, Russia, and India don't have dedicated Wikipedia articles … opportunities in those markets" |
| Limitation (R5) | **fail** | no limitation; every fresh run since run 04 quoted the sentence word for word |
| Causal speculation | present | "consider whether your user base searches elsewhere (Google, educational platforms, social media)" |
| R1, R6, R7 (3 calls) | pass | |

## Observations

1. The table leaves out whole-Wikipedia change, share change and warnings.
2. The failures differ from those of runs 15 and 16 on nearly the same text: the rules broken here
   (limitation, the "320 and 116, not 2.8×" example) were followed in earlier runs.

## Changes triggered

None. Case 6 and the held-out prompts were not run; stopped for review.

After review: no further wording for this failure; SKILL.md 1.4 changed the behavior instead: an audience question with no scope now gets a clarifying question, and case 4 became three turns ([run 18](18-audiences-scope-turn-1.md)).
