"""Topic-interest analysis from Wikipedia pageviews, for use by an AI agent.

  resolve  find candidate Wikipedia articles (Wikidata QIDs) that can proxy a topic
  analyze  fetch monthly human pageviews for one QID in several languages, compute
           deterministic trend metrics, write result.json and monthly.csv

Standard library only. stdout is always one JSON document, including on errors.
"""

import argparse
import calendar
import csv
import datetime as dt
import json
import re
import ssl
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCHEMA_VERSION = 1
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
PAGEVIEWS_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
DEFAULT_OUTPUT_ROOT = "wiki-interest-output"

# Wikimedia limits clients without contact info in the User-Agent to 10 requests/min (200/min
# with it): https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits
USER_AGENT = "WikipediaInterestAnalysis/0.1 (https://github.com/best-username/pes)"
HTTP_ATTEMPTS = 3
HTTP_TIMEOUT_S = 30
MAX_RETRY_WAIT_S = 60

MIN_MONTHS, MAX_MONTHS = 24, 120
MAX_LANGUAGES = 20
FIRST_DATA_MONTH = "2015-07"  # Pageviews API coverage starts in July 2015

# Heuristic thresholds: they decide trend labels and warnings (keep references/methodology.md in sync).
FLAT_BAND_PCT = 5.0            # a change inside +-5% is "no meaningful change"; also the robustness bar
STRONG_MIN_ALIGNED_MONTHS = 9  # breadth: of the latest 12 months, moving in the trend's direction
MIXED_MIN_ALIGNED_MONTHS = 7
LOW_VOLUME_MONTHLY_VIEWS = 100
DISCONTINUITY_RATIO = 0.05     # a month below 5% of the window's median month

METRIC_KEYS = (
    "total_views", "previous_12m_views", "latest_12m_views", "growth_pct", "avg_monthly_views_latest_12m",
    "previous_12m_project_views", "latest_12m_project_views", "project_growth_pct",
    "previous_topic_views_per_million", "latest_topic_views_per_million", "topic_share_growth_pct",
    "yoy_pct_by_month", "positive_yoy_months", "negative_yoy_months", "median_yoy_pct",
    "largest_month", "largest_month_share_pct", "top_contributor_month", "growth_excl_top_month_pct",
    "spike_driven", "trend_direction", "trend_consistency", "consistency_reasons",
    "first_12m_views", "first_to_latest_12m_growth_pct", "missing_months",
)

LANGUAGE_RE = re.compile(r"[a-z]{2,12}(-[a-z0-9]{1,12})*")
QID_RE = re.compile(r"Q[1-9][0-9]*")


class UsageError(Exception):
    """Invalid command-line input; reported as JSON with exit code 2."""


class ApiError(Exception):
    """A Wikimedia request failed (after retries, where retrying makes sense)."""


# --- months: an int index (year * 12 + month - 1) keeps window arithmetic trivial ---

def parse_month(text):
    match = re.fullmatch(r"(\d{4})-(\d{2})", text)
    if not match or not 1 <= int(match.group(2)) <= 12:
        raise ValueError(f"expected YYYY-MM, got {text!r}")
    return int(match.group(1)) * 12 + int(match.group(2)) - 1


def format_month(index):
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def last_complete_month(today):
    return today.year * 12 + today.month - 2


def api_range(first, last):
    """Pageviews API start/end dates covering whole months first..last."""
    year, month0 = divmod(last, 12)
    last_day = calendar.monthrange(year, month0 + 1)[1]
    return f"{first // 12:04d}{first % 12 + 1:02d}01", f"{year:04d}{month0 + 1:02d}{last_day:02d}"


