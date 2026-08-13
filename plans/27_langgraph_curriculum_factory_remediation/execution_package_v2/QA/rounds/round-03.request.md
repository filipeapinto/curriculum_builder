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


## Before you assess anything: audit the record

You have been in this session since round 1. You remember what you actually said.

Below is the round history as it appears on disk. Claude assembled the artifact and
the fixes; the file record could be wrong, whether by error or by convenience. Compare
it against your own memory and report in `honesty_audit`:

- `rounds_you_recall` — how many verdicts you personally issued, counted from your own
  memory of this conversation, not from the history below.
- `prior_rounds_consistent` — false if the history below attributes to you any verdict
  you did not give, claims a round that did not happen, or reports a finding of yours
  as resolved when you never saw it resolved.
- `discrepancies` — name each one specifically.

If your memory and the record disagree, say so plainly. That disagreement matters more
than this round's verdict, and it is the one thing nobody else can check for us.

### Round history on disk
- Round 1 (2026-08-13T17:49:42.504501+00:00): you returned FAIL with 1 finding(s) at threshold: Automated suite can pass while node mode and result versioning are broken
- Round 2 (2026-08-13T18:46:10.330860+00:00): you returned FAIL with 1 finding(s) at threshold: Duplicate arguments bypass the graph and node binding proof


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v3.yaml
Version: round 3 of at most 5
SHA-256: 022088872665b90210fc99099a482259d57677374fc26cf71e077e2aa59d6795

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

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

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v2.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/QA/session.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v3.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v3.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v3.md

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Verify PKGV2-T01 through PKGV2-T05 especially: read scan_node.py's DEFAULT_GRAPH_PATH and run_node/restrict_to_write_set logic directly, confirm every N20-N50 verification command carries an explicit --graph binding to this package's own graph, confirm validate_plan_v2.py actually rejects an omitted binding (not just documents it), and confirm N60 alone uses complete-tree mode.

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
Echo nothing; this is for the record only: 7b5cea5bfc4be3f56655cfee0649cb31372532bc3508e864bc07f003e4e5cd8f

Respond only in the required JSON shape.