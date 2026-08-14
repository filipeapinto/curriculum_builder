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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc6/rc6_review_bundle.v1.md
Version: round 1 of at most 1
SHA-256: 1fb3b60bfaa3216dbce339b8ad7f586807c828f8687724fa5f71a6ca9ed688e4

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# QA criteria — Run 27 execution package v2, release-candidate rc6

The artifact under review is `rc6_review_bundle.v1.md`, beside this file. It embeds,
verbatim and in full, this package's current corrected content: the graph
(`implementation.graph.v6.yaml`), the node-scoped/complete-tree scanner entry point
(`controller/scan_node.py`), the two validator entry points (`tools/validate_plan_v2.py`,
`tools/validate_result_v2.py`), the automated test suite
(`tests/test_execution_package_v2.py`), the three fresh node prompts
(`N00_spec_approval_gate.prompt.v6.md`, `N20_provider_transport.prompt.v6.md`,
`N30_preflight_egress.prompt.v6.md`), and the two artifacts this generation adds: the
package-scoped approval schema (`schemas/spec_approval.schema.v3.json`) and the approval
contract that validates against it (`contracts/spec_approval.v3.yaml`). Judge the text
embedded in the bundle itself — every criterion below can be checked directly against a
section of that one file.

## Why this session exists

This package's content already went through five independent review generations,
summarized in `release_candidate/rc5/QA_criteria.rc5.v1.md` (read that file directly for
the full history if useful; none of it is reopened, edited, or overridden here). rc3
(session `019ffcc7-a48f-7870-a933-5d80bb61dac3`) reached `QA_PASSED` / `chain_valid true`
and was approved by the user by exact hash in `contracts/spec_approval.v1.yaml`. rc4
`FAIL`ed (`RC4-QA-001`, a manifest omission); rc5 fixed it and reached `QA_PASSED` /
`chain_valid true`, carrying forward rc4's own fix for an unrelated N00-schema blocker
(`schemas/spec_approval.schema.v2.json` / `contracts/spec_approval.v2.yaml`,
`implementation.graph.v5.yaml`).

This rc6 snapshot exists because of what happened *after* rc5: `N20_PROVIDER_TRANSPORT`
was actually, genuinely executed for real against `implementation.graph.v5.yaml` — not a
rehearsal. It correctly rewrote `runtime/langgraph_factory/transport.py`, `egress.py`,
`model_nodes.py`, `config/model_jobs.v1.yaml`, `policy/routes.v1.yaml`,
`policy/routing/model_registry.v1.yaml`, and related schemas/tests, including
live-CLI-proven transport mechanics and a self-caught critical bug fix. All of that
production code is independently verified correct and is **not** touched by this
session. But N20 reached a genuine, well-evidenced `BLOCKED` — finding `N20V2-F01`,
recorded in
`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json`
— because `implementation.graph.v5.yaml` placed `tests/runtime/test_gemini.py` and
`tests/runtime/test_capabilities.py` in `N20_PROVIDER_TRANSPORT`'s write set, but those
two files test `runtime/gemini.py`, used only by a wholly separate, still-active Plan
11/19/20/21 curriculum pipeline (`runtime/capability_cycle.py`,
`runtime/model_worker.py`) this migration does not own. `rules.retired_provider_test_scan.scan_roots`
was `['tests/runtime']`, walked recursively with a zero-occurrence policy and no
exemption mechanism, so it legitimately found 16 real occurrences of "gemini" in exactly
those two unrelated files and failed — with no way to pass short of vandalizing correct,
unrelated test coverage or editing a file outside N20's write-set authority. Removing the
two files from N20's write set alone would be insufficient: `N60_ADVERSARIAL_REGRESSION`'s
verification runs the same scanner in complete-tree mode (no `--node`), which — since
`scan_roots` named the whole directory — would still recursively scan every file under
it, including the same two unrelated files, and fail identically at N60.

