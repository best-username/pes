# Run 02: single-language trend, rerun after wording fixes (case 1)

Same prompt as [run 01](01-single-language-astronomy-uk.md), fresh session, after the general fixes that
run 01 triggered (SKILL.md 0.2, clarified robustness wording and limitation sentence).

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "How has interest in astronomy changed in Ukrainian Wikipedia over the last two years?" |
| Model | `claude-haiku-4-5-20251001` |
| Host | Claude Code 2.1.283, print mode, `--setting-sources project --strict-mcp-config --permission-mode dontAsk` |
| Skill installed | yes: project skill, listed in the `init` event, loaded by the model through the `Skill` tool |
| Skill version | SKILL.md 0.2 |
| Turns, time, cost | 5 turns, 24.8 s, $0.040 (as reported by Claude Code) |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`
2. `uv run --frozen --project <skill> python <skill>/scripts/wiki_interest.py resolve --query "astronomy" --languages uk`
   → first candidate Q333 "Astronomy" (available in `uk`)
3. `uv run --frozen --project <skill> python <skill>/scripts/wiki_interest.py analyze --qid Q333 --languages uk --topic "astronomy" --assumption "Astronomy article on Ukrainian Wikipedia"`

`<skill>` = `<workspace>/.claude/skills/wikipedia-interest-analysis`.

## Key `result.json` evidence

Same data as run 01: growth −59.6%, whole Wikipedia −24.6%, topic share −46.4%, 11 of 12 months down,
largest contributor to change 2025-09, −57.5% without it, `strong`, no warnings.
Year-over-year by month: 2026-01 −71.2, 2025-11 −68.1, 2026-02 −67.2, 2025-09 −65.0, 2025-10 −64.2,
2025-12 −61.9, 2026-03 −61.6, 2026-04 −60.3, 2026-05 −24.0, 2026-06 −22.2, 2026-08 −4.0, 2026-07 +5.6.
Report: `<workspace>/wiki-interest-output/Q333_uk_2024-09_2026-08/report.html`.

## Final answer (verbatim)

> ## Interest in Astronomy on Ukrainian Wikipedia Declined Sharply
>
> I analyzed the **Astronomy** article (Астрономія) on Ukrainian Wikipedia, comparing the latest 12 months (September 2025–August 2026) against the previous 12 months (September 2024–August 2025).
>
> **Key Findings:**
>
> - **Overall decline: -59.6%** — Pageviews fell from 16,614 to 6,708, with an average of 559 views per month recently
> - **Strong downward trend** — 11 out of 12 months showed year-over-year declines, with the most dramatic drops in late 2025 (November at -68.1%, January at -71.2%)
> - **Topic share declined faster than the platform** — While Ukrainian Wikipedia overall declined by 24.6%, astronomy's share of the platform fell 46.4%, meaning the topic lost attention faster than the general trend
> - **Not driven by a single event** — The decline is consistent across months; even excluding the largest contributor month (September 2025), the change would still be -57.5%
> - **Early signs of stabilization** — Recent months show less severe declines (May at -24.0%, July at +5.6%), though August dipped back to -4.0%
>
> **Important limitation:** Wikipedia pageviews reflect reader attention, not demand or market size. The data shows *how* attention to astronomy changed on Ukrainian Wikipedia, not *why* — that would require additional context about events, policy changes, or platform shifts during this period.
>
> A detailed interactive report is available at:
> `wiki-interest-output/Q333_uk_2024-09_2026-08/report.html`

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands, no replacement code or scraping | pass | only `resolve` and `analyze` |
| R2 numbers supported by `result.json` | pass | 27 numbers in the answer, all found in `result.json`; ordering claims checked by hand |
| R3 proxy stated | pass | "the Astronomy article (Астрономія)" |
| R4 warnings and data gaps | n/a | no warnings |
| R5 limitation, no market claims | pass | "reflect reader attention, not demand or market size" |
| R6 report path | pass | relative path to `report.html` |
| R7 few tool calls | pass | 3 (Skill, resolve, analyze) |
| R8 no silent proxy swap | pass | the requested topic's own article |
| R9 no automatic ranking | n/a | single language |
| Case: QID from resolve, 24 months, whole-Wikipedia context | pass | all present |

## Against run 01's issues

- "Highest month" misstatement: gone ("the largest contributor month (September 2025)").
- Causal speculation: gone; the answer says the data shows how attention changed, not why.
- Over-hedged limitation: gone; pageviews are described as reader attention.

## Observations

1. "The most dramatic drops in late 2025 (November …, January …)": the two values are the two largest
   drops, but January is 2026, so "late 2025" mislabels one of them.
2. "Early signs of stabilization" is an interpretation of the milder year-over-year changes in
   May–August 2026; the values quoted are correct.
3. "Interactive report" overstates it: the report is a static page with hover tooltips.

## Changes triggered

None.
