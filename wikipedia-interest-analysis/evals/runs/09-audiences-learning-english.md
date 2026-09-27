# Run 09: ambiguous proxy, audience investigation (case 4)

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 0.8 |
| Turns, time, cost | 5 turns, 36.5 s, $0.051 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "English language learning" --languages es fr de ja zh pt ru it pl tr` →
   Q130192 "English as a second or foreign language" (available es, de, zh, tr; missing fr, ja, pt, ru, it,
   pl); Q2876734 "BBC Learning English"; Q17081060 "English-language learner" (no articles);
   Q1194674 "Computer-assisted language learning"; Q27968 "English studies" (8 of 10)
3. `analyze --qid Q130192 --languages es de zh tr --topic "English language learning" --assumption "Using 'English as a second or foreign language' as a proxy for learning English" --months 36`

## Key `result.json` evidence

| Language | latest 12m views | growth | whole Wikipedia | per million | share change | consistency | warnings |
|---|---|---|---|---|---|---|---|
| es | 1,389 | −52.3 | −20.9 | 0.213 | −39.8 | strong (12 of 12) | none |
| de | 871 | −32.6 | −7.3 | 0.103 | −27.2 | strong (11 of 12) | **low_volume** (73 per month) |
| zh | 3,838 | −35.4 | −9.6 | 0.78 | −28.5 | strong (11 of 12) | none |
| tr | 832 | −41.7 | −16.3 | 0.637 | −30.3 | strong (12 of 12) | **low_volume** (69 per month) |

## Final answer (verbatim)

> ## Key Findings
>
> I analyzed attention to "English as a second or foreign language" across the four available languages from September 2023 to August 2026. **Important caveat:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.
>
> | Language | Latest 12m views | Growth | Project growth | Topic share growth |
> |---|---|---|---|---|
> | Spanish | 1,389 | -52.3% | -20.9% | -39.8% |
> | Chinese | 3,838 | -35.4% | -9.6% | -28.5% |
> | German | 871 | -32.6% | -7.3% | -27.2% |
> | Turkish | 832 | -41.7% | -16.3% | -30.3% |
>
> **What this shows:** All four languages show strong downward trends. Spanish has the steepest decline (-52.3%), while Chinese's decline is more moderate (-35.4%) but from a much higher base (3,838 views vs. 1,389 for Spanish). Importantly, in all four languages, the topic declined **faster than Wikipedia as a whole**, suggesting people are moving away from Wikipedia to learn about English language learning specifically.
>
> ## Recommendation for Next Audiences
>
> Given the data gaps and the broader context, I'd prioritize investigating these audiences next:
>
> 1. **French and Japanese** — These are major language markets conspicuously absent from Wikipedia coverage of this topic. The missing articles may indicate either underserved communities or platforms where they're already getting language learning content elsewhere (like apps or dedicated platforms).
>
> 2. **Portuguese and Russian** — Similar gap; Brazil and Russia are large populations where English learning is relevant.
>
> 3. **Re-examine the available languages with a different metric** — The Wikipedia decline may reflect a shift in *where* people learn English (toward apps like Duolingo, YouTube, or dedicated platforms) rather than *whether* they're learning. Low Wikipedia traffic doesn't equal low market demand.
>
> **A better next step:** Rather than adding more languages to this Wikipedia analysis, consider surveying which platforms and products these audiences actually use for English learning. Wikipedia attention is declining everywhere—that might tell you the market has matured and moved to dedicated tools.
>
> View the detailed HTML report here: `<workspace>/wiki-interest-output/Q130192_de-es-tr-zh_2023-09_2026-08/report.html`

## Verdict: FAIL

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | one resolve, one analyze |
| R2 numbers supported | pass | 42 numbers, all in `result.json` |
| R3 proxy stated | pass | chose by meaning (not "English studies", available in 8 of 10) |
| R4 warnings and data gaps | **fail** | `low_volume` for de and tr not mentioned; Italian and Polish omitted from the gaps |
| R5 limitation, no market claims | **fail** | "major language markets", "large populations", "the market has matured" |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass | |
| R9 no automatic ranking | **fail** | a prioritized audience list built on missing articles and population, not on the data |
| Case: shortlist and proxy stated as assumptions | **fail**, partly | proxy stated; the 10-language shortlist never stated |
| Rule: no causal speculation | **fail** | "people are moving away from Wikipedia", "shift … toward apps like Duolingo" |

## Changes triggered

SKILL.md 0.9 (general):
- The table gets a warnings column (codes such as `low_volume`), so warnings cannot be skipped.
- Workflow: when the user did not name languages, say which languages you checked and why; languages
  `resolve` shows as missing may be left out of `analyze`, but every one is named as having no article.
- A recipe for "which audiences" questions: per dimension that fits the user's goal (attention size,
  momentum, reliability) say which languages lead, with values, and leave the choice to the user; a
  missing article means no data, not a signal of demand or an underserved market.
- Red-flag phrases for the causes rule ("this may reflect…", "people are moving to…", "the market has…").

Verified by [run 10](10-audiences-learning-english-rerun.md).
