# Methodology

How `scripts/wiki_interest.py` turns Wikipedia data into the numbers in `result.json`. Every threshold is
a named constant at the top of the script.

## Data sources

| Command | Endpoint | Used for |
|---|---|---|
| `resolve` | `https://{lang}.wikipedia.org/w/api.php?action=query&generator=search&prop=pageprops\|description` | candidate articles with short descriptions and Wikidata QIDs; disambiguation pages and pages without a QID are skipped |
| `resolve`, `analyze` | `https://www.wikidata.org/w/api.php?action=wbgetentities` | the article title of an item in each language (sitelinks), its label and description; merged items are followed |
| `analyze` | `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{lang}.wikipedia.org/all-access/user/{title}/monthly/{start}/{end}` | monthly views of the article |
| `analyze` | `https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/{lang}.wikipedia.org/all-access/user/monthly/{start}/{end}` | monthly views of the whole Wikipedia in that language (the baseline) |

`user` is traffic Wikimedia classifies as human; `all-access` covers desktop, mobile web and apps.
Requests are sequential and send a User-Agent with a contact URL (Wikimedia limits clients without one to
10 requests per minute). 429 and 5xx responses are retried up to 3 times, honouring `Retry-After`
(otherwise waiting 5 s, then 10 s).

Behaviour the code relies on, checked against the live APIs on 2026-09-26:
- Clients without contact information in the User-Agent get 10 requests per minute, with it 200; the
  default Python User-Agent is refused with 403.
- The per-article endpoint returns the still-running month when the range covers it; the aggregate
  endpoint omits a month until it is published.
