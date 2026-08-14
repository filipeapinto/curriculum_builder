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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc5/rc5_review_bundle.v1.md
Version: round 1 of at most 1
SHA-256: afaef1bad7e1be615b9f7d13c4bf15f7e5a0d86c1019d58a3644c096d0454bfd

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# QA criteria — Run 27 execution package v2, release-candidate rc5

The artifact under review is `rc5_review_bundle.v1.md`, beside this file. It embeds,
verbatim and in full, this package's current corrected content: the graph
(`implementation.graph.v5.yaml`), the node-scoped/complete-tree scanner entry point
(`controller/scan_node.py`), the two validator entry points (`tools/validate_plan_v2.py`,
`tools/validate_result_v2.py`), the automated test suite
(`tests/test_execution_package_v2.py`), the three fresh node prompts
(`N00_spec_approval_gate.prompt.v5.md`, `N20_provider_transport.prompt.v5.md`,
`N30_preflight_egress.prompt.v5.md`), and the two new artifacts this generation adds:
the package-scoped approval schema (`schemas/spec_approval.schema.v2.json`) and the
approval contract that validates against it (`contracts/spec_approval.v2.yaml`). Judge
the text embedded in the bundle itself — every criterion below can be checked directly
against a section of that one file.

## Why this session exists

This package's content already went through four independent review generations. The
first three are summarized in `release_candidate/rc3/QA_criteria.rc3.v1.md` (a
four-round session with a preserved `INTEGRITY_BREACH` self-report, then `rc1`
`FAIL`/`RC1-QA-001`, then `rc2` `FAIL`/`RC2-QA-001`) — read that file directly for the
full history if useful; none of it is reopened, edited, or overridden here.

The fourth, `rc3` (session `019ffcc7-a48f-7870-a933-5d80bb61dac3`), reached
`QA_PASSED` / `chain_valid true`, 0 problems, and the user approved it — and
`implementation.graph.v4.yaml`, its own specification v4, and their digests — by
exact hash in `contracts/spec_approval.v1.yaml`. That session is preserved exactly as
it was and is not reopened here. But attempting to actually *execute* `N00` against
that approval, after it was recorded, surfaced a defect no prior QA round's criteria
covered: `plans/27_langgraph_curriculum_factory_remediation/schemas/spec_approval.schema.v1.json`
— the *parent* v1 Run 27 package's own frozen approval schema, shared infrastructure
across the whole Run 27 effort — const-locks its `approved_spec` field to the parent
package's own spec
(`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`),
a path this package's approved specification v4
(`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`)
can never equal. Validation against it fails structurally and unconditionally no
matter how the approval record is filled in — this is not a missing-field or
wrong-value defect an approval record could ever fix; the schema itself cannot
validate this package's approval. `N00_spec_approval_gate.prompt.v4.md`'s own TEST
step 6 additionally claimed that schema "is frozen and unversioned per
`rules.frozen_before_entry`", which was also false: `implementation.graph.v4.yaml`'s
own `rules.frozen_before_entry` never listed it, only
`node_result.schema.v1.json`. Neither defect was in scope for rc1/rc2/rc3's own
criteria, which covered graph/scanner/validator/prompt internal consistency, not this
specific cross-package schema-compatibility fact.

The immediately prior release candidate, `release_candidate/rc4/` (session
`019ffd00-2b26-7f41-8db3-d69508c73480`), returned a real, specific `FAIL`:
finding `RC4-QA-001`, "RC4 manifest omits the deprecated approved graph." rc4's
own `manifest.v1.json` bound every reviewed file's SHA-256 but never listed
`deprecated/implementation.graph.v4.yaml` at all, even though rc4's own
criterion PKGV2-T18 (below, unchanged) explicitly requires that file's SHA-256
to be recorded in the manifest so a consumer can verify the move to
`deprecated/` preserved the user's originally approved graph byte-for-byte.
The live file's digest was, and remains, correct
(`0d5b5af8b0c60847e3b52ac93c4c10328f48a1404130a6b785485bcbbae3d571`) — the
defect was an incomplete manifest, not a wrong digest or a mutated file. rc4,
its `QA/` session, and its `QA_FAILED` / `MAX_ITERATIONS_EXHAUSTED` verdict
are preserved exactly as they were and are **not** reopened, edited, or
overridden by this snapshot or this session.

This rc5 snapshot fixes exactly that omission and nothing else: `manifest.v1.json`
now includes a `deprecated/implementation.graph.v4.yaml` entry bound to the
digest above, and that file itself is supplied to this session as `--ground`
material (genuinely static historical content, unchanged since it was
originally approved — not logic under review, so it does not belong embedded
in the review bundle) so the binding is verifiable inside this session's own
tamper-evident hash chain rather than only against ambient repository state.
Every other reviewed file (the graph, scanner, validators, test suite,
prompts, schema v2, contract v2) is byte-identical to rc4's own copies —
confirmed by SHA-256 equality in `manifest.v1.json` beside this file.

This rc5 snapshot also fixes, by user's exact design (unchanged narrative from
rc4, restated below for completeness): a new
package-scoped `schemas/spec_approval.schema.v2.json` that const-locks the *right*
specification and this package's own active graph (instead of the parent package's),
a new `contracts/spec_approval.v2.yaml` that carries forward — never reinvents — the
exact five digests and model/effort decision already recorded in
`contracts/spec_approval.v1.yaml`'s `approval_statement`, now as schema-validated
structured fields, `implementation.graph.v5.yaml` (a gate-lineage rename of v4, the
same mechanical discipline v3→v4 already established, now also declaring schema v2 in
its own `rules.frozen_before_entry` alongside the pre-existing
`node_result.schema.v1.json` entry), and `N00_spec_approval_gate.prompt.v5.md` (which
validates against schema v2 and states the frozen-schema claim accurately). Because
the graph's own filename changed, `N20_provider_transport.prompt.v5.md` and
`N30_preflight_egress.prompt.v5.md` are also included: they are mechanical
gate-lineage renames of their own v4 predecessors (only their own literal `--graph`
values changed, from `implementation.graph.v4.yaml` to `implementation.graph.v5.yaml`)
— without this, those two prompts' own fresh instructions would go stale relative to
the newly-enforced graph, recreating the exact class of defect `RC1-QA-001` found.
`spec_approval.schema.v1.json`, `spec_approval.v1.yaml`,
`N00_spec_approval_gate.prompt.v4.md`, `N20_provider_transport.prompt.v4.md`,
`N30_preflight_egress.prompt.v4.md`, `implementation.graph.v4.yaml` (preserved at
`deprecated/implementation.graph.v4.yaml`), and rc1/rc2/rc3 in full (including rc3's
`QA/` session) are all preserved exactly as they were and are not reopened, edited, or
overridden here. **Do not treat any prior session's history as evidence of anything in
this session** — it is cited above only to explain why this session exists. This
session's own findings and verdict are the only ones that count here.

## Criteria (PKGV2-T00–T11 carried forward, PKGV2-T12–T18 new)

1. **PKGV2-T00 — Historical immutability.** The parent v1 package's graph, the first
   failed execution-package correction, `release_candidate/rc1/`, `rc2/`, and `rc3/`
   in full, `spec_approval.schema.v1.json`, `spec_approval.v1.yaml`, and every
   `*.prompt.v4.md` file are unchanged from the live repository — verify directly.
2. **PKGV2-T01 — No silent v1 graph fallback.** Unchanged from rc3: confirm
   `controller/scan_node.py`'s `DEFAULT_GRAPH_PATH` and every node-scoped
   `scan_node.py --node <ID>` verification command in `implementation.graph.v5.yaml`
   still explicitly binds `--graph` to this package's own graph file (now
   `implementation.graph.v5.yaml`), and `tools/validate_plan_v2.py` still rejects an
   omitted binding.
