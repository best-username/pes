# Run 00: baseline without the skill

Purpose: see what the same model does on a neutral request when the skill is not installed.

| | |
|---|---|
| Date | 2026-09-27 |
| Prompt | "How has interest in photography changed in Italian Wikipedia over the last two years?" |
| Model | `claude-haiku-4-5-20251001` |
| Host | Claude Code 2.1.283, print mode, `--setting-sources project --strict-mcp-config --permission-mode dontAsk` |
| Skill installed | no |

## 00a: restricted tools (as in the skill runs)

- Tool calls: `ToolSearch` for WebSearch, then `WebSearch` (denied: not allowed in this setup).
- Answer: said web search was disabled, listed what it would look for (pageviews, edit activity), and
  asked for permission or data. No numbers.
- 3 turns, 9.6 s, $0.049.

## 00b: web tools allowed

- Tool calls: 3 × `WebSearch` (generic photography-trend and Wikipedia-statistics queries), 1 × `WebFetch`
  (a Meta-Wiki research page on Italian Wikipedia editor decline).
- Answer: could not find topic-level data; pointed to pageview tools; cited unverified platform figures
  from web pages ("~15.3 million daily page views", "~1.9 million articles"). It never used the
  Pageviews API.
- 6 turns, 32.5 s, $0.131.

## Takeaways

- Without the skill the model has no path to per-article pageview data and gives up; with web access it
  substitutes unverified figures from web pages.
- It did not invent a trend, but it also did not identify a topic proxy, complete months or a baseline.
