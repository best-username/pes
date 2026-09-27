"""Offline, deterministic unit tests for scripts/wiki_interest.py.

Expected values are literals derived by hand (or, for the real Czech series, by hand and
cross-checked with an independent throwaway script) - never computed with the code under test.
Run: uv run --frozen python -m unittest discover -s tests -v
"""

import csv
import email.message
import io
import json
import ssl
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import wiki_interest as wi  # noqa: E402

TODAY = date(2026, 9, 26)


def month(text):
    return wi.parse_month(text)


class MonthTests(unittest.TestCase):
    def test_last_complete_month_is_the_month_before_today(self):
        self.assertEqual(wi.format_month(wi.last_complete_month(TODAY)), "2026-08")

    def test_last_complete_month_wraps_the_year_in_january(self):
        self.assertEqual(wi.format_month(wi.last_complete_month(date(2026, 1, 5))), "2025-12")

    def test_api_range_covers_whole_months_including_leap_february(self):
        self.assertEqual(wi.api_range(month("2024-02"), month("2024-02")), ("20240201", "20240229"))
        self.assertEqual(wi.api_range(month("2024-09"), month("2026-08")), ("20240901", "20260831"))

    def test_parse_month_rejects_malformed_input(self):
        for bad in ("2026-13", "2026-00", "2026-8", "26-08", "2026/08", ""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                wi.parse_month(bad)


class PeriodTests(unittest.TestCase):
    def period(self, end_month, months):
        start, end = wi.resolve_period(end_month, months, TODAY)
        return wi.format_month(start), wi.format_month(end)

    def test_default_period_is_the_last_24_complete_months(self):
        self.assertEqual(self.period(None, 24), ("2024-09", "2026-08"))

    def test_months_need_not_be_a_multiple_of_12(self):
        self.assertEqual(self.period("2025-12", 30), ("2023-07", "2025-12"))

    def test_rejects_the_current_or_a_future_month_as_end(self):
        for end_month in ("2026-09", "2027-01"):
            with self.subTest(end_month=end_month), self.assertRaises(wi.UsageError):
                self.period(end_month, 24)

    def test_rejects_months_outside_24_to_120(self):
        for months in (23, 121):
            with self.subTest(months=months), self.assertRaises(wi.UsageError):
                self.period(None, months)

    def test_window_may_start_at_but_not_before_the_first_pageviews_month(self):
        self.assertEqual(self.period("2017-06", 24), ("2015-07", "2017-06"))
        with self.assertRaises(wi.UsageError):
            self.period("2017-05", 24)

    def test_malformed_end_month_is_a_usage_error(self):
        with self.assertRaises(wi.UsageError):
            self.period("2026-8", 24)


class InputTests(unittest.TestCase):
    def test_languages_accept_commas_case_underscores_and_are_deduplicated(self):
        self.assertEqual(wi.normalize_languages(["PL,cs", "cs", " zh_yue "]), ["pl", "cs", "zh-yue"])

    def test_up_to_20_languages_are_accepted(self):
        codes = [f"a{chr(97 + i)}" for i in range(21)]
        self.assertEqual(len(wi.normalize_languages(codes[:20])), 20)
        with self.assertRaises(wi.UsageError):
            wi.normalize_languages(codes)

    def test_codes_that_could_alter_a_url_are_invalid(self):
        for code in ("evil.com/x", "pl.wikipedia.org", "pl?x=1", "../etc", "p", ""):
            with self.subTest(code=code):
                self.assertFalse(wi.is_valid_language(code))
        for code in ("pl", "simple", "zh-min-nan", "be-tarask"):
            with self.subTest(code=code):
                self.assertTrue(wi.is_valid_language(code))

    def test_qid_is_normalized_and_validated(self):
        self.assertEqual(wi.normalize_qid(" q333 "), "Q333")
        for bad in ("Q0", "333", "Q12a", "P31", ""):
            with self.subTest(bad=bad), self.assertRaises(wi.UsageError):
                wi.normalize_qid(bad)

    def test_titles_are_fully_percent_encoded_for_the_pageviews_path(self):
        self.assertEqual(wi.title_path("AC/DC"), "AC%2FDC")
        self.assertEqual(wi.title_path("Přerušovaný půst"), "P%C5%99eru%C5%A1ovan%C3%BD_p%C5%AFst")


# Real data: cs.wikipedia "Přerušovaný půst" (Q1666254) and all of cs.wikipedia, human views,
# 2024-09..2026-08, as returned by the Pageviews API on 2026-09-26.
CS_VIEWS = [393, 634, 329, 294, 489, 272, 366, 958, 225, 238, 157, 386,
            270, 141, 151, 218, 474, 196, 179, 135, 109, 115, 91, 119]
CS_PROJECT = [62292789, 70881496, 68852170, 70360761, 83396601, 69753016,
              74887886, 67010206, 73630159, 56271438, 61159851, 57515129,
              57306454, 66546281, 72883460, 59967317, 67410000, 58306397,
              58040192, 54688383, 59792880, 53683305, 53131065, 51467770]


def window(n, end="2026-08"):
    last = month(end)
    return list(range(last - n + 1, last + 1))


def metrics(views, project=None):
    """language_metrics over a window ending 2026-08 -> (metrics, set of warning codes)."""
    project = project if project is not None else [1_000_000] * len(views)
    result, warnings = wi.language_metrics(views, project, window(len(views)))
    return result, {w["code"] for w in warnings}


class RealSeriesTests(unittest.TestCase):
    def setUp(self):
        self.r, self.warnings = metrics(CS_VIEWS, CS_PROJECT)

    def test_totals_and_growth(self):
        r = self.r
        self.assertEqual((r["total_views"], r["previous_12m_views"], r["latest_12m_views"]), (6939, 4741, 2198))
        self.assertEqual(r["growth_pct"], -53.6)
        self.assertEqual(r["avg_monthly_views_latest_12m"], 183)

    def test_month_by_month_changes(self):
        r = self.r
        self.assertEqual(r["yoy_pct_by_month"]["2025-09"], -31.3)  # 270 vs 393
        self.assertEqual(r["yoy_pct_by_month"]["2026-04"], -85.9)  # 135 vs 958
        self.assertEqual((r["positive_yoy_months"], r["negative_yoy_months"]), (0, 12))
        self.assertEqual(r["median_yoy_pct"], -51.3)

    def test_concentration_and_leave_one_out(self):
        r = self.r
        self.assertEqual((r["largest_month"], r["largest_month_share_pct"]), ("2026-01", 21.6))
        self.assertEqual((r["top_contributor_month"], r["growth_excl_top_month_pct"]), ("2026-04", -45.5))
        self.assertFalse(r["spike_driven"])

    def test_seasonal_january_does_not_block_a_strong_decline(self):
        # January is 21.6% of the latest year (the old ">20% of the year" rule would say "mixed").
        self.assertEqual((self.r["trend_direction"], self.r["trend_consistency"]), ("down", "strong"))

    def test_reasons_quote_the_evidence(self):
        text = " ".join(self.r["consistency_reasons"])
        for fragment in ("12 of 12", "2026-04", "-45.5%"):
            self.assertIn(fragment, text)

    def test_project_baseline_and_topic_share(self):
        r = self.r
        self.assertEqual((r["previous_12m_project_views"], r["latest_12m_project_views"]), (816011502, 713223504))
        self.assertEqual(r["project_growth_pct"], -12.6)
        self.assertEqual((r["previous_topic_views_per_million"], r["latest_topic_views_per_million"]), (5.81, 3.08))
        self.assertEqual(r["topic_share_growth_pct"], -47.0)  # growth minus project growth would be -41.0
        self.assertEqual(self.warnings, set())


class ConsistencyTests(unittest.TestCase):
    def test_steady_growth_is_strong(self):
        r, _ = metrics([100] * 12 + [110] * 12)
        self.assertEqual((r["growth_pct"], r["positive_yoy_months"], r["median_yoy_pct"]), (10.0, 12, 10.0))
        self.assertEqual((r["trend_direction"], r["trend_consistency"], r["spike_driven"]), ("up", "strong", False))

    def test_seasonal_peak_does_not_block_strong(self):
        r, _ = metrics([100] * 11 + [400] + [110] * 11 + [440])
        self.assertEqual(r["largest_month_share_pct"], 26.7)
        self.assertEqual(r["trend_consistency"], "strong")

    def test_growth_from_one_spike_month_is_weak_and_spike_driven(self):
        r, _ = metrics([100] * 12 + [100] * 11 + [700])
        self.assertEqual((r["growth_pct"], r["positive_yoy_months"], r["median_yoy_pct"]), (50.0, 1, 0.0))
        self.assertEqual((r["top_contributor_month"], r["growth_excl_top_month_pct"]), ("2026-08", 0.0))
        self.assertEqual((r["trend_consistency"], r["spike_driven"]), ("weak", True))

    def test_breadth_thresholds(self):
        for up_months, label in ((9, "strong"), (8, "mixed"), (7, "mixed"), (6, "weak")):
            with self.subTest(up_months=up_months):
                r, _ = metrics([100] * 12 + [120] * up_months + [99] * (12 - up_months))
                self.assertEqual((r["trend_direction"], r["trend_consistency"]), ("up", label))

    def test_unchanged_months_are_not_evidence_for_the_trend(self):
        r, _ = metrics([100] * 12 + [120] * 6 + [100] * 3 + [95] * 3)
        self.assertEqual((r["growth_pct"], r["positive_yoy_months"], r["negative_yoy_months"]), (8.8, 6, 3))
        self.assertEqual(r["trend_consistency"], "weak")  # 6 aligned months; the 3 unchanged ones do not count

    def test_a_trend_that_needs_its_biggest_month_is_lowered_one_level(self):
        # broad (10 of 12) but not robust: strong -> mixed
        r, _ = metrics([100] * 12 + [101] * 9 + [95] * 2 + [300])
        self.assertEqual((r["growth_pct"], r["positive_yoy_months"], r["median_yoy_pct"]), (16.6, 10, 1.0))
        self.assertEqual(r["growth_excl_top_month_pct"], -0.1)
        self.assertEqual((r["trend_consistency"], r["spike_driven"]), ("mixed", True))
        # moderately broad (8 of 12) and not robust: mixed -> weak
        r, _ = metrics([100] * 12 + [101] * 7 + [99] * 4 + [300])
        self.assertEqual((r["growth_pct"], r["positive_yoy_months"], r["growth_excl_top_month_pct"]), (16.9, 8, 0.3))
        self.assertEqual((r["trend_consistency"], r["spike_driven"]), ("weak", True))

    def test_flat_change_is_not_applicable(self):
        r, _ = metrics([100] * 12 + [102] * 12)
        self.assertEqual((r["growth_pct"], r["trend_direction"], r["trend_consistency"]), (2.0, "flat", "not_applicable"))
        self.assertIsNone(r["spike_driven"])
        self.assertIsNone(r["growth_excl_top_month_pct"])

    def test_flat_band_boundaries(self):
        cases = (([100] * 12 + [105] * 12, "up"), ([100] * 12 + [95] * 12, "down"), ([1000] * 12 + [1049] * 12, "flat"))
        for views, direction in cases:
            with self.subTest(direction=direction):
                self.assertEqual(metrics(views)[0]["trend_direction"], direction)

    def test_tiny_negative_change_is_reported_as_zero_not_negative_zero(self):
        r, _ = metrics([2500] * 12 + [2499] * 12)
        self.assertEqual(repr(r["growth_pct"]), "0.0")

    def test_largest_month_ties_resolve_to_the_earliest_month(self):
        r, _ = metrics([100] * 24)
        self.assertEqual(r["largest_month"], "2025-09")


class MissingAndZeroDataTests(unittest.TestCase):
    def test_missing_month_in_latest_24_makes_trend_insufficient(self):
        r, warnings = metrics([100] * 23 + [None])
        self.assertEqual(r["missing_months"], ["2026-08"])
        self.assertIsNone(r["total_views"])
        self.assertIsNone(r["growth_pct"])
        self.assertEqual(r["trend_consistency"], "insufficient_data")
        self.assertIn("missing_months", warnings)

    def test_zero_previous_year_gives_no_growth_instead_of_dividing_by_zero(self):
        r, warnings = metrics([0] * 12 + [10] * 12)
        self.assertIsNone(r["growth_pct"])
        self.assertEqual(r["trend_consistency"], "insufficient_data")
        self.assertIn("zero_baseline", warnings)

    def test_single_zero_month_blocks_its_yoy_but_not_annual_growth(self):
        r, warnings = metrics([100] * 11 + [0] + [110] * 12)
        self.assertEqual(r["growth_pct"], 20.0)
        self.assertIsNone(r["yoy_pct_by_month"]["2026-08"])
        self.assertIsNone(r["median_yoy_pct"])
        self.assertEqual(r["trend_consistency"], "insufficient_data")
        self.assertIn("zero_baseline", warnings)

    def test_zero_views_are_data_not_missing(self):
        r, _ = metrics([5] * 12 + [0] + [5] * 11)
        self.assertEqual(r["missing_months"], [])
        self.assertEqual(r["latest_12m_views"], 55)


class ProjectBaselineTests(unittest.TestCase):
    def test_topic_share_growth_is_the_ratio_of_shares(self):
        r, _ = metrics([100] * 12 + [120] * 12, [1_000_000] * 12 + [800_000] * 12)
        self.assertEqual((r["growth_pct"], r["project_growth_pct"]), (20.0, -20.0))
        self.assertEqual((r["previous_topic_views_per_million"], r["latest_topic_views_per_million"]), (100.0, 150.0))
        self.assertEqual(r["topic_share_growth_pct"], 50.0)  # growth minus project growth would be 40.0

    def test_views_per_million_have_two_decimals_from_one_upward_and_three_below(self):
        # 133.177 reads like the integer 133,177; 133.18 cannot
        for raw, published in ((133.177, 133.18), (3.082, 3.08), (0.799, 0.799), (0.103, 0.103), (None, None)):
            self.assertEqual(wi.rnd_per_million(raw), published)

    def test_change_that_mirrors_the_whole_wiki_is_flagged(self):
        r, warnings = metrics([100] * 12 + [90] * 12, [1_000_000] * 12 + [900_000] * 12)
        self.assertEqual((r["growth_pct"], r["topic_share_growth_pct"]), (-10.0, 0.0))
        self.assertIn("tracks_platform_trend", warnings)

    def test_missing_project_month_leaves_article_metrics_intact(self):
        r, warnings = metrics([100] * 12 + [110] * 12, [1_000_000] * 23 + [None])
        self.assertEqual(r["growth_pct"], 10.0)
        self.assertIsNone(r["project_growth_pct"])
        self.assertIsNone(r["topic_share_growth_pct"])
        self.assertIn("project_baseline_unavailable", warnings)


class WarningTests(unittest.TestCase):
    def test_low_volume(self):
        self.assertIn("low_volume", metrics([50] * 12 + [60] * 12)[1])
        self.assertNotIn("low_volume", metrics([500] * 12 + [600] * 12)[1])

    def test_unusually_low_months_flag_a_possible_history_discontinuity(self):
        self.assertIn("possible_history_discontinuity", metrics([4, 2] + [1000] * 22)[1])
        self.assertNotIn("possible_history_discontinuity", metrics([400, 300] + [1000] * 22)[1])


class IndexTests(unittest.TestCase):
    def test_index_is_relative_to_the_previous_12_month_average(self):
        # previous 12 months average 100 (50 and 150 alternating), so index == views
        self.assertEqual(wi.index_series([50, 150] * 6 + [120] * 12), [50.0, 150.0] * 6 + [120.0] * 12)
        self.assertEqual(wi.index_series([200] * 12 + [100] * 12)[-1], 50.0)
        # 36 months: the baseline is the previous 12 months (100), not the first 12 (10)
        self.assertEqual(wi.index_series([10] * 12 + [100] * 12 + [120] * 12)[-1], 120.0)

    def test_no_index_without_a_complete_nonzero_previous_12_months(self):
        self.assertIsNone(wi.index_series([None] + [100] * 23))
        self.assertIsNone(wi.index_series([0] * 12 + [100] * 12))


class MessageTests(unittest.TestCase):
    def test_long_month_lists_are_summarized_without_trailing_ellipsis(self):
        self.assertEqual(wi.summarize(["2024-09", "2024-10"]), "2024-09, 2024-10")
        self.assertEqual(wi.summarize([f"2024-{m:02d}" for m in range(1, 10)]),
                         "2024-01, 2024-02, 2024-03, 2024-04, 2024-05, 2024-06 and 3 more")


class LongerWindowTests(unittest.TestCase):
    def test_36_months_total_all_months_and_compare_first_with_latest_year(self):
        r, _ = metrics([100] * 12 + [100] * 12 + [120] * 12)
        self.assertEqual((r["total_views"], r["first_12m_views"], r["first_to_latest_12m_growth_pct"]), (3840, 1200, 20.0))
        self.assertEqual(r["growth_pct"], 20.0)

    def test_30_months_use_the_most_recent_24_for_latest_vs_previous(self):
        r, _ = metrics([50] * 6 + [100] * 12 + [110] * 12)
        self.assertEqual((r["total_views"], r["previous_12m_views"], r["growth_pct"]), (2820, 1200, 10.0))
        self.assertEqual((r["first_12m_views"], r["first_to_latest_12m_growth_pct"]), (900, 46.7))

    def test_24_month_window_has_no_separate_first_year_comparison(self):
        r, _ = metrics([100] * 12 + [110] * 12)
        self.assertIsNone(r["first_12m_views"])
        self.assertIsNone(r["first_to_latest_12m_growth_pct"])


# Response shapes recorded from the live APIs on 2026-09-26 (trimmed to the parts noted).
SEARCH_RESPONSE = {  # en.wikipedia generator=search "learning English", gsrlimit=3, plus one unlinked page
    "batchcomplete": True,
    "continue": {"gsroffset": 3, "continue": "gsroffset||"},
    "query": {"pages": [
        {"pageid": 415406, "ns": 0, "title": "English as a second or foreign language", "index": 2,
         "pageprops": {"wikibase_item": "Q130192"},
         "description": "Use of English by speakers with different native languages", "descriptionsource": "local"},
        {"pageid": 11178098, "ns": 0, "title": "BBC Learning English", "index": 3,
         "pageprops": {"wikibase_item": "Q2876734"},
         "description": "Department of the BBC World Service", "descriptionsource": "local"},
        {"pageid": 21331306, "ns": 0, "title": "Learning English", "index": 1,
         "pageprops": {"disambiguation": "", "wikibase_item": "Q16871974"},
         "description": "Topics referred to by the same term", "descriptionsource": "local"},
        {"pageid": 1, "ns": 0, "title": "Unlinked page", "index": 4},
    ]},
}
ENTITY_RESPONSE = {  # wbgetentities Q1666254, sitefilter=plwiki|cswiki|nbwiki|xxwiki
    "warnings": {"wbgetentities": {"*": 'Unrecognized values for parameter "sitefilter": nbwiki, xxwiki'}},
    "entities": {"Q1666254": {
        "type": "item", "id": "Q1666254",
        "labels": {"en": {"language": "en", "value": "intermittent fasting"}},
        "descriptions": {"en": {"language": "en", "value": "a diet that cycles between a period of fasting and non-fasting"}},
        "sitelinks": {"cswiki": {"site": "cswiki", "title": "Přerušovaný půst", "badges": []}}}},
    "success": 1,
}
REDIRECTED_ENTITY = {  # wbgetentities for a merged item
    "entities": {"Q141516907": {
        "redirects": {"from": "Q141516907", "to": "Q13028547"}, "type": "item", "id": "Q13028547",
        "labels": {"en": {"language": "en", "value": "Memorial Complex «Katyusha» in Orsha"}},
        "descriptions": {"en": {"language": "en", "value": "monument in Orsha, Belarus"}}, "sitelinks": {}}},
    "success": 1,
}
MISSING_ENTITY = {
    "error": {"code": "no-such-entity", "info": 'Could not find an entity with the ID "Q999999999999".',
              "id": "Q999999999999", "messages": [{"name": "wikibase-api-no-such-entity", "parameters": ["Q999999999999"]}]},
    "servedby": "mw-api-ext.eqiad.main",
}
AVAILABILITY_RESPONSE = {  # wbgetentities Q130192|Q2876734, props=sitelinks, sitefilter=eswiki|plwiki|frwiki|nbwiki
    "warnings": {"wbgetentities": {"*": 'Unrecognized value for parameter "sitefilter": nbwiki'}},
    "entities": {
        "Q130192": {"type": "item", "id": "Q130192", "sitelinks": {
            "eswiki": {"site": "eswiki", "title": "Inglés como segunda lengua", "badges": []}}},
        "Q2876734": {"type": "item", "id": "Q2876734", "sitelinks": {
            "eswiki": {"site": "eswiki", "title": "BBC Learning English", "badges": []},
            "frwiki": {"site": "frwiki", "title": "BBC Learning English", "badges": []}}}},
    "success": 1,
}


def pv_item(timestamp, views, project="cs.wikipedia", article="Přerušovaný_půst"):
    """One per-article item as the Pageviews API returns it (aggregate items just lack 'article')."""
    item = {"project": project, "article": article, "granularity": "monthly", "timestamp": timestamp,
            "access": "all-access", "agent": "user", "views": views}
    if article is None:
        del item["article"]
    return item


PER_ARTICLE_SAMPLE = {"items": [pv_item("2026060100", 115), pv_item("2026070100", 91),
                                pv_item("2026080100", 119), pv_item("2026090100", 60)]}


class ParsingTests(unittest.TestCase):
    def test_search_candidates_follow_rank_and_skip_disambiguation_and_unlinked_pages(self):
        candidates, excluded = wi.parse_search(SEARCH_RESPONSE, limit=5)
        self.assertEqual([c["qid"] for c in candidates], ["Q130192", "Q2876734"])
        self.assertEqual(candidates[0], {"qid": "Q130192", "title": "English as a second or foreign language",
                                         "description": "Use of English by speakers with different native languages"})
        self.assertEqual(excluded, {"disambiguation_pages": 1, "without_qid": 1})

    def test_search_limit(self):
        candidates, _ = wi.parse_search(SEARCH_RESPONSE, limit=1)
        self.assertEqual([c["qid"] for c in candidates], ["Q130192"])

    def test_search_without_results(self):
        self.assertEqual(wi.parse_search({"batchcomplete": True}, limit=5)[0], [])

    def test_sites_rejected_by_wikidata_are_read_from_its_warning(self):
        self.assertEqual(wi.parse_rejected_sites(ENTITY_RESPONSE), {"nbwiki", "xxwiki"})
        self.assertEqual(wi.parse_rejected_sites(AVAILABILITY_RESPONSE), {"nbwiki"})
        self.assertEqual(wi.parse_rejected_sites({"entities": {}, "success": 1}), set())

    def test_entity_label_description_and_sitelinks(self):
        self.assertEqual(wi.parse_entity(ENTITY_RESPONSE, "Q1666254"), {
            "id": "Q1666254", "label": "intermittent fasting",
            "description": "a diet that cycles between a period of fasting and non-fasting",
            "sitelinks": {"cswiki": "Přerušovaný půst"}})

    def test_merged_item_resolves_to_its_target(self):
        self.assertEqual(wi.parse_entity(REDIRECTED_ENTITY, "Q141516907")["id"], "Q13028547")

    def test_unknown_item_is_none(self):
        self.assertIsNone(wi.parse_entity(MISSING_ENTITY, "Q999999999999"))

    def test_monthly_values_align_to_the_window_and_drop_the_partial_current_month(self):
        # 2026-09 (60 views) was still running when recorded; 2026-05 has no row at all
        self.assertEqual(wi.monthly_values(PER_ARTICLE_SAMPLE["items"], window(4)), [None, 115, 91, 119])


def http_error(code, body=b"", retry_after=None):
    headers = email.message.Message()
    if retry_after:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError("https://wikimedia.org/api", code, "error", headers, io.BytesIO(body))


class HttpTests(unittest.TestCase):
    def get(self, *outcomes):
        """get_json with the network replaced by queued outcomes -> (result or ApiError, requests, sleeps)."""
        queue, requests, sleeps = list(outcomes), [], []

        def urlopen(request, timeout):
            requests.append(request)
            outcome = queue.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return io.BytesIO(outcome)

        with mock.patch("urllib.request.urlopen", urlopen), mock.patch("time.sleep", sleeps.append):
            try:
                result = wi.get_json("https://wikimedia.org/api/rest_v1/metrics/x")
            except wi.ApiError as err:
                result = err
        return result, requests, sleeps

    def test_rate_limited_request_waits_for_retry_after_then_succeeds(self):
        result, requests, sleeps = self.get(http_error(429, retry_after="21"), b'{"items": []}')
        self.assertEqual((result, len(requests), sleeps), ({"items": []}, 2, [21.0]))

    def test_every_request_identifies_the_client_with_a_contact_url(self):
        _, requests, _ = self.get(b"{}")
        self.assertIn("https://github.com/", requests[0].get_header("User-agent"))

    def test_not_found_means_no_data_and_is_not_retried(self):
        self.assertEqual(self.get(http_error(404)), (None, mock.ANY, []))

    def test_client_errors_fail_fast_with_the_server_message(self):
        result, requests, _ = self.get(http_error(403, b"Please set a user-agent and respect our robot policy"))
        self.assertIsInstance(result, wi.ApiError)
        self.assertIn("403", str(result))
        self.assertIn("Please set a user-agent", str(result))
        self.assertEqual(len(requests), 1)

    def test_gives_up_after_three_attempts_waiting_5_then_10_seconds(self):
        result, requests, sleeps = self.get(http_error(429), http_error(503), http_error(500))
        self.assertIsInstance(result, wi.ApiError)
        self.assertEqual((len(requests), sleeps), (3, [5.0, 10.0]))

    def test_long_or_non_numeric_retry_after(self):
        self.assertEqual(self.get(http_error(429, retry_after="600"), b"{}")[2], [60.0])
        self.assertEqual(self.get(http_error(503, retry_after="Wed, 21 Oct 2026 07:28:00 GMT"), b"{}")[2], [5.0])

    def test_network_errors_are_retried(self):
        result, requests, _ = self.get(urllib.error.URLError("timed out"), b'{"ok": 1}')
        self.assertEqual((result, len(requests)), ({"ok": 1}, 2))

    def test_certificate_errors_fail_fast_with_a_hint(self):
        result, requests, _ = self.get(urllib.error.URLError(ssl.SSLCertVerificationError(1, "certificate verify failed")))
        self.assertIsInstance(result, wi.ApiError)
        self.assertIn("SSL_CERT_FILE", str(result))
        self.assertEqual(len(requests), 1)

    def test_non_json_response_is_an_api_error(self):
        self.assertIsInstance(self.get(b"<html>maintenance</html>")[0], wi.ApiError)


def timestamps(year, month_, count):
    for _ in range(count):
        yield f"{year:04d}{month_:02d}0100"
        year, month_ = (year + 1, 1) if month_ == 12 else (year, month_ + 1)


def article_items(year, month_, values, project="cs.wikipedia", article="Přerušovaný_půst"):
    return [pv_item(ts, v, project, article) for ts, v in zip(timestamps(year, month_, len(values)), values)]


def project_items(year, month_, values, project="cs.wikipedia"):
    return [pv_item(ts, v, project, None) for ts, v in zip(timestamps(year, month_, len(values)), values)]


# The same item as ENTITY_RESPONSE, requested with sitefilter=plwiki|cswiki (so no warning).
CS_ENTITY = {"entities": {"Q1666254": ENTITY_RESPONSE["entities"]["Q1666254"]}, "success": 1}
UK_CS_ENTITY = {"entities": {"Q1666254": {**ENTITY_RESPONSE["entities"]["Q1666254"], "sitelinks": {
    "cswiki": {"site": "cswiki", "title": "Přerušovaný půst", "badges": []},
    "ukwiki": {"site": "ukwiki", "title": "Інтервальне голодування", "badges": []}}}}, "success": 1}
# 2024-08 (value synthetic) is fetched too: the publication check looks one month further back.
CS_AGGREGATE = project_items(2024, 8, [60_000_000] + CS_PROJECT)
CS_ARTICLE = article_items(2024, 9, CS_VIEWS)


class CommandTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name)
        self.urls = []

    def fake_api(self, entity, aggregate=(), article=(), failing=()):
        """URL-dispatching stand-in for get_json that returns recorded response shapes."""
        def get_json(url):
            self.urls.append(url)
            if any(f"/{code}.wikipedia.org/" in url for code in failing):
                raise wi.ApiError("HTTP 503 from wikimedia.org after 3 attempts")
            if "action=wbgetentities" in url:
                return entity
            if "generator=search" in url:
                return SEARCH_RESPONSE
            if "/aggregate/" in url:
                return {"items": list(aggregate)}
            if "/per-article/" in url:
                return {"items": list(article)}
            raise AssertionError(f"unexpected request: {url}")
        return mock.patch.object(wi, "get_json", get_json)

    def analyze(self, entity, aggregate=CS_AGGREGATE, article=CS_ARTICLE, failing=(), **kwargs):
        with self.fake_api(entity, aggregate, article, failing):
            return wi.run_analyze(today=TODAY, output=str(self.out), **kwargs)