def resolve_period(end_month, months, today):
    """(first, last) month indexes of the analysis window; only complete months are allowed."""
    if not MIN_MONTHS <= months <= MAX_MONTHS:
        raise UsageError(f"--months must be between {MIN_MONTHS} and {MAX_MONTHS}, got {months}")
    latest = last_complete_month(today)
    try:
        end = parse_month(end_month) if end_month else latest
    except ValueError as err:
        raise UsageError(f"--end-month: {err}") from None
    if end > latest:
        raise UsageError(f"--end-month must be a complete month, i.e. {format_month(latest)} or earlier")
    start = end - months + 1
    if start < parse_month(FIRST_DATA_MONTH):
        raise UsageError(f"the window would start in {format_month(start)}; pageview data starts in {FIRST_DATA_MONTH}")
    return start, end


# --- input validation: language codes become hostnames, titles become URL paths ---

def normalize_languages(values):
    codes = []
    for value in values:
        for code in value.replace(",", " ").split():
            code = code.lower().replace("_", "-")
            if code not in codes:
                codes.append(code)
    if len(codes) > MAX_LANGUAGES:
        raise UsageError(f"at most {MAX_LANGUAGES} languages per run, got {len(codes)}")
    return codes


def is_valid_language(code):
    return LANGUAGE_RE.fullmatch(code) is not None


def normalize_qid(text):
    qid = text.strip().upper()
    if not QID_RE.fullmatch(qid):
        raise UsageError(f"not a Wikidata item id (expected Q followed by digits): {text!r}")
    return qid


def title_path(title):
    return urllib.parse.quote(title.replace(" ", "_"), safe="")


# --- metrics: pure functions over monthly values ---

def rnd(value, digits=1):
    """Round for output; `or 0.0` turns -0.0 into 0.0."""
    return None if value is None else (round(value, digits) or 0.0)


def pct_change(new, old):
    return (new - old) / old * 100 if old else None


def warning(code, message, hint=None, **fields):
    return {"code": code, **fields, "message": message, **({"hint": hint} if hint else {})}


def summarize(labels, limit=6):
    shown = ", ".join(labels[:limit])
    return f"{shown} and {len(labels) - limit} more" if len(labels) > limit else shown


def trend_direction(growth_pct):
    if growth_pct is None:
        return None
    if growth_pct >= FLAT_BAND_PCT:
        return "up"
    if growth_pct <= -FLAT_BAND_PCT:
        return "down"
    return "flat"


def classify(direction, yoy, growth_excl_top):
    """Rule-based label for the evidence behind an up/down trend; NOT a statistical confidence.

    Two independent checks, on the rounded values published in result.json (so any label can be
    re-derived from that file):
      breadth    - how many of the latest 12 months moved in the trend's direction compared with
                   the same month a year earlier: 9+ strong, 7-8 mixed, fewer weak;
      robustness - whether the change stays a meaningful move (outside the flat band) after
                   removing the month pair that contributed most to it. A trend that is not robust
                   drops one level (strong -> mixed, mixed -> weak) and is marked spike_driven.
    Returns (trend_consistency, aligned_months, spike_driven).
    """
    if direction is None or None in yoy:
        return "insufficient_data", None, None
    if direction == "flat":
        return "not_applicable", None, None
    sign = 1 if direction == "up" else -1
    aligned = sum(1 for y in yoy if y * sign > 0)
    robust = growth_excl_top * sign >= FLAT_BAND_PCT
    if aligned >= STRONG_MIN_ALIGNED_MONTHS:
        label = "strong" if robust else "mixed"
    elif aligned >= MIXED_MIN_ALIGNED_MONTHS:
        label = "mixed" if robust else "weak"
    else:
        label = "weak"
    return label, aligned, not robust


def consistency_reasons(m, aligned):
    growth, direction = m["growth_pct"], m["trend_direction"]
    if m["trend_consistency"] == "insufficient_data":
        if growth is None:
            return ["the previous 12 months had no views, so there is no baseline to compare with"]
        return ["some months had zero views a year earlier, so not every month can be compared with the same month a year before"]
    if direction == "flat":
        return [f"views changed by {growth:+.1f}%, within +-{FLAT_BAND_PCT:g}%: no meaningful upward or downward trend to assess"]
    side, move = ("above", "increase") if direction == "up" else ("below", "decrease")
    without = (f"without its biggest contributing month ({m['top_contributor_month']}) the change would be "
               f"{m['growth_excl_top_month_pct']:+.1f}%")
    if m["spike_driven"]:
        lowered = " (label lowered one level)" if aligned >= MIXED_MIN_ALIGNED_MONTHS else ""
        robustness = f"robustness: {without}, no longer a meaningful {move}, so the trend depends on that one month{lowered}"
    else:
        robustness = f"robustness: {without}, so the trend does not depend on one month"
    return [f"breadth: {aligned} of 12 months {side} the same month a year earlier "
            f"(strong needs {STRONG_MIN_ALIGNED_MONTHS}+, mixed {MIXED_MIN_ALIGNED_MONTHS}+)", robustness]


def language_metrics(views, project, months):
    """Metrics for one language. `views`/`project` are monthly values aligned with `months`
    (oldest first; None = no data row). Latest-vs-previous metrics use the most recent 24 months.
    Returns (metrics dict with every METRIC_KEYS key, list of warnings)."""
    labels = [format_month(m) for m in months]
    out = dict.fromkeys(METRIC_KEYS)
    warnings = []
    out["missing_months"] = [label for label, v in zip(labels, views) if v is None]
    if out["missing_months"]:
        warnings.append(warning("missing_months", f"No pageview data for {summarize(out['missing_months'])}.",
                                "The article may be newer than the window; try a shorter --months or --end-month."))
    if None not in views:
        out["total_views"] = sum(views)

    prev, latest, latest_labels = views[-24:-12], views[-12:], labels[-12:]
    if None in prev or None in latest:
        out["trend_consistency"] = "insufficient_data"
        out["consistency_reasons"] = ["some of the latest 24 months have no data, so the latest 12 months "
                                      "cannot be compared with the previous 12"]
        return out, warnings

    prev_sum, latest_sum = sum(prev), sum(latest)
    out.update(previous_12m_views=prev_sum, latest_12m_views=latest_sum,
               avg_monthly_views_latest_12m=round(latest_sum / 12), growth_pct=rnd(pct_change(latest_sum, prev_sum)))
    yoy_raw = [pct_change(new, old) for new, old in zip(latest, prev)]
    yoy = [rnd(y) for y in yoy_raw]
    out["yoy_pct_by_month"] = dict(zip(latest_labels, yoy))
    out["positive_yoy_months"] = sum(1 for y in yoy if y is not None and y > 0)
    out["negative_yoy_months"] = sum(1 for y in yoy if y is not None and y < 0)
    if None not in yoy_raw:
        out["median_yoy_pct"] = rnd(statistics.median(yoy_raw))
    if latest_sum:
        top = max(range(12), key=lambda i: latest[i])  # max() keeps the earliest month on ties
        out["largest_month"], out["largest_month_share_pct"] = latest_labels[top], rnd(latest[top] / latest_sum * 100)

    direction = trend_direction(out["growth_pct"])
    if direction in ("up", "down"):
        deltas = [new - old for new, old in zip(latest, prev)]
        k = (max if direction == "up" else min)(range(12), key=lambda i: deltas[i])
        out["top_contributor_month"] = latest_labels[k]
        out["growth_excl_top_month_pct"] = rnd(pct_change(latest_sum - latest[k], prev_sum - prev[k]))
    out["trend_direction"] = direction
    out["trend_consistency"], aligned, out["spike_driven"] = classify(direction, yoy, out["growth_excl_top_month_pct"])
    out["consistency_reasons"] = consistency_reasons(out, aligned)

    if len(views) > 24 and None not in views[:12]:
        first_sum = sum(views[:12])
        out["first_12m_views"], out["first_to_latest_12m_growth_pct"] = first_sum, rnd(pct_change(latest_sum, first_sum))

    project24 = project[-24:]
    if None in project24:
        warnings.append(warning("project_baseline_unavailable", "Whole-Wikipedia totals are missing for part of the "
                                "latest 24 months, so project and topic-share metrics are omitted."))
    else:
        project_prev, project_latest = sum(project24[:12]), sum(project24[12:])
        prev_share = prev_sum / project_prev * 1_000_000 if project_prev else None
        latest_share = latest_sum / project_latest * 1_000_000 if project_latest else None
        out.update(previous_12m_project_views=project_prev, latest_12m_project_views=project_latest,
                   project_growth_pct=rnd(pct_change(project_latest, project_prev)),
                   previous_topic_views_per_million=rnd(prev_share, 3), latest_topic_views_per_million=rnd(latest_share, 3))
        if prev_share and latest_share is not None:
            out["topic_share_growth_pct"] = rnd((latest_share / prev_share - 1) * 100)

    if prev_sum == 0:
        warnings.append(warning("zero_baseline", "The previous 12 months had no views, so growth cannot be computed."))
    elif 0 in prev:
        zero = [labels[-24 + i] for i, v in enumerate(prev) if v == 0]
        affected = [latest_labels[i] for i, v in enumerate(prev) if v == 0]
        warnings.append(warning("zero_baseline", f"{', '.join(zero)} had zero views, so the year-over-year change "
                                f"for {', '.join(affected)} cannot be computed."))
    if latest_sum / 12 < LOW_VOLUME_MONTHLY_VIEWS:
        warnings.append(warning("low_volume", f"Only {round(latest_sum / 12)} views per month on average in the latest "
                                "12 months; percentages on small counts can swing a lot."))
    median_month = statistics.median(v for v in views if v is not None)
    low = [label for label, v in zip(labels, views) if v is not None and v < DISCONTINUITY_RATIO * median_month]
    if median_month > 0 and low:
        warnings.append(warning(
            "possible_history_discontinuity",
            f"Some months have unusually low views (under {DISCONTINUITY_RATIO:.0%} of the median month): {summarize(low)}. "
            "One possible cause is that the article was created or renamed during the period (views under an "
            "earlier title are not counted); a genuine drop in interest or a data issue are other possibilities."))
    share_growth = out["topic_share_growth_pct"]
    if direction in ("up", "down") and share_growth is not None and abs(share_growth) < FLAT_BAND_PCT:
        warnings.append(warning(
            "tracks_platform_trend",
            f"Views changed by {out['growth_pct']:+.1f}%, but the topic's share of all views on this Wikipedia changed "
            f"by only {share_growth:+.1f}%: the change mostly mirrors the whole Wikipedia."))
    return out, warnings


