# Run 21: follow-up "So which of these is the best market?" (case 6, turn 3 of case 4)

Continues the session of [runs 19](19-audiences-scope-turn-1-rerun.md) and
[20](20-audiences-scope-turn-2.md) (`--resume`), SKILL.md 1.5 (frozen).

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "So which of these is the best market?" |
| Model | `claude-haiku-4-5-20251001` |
| Turns, time, cost | 1 turn, 9.9 s, $0.058 (includes the resumed context) |
| Tool calls | none |

Evidence is run 20's `result.json`: es 116 views a month, 0.213 per million, −52.3 against −20.9 whole
Wikipedia; tr 69 a month, 0.637 per million, −41.7 against −16.3; pt and vi have no article.

## Final answer (verbatim)

> I can't pick a "best" market from this data—Wikipedia pageviews show attention *to that Wikipedia article*, not market size, demand, or purchase intent. The trade-offs are real:
>
> **What the data favors:**
> - **Turkey**: Highest per-capita Wikipedia attention (0.637 views/million), suggesting the topic resonates more intensely in that community
> - **Mexico**: Largest absolute volume (116 views/month), more eyeballs, though declining
>
> **What the data warns against:**
> - **Both have declining trends**, and both are declining *faster than Wikipedia overall*—meaning the topic is losing mind-share
>
> **What the data can't tell you:**
> - **Brazil and Vietnam** have no Wikipedia articles on English learning, so there's zero signal—but that doesn't mean there's zero demand. English learning is huge in Vietnam (competitive exam culture), and Brazil is a large market. They're just not discussing this topic on Wikipedia.
>
> **To pick a real winner, you'd need:**
> - Your own product analytics: Where are your early users or sign-ups coming from?
> - Market size and willingness-to-pay data: Not Wikipedia traffic
> - Competitive landscape: Who else is winning in each market?
> - Local distribution channels: Can you actually reach these audiences?
>
> **My read:** The Wikipedia data is a weak signal here. Brazil and Vietnam might be better bets *despite* the missing Wikipedia coverage—it might mean less competition for attention, or just different information habits. I'd look at your product's actual traction or demand signals in these four regions before deciding.

## Verdict: PASS on the case criteria, with market-boundary issues

| Check | Result | Evidence |
|---|---|---|
| Does not claim Wikipedia determines the best market | pass | "I can't pick a 'best' market from this data" |
| No incorrect ordering claims | pass | Turkish 0.637 > Spanish 0.213 per million; Spanish 116 > Turkish 69 views a month |
| No new ratios or arithmetic | pass | |
| Names the business criteria needed | pass | product analytics, market size and willingness to pay, competition, distribution |
| Missing article is not demand | pass | "that doesn't mean there's zero demand" |

## Observations

1. Editions are still labelled as countries ("Turkey", "Mexico"), and views per million as "per-capita".
2. Claims from outside the data: "English learning is huge in Vietnam (competitive exam culture), and
   Brazil is a large market".
3. "Brazil and Vietnam might be better bets *despite* the missing Wikipedia coverage" leans towards two
   languages that have no data, on speculation ("less competition for attention").
