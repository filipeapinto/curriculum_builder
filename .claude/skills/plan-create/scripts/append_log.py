#!/usr/bin/env python3
"""Append one entry to a plan-create plans.log.md, in the fixed format.

The log is append-only: this script only ever opens the file in append mode,
so it cannot rewrite a prior entry. It refuses to run if the log doesn't
exist yet -- run init_plan_workspace.py first so every package shares the
same header.

Usage:
    append_log.py <log-path> agent=<agent/task> action="..." \\
        paths="..." evidence="..." issues="..."

All four of agent/action/paths/evidence/issues are required, matching the
fixed entry template exactly. Use paths="none" or issues="None." when there
is nothing to report -- don't omit the key.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = ("agent", "action", "paths", "evidence", "issues")


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    log_path = Path(argv[1])
    if not log_path.exists():
        print(
            f"error: {log_path} does not exist -- run init_plan_workspace.py first",
            file=sys.stderr,
        )
        return 2

    fields = {}
    for pair in argv[2:]:
        if "=" not in pair:
            print(f"error: expected key=value, got {pair!r}", file=sys.stderr)
            return 2
        key, value = pair.split("=", 1)
        fields[key] = value

    missing = [k for k in REQUIRED_KEYS if k not in fields]
    if missing:
        print(f"error: missing required key(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = (
        f"\n### {timestamp} — {fields['agent']}\n"
        f"- Action: {fields['action']}\n"
        f"- Paths touched: {fields['paths']}\n"
        f"- Evidence/decision: {fields['evidence']}\n"
        f"- Issues: {fields['issues']}\n"
    )

    with log_path.open("a") as handle:
        handle.write(entry)

    print(f"appended entry to {log_path} at {timestamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