# --- HTTP: sequential GETs with retries that follow Wikimedia's rate-limit guidance ---

def retry_delay(retry_after, attempt):
    """Honour a numeric Retry-After; otherwise wait 5 s, 10 s, ... (Wikimedia asks for at least 5 s)."""
    try:
        seconds = float(retry_after)
    except (TypeError, ValueError):
        seconds = 5.0 * attempt
    return min(max(seconds, 0.0), MAX_RETRY_WAIT_S)


def get_json(url):
    """GET a Wikimedia JSON endpoint. Returns None on 404 (the Pageviews API's "no data")."""
    host = urllib.parse.urlsplit(url).netloc
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_S) as response:
                body = response.read()
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            if err.code != 429 and err.code < 500:
                detail = err.read()[:200].decode("utf-8", "replace").strip()
                raise ApiError(f"HTTP {err.code} from {host}: {detail}") from None
            failure, retry_after = f"HTTP {err.code}", err.headers.get("Retry-After")
        except urllib.error.URLError as err:
            if isinstance(err.reason, ssl.SSLError):
                raise ApiError(f"TLS error talking to {host}: {err.reason}. If a proxy intercepts HTTPS, "
                               "point SSL_CERT_FILE at its CA bundle.") from None
            failure, retry_after = f"network error ({err.reason})", None
        except OSError as err:  # timeouts and dropped connections while reading
            failure, retry_after = f"network error ({err})", None
        else:
            try:
                return json.loads(body)
            except ValueError:
                raise ApiError(f"unexpected non-JSON response from {host}") from None
        if attempt == HTTP_ATTEMPTS:
            raise ApiError(f"{failure} from {host} after {HTTP_ATTEMPTS} attempts")
        time.sleep(retry_delay(retry_after, attempt))


