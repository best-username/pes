# Run 10: audience investigation, rerun (case 4)

Same prompt as [run 09](09-audiences-learning-english.md), fresh session, SKILL.md 0.9.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.9 |
| Turns, time, cost | 5 turns, 37.4 s, $0.055 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "English language learning" --languages ja,zh,es,fr,de,ru,pt,ko,it,pl,tr,hi,ar,vi` →
   Q130192 "English as a second or foreign language" missing ja, fr, ru, pt, it, pl, hi, vi
3. `analyze --qid Q130192 --languages zh,es,de,ko,tr,ar --topic "English language learning" --assumption "English as a second or foreign language article, covering how non-native speakers use English"`

## Key `result.json` evidence

| Language | latest 12m | avg / month | growth | per million | share change | consistency | warnings |
|---|---|---|---|---|---|---|---|
| zh | 3,838 | 320 | −35.4 | 0.78 | −28.5 | strong | none |
| es | 1,389 | 116 | −52.3 | 0.213 | −39.8 | strong | none |
| de | 871 | 73 | −32.6 | 0.103 | −27.2 | strong | low_volume |
| ko | — | — | — | — | — | insufficient_data | missing_months (6) |
| tr | 832 | 69 | −41.7 | 0.637 | −30.3 | strong | low_volume |
| ar | 1,086 | 90 | −36.7 | 0.799 | −11.6 | strong | low_volume |

## Final answer (verbatim)

> ## Summary
>
> Based on Wikipedia pageview data (September 2024 to August 2026), here's what the available languages show:
>
> | Language | Avg views/month | Growth (12m) | Views per million | Trend |
> |----------|-----------------|--------------|-------------------|-------|
> | Chinese (Simplified) | 320 | -35.4% | 0.78 | Strong decline |
> | Arabic | 90 | -36.7% | 0.799 | Strong decline |
> | Turkish | 69 | -41.7% | 0.637 | Strong decline |
> | German | 73 | -32.6% | 0.103 | Strong decline |
> | Spanish | 116 | -52.3% | 0.213 | Strong decline |
>
> **The main finding: every language with available data shows a strong, consistent downward trend in attention to this topic over the past 12 months.** The Chinese Wikipedia article receives roughly 3.5× more views monthly than Spanish, which is second in absolute traffic.
>
> ### What this suggests:
>
> **For absolute attention size:** Chinese stands out with 320 average monthly views, followed by Spanish at 116. This tells you where the largest Wikipedia audiences for this topic exist.
>
> **For topic share within each Wikipedia:** Turkish (0.637 views per million) and Arabic (0.799 views per million) show stronger relative attention to English-language learning topics within their respective Wikipedia ecosystems compared to German (0.103 per million).
>
> **Cautions:** All languages show declining interest relative to their own Wikipedia traffic. German, Turkish, and Arabic all have low-volume warnings (small monthly view counts make percentages volatile). Korea's article appears too new for reliable year-over-year comparison.
>
> **Languages without Wikipedia articles on this topic:** Japanese, French, Russian, Portuguese, Italian, Polish, Hindi, and Vietnamese have no dedicated articles—meaning you cannot use Wikipedia pageviews to assess attention in these regions.
>
> Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent. A detailed report is available at `wiki-interest-output/Q130192_ar-de-es-ko-tr-zh_2024-09_2026-08/report.html`.

## Verdict: FAIL (one wrong self-computed ratio)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | one resolve, one analyze |
| R2 numbers supported | **fail** | "roughly 3.5× more views" is the model's own ratio and wrong (320 vs 116 per month); every other number matches |
| R3 proxy stated | pass, partly | the article is named in the table context; the assumption text is not repeated |
| R4 warnings and data gaps | pass | low_volume for de, tr, ar; Korean too new (missing months); all 8 missing languages named |
| R5 limitation, no market claims | pass | sentence as written; no market framing |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass | |
| R9 no automatic ranking | pass | organized by dimension (attention size, topic share), choice left to the user |
| Case: shortlist stated as an assumption | partly | the checked languages can be read off the answer, but why they were chosen is not said |

## Observations

1. SKILL.md 0.9 fixed the warnings, the gaps, the market framing, the ranking and the speculation.
2. The table leaves out share change, whole-Wikipedia growth and the warnings column that the recipe asks
   for; the prose covers the warnings.
3. "Turkish and Arabic show stronger relative attention … compared to German" is true but omits Chinese
   (0.78), which is second on that field.
4. "Chinese (Simplified)": Chinese Wikipedia covers all scripts; the qualifier is the model's own.

## Changes triggered

None applied yet; the ratio habit (runs 04, 07, 10) is listed for review.

After review: SKILL.md 1.0 added a check before sending (every number, comparison and "all"/"none" against the JSON) and consolidated the rules; see runs 13–15.
