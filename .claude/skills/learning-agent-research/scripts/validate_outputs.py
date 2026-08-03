#!/usr/bin/env python3
"""Validate a completed SOTA scan directory.

Usage:
    validate_outputs.py <output-dir>

Checks, in order of how much they matter:

  1. Every URL cited in the recommendation JSON or in a thread file has a
     web_fetch_verify entry in action_log.jsonl whose decision keeps it.
     This is the mechanical enforcement of "fetch before you cite".
  2. The recommendation JSON matches the six-key schema.
  3. Every action log line is valid JSON with ts and action.
  4. Thread files exist and carry the required sections.

Exits non-zero if any check fails. URLs appearing under a "Discarded" heading
in a thread file are expected to be unverified and are skipped.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = {
    "agent",
    "function",
    "what_makes_it_sota",
    "role_in_curriculum_builder",
    "issues_resolved",
    "sources",
}
REQUIRED_SECTIONS = ["why this thread", "findings", "sources", "discarded"]
URL_RE = re.compile(r"https?://[^\s<>\"'\])]+")


def clean(url):
    return url.rstrip(".,;:—-")


def urls_in_markdown(text):
    """URLs from a thread file, skipping any under a Discarded heading."""
    found, in_discarded = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            in_discarded = "discard" in line.lower()
        if not in_discarded:
            found.extend(clean(u) for u in URL_RE.findall(line))
    return found


def load_log(path, errors):
    entries = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{number}: not valid JSON ({exc})")
            continue
        for key in ("ts", "action"):
            if key not in entry:
                errors.append(f"{path.name}:{number}: missing '{key}'")
        entries.append(entry)
    return entries


def kept_urls(entries):
    """URLs the log records a decision to keep."""
    kept = set()
    for entry in entries:
        url = entry.get("url")
        if not url:
            continue
        decision = str(entry.get("decision", "")).lower()
        if decision.startswith("keep") or decision.startswith("pending"):
            kept.add(clean(url))
    return kept


def check_recommendations(path, errors):
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: not valid JSON ({exc})")
        return []
    if not isinstance(data, list) or not data:
        errors.append(f"{path.name}: must be a non-empty JSON array")
        return []

    cited = []
    for index, item in enumerate(data):
        label = f"{path.name}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: not an object")
            continue
        missing = REQUIRED_KEYS - item.keys()
        extra = item.keys() - REQUIRED_KEYS
        if missing:
            errors.append(f"{label}: missing keys {sorted(missing)}")
        if extra:
            errors.append(f"{label}: unexpected keys {sorted(extra)}")
        for key in REQUIRED_KEYS - {"sources"}:
            if not str(item.get(key, "")).strip():
                errors.append(f"{label}: '{key}' is empty")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}: 'sources' must be a non-empty array")
        else:
            cited.extend((label, clean(str(s))) for s in sources)
    return cited


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    root = Path(argv[1])
    errors = []

    if not root.is_dir():
        print(f"FAIL: {root} is not a directory", file=sys.stderr)
        return 1

    log_path = root / "action_log.jsonl"
    if not log_path.is_file():
        errors.append("action_log.jsonl is missing")
        entries = []
    else:
        entries = load_log(log_path, errors)
        if not entries:
            errors.append("action_log.jsonl is empty")

    json_paths = sorted(root.glob("sota_agents.v*.json"))
    if not json_paths:
        errors.append("no sota_agents.v<N>.json found")
    cited = []
    for json_path in json_paths:
        cited.extend(check_recommendations(json_path, errors))

    thread_paths = sorted(root.glob("*.md"))
    if not thread_paths:
        errors.append("no thread .md files found")
    for thread_path in thread_paths:
        text = thread_path.read_text()
        lowered = text.lower()
        for section in REQUIRED_SECTIONS:
            if section not in lowered:
                errors.append(f"{thread_path.name}: no '{section}' section")
        cited.extend((thread_path.name, u) for u in urls_in_markdown(text))

    kept = kept_urls(entries)
    unverified = sorted({(where, url) for where, url in cited if url not in kept})
    for where, url in unverified:
        errors.append(f"{where}: cites {url} with no kept verification in the action log")

    print(f"threads: {len(thread_paths)}  log entries: {len(entries)}  "
          f"citations checked: {len(cited)}  verified URLs in log: {len(kept)}")

    if errors:
        print(f"\nFAIL ({len(errors)} problem(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: every citation traces to a kept verification; schema and log are well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