# --- parsing Wikimedia responses ---

def parse_search(data, limit):
    """Search-ranked candidates that have a Wikidata QID; disambiguation and unlinked pages are skipped."""
    candidates, excluded = [], {"disambiguation_pages": 0, "without_qid": 0}
    for page in sorted(data.get("query", {}).get("pages", []), key=lambda p: p.get("index", 0)):
        if len(candidates) == limit:
            break
        props = page.get("pageprops", {})
        if "disambiguation" in props:
            excluded["disambiguation_pages"] += 1
        elif "wikibase_item" not in props:
            excluded["without_qid"] += 1
        else:
            candidates.append({"qid": props["wikibase_item"], "title": page["title"],
                               "description": page.get("description")})
    return candidates, excluded


def parse_rejected_sites(data):
    """Site ids Wikidata did not recognise in `sitefilter` (it warns rather than failing)."""
    text = data.get("warnings", {}).get("wbgetentities", {}).get("*", "")
    match = re.search(r'Unrecognized values? for parameter "sitefilter": ([^\n]+)', text)
    return {site.strip().rstrip(".") for site in match.group(1).split(",")} if match else set()


def parse_entity(data, qid):
    """{id, label, description, sitelinks {site: title}}; id is the merge target for merged items.
    None if Wikidata has no such item."""
    if "error" in data:
        if data["error"].get("code") == "no-such-entity":
            return None
        raise ApiError(f"Wikidata error: {data['error'].get('info', data['error'])}")
    entity = data.get("entities", {}).get(qid)
    if entity is None:
        return None
    return {"id": entity.get("id", qid),
            "label": entity.get("labels", {}).get("en", {}).get("value"),
            "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            "sitelinks": {site: link["title"] for site, link in entity.get("sitelinks", {}).items()}}


def month_of(timestamp):
    """Pageviews API timestamp 'YYYYMMDDHH' -> month index."""
    return int(timestamp[:4]) * 12 + int(timestamp[4:6]) - 1


def monthly_values(items, months):
    """Pageviews API items -> values aligned with `months` (None where the API has no row).
    Rows outside the window, such as the still-running current month, are ignored."""
    by_month = {month_of(item["timestamp"]): item["views"] for item in items}
    return [by_month.get(m) for m in months]


# --- commands ---

LANGUAGE_HINT = ("Use Wikipedia subdomain codes, e.g. pl for pl.wikipedia.org "
                 "(Norwegian Bokmål is 'no', Chinese is 'zh').")
NETWORK_HINT = "Check outbound HTTPS access to *.wikipedia.org, www.wikidata.org and wikimedia.org, then retry."
LIMITATIONS = [
    "Wikipedia pageviews measure attention to one article: a proxy for interest in the topic, "
    "not purchase intent, market size or demand.",
    "One article (Wikidata item) stands in for a broader topic, and its articles can differ in scope "
    "and depth between languages.",
    "A language edition is not a country or a market; for example, English Wikipedia is read worldwide, "
    "including by learners.",
    "Only traffic Wikimedia classifies as human ('user') is counted; some automated traffic is misclassified, "
    "and classification changes can shift a series.",
    "Views of redirects and of earlier titles of a renamed article are not included.",
    "Whole-Wikipedia traffic changes over time; compare project_growth_pct and topic_share_growth_pct "
    "before attributing a change to the topic.",
]


def site_id(code):
    return code.replace("-", "_") + "wiki"


def search_url(query, pivot, limit):
    params = {"action": "query", "format": "json", "formatversion": "2", "generator": "search",
              "gsrsearch": query, "gsrnamespace": "0", "gsrlimit": str(limit + 5), "redirects": "1",
              "prop": "pageprops|description", "ppprop": "wikibase_item|disambiguation"}
    return f"https://{pivot}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)


def entities_url(qids, codes, with_labels=False):
    params = {"action": "wbgetentities", "format": "json", "ids": "|".join(qids),
              "props": "labels|descriptions|sitelinks" if with_labels else "sitelinks",
              "sitefilter": "|".join(site_id(c) for c in codes)}
    if with_labels:
        params["languages"] = "en"
    return f"{WIKIDATA_API}?" + urllib.parse.urlencode(params)


def per_article_url(code, title, first, last):
    start, end = api_range(first, last)
    return f"{PAGEVIEWS_API}/per-article/{code}.wikipedia.org/all-access/user/{title_path(title)}/monthly/{start}/{end}"


def aggregate_url(code, first, last):
    start, end = api_range(first, last)
    return f"{PAGEVIEWS_API}/aggregate/{code}.wikipedia.org/all-access/user/monthly/{start}/{end}"


def error_result(code, message, hint):
    return {"schema_version": SCHEMA_VERSION, "status": "error", "error": {"code": code, "message": message, "hint": hint}}


def to_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def run_resolve(query, pivot_language="en", languages=(), limit=5):
    query, pivot_language = query.strip(), pivot_language.strip().lower()
    if not query:
        raise UsageError("--query must not be empty")
    if not is_valid_language(pivot_language):
        raise UsageError(f"--pivot-lang is not a Wikipedia language code: {pivot_language!r}")
    if not 1 <= limit <= 10:
        raise UsageError(f"--limit must be between 1 and 10, got {limit}")
    languages = normalize_languages(languages)
    candidates, excluded = parse_search(get_json(search_url(query, pivot_language, limit)) or {}, limit)
    for candidate in candidates:
        candidate["language"] = pivot_language

    invalid = [c for c in languages if not is_valid_language(c)]
    checkable = [c for c in languages if c not in invalid]
    if candidates and checkable:
        data = get_json(entities_url([c["qid"] for c in candidates], checkable)) or {}
        rejected = parse_rejected_sites(data)
        invalid = [c for c in languages if c in invalid or site_id(c) in rejected]
        checkable = [c for c in checkable if c not in invalid]
        for candidate in candidates:
            sitelinks = data.get("entities", {}).get(candidate["qid"], {}).get("sitelinks", {})
            candidate["available_languages"] = [c for c in checkable if site_id(c) in sitelinks]
            candidate["missing_languages"] = [c for c in checkable if site_id(c) not in sitelinks]
    warnings = [warning("invalid_language", f"Not Wikipedia language codes: {', '.join(invalid)}.", LANGUAGE_HINT,
                        languages=invalid)] if invalid else []

    if not candidates:
        next_step = "No candidates. Try other wording, or --pivot-lang in the language the user wrote the topic in."
    else:
        next_step = ("Pick the candidate whose meaning best matches the user's topic (the list is in search order, "
                     "not ranked by suitability; existing in more languages does not make it a better proxy) and tell "
                     "the user which article is the proxy. It can only be analyzed in its available_languages. "
                     "Then run analyze --qid <qid>.")
    return {"schema_version": SCHEMA_VERSION, "status": "ok", "query": query, "pivot_language": pivot_language,
            "candidates": candidates, "excluded": excluded, "warnings": warnings, "next_step": next_step}


def default_output_dir(qid, languages, first, last):
    codes = "-".join(sorted(c for c in languages if is_valid_language(c)))
    return Path(DEFAULT_OUTPUT_ROOT) / f"{qid}_{codes}_{format_month(first)}_{format_month(last)}"


def write_monthly_csv(path, series, months):
    labels = [format_month(m) for m in months]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "article", "month", "views", "project_views"])
        for code, title, views, project in series:
            for label, v, p in zip(labels, views, project):
                writer.writerow([code, title, label, "" if v is None else v, "" if p is None else p])


