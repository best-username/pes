# Wikipedia interest analysis

An [Agent Skill](https://agentskills.io/specification) that measures how attention to a topic changes
over time from Wikipedia pageviews, in one or several language editions, and writes a shareable,
self-contained HTML report.

The agent decides what the user means and which Wikipedia article stands for it. A standard-library
Python script fetches the data and computes every number. Wikipedia pageviews are a proxy for attention
to the topic, not market size, demand, or purchase intent.

## How it works

1. **The agent** reads [`SKILL.md`](SKILL.md). It takes the languages from the user, asking one fixed
   question when an audience comparison names none, and chooses the article by meaning.
2. **`resolve`** turns topic words into candidate Wikidata items (QIDs), with descriptions and the
   requested languages that have an article.
3. **`analyze`** takes one QID and up to 20 languages. It fetches monthly human pageviews for the article
   and for the whole Wikipedia in each language. It then computes:
   - the latest 12 months against the previous 12;
   - the change in the topic's share of that Wikipedia;
   - each month against the same month a year earlier;
   - a rule-based trend-consistency label;
   - warnings.
4. **The outputs** are `result.json`, `monthly.csv` and `report.html`. The agent answers from the JSON
   and points to the report.

Formulas, thresholds, warning codes and the API behaviour the code relies on are in
[`references/methodology.md`](references/methodology.md).

## Requirements

- [uv](https://docs.astral.sh/uv/). It installs Python 3.12 if it is missing.
- Outbound HTTPS to `*.wikipedia.org`, `www.wikidata.org` and `wikimedia.org`. No API keys.
- No third-party packages, for either running or testing.

## Setup and tests

```
cd wikipedia-interest-analysis
uv sync --locked
uv run --frozen python -m unittest discover -s tests -v
```

The 89 tests run offline, with HTTP mocked. To validate the skill against the specification, run this
from the folder that contains the skill:

```
uvx --from skills-ref==0.1.1 agentskills validate wikipedia-interest-analysis
```

## Install as a skill

- **Claude Code:** copy or symlink this folder to `.claude/skills/wikipedia-interest-analysis/` in a
  project, or to `~/.claude/skills/wikipedia-interest-analysis/` for every project. Keep the folder name:
  it must match the skill's `name`.
- **Other Agent Skills hosts:** install the folder the way the host expects. `SKILL.md` follows the Agent
  Skills specification, and nothing depends on Claude-specific features.
- **Any other agent or a shell:** run the commands below directly.

On first use, `uv run --project` creates `.venv` inside the skill folder, so the folder must be
writable. To keep it elsewhere, set `UV_PROJECT_ENVIRONMENT=/some/path`.

## Command-line usage

```
SKILL_DIR=path/to/wikipedia-interest-analysis
uv run --frozen --project "$SKILL_DIR" python "$SKILL_DIR/scripts/wiki_interest.py" resolve --query "intermittent fasting" --languages pl cs
uv run --frozen --project "$SKILL_DIR" python "$SKILL_DIR/scripts/wiki_interest.py" analyze --qid Q1666254 --languages pl cs --topic "intermittent fasting"
```

| Command | Options |
|---|---|
| `resolve` | `--query` (required), `--pivot-lang` (Wikipedia to search, default `en`), `--languages`, `--limit` (1–10) |
| `analyze` | `--qid` and `--languages` (required, up to 20), `--months` (24–120, default 24), `--end-month YYYY-MM`, `--topic`, `--assumption` (repeatable), `--output` |

Each command prints one JSON document. The exit code is 0 for `ok` or `partial`, 1 for a data or API
error, and 2 for a usage error.

`analyze` writes to `./wiki-interest-output/<qid>_<languages>_<start>_<end>/`:

| File | Contents |
|---|---|
| `result.json` | The authoritative output: status, topic, assumptions, proxy, period, one result per language, warnings, limitations, artifact paths |
| `monthly.csv` | `language, article, month, views, project_views` |
| `report.html` | A self-contained report with inline SVG charts and no scripts or external resources. It opens offline and prints to PDF |

## Layout

```
wikipedia-interest-analysis/
├── SKILL.md                    instructions for the agent
├── README.md
├── pyproject.toml, uv.lock     Python 3.12, no dependencies
├── .python-version
├── scripts/wiki_interest.py    resolve and analyze, standard library only
├── references/methodology.md   formulas, thresholds, warnings, verified API behaviour
├── tests/test_metrics.py       offline unit tests
└── evals/
    ├── cases.md                rubric, cases, results and summary
    └── runs/                   one record per evaluation run
```

## Evaluation

The skill was evaluated end to end on Claude Haiku 4.5 in Claude Code: 27 runs, $1.33 in total. The
records, rubric and cases are in [`evals/cases.md`](evals/cases.md).

The deterministic data pipeline and artifact generation were reliable across the evaluation. The main
failure mode on Claude Haiku 4.5 was free-form synthesis for large, open-ended multi-language
comparisons: the model occasionally omitted warnings, introduced unsupported comparisons, or conflated
Wikipedia language editions with geographic markets. This is why result.json and report.html remain the
authoritative outputs.

- **What was reliable:** the skill was found and used in every run, with `resolve` and `analyze` rather
  than scraping or new code. Without the skill, both baseline runs gave up.
- **Results on the frozen SKILL.md:**
  - Passed: the missing-article case, the clarifying question, the ambiguous-country case, the
    "best market" follow-up, and both held-out prompts.
  - Failed: the country-scoped audience comparison. It made one wrong ordering claim, described editions
    as countries, and left out the limitation.
- **Interaction design found by the evals:** early runs answered an audience comparison without a
  scope by inventing a 10–15 language shortlist. Now, when such a request names no languages or regions,
  the skill asks which language audiences, regions or product constraints are relevant, with one fixed
  question, instead of inventing a market shortlist.

## Limitations

- **A proxy, not demand:** pageviews measure attention to one article, not market size, demand or
  purchase intent. They show how attention changed, not why.
- **One article per topic:** a single Wikidata item stands in for the topic, and its articles can
  differ in scope between languages.
- **Editions are not markets:** a language edition is not a country or a market. English Wikipedia,
  for example, is read worldwide.
- **What is counted:** only traffic Wikimedia classifies as human, and not views of redirects or of a
  renamed article's former titles.
- **Consistency is a heuristic:** `trend_consistency` is a rule-based label, not a statistical
  confidence.
- **24-month minimum:** the analysis needs at least 24 months, because each month is compared with
  the same month a year earlier.
- **Small models:** in free-form answers they can misreport correct numbers (see Evaluation).

## Future work

- **Agent-oriented summary (not implemented):** a compact `answer_facts` layer in `result.json` could
  reduce the synthesis burden on small models by flattening warnings and safe comparison facts. The
  model would then copy facts instead of composing multi-language comparisons. This is motivated by
  the Haiku runs above.
- **Topic baskets:** several articles per topic, for concepts that no single article covers.
- **Redirects and former titles:** pageviews of these, and a statistical measure of trend
  uncertainty alongside the rule-based label.

## AI-assisted development and verification

- **Where AI assisted:**
  - Claude Code with Claude Opus 5.5 drafted the plans, code, tests and documentation, and ran the API
    probes and the evaluation.
  - Claude Haiku 4.5 was the model under test.
  - The author set the requirements, made the design decisions, and approved each phase twice: before
    implementation and before its commit.
- **How generated code and claims were reviewed:**
  - The work went in three phases: core CLI and metrics; the HTML report; SKILL.md, evaluation and
    documentation.
  - Each phase started with a written plan and open decisions, and ended with the author reviewing
    the diff, the test results and live examples.
  - Decisions made in review include measuring share change as a ratio of shares (not a difference of
    growth rates), `not_applicable` for flat trends, no ranking field, the one-level downgrade for
    spike-driven trends, and the 20-language limit.
- **How API behaviour was verified:** every API behaviour the code depends on was probed against the
  live APIs before the code relied on it:
  - rate limits, and the 403 for the default User-Agent;
  - the partial current month;
  - omitted months;
  - `sitefilter` warnings;
  - merged and unknown items.

  The findings are listed, with the date, in the methodology.
- **How deterministic calculations were checked:**
  - The unit tests compare against literal values worked out by hand, never computed with the code
    under test. The real Czech series was also cross-checked by an independent throwaway script.
  - The tests cover missing and zero months, zero baselines, flat and spike-driven trends, longer
    windows, HTTP retries and errors, HTML escaping, and the CLI contract.
  - Mutation checks deliberately broke the code to confirm that a test fails. They found three gaps:
    two led to new tests, and one showed that a consistency rule could never change a label, so the
    rule was removed.
  - The report was inspected in headless Chrome at desktop, mobile and print sizes.
- **How end-to-end behaviour was tested:**
  - The evaluation used Claude Code sessions on Claude Haiku 4.5, isolated from user settings,
    plugins and MCP servers, with only the tools the skill needs.
  - The rubric and cases were written before the first run.
  - Every number in every answer was checked against that run's `result.json`.
  - Two baseline runs had no skill. Two held-out prompts were chosen after SKILL.md was frozen.
- **What the tests do not prove:** passing tests do not show that the code is correct. The tests check
  the arithmetic against values we worked out, so an error in the specification would still pass. The
  evaluation also showed that correct numbers can be misreported by the model, so answers are checked
  against `result.json` rather than trusted.
