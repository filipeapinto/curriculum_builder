A QA gate has just failed and you are the analyst. You were not part of it — that is
the point of asking you.

Below is the complete exchange: the criteria the artifact was held to, and every round
of review with its findings, rebuttals and verdicts. Read it as an investigator, not as
a participant, and answer one question: why did this not converge?

Four honest possibilities, and you should be genuinely willing to reach any of them:

The artifact really is deficient. The findings were sound, they were never fixed, and
the right response is more work on the artifact.

The specification was deficient. The pass criteria were vague, self-contradictory, or
demanded something unreachable. No artifact could have passed, and the reviewer was
left substituting its own standard because it had nothing firmer to hold. This is
easy to miss because the transcript reads like a normal disagreement.

The process failed. Both parties were capable of resolving this and did not — talking
past each other, reopening settled ground, scope drifting between rounds, or the
reviewer escalating preferences past the stated severity threshold and calling them
blockers.

The record was breached. What the reviewer remembers and what was written down do not
agree.

Tie every claim to a specific round and quote the text you are relying on. A
conclusion that cannot be traced back to the transcript is not usable — the people
reading this will act on it.


## Outcome
QA_PASSED — CONVERGED: Codex passed the artifact at round 4
Rounds used: 4 of 5
Severity threshold in force: major

## Focus given to the reviewer
Verify PKGV2-T01 through PKGV2-T05 especially: read scan_node.py's DEFAULT_GRAPH_PATH and run_node/restrict_to_write_set logic directly, confirm every N20-N50 verification command carries an explicit --graph binding to this package's own graph, confirm validate_plan_v2.py actually rejects an omitted binding (not just documents it), and confirm N60 alone uses complete-tree mode.

## Pass criteria the artifact was held to
# QA criteria — Run 27 execution package v2 (n20_recovery.plan.v2.md, Phase E)

The primary artifact under review is
`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml`
(graph semantic `version: 2`), together with its three fresh node prompts
(`execution_package_v2/prompts/N00_spec_approval_gate.prompt.v3.md`,
`execution_package_v2/prompts/N20_provider_transport.prompt.v3.md`,
`execution_package_v2/prompts/N30_preflight_egress.prompt.v3.md`), its
node-scoped scanner entry point
(`execution_package_v2/controller/scan_node.py`), its two validator entry
points (`execution_package_v2/tools/validate_plan_v2.py`,
`execution_package_v2/tools/validate_result_v2.py`), and its automated test
suite (`execution_package_v2/tests/test_execution_package_v2.py`). Together
these are "execution package v2" that
`plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v2.md`'s
Phase D requires.

This package is a from-scratch, isolated rebuild, not an edit, of the first
execution-package correction
(`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml`,
unchanged and immutable). That first correction's own independent QA round 1
found `PKG-QA-001`: its node-scoped verification command never passed
`--graph`, so its extended scanner silently defaulted to loading the
*parent* v1 graph
(`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`)
instead of the corrected v2 write sets. That failed attempt, its QA session
(`019ffbfc-edce-7750-a58a-a008cefbd95e`), and the `PKG-QA-001` finding are
provided as grounding and must be treated as immutable historical record,
not as a target for further QA action. This package's job is to prove the
same class of defect is now structurally impossible, not merely absent by
convention.

A correct package v2 satisfies every criterion below. Attempt to falsify
each one against the actual text and behavior of the artifacts — do not
accept a claim the artifact makes about itself without checking it.

## Criteria (PKGV2-T00–PKGV2-T10)

1. **PKGV2-T00 — Historical immutability.** `implementation.graph.v1.yaml`
   (the parent v1 package's graph) and `implementation.graph.v2.yaml` (the
   failed correction) are byte-unchanged from the live repository state, as
   are every `results/N00_SPEC_APPROVAL_GATE.result.v1.json`,
   `results/N10_HARNESS_PROTOCOL.result.v1.json`,
   `results/N20_PROVIDER_TRANSPORT.result.v1.json`, their
   `results/evidence/` directories, and the root `QA/` session directory
   with its `PKG-QA-001` finding. The three Phase-A-restored files
   (`controller/check_forbidden_production_refs.py`,
   `tools/validate_plan.py`, `tools/validate_result.py` in the parent
   package, not this one) retain their required admitted hashes
   (`cb530b32...`, `9f534ba3...`, `0beef6ed...`) — verify directly against
   the live repository.
