# Evaluation cases

The end-to-end cases (prompt, expected behaviour, expected tool calls, failure conditions) are written in
Phase 3 and run on a low-cost model. Items already agreed to evaluate:

- **Missing article in a requested language.** "Compare growth of interest in intermittent fasting in Polish
  and Czech Wikipedia": Q1666254 has no Polish article. Pass: the agent reports the gap. Fail: it silently
  switches to the broader *Fasting* (Q44602) because that item exists in both languages.
- **Coverage bias in `resolve`.** For "learning English", *Simple English Wikipedia* (Q200183) exists in all
  12 shortlisted languages but is a poor proxy. Pass: the agent chooses on meaning, not on coverage.
- **Follow-up: "Show me only the last year."** Analysis needs 24 months (the latest 12 are compared with the
  previous 12). Decide whether a 12-month presentation window, with 12 extra months fetched internally for
  year-over-year changes, is worth supporting. Do not build it unless the eval shows it is needed.
- **Rows for languages without data** carry ~25 `null` keys. Check whether they confuse the model; compact
  them only if they do.
- **Artifact paths** in `result.json` are absolute. Check whether relative paths would serve the agent better.
