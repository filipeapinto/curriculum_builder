#!/usr/bin/env python3
"""Initialize a plan-create workspace under plans/<slug>/.

Creates plans/<slug>/qa/ and plans/<slug>/prompts/, and writes
plans/<slug>/plans.log.md with the fixed header, objective, and entry
template -- but only if plans.log.md doesn't already exist. Never overwrites
an existing log; re-running this on an existing package is a no-op for the
log (directories are created idempotently via mkdir -p semantics).

Usage:
    init_plan_workspace.py plans/<slug> --title "<TITLE>" --objective "<...>"
"""

import argparse
import sys
from pathlib import Path

LOG_TEMPLATE = """# {title} Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

{objective}

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries
"""


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="plans/<slug> directory to initialize")
    parser.add_argument("--title", required=True, help="human-readable title")
    parser.add_argument("--objective", required=True, help="one-paragraph objective")
    args = parser.parse_args(argv[1:])

    root = Path(args.root)
    (root / "qa").mkdir(parents=True, exist_ok=True)
    (root / "prompts").mkdir(parents=True, exist_ok=True)

    log_path = root / "plans.log.md"
    if log_path.exists():
        print(f"exists, left untouched: {log_path}")
        return 0

    log_path.write_text(LOG_TEMPLATE.format(title=args.title, objective=args.objective))
    print(f"created: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
