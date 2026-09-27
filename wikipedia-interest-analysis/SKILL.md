---
name: wikipedia-interest-analysis
description: Measures how attention to a topic changes over time from Wikipedia pageviews, in one or several language editions, and writes a shareable HTML report. Use when a user asks how interest in a topic has changed, wants to compare interest in a topic across languages or language Wikipedias, or wants to know which language audiences to look into. Pageviews are a proxy for attention to a topic, not market size, demand or purchase intent.
compatibility: Requires uv (it installs Python 3.12 if missing) and outbound HTTPS to *.wikipedia.org, www.wikidata.org and wikimedia.org. No API keys.
metadata:
  version: "1.5"
---

# Wikipedia interest analysis

You decide what the user means and which Wikipedia article stands for it. The script fetches the data
and computes every number. You never do the arithmetic.

## Command

`SKILL_DIR` is this skill's base directory (the folder that contains this file). Run from the user's
working directory; the outputs are written there.

```
uv run --frozen --project SKILL_DIR python SKILL_DIR/scripts/wiki_interest.py <resolve|analyze> [options]
```

Each command prints one JSON document. Add `--help` after the command to list its options.

## Workflow

1. Identify the topic, the languages and the period. Languages are Wikipedia codes, not country codes
   (`ja` Japanese, `el` Greek, `sv` Swedish, `no` Norwegian); up to 20 per run. The languages come from
   the user, never from Wikipedia size:
   - Languages named: use them.
   - Countries or regions only: map each to its edition where that is straightforward (Brazil →
     `pt`) and say so; if a mapping is ambiguous (India, Switzerland), ask.
   - An audience or cross-language question naming neither: reply with exactly the following text and
     nothing else, then run nothing until the user names or approves languages:
     "I can compare Wikipedia attention across language audiences, but I don't want to invent a market
     shortlist for you. Which 3–10 language audiences are realistically in scope for the product? If
     you don't have a shortlist, tell me the target regions or product constraints and I can help
     narrow one down first."
   - For a single-topic trend question that names no language or audience, use the language of the
     user's message as the default Wikipedia edition and state that assumption.
2. Never guess a QID. Unless an earlier result already gave you one, search with the user's own topic
   words: `resolve --query "<the user's topic words>" --languages <codes>` (add `--pivot-lang <code>`
   if they are not English). Do not broaden, simplify or reinterpret them before you have seen the
   candidates.
3. Choose the candidate whose meaning best matches the user's topic, even if its title uses other words.
   If it has `missing_languages`, still analyze that candidate: the missing languages have no data, and
   you name them. Never replace it with a broader or different candidate because that one exists in
   more languages; you may only offer that one as a clearly labelled alternative, and analyze it only if
   the user asks. Keep the user's words in `--topic`.
4. Analyze:
   `analyze --qid <QID> --languages <codes> --topic "<the user's words>" --assumption "<your proxy choice and why>"`
   The window is 24 months by default: the latest 12 months against the previous 12. `--months N`
   (24 to 120) covers longer periods and `--end-month YYYY-MM` ends earlier. Nothing shorter than
   24 months is possible, because each month is compared with the same month a year earlier.
5. Disclose the proxy before any figures: tell the user which article you used, and say explicitly
   when it is broader, narrower or otherwise imperfect for what they asked.
6. Answer from the JSON the command printed.

## Answer

Answer naturally, and include:
1. The proxy disclosure (workflow step 5) and any country-to-edition mapping, first.
2. The figures. With two or more languages use this table, one row per language, each value copied
   from that language's own result:
   `| Language | Views, latest 12 months | Change | Whole Wikipedia | Views per million | Share change | Consistency | Warnings |`
   (`latest_12m_views`, `growth_pct`, `project_growth_pct`, `latest_topic_views_per_million`,
   `topic_share_growth_pct`, `trend_consistency` with how many of the 12 months moved with the trend,
   warning codes). With one language, give the same figures in a sentence or two.
3. What the figures show: whether the topic moved faster or slower than the whole Wikipedia
   (`growth_pct` against `project_growth_pct`, and `topic_share_growth_pct`), and the evidence in
   `consistency_reasons`. Leave month-by-month detail to the report unless the user asks.
4. If the user asks which audiences or languages to look into: for each dimension that fits their goal
   (attention size: views and views per million; momentum: change and share change; reliability:
   consistency and warnings), say which languages lead, with their values, and leave the choice to the
   user.
5. Every warning, from the top-level `warnings` and from each result's `warnings`, in plain words.
6. This limitation, as written: "Wikipedia pageviews are a proxy for attention to the topic, not market
   size, demand, or purchase intent."
7. The path to the report, `artifacts.report`.

**Before you send it**, check the answer against the JSON: every number, every comparison (higher,
lower, largest, smallest, more, less) and every "all", "every", "none" or "only" must match the values
of the language and result it is about. Rewrite or delete anything that does not.

## Accuracy

- **Numbers** come only from the JSON, each from the language and result it describes; never move a
  value or a month from one to another. Never calculate new numbers (ratios, multiples, differences,
  ranges, rounding): state the values instead ("320 and 116 monthly views", not "2.8× more"). If a
  number the user wants is not there, say so. Add no size words of your own ("slightly", "much").
- **Months** keep their exact month and year; never group them under a label that does not fit all of
  them ("late 2025" for a set that includes a 2026 month).
- **Causes:** the data shows how attention changed, not why. Do not suggest causes (changes to the
  article, editorial shifts, readers moving elsewhere, changes in how people use Wikipedia) unless the
  JSON shows them. Sentences such as "this may reflect…", "people are moving to…" or "the market
  has…" are guesses.
- **Markets:** pageviews are not market size, demand, purchase intent or proof of a commercial
  opportunity, and a language edition is not a country or a market. Never name a "best market"; set
  out the trade-offs against the user's goal. A language without the article has no data, which says
  nothing about demand.
- `trend_consistency` is a rule-based label, not a probability: `strong`, `mixed` and `weak` rate the
  evidence for an upward or downward trend, and `not_applicable` means the change is within ±5%.
  `top_contributor_month` is the month whose
  year-over-year change contributed most to the 12-month change, not necessarily the busiest month.

## Status and warnings

| In the JSON | Tell the user |
|---|---|
| `status: "partial"` | Some languages have no data: name them and report the others. |
| `no_article` | The item has no article in that language. |
| `invalid_language` | Not a Wikipedia language code: fix it and rerun. |
| `missing_months`, `insufficient_data`, `zero_baseline` | Too few complete months to compare. |
| `low_volume` | Small numbers: percentages swing a lot. |
| `possible_history_discontinuity` | Unusually low early months; one possible cause is a new or renamed article. |
| `tracks_platform_trend` | The change mostly mirrors the whole Wikipedia. |
| `spike_driven: true` | The change depends on one month (`top_contributor_month`). |
| `status: "error"` | Explain `error.message` and follow `error.hint`. |

## Follow-ups and the report

Reuse the QID and change only `--languages`, `--months` or `--end-month`; each run writes its own folder.

`report.html` is the canonical shareable output: a self-contained, detailed HTML report that opens
offline and prints to PDF (do not call it interactive). If you can also display or publish a document,
use only numbers from the JSON there and still give the `report.html` path.

Formulas, thresholds and data caveats: [references/methodology.md](references/methodology.md).
