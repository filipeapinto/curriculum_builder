#!/usr/bin/env bash
# Applies the rebrand mechanically. Requires assets/targets.v1.txt and
# assets/readme_targets.v1.txt to already exist (run
# find_old_name_references.sh first). Idempotent: safe to re-run.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ASSETS="prompts/rebrand_system/assets"
[ -f "$ASSETS/targets.v1.txt" ] || { echo "run find_old_name_references.sh first" >&2; exit 1; }

# 1) Phrase replace in every discovered target file: "curriculum builder"
#    and "curriculum pipeline" -> "Curriculum Factory" (ALL CAPS input stays
#    ALL CAPS, everything else becomes Title case), case-insensitive match.
python3 - "$ASSETS/targets.v1.txt" <<'PY'
import re, sys, pathlib

targets_file = pathlib.Path(sys.argv[1])
pattern = re.compile(r"curriculum\s+(builder|pipeline)", re.IGNORECASE)

def repl(m):
    return "CURRICULUM FACTORY" if m.group(0).isupper() else "Curriculum Factory"

for line in targets_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    p = pathlib.Path(line)
    text = p.read_text()
    new_text = pattern.sub(repl, text)
    if new_text != text:
        p.write_text(new_text)
        print(f"rebranded: {p}")
PY

# 2) readme.md: fix its self-description line and the three broken path
#    references. Exact, known strings only — no invention.
python3 - <<'PY'
import pathlib

p = pathlib.Path("readme.md")
text = p.read_text()

text = text.replace(
    "A contract-first, curriculum-neutral pipeline for producing curriculum units from a",
    "Curriculum Factory: a contract-first, curriculum-neutral engine that produces\ncurriculum units from a",
)

old_block = (
    "See `docs/how_it_works.md` and\n"
    "`docs/png/curriculum_pipeline_infographic.v2.png` for the current architecture. The\n"
    "ImageGen production brief is in\n"
    "`docs/prompts/curriculum_pipeline_infographic.v2.prompt.md`."
)
new_block = (
    "See `docs/images/png/curriculum_pipeline_infographic.v2.png` for the current\n"
    "architecture. The ImageGen production brief is in\n"
    "`docs/images/prompts/curriculum_pipeline_infographic.v2.prompt.md`."
)
if old_block in text:
    text = text.replace(old_block, new_block)
    print("rebranded: readme.md (path repair)")

p.write_text(text)
PY

echo "apply_rebrand.sh done"
