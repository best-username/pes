# Run 18: audience question without a scope, turn 1 (case 4)

First run of the three-turn case 4, fresh session, SKILL.md 1.4 (ask before choosing languages, with a
fixed question).

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "Which language audiences should I investigate next for a product about learning English, and why?" |
| Model | `claude-haiku-4-5-20251001` |
| Skill version | SKILL.md 1.4 |
| Turns, time, cost | 3 turns, 10.7 s, $0.024 |
| Permission denials | none |

## Tool calls

1. `Skill` → `wikipedia-interest-analysis`

No `resolve` or `analyze`; no output folder was written.

## Final answer (verbatim)

> I can compare Wikipedia attention for English language learning across different language editions—pageviews are a proxy for interest in the topic. But I need to know which language audiences to investigate.
>
> Which 3–10 language audiences should I include in the comparison? Some common choices for English learning products are:
>
> - **Major Asian markets** (Chinese: `zh`, Japanese: `ja`, Korean: `ko`, Vietnamese: `vi`, Thai: `th`)
> - **Major European/Latin markets** (Spanish: `es`, French: `fr`, German: `de`, Italian: `it`, Portuguese: `pt`, Polish: `pl`, Russian: `ru`)
> - **Other regions** (Turkish: `tr`, Arabic: `ar`, Hindi: `hi`, Indonesian: `id`)
>
> Or if you have target regions or constraints in mind (specific countries, existing user bases, growth priorities), I can help you narrow down which languages make sense to analyze.

## Verdict: FAIL (proposed its own languages, grouped as markets)

| Check | Result | Evidence |
|---|---|---|
| Exactly one concise clarifying question | pass, partly | one question plus the regions and constraints offer, but padded with a 16-language list |
| Explains that Wikipedia should not invent the market shortlist | **fail** | says what it can compare and that it needs the audiences; "I don't want to invent a market shortlist for you" is left out |
| No `resolve` or `analyze` | pass | Skill call only |
| No languages or markets of its own (R10) | **fail** | 16 languages under "Major Asian markets", "Major European/Latin markets" and "Other regions" |

## Cause

The question template is introduced as what to ask, not "as written", and SKILL.md never says to
suggest no languages; "The languages come from the user" is the only guard. The model kept parts of the
template ("Which 3–10 language audiences", the offer to narrow down) and added its own suggestions. By
contrast, the limitation, introduced "as written", is quoted word for word in nearly every run.

## Changes triggered

None; stopped for review. Turns 2 and 3 were not run.

After review: SKILL.md 1.5: reply with exactly the fixed question and nothing else. Verified by [run 19](19-audiences-scope-turn-1-rerun.md).
