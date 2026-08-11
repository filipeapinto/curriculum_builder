# N12_EVIDENCE_ARTIFACTS result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N12_evidence_artifacts.prompt.v1.md (c08f571402a5e601038a41dbb27cde3b443b45fafaa1558f29f3ff33c8512210)
generation: 2

## Inputs

- `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` (c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5) — sole predecessor, `depends_on: [N00_BASELINE_FREEZE]`
- `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` (063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0) — binding hashing/canonical-JSON convention
- `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` (7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7) — file names and package layout
- `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` (d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad) — this record's structure
- `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` (c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2)
- `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` (edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b) — rows 11.1-11.2, 15, and the dual-persistence adversarial row assign this node its scope
- `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` (896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af)
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` (44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6) — sections 11.2 (two persistence layers), 13.1 item 13 (append-only integrity through the acceptance high-water mark), 14 (terminal evidence), 15 (filesystem/artifact layout)
- `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` (96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8) — this node's `writes` set

## Outputs

- `runtime/langgraph_factory/artifacts.py` (dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf)
- `runtime/langgraph_factory/evidence.py` (95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199)
- `tests/runtime/test_plan26_evidence.py` (391dc9c9a40889974951b59e2fdcc342121bd2eae7e8474ed63390f19813db7c)
- `plans/26_langgraph_curriculum_factory/results/N12_EVIDENCE_ARTIFACTS.result.v1.md` (this file; not self-hashed per [[result_record_schema.v1]])

Out-of-writes-set side effect, disclosed: `runtime/langgraph_factory/__init__.py`
(c314b9c501bc6fe4dd0da84555ec3343e5c58ac30ee9fcfd1f188001376a6c20 at the time of
this record) is owned by N11 per [[shared_names_and_paths.v1]]. It did not exist
when this node started and the package is unimportable without it. It was created
with an exclusive-create (`open(path, "x")`) containing only a one-line module
docstring, so no N11 content could be clobbered; N11 may overwrite it freely and
this node depends on nothing in it.

## Commands

- `python3 -m pytest tests/runtime/test_plan26_evidence.py -q` — exit 0 — `10 passed, 13 subtests passed in 0.12s` (output under 4 KiB, inlined per [[digest_algorithm.v1]])
- `python3 -m pytest -q` — exit 0 — `204 passed, 2 skipped, 137 subtests passed in 101.58s`
- `python3 -m pytest -q -rs` — exit 0 — `265 passed, 2 skipped, 282 subtests passed in 103.14s`; the two skips are `tests/runtime/test_plan26_api_contract.py:28` (`No module named 'langgraph'`) and `tests/runtime/test_plan26_lock_drift.py:220` (pinned generator absent), both owned by N10, neither this node's file. Counts rose between the two full runs because sibling nodes N10/N11/N13 landed tests in the same working tree during execution; no pre-existing test changed status and the N00 baseline of 175 passing tests remains fully contained in both runs.
- `shasum -a 256 <path>` for every hashed path in this record — exit 0 each

## Artifact protocol

The output-root layout is spec section 15; every path below is store-relative
and resolved through one guard.

**Containment.** `resolve_within(root, relative)` rejects an absolute path, an
empty path, any `.`/`..`/NUL/separator component, and any component in the chain
that is a symlink, then requires `os.path.realpath(target)` to equal the joined
target and to be relative to `root.resolve(strict=True)`. Every read and write
in both modules goes through it; there is no unguarded path constructor.

**Admission.** All bytes are written by `stage()` then `commit()`.
`stage()` writes into `<root>/.staging/` with `mkstemp`, `flush`, `fsync`; it is
on the same filesystem as every final path, so `commit()` is a single
`os.replace()` followed by an `fsync` of the destination directory. No partial
file is ever visible at a final path. `put_bytes()` is the guarded composition of
the two and unlinks its staged file if the commit raises.

**Crash recovery.** `recover_staging()` is the startup check: it moves every
orphaned `.staging/` entry to `<root>/.staging_orphans/<content_hash>-<name>`
rather than deleting it (forensic bytes preserved) and returns the recovered
entries. Because the rename is the only visibility transition, the store after
recovery is either the old valid state or one complete new artifact.

**Content addressing and versions.** `admit_version(stream, data=..., version=...,
parent_hash=..., idempotency_key=...)` computes `content_hash =
sha256(raw bytes)` — there is no parameter by which a caller supplies a hash.
Bytes land at `<base>/versions/<channel>/blobs/<content_hash>`; the version
record at `<base>/versions/<channel>/records/<version:06d>.json` holds
`{"record": <body>, "record_hash": canonical_digest(body)}` using the one
canonical-JSON rule from [[digest_algorithm.v1]]
(`sort_keys=True, ensure_ascii=False, separators=(",", ":")`, plus
`allow_nan=False` to fail closed on non-finite floats). Version 1 must declare
`parent_hash=None`; version N>1 must declare the content hash of the admitted
version N-1, so chains are immutable parent/child and never fork in place.

**Idempotency.** `<base>/versions/<channel>/keys/<sha256(key)>.json` binds an
idempotency key to a version and record hash. Re-admitting byte-identical
content under the same key returns the existing record with no new file.
Admitting different content under a used key, or any second admission of an
existing version number, raises `ArtifactConflict` before any byte is staged.

**Heads.** `advance_head()` reads the version record from disk (the filesystem,
not an in-memory reducer, is the authority), then admits the advance only if the
current head is absent and the record is version 1 with `parent_hash=None`, or
the record is `current.version + 1` with `parent_hash == current.content_hash`.
The head pointer at `<base>/heads/<channel>.json` is the one path written with
`overwrite=True`, and it is replaced atomically.

**Acceptance.** `accept(stream, receipt_hash=..., files=...)` copies bytes (never
hard-links; the accepted inode differs from the version blob and `st_nlink == 1`)
into `<base>/accepted/<receipt_hash>/`, then chmods files to `0o444` and
directories to `0o555`. `_assert_admissible()` raises `AcceptedImmutable` before
any staging whenever the target lies under an existing `accepted/<hash>/`
directory, including on the `overwrite=True` path, so accepted bytes have no
write path at all. Re-accepting a byte-identical file set under the same receipt
hash is an idempotent no-op; any difference in bytes or file set raises.

**Evidence.** `EvidenceStore` owns the six append-only logs
(`evidence/events.jsonl activations.jsonl routes.jsonl executions.jsonl
checkpoints.jsonl index.jsonl`). Each line is
`{"schema","ordinal","prev_hash","payload","record_hash"}` where `record_hash =
canonical_digest` of the record minus `record_hash`, ordinals are monotonic from
1, and `prev_hash` of ordinal 1 is 64 zeros. Appends take an exclusive `flock`,
re-audit the whole chain before writing, `fsync`, and refuse to append to a
broken chain (`EvidenceCorrupt`) rather than self-healing. Callers may not supply
`schema`/`ordinal`/`prev_hash`/`record_hash`; per-log required fields
(`run_id`/`episode_id` everywhere, plus activation/route/execution/checkpoint/
index specifics from spec section 11.2) are enforced before the write.

**Audit and high-water mark.** `audit_log_file()` recomputes the chain from raw
bytes and returns `PASS`/`FAIL`, `record_count`, `high_water_mark` (the last
verified ordinal, which is what spec 13.1 item 13 requires acceptance to bind
against) and `broken_ordinal` (the 1-based position at which verification first
fails). `EvidenceStore.write_audit_report()` writes a content-addressed report to
`evidence/log_audits/audit.<sha256>.json`, which is naturally append-only and
idempotent.

## Tests

All in `tests/runtime/test_plan26_evidence.py`; command
`python3 -m pytest tests/runtime/test_plan26_evidence.py -q`, 10 tests and 13
subtests, all passing.

1. **Every admitted artifact is within the correct root and hash-addressed** —
   PASS. `test_admitted_artifact_is_inside_root_and_hash_addressed` asserts the
   blob resolves relative to the root, that its filename equals
   `hashlib.sha256(data).hexdigest()`, that the on-disk digest equals the record
   hash, that the store-relative path is exactly
   `units/U01/versions/domain/blobs/<content_hash>`, and that
   `verify_artifact()` recomputes true.
   `test_evidence_paths_are_contained_and_reject_unknown_logs` asserts all six
   JSONL logs resolve under `<root>/evidence/`.
2. **In-place parent/accepted mutation and symlink/path escape fail before
   write** — PASS.
   `test_mutation_and_path_escape_fail_before_any_byte_is_written` asserts, for
   every case, that the target file is absent or unchanged, not merely that an
   exception was raised: overwrite of an accepted receipt (both with and without
   `overwrite=True`) and a new file inside a sealed receipt directory raise
   `AcceptedImmutable` while the accepted bytes stay `{"ok":true}` and
   `extra.json` never appears; re-`accept()` with different bytes raises;
   re-admitting version 1 with different bytes raises `ArtifactConflict` and the
   version-1 content hash is unchanged; admitting version 2 with a wrong parent
   raises and `records/000002.json` never exists; `../escape.txt`, an absolute
   path outside the root, a directory symlink (`evil/ -> outside/`), and a
   file symlink (`evil_file.json -> outside/leaf.txt`) each raise `PathEscape`
   with the escape target asserted non-existent. The same test asserts the
   accepted file is write-protected, has `st_nlink == 1`, and has a different
   inode from the version blob.
   `test_head_advances_only_to_a_declared_child_of_the_current_head` covers
   storage-side head enforcement: skipping to version 2 with no head, jumping
   from head 1 to version 3, and a forged record whose declared parent is not
   the current head all raise `HeadAdvanceError` and leave the head unmoved.
3. **Equal replay is idempotent; conflicting duplicate admission fails** — PASS.
   `test_equal_replay_is_idempotent_and_conflicting_duplicate_fails` asserts the
   replayed record equals the first, that `records/`, `blobs/`, and `keys/` each
   still hold exactly one entry, and that both a same-key/different-bytes and a
   different-key/same-version admission raise `ArtifactConflict` without adding
   a record or blob.
4. **Crash before/after staging/admission leaves either old valid state or one
   complete new artifact** — PASS.
   `test_crash_between_staging_and_rename_leaves_no_partial_artifact` stages
   bytes, performs no rename (the simulated kill point), constructs a fresh
   `ArtifactStore` over the same root, and runs `recover_staging()`. It asserts
   the final content-addressed path never appeared, the staged file is gone from
   `.staging/`, the head and the previously admitted artifact still verify, the
   orphaned bytes are byte-identical in `.staging_orphans/`, and recovery is
   idempotent. It then completes a stage-plus-commit and asserts exactly one
   complete new artifact with the correct digest.
5. **Event/index chains detect deletion, insertion, reorder, or byte change** —
   PASS. `test_audit_detects_deletion_insertion_reorder_and_byte_change` builds
   a five-record chain and, as five subtests, deletes record 3, swaps records 3
   and 4, inserts a duplicate at position 3, flips `D08` to `D09` inside record
   3, and truncates record 5. Each asserts `status == "FAIL"`,
   `broken_ordinal` exactly 3 (3, 3, 3, 3) and 5 respectively,
   `high_water_mark == broken_ordinal - 1`, and that `append()` raises
   `EvidenceCorrupt` rather than extending a broken chain. Restoring the
   pristine bytes returns `PASS` and the next append is ordinal 6.
   `test_chain_is_ordinal_linked_and_audits_clean` asserts the untouched chain is
   `PASS` with contiguous ordinals, genesis `prev_hash`, every `prev_hash`
   equal to its predecessor's `record_hash`, and an idempotent
   content-addressed audit report.
6. **Product evidence cannot be fabricated from checkpoint or fake-test
   records** — PASS.
   `test_product_evidence_cannot_be_fabricated_from_checkpoint_or_fixture`
   asserts by signature introspection that `admit_version`, `accept`,
   `verify_artifact`, and `EvidenceLog.append` expose no
   `content_hash`/`record_hash`/`ordinal`/`prev_hash`/`checkpoint`/
   `checkpoint_tuple`/`state_snapshot`/`trust`/`trusted`/`skip_verify`/`fixture`
   parameter — there is no trust-this-checkpoint or trust-this-fixture shortcut
   into product evidence. It then asserts that forging any of the four chain
   fields in a payload raises `EvidenceError` with the high-water mark
   unchanged; that a checkpoint record claiming 500 activations and an
   unadmitted artifact hash advances only `checkpoints.jsonl` and leaves the
   activation chain at ordinal 1; that a checkpoint record missing required
   correlation fields is rejected; that `verify_artifact()` on a fabricated
   `VersionRecord` returns False and no version record exists; and that swapping
   the bytes under a genuinely admitted record makes `verify_artifact()` return
   False, proving verification recomputes from bytes rather than trusting the
   record.
   `test_canonical_serialization_rejects_non_finite_numbers` additionally proves
   the [[digest_algorithm.v1]] fail-closed rule: NaN/Infinity payloads raise and
   write no record.

## Findings

1. `runtime/langgraph_factory/__init__.py` was created by this node although it
   belongs to N11's write set. Owner: `state_or_reducer` -> N11_STATE_REDUCERS.
   Evidence key: the Outputs section disclosure above. Fingerprint:
   `n12-created-n11-owned-package-init`. Non-blocking: exclusive-create only, a
   one-line docstring, no dependency from this node's code. N11 may overwrite.
2. `evidence.py` imports `canonical_json_bytes`, `canonical_digest`,
   `file_digest`, `resolve_within`, and `ArtifactStore` from `artifacts.py` so
   that exactly one canonical-JSON and one path-containment implementation
   exists in the package. Owner: N12. Evidence key: the Artifact protocol
   section. Fingerprint: `n12-single-digest-and-path-guard-implementation`.
   Non-blocking: recorded so later nodes import these primitives rather than
   re-deriving a second convention, which [[digest_algorithm.v1]] forbids.

No blocking finding is open.

## Invalidated descendants

None (first-pass PASSED, no rework).

## Hashes

```
96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8  plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml
c08f571402a5e601038a41dbb27cde3b443b45fafaa1558f29f3ff33c8512210  plans/26_langgraph_curriculum_factory/prompts/N12_evidence_artifacts.prompt.v1.md
44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6  plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md
896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af  plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md
063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0  plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md
c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2  plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md
d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad  plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md
7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7  plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md
edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b  plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md
c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5  plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md
dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf  runtime/langgraph_factory/artifacts.py
95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199  runtime/langgraph_factory/evidence.py
c314b9c501bc6fe4dd0da84555ec3343e5c58ac30ee9fcfd1f188001376a6c20  runtime/langgraph_factory/__init__.py
391dc9c9a40889974951b59e2fdcc342121bd2eae7e8474ed63390f19813db7c  tests/runtime/test_plan26_evidence.py
```