- Months before an article existed are omitted rather than returned as 0; months with no views are 0.
- `wbgetentities` reports site IDs it does not know as a warning ("Unrecognized value(s) for parameter
  'sitefilter'"), returns a merged item under the requested QID with `redirects: {from, to}`, and answers
  an unknown QID with HTTP 200 and `error.code: no-such-entity`.

## Analysis window

- Only complete calendar months (UTC) are used. The default window ends with the last complete month. If
  Wikimedia has not yet published that month's whole-Wikipedia totals, the window moves back one month
  and `latest_month_not_published` is reported; an explicit `--end-month` is never moved. The per-article
  API returns the still-running month when a request covers it; that month is always discarded.
- `--months` is 24 to 120 (default 24); data starts in 2015-07.
- Growth, year-over-year changes and trend consistency always use the most recent 24 months: the latest
  12 months against the previous 12. `total_views` covers the whole window. In windows longer than 24
  months, `first_to_latest_12m_growth_pct` compares the first 12 months with the latest 12.

## Metrics (per language)

| Field | Definition |
|---|---|
| `previous_12m_views`, `latest_12m_views` | article views in each 12-month period |
| `growth_pct` | (latest − previous) / previous × 100 |
| `avg_monthly_views_latest_12m` | latest_12m_views / 12, rounded |
| `previous_12m_project_views`, `latest_12m_project_views` | whole-Wikipedia views in each period |
| `project_growth_pct` | the same growth formula for the whole Wikipedia |
| `previous_topic_views_per_million`, `latest_topic_views_per_million` | article views / whole-Wikipedia views × 1,000,000, per period |
| `topic_share_growth_pct` | (latest share / previous share − 1) × 100: a ratio of shares, not growth_pct − project_growth_pct |
| `yoy_pct_by_month` | each of the latest 12 months against the same month a year earlier |
| `positive_yoy_months`, `negative_yoy_months`, `median_yoy_pct` | counts and median of those 12 changes |
| `largest_month`, `largest_month_share_pct` | the latest-year month with the most views and its share of the latest year |
| `top_contributor_month` | the latest-year month whose year-over-year change contributed most to the aggregate 12-month change (in the trend's direction); not necessarily the highest-traffic month. The report calls it the "largest contributor to change" |
| `growth_excl_top_month_pct` | growth recomputed without that month and the same month a year earlier |

`median_yoy_pct` and `largest_month_share_pct` are descriptive; they do not decide any label.

## Trend direction and consistency

`trend_consistency` is a transparent rule-based heuristic, **not a statistical confidence or probability**.

1. **Direction.** `up` if `growth_pct` ≥ +5, `down` if ≤ −5, otherwise `flat` (`FLAT_BAND_PCT = 5`).
   A flat trend gets `not_applicable`.
2. **Breadth.** The number of the latest 12 months whose change against a year earlier has the
   direction's sign; unchanged months do not count. 9 or more: strong; 7 or 8: mixed; fewer: weak
   (`STRONG_MIN_ALIGNED_MONTHS = 9`, `MIXED_MIN_ALIGNED_MONTHS = 7`).
3. **Robustness.** Remove the top contributing month together with the same month a year earlier. If
   the change is then no longer outside ±5% in the same direction, the label drops one level
   (strong → mixed, mixed → weak) and `spike_driven` is true.
4. **Insufficient data.** Any of the latest 24 months missing, no views in the previous 12 months, or a
   month with zero views a year earlier (its change is undefined) gives `insufficient_data`.

Labels are computed from the rounded values published in `result.json`, so they can be re-derived from
the file. `consistency_reasons` states the breadth and robustness evidence in words.

## Missing, zero and rounding

- A month for which the API returns no row is missing (`null`): for example, months before an article
  existed. A month with zero views is data (0).
- Percentages have one decimal. Views per million have two decimals from 1 upward and three below 1
  (133.18, 3.08, 0.799), so no value reads like a number with a thousands separator; the report shows
  the same values. Rounding is for output only: `topic_share_growth_pct` uses the unrounded shares.
  −0.0 is written as 0.0.

## Warnings

| Code | Meaning |
|---|---|
| `no_article` | the item has no article in that language |
| `invalid_language` | not a Wikipedia language code (checked locally, then by Wikidata) |
| `no_data` | the Pageviews API has no data for the article in the window |
| `api_error` | a request failed after retries |
| `missing_months` | months without data in the window |
| `zero_baseline` | no views in the previous 12 months, or a month with zero views a year earlier |
| `low_volume` | fewer than 100 views per month on average in the latest 12 months (`LOW_VOLUME_MONTHLY_VIEWS`) |
| `possible_history_discontinuity` | a month below 5% of the window's median month (`DISCONTINUITY_RATIO`); a new or renamed article is one possible cause |
| `tracks_platform_trend` | the trend is up or down, but `topic_share_growth_pct` is within ±5%: the change mostly mirrors the whole Wikipedia |
| `project_baseline_unavailable` | whole-Wikipedia totals are missing, so the baseline and share fields are null |
| `latest_month_not_published` | the default window moved back one month |
| `qid_redirected` | the requested QID was merged into another item |
| `report_failed` | `report.html` could not be generated; `result.json` is still written |

## Report chart

With one language the chart shows monthly views. With several it shows an index: monthly views × 100 /
the average month of the previous 12 months, so 100 is that language's previous-year average and
different-size Wikipedias can be compared by shape (as small multiples beyond four languages). A language
whose previous 12 months are incomplete or zero is not charted.

## Limitations

- Wikipedia pageviews are a proxy for attention to the topic, not market size, demand, or purchase
  intent. They show how attention changed, not why.
- One article (Wikidata item) stands in for a broader topic, and its articles can differ in scope and
  depth between languages; an item may have no article in some languages.
- A language edition is not a country or a market; English Wikipedia, for example, is read worldwide.
- Only traffic Wikimedia classifies as human is counted. Some automated traffic is misclassified, and
  changes to the classification can shift a series.
- Views of redirects, and of earlier titles of a renamed article, are not included.
- Whole-Wikipedia traffic changes over time and differs between languages; compare `project_growth_pct`
  and `topic_share_growth_pct` before attributing a change to the topic.
