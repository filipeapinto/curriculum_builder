import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--domain", required=True, type=Path)
parser.add_argument("--forbidden", required=True, type=Path)
args = parser.parse_args()
body = json.loads(args.domain.read_text(encoding="utf-8"))
if body.get("kind") == "reject":
    print("synthetic-reject: expected fixture")
    raise SystemExit(1)
if body.get("kind") == "accept":
    raise SystemExit(0)
size = args.forbidden.stat().st_size
print(f"observed-size: {size}")
raise SystemExit(size % 2)