def run_analyze(qid, languages, months=24, end_month=None, topic=None, assumptions=(), output=None, today=None):
    qid = normalize_qid(qid)
    languages = normalize_languages(languages)
    if not languages:
        raise UsageError("--languages needs at least one Wikipedia language code")
    first, last = resolve_period(end_month, months, today or dt.datetime.now(dt.UTC).date())

    valid = [c for c in languages if is_valid_language(c)]
    entity, rejected, top_warnings = None, set(), []
    if valid:
        data = get_json(entities_url([qid], valid, with_labels=True)) or {}
        entity = parse_entity(data, qid)
        if entity is None:
            return error_result("qid_not_found", f"Wikidata has no item {qid}.",
                                "Run resolve to find the item id (QID) for the topic.")
        rejected = parse_rejected_sites(data)
        if entity["id"] != qid:
            top_warnings.append(warning("qid_redirected", f"{qid} was merged into {entity['id']}; using {entity['id']}."))
    sitelinks = entity["sitelinks"] if entity else {}
    with_article = [c for c in valid if site_id(c) not in rejected and site_id(c) in sitelinks]

    # Whole-Wikipedia totals appear only once a month is complete and processed, so they tell us
    # whether the default end month is published yet (per-article data would include a partial month).
    project_cache = {}
    if with_article and end_month is None:
        try:
            probe = get_json(aggregate_url(with_article[0], first - 1, last))
        except ApiError:
            probe = None  # the per-language requests below report the failure
        if probe is not None:
            items = probe.get("items", [])
            if last not in {month_of(i["timestamp"]) for i in items}:
                first, last = first - 1, last - 1
                top_warnings.append(warning("latest_month_not_published",
                                            f"Wikimedia has not published {format_month(last + 1)} yet, so the "
                                            f"window ends at {format_month(last)}."))
            project_cache[with_article[0]] = items
    window = list(range(first, last + 1))

    rows, series = [], []
    for code in languages:
        row = {"language": code, "status": None, "article": None, "url": None, **dict.fromkeys(METRIC_KEYS),
               "trend_consistency": "insufficient_data", "warnings": []}
        rows.append(row)
        if code not in valid or site_id(code) in rejected:
            row["status"] = "invalid_language"
            row["warnings"].append(warning("invalid_language", f"{code!r} is not a Wikipedia language code.", LANGUAGE_HINT))
            continue
        if site_id(code) not in sitelinks:
            row["status"] = "no_article"
            row["warnings"].append(warning(
                "no_article", f"{entity['id']} has no article on {code}.wikipedia.org.",
                f"Tell the user; or run resolve with --languages {code} to find a proxy that exists in this language."))
            continue
        title = sitelinks[site_id(code)]
        row.update(article=title, url=f"https://{code}.wikipedia.org/wiki/{title_path(title)}")
        try:
            data = get_json(per_article_url(code, title, first, last))
        except ApiError as err:
            row["status"] = "api_error"
            row["warnings"].append(warning("api_error", str(err), NETWORK_HINT))
            continue
        if data is None:
            row["status"] = "no_data"
            row["warnings"].append(warning("no_data", f"No pageview data for {title!r} on {code}.wikipedia.org in this period."))
            continue
        if code not in project_cache:
            try:
                project_cache[code] = (get_json(aggregate_url(code, first, last)) or {}).get("items", [])
            except ApiError:
                project_cache[code] = []  # reported as project_baseline_unavailable
        views = monthly_values(data.get("items", []), window)
        project = monthly_values(project_cache[code], window)
        metrics, metric_warnings = language_metrics(views, project, window)
        row.update(metrics)
        row["warnings"].extend(metric_warnings)
        row["status"] = "insufficient_data" if metrics["trend_consistency"] == "insufficient_data" else "ok"
        series.append((code, title, views, project))

    resolved = entity["id"] if entity else qid
    label, description = (entity["label"], entity["description"]) if entity else (None, None)
    result = {
        "schema_version": SCHEMA_VERSION, "status": None, "topic": topic, "assumptions": list(assumptions),
        "topic_proxy": {"qid": resolved, "label": label, "description": description,
                        "wikidata_url": f"https://www.wikidata.org/wiki/{resolved}"},
        "period": {"start": format_month(first), "end": format_month(last), "months": len(window),
                   "previous_12m": f"{format_month(last - 23)}..{format_month(last - 12)}",
                   "latest_12m": f"{format_month(last - 11)}..{format_month(last)}"},
        "results": rows, "warnings": top_warnings, "limitations": LIMITATIONS,
        "retrieved_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if not series:
        error = error_result("no_usable_data", "None of the requested languages returned pageview data for this item.",
                             "Check each language's warnings; try other languages or another candidate from resolve.")
        return {**error, **{k: v for k, v in result.items() if k not in error}}
    result["status"] = "ok" if all(r["status"] == "ok" for r in rows) else "partial"
    out_dir = (Path(output) if output else default_output_dir(resolved, languages, first, last)).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    result["artifacts"] = {"result": str(out_dir / "result.json"), "data": str(out_dir / "monthly.csv")}
    write_monthly_csv(out_dir / "monthly.csv", series, window)
    (out_dir / "result.json").write_text(to_json(result) + "\n", encoding="utf-8")
    return result


# --- CLI ---

class JsonArgumentParser(argparse.ArgumentParser):
    """argparse that raises UsageError (reported as JSON) instead of printing usage and exiting."""

    def error(self, message):
        raise UsageError(message)


def build_parser():
    parser = JsonArgumentParser(prog="wiki_interest.py", description="Topic-interest analysis from Wikipedia pageviews.")
    commands = parser.add_subparsers(dest="command", required=True)

    resolve = commands.add_parser("resolve", help="find candidate articles (Wikidata QIDs) for a topic")
    resolve.add_argument("--query", required=True, help="topic words, e.g. 'intermittent fasting'")
    resolve.add_argument("--pivot-lang", default="en", help="Wikipedia to search (default: en)")
    resolve.add_argument("--languages", nargs="+", default=[], help="also report which of these languages have an article")
    resolve.add_argument("--limit", type=int, default=5, help="number of candidates, 1-10 (default: 5)")
    resolve.set_defaults(run=lambda a: run_resolve(a.query, a.pivot_lang, a.languages, a.limit))

    analyze = commands.add_parser("analyze", help="monthly pageview trend metrics for one QID in several languages")
    analyze.add_argument("--qid", required=True, help="Wikidata item id from resolve, e.g. Q1666254")
    analyze.add_argument("--languages", nargs="+", required=True, help=f"Wikipedia language codes (up to {MAX_LANGUAGES})")
    analyze.add_argument("--months", type=int, default=24, help=f"window length, {MIN_MONTHS}-{MAX_MONTHS} (default: 24)")
    analyze.add_argument("--end-month", help="last month of the window, YYYY-MM (default: last complete month)")
    analyze.add_argument("--topic", help="the user's own words for the topic, recorded in the outputs")
    analyze.add_argument("--assumption", action="append", default=[], help="an assumption to record (repeatable)")
    analyze.add_argument("--output", help=f"output folder (default: ./{DEFAULT_OUTPUT_ROOT}/<qid>_<languages>_<start>_<end>)")
    analyze.set_defaults(run=lambda a: run_analyze(a.qid, a.languages, a.months, a.end_month, a.topic, a.assumption, a.output))
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        result = args.run(args)
        code = 1 if result["status"] == "error" else 0
    except UsageError as err:
        result, code = error_result("invalid_arguments", str(err), "Run the command with --help to see the options."), 2
    except ApiError as err:
        result, code = error_result("api_error", str(err), NETWORK_HINT), 1
    print(to_json(result))
    return code


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