This rc6 snapshot fixes N20V2-F01 at the graph level, and nothing else:
`rules.retired_provider_test_scan.scan_roots` becomes the explicit, exact union of every
migration-owned active test file across N20 through N60 (17 files), replacing the
directory `['tests/runtime']`. `N20_PROVIDER_TRANSPORT.writes` drops the two unrelated
files (owned by no node in this graph). Because an explicit file path was already
supported, unmodified, by the parent scanning module's own `collect_files()` helper (it
checks `target.is_file()` before `target.is_dir()`), this required **no change to
`controller/check_forbidden_production_refs.py`** (which this package must not edit) and
no functional change to `controller/scan_node.py` beyond its own `DEFAULT_GRAPH_PATH`
constant — only the graph's own configuration narrowed. `implementation.graph.v5.yaml`
is preserved byte-for-byte at `deprecated/implementation.graph.v5.yaml`;
`N20_PROVIDER_TRANSPORT`'s `BLOCKED` result and evidence under it remain untouched,
immutable history. Because the active graph's own path and rules changed, this session
also introduces `schemas/spec_approval.schema.v3.json` (const-locking `approved_graph`
to v6 instead of v5) and `contracts/spec_approval.v3.yaml` (carrying forward — never
reinventing — the exact approval already recorded in `spec_approval.v2.yaml`: the same
specification, spec QA, rc3-manifest, and rc3-QA digests, the same eight model/effort
assignments — updated only for the new graph's path/digest and schema version;
`approved_rc_manifest` deliberately stays `rc3`, the approved package-structure
snapshot, not this session's own `rc6`), and mechanical gate-lineage renames of the three
prompts that reference the graph by exact filename. `spec_approval.schema.v2.json`,
`spec_approval.v2.yaml`, `N00_spec_approval_gate.prompt.v5.md`,
`N20_provider_transport.prompt.v5.md`, `N30_preflight_egress.prompt.v5.md`,
`implementation.graph.v4.yaml`, `implementation.graph.v5.yaml` (preserved at
`deprecated/`), and rc1 through rc5 in full (including each one's `QA/` session) are all
preserved exactly as they were and are **not** reopened, edited, or overridden here.
**Do not treat any prior session's history as evidence of anything in this session** — it
is cited above only to explain why this session exists. This session's own findings and
verdict are the only ones that count here.

## Criteria (PKGV2-T00–T18 carried forward against graph v6/schema v3/contract v3, PKGV2-T19–T24 new)

1. **PKGV2-T00 — Historical immutability.** The parent v1 package's graph, the first
   failed execution-package correction, `release_candidate/rc1/` through `rc5/` in full
   (including each one's `QA/` session), `spec_approval.schema.v1.json`,
   `spec_approval.v1.yaml`, `spec_approval.schema.v2.json`, `spec_approval.v2.yaml`, and
   every `*.prompt.v(1-5).md` file are unchanged from the live repository — verify
   directly.
2. **PKGV2-T01 — No silent v1 graph fallback.** Confirm `controller/scan_node.py`'s
   `DEFAULT_GRAPH_PATH` and every node-scoped `scan_node.py --node <ID>` verification
   command in `implementation.graph.v6.yaml` still explicitly binds `--graph` to
   `implementation.graph.v6.yaml`, and `tools/validate_plan_v2.py` still rejects an
   omitted binding.
3. **PKGV2-T02 — Node mode is a genuine narrowing.** Confirm `controller/scan_node.py`'s
   node mode still filters the parent module's unmodified whole-tree scan results rather
   than reimplementing scan logic — unchanged from rc5, and still true even though the
   scan_roots value it narrows has itself changed shape (directory → explicit file list).
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.** Confirm
   `implementation.graph.v6.yaml`'s N20/N30 write-set and read-only-input split, and
   `N30_preflight_egress.prompt.v6.md`'s read-only consumption language, are unchanged
   in substance from v5.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.** Confirm
   the correspondence still holds under the new explicit-file-list `scan_roots`.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** Unchanged from rc5, now against
   `implementation.graph.v6.yaml`.
7. **PKGV2-T06 — result/evidence versioning never reuses v1 paths.** Unchanged from rc5.
8. **PKGV2-T07 — source_spec binding.** Unchanged from rc5: `implementation.graph.v6.yaml`'s
   `source_spec` still names the QA-passed spec v4 at its exact digest.
9. **PKGV2-T08 — no write-set overlap.** You may run
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   against the live repository (read-only) and confirm `valid: true`.
10. **PKGV2-T09 — no implementation performed; no production edit.** `git status`
    (read-only) shows changes confined to
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/` (prompts,
    `implementation.graph.v6.yaml`, the moved `deprecated/implementation.graph.v5.yaml`,
    `schemas/`, `contracts/`, `tests/test_execution_package_v2.py`,
    `tools/validate_plan_v2.py`, `tools/validate_result_v2.py`,
    `controller/scan_node.py`, and `release_candidate/`). Any diff under `runtime/`,
    `policy/`, `schemas/routes.schema.v1.json`, or `schemas/model_registry.schema.v1.json`
    must be explainable entirely by `N20_PROVIDER_TRANSPORT.result.v1.json`'s own
    already-recorded `changed_files` (real, independently-verified, previously-admitted
    N20 production work this session does not touch) — confirm every such path's live
    SHA-256 matches that result's recorded hash exactly, and that no path outside that
    recorded set differs at all.
11. **PKGV2-T10 — automated proof, not narrative.** Confirm
    `tests/test_execution_package_v2.py` remains a real, passing, automated suite. You
    may run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    against the live repository (read-only) and confirm it passes (160 tests) — this runs
    the live originals the bundle text was copied from, proven byte-identical in
    `manifest.v1.json` beside the bundle.
12. **PKGV2-T11 — fresh-prompt graph-reference consistency, exact resolution, both flag
    spellings.** Confirm every graph-path reference in
    `N00_spec_approval_gate.prompt.v6.md`, `N20_provider_transport.prompt.v6.md`, and
    `N30_preflight_egress.prompt.v6.md` resolves to `implementation.graph.v6.yaml`,
    never a missing, stale, or wrong-prefixed filename — including that neither v6
    prompt still names `implementation.graph.v5.yaml` in an operative `--graph` command
    (a legitimate historical mention explaining the rename is not itself a binding
    reference and is not a defect).
13. **PKGV2-T12 — schema v3 const-locks the right package's own artifacts, not the
    parent's, and not schema v2's now-superseded graph.** In the bundle's
    `schemas/spec_approval.schema.v3.json` section, confirm `properties.approved_spec.const`
    equals `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
    and `properties.approved_graph.const` equals
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml`
    (not v5). Confirm every digest field remains `pattern`-typed, never a schema-level
    `const`.
14. **PKGV2-T13 — the RC-manifest field is deliberately not const-locked, and the graph
    field deliberately is; the reasoning for the asymmetry is sound.** Unchanged in
    substance from rc5's schema v2 criterion, now against schema v3's own `$comment`
    text — confirm it additionally explains that this session's own rc6 is supporting
    engineering QA for the graph correction, not a re-anchoring of the package's
    approval-of-record (which stays rc3).
15. **PKGV2-T14 — contract v3 carries forward the exact already-approved decision; it
    does not reinvent one, and does not silently re-anchor to a new RC.** In the
    bundle's `contracts/spec_approval.v3.yaml` section, confirm `approved_spec_sha256`,
    `spec_qa_verification_sha256`, `approved_rc_manifest_sha256`,
    `execution_package_qa_verification_sha256`, and `approved_at` are byte-identical to
    `spec_approval.v2.yaml`'s own values, and `approved_rc_manifest` still names `rc3`
    (not `rc6`) — only `approved_graph`/`approved_graph_sha256` advance, to
    `implementation.graph.v6.yaml`. Confirm `model_assignments` is unchanged from v2
    (M01/M06/M08 = claude-sonnet-5/xhigh; M02/M03/M04 = claude-sonnet-5/high; M05/M07 =
    gpt-5.6-sol/xhigh).
16. **PKGV2-T15 — the validator performs a real digest recompute, not a schema-shape
    check alone.** Unchanged from rc5's criterion, now against
    `CONTRACT_SCHEMA_PATH`/`CONTRACT_PATH` bound to schema v3/contract v3 in
    `tools/validate_plan_v2.py`.
17. **PKGV2-T16 — automated mutation proof for the schema v3 / contract v3 chain.**
    In the bundle's `tests/test_execution_package_v2.py` section, confirm dedicated
    tests: (a) prove `implementation.graph.v6.yaml`'s `rules.frozen_before_entry`
    includes `schemas/spec_approval.schema.v3.json` and excludes both schema v2 and the
    parent's schema v1; (b) prove `contracts/spec_approval.v3.yaml` validates against
    `schemas/spec_approval.schema.v3.json`; (c) prove each of the five bound digests
    recomputes against live bytes; (d) prove a copy of the contract with one bound
    digest changed to a wrong-but-well-formed value is rejected by the real validator
    function; (e) prove a copy with `approved_spec`, `approved_graph` (including a value
    naming the now-superseded v5), or a `model_assignments` entry changed to a wrong
    value is rejected; (f) prove an unmutated copy still passes; (g) prove
    `spec_approval.schema.v1.json` (the parent's) and `spec_approval.schema.v2.json`/
    `spec_approval.v2.yaml` (this package's own prior generation) are all byte-unchanged
    by hash comparison.
18. **PKGV2-T17 — N20/N30 prompt v6 are honest mechanical renames, not silent scope
    changes.** In the bundle's `N20_provider_transport.prompt.v6.md` and
    `N30_preflight_egress.prompt.v6.md` sections, confirm every TEST step, write-set
    claim, and substantive instruction is otherwise identical to their respective
    `*.prompt.v5.md` predecessors (available for direct comparison in the live
    repository, read-only) — only the literal `--graph` value(s) changed, plus each
    file's own explanatory header paragraph describing the N20V2-F01 correction.
19. **PKGV2-T18 — deprecated graph v5 is byte-identical to the graph N20 actually
    executed against.** Confirm `manifest.v1.json` contains a
    `deprecated/implementation.graph.v5.yaml` entry with recorded SHA-256
    `ce2362787a9760c9db3b2f667a0561ebd877ec89f24d690b2210ec9b6f3777b8` — the exact digest
    bound in `contracts/spec_approval.v2.yaml`'s `approved_graph_sha256` and cited in
    `N20_PROVIDER_TRANSPORT.result.v1.json`. This file is supplied as `--ground` material
    (genuinely static historical content); confirm the grounded copy's hash matches the
    manifest entry and the live `deprecated/` file.
20. **PKGV2-T19 — no node owns the two unrelated Gemini-pipeline test files.** In the
    bundle's `implementation.graph.v6.yaml` section, confirm no node's `writes` list
    contains `tests/runtime/test_gemini.py` or `tests/runtime/test_capabilities.py`
    (N20's own write set in particular must not, since v5's did). Confirm
    `tools/validate_plan_v2.py` contains a structural check that rejects any node
    owning either file, and `tests/test_execution_package_v2.py` proves it directly
    against the live graph.
21. **PKGV2-T20 — `retired_provider_test_scan.scan_roots` is the explicit, exact
    migration-owned union, not a directory.** In the bundle's
    `implementation.graph.v6.yaml` section, confirm `scan_roots` is a list of 17 exact
    `.py` file paths (never a directory entry), covering every `tests/runtime/test_*.py`
    file named in N20 through N60's own write sets (N20: 7 files after removing the two
    unrelated ones; N30: 3; N40: 4; N50: 2; N60: 1, `test_plan27_adversarial.py`, which
    does not exist on disk yet), and that it excludes `test_gemini.py`/
    `test_capabilities.py`. Confirm `tools/validate_plan_v2.py` rejects a directory
    entry, a non-`.py` entry, an entry with zero or more than one owning node, or either
    excluded file's presence.
22. **PKGV2-T21 — the missing future N60 test file causes no scan error.** Confirm
    `controller/scan_node.py`'s `collect_files` (in the unmodified parent module it
    imports) silently omits a `scan_roots` entry that is neither an existing file nor an
    existing directory, and `tests/test_execution_package_v2.py` proves, against the
    live repository, that `tests/runtime/test_plan27_adversarial.py`'s current absence
    causes no exception in any node-scoped scan (N20 through N50) nor in the current
    complete-tree scan.
23. **PKGV2-T22 — the scan-scope narrowing is a real behavioral fix, proven against the
    real repository, not merely a configuration relabeling.** In the bundle's
    `tests/test_execution_package_v2.py` section, confirm dedicated tests, run against
    the real repository and real graph (not only a synthetic fixture): (a) N20's own
    node-scoped scan (`scan_node.py --node N20_PROVIDER_TRANSPORT --graph
    implementation.graph.v6.yaml`) now passes with zero violations — the exact command
    that failed with 16 violations under graph v5; (b) a seeded forbidden reference
    (`# gemini`) written into one real migration-owned file from each of
    N20/N30/N40/N50's own set is caught by that node's own node-scoped scan AND by
    complete-tree mode, then the file is restored to its original content; (c) a seeded
    forbidden reference written into `test_gemini.py` and into `test_capabilities.py`
    is caught by **neither** node-scoped nor complete-tree mode (positive proof of the
    exemption, not merely today's absence of a violation), then each file is restored.
    Confirm the restoration is real (the test suite leaves the working tree
    byte-identical to before it ran) — a `try/finally` around the seed-and-restore, not
    merely a best-effort cleanup.
24. **PKGV2-T23 — the fix required no change to the shared, must-not-edit parent
    scanning module.** In the bundle's `implementation.graph.v6.yaml` and
    `controller/scan_node.py` sections, confirm the header/docstring text correctly
    explains that an explicit file path in `scan_roots` was already supported,
    unmodified, by `collect_files()` in
    `plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py`
    (checks `target.is_file()` before `target.is_dir()`), so this fix is a
    configuration narrowing of an existing, unmodified mechanism — confirm this claim by
    reading `collect_files`'s actual behavior (available in the live repository,
    read-only; not itself part of this bundle since it is unedited) rather than trusting
    the prose alone.

## Falsification targets

- `schemas/spec_approval.schema.v3.json`'s `model_assignments` sub-schema const-locks
  each of the eight job IDs' `model`/`effort` pair individually — confirm this constraint
  survived the v2→v3 edit unchanged, and is not merely an open `enum`.
- `contracts/spec_approval.v3.yaml`'s `approved_rc_manifest` still names `rc3`, not
  `rc6` — this is a deliberate, load-bearing design choice (see the narrative above and
  PKGV2-T14), not an oversight; confirm the contract's own prose explains it, and flag
  it as a genuine defect only if the reasoning itself does not hold up (e.g., if `rc3`'s
  own manifest no longer actually describes graph v6's write sets/rules — it should not,
  since `rc3` reviewed v3-era content and this correction is graph v6's own separate
  rc6 lineage, not a re-review of rc3's content).
- `tools/validate_plan_v2.py`'s new `retired_provider_test_scan.scan_roots` ownership
  check (`owners_of(nodes, root_value)`) must require **exactly one** owner, not "at
  least one" — confirm a hypothetical entry owned by two nodes (which cannot occur in
  the live graph, since no other structural check would allow overlapping ownership,
  but the check should not silently rely on that fact alone) would still be rejected on
  its own terms.
- `implementation.graph.v6.yaml`'s header claims no node, write set, edge, or
  verification *logic* changed in substance from v5 beyond the two write-set removals,
  the `scan_roots` narrowing, and the schema-version bump — confirm this against the
  bundle text directly (compare N10, N40–N90's sections byte-for-byte against v5, which
  remains available at `deprecated/implementation.graph.v5.yaml`) rather than trusting
  the header's own prose.
- The seeded-violation tests (PKGV2-T22b/c) mutate real files under `tests/runtime/`
  inside a `try/finally` — confirm the `finally` block runs even if an assertion inside
  the `try` block raises (i.e., the restore is not accidentally placed only on the
  success path), and confirm the test file's own final `git status --porcelain --
  tests/runtime` (read-only, run after the suite completes) shows no diff attributable
  to these tests beyond N20's own already-recorded real changes.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
twenty-four numbered criteria above (a stated criterion fails on a realistic reading of
the bundle, not merely a stylistic quibble). Anything you notice that does not defeat a
numbered criterion belongs in observations, not findings.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc6/deprecated/implementation.graph.v5.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc6/manifest.v1.json

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Judge the embedded bundle text itself as the reviewed logic (not a live version at the path), against every numbered criterion in QA_criteria.rc6.v1.md (PKGV2-T00 through T23), with particular attention to PKGV2-T19-T23 covering the scan-scope narrowing.

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