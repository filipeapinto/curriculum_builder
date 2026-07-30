#!/bin/sh
# ./tests/run_gates.sh <phase>
#
# Runs every gate with activation_phase <= <phase> in dependency order, ties
# broken by ID, and records one JSON result under tests/results/. Exits non-zero
# if any gate FAILed or is BLOCKED.
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: ./tests/run_gates.sh <phase>" >&2
    exit 2
fi

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$here/gates/runner.py" "$1"
