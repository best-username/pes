# Run 25: held-out prompt 2, single-topic trend with no language

Chosen after SKILL.md 1.5 was frozen and never used for tuning. Fresh session. It exercises the rule for
a single-topic trend question that names no language.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "How has interest in the Rust programming language changed over the last two years?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.5 (frozen) |
| Turns, time, cost | 5 turns, 23.8 s, $0.039 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "Rust programming language" --languages en` → Q575650 "Rust (programming language)"
3. `analyze --qid Q575650 --languages en --topic "Rust programming language" --assumption "Using the English Wikipedia article on Rust as a proxy for global interest in the language"`

## Key `result.json` evidence

en "Rust (programming language)": 696,388 → 662,396 views, growth −4.9, whole Wikipedia −7.0, 7.99 →
8.17 views per million, share change +2.3, trend `flat` (`not_applicable`), 6 months up and 6 down,
median year-over-year +2.3, largest month 2025-12 (11.7% of the year), year-over-year from −34.2
(2025-09) to +29.2 (2025-12), no warnings.

## Final answer (verbatim)

> ## Interest in Rust: Flat Over the Last Two Years
>
> **Proxy used:** The English Wikipedia article "Rust (programming language)" — a general-purpose programming language article. This captures interest in the language itself across an English-reading audience globally.
>
> **The overview:** Interest in Rust on Wikipedia was essentially flat over the past 24 months (September 2024 to August 2026). The article received 662,396 views in the latest 12 months (September 2025–August 2026), down 4.9% from the previous 12 months (696,388 views). However, this slight decline was slower than Wikipedia's overall traffic, which fell 7.0%, so Rust's share of Wikipedia attention actually grew by 2.3%.
>
> **Month-by-month pattern:** There's no clear trend. Exactly 6 months showed year-over-year growth and 6 showed declines. The largest month was December 2025 (11.7% of the year's views). The year-over-year changes ranged from −34.2% (September 2025) to +29.2% (December 2025), but the median was +2.3%, showing the year-to-year swings balance out.
>
> **What this means:** Within the limits of Wikipedia pageviews as a proxy, interest in Rust remained steady over this period — no acceleration or decline. The language held its ground while Wikipedia traffic overall contracted.
>
> See the detailed report at `<workspace>/wiki-interest-output/Q575650_en_2024-09_2026-08/report.html` for month-by-month breakdown.
>
> **Limitation:** Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase intent.

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | pass | every number in `result.json`; the lowest and highest months are the true extremes |
| R3 proxy stated | pass | "Rust (programming language)" on English Wikipedia |
| R4 warnings | pass | none in the JSON |
| R5 limitation | pass | sentence as written |
| R6 report path, R7 (3 calls) | pass | |
| R8 no silent proxy swap | pass | the ambiguous word resolved to the programming language, as the user said |
| R10 default edition | pass | English, the language of the message, stated as the proxy's edition |

## Observations

1. It does not say that English was chosen because no language was named; the `--assumption` calls it
   "a proxy for global interest", which overstates what one edition covers (the answer says
   "English-reading audience").
2. "slight decline": a size word.
