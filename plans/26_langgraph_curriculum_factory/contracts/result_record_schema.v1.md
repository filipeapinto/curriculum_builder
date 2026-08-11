# N00 result-record schema (frozen)

Every node result at `plans/26_langgraph_curriculum_factory/results/{node_id}.result.v1.md`
MUST contain these sections, in order, so the scheduler can recompute status
from evidence rather than trust file presence (per `run.prompt.md` TEST #1).
A missing required section makes the record inadmissible; the scheduler
treats the node as not-yet-`PASSED`.

```markdown
# {NODE_ID} result

status: PASSED | NOT_AVAILABLE | BLOCKED
graph_digest: <sha256 of implementation.graph.v2.yaml at execution time>
node_prompt: <path> (<sha256 of prompt file>)
generation: <scheduler generation integer this node executed in>

## Inputs
- predecessor result records consumed, each as `{node_id}: {sha256 of that
  result record file}`
- other frozen inputs read (contracts, spec sections, prior artifacts), each
  with a path and sha256

## Outputs
- every path in this node's `writes` set from implementation.graph.v2.yaml,
  each with a sha256 (or `NOT_CREATED` with justification, only permitted
  where `allowed_results` includes `NOT_AVAILABLE`)

## Commands
- literal command string, exit code, and evidence path to captured
  stdout/stderr, for every command run in service of this node (test runs,
  hash computation, lint, etc.)

## Tests
- every test name/command required by this node's TEST section, PASS/FAIL,
  and the exact assertion or count backing that verdict

## Findings
- open findings this node leaves behind, each with owner (per
  `rework_edges`), evidence key, and fingerprint; empty list if none

## Invalidated descendants
- node IDs invalidated by this execution (rework only); empty list on a
  first-pass PASSED

## Hashes
- consolidated hash table: every hash referenced above, deduplicated, so a
  later node can verify without re-deriving
```

## Status semantics

- `PASSED`: every TEST item verified, every declared `writes` path exists
  with a recorded hash (unless explicitly `NOT_CREATED` under an
  `allowed_results` node), no open blocking finding.
- `NOT_AVAILABLE`: permitted only where the graph's `allowed_results` for
  that node includes it (currently only `N60_LIVE_PRODUCT_PROOF`); requires a
  named missing external prerequisite, not an implementation gap.
- `BLOCKED`: node exhausted its LOOP bound (two repeated same-cause
  failures) or ownership/spec ambiguity stopped it; findings section MUST
  name the exact blocking cause.

## Hash discipline

All hashes use [[digest_algorithm.v1]]. A result record's own file is not
self-hashed inside itself (unresolvable); the scheduler hashes the result
record file externally when a later node cites it as an input.
