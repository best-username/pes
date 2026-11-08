"""Run: python3 -m unittest discover -s winner-mods/tests"""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import mods  # noqa: E402

WINNER = {"hook": "Three kids. Fifteen socks. Zero pairs.", "first_line": "That's every laundry day.",
          "on_screen": "3 kids | 0 matching pairs", "body": "These socks clip together.", "cta": "Take the quiz."}


def variant(**changes):
    return {**WINNER, "rationale": "lever", **changes}


def issues(*variants, history=(), banned=("guaranteed",)):
    data = {"winner_id": "W011", "winner": WINNER, "variants": list(variants)}
    return [r["issues"] for r in mods.check(data, list(history), list(banned))]


class CheckTest(unittest.TestCase):
    def test_one_changed_element_passes(self):
        self.assertEqual(issues(variant(hook="Where do the socks go?")), [[]])

    def test_two_changed_elements_fail(self):
        [i] = issues(variant(hook="Where do the socks go?", first_line="I counted."))
        self.assertIn("changed 2", i[0])

    def test_unchanged_variant_fails(self):
        self.assertIn("changed 0", issues(variant())[0][0])

    def test_body_may_not_change(self):
        [i] = issues(variant(body="Totally new body."))
        self.assertTrue(any("body and cta stay" in x for x in i))

    def test_whitespace_and_case_are_not_a_change(self):
        self.assertIn("changed 0", issues(variant(hook="  three kids.  fifteen socks. ZERO pairs."))[0][0])

    def test_long_hook_and_on_screen_line(self):
        [h] = issues(variant(hook="one two three four five six seven eight nine ten eleven"))
        [o] = issues(variant(on_screen="short | this line is definitely longer than forty characters"))
        self.assertIn("11 words", h[0])
        self.assertIn("over 40 chars", o[0])

    def test_banned_claim_anywhere_in_script(self):
        [i] = issues(variant(hook="Pairs guaranteed. Every wash."))
        self.assertIn('banned claim: "guaranteed"', i)

    def test_near_duplicate_in_batch_and_in_history(self):
        a, b = issues(variant(hook="Where do the socks go?"), variant(hook="Where do the socks go??"))
        self.assertEqual(a, [])
        self.assertIn("near-duplicate of variant 1", b[0])
        history = [{"mod_id": "W011-M004", "winner_id": "W011", "element": "hook", "text": "Where do socks go?"}]
        self.assertIn("near-duplicate of W011-M004", issues(variant(hook="Where do the socks go?"), history=history)[0][0])

    def test_empty_rationale(self):
        self.assertIn("rationale is empty", issues({**variant(hook="New hook here"), "rationale": " "})[0][0])


class ExportTest(unittest.TestCase):
    def test_numbering_continues_from_history_and_appends(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            history = d / "h.csv"
            history.write_text("mod_id,winner_id,element,text,date\nW011-M007,W011,hook,Old hook,2026-11-01\n")
            src = d / "v.json"
            src.write_text(json.dumps({"winner_id": "W011", "winner": WINNER,
                                       "variants": [variant(hook="Where do the socks go?")]}))
            self.assertEqual(mods.main([str(src), "--history", str(history), "--out-dir", str(d / "b")]), 0)
            rows = list(csv.DictReader(open(d / "b" / "W011-brief.csv")))
            self.assertEqual(rows[0]["mod_id"], "W011-M008")
            self.assertEqual(rows[0]["ad_name"], "SL_US_W011-M008_hook_ai")
            self.assertEqual(len(list(csv.DictReader(open(history)))), 2)

    def test_issues_write_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            src = d / "v.json"
            src.write_text(json.dumps({"winner_id": "W011", "winner": WINNER, "variants": [variant()]}))
            self.assertEqual(mods.main([str(src), "--history", str(d / "h.csv"), "--out-dir", str(d / "b")]), 1)
            self.assertFalse((d / "h.csv").exists())


if __name__ == "__main__":
    unittest.main()
