# QA criteria — Run 27 execution package v2, release-candidate rc8

The artifact under review is `rc8_review_bundle.v1.md`, beside this file. It embeds,
verbatim and in full, this package's current corrected content: the graph
(`implementation.graph.v7.yaml`), the node-scoped/complete-tree scanner entry point
(`controller/scan_node.py`), the two validator entry points (`tools/validate_plan_v2.py`,
`tools/validate_result_v2.py`), the automated test suite
(`tests/test_execution_package_v2.py`), the three node prompts
(`N00_spec_approval_gate.prompt.v7.md`, `N20_provider_transport.prompt.v7.md`,
`N30_preflight_egress.prompt.v7.md`), the package-scoped approval schema
(`schemas/spec_approval.schema.v4.json`), the approval contract that validates against
it (`contracts/spec_approval.v4.yaml`), and the superseded
`deprecated/implementation.graph.v6.yaml` (supplied for its own byte-identity check, not
as logic under review). Judge the text embedded in the bundle itself — every criterion
below can be checked directly against a section of that one file.

## Why this session exists

Independent verification of `release_candidate/rc7` (`QA_PASSED`, chain-valid, session
`019ffd88-b735-77c0-ad8d-145ba014751a`) found one real execution-lineage blocker rc7's
own QA criteria did not cover: `implementation.graph.v6.yaml`'s `result_pattern`
(`execution_package_v2/results/{node_id}.result.v1.json`) is byte-identical to
`implementation.graph.v5.yaml`'s own. `N00_SPEC_APPROVAL_GATE` and
`N10_HARNESS_PROTOCOL` are already ADMITTED (`PASSED`) and `N20_PROVIDER_TRANSPORT` is
already `BLOCKED` (finding `N20V2-F01`), all three with real results at that exact
shared path
(`execution_package_v2/results/{N00_SPEC_APPROVAL_GATE,N10_HARNESS_PROTOCOL,N20_PROVIDER_TRANSPORT}.result.v1.json`).
Because graph v6 genuinely rebound N00's prompt/schema (to prompt v6 / schema v3), the
already-admitted N00 result's recorded `prompt_sha256` no longer matches the live
prompt v6 file: running `tools/validate_result_v2.py --node N00_SPEC_APPROVAL_GATE`
against graph v6 as originally built genuinely returns `{"error":
"N00_SPEC_APPROVAL_GATE: prompt hash mismatch", "valid": false}` (independently
reproducible, read-only, against the live repository as it stood before this rc8
generation existed). If any of N00, N10, or N20 were re-executed under graph v6, the
new result JSON would be written to the exact same path as the existing admitted or
blocked record, silently overwriting it — directly violating this whole recovery
effort's repeated, explicit "preserve prior attempts, never overwrite an admitted or
blocked record" requirement, and doing so invisibly: nothing about such a write is
malformed, so no schema or scan check would catch it, only path collision does.