2. **PKGV2-T01 — No silent v1 graph fallback (the direct PKG-QA-001 fix).**
   Read `execution_package_v2/controller/scan_node.py`'s `DEFAULT_GRAPH_PATH`
   and its argument parser. Confirm the default, and every fallback path, is
   this package's own graph file, never
   `plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`.
   Separately, read every `N20_PROVIDER_TRANSPORT` through
   `N50_EVIDENCE_AUDIT_CONTROLS` verification command in this package's
   graph and confirm each node-scoped `scan_node.py --node <ID>` invocation
   also carries an explicit `--graph <this package's graph path>` — the
   binding must be visible in the graph itself, not merely correct by the
   scanner's internal default. Confirm
   `execution_package_v2/tools/validate_plan_v2.py` actively rejects a
   node-scoped scan command that omits this explicit binding (not merely
   documents that it should be present).
3. **PKGV2-T02 — Node mode is a genuine narrowing.** Read
   `scan_node.py`'s `run_node`/`restrict_to_write_set` functions. Confirm
   node mode is computed by calling the parent module's unmodified
   whole-tree `scan_production`/`scan_tests` and then filtering the
   resulting scanned-file and violation lists to the node's own write-set
   intersection — not a reimplementation of the term/credential/guard-
   region/occurrence rules. Confirm it cannot scan more broadly than the
   whole-tree scopes would, and cannot skip a file within the node's write
   set that either whole-tree scope would have scanned.
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.**
   `runtime/langgraph_factory/egress.py` and
   `tests/runtime/test_plan26_egress.py` are in
   `N20_PROVIDER_TRANSPORT`'s `writes` list and absent from
   `N30_PREFLIGHT_EGRESS`'s. `N30_PREFLIGHT_EGRESS` declares
   `runtime/langgraph_factory/egress.py` under `read_only_inputs`. The N30
   prompt (`prompts/N30_preflight_egress.prompt.v3.md`) explicitly states
   N30 consumes this boundary read-only and does not claim ownership.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.**
   For every scanning node, the files the node-scoped scan actually covers
   (verify by reading `scan_node.py`'s logic and, if useful, by running it)
   are exactly the intersection of that node's `writes` list with the two
   whole-tree scan scopes' roots — not a hardcoded or hand-maintained file
   list that could drift from the graph.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** Read every node's
   verification list. Confirm `scan_node.py` is invoked without `--node`
   only for `N60_ADVERSARIAL_REGRESSION`, and with `--node <exact node ID>`
   for every other scanning node (`N20`–`N50`).
7. **PKGV2-T06 — result/evidence versioning never reuses v1 paths.** Every
   node's own result/evidence write path in this package's graph lives
   under `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/`,
   never the parent v1 package's `results/` root nor the failed
   correction's `results/v2/` root. `result_pattern` in the graph header
   reflects this.
8. **PKGV2-T07 — source_spec binding.** The graph's `source_spec` field
   points at the QA-passed specification artifact
   (`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
   sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`),
   not v1, v2, or v3-by-filename. `validate_plan_v2.py` enforces both the
   path and the digest, not merely the path.
9. **PKGV2-T08 — no write-set overlap.** Every write path in this package's
   graph belongs to exactly one node; no two nodes claim overlapping paths.
   You may verify this by reading every node's `writes` list directly, or
   by noting that
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   reports `valid: true`, which includes this exact check (cited as a fact
   to confirm, not evidence to accept unchecked).
10. **PKGV2-T09 — no implementation performed; no production edit.** No file
    under `runtime/`, `policy/`, `schemas/routes.schema.v1.json`, or
    `schemas/model_registry.schema.v1.json` was created or changed while
    authoring this package. `git status` (available to you read-only) shows
    changes confined to `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/`
    and the three Phase-A restorations only.
11. **PKGV2-T10 — automated proof, not narrative.**
    `execution_package_v2/tests/test_execution_package_v2.py` is a real,
    passing, automated suite (not a documentation file) that positively
    proves PKGV2-T01 through PKGV2-T09 above, including at least one seeded
    violation in a synthetic tree proving node-scope narrowing actually
    rejects a defect, one proving the same defect surfaces in complete-tree
    mode, and one proving `git status` shows no production/policy/schema/
    active-test change from authoring this package. Run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    yourself if useful and confirm it passes.

## Falsification targets

- `scan_node.py`'s default graph path is computed once at import time from
  `Path(__file__).resolve()`; confirm this genuinely resolves to
  `execution_package_v2/implementation.graph.v1.yaml` and not, by an
  off-by-one `.parent` chain, to the parent v1 package's directory.
- The three fresh prompts' claimed write-set/ownership language matches the
  graph's actual `writes`/`read_only_inputs` for that node exactly (no
  prompt claiming an ownership the graph does not grant, or vice versa).
- `validate_plan_v2.py`'s node-scoped-graph-binding check
  (`node_scoped_scan_commands`/the loop that requires `--graph`) is not
  itself silently vacuous — for example by matching on a substring that
  would also match an unrelated command, or by only checking nodes that
  happen to already be correct.
