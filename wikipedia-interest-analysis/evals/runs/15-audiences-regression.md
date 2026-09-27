# Run 15: audience investigation, regression after consolidation (case 4)

Same prompt as [run 09](09-audiences-learning-english.md), fresh session, SKILL.md 1.1.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.1 |
| Turns, time, cost | 5 turns, 44.1 s, $0.067 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis` (the call's own args: `topic:"English language"`)
2. `resolve --query "English language" --languages es fr de pt zh ja ru hi ar ko it nl pl tr` → Q1860
   "English language" (all 14), Q42365 Old English (all), Q130192 "English as a second or foreign
   language" (missing fr, pt, ja, ru, hi, it, nl, pl), Q7979 British English, Q4135602 Longest word in English
3. `analyze --qid Q1860 --languages es fr de pt zh ja ru hi ar ko it nl pl tr --topic "English language" --assumption "Wikipedia pageviews to the English language article indicate interest and engagement with English across non-English speaking language editions"`

## Key `result.json` evidence

Q1860, 2025-09..2026-08 against 2024-09..2025-08; every language `strong` and down.

| Language | latest 12m | growth | whole Wikipedia | per million | share change | months down | warnings |
|---|---|---|---|---|---|---|---|
| es | 311,543 | −29.1 | −20.9 | 47.688 | −10.4 | 12 | none |
| fr | 190,481 | −19.3 | −10.6 | 26.709 | −9.7 | 11 | none |
| de | 281,719 | −8.0 | −7.3 | 33.304 | −0.7 | 9 | tracks_platform_trend |
| pt | 110,133 | −25.9 | −16.6 | 51.176 | −11.2 | 10 | none |
| zh | 71,478 | −25.7 | −9.6 | 14.535 | −17.7 | 12 | none |
| ja | 436,599 | −14.9 | −4.4 | 41.409 | −11.0 | 12 | none |
| ru | 1,041,461 | −54.3 | −21.7 | 133.177 | −41.6 | 12 | none |
| hi | 46,099 | −42.5 | −42.7 | 237.254 | +0.4 | 12 | tracks_platform_trend |
| ar | 359,290 | −39.0 | −28.4 | 264.316 | −14.7 | 12 | none |
| ko | 91,983 | −37.5 | −25.3 | 134.361 | −16.3 | 12 | none |
| it | 144,251 | −29.5 | −13.0 | 31.413 | −19.0 | 12 | none |
| nl | 38,789 | −17.9 | −7.8 | 31.627 | −11.0 | 11 | none |
| pl | 97,042 | −18.3 | −8.8 | 42.998 | −10.4 | 10 | none |
| tr | 84,960 | −16.5 | −16.3 | 65.063 | −0.2 | 10 | tracks_platform_trend |

## Final answer (verbatim)

> ## Audience recommendations by dimension:
>
> | Language | Views, latest 12m | Change | Views per million | Share change | Consistency |
> |----------|------------------|--------|------------------|--------------|-------------|
> | **Russian** | 1,041,461 | -54.3% | 133,177 | -41.6% | Strong |
> | **Japanese** | 436,599 | -14.9% | 41,409 | -11.0% | Strong |
> | **Spanish** | 311,543 | -29.1% | 47,688 | -10.4% | Strong |
> | **Arabic** | 359,290 | -39.0% | 264,316 | -14.7% | Strong |
> | **German** | 281,719 | -8.0% | 33,304 | -0.7% | Strong |
> | **Portuguese** | 110,133 | -25.9% | 51,176 | -11.2% | Strong |
> | **Chinese** | 71,478 | -25.7% | 14,535 | -17.7% | Strong |
> | **Turkish** | 84,960 | -16.5% | 65,063 | -0.2% | Strong |
> | **Hindi** | 46,099 | -42.5% | 237,254 | +0.4% | Strong |
> | **Korean** | 91,983 | -37.5% | 134,361 | -16.3% | Strong |
> | **Italian** | 144,251 | -29.5% | 31,413 | -19.0% | Strong |
> | **Polish** | 97,042 | -18.3% | 42,998 | -10.4% | Strong |
> | **French** | 190,481 | -19.3% | 26,709 | -9.7% | Strong |
> | **Dutch** | 38,789 | -17.9% | 31,627 | -11.0% | Strong |
>
> ### What this shows:
>
> **Highest absolute engagement:** Russian (1M+ views) and Japanese (437K) lead in raw volume, but Russian's -54.3% decline is severe and consistent across all 12 months, suggesting a sustained shift in how Russian speakers engage with English language content. Japanese remains relatively stable at -14.9%.
>
> **Highest relative interest (per million):** Arabic (264K per million), Hindi (237K per million), and Korean (134K per million) have the strongest interest *relative to their Wikipedia size*. However, Arabic and Hindi are both experiencing steep declines (-39.0% and -42.5%).
>
> **Most resilient markets:** German (-8.0%), Turkish (-16.5%), and Japanese (-14.9%) show the smallest declines — and German's share of Wikipedia traffic is essentially unchanged (-0.7%), suggesting this audience's English interest is stable.
>
> ### Recommendation by goal:
>
> - **For high-volume potential:** Investigate **Japanese** (stable, high views) and **German** (stable, lowest decline). Russian's massive audience is collapsing—understand why before investing there.
> - **For fast-growing/emerging markets:** **Hindi** and **Arabic** show exceptional *interest intensity* (237K–264K per million) even as overall views decline. If they stabilize or reverse, they could offer outsized growth.
> - **For reliable Western expansion:** **German**, **Spanish**, and **French** represent traditional markets with moderate declines and stable regional patterns.
>
> ⚠️ **Important limitation:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.
>
> A detailed report is available at `<workspace>/wiki-interest-output/Q1860_ar-de-es-fr-hi-it-ja-ko-nl-pl-pt-ru-tr-zh_2024-09_2026-08/report.html`.

## Verdict: FAIL (serious)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | **fail** | every views-per-million value 1,000 times too large: "133,177" for 133.177, "264K per million" for 264.316; "437K" rounds 436,599; "relatively stable" and "stable" for strong downward trends (Japanese 12 of 12 months down, German 9 of 12) |
| R3 proxy stated | **fail** | no article is named |
| R4 warnings and data gaps | **fail** | `tracks_platform_trend` for German, Hindi and Turkish not mentioned; the Whole Wikipedia and Warnings columns left out |
| R5 limitation, no market claims | **fail** | the sentence is there, but "Most resilient markets", "before investing there", "fast-growing/emerging markets", "could offer outsized growth", "traditional markets"; causal guess "suggesting a sustained shift in how Russian speakers engage with English language content" |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | **fail** | "learning English" became "English language" in `--query`, `--topic` and the proxy without a word to the user; Q130192 "English as a second or foreign language", listed by `resolve`, was neither chosen nor mentioned |
| R9 no automatic ranking | fail, partly | no best market, and the suggestions are grouped by goal, but languages are called markets and ordered as "most resilient" |
| Case: proxy and shortlist stated as assumptions; proxy chosen by meaning; trade-offs; leads to investigate | **fail** | neither the proxy nor the reason for these 14 languages is given |

## Cause, as far as one run shows

1. The model named the topic "English language" before reading the skill (the Skill call's args) and
   searched for that, so Q1860 came first. In [run 10](10-audiences-learning-english-rerun.md)
   (SKILL.md 0.9) it searched "English language learning" and chose Q130192. SKILL.md 1.1 asks for the
   user's words in `--topic`, not in `--query`.
2. The consolidation folded 0.9's workflow step "Tell the user which article you use as the proxy, and
   say so when it is broader or narrower than what they asked for" into answer item 1; this answer names
   no article.
3. Views per million have three decimals in the JSON. For this proxy they exceed 100 (133.177), which
   reads like a thousands-grouped integer; in runs 09 and 10 they were below 1, and the chess values
   (20.058, run 06) were copied correctly.
4. One run cannot separate the consolidation from run-to-run variation: run 09 (SKILL.md 0.8) also missed
   warnings and used market language.

## Changes triggered

None. The case 6 follow-up and the held-out prompts were conditional on this case passing and were not
run; the fix waits for review.

After review: SKILL.md 1.2: search with the user's own topic words, disclose the proxy as a workflow step, and (script) views per million with two decimals from 1 upward. Verified by [run 16](16-audiences-regression-2.md).