This rc8 bundle fixes exactly that defect and makes **no other change**:
`implementation.graph.v6.yaml` is deprecated properly (preserved byte-for-byte at
`deprecated/implementation.graph.v6.yaml`, unchanged at sha256
`b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26`), and
`implementation.graph.v7.yaml` is introduced with `result_pattern` (and every node's
own result-write and evidence-root entries in `writes`) moved to the versioned
subdirectory `execution_package_v2/results/v7/`, whose per-node filenames never
coincide with the flat per-node files directly under `execution_package_v2/results/`.
`schemas/spec_approval.schema.v4.json` and `contracts/spec_approval.v4.yaml` carry
forward rc3's already-approved specification/RC-manifest/QA digests and model
assignments unchanged, updated only for the new graph's path/digest and schema
version. The three prompts are mechanical gate-lineage renames of their v6
predecessors, with no substantive `TEST` requirement changed.
`controller/scan_node.py`'s `DEFAULT_GRAPH_PATH` and both `tools/validate_*.py`
modules' own graph/schema/contract/result-prefix bindings move to this generation's
own artifacts, following the exact same per-generation hardcoded-binding discipline
already used across v1 through v6 — neither validator grows a mutable `--graph` flag of
its own (see `tools/validate_result_v2.py`'s own updated module docstring for the
reasoning: adding one would reintroduce the exact PKG-QA-001 defect class — a silently
omittable/wrong graph binding — this package's tooling already exists to prevent).
`tests/test_execution_package_v2.py` gains a dedicated "RC8: result-namespace collision
/ preservation proofs" section (175 tests total, 14 more than rc7's 161).

`release_candidate/rc1` through `rc7` in full (including each one's `QA/` session),
`implementation.graph.v4.yaml`/`v5.yaml` (preserved at `deprecated/`),
`spec_approval.schema.v1.json`/`v2.json`/`v3.json`,
`spec_approval.v1.yaml`/`v2.yaml`/`v3.yaml`, every `*.prompt.v(1-6).md` file, and every
N00/N10/N20 result and its evidence are preserved exactly as they were and are **not**
reopened, edited, or overridden by this bundle or this session. **Do not treat any
prior session's history as evidence of anything in this session** — it is cited above
only to explain why this session exists. This session's own findings and verdict are
the only ones that count here.

## Criteria (PKGV2-T00–T24 and RC7-T01–T02 carried forward unchanged against
## byte-identical-in-substance content; RC8-T01–T06 new, covering the result-namespace
## collision fix itself)

1. **PKGV2-T00 — Historical immutability.** The parent v1 package's graph, the first
   failed execution-package correction, `release_candidate/rc1/` through `rc7/` in full
   (including each one's `QA/` session), `spec_approval.schema.v1.json` through `v3.json`,
   `spec_approval.v1.yaml` through `v3.yaml`, and every `*.prompt.v(1-6).md` file are
   unchanged from the live repository — verify directly.
2. **PKGV2-T01 — No silent stale-graph fallback.** Confirm `controller/scan_node.py`'s
   `DEFAULT_GRAPH_PATH` and every node-scoped `scan_node.py --node <ID>` verification
   command in `implementation.graph.v7.yaml`'s own text still explicitly binds `--graph`
   to `implementation.graph.v7.yaml`, and `tools/validate_plan_v2.py` still rejects an
   omitted binding.
3. **PKGV2-T02 — Node mode is a genuine narrowing.** Confirm `controller/scan_node.py`'s
   node mode still filters the parent module's unmodified whole-tree scan results rather
   than reimplementing scan logic.
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.** Confirm
   `implementation.graph.v7.yaml`'s N20/N30 write-set and read-only-input split, and
   `N30_preflight_egress.prompt.v7.md`'s read-only consumption language, are unchanged in
   substance from v6.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.** Confirm
   the correspondence still holds under the explicit-file-list `scan_roots`.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** Unchanged, against
   `implementation.graph.v7.yaml`.
7. **PKGV2-T06 — result/evidence versioning never reuses a colliding path.** Confirm
   `implementation.graph.v7.yaml`'s `result_pattern`
   (`execution_package_v2/results/v7/{node_id}.result.v1.json`) and every node's own
   result-write and evidence-root entries in `writes` live under
   `execution_package_v2/results/v7/`, never the parent v1 package's `results/` root,
   the failed correction's `results/v2/` root, nor this package's own earlier flat
   `results/` root (where the admitted N00/N10 results and the BLOCKED N20 result
   permanently live).
8. **PKGV2-T07 — source_spec binding.** Unchanged: `implementation.graph.v7.yaml`'s
   `source_spec` still names the QA-passed spec v4 at its exact digest.
9. **PKGV2-T08 — no write-set overlap.** You may run
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   against the live repository (read-only) and confirm `valid: true`.
10. **PKGV2-T09 — no implementation performed; no production edit.** `git status`
    (read-only) shows changes confined to
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/`
    (`controller/`, `tools/`, `tests/`, and `release_candidate/rc8/`). Any diff under
    `runtime/`, `policy/`, `schemas/routes.schema.v1.json`, or
    `schemas/model_registry.schema.v1.json` must be explainable entirely by
    `results/N20_PROVIDER_TRANSPORT.result.v1.json`'s own already-recorded
    `changed_files` (real, independently-verified, previously-admitted N20 production
    work this session does not touch) — confirm every such path's live SHA-256 matches
    that result's recorded hash exactly, and that no path outside that recorded set
    differs at all.
11. **PKGV2-T10 — automated proof, not narrative.** Confirm
    `tests/test_execution_package_v2.py` remains a real, passing, automated suite. You
    may run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    against the live repository (read-only) and confirm it passes (175 tests, 14 more
    than rc7's 161 — the new RC8 collision/preservation section) — this runs the live
    originals the bundle text was copied from, proven byte-identical in
    `manifest.v1.json` beside the bundle.
12. **PKGV2-T11 — fresh-prompt graph-reference consistency, exact resolution, both flag
    spellings.** Confirm every graph-path reference in
    `N00_spec_approval_gate.prompt.v7.md`, `N20_provider_transport.prompt.v7.md`, and
    `N30_preflight_egress.prompt.v7.md` resolves to `implementation.graph.v7.yaml`.
13. **PKGV2-T12 — schema v4 const-locks the right package's own artifacts.** In the
    bundle's `schemas/spec_approval.schema.v4.json` section, confirm
    `properties.approved_spec.const` equals
    `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
    and `properties.approved_graph.const` equals
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml`.
    Confirm every digest field remains `pattern`-typed, never a schema-level `const`.
14. **PKGV2-T13 — the RC-manifest field is deliberately not const-locked, and the graph
    field deliberately is.** Unchanged in substance from rc7's schema v3 criterion.
15. **PKGV2-T14 — contract v4 carries forward the exact already-approved decision.** In
    the bundle's `contracts/spec_approval.v4.yaml` section, confirm
    `approved_spec_sha256`, `spec_qa_verification_sha256`, `approved_rc_manifest_sha256`,
    `execution_package_qa_verification_sha256`, and `approved_at` are byte-identical to
    `spec_approval.v3.yaml`'s own values, and `approved_rc_manifest` still names `rc3`
    (not `rc6`, `rc7`, or `rc8`) — only `approved_graph`/`approved_graph_sha256` name
    `implementation.graph.v7.yaml`. Confirm `model_assignments` is unchanged from v3.
16. **PKGV2-T15 — the validator performs a real digest recompute.** Unchanged, against
    `CONTRACT_SCHEMA_PATH`/`CONTRACT_PATH` bound to schema v4/contract v4 in
    `tools/validate_plan_v2.py`.
17. **PKGV2-T16 — automated mutation proof for the schema v4 / contract v4 chain.**
    Unchanged from rc7's criterion; confirm the relevant tests are still present, intact,
    and passing in the bundle's `tests/test_execution_package_v2.py` section.
18. **PKGV2-T17 — N20/N30 prompt v7 are honest mechanical renames.** Unchanged from
    rc7's criterion.
19. **PKGV2-T18 — deprecated graph v6 is byte-identical to the graph rc7 approved.**
    Confirm `manifest.v1.json` contains a `deprecated/implementation.graph.v6.yaml`
    entry with recorded SHA-256
    `b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26`, and that the
    bundle's own `deprecated/implementation.graph.v6.yaml` section's embedded content
    hashes to the same value.
20. **PKGV2-T19 — no node owns the two unrelated Gemini-pipeline test files.** Unchanged
    from rc7's criterion — carried forward from graph v6.
21. **PKGV2-T20 — `retired_provider_test_scan.scan_roots` is the explicit, exact
    migration-owned union, not a directory.** Unchanged from rc7's criterion.
22. **PKGV2-T21 — the missing future N60 test file causes no scan error.** Unchanged
    from rc7's criterion.
23. **PKGV2-T22 — the N20V2-F01 scan-scope fix is carried forward, not regressed.** In
    the bundle's `tests/test_execution_package_v2.py` section, confirm the dedicated
    N20 real-node-scoped-scan zero-violations tests from rc7 are still present and
    unchanged in substance, and confirm `implementation.graph.v7.yaml`'s
    `retired_provider_test_scan.scan_roots` and `N20_PROVIDER_TRANSPORT.writes` are
    byte-identical in substance to `implementation.graph.v6.yaml`'s own (both embedded
    in the bundle for direct comparison).
24. **PKGV2-T23 — the fix required no change to the shared, must-not-edit parent
    scanning module.** Unchanged from rc7's criterion.
25. **RC7-T01 (carried forward) — the bundle is genuinely byte-identical, not merely
    re-asserted to be.** For at least three of the eleven fenced sections in
    `rc8_review_bundle.v1.md` of your own choosing (not all eleven need be checked, but
    do not choose only the shortest), extract the fenced content exactly as delimited
    by its opening and closing fence lines, recompute its SHA-256, and confirm it
    equals both the SHA-256 stated in that section's own trailing "SHA-256: `...`" line
    and the SHA-256 recorded for that path in `manifest.v1.json`. Report a failure only
    if you find an actual mismatch.
26. **RC7-T02 (carried forward) — the N20 zero-violations regression proof remains
    intact.** In the bundle's `tests/test_execution_package_v2.py` section, confirm
    `test_n20_node_mode_includes_its_newly_owned_egress_module_and_test` and
    `test_n20_real_node_scoped_scan_is_the_regression_proof_that_n20v2_f01_is_fixed`
    are both still present and still assert zero violations for
    `N20_PROVIDER_TRANSPORT` specifically.
27. **RC8-T01 — the result-namespace collision genuinely cannot recur.** In the
    bundle's `implementation.graph.v7.yaml` section, confirm `result_pattern` is
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/{node_id}.result.v1.json`
    and that every node's own result-write and evidence-root `writes` entries live
    under that same `results/v7/` root — never the flat `results/` root the
    admitted/blocked N00/N10/N20 records occupy.
28. **RC8-T02 — the validator honestly reports absence, not a stale pass or a silent
    overwrite path.** In the bundle's `tools/validate_result_v2.py` section, confirm
    `GRAPH_PATH` is bound to `implementation.graph.v7.yaml`. You may run
    `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py --node N00_SPEC_APPROVAL_GATE`
    (and the same for `N10_HARNESS_PROTOCOL`, `N20_PROVIDER_TRANSPORT`) against the live
    repository, read-only, and confirm each returns exit code 1 with `"valid": false`
    and an error naming a missing file under `results/v7/` — never a hash mismatch
    against the old file, and never exit code 0.
29. **RC8-T03 — the admitted/blocked historical records are byte-for-byte unchanged.**
    You may run, read-only,
    `shasum -a 256 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N10_HARNESS_PROTOCOL.result.v1.json plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json`
    against the live repository and confirm the three hashes match the bundle's
    `tests/test_execution_package_v2.py` section's own
    `ADMITTED_OR_BLOCKED_RESULT_HASHES` values exactly.
30. **RC8-T04 — graph v7 is otherwise unchanged in substance from graph v6.** In the
    bundle, compare `implementation.graph.v7.yaml`'s `edges`, `terminals`,
    `rules.forbidden_production_scan`, `rules.retired_provider_test_scan`, and every
    node's `depends_on`/`read_only_inputs`/`allowed_results`/non-result `writes` entries
    against `deprecated/implementation.graph.v6.yaml`'s own section, and confirm they
    are identical apart from the result/evidence path segment and the `--graph`
    literal values.
31. **RC8-T05 — `tools/validate_result_v2.py` deliberately keeps its no-`--graph`-flag
    design.** Confirm the module's own docstring (embedded in the bundle) explains this
    is deliberate — reintroducing a mutable/omittable `--graph` flag here would repeat
    the PKG-QA-001 defect class this package's tooling already exists to prevent — and
    is not an oversight this rc8 generation failed to address. This is a design-review
    criterion: report a finding only if you believe the no-flag design is actually
    wrong for this validator, with a concrete scenario it fails to handle that an
    explicit flag would fix.
32. **RC8-T06 — the collision fix required no re-execution and no new approval
    beyond rc3's own.** Confirm `contracts/spec_approval.v4.yaml`'s
    `approval_statement` explains the fix as carrying forward rc3's approval unchanged
    (only `approved_graph`/`approved_graph_sha256`/`schema_version` move), and that no
    N00/N10/N20 result was re-executed, edited, or newly authored by this session
    (PKGV2-T00/RC8-T03 already establish their byte-identity).

## Falsification targets

- Do not accept the header prose's stated SHA-256 for any of the eleven fenced sections
  at face value — recompute at least three yourself (RC7-T01).
- `implementation.graph.v7.yaml`'s header claims no node, write set, edge, or
  verification *logic* changed in substance from v6 beyond the result/evidence path move
  and the `--graph` literal renames — confirm this against the bundle text directly
  (compare N10, N40–N90's sections byte-for-byte against v6, which remains available at
  `deprecated/implementation.graph.v6.yaml` in the same bundle).
- `tools/validate_result_v2.py`'s claim that it "cannot" silently collide is a design
  claim, not merely an assertion — trace through what happens if this tool were run
  with a fresh result for `N00_SPEC_APPROVAL_GATE`: does `result_path` resolve to
  `results/v7/N00_SPEC_APPROVAL_GATE.result.v1.json` (a path distinct from the admitted
  record) in every code path, or is there any way `GRAPH_PATH`/`result_pattern`
  resolution could still land on the legacy path?
- The RC8 test section's `test_admitted_or_blocked_result_file_is_byte_unchanged` and
  `test_validate_result_v2_reports_missing_not_a_collision_for_admitted_nodes` tests
  must not silently pass by accident (e.g. by asserting on the wrong path, or by
  catching an exception that would mask a real overwrite) — read their assertions
  directly rather than trusting their names.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
thirty-two numbered criteria above (a stated criterion fails on a realistic reading of
the bundle, not merely a stylistic quibble). Anything you notice that does not defeat a
numbered criterion belongs in observations, not findings.