3. **PKGV2-T02 — Node mode is a genuine narrowing.** Unchanged from rc3: confirm
   `controller/scan_node.py`'s node mode still filters the parent module's unmodified
   whole-tree scan results rather than reimplementing scan logic.
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.** Unchanged from rc3:
   confirm `implementation.graph.v5.yaml`'s N20/N30 write-set and read-only-input
   split, and `N30_preflight_egress.prompt.v5.md`'s read-only consumption language.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.**
   Unchanged from rc3.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** Unchanged from rc3, now against
   `implementation.graph.v5.yaml`.
7. **PKGV2-T06 — result/evidence versioning never reuses v1 paths.** Unchanged from
   rc3.
8. **PKGV2-T07 — source_spec binding.** Unchanged from rc3: `implementation.graph.v5.yaml`'s
   `source_spec` still names the QA-passed spec v4 at its exact digest, enforced by
   `tools/validate_plan_v2.py`.
9. **PKGV2-T08 — no write-set overlap.** Unchanged from rc3. You may run
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   against the live repository (read-only) and confirm `valid: true`.
10. **PKGV2-T09 — no implementation performed; no production edit.** `git status`
    (read-only) shows changes confined to
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/` (prompts,
    `implementation.graph.v5.yaml`, the moved `deprecated/implementation.graph.v4.yaml`,
    `schemas/`, `contracts/`, `tests/test_execution_package_v2.py`,
    `tools/validate_plan_v2.py`, `tools/validate_result_v2.py`,
    `controller/scan_node.py`, and `release_candidate/`) — never `runtime/`, `policy/`,
    `schemas/routes.schema.v1.json`, or `schemas/model_registry.schema.v1.json`.
11. **PKGV2-T10 — automated proof, not narrative.** Confirm
    `tests/test_execution_package_v2.py` remains a real, passing, automated suite
    proving PKGV2-T01–T09. You may run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    against the live repository (read-only) and confirm it passes — this runs the live
    originals the bundle text was copied from, proven byte-identical in
    `manifest.v1.json` beside the bundle.
12. **PKGV2-T11 — fresh-prompt graph-reference consistency, exact resolution, both
    flag spellings.** Confirm every graph-path reference in
    `N00_spec_approval_gate.prompt.v5.md`, `N20_provider_transport.prompt.v5.md`, and
    `N30_preflight_egress.prompt.v5.md` resolves to `implementation.graph.v5.yaml`,
    never a missing, stale, or wrong-prefixed filename — including that neither v5
    prompt still names `implementation.graph.v4.yaml` in an operative `--graph`
    command (a legitimate historical mention explaining the rename, e.g. "this v5
    prompt corrects v4, whose own `--graph` values named
    `implementation.graph.v4.yaml`", is not itself a binding reference and is not a
    defect).
13. **PKGV2-T12 — schema v2 const-locks the right package's own artifacts, not the
    parent's.** In the bundle's `schemas/spec_approval.schema.v2.json` section,
    confirm `properties.approved_spec.const` equals
    `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`
    (this package's actually approved spec, not the parent v1 package's
    `spec.v2.md`), and `properties.approved_graph.const` equals
    `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v5.yaml`
    (this package's own active graph). Confirm every digest field
    (`approved_spec_sha256`, `spec_qa_verification_sha256`,
    `approved_rc_manifest_sha256`, `execution_package_qa_verification_sha256`,
    `approved_graph_sha256`) is a `pattern`-typed 64-hex-character string, never a
    schema-level `const` — a digest cannot be known at schema-authoring time for a
    field whose value depends on the exact bytes of a specific approval instance, and
    JSON Schema cannot compute or verify a file hash regardless.
14. **PKGV2-T13 — the RC-manifest field is deliberately not const-locked, and the
    graph field deliberately is; the reasoning for the asymmetry is sound.** In the
    bundle's `schemas/spec_approval.schema.v2.json` section, confirm
    `approved_rc_manifest` is a `pattern` (matching any
    `release_candidate/rc<N>/manifest.v1.json`, not const-locked to `rc3`), with an
    explicit `$comment` reasoning that a future re-approval landing on a later RC
    generation must be expressible without a new schema version. Confirm
    `approved_graph`, by contrast, IS const-locked (like `approved_spec`), with an
    explicit `$comment` reasoning that the active graph is a governing identity
    document this schema exists to bind precisely, not a floating review-lineage
    pointer — and that a future graph version needing fresh approval should get its
    own new schema version, exactly as this schema itself exists because the parent's
    v1 schema pointed at the wrong package's spec. Judge whether this asymmetry is a
    genuine, defensible design choice (not an inconsistency) on its own stated terms.
15. **PKGV2-T14 — contract v2 carries forward the exact already-approved decision;
    it does not reinvent one.** In the bundle's `contracts/spec_approval.v2.yaml`
    section, confirm all five digest fields plus `approved_at` match the values
    already recorded in the live, unmodified `contracts/spec_approval.v1.yaml`'s
    `approval_statement` (`approved_spec_sha256`
    `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`,
    `spec_qa_verification_sha256`
    `899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631`,
    `approved_rc_manifest_sha256`
    `0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d`,
    `execution_package_qa_verification_sha256`
    `202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217`,
    `approved_at` `2026-08-13T20:57:25Z`) — except `approved_graph_sha256`, which
    legitimately differs from v1's bound graph digest because it names
    `implementation.graph.v5.yaml`, the gate-lineage rename this very correction
    performs; confirm the contract's own prose explains this exception rather than
    silently diverging. Confirm `model_assignments` structurally encodes exactly
    USER_DECISION_REQUIRED-01's already-resolved decision (M01/M06/M08 =
    claude-sonnet-5/xhigh; M02/M03/M04 = claude-sonnet-5/high; M05/M07 =
    gpt-5.6-sol/xhigh), matching `spec_approval.v1.yaml`'s prose exactly.
16. **PKGV2-T15 — the validator performs a real digest recompute, not a schema-shape
    check alone.** In the bundle's `tools/validate_plan_v2.py` section, confirm
    `validate_spec_approval_contract()` reads live file bytes and recomputes SHA-256
    for all five bound digests (the specification, its QA-verification record, the
    bound RC manifest, that RC's own QA-verification record, and the bound graph),
    comparing each against the contract's recorded value, and raises on any mismatch
    — not merely validating the contract's shape against the schema (`jsonschema`
    cannot read or hash a file, so a schema-only check would accept a well-formed but
    wrong digest). Confirm this function is actually wired into `main()`, not defined
    and never called.
17. **PKGV2-T16 — automated mutation proof for the schema v2 / contract v2 chain.**
    In the bundle's `tests/test_execution_package_v2.py` section, confirm dedicated
    tests: (a) prove `implementation.graph.v5.yaml`'s `rules.frozen_before_entry`
    includes `schemas/spec_approval.schema.v2.json` and excludes the parent's
    `spec_approval.schema.v1.json`; (b) prove `contracts/spec_approval.v2.yaml`
    validates against `schemas/spec_approval.schema.v2.json`; (c) prove each of the
    five bound digests recomputes against live bytes; (d) prove a copy of the
    contract with one bound digest changed to a wrong-but-well-formed value is
    rejected by the real validator function (not merely documented as wrong); (e)
    prove a copy with `approved_spec`, `approved_graph`, or a `model_assignments`
    entry changed to a wrong value is rejected; (f) prove an unmutated copy still
    passes (a positive control, proving the rejections above are catching a real
    mutation rather than the check always failing); (g) prove
    `spec_approval.schema.v1.json` (the parent's) is byte-unchanged by hash
    comparison.
18. **PKGV2-T17 — N20/N30 prompt v5 are honest mechanical renames, not silent scope
    changes.** In the bundle's `N20_provider_transport.prompt.v5.md` and
    `N30_preflight_egress.prompt.v5.md` sections, confirm every TEST step, write-set
    claim, and substantive instruction is otherwise identical to their respective
    `*.prompt.v4.md` predecessors (available for direct comparison in the live
    repository, read-only) — only the literal `--graph` value(s) changed from
    `implementation.graph.v4.yaml` to `implementation.graph.v5.yaml`, plus each
    file's own explanatory header paragraph describing the rename.
19. **PKGV2-T18 — deprecated graph v4 is byte-identical to the originally approved
    graph (the direct RC4-QA-001 fix).** Confirm `manifest.v1.json` itself contains a
    `deprecated/implementation.graph.v4.yaml` entry (rc4's own manifest omitted this
    entry entirely, which is exactly what `RC4-QA-001` found), and that its recorded
    SHA-256 equals `0d5b5af8b0c60847e3b52ac93c4c10328f48a1404130a6b785485bcbbae3d571`
    — the exact digest the user approved in `contracts/spec_approval.v1.yaml`'s
    `approval_statement`. This file is supplied as `--ground` material (genuinely
    static historical content, not logic under review); confirm the grounded copy's
    hash matches the manifest entry and the live `deprecated/` file — proving the
    move to `deprecated/` did not alter a single byte of the artifact the user
    actually approved.

## Falsification targets

- `schemas/spec_approval.schema.v2.json`'s `model_assignments` sub-schema const-locks
  each of the eight job IDs' `model`/`effort` pair individually; confirm it is not
  merely an open `enum` that would accept any combination of already-seen values
  (e.g. `M01` bound to `claude-sonnet-5`/`high` instead of its actually-approved
  `xhigh`) as still valid.
- `validate_spec_approval_contract()`'s digest recompute derives the spec's
  QA-verification path and the RC's own QA-verification path from the contract's
  *other* bound paths (`Path(contract["approved_spec"]).parent / "QA" /
  "verification.json"` and `rc_manifest_path.parent / "QA" / "verification.json"`),
  not from independently hardcoded constants — confirm this derivation cannot be
  satisfied by a mutated `approved_rc_manifest` pointing at a directory containing an
  attacker-substituted `QA/verification.json` that was never independently reviewed
  (i.e., confirm the RC-manifest's own digest is still independently checked against
  the manifest file itself, so the directory identity cannot be spoofed without also
  failing that check).
- `implementation.graph.v5.yaml`'s header claims no node, write set, edge, or
  verification *logic* changed in substance from v4 beyond the `--graph` self-rename
  and one added `frozen_before_entry` entry — confirm this against the bundle text
  directly (compare N10, N40–N90's sections) rather than trusting the header's own
  prose.
- The mutation tests for `approved_spec`/`approved_graph`/`model_assignments`
  (PKGV2-T16e) expect `jsonschema.ValidationError` specifically (shape/const
  failures), while the digest mutation tests (PKGV2-T16d) expect
  `validate_plan_v2.ValidationError` (a validator-level integrity failure) — confirm
  the test suite's exception-type expectations are actually correct for each case
  rather than accidentally passing because both exception types happen to be caught
  by an overly broad `except`.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
nineteen numbered criteria above (a stated criterion fails on a realistic reading of
the bundle, not merely a stylistic quibble). Anything you notice that does not defeat
a numbered criterion belongs in observations, not findings.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc5/deprecated/implementation.graph.v4.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc5/manifest.v1.json

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
This is RC5, fixing RC4-QA-001 (rc4's manifest.v1.json omitted a deprecated/implementation.graph.v4.yaml entry). Confirm manifest.v1.json now binds that file's SHA-256 correctly and it matches the grounded copy. Every other reviewed file is byte-identical to rc4's own (already-reviewed) copies -- confirm via the manifest's SHA-256 entries, not a full re-derivation of every prior finding.

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