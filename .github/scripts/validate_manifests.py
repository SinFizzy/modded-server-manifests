"""Checks every servers/<id>/manifest.json before it can reach players.

Run locally:  pip install jsonschema && python .github/scripts/validate_manifests.py
Exits with code 1 if any manifest has a problem.
"""

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schema" / "manifest.v1.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

# Things that must never appear in this public repo.
SECRET_PATTERNS = [
    (re.compile(r"discord(?:app)?\.com/api/webhooks/", re.I), "a Discord webhook URL"),
    (re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}"), "a GitHub token"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b"), "an IP address with a port (server addresses belong in invite links)"),
    (re.compile(r"\"(?:password|token|apiKey|api_key|secret)\"\s*:", re.I), "a password/token field"),
]


def check(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")

    for pattern, what in SECRET_PATTERNS:
        if pattern.search(text):
            problems.append(f"contains {what}. Remove it: this repo is public.")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return problems + [f"isn't valid JSON (line {e.lineno}): {e.msg}"]

    for error in sorted(VALIDATOR.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(p) for p in error.absolute_path) or "(top level)"
        problems.append(f"{where}: {error.message}")

    if isinstance(data, dict):
        server_id = (data.get("server") or {}).get("id")
        if server_id and server_id != path.parent.name:
            problems.append(f"server.id is \"{server_id}\" but the folder is \"{path.parent.name}\". They must match.")

        seen: dict[tuple[str, str], int] = {}
        for i, mod in enumerate(data.get("mods") or []):
            if not isinstance(mod, dict):
                continue
            key = (str(mod.get("source", "")), str(mod.get("id", "")).lower())
            if key in seen:
                problems.append(f"mods.{i}: \"{mod.get('id')}\" is listed twice (also mods.{seen[key]}).")
            else:
                seen[key] = i

    return problems


def main() -> int:
    manifests = sorted((ROOT / "servers").glob("*/manifest.json"))
    failed = 0
    for path in manifests:
        rel = path.relative_to(ROOT)
        problems = check(path)
        if problems:
            failed += 1
            print(f"FAIL  {rel}")
            for p in problems:
                print(f"      {p}")
        else:
            print(f"ok    {rel}")

    stray = [p for p in (ROOT / "servers").rglob("*.json") if p.name != "manifest.json"]
    for p in stray:
        print(f"note  {p.relative_to(ROOT)} isn't named manifest.json, so launchers won't read it.")

    print(f"\n{len(manifests) - failed} ok, {failed} with problems, {len(manifests)} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
