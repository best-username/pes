# Run 11: follow-up "Show me only the last year." (case 5)

Continues the session of [run 06](06-multi-language-chess-rerun-3.md) (`--resume`); the skill text in
context is SKILL.md 0.6.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Show me only the last year." |
| Model | `claude-haiku-4-5-20251001` |
| Turns, time, cost | 2 turns, 13.1 s, $0.057 (includes the resumed context) |
| Permission denials | none |

## Tool calls

1. `analyze --qid Q718 --languages de,fr,es --topic "chess" --assumption "Chess (traditional board game)" --months 12`
   → exit 2, `invalid_arguments`: "--months must be between 24 and 120, got 12"

## Final answer (verbatim)

> The skill requires a minimum of 24 months for comparison (so it can compare each month with the same month a year earlier). However, I can show you the latest 12 months from the data I already retrieved (September 2025–August 2026):
>
> | Language | Latest 12m views | Growth vs. prior year | Per million | Topic share growth |
> |----------|------------------|----------------------|--------------|--------------------|
> | German   | 169672           | -19.7%               | 20.058       | -13.3%            |
> | French   | 144668           | -32.4%               | 20.285       | -24.4%            |
> | Spanish  | 234042           | -38.2%               | 35.825       | -21.9%            |
>
> These figures show the last 12 months (latest_12m) compared to the 12 months immediately before (previous_12m). All three languages show declines year-over-year, with Spanish declining the steepest.
>
> For a deeper look at month-by-month trends in the last year, see the detailed HTML report:
> `<workspace>/wiki-interest-output/Q718_de-es-fr_2024-09_2026-08/report.html`

## Verdict: PASS

| Criterion | Result | Evidence |
|---|---|---|
| R1 skill commands | pass | |
| R2 numbers supported | pass | 38 numbers, all in the run 06 `result.json`; "Spanish declining the steepest" is correct for growth |
| R4 warnings | n/a | none |
| R5 limitation, no market claims | pass, with a note | no market claims; the limitation is not repeated in the follow-up |
| R6 report path | pass | |
| R7 few tool calls | pass | 1 (rejected, then answered from the existing result) |
| Case: explain the 24-month design; latest-12-month figures without recomputing; no invented 12-month analysis | pass | |

## Observations

1. The first instinct was `--months 12`, despite SKILL.md saying windows are never shorter than 24
   months; the structured error redirected it after one call.
2. A 12-month presentation window: the data the user wanted was already in `result.json`; the only cost
   was one rejected call. Not worth building on this evidence.
