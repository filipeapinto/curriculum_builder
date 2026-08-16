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
- Round 1 (2026-08-16T12:56:52.674167+00:00): you returned FAIL with 2 finding(s) at threshold: Resolved manifest does not activate or resolve the claimed 13 prompts; P02S does not own the live structured-file edits
- Round 2 (2026-08-16T12:58:58.804979+00:00): you returned FAIL with 2 finding(s) at threshold: Resolved manifest still does not contain the required 13 activated prompts; P02S still does not own all live structured-file edits


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder_wt/refactor-curriculum-factory-repository/plans_internal/refactor_repo/checkpoints/P00A/P00A_execution_checkpoint.v3.md
Version: round 3 of at most 5
SHA-256: e53d4e9e443669b857af702ef098c32d53d078e8be78c21df4634a6ca38d9994

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# P00A Checkpoint QA Criteria

This document defines the observable, verifiable conditions for P00A checkpoint acceptance.

## Criterion 1: P00 Evidence Completeness and Currency

**Observable condition**: P00 has witnessed QA_PASSED verdict, inventory is flagged complete, baseline digests are stable and match prior values.

**How to verify**:
- Check P00 QA verdict file: `plans_internal/refactor_repo/checkpoints/P00/QA_repaired/verdict.json` contains `"state": "QA_PASSED"`
- Check P00 inventory: `provenance.complete` is `true`
- Verify inventory and baseline SHA256 digests match expected values
- Confirm no modifications to P00 evidence files

**Pass condition**: P00 verdict is QA_PASSED, inventory flagged complete, all digests stable.

---

## Criterion 2: Prompt Count and Boundaries Are Inventory-Derived

**Observable condition**: Resolved manifest exists, contains exactly 13 activated prompts (P00, P00A, P01–P10), each with inventory-derived mutation units, no gaps or overlaps.

**How to verify**:
- Check manifest file exists: `plans_internal/refactor_repo/prompts/resolved/prompt_manifest.resolved.v1.yaml`
- Load manifest and count prompts: should be 13
- Verify each prompt has a non-empty `owns` list
- Verify no mutation unit appears in multiple prompts' `owns` lists
- Confirm prompt list matches specification §8 phase structure

**Pass condition**: 13 prompts present, all have disjoint ownership, no gaps in cluster coverage.

---

## Criterion 3: Mutation Ownership Is Complete and Non-Overlapping

**Observable condition**: Every mutation unit is owned by exactly one prompt, with zero duplicates or conflicts.

**How to verify**:
- Extract all units from all prompts' `owns` lists
- Count total units and unique units: must be equal
- Check for any unit appearing in multiple `owns` lists
- Verify at least 20+ units (full decomposition scope)

**Pass condition**: Total units = unique units, zero conflicts, at least 20 units total.

---

## Criterion 4: Structured-File Transformations Have Full Codemod Controls

**Observable condition**: P02S (structured data codemod) is assigned responsibility for all TOML/JSON/YAML edits, with parser-based transformation controls defined in prompt.

**How to verify**:
- Check manifest: P02S has `toml_json_yaml_codemod_tooling` in its `owns` list
- Verify no other prompt owns structured-file transformation units
- Check P02S prompt v3 file contains parser-based codemod specification, dry-run, idempotence, fixture controls

**Pass condition**: P02S owns all structured file edits, no regex-based edits in other prompts.

---

## Criterion 5: Acceptance Criteria Traceability

**Observable condition**: All 20 specification acceptance criteria are assigned to exactly one primary prompt owner, with CLI completeness (Criterion 20) assigned to P08.

**How to verify**:
- Map each criterion 1–20 to its owning prompt (per specification §2–11)
- Check that every criterion has exactly one owner
- Verify Criterion 20 (CLI completeness post-repair) is owned by P08 (clean_room_release)
- Confirm P08 runs the full end-to-end interface test

**Pass condition**: 20 criteria mapped, each with exactly one owner, Criterion 20 owned by P08.

---

## Criterion 6: Schema Validation and Independent Gating

**Observable condition**: P00A prompt validates against schema, no validation errors, ready for Codex QA verification.

**How to verify**:
- Run schema validator: `python3 schemas/validate_instance.py --schema schemas/prompt.schema.v4.json --instance plans_internal/refactor_repo/prompts/P00A_post_inventory_decomposition.prompt.v3.yaml`
- Verify exit code is 0 (no validation errors)
- Confirm P01–P10 templates are pre-existing v3 (no modifications)

**Pass condition**: P00A validates, downstream templates unmodified, no schema errors.

---

## Criterion 7: Versioning and Authorized Paths

**Observable condition**: No source code or non-authorized files modified; only P00A planning artifacts created within authorized paths.

**How to verify**:
- Run git diff: no changes to files outside `plans_internal/refactor_repo/`
- Check untracked files: all are within authorized paths:
  - `plans_internal/refactor_repo/prompts/resolved/`
  - `plans_internal/refactor_repo/prompts/generated/`
  - `plans_internal/refactor_repo/checkpoints/P00A/`
  - `plans_internal/refactor_repo/execution/P00A/`
- Verify P00 checkpoints, inventory, baseline are byte-for-byte unchanged
- Confirm no existing artifacts overwritten with new versions

**Pass condition**: Zero unauthorized file changes, all new artifacts within authorized paths, prior artifacts unchanged.

---

## Summary

**Checkpoint acceptable when all 7 criteria pass.**

Each criterion is independently verifiable without consulting the artifact's own claims; the artifact is the evidence for checking them, not the judge.

**Blocker threshold**: Any criterion failing blocks completion.  
**Repair authority**: P00A implementation (prompts, manifest, checkpoint logic); does not extend to P01–P10 prompt modifications.  
**Non-targets**: Source code refactoring, P00 changes, CI/environment setup.

## Severity threshold: blocker

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `blocker` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: 0be0f4823e1f1ae7d738291abad764a810db3e0a73a95fd203bf45581e6603f0

Respond only in the required JSON shape.