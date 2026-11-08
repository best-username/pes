#!/usr/bin/env python3
"""Check modifications of a winning ad script and export a designer brief.

Usage: python3 mods.py <variants.json> [--history mods-history.csv] [--out-dir DIR] [--check-only]

Input (written by the model, see SKILL.md):
{
  "winner_id": "W012", "market": "US",
  "winner": {"hook": "...", "first_line": "...", "on_screen": "...", "body": "...", "cta": "..."},
  "variants": [{"hook": "...", "first_line": "...", "on_screen": "...", "body": "...", "cta": "...",
                "rationale": "..."}]
}
Each variant is a full script; it must differ from the winner in exactly one of the elements
in VARIABLE. The script prints one JSON document; exit code 1 when any variant has an error.
"""
import argparse
import csv
import datetime
import difflib
import json
import re
import sys
from pathlib import Path

ELEMENTS = ("hook", "first_line", "on_screen", "body", "cta")
VARIABLE = ("hook", "first_line", "on_screen")  # what a modification may change
HOOK_MAX_WORDS = 10        # ~3 seconds of voiceover at 2.5-3 words per second
ON_SCREEN_MAX_CHARS = 40   # per line ("|" separates lines); readable on a phone in ~2 seconds
NEAR_DUPLICATE = 0.85      # difflib ratio; ponytail: character similarity, swap for embeddings if paraphrases slip through
BANNED_FILE = Path(__file__).resolve().parent.parent / "references" / "banned-claims.txt"
HISTORY_FIELDS = ("mod_id", "winner_id", "element", "text", "date")


def norm(text):
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def load_banned(path=BANNED_FILE):
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    return [l.strip().lower() for l in lines if l.strip() and not l.startswith("#")]


def load_history(path):
    if not path or not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def similar(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def check(data, history, banned):
    """Return one result per variant: changed element and a list of issues."""
    winner = data["winner"]
    missing = [e for e in ELEMENTS if e not in winner]
    if missing:
        raise ValueError(f"winner is missing elements: {', '.join(missing)}")
    seen = {e: [(h["mod_id"], h["text"]) for h in history
                if h["winner_id"] == data["winner_id"] and h["element"] == e] for e in VARIABLE}
    results = []
    for i, v in enumerate(data["variants"], 1):
        issues = []
        changed = [e for e in ELEMENTS if norm(v.get(e, winner[e])) != norm(winner[e])]
        if len(changed) != 1:
            issues.append(f"must change exactly one element, changed {len(changed)}: {', '.join(changed) or 'none'}")
        if any(e not in VARIABLE for e in changed):
            issues.append(f"only {', '.join(VARIABLE)} may change; body and cta stay as in the winner")
        element = changed[0] if len(changed) == 1 else None
        text = v.get(element, "") if element else ""
        if element == "hook" and len(text.split()) > HOOK_MAX_WORDS:
            issues.append(f"hook has {len(text.split())} words, max {HOOK_MAX_WORDS} (~3 s)")
        if element == "on_screen":
            for line in text.split("|"):
                if len(line.strip()) > ON_SCREEN_MAX_CHARS:
                    issues.append(f"on-screen line over {ON_SCREEN_MAX_CHARS} chars: \"{line.strip()}\"")
        full = " ".join(norm(v.get(e, winner[e])) for e in ELEMENTS)
        issues += [f"banned claim: \"{b}\"" for b in banned if b in full]
        if element in VARIABLE:
            for ref, prev in seen[element]:
                if similar(text, prev) >= NEAR_DUPLICATE:
                    issues.append(f"near-duplicate of {ref}: \"{prev}\"")
                    break
            seen[element].append((f"variant {i}", text))
        if not str(v.get("rationale", "")).strip():
            issues.append("rationale is empty: say what changed and why it may win")
        results.append({"variant": i, "element": element, "text": text, "issues": issues})
    return results


def next_number(history, winner_id):
    nums = [int(m.group(1)) for h in history if h["winner_id"] == winner_id
            for m in [re.search(r"-M(\d+)", h["mod_id"])] if m]
    return max(nums, default=0) + 1


def export(data, results, history, history_path, out_dir):
    winner, wid, market = data["winner"], data["winner_id"], data.get("market", "US")
    today = datetime.date.today().isoformat()
    n = next_number(history, wid)
    rows = []
    for r, v in zip(results, data["variants"]):
        mod_id = f"{wid}-M{n:03d}"
        n += 1
        rows.append({
            "mod_id": mod_id,
            "ad_name": f"SL_{market}_{mod_id}_{r['element']}_ai",  # UA keeps this in Meta: results trace back to the winner, _ai marks skill-made mods
            "element": r["element"],
            "before": winner[r["element"]],
            "after": r["text"],
            "rationale": v["rationale"].strip(),
        })
    out_dir.mkdir(parents=True, exist_ok=True)
    brief_csv = out_dir / f"{wid}-brief.csv"
    with open(brief_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    brief_md = out_dir / f"{wid}-brief.md"
    lines = [f"# Modifications of {wid} ({market}), {today}", "",
             "Everything not listed stays exactly as in the winner.", ""]
    for r in rows:
        lines += [f"## {r['ad_name']}", f"- **Change:** {r['element']}", f"- **Was:** {r['before']}",
                  f"- **New text:** {r['after']}", f"- **Why:** {r['rationale']}", ""]
    brief_md.write_text("\n".join(lines), encoding="utf-8")
    new_file = not Path(history_path).exists()
    with open(history_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        if new_file:
            w.writeheader()
        w.writerows({"mod_id": r["mod_id"], "winner_id": wid, "element": r["element"],
                     "text": r["after"], "date": today} for r in rows)
    return {"brief_csv": str(brief_csv), "brief_md": str(brief_md), "history": str(history_path),
            "mod_ids": [r["mod_id"] for r in rows]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("variants", type=Path)
    p.add_argument("--history", type=Path, default=Path("mods-history.csv"))
    p.add_argument("--out-dir", type=Path, default=Path("briefs"))
    p.add_argument("--check-only", action="store_true", help="validate, write nothing")
    a = p.parse_args(argv)
    try:
        data = json.loads(a.variants.read_text(encoding="utf-8"))
        history = load_history(a.history)
        results = check(data, history, load_banned())
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({"status": "error", "message": f"{type(e).__name__}: {e}"}))
        return 2
    failed = [r for r in results if r["issues"]]
    out = {"status": "issues" if failed else "ok", "variants": len(results), "with_issues": len(failed),
           "results": results}
    if not failed and not a.check_only and results:
        out["artifacts"] = export(data, results, history, a.history, a.out_dir)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