class AnalyzeCommandTests(CommandTestCase):
    def test_partial_result_when_one_language_has_no_article(self):
        result = self.analyze(CS_ENTITY, qid="Q1666254", languages=["pl", "cs"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["topic_proxy"]["qid"], "Q1666254")
        self.assertEqual(result["period"], {"start": "2024-09", "end": "2026-08", "months": 24,
                                            "previous_12m": "2024-09..2025-08", "latest_12m": "2025-09..2026-08"})
        pl, cs = result["results"]
        self.assertEqual((pl["language"], pl["status"], pl["growth_pct"]), ("pl", "no_article", None))
        self.assertEqual([w["code"] for w in pl["warnings"]], ["no_article"])
        self.assertEqual((cs["status"], cs["article"], cs["growth_pct"], cs["topic_share_growth_pct"]),
                         ("ok", "Přerušovaný půst", -53.6, -47.0))

    def test_uses_one_entity_request_plus_two_per_language_over_whole_months(self):
        self.analyze(CS_ENTITY, qid="Q1666254", languages=["pl", "cs"])
        self.assertEqual(len(self.urls), 3)
        self.assertTrue(any(u.endswith("/per-article/cs.wikipedia.org/all-access/user/"
                                       "P%C5%99eru%C5%A1ovan%C3%BD_p%C5%AFst/monthly/20240901/20260831") for u in self.urls))
        self.assertTrue(any(u.endswith("/aggregate/cs.wikipedia.org/all-access/user/monthly/20240801/20260831")
                            for u in self.urls))

    def test_writes_result_json_and_monthly_csv(self):
        result = self.analyze(CS_ENTITY, qid="Q1666254", languages=["pl", "cs"])
        self.assertEqual(json.loads((self.out / "result.json").read_text(encoding="utf-8")), result)
        with (self.out / "monthly.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["language", "article", "month", "views", "project_views"])
        self.assertEqual(rows[1], ["cs", "Přerušovaný půst", "2024-09", "393", "62292789"])
        self.assertEqual(len(rows), 25)
        self.assertEqual(result["artifacts"], {"result": str(self.out / "result.json"), "data": str(self.out / "monthly.csv"),
                                               "report": str(self.out / "report.html")})

    def test_window_moves_back_a_month_when_the_last_one_is_not_published_yet(self):
        aggregate = project_items(2024, 8, [1_000_000] * 24)            # ends 2026-07: 2026-08 not published
        article = article_items(2024, 8, [100] * 12 + [110] * 12 + [55])  # includes a partial 2026-08
        result = self.analyze(CS_ENTITY, aggregate, article, qid="Q1666254", languages=["cs"])
        self.assertEqual((result["period"]["start"], result["period"]["end"]), ("2024-08", "2026-07"))
        self.assertEqual([w["code"] for w in result["warnings"]], ["latest_month_not_published"])
        self.assertEqual(result["results"][0]["growth_pct"], 10.0)
        self.assertTrue(any(u.endswith("/monthly/20240801/20260731") for u in self.urls if "/per-article/" in u))

    def test_explicit_end_month_is_not_moved(self):
        result = self.analyze(CS_ENTITY, qid="Q1666254", languages=["cs"], end_month="2026-08")
        self.assertEqual(result["period"]["end"], "2026-08")
        self.assertEqual(result["warnings"], [])

    def test_invalid_language_codes_become_rows_and_never_reach_a_url(self):
        result = self.analyze(ENTITY_RESPONSE, qid="Q1666254", languages=["pl", "cs", "nb", "xx", "evil.com/x"])
        self.assertEqual([(r["language"], r["status"]) for r in result["results"]],
                         [("pl", "no_article"), ("cs", "ok"), ("nb", "invalid_language"),
                          ("xx", "invalid_language"), ("evil.com/x", "invalid_language")])
        self.assertFalse(any("evil.com" in u for u in self.urls))

    def test_one_failing_language_does_not_stop_the_others(self):
        result = self.analyze(UK_CS_ENTITY, failing=("uk",), qid="Q1666254", languages=["cs", "uk"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual([(r["language"], r["status"]) for r in result["results"]], [("cs", "ok"), ("uk", "api_error")])

    def test_unknown_qid_is_an_error_and_writes_nothing(self):
        result = self.analyze(MISSING_ENTITY, qid="Q999999999999", languages=["cs"])
        self.assertEqual((result["status"], result["error"]["code"]), ("error", "qid_not_found"))
        self.assertEqual(list(self.out.iterdir()), [])

    def test_no_usable_data_in_any_language_is_an_error_that_keeps_the_per_language_reasons(self):
        result = self.analyze(CS_ENTITY, qid="Q1666254", languages=["pl"])
        self.assertEqual((result["status"], result["error"]["code"]), ("error", "no_usable_data"))
        self.assertEqual(result["results"][0]["status"], "no_article")
        self.assertEqual(list(self.out.iterdir()), [])

    def test_merged_qid_is_followed_and_reported(self):
        result = self.analyze(REDIRECTED_ENTITY, qid="Q141516907", languages=["cs"])
        self.assertEqual(result["topic_proxy"]["qid"], "Q13028547")
        self.assertIn("qid_redirected", [w["code"] for w in result["warnings"]])

    def test_default_output_folder_is_named_after_the_analysis_and_path_safe(self):
        self.assertEqual(wi.default_output_dir("Q1666254", ["pl", "cs", "evil.com/x"], month("2024-09"), month("2026-08")),
                         Path("wiki-interest-output/Q1666254_cs-pl_2024-09_2026-08"))


class ReportTests(CommandTestCase):
    def report(self, entity=CS_ENTITY, **kwargs):
        result = self.analyze(entity, **kwargs)
        return result, (self.out / "report.html").read_text(encoding="utf-8")

    def test_partial_analysis_reports_the_available_language_and_marks_the_missing_one(self):
        result, page = self.report(qid="Q1666254", languages=["pl", "cs"])
        self.assertEqual(result["status"], "partial")
        self.assertIn("Monthly Wikipedia article pageviews", page)  # one usable language: absolute chart
        self.assertIn("No article", page)
        self.assertIn("pl.wikipedia.org", page)
        self.assertIn("−53.6%", page)  # negative growth, typographic minus

    def test_multi_language_report_uses_the_indexed_chart(self):
        result, page = self.report(UK_CS_ENTITY, qid="Q1666254", languages=["cs", "uk"])
        self.assertEqual(result["status"], "ok")
        self.assertIn("Indexed trend: 100 = each language's average monthly article views during the previous "
                      "12 months. Use the metrics table for absolute audience size.", page)

    def test_report_is_self_contained(self):
        _, page = self.report(qid="Q1666254", languages=["cs"])
        self.assertIn("<svg", page)
        for dependency in ("<script", "<link", "src=", "@import", "url("):
            self.assertNotIn(dependency, page)

    def test_user_and_api_text_is_escaped_and_assumptions_and_limitations_appear(self):
        entity = {"entities": {"Q1666254": {**CS_ENTITY["entities"]["Q1666254"], "sitelinks": {
            "cswiki": {"site": "cswiki", "title": "<img src=x onerror=alert(1)>", "badges": []}}}}, "success": 1}
        _, page = self.report(entity, qid="Q1666254", languages=["cs"], topic="<script>alert('topic')</script>",
                              assumptions=["fasting & <b>bold</b> claims"])
        self.assertNotIn("<script>alert", page)
        self.assertNotIn("<img src=x", page)
        self.assertIn("&lt;script&gt;alert", page)
        self.assertIn("fasting &amp; &lt;b&gt;bold&lt;/b&gt; claims", page)
        self.assertIn("a proxy for attention to the topic, not market size, demand, or purchase intent", page)

    def test_flat_trend_renders_as_not_applicable(self):
        article = article_items(2024, 9, [100] * 12 + [102] * 12)
        _, page = self.report(qid="Q1666254", languages=["cs"], aggregate=project_items(2024, 8, [1_000_000] * 25),
                              article=article)
        self.assertIn("not applicable", page)
        self.assertIn("+2.0%", page)

    def test_views_per_million_in_the_report_match_the_json(self):
        article = article_items(2024, 9, [799] * 12 + [133177] * 12)
        result, page = self.report(qid="Q1666254", languages=["cs"], article=article,
                                   aggregate=project_items(2024, 8, [1_000_000_000] * 25))
        r = result["results"][0]
        self.assertEqual((r["previous_topic_views_per_million"], r["latest_topic_views_per_million"]), (0.799, 133.18))
        self.assertIn("0.799 → 133.18", page)

    def test_a_report_failure_does_not_lose_the_analysis(self):
        with mock.patch.object(wi, "render_report", side_effect=RuntimeError("boom")):
            result = self.analyze(CS_ENTITY, qid="Q1666254", languages=["cs"])
        self.assertIsNone(result["artifacts"]["report"])
        self.assertIn("report_failed", [w["code"] for w in result["warnings"]])
        self.assertEqual(json.loads((self.out / "result.json").read_text(encoding="utf-8")), result)
        self.assertFalse((self.out / "report.html").exists())


class ResolveCommandTests(CommandTestCase):
    def resolve(self, **kwargs):
        with self.fake_api(AVAILABILITY_RESPONSE):
            return wi.run_resolve(**kwargs)

    def test_candidates_show_which_requested_languages_have_an_article(self):
        result = self.resolve(query="learning English", languages=["es", "pl", "fr", "nb", "evil.com/x"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual([(c["qid"], c["language"], c["available_languages"], c["missing_languages"])
                          for c in result["candidates"]],
                         [("Q130192", "en", ["es"], ["pl", "fr"]), ("Q2876734", "en", ["es", "fr"], ["pl"])])
        self.assertEqual(result["excluded"], {"disambiguation_pages": 1, "without_qid": 1})
        self.assertEqual([(w["code"], w["languages"]) for w in result["warnings"]], [("invalid_language", ["nb", "evil.com/x"])])
        self.assertEqual(len(self.urls), 2)
        self.assertFalse(any("evil.com" in u for u in self.urls))

    def test_without_languages_resolve_makes_a_single_request(self):
        result = self.resolve(query="learning English")
        self.assertEqual(len(self.urls), 1)
        self.assertNotIn("missing_languages", result["candidates"][0])

    def test_rejects_empty_query_bad_pivot_and_bad_limit(self):
        for kwargs in ({"query": "  "}, {"query": "x", "pivot_language": "en.evil"}, {"query": "x", "limit": 0},
                       {"query": "x", "limit": 11}):
            with self.subTest(**kwargs), self.assertRaises(wi.UsageError):
                wi.run_resolve(**kwargs)


class CliTests(CommandTestCase):
    def main(self, *argv, entity=CS_ENTITY):
        stdout = io.StringIO()
        with self.fake_api(entity, CS_AGGREGATE, CS_ARTICLE), redirect_stdout(stdout):
            code = wi.main(list(argv))
        return code, json.loads(stdout.getvalue())

    def test_successful_analyze_prints_the_result_and_exits_0(self):
        code, result = self.main("analyze", "--qid", "Q1666254", "--languages", "pl,cs", "--output", str(self.out))
        self.assertEqual((code, result["status"], [r["language"] for r in result["results"]]), (0, "partial", ["pl", "cs"]))

    def test_argument_errors_are_json_with_exit_code_2(self):
        for argv in (("analyze", "--qid", "Q1666254"), ("analyze", "--qid", "Q1666254", "--languages", "cs", "--months", "23"),
                     ("analyze", "--qid", "banana", "--languages", "cs"), ("frobnicate",)):
            with self.subTest(argv=argv):
                code, result = self.main(*argv)
                self.assertEqual((code, result["status"], result["error"]["code"]), (2, "error", "invalid_arguments"))
        self.assertEqual(self.urls, [])

    def test_data_errors_are_json_with_exit_code_1(self):
        code, result = self.main("analyze", "--qid", "Q999999999999", "--languages", "cs", entity=MISSING_ENTITY)
        self.assertEqual((code, result["error"]["code"]), (1, "qid_not_found"))

    def test_api_failures_are_json_with_exit_code_1(self):
        stdout = io.StringIO()
        with mock.patch.object(wi, "get_json", side_effect=wi.ApiError("HTTP 503 from www.wikidata.org after 3 attempts")), \
                redirect_stdout(stdout):
            code = wi.main(["resolve", "--query", "astronomy"])
        self.assertEqual((code, json.loads(stdout.getvalue())["error"]["code"]), (1, "api_error"))


if __name__ == "__main__":
    unittest.main()
