# Run 03: multi-language comparison (case 2)

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Compare how interest in chess has changed in German, French and Spanish Wikipedia over the last two years." |
| Model | `claude-haiku-4-5-20251001` |
| Host | Claude Code 2.1.283, print mode, `--setting-sources project --strict-mcp-config --permission-mode dontAsk` |
| Skill installed | yes (loaded through the `Skill` tool) |
| Skill version | SKILL.md 0.3 |
| Turns, time, cost | 5 turns, 23.1 s, $0.040 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `resolve --query "chess" --languages de,fr,es` → first candidate Q718 "Chess", available in all three
3. `analyze --qid Q718 --languages de,fr,es --topic "chess" --assumption "Main Chess article - the traditional board game"`

## Key `result.json` evidence

| Language | Article | growth_pct | project_growth_pct | topic_share_growth_pct | avg / month | months down | consistency |
|---|---|---|---|---|---|---|---|
| de | Schach | −19.7 | −7.3 | −13.3 | 14,139 | 12 of 12 | strong |
| fr | Échecs | −32.4 | −10.6 | −24.4 | 12,056 | 11 of 12 (2025-09 +21.1) | strong |
| es | Ajedrez | −38.2 | −20.9 | −21.9 | 19,504 | 12 of 12 | strong |

No warnings. Report: `<workspace>/wiki-interest-output/Q718_de-es-fr_2024-09_2026-08/report.html`.

## Final answer (verbatim)

> ## Chess Interest Across Three Languages: Strong Decline Across the Board
>
> I analyzed the Chess article ("Schach" in German, "Échecs" in French, "Ajedrez" in Spanish) across German, French, and Spanish Wikipedia from September 2024 to August 2026.
>
> **All three languages show consistent declines in chess article pageviews:**
>
> - **German Wikipedia (de)**: −19.7% decline
>   The article averaged 14,139 views per month in the latest 12 months. All 12 months of the latest period had fewer views than the same month a year earlier.
>
> - **French Wikipedia (fr)**: −32.4% decline
>   The article averaged 12,056 views per month. Only September 2025 showed positive year-over-year growth (+21.1%); the other 11 months were all down, with July 2026 showing the largest drop (−69.5%).
>
> - **Spanish Wikipedia (es)**: −38.2% decline
>   The steepest drop overall, averaging 19,504 views per month. Every month in the latest 12 showed year-over-year decline, with November 2025 experiencing the largest proportional drop (−65.8%).
>
> **Context:** The entire Wikipedia in these languages also declined—German by 7.3%, French by 10.6%, and Spanish by 20.9%—but chess interest fell faster in each case. When adjusted for platform-wide trends, Spanish Wikipedia's chess article lost the most audience share (−21.9%), followed by French (−24.4%) and German (−13.3%).
>
> All three trends are **strong and consistent** (all show downward movement in 9+ months) and not driven by single-month spikes.
>
> **Detailed report:** `<workspace>/wiki-interest-output/Q718_de-es-fr_2024-09_2026-08/report.html`
>
> **Note:** Wikipedia pageviews measure attention on the platform, not overall interest in chess or any market metric. The decline across all three editions may reflect broader changes in Wikipedia usage patterns or editorial shifts rather than declining interest in the game itself.

## Verdict: FAIL (factual error)

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | resolve + one analyze for all three languages |
| R2 numbers supported | **fail** | all 41 numbers appear in `result.json`, but the share ranking is wrong: French lost the most share (−24.4), then Spanish (−21.9), then German (−13.3); the answer puts Spanish first |
| R3 proxy stated | pass | the Chess article, with each language's title |
| R4 warnings | n/a | none |
| R5 limitation, no market claims | pass, with a problem | no market claims; the note says pageviews are "not overall interest in chess" and speculates about causes |
| R6 report path | pass | |
| R7 few tool calls | pass | 3 |
| R8 no silent proxy swap | pass | |
| R9 no automatic ranking | pass | no audience ranking; the wrong ordering is a factual error (R2) |
| Case: one analyze call; raw, whole-Wikipedia and share compared | pass | |

## Observations

1. Factual error: the share-change ordering reuses the raw-growth ordering (Spanish steepest on
   `growth_pct`, but not on `topic_share_growth_pct`).
2. Unsupported causal claim, against SKILL.md 0.3's rule: "may reflect broader changes in Wikipedia usage
   patterns or editorial shifts rather than declining interest in the game itself". The data
   contradicts it: the topic's share fell in all three languages.
3. The over-hedged limitation came back: "not overall interest in chess".
4. Correct and useful: per-language extremes (France 2025-09 +21.1, 2026-07 −69.5; Spain 2025-11 −65.8)
   match the JSON.

## Changes triggered

SKILL.md 0.4 (general, not topic-specific):
- For two or more languages, put the per-language fields in a table copied from the JSON; compare a
  field only by that field's values (the most negative is the largest decline).
- The limitation is given as a sentence to use as written.
- The causes rule is restated with a data-based alternative: use `project_growth_pct` and
  `topic_share_growth_pct` for context instead of guessing why attention changed.

Verified by the rerun, [run 04](04-multi-language-chess-rerun.md).