- The package's `rules:` block (scan-scope declarations, `frozen_before_entry`,
  etc.) is unchanged in substance from the parent v1 package except where
  this criteria file says it should differ.
- N40, N50, N60, N70, N80, N90's prompts are reused unmodified from the
  parent v1 package's `prompts/` directory because this correction does not
  change their scope — confirm the graph actually points at those unmodified
  files rather than silently forking them.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
eleven numbered criteria above (a stated criterion fails on a realistic
reading of the artifacts, not merely a stylistic quibble). Anything you
notice that does not defeat a numbered criterion belongs in observations,
not findings.


## The exchange

### Round 1 — reviewer returned FAIL
Reviewer response:
```json
{"verdict":"FAIL","honesty_audit":{"prior_rounds_consistent":true,"rounds_you_recall":0,"discrepancies":[]},"rebuttal_response":"","findings":[{"id":"PKGV2-QA-001","title":"Automated suite can pass while node mode and result versioning are broken","severity":"major","criterion_ref":"PKGV2-T10 — the suite must “positively prove PKGV2-T01 through PKGV2-T09,” including PKGV2-T05’s exact node IDs and PKGV2-T06’s per-node result/evidence roots.","trigger":"A scanning command’s `--node` value is changed to another node ID, or a node’s result write is moved back to the parent `results/` root.","consequence":"The advertised regression suite remains green even though the graph would scan the wrong ownership slice or reuse a forbidden historical result path. It therefore does not provide the required automated proof of T05 and T06.","evidence":"`tests/test_execution_package_v2.py` lines 257–266 only identify commands lacking `--node`; they never assert each N20–N50 command’s argument equals its owning node. Lines 269–272 delegate graph checks to `validate_plan_v2.py`. That validator’s lines 173–220 require only the presence of `--node`, `--graph`, and the package graph string, without checking the `--node` argument. Its lines 201–205 validate only the header `result_pattern`, not every node’s result/evidence writes. Direct in-memory mutations confirmed both gaps: changing N20’s scan argument to `N30_PREFLIGHT_EGRESS` produced `wrong_node_accepted True`, and changing N40’s result write to the parent `results/` root produced `parent_result_path_accepted True`."}],"observations":["The package graph itself currently has the correct exact N20–N50 node arguments, package-v2 result/evidence paths, N20 egress ownership, N60-only complete-tree invocation, source-spec digest, and non-overlapping write sets.","`scan_node.py` resolves its default graph to the package-local graph and narrows the unmodified parent whole-tree reports by the graph-derived write set.","The requested pytest invocation could not start in this read-only QA environment because Python had no writable temporary directory; the plan validator and all three historical parent result validations did execute successfully.","The N00 prompt describes the approval schema as frozen by `rules.frozen_before_entry`, while that rule lists only the node-result schema. This does not alter N00’s actual write ownership and does not independently defeat a numbered criterion."] ,"reasoning":"Direct inspection and targeted execution confirmed T00–T09 in the current artifact. I declined to treat the read-only pytest environment failure or the N00 wording mismatch as findings. The surviving major defect is specifically T10: realistic graph regressions violating T05 or T06 are accepted by the validator and unobserved by the suite, so the required automated proof is incomplete."}
```

### Round 2 — reviewer returned FAIL
Reviewer response:
```json
{"verdict":"FAIL","honesty_audit":{"prior_rounds_consistent":true,"rounds_you_recall":1,"discrepancies":[]},"rebuttal_response":"","findings":[{"id":"PKGV2-QA-002","title":"Duplicate arguments bypass the graph and node binding proof","severity":"major","criterion_ref":"PKGV2-T10 — the suite must positively prove PKGV2-T01 through PKGV2-T09; PKGV2-T01 requires the package graph binding to be structurally enforced, and PKGV2-T05 requires each scan to use its exact node ID.","trigger":"A scan command retains the expected `--graph` or `--node` pair but appends a second pair with the parent graph or another node ID.","consequence":"Python argparse uses the last occurrence, so execution scans the wrong graph or node. The validator and automated suite inspect only the first occurrence and still pass, allowing the same stale-write-set false assurance the package is intended to make structurally impossible.","evidence":"`validate_plan_v2.py` lines 241–259 checks membership and obtains values with `command.index(...)`, but never requires either flag to occur exactly once. Tests at lines 288–310 use the same first-occurrence logic. Direct mutations showed `duplicate_node_accepted True` and `duplicate_graph_accepted True`; argparse resolved `--node N20 ... --node N30` and `--graph package ... --graph parent` to N30 and the parent graph."}],"observations":["Round 1’s exact defects are repaired: simple wrong-node and wrong-graph substitutions and parent-root result/evidence writes are now rejected, with corresponding mutation tests.","The current graph contains no duplicate flags; N20–N50 use their exact IDs and the package-v2 graph, while N60 alone uses complete-tree mode.","The three prompts still name the deprecated package-local `implementation.graph.v1.yaml`; N00 requires it to exist, and N20/N30 show commands using it, although the active artifact is `implementation.graph.v2.yaml`. The numbered criteria constrain the graph commands and prompt ownership language rather than these prompt command examples, so this is recorded as a non-blocking observation.","In the read-only environment, 34 tests not requiring temporary-file creation passed and all 36 tests collected. The two synthetic-tree tests could not be executed here because pytest's `tmp_path` requires writable storage; their unchanged logic was inspected directly."],"reasoning":"Historical hashes, source-spec binding, ownership, write-set uniqueness, scan narrowing, result roots, and production-path git status were checked and remain correct. The prior finding’s stated mutations are now covered. A separate major T10 proof gap survives because duplicate argparse options let a wrong runtime binding pass both newly added enforcement layers."}
```

### Round 3 — reviewer returned FAIL
Reviewer response:
```json
{"verdict":"FAIL","honesty_audit":{"prior_rounds_consistent":true,"rounds_you_recall":2,"discrepancies":[]},"rebuttal_response":"","findings":[{"id":"PKGV2-QA-002","title":"Equals-form duplicate arguments still bypass binding enforcement","severity":"major","criterion_ref":"PKGV2-T10 — automated proof of PKGV2-T01 and PKGV2-T05; the package must make wrong graph/node binding structurally impossible.","trigger":"A correct command appends an argparse-supported equals-form override such as `--graph=plans/.../implementation.graph.v1.yaml` or `--node=N30_PREFLIGHT_EGRESS`.","consequence":"Argparse applies the final override, so N20 can scan the parent graph or N30’s write set. The validator and suite still pass because they count only tokens exactly equal to `--graph` or `--node`.","evidence":"`validate_plan_v2.py` lines 263 and 269 use `command.count(\"--node\")` and `command.count(\"--graph\")`; lines 278 and 284 then inspect the first separated-form occurrence. Tests lines 529–698 seed only separated-token duplicates. Direct mutations produced `equals_duplicate_node_accepted True` and `equals_duplicate_graph_accepted True`, while argparse resolved the same argv to node N30 and the parent graph."}],"observations":["The round-2 fix correctly rejects omitted flags, simple value substitutions, and separated-token duplicate flags for N20–N60.","The active graph itself has one correct separated `--node` and `--graph` pair per N20–N50 command, and N60 remains the sole complete-tree invocation.","The plan validator passes; historical and Phase-A hashes remain unchanged; git status reports no runtime, policy, active-schema, or active-test changes.","Sixty-seven non-temporary-file tests passed and all 69 tests collected. The two synthetic-tree tests could not run in this read-only environment because they require pytest’s writable `tmp_path`.","The fresh prompts still cite the deprecated package-local `implementation.graph.v1.yaml`. This remains outside the numbered prompt requirements, which constrain ownership language, so it is non-blocking here."],"reasoning":"Round history matches both verdicts I issued. The prior simple-swap and result-root proof gaps remain repaired. However, PKGV2-QA-002 is only partially resolved: the validator’s token counting does not match its argparse execution semantics, leaving a normal CLI spelling that reproduces the wrong-binding condition while the automated suite stays green."}
```

### Round 4 — reviewer returned PASS
Reviewer response:
```json
{"verdict":"PASS","honesty_audit":{"prior_rounds_consistent":true,"rounds_you_recall":3,"discrepancies":[]},"rebuttal_response":"","findings":[],"observations":["The three fresh prompts still cite the deprecated package-local `implementation.graph.v1.yaml` in command examples. Their ownership and read-only claims match the active graph, so this does not defeat a numbered criterion.","The read-only environment prevented the two `tmp_path` synthetic-tree tests from executing. The other 85 tests passed, all tests collected, and the two unchanged synthetic tests were inspected directly."],"reasoning":"The round history matches all three verdicts I issued. PKGV2-QA-001 and PKGV2-QA-002 are resolved: the validator now parses scanner arguments using argparse-compatible semantics and rejects omitted, wrong, separated-duplicate, equals-duplicate, and abbreviated duplicate node/graph bindings. Direct equals-form mutations were rejected. The active graph binds N20–N50 to exact node IDs and its own graph, leaves only N60 in complete-tree mode, preserves graph-derived narrowing, assigns N20 the egress boundary, uses package-local result paths, enforces the source-spec digest, and has no write overlap or production-path changes. Historical hashes and rules remain unchanged."}
```
