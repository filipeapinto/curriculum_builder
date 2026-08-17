#!/usr/bin/env bash
# Mechanical acceptance run for graph-doc-graph-visualize.
#
#   bash evals/run_checks.sh [python-executable]
#
# Proves the machine contract (A1-A5) end to end and re-renders both fixtures
# through every available backend. Everything it writes goes under
# evals/fixtures/*/out/ and evals/negative/out/. Exit 0 = all checks passed.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="$(dirname "$HERE")"
PY="${1:-python3}"
R="$SKILL/scripts/render_manifest.py"
I="$SKILL/scripts/inspect_layout.py"

REAL="${MANIFEST_UNDER_TEST:-$SKILL/../../../specs/graph_doc_createtion_compile_skill/prompts/10_output/run/manifest.v1.json}"
MIN="$HERE/fixtures/minimal/manifest.json"

pass=0; fail=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
check(){ if [ "$1" = "0" ]; then ok "$2"; else bad "$2"; fi; }

echo "== A1/A2/A3: named input, named output, checkable artifact =="
for fx in "uspto-whitepaper:$REAL" "minimal:$MIN"; do
  name="${fx%%:*}"; man="${fx#*:}"
  out="$HERE/fixtures/$name/out"; mkdir -p "$out"
  if [ ! -f "$man" ]; then bad "$name: manifest missing ($man)"; continue; fi

  "$PY" "$R" --manifest "$man" --out "$out/graph.svg" >/dev/null
  rc=$?
  check $rc "$name: studio -> svg exits 0"
  if [ -s "$out/graph.svg" ] && head -c 4096 "$out/graph.svg" | grep -q "<svg" \
     && tail -c 2048 "$out/graph.svg" | grep -q "</svg>"; then
    ok "$name: svg is non-empty and well-formed at the exact --out path"
  else
    bad "$name: svg A3 check"
  fi

  "$PY" "$R" --manifest "$man" --out "$out/graph.png" --scale 1.5 >/dev/null
  check $? "$name: studio -> png exits 0"
  if [ -s "$out/graph.png" ] && file "$out/graph.png" | grep -q "PNG image data"; then
    ok "$name: png carries a valid PNG signature"
  else
    bad "$name: png A3 check"
  fi

  "$PY" "$I" --svg "$out/graph.svg" --report "$out/graph.inspect.json" >/dev/null
  check $? "$name: inspect_layout reports no blocker"
  st=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['status'])" "$out/graph.inspect.json" 2>/dev/null)
  if [ "$st" = "clean" ]; then ok "$name: inspection status is clean"
  else bad "$name: inspection status is '$st' (expected clean)"; fi
done

echo "== alternate backends =="
out="$HERE/fixtures/uspto-whitepaper/out"
if command -v dot >/dev/null 2>&1; then
  "$PY" "$R" --manifest "$REAL" --out "$out/graph.graphviz.svg" --backend graphviz >/dev/null
  check $? "graphviz backend exits 0"
else
  echo "  SKIP graphviz (dot not on PATH)"
fi
if command -v d2 >/dev/null 2>&1; then
  "$PY" "$R" --manifest "$REAL" --out "$out/graph.d2.svg" --backend d2 --detail compact --d2-engine dagre >/dev/null
  check $? "d2 backend exits 0"
else
  echo "  SKIP d2 (d2 not on PATH)"
fi
for d in compact standard full; do
  "$PY" "$R" --manifest "$REAL" --out "$out/graph.$d.svg" --detail "$d" >/dev/null 2>&1
  check $? "--detail $d renders"
  "$PY" "$I" --svg "$out/graph.$d.svg" >/dev/null 2>&1
  check $? "--detail $d passes inspection"
done

echo "== A4: failure signal =="
nout="$HERE/negative/out"; mkdir -p "$nout"
neg() { # file, label
  rm -f "$nout/$2.svg" "$nout/$2.svg.failure.json"
  "$PY" "$R" --manifest "$1" --out "$nout/$2.svg" >/dev/null 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then bad "$2: expected non-zero exit, got 0"; return; fi
  if [ -e "$nout/$2.svg" ]; then bad "$2: wrote an artifact despite failing"; return; fi
  if [ ! -s "$nout/$2.svg.failure.json" ]; then bad "$2: no failure record"; return; fi
  "$PY" -c "
import json,sys
r=json.load(open(sys.argv[1]))
assert r['status']=='failed', r
assert r['reason'].strip(), r
assert r['stage'] in ('input','layout','raster','verify','internal'), r
" "$nout/$2.svg.failure.json" || { bad "$2: failure record malformed"; return; }
  ok "$2: exits non-zero, writes no artifact, records status=failed with a reason"
}
neg "$HERE/negative/not-json.json"      "not-json"
neg "$HERE/negative/no-nodes.json"      "no-nodes"
neg "$HERE/negative/no-node-array.json" "no-node-array"
neg "$HERE/negative/forward-cycle.json" "forward-cycle"
neg "$HERE/negative/does-not-exist.json" "missing-input"

rm -f "$nout/bad-ext.txt" "$nout/bad-ext.txt.failure.json"
"$PY" "$R" --manifest "$MIN" --out "$nout/bad-ext.txt" >/dev/null 2>&1
if [ $? -ne 0 ] && [ -s "$nout/bad-ext.txt.failure.json" ]; then
  ok "unsupported --out extension fails with a status record"
else
  bad "unsupported --out extension"
fi

echo "== A2: --status-path is honoured =="
rm -f "$nout/custom-status.json"
"$PY" "$R" --manifest "$HERE/negative/no-nodes.json" --out "$nout/x.svg" \
  --status-path "$nout/custom-status.json" >/dev/null 2>&1
if [ -s "$nout/custom-status.json" ]; then ok "--status-path honoured"; else bad "--status-path ignored"; fi

echo
echo "passed=$pass failed=$fail"
[ "$fail" -eq 0 ]
