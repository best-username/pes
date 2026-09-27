# Run 01: single-language trend (case 1)

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "How has interest in astronomy changed in Ukrainian Wikipedia over the last two years?" |
| Model | `claude-haiku-4-5-20251001` |
| Host | Claude Code 2.1.283, print mode, `--setting-sources project --strict-mcp-config --permission-mode dontAsk` |
| Skill installed | yes: project skill, listed in the `init` event, loaded by the model through the `Skill` tool |
| Skill version | SKILL.md 0.1 (first draft) |
| Turns, time, cost | 5 turns, 24.4 s, $0.038 (as reported by Claude Code) |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `uv run --frozen --project <skill> python <skill>/scripts/wiki_interest.py resolve --query "astronomy" --languages uk`
   → first candidate Q333 "Astronomy" (available in `uk`)
3. `uv run --frozen --project <skill> python <skill>/scripts/wiki_interest.py analyze --qid Q333 --languages uk --topic "astronomy" --assumption "The main Astronomy article, the standard proxy for the field"`

`<skill>` = `<workspace>/.claude/skills/wikipedia-interest-analysis`.

## Key `result.json` evidence

| Field | Value |
|---|---|
| status, warnings | `ok`, none |
| period | 2024-09..2026-08 (previous 12: 2024-09..2025-08, latest 12: 2025-09..2026-08) |
| article | Астрономія (uk) |
| previous / latest 12m views | 16,614 / 6,708 |
| growth_pct | −59.6 |
| project_growth_pct | −24.6 |
| topic views per million | 18.454 → 9.886 |
| topic_share_growth_pct | −46.4 |
| negative_yoy_months | 11 |
| yoy 2026-07 / 2026-08 | +5.6 / −4.0 |
| top_contributor_month, growth_excl_top_month_pct | 2025-09, −57.5 |
| trend_direction, trend_consistency, spike_driven | down, strong, false |
| report | `<workspace>/wiki-interest-output/Q333_uk_2024-09_2026-08/report.html` (13,498 bytes) |

## Final answer (verbatim)

> Interest in astronomy on Ukrainian Wikipedia has **declined significantly** over the last two years.
>
> ## Key findings
>
> **Article analyzed:** The main Astronomy article ("Астрономія") in Ukrainian Wikipedia
>
> **The trend:**
> - The latest 12 months (Sep 2025–Aug 2026) received **59.6% fewer views** than the previous 12 months (Sep 2024–Aug 2025)
> - Views fell from 16,614 in the earlier period to 6,708 in the latest period
> - This is a **strong downward trend**: 11 out of 12 months showed year-over-year declines
>
> **Context:**
> - While Ukrainian Wikipedia overall declined 24.6%, astronomy content declined much more steeply, losing 46.4% of its relative share on the platform
> - The decline is not driven by a single spike—even excluding the highest month, the trend would still be −57.5%
> - A small uptick appeared in July 2026 (+5.6%), but this was not sustained
>
> ## Limitations to keep in mind
>
> Wikipedia pageviews measure attention to an article, not actual market demand, purchase intent, or real-world interest in astronomy as a field. The views show what Ukrainian speakers were reading on that Wikipedia article specifically. The article itself may have changed in scope, or readers may have shifted to other sources (including other Wikipedia language editions or the web more broadly).
>
> **Full report:** `<workspace>/wiki-interest-output/Q333_uk_2024-09_2026-08/report.html`

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands, no replacement code or scraping | pass | only `resolve` and `analyze`; no web or file-writing attempts |
| R2 numbers supported by `result.json` | pass | 32 numbers in the answer, all found in `result.json` (checked by script, then by hand for +5.6) |
| R3 proxy stated | pass | "The main Astronomy article ("Астрономія")" |
| R4 warnings and data gaps | n/a | `result.json` has no warnings |
| R5 limitation, no market claims | pass | limitation paragraph; explicitly not demand or purchase intent |
| R6 report path | pass | absolute path to `report.html` |
| R7 few tool calls | pass | 3 (Skill, resolve, analyze) |
| R8 no silent proxy swap | pass | the requested topic's own article |
| R9 no automatic ranking | n/a | single language |
| Case: QID from resolve, 24 months, whole-Wikipedia context | pass | all present |

## Observations

1. Misread evidence: "excluding the highest month" describes 2025-09, which is the month whose drop from
   a year earlier contributed most (its year-earlier month, 2024-09, was the window's peak), not the
   latest year's highest month. The −57.5% itself is correct.
2. The limitation over-hedges: "not ... real-world interest in astronomy as a field" undercuts the
   skill's premise that pageviews are a proxy for interest in the topic.
3. Speculative causes ("the article may have changed in scope", "readers may have shifted to other
   sources") are not in the data; they are hedged as possibilities.
4. The QID (Q333) was not mentioned; the article name identifies the proxy.

## Changes triggered

General wording fixes, verified by [run 02](02-single-language-astronomy-uk-rerun.md):
- `consistency_reasons` now says "without 2025-09 — the month whose year-over-year change contributed
  most to the 12-month change — the overall change would still be …"; the report's evidence table calls
  it "Largest contributor to change"; SKILL.md 0.2 states that `top_contributor_month` is not
  necessarily the highest-traffic month. The field name is unchanged.
- The core limitation now reads "Wikipedia pageviews are a proxy for attention to the topic, not market
  size, demand, or purchase intent" (SKILL.md, `result.json` limitations, methodology).
- SKILL.md 0.2 adds a rule: do not explain why attention changed unless the JSON supports it.
