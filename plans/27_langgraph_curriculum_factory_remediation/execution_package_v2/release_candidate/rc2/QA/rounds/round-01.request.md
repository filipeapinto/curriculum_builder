You are the independent QA authority for the artifact below. A Claude agent authored
it and will act on whatever you find, but the verdict is yours alone. Claude cannot
overrule you, and a Claude claim that something passed carries no weight here.

Two failure modes are equally bad, so hold both in mind:

Passing something broken. Someone downstream depends on this working.

Failing something sound. Reviewers under pressure to be useful invent defects — they
flag what they would have done differently and dress it as a defect. That wastes
rounds and buries the real finding. The severity threshold below is not a suggestion
about tone; it is the definition of what counts as a finding at all.

Anything you notice that does not defeat a stated criterion goes in `observations`.
Observations are recorded permanently and never block. Use them freely — that is
where your judgement about taste, hardening, and alternatives belongs. What must not
happen is a preference being promoted to a finding to justify a FAIL.

A finding must name the criterion it defeats. If you cannot point at one, you have an
observation.


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc2/rc2_review_bundle.v1.md
Version: round 1 of at most 1
SHA-256: 5a0deece8bf50d094d3dde9b4ac420f3d27ae3944f3134c822292eb89380f7b9

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# QA criteria — Run 27 execution package v2, release-candidate rc2

The artifact under review is `rc2_review_bundle.v1.md`, beside this file. It embeds,
verbatim and in full, this package's current corrected content: the graph
(`implementation.graph.v4.yaml`), the node-scoped/complete-tree scanner entry point
(`controller/scan_node.py`), the two validator entry points (`tools/validate_plan_v2.py`,
`tools/validate_result_v2.py`), the automated test suite
(`tests/test_execution_package_v2.py`), and the three fresh node prompts
(`N00_spec_approval_gate.prompt.v4.md`, `N20_provider_transport.prompt.v4.md`,
`N30_preflight_egress.prompt.v4.md`). Judge the text embedded in the bundle itself —
every criterion below can be checked directly against a section of that one file.

## Why this session exists

This package's content already went through two independent review generations.
First, a four-round session
(`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/QA/`, session
`019ffc3b-6379-7ef3-839d-759ed5c7fc9c`) raised and legitimately fixed three real
findings (`PKGV2-QA-001`, `PKGV2-QA-002` twice), reached round-4 PASS, then had its own
`verify` step report `QA_FAILED` / `INTEGRITY_BREACH` because the four files those
findings were about had been supplied as `--ground` sources instead of reviewed
artifact content. That session is preserved exactly as it was and is not reopened here.

Second, a corrected one-round session built on the resulting release-candidate
pattern (`release_candidate/rc1/`, session `019ffcaa-f6b4-7d71-9005-0e53c79a5cc4`)
reviewed the same round-4-passing content correctly — as the single versioned artifact
`qa-gate-codex-run` judges, never as grounding — and returned a real, specific `FAIL`:
finding `RC1-QA-001`, "Automated suite does not prove fresh-prompt consistency." The
automated suite defined graph/scanner/validator paths but no prompt paths or
prompt-content assertions, so it stayed green while all three fresh node prompts
(`N00`, `N20`, `N30`) instructed a scan against `implementation.graph.v1.yaml` — a
filename this package does not contain — instead of the package's actually enforced
and graph-bound `implementation.graph.v4.yaml`. That session is preserved exactly as it
was, its `QA_FAILED` / `MAX_ITERATIONS_EXHAUSTED` verdict stands, and it is not
reopened, edited, or overridden here.

This rc2 snapshot fixes exactly that defect and nothing else: N00, N20, and N30 are
corrected to version 4 (`*.prompt.v4.md`, the superseded `*.prompt.v3.md` files and the
graph's own binding to them preserved unchanged as historical record), every graph-path
reference in their text now resolves to `implementation.graph.v4.yaml`, and the
automated suite gained a real, deterministic, mutation-proven regression test that
parses all three prompts' actual text and rejects a missing, stale, or mismatched graph
reference. **Do not treat either prior session's history as evidence of anything in
this session** — it is cited above only to explain why this session exists. This
session's own findings and verdict are the only ones that count here.

## Criteria (PKGV2-T00–PKGV2-T11)

1. **PKGV2-T00 — Historical immutability.** The parent v1 package's graph
   (`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`)
   and the first, failed execution-package correction
   (`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml`)
   are unchanged from the live repository, as are every
   `results/N00_SPEC_APPROVAL_GATE.result.v1.json`,
   `results/N10_HARNESS_PROTOCOL.result.v1.json`,
   `results/N20_PROVIDER_TRANSPORT.result.v1.json`, their `results/evidence/`
   directories, the root `QA/` session directory with its `PKG-QA-001` finding, and
   `release_candidate/rc1/` in full (its `manifest.v1.json`, `rc1_review_bundle.v1.md`,
   and `QA/` session directory) — all provided as grounding, below. The three
   Phase-A-restored files (`controller/check_forbidden_production_refs.py`,
   `tools/validate_plan.py`, `tools/validate_result.py` in the parent v1 package, not
   this one) retain their required admitted hashes (`cb530b32...`, `9f534ba3...`,
   `0beef6ed...`) — verify directly against the live repository, which you have
   read-only access to.
2. **PKGV2-T01 — No silent v1 graph fallback (the direct PKG-QA-001 fix).** In the
   bundle's `controller/scan_node.py` section, read `DEFAULT_GRAPH_PATH` and the
   argument parser. Confirm the default, and every fallback path, is this package's
   own graph file, never the parent v1 graph. Separately, in the bundle's
   `implementation.graph.v4.yaml` section, confirm every `N20_PROVIDER_TRANSPORT`
   through `N50_EVIDENCE_AUDIT_CONTROLS` node-scoped `scan_node.py --node <ID>`
   verification command also carries an explicit
   `--graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml`
   — the binding must be visible in the graph text itself, not merely correct by the
   scanner's internal default. Confirm the bundle's `tools/validate_plan_v2.py`
   section actively rejects a node-scoped scan command that omits this explicit
   binding (not merely documents that it should be present).
3. **PKGV2-T02 — Node mode is a genuine narrowing.** In the bundle's
   `controller/scan_node.py` section, read `run_node`/`restrict_to_write_set`.
   Confirm node mode is computed by calling the parent module's unmodified
   whole-tree `scan_production`/`scan_tests` and then filtering the resulting
   scanned-file and violation lists to the node's own write-set intersection — not a
   reimplementation of the term/credential/guard-region/occurrence rules. Confirm it
   cannot scan more broadly than the whole-tree scopes would, and cannot skip a file
   within the node's write set that either whole-tree scope would have scanned.
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.** In the bundle's
   `implementation.graph.v4.yaml` section, confirm `runtime/langgraph_factory/egress.py`
   and `tests/runtime/test_plan26_egress.py` are in `N20_PROVIDER_TRANSPORT`'s
   `writes` list and absent from `N30_PREFLIGHT_EGRESS`'s, and that
   `N30_PREFLIGHT_EGRESS` declares `runtime/langgraph_factory/egress.py` under
   `read_only_inputs`. In the bundle's `N30_preflight_egress.prompt.v4.md` section,
   confirm the prompt explicitly states N30 consumes this boundary read-only and does
   not claim ownership.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.** For
   every scanning node, the files the node-scoped scan actually covers (verify by
   reading the bundle's `controller/scan_node.py` logic) are exactly the intersection
   of that node's `writes` list (bundle's `implementation.graph.v4.yaml` section) with
   the two whole-tree scan scopes' roots — not a hardcoded or hand-maintained file
   list that could drift from the graph.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** In the bundle's
   `implementation.graph.v4.yaml` section, read every node's verification list.
   Confirm `scan_node.py` is invoked without `--node` only for
   `N60_ADVERSARIAL_REGRESSION`, and with `--node <exact node ID>` for every other
   scanning node (`N20`–`N50`).
7. **PKGV2-T06 — result/evidence versioning never reuses v1 paths.** In the bundle's
   `implementation.graph.v4.yaml` section, confirm every node's own result/evidence
   write path lives under
   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/`,
   never the parent v1 package's `results/` root nor the failed correction's
   `results/v2/` root, and that `result_pattern` in the graph header reflects this.
8. **PKGV2-T07 — source_spec binding.** In the bundle's `implementation.graph.v4.yaml`
   section, confirm the graph's `source_spec` field points at the QA-passed
   specification artifact
   (`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
   sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`), not v1,
   v2, or v3-by-filename. In the bundle's `tools/validate_plan_v2.py` section, confirm
   it enforces both the path and the digest, not merely the path.
9. **PKGV2-T08 — no write-set overlap.** In the bundle's `implementation.graph.v4.yaml`
   section, confirm every write path belongs to exactly one node; no two nodes claim
   overlapping paths. You may also run
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   against the live repository (read-only) and confirm it reports `valid: true` —
   note this runs the live, unmodified originals this bundle was copied from, not the
   bundle text itself, and is cited as a fact to confirm, not evidence to accept
   unchecked.
10. **PKGV2-T09 — no implementation performed; no production edit.** No file under
    `runtime/`, `policy/`, `schemas/routes.schema.v1.json`, or
    `schemas/model_registry.schema.v1.json` was created or changed while authoring
    this package or this release-candidate snapshot. `git status` (available to you
    read-only) shows changes confined to
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/`
    (new `*.prompt.v4.md` files),
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml`,
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`,
    and
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/` only.
11. **PKGV2-T10 — automated proof, not narrative.** In the bundle's
    `tests/test_execution_package_v2.py` section, confirm it is a real, passing,
    automated suite (not a documentation file) that positively proves PKGV2-T01
    through PKGV2-T09 above, including at least one seeded violation in a synthetic
    tree proving node-scope narrowing actually rejects a defect, one proving the same
    defect surfaces in complete-tree mode, and one proving `git status` shows no
    production/policy/schema/active-test change from authoring this package. You may
    run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    against the live repository (read-only) yourself if useful and confirm it passes
    — again, this runs the live originals the bundle text was copied from, not the
    bundle text itself; the two are proven byte-identical in `manifest.v1.json`
    beside the bundle.
12. **PKGV2-T11 — fresh-prompt graph-reference consistency (the direct RC1-QA-001
    fix).** In the bundle's `N00_spec_approval_gate.prompt.v4.md`,
    `N20_provider_transport.prompt.v4.md`, and `N30_preflight_egress.prompt.v4.md`
    sections, confirm every graph-path reference each prompt's own text makes —
    every `--graph <path>` shell-command argument and every "Require `<path>` to
    exist" requirement — resolves to this package's actually enforced graph,
    `implementation.graph.v4.yaml`, never a missing, stale, or otherwise mismatched
    filename. In the bundle's `tests/test_execution_package_v2.py` section, confirm
    the suite contains a real, deterministic test that parses these three prompts'
    actual text (not merely the graph's own `verification` command list, which was
    already covered) and fails on a missing, stale, or mismatched reference — and
    confirm this is proven as a real regression test, not a vacuous positive
    assertion: it must be shown to actually reject the exact historical defective
    text that produced RC1-QA-001 (the superseded `*.prompt.v3.md` files, embedded in
    RC1's own bundle and still present on disk, unchanged, as historical fixtures),
    not merely assert something true about the already-corrected v4 text.

## Falsification targets

- The bundle's `controller/scan_node.py` `DEFAULT_GRAPH_PATH` is computed once at
  import time from `Path(__file__).resolve()`; confirm the logic genuinely resolves
  to this package's own graph and not, by an off-by-one `.parent` chain, to the
  parent v1 package's directory (judge the logic as written; do not assume it is
  correct because a prior round said so).
- The three fresh prompts' claimed write-set/ownership language matches the graph's
  actual `writes`/`read_only_inputs` for that node exactly (no prompt claiming an
  ownership the graph does not grant, or vice versa).
- The bundle's `tools/validate_plan_v2.py` node-scoped-graph-binding check
  (`node_scoped_scan_commands`, `flag_values`, and the loop that requires `--graph`)
  is not itself silently vacuous — for example by matching on a substring that would
  also match an unrelated command, by only checking nodes that happen to already be
  correct, or by miscounting occurrences for any argparse-accepted spelling
  (`--node value`, `--node=value`, an unambiguous prefix abbreviation).
- N40, N50, N60, N70, N80, N90's prompts are reused unmodified from the parent v1
  package's `prompts/` directory because this correction does not change their scope
  — confirm the bundle's `implementation.graph.v4.yaml` section actually points at
  those unmodified files rather than silently forking them.
- The new PKGV2-T11 test's graph-reference parser is not itself silently vacuous —
  for example by matching a pattern general enough to also match an unrelated,
  legitimate historical filename mention (this package's prose legitimately names
  the parent's own superseded `implementation.graph.v2.yaml` by way of explaining
  the `PKG-QA-001` finding; that is not itself a binding reference and must not be
  required to equal the enforced graph), or narrow enough to silently skip a real
  stale reference by relying only on a single phrasing the corrected text happens to
  use.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the twelve
numbered criteria above (a stated criterion fails on a realistic reading of the
bundle, not merely a stylistic quibble). Anything you notice that does not defeat a
numbered criterion belongs in observations, not findings.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v2.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/QA/session.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/QA/session.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/QA/verification.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc1/manifest.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc1/QA/session.json

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Verify PKGV2-T11 above all: does every graph-path reference in N00/N20/N30's own prompt text (every --graph flag value and every 'Require `X` to exist' requirement) actually resolve to implementation.graph.v4.yaml, and does the automated suite's new regression test genuinely prove this by rejecting the real historical RC1-QA-001 defect (the superseded v3 prompts), not merely assert something true about the already-corrected text. Also re-confirm T01, T05, T06, T09, T10 are still intact and that nothing outside the stated scope changed.

This narrows where you look. It does not lower the bar for what you find
there, and a blocker spotted outside this area is still a blocker.

## Severity threshold: major

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `major` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: GENESIS

Respond only in the required JSON shape.