#!/usr/bin/env python3
"""Append one timestamped action to a scan's action_log.jsonl.

Usage:
    log_action.py <log-path> key=value [key=value ...]

Values that parse as JSON (lists, numbers, objects) are stored as JSON;
everything else is stored as a string. `ts` is added automatically.

    log_action.py docs/research/scan/action_log.jsonl \\
        action=web_fetch_verify url=https://arxiv.org/abs/2406.09205 \\
        claim="ReadCtrl outperforms plain prompting at grade-band control" \\
        result="VERIFIED - abstract retrieved, 52.1 vs 35.7 win rate" \\
        decision="keep, cite in readability thread"
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_value(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2

    log_path = Path(argv[1])
    entry = {"ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

    for pair in argv[2:]:
        if "=" not in pair:
            print(f"error: expected key=value, got {pair!r}", file=sys.stderr)
            return 2
        key, raw = pair.split("=", 1)
        entry[key] = parse_value(raw)

    if "action" not in entry:
        print("error: an 'action' key is required", file=sys.stderr)
        return 2

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as handle:
        handle.write(json.dumps(entry) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
