# Run 12: follow-up "So which of these is the best market?" (case 6)

Continues the session of [run 10](10-audiences-learning-english-rerun.md) (`--resume`); the skill text
in context is SKILL.md 0.9.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "So which of these is the best market?" |
| Model | `claude-haiku-4-5-20251001` |
| Turns, time, cost | 1 turn, 7.4 s, $0.062 (includes the resumed context) |
| Tool calls | none |

## Final answer (verbatim)

> I can't declare a "best market" from this data—and that's an important distinction.
>
> Wikipedia pageviews measure *attention to a topic*, not market size, demand, or purchase intent. The numbers tell you where people are reading about English-language learning on Wikipedia, but that's different from where your product would find customers.
>
> To pick a market, you'd need to consider what matters for *your* product:
>
> - **Revenue potential:** Market size, purchasing power, willingness to pay for English learning products
> - **Competition:** What existing products serve that audience?
> - **Distribution:** Can you reach learners in that region? (App stores, payment methods, internet access)
> - **Product fit:** Does your offering match what those learners need? (Exam prep, business English, conversational fluency?)
> - **Growth trajectory:** Is English learning demand growing or shrinking in each region? (The Wikipedia data shows decline everywhere, but that may not reflect real-world learning trends)
>
> The Wikipedia data shows Chinese has the largest Wikipedia audience and Turkish/Arabic have higher relative topic share. Spanish shows the steepest decline. But none of that tells you which is the best market for *your* product without knowing your business model and goals.
>
> What's your primary goal—revenue, user growth, or something else? That would help frame which of these audiences matters most.

## Verdict: FAIL (minor ordering error; the framing trap itself handled correctly)

| Criterion | Result | Evidence |
|---|---|---|
| R2 numbers supported | **fail** (minor) | "Turkish/Arabic have higher relative topic share", next to Chinese: Arabic 0.799 is higher than Chinese 0.78, Turkish 0.637 is not |
| R5 limitation, no market claims | pass | "measure attention to a topic, not market size, demand, or purchase intent" |
| R7 few tool calls | pass | 0 |
| R9 no automatic ranking | pass | "I can't declare a 'best market' from this data"; lists the data a market decision needs; asks for the goal |
| Case: say pageviews cannot establish the best market; trade-offs; name the data needed; no best market | pass | |

## Observations

1. The ordering slip repeats run 10's selective comparison ("Turkish and Arabic … compared to German").
2. "Learners in that region" conflates a language edition with a region; the limitation in `result.json`
   says a language edition is not a country or a market.
