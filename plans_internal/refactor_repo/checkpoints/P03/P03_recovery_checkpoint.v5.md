# P03 recovery checkpoint — Move Production Source and Rewrite Runtime Imports

## Status: QA_PENDING

This checkpoint is submitted for independent review. It does **not** claim completion
and does **not** claim `QA_PASSED`. Per clarified criterion 7, `QA_PASSED` can only be
established by the sanctioned gate in a separate verdict and verification receipt bound
to this checkpoint's immutable digest, and nothing in this file asserts that such a
receipt exists.

**Immutable identity of what is being reviewed.** Every deliverable in this checkpoint
carries a published sha256, and the coverage closes without a gap and without a fixpoint,
through three links:

1. **`evidence/digest_manifest.json` covers every deliverable** in the delta — every
   evidence file including all four under `evidence/ledger/`, the journal, the exceptions
   ledger, the amended prompt, criteria and resolved manifest, every superseded-session
   file, and every relocated source and test file.
2. **This report publishes the manifest's own digest**, in §2.4. The manifest therefore
   does not cover this report: a file and the file that hashes it cannot each be inside
   the other.
3. **`evidence/report_digest.txt` publishes this report's own sha256**, written after
   the report is frozen and before review begins. It carries nothing but that digest, so
   it needs no external binding of its own: tampering with it is caught by recomputing
   `sha256` of the report, not by trusting a further file. The QA gate independently
   hashes the artifact each round into its chain and rollout witness, and `verify`
   re-checks byte identity — but that is corroboration, not the publication criterion
   7.3 requires.

The only other exclusion is `checkpoints/P03/QA/`, which is gate-owned. §2.4 gives the
exact exclusion table and counts.

This scheme took three attempts and both earlier ones were caught by review, which is
recorded here rather than smoothed over. v3 used a `checkpoint_digest.json` anchor plus a
`git write-tree` tree id; round 1 found six files vouched for by nothing, because the
tree id was never actually published. v4 removed the anchor and closed the ledger gap,
but left the report's own digest to the gate's future hash; round 2 found that a digest
produced *during* review cannot satisfy a criterion requiring publication *before* it.
Both findings were correct and neither was rebutted.

---

## 1. Identification

| Field | Value |
|---|---|
| Executing prompt | `plans_internal/refactor_repo/prompts/P03_source_move.prompt.v3.yaml` |
| Prompt version | v3, with two disclosed operator-authorized amendments (§6) |
| Specification | v8 — `plans_internal/refactor_repo/refactor_repository.spec.v8.html` |
| Shared criteria | `plans_internal/refactor_repo/prompts/checkpoint_qa_criteria.v1.md` (criterion 7 clarified — §6.2) |
| Baseline commit (t0) | `ccacad34ef5a11cf7d05dea3c62612893a60cf7d` |
| Worktree | `/Users/filipepinto/Projects/curriculum_builder_wt/p03-recovery`, branch `refactor/p03-recovery` |
| Starting dirty state | **None.** The worktree was created fresh from `ccacad3` and `git status --porcelain` was empty (0 lines) before any P03 change. |
| Artifact under review | **this file**, `P03_recovery_checkpoint.v5.md` (v1–v4 superseded — §1.2) |
| Execution journal | `plans_internal/refactor_repo/execution/P03/execution_log.jsonl` — 52 records, **zero unclosed starts** |
| Exceptions ledger | `plans_internal/refactor_repo/exceptions/source_move.v1.yaml` — 10 residuals |
| Commits created | **None.** The entire delta is uncommitted. |

### 1.1 Why this is a recovery checkpoint

The first P03 QA session terminated `QA_FAILED / MAX_ITERATIONS_EXHAUSTED` after 5 of 5
rounds. An independent fresh Codex session classified that failure
`SPECIFICATION_DEFICIENT`: criterion 7 required the artifact under review to already
contain the successful result of that same review, so every revision produced a new
unverified artifact and no version could converge. That whole session — five rounds, the
terminal verdict, the postmortem, and all five superseded report versions — is preserved
unaltered at `checkpoints/P03/superseded_sessions/QA-2026-08-16-exhausted/` with a
provenance README.

During that session a provisional commit `ee8922a3d833af4205d8d33a70f9e85afddf19a5` was
made on a separate local branch. **It is preserved as evidence and is not the basis of
this checkpoint.** It has not been pushed, amended, reset, rebased, cleaned, or
continued from; it and its worktree were read only. This checkpoint's move was
**re-executed from `ccacad3`** — see §2.1.

The four non-circular findings that postmortem returned are each addressed in the
artifact rather than in argument:

| Finding | Addressed in |
|---|---|
| P03-QA-007 — ownership overlap contradicted Test 1 | §3.1, and the amended `path_ownership_model` in the resolved manifest |
| P03-QA-004 — pre-move reconciliation never recorded | §3.2 — resolved by re-execution, not by exception |
| P03-QA-005 — path ledger descriptive, not complete | §2.2 and `evidence/ledger/` |
| P03-QA-006 — deliverables lacked digest coverage | §2.4 and `evidence/digest_manifest.json` |

### 1.2 What changed across versions of this checkpoint

Round 1 of the current (fresh) QA session returned `FAIL` with two blocker findings. It
raised no circular finding, so the criterion-7 clarification did what it was meant to.
Both findings were fixed by doing work, not by rebuttal:

| Round-1 finding | What was wrong | What was done |
|---|---|---|
| `P03-QA-TEST2-NONCONTEMPORANEOUS` | v1 admitted the prompt-required pre-move inspection was reconstructed after the move, then still counted Test 2 among "Tests 1–7 PASS". | The worktree was rolled back to `ccacad3`, the inspection was performed and recorded **with `runtime/` still intact and the move not yet made**, the stop condition was evaluated at that point, and only then was the move performed. §3.2. |
| `P03-QA-TEST7-WRONG-TREE` | v1's regression evidence came from tree `db6f611…`, while the submitted checkpoint tree was `e964ab07…`; v1 called them identical. | The full suite was re-run against the checkpoint's own staged tree, materialised into a standalone repository whose tree id computes to the same content address. §3.7. |

The round-1 observation about a stale `scan_summary` in the exceptions ledger (33 files
/ 52 residuals versus the current 32 / 51) was also corrected at source, with a note
recording why the old figures existed.

Round 2 **retired both round-1 findings** after inspecting the new pre-move evidence,
journal ordering, tree comparison and failure-set evidence, and returned two new
blockers. Neither concerned the move; both concerned how the gate was driven and how
this checkpoint accounted for paths the gate itself writes:

| Round-2 finding | What was wrong | What was done |
|---|---|---|
| `P03-QA-DIGEST-BINDING-MISMATCH` | The round-2 request still published v1's digests, because `qa_gate.py` fixes `--focus` at `start` and offers no way to update it per round. The gate was therefore instructed to bind a verdict to a superseded checkpoint. | Digests are no longer carried in fixed request text at all. The manifest's digest is published in this report (§2.4) and the report's is established by the gate's own chain, so the binding is correct on every round without the request text having to change. §1.3, §2.4. |
| `P03-QA-LEDGER-NOT-CURRENT` | The gate relocated `P03_recovery_checkpoint.v1.md` into `deprecated/` *after* the freeze, so the published status and ledger no longer described the actual tree. | That relocation is now staged and appears in the ledger at its current path. `deprecated/` and `QA/` are declared gate-owned, and the single predictable pending relocation is stated explicitly. §2.4. |

### 1.3 The second QA session was retired, and why

Session `01a00c05-c34c-7c72-b3c8-ce82757de10c` ran 2 rounds of a possible 5 and was
retired deliberately. It was **not** exhausted, and it is **not** being replaced to shop
for a friendlier verdict — its round-2 verdict is what drove the fixes above, and both of
its rounds are cited here and preserved in full by the gate script's own archival.

It was retired because two of its properties made a clean, verified `QA_PASSED`
unreachable from inside it, whatever the artifact said:

1. **The focus text is immutable.** `qa_gate.py round` accepts `--artifact`,
   `--rebuttal` and `--transport`, but not `--focus`; the focus is fixed at `start` and
   replayed verbatim every round. Since it contained the v1 digests, every later round
   would keep binding the gate to a superseded checkpoint. That is exactly what
   `P03-QA-DIGEST-BINDING-MISMATCH` identified, and it cannot be fixed within the
   session.
2. **Two grounding sources necessarily change between rounds.**
   `exceptions/source_move.v1.yaml` and `evidence/digest_manifest.json` were passed as
   `--ground` at `start`. The gate hashes every grounding source each round and folds it
   into the chain, and `verify` reports `GROUNDING_CHANGED` when a source's hash differs
   from the previous round. A digest manifest that covers the artifact must change
   whenever the artifact does, so this session was guaranteed to fail `verify` on those
   two files.

The replacement session is configured to remove both causes: grounding is restricted to
sources that do not change during a session, and the focus points the reviewer at the
digest anchor file to read and re-hash rather than hard-coding values. The retirement,
its reason, and the fact that the retired session's own verdict retired the round-1
findings are recorded in the journal at `ACT-045`/`ACT-046`.

Session 3 then returned one blocker in its round 1,
`P03-QA-UNDIGESTED-DELIVERABLES`: six relied-on deliverables were excluded from digest
coverage while the `git write-tree` tree id they were said to fall back on was never
actually published anywhere. The finding was correct and is accepted, not rebutted. It is
fixed structurally in §2.4 — the anchor file is deleted, the ledger files are covered by
the manifest like everything else, and the irreducible two-file loop is closed by the
gate's own chain. Round 1 also flagged, as a non-blocking observation, that this report
claimed the manifest covered 218 deliverables when its `covered_count` was 230; that
stale count is corrected. `ACT-049`/`ACT-050` record the work.

Round 2 narrowed the same finding to the report itself: v4 published every other
deliverable's digest but deferred its own to a hash the gate would compute during review,
and criterion 7.3 requires publication before review. That is fixed in v5 by
`evidence/report_digest.txt`. `ACT-051`/`ACT-052` record it.

Two further handling facts belong here rather than in a footnote:

- The first attempt to open the replacement session used `start --force` against the
  live `QA/` directory. `--force` overwrites in place rather than archiving, and it
  truncated session 2's `session.json`, `rounds/round-01.request.md` and
  `rounds/round-01.events.jsonl`. All three were restored byte-for-byte from the git
  index, which already held them staged, and session 2 was archived to
  `superseded_sessions/QA-2026-08-16-session2-retired/` before any further attempt. No
  round response, verdict or meta file was affected. The archive's README states this.
- Opening the replacement session then returned `QA_ERROR / CODEX_TURN_FAILED`
  (`failed to load configuration`) twice on the app-server transport, with zero rounds
  completed. `QA_ERROR` is a transport state, not a verdict, and is not being treated as
  a pass. The `codex` CLI itself is healthy and answers a direct probe, so the fault is
  in the app-server sidecar; the skill documents `--transport exec` as the sanctioned
  rollback lever, and both transports produce the same tamper-evident log and rollout
  witness that `verify` checks. The replacement session runs on `exec`. `ACT-047`/
  `ACT-048` record the diagnosis.

---

## 2. Complete path ledger

### 2.1 The move was re-executed, not reconstructed

v1 rebuilt the delta by applying `git diff ccacad3 ee8922a`. That was byte-exact but it
could not make Test 2 contemporaneous. For v2 the worktree was reset to `ccacad3`
(`git status --porcelain` → 0 lines, `git write-tree` → `8ffe8e2f…` = `ccacad3`'s tree,
69 files under `runtime/`), and the move was performed forwards:

1. The pre-move inspection was run and recorded — §3.2. Only then:
2. `git mv` for all 68 relocated files plus `git rm runtime/__init__.py`, leaving
   **0 tracked files under `runtime/`** and 69 under `src/curriculum_factory/`.
3. The codemod was applied once: `files_scanned=87, files_changed=34, files_unsafe=0,
   files_parse_error=0` — **exactly the 34 files the pre-move dry-run had predicted**.
   A second application changed 0 files.
4. The 31 reviewed non-codemod transformations were applied and are enumerated at
   `evidence/move_execution/reviewed_transformations_applied.txt`.

Equivalence to the reviewed delta is then checked, not assumed:

```
$ git diff --name-only ee8922a -- src tests tools runtime plans/26_langgraph_curriculum_factory
(no output)
```

**Zero differences on every code, test, tooling and receipt path.** The full
`git diff --name-status ee8922a` across the entire tree is preserved at
`evidence/move_execution/equivalence_to_reviewed_delta.txt`; every entry in it lies
under `plans_internal/refactor_repo/{checkpoints/P03, execution/P03, exceptions,
prompts}` — this checkpoint's own documentation, its journal, and the four files
carrying the two operator-authorized amendments.

### 2.2 The literal, unabridged current state

`git status --porcelain`, complete and verbatim, is at
`evidence/ledger/git_status_porcelain_current.txt`. It is not summarised here by
directory or filename class; the literal file is the ledger.

`evidence/ledger/path_ledger_complete.json` records, for **every** path in the delta:
status, path, rename source where applicable, the blob sha256 at `HEAD`, the sha256 now,
and the exact `authorized_paths` clause authorizing it. `evidence/ledger/delta_raw_with_blob_shas.txt`
holds `git diff-index -r --find-renames HEAD` with old and new blob shas.

Authorization is computed, not asserted: each path is matched against P03's declared
clauses and the narrowest match recorded.

| | |
|---|---|
| Total paths in delta vs `ccacad3` | **250** |
| Added | 141 |
| Renamed | 68 |
| Modified | 40 |
| Deleted | 1 |
| **Unauthorized paths** | **0** |

The count exceeds the code delta because this checkpoint's own report, evidence,
digest manifest, ledger, journal and preserved superseded-session record are themselves
deliverables and are counted. Nothing is excluded from the ledger for being "just
documentation". The clause-by-clause breakdown and per-path detail, including the
rename source and its separate authorization check for each of the 68 renames, are in
the ledger JSON.

### 2.3 Pre-existing user changes

None. The worktree was created from `ccacad3` with an empty status, and the user's
original worktree at `/Users/filipepinto/Projects/curriculum_builder` was never
modified, cleaned, or committed to by this checkpoint.

### 2.4 Digest coverage

`evidence/digest_manifest.json` records the sha256 of every deliverable in the delta —
every evidence file **including all four under `evidence/ledger/`**, every
superseded-session file, both superseded checkpoint versions under `deprecated/`, the
execution journal, the exceptions ledger, the amended prompt, the amended criteria, the
amended resolved manifest, and every relocated source and test file — and separately
lists the 69 paths the delta deletes.

**`sha256(evidence/digest_manifest.json)` = `9b9ba2aa9b4448391518febbad2995fa9fe30ff7fce11be0dd2870c143d7aa94`**

That value is the one thing the manifest cannot record about itself, so this report
records it. In exchange, the manifest does not cover this report — a file and the file
that hashes it cannot each be inside the other — and this report's own sha256 is
published in `evidence/report_digest.txt`, written after this report is frozen and before
review begins. The QA gate additionally hashes the artifact each round into its chain and
Codex's rollout file, and `verify` re-checks byte identity, but that corroborates the
published digest rather than replacing it.

Exactly three paths are excluded from the manifest, and the manifest names each and why:

| Excluded | Its digest lives in |
|---|---|
| `evidence/digest_manifest.json` | this section, above |
| `P03_recovery_checkpoint.v5.md` (this report) | `evidence/report_digest.txt`, written after this report is frozen and before review begins |
| `evidence/report_digest.txt` | nowhere, and it needs nowhere: its entire content is the sha256 of this report, so its correctness is established by recomputing that hash rather than by trusting a further file. It carries no original information that could be silently altered — which is exactly what distinguished it from the `checkpoint_digest.json` anchor round 1 rejected, and from the ledger files, which do carry original information and are therefore covered by the manifest |
| `checkpoints/P03/QA/` | the gate's own hash chain and session witness — it is gate-owned, written only by the sanctioned script and only after this checkpoint is frozen, and per clarified criterion 7.4 the executing agent never writes there |

`evidence/ledger/path_ledger_complete.json` mirrors this: for those same paths it records
`sha256_now: null` together with a `sha256_now_published_in` field naming where the digest
does live, rather than leaving a blank field a reader has to interpret.

**What changed here, and why.** Round 1 of this session found six relied-on deliverables
— the four ledger files, the manifest, and a `checkpoint_digest.json` anchor — excluded
from coverage while the fallback they were said to rely on, a `git write-tree` tree id,
was published nowhere. Round 2 then found that v4's replacement still left the report's
own digest unpublished before review, deferring it to a hash the gate would compute
during review. Both findings were correct; neither was rebutted. The result is the scheme
above: the anchor is gone, the ledger files are covered by the manifest like everything
else, the manifest's digest is in this report, and the report's digest is in a sidecar
whose only content is that digest.

`deprecated/` is *not* excluded: its current contents — four superseded checkpoint
versions — are staged, listed in the ledger, and digest-covered like any other
deliverable.

Two gate-owned post-freeze mutations are stated here rather than left to be discovered,
because an earlier version of this checkpoint tripped over exactly this:

1. **A further round relocates this file.** If the gate returns findings, `round` moves
   `P03_recovery_checkpoint.v5.md` into `deprecated/`. It cannot be pre-staged without
   breaking the script's own lineage bookkeeping.
2. **Opening a replacement session would archive the current one.** `qa_gate.py start`
   moves an existing `QA/` directory aside.

Both are gate-owned, both are post-freeze by construction, and neither touches any code,
test, tooling or receipt path. The already-completed relocations —
`deprecated/P03_recovery_checkpoint.v1.md`, moved by the gate during session 2 round 2, and
`deprecated/P03_recovery_checkpoint.v2.md`, `deprecated/P03_recovery_checkpoint.v3.md`
and `deprecated/P03_recovery_checkpoint.v4.md`, moved by hand so that no superseded
version sits in the live slot at freeze time and every one of them is digest-covered at a
stable path — are staged, appear in the ledger, and are covered by the manifest.

---

## 3. Test evidence

Every command below was executed. Exit statuses and material output are literal.

### 3.1 Test 1 — Resolved manifest grants exact non-overlapping mutation ownership — **PASS**

The earlier scan compared `authorized_paths` entries only for exact string equality and
reported 3 overlaps. That was too weak: the prompt's expected result also forbids a unit
being "merely covered by a broader authorized path", which is containment, not equality.
The scan was rewritten to test exact equality **and** directory-prefix containment, in
both directions, across every prompt in the manifest. Full per-prompt declarations and
the complete matrix: `evidence/test1_ownership_overlap_scan.v2.txt`.

```
P00   OTHER_COVERS_P03  other='tools/refactor_repo/'                           p03='tools/refactor_repo/baseline.py'
P00A  OTHER_COVERS_P03  other='plans_internal/refactor_repo/prompts/resolved/' p03='.../prompt_manifest.resolved.v1.yaml'
P01   P03_COVERS_OTHER  other='src/curriculum_factory/__init__.py'             p03='src/curriculum_factory/'
P01   EXACT             other='tests/refactor_repo/test_packaging_skeleton.py'
P02   OTHER_COVERS_P03  other='tests/refactor_repo/codemod/'                   p03='.../test_rewrite_runtime_imports.py'
P04   EXACT             other='src/curriculum_factory/'
P04   OTHER_COVERS_P03  other='tests/'  × 6 P03 paths
P05   OTHER_COVERS_P03  other='tests/'  × 6 P03 paths
P09   EXACT             other='tests/runtime/'

total overlapping declarations: 19
```

**This is 19 overlaps, not 3.** The previous checkpoint under-reported them because of
the weaker scan. That is stated plainly rather than minimised.

The postmortem's instruction was to *resolve or formally amend* the ownership contract
rather than explain it inside a report. It has been formally amended: the resolved
manifest now carries an authoritative `path_ownership_model` block defining textual
ceiling versus active mutation ownership, four invariants (including that exactly one
prompt is in flight at a time, and that **borrowing a not-yet-run successor's authority
remains absolutely prohibited**), an explicit Test 1 evaluation rule, and nine
adjudication entries covering all 19 overlapping declarations.

Under that contract the result is checkable rather than rhetorical: **19 of 19
overlapping declarations are enumerated and adjudicated, 0 are unadjudicated, and 0 of
P03's mutations touch a path actively owned by another prompt.** P03's new
`checkpoint_qa_criteria.v1.md` grant is covered by no other prompt's ceiling and adds no
overlap.

Two overlaps deserve naming precisely rather than by class:

- **P04 / `src/curriculum_factory/`** is an exact overlap with an unstarted successor.
  P03 borrows nothing from it: every P03 change under that path is the mechanical
  relocation, and all 29 resource/root defects that are P04's actual subject are handed
  over untouched (§3.7).
- **P01 / `tests/refactor_repo/test_packaging_skeleton.py`**, and the P00/P02 file
  grants, are mutations inside *completed predecessors'* ceilings made under the narrow
  2026-08-16 operator grant enumerated file by file in §6.1 — not successor borrowing.

### 3.2 Test 2 — Prerequisites and pre-move source map reconcile exactly — **PASS**

This test was re-executed at its mandated time. Full record:
`evidence/premove_inspection/premove_inspection.txt`, with the four diagnostics and two
candidate lists beside it. Journal `ACT-039` opens the inspection and `ACT-040` closes
it; the move only begins at `ACT-041`.

**Proof that no move had occurred when this ran:**

```
HEAD: ccacad34ef5a11cf7d05dea3c62612893a60cf7d
$ git ls-files runtime/ | wc -l
69
$ find runtime -type f -not -path '*__pycache__*' | wc -l
69
$ find src/curriculum_factory -type f -not -path '*__pycache__*'
src/curriculum_factory/__init__.py
```

**Prerequisites:**

```
967d702 ancestor of HEAD: yes    967d702 refactor(repo): complete P01 packaging skeleton
d35aea3 ancestor of HEAD: yes    d35aea3 P02 import codemod (Codex QA_PASSED, ...)
```

**Inputs unchanged versus the P00 source map:**

```
present files: 69;  t0 recorded: 69
$ diff <t0 digests> <present digests>
(empty) -> INPUTS UNCHANGED: 69/69 byte-identical to the P00 baseline
```

**P02's live dry-run inventory, re-derived at this exact pre-move state**, reproduces
the P02 checkpoint's recorded figures exactly:

```
summary: {"files_parse_error": 0, "files_scanned": 94, "files_unsafe": 0, "files_would_change": 33}
diagnostic kinds: {'rewrite_import': 163, 'non_target_shadowed': 10}
P02 checkpoint recorded: files_scanned=94 files_would_change=33 files_unsafe=0 files_parse_error=0,
                         rewrite_import=163 non_target_shadowed=10
```

**P03's own dry-run over its authorized surface, at the same pre-move state:**

```
summary: {"files_parse_error": 0, "files_scanned": 87, "files_unsafe": 0, "files_would_change": 34}
diagnostic kinds: {'rewrite_import': 164, 'non_target_shadowed': 10}
```

**Stop-condition evaluation, made there and then, before any move** (quoted from the
recorded inspection):

```
  files_unsafe      = 0 -> zero ambiguous transformations
  files_parse_error = 0 -> every candidate parsed and classified
  decision: candidate coverage reconciles and no ambiguity exists, so the prompt stop
            condition ("stop before applying if candidate coverage does not reconcile,
            or on any ambiguous transform") does NOT fire. Proceeding to the move.
```

**Candidate reconciliation, both directions:**

```
in P03 but not in P02 (expected: exactly the operator-granted compatibility files):
    tools/refactor_repo/baseline.py
in P02 but not in P03 (expected: none):
  ^ empty
```

P03's 34 candidates are a strict superset of P02's 33, differing by exactly the one
operator-granted file. Against the current AST inventory: 87 files scanned, 34
candidates, 53 parsed and inspected with no `runtime` reference. The subsequent apply
changed exactly those 34 files (§3.4) — the prediction and the outcome agree file for
file.

The exceptions ledger entry
`premove-dryrun-reconciliation-not-recorded-contemporaneously` is now marked **RESOLVED
by re-execution**, and retains its original text so the history stays legible.

### 3.3 Test 3 — Source relocation preserves the complete production tree — **PASS**

Evidence: `evidence/test3_relocation_completeness.txt`.

```
$ git ls-files runtime/ | wc -l
0
$ find runtime -type f -not -path '*__pycache__*'
bfs: error: runtime: No such file or directory.
$ find src/curriculum_factory -type f -not -path '*__pycache__*' | wc -l
69
```

Every one of the 69 files in the recorded t0 `runtime/` digest manifest was mapped to
its expected destination and re-hashed:

```
t0 runtime/ files: 69
destinations present: 69   missing: 0
byte-identical after move: 61
content-changed (authorized import token rewrite only): 8
files in src/curriculum_factory not traceable to a t0 runtime/ file: 0
```

The 8 content-changed files are named individually in the evidence file. File modes:
`git diff --cached --raw --find-renames HEAD` shows `:100644 100644` for all moved and
modified entries, and `git ls-tree -r HEAD runtime/` shows all 69 source files were mode
`100644` — no mode changed. Subpackage boundaries and non-Python resource layout are
preserved 1:1 by construction: every destination is the source path with only the
package root renamed.

### 3.4 Test 4 — Codemod application is complete and idempotent — **PASS**

First application, during the re-executed move:

```
apply pass 1: {"files_changed": 34, "files_parse_error": 0, "files_scanned": 87, "files_unsafe": 0}
apply pass 2: {"files_changed":  0, "files_parse_error": 0, "files_scanned": 87, "files_unsafe": 0}
```

The first application matches the pre-move dry-run's 34 predicted candidates exactly;
the second is empty. A separate post-move dry-run over the same surface
(`evidence/test4_postmove_idempotency_dryrun.json`) also reports `files_would_change: 0`.

Repo-wide postcondition scan:

```
{"files_scanned": 263, "files_with_residuals": 32, "residual_count": 51}
```

Every residual is classified, not merely counted. `evidence/test4_residual_classification.txt`
maps all 51 diagnostics across all 32 files to an entry in the exceptions ledger:

```
unclassified residual files: 0
```

The classes are: frozen Plan 26/27 archival evidence scripts (out of scope, untouched),
codemod fixture `before.py`/`after.py` files that must retain old-identity text to test
the codemod itself, and the deliberately malformed-Python fixture. No silent residual
exists. The ledger's `generated_from.scan_summary` previously carried 33 files / 52
residuals from a scan taken in the provisional worktree while it held an extra untracked
fixture copy; it now carries the reproducible 32 / 51 with a note recording the
correction.

### 3.5 Test 5 — Installed imports and module origins use only `curriculum_factory` — **PASS**

Evidence: `evidence/test5_installed_import_origins.txt`. Wheel built from the content
under review and installed into a fresh venv. From repository root, from `tests/runtime`,
and from `/tmp`, all four representative modules resolve inside the installed
distribution:

```
curriculum_factory                         -> .../site-packages/curriculum_factory/__init__.py
curriculum_factory.run_curriculum          -> .../site-packages/curriculum_factory/run_curriculum.py
curriculum_factory.langgraph_factory.graph -> .../site-packages/curriculum_factory/langgraph_factory/graph.py
curriculum_factory.io                      -> .../site-packages/curriculum_factory/io.py
import runtime -> ModuleNotFoundError: No module named 'runtime'
```

No `sys.path` edits were used, nothing resolved from the checkout or the test tree, and
all four declared console scripts are installed.

### 3.6 Test 6 — CLI interface matches the P00 baseline at the mechanical boundary — **PASS**

Evidence: `evidence/test6_cli_boundary.txt`, `evidence/test6_preflight_no_mutation.txt`,
`evidence/test6_preflight_stdout.json`.

Against the P00 t0 baseline's recorded digests, with the single predeclared
normalization (prog token `curriculum_factory.run_curriculum` mapped back to
`runtime.run_curriculum`):

| t0 command | exit t0 → now | stdout sha256 |
|---|---|---|
| `-m runtime.run_curriculum --help` | 0 → 0 | differs raw; analysed below |
| `-m runtime.run_curriculum` (no args) | 2 → 2 | **exact match** |
| `-m runtime.run_curriculum --engine-root x` | 2 → 2 | **exact match** |

The `--help` raw difference is disclosed rather than normalized away. It is entirely
argparse usage-line wrapping: the new prog token is 31 characters against the old 22, so
argparse re-indents the continuation lines. The `diff` is four usage-line hunks and
nothing else. After collapsing runs of whitespace:

```
t0  collapsed sha256: 597bcd832c91b41ed88abef3e677811ed739a7193652d2cbf30c4829db696b8e
now collapsed sha256: 597bcd832c91b41ed88abef3e677811ed739a7193652d2cbf30c4829db696b8e
identical after whitespace collapse: True
option/flag set identical: True
```

No-mutation preflight, in the installed distribution:

```
$ python -m curriculum_factory.run_curriculum --engine-root . --curriculum curricula/arduino_kit \
    --output-root /tmp/p03_preflight_out --preflight
exit=0
BEFORE digest-of-digests: 62316f4f45083db76d67f4cf49b3a3b29035ee991b1caa1f9e1cf9918f6e2834
AFTER  digest-of-digests: 62316f4f45083db76d67f4cf49b3a3b29035ee991b1caa1f9e1cf9918f6e2834
NO MUTATION CONFIRMED
ls: /tmp/p03_preflight_out: No such file or directory
```

`"ready": true` with real capability probes (model CLI identity, retrieval/egress,
renderer, rasterizer, persistence, logger — all PASS). The output root is not created,
and `src/`, `curricula/`, `policy/`, `schemas/` and `meta_prompt/` are byte-identical
before and after.

Resource/root-dependent CLI cases are **not** reported as passing here; they are
delegated to P04 and appear by exact test id in §3.7.

### 3.7 Test 7 — Regression delta is confined to predeclared P04 handoff failures — **PASS**

Evidence: `t5_final_tree/`, `evidence/verification/`.

The prompt requires an installed-distribution run, and one test —
`test_baseline_compare_detects_changed_behavior` — creates a scratch worktree from
`HEAD`, so it needs `HEAD` to reflect the move. This checkpoint has created no commit.
Rather than commit early, or report the test as inconclusive, the run was made against
the checkpoint's **own staged tree**, materialised into a standalone repository:

```
$ git write-tree                                  # this checkpoint, staged
a3234a67dcafebca06656241b633c36afa11e34d
$ git -C /tmp/p03_final_repo rev-parse HEAD^{tree} # standalone repo built from it
a3234a67dcafebca06656241b633c36afa11e34d
```

Git tree ids are content addresses, so equality here is proof of byte identity, not
similarity. No ref, commit or object was created in the real repository, and the
preserved provisional commit was not touched.

```
$ /tmp/p03_venv2/bin/python -m pytest -q tests/
109 failed, 1370 passed, 2 skipped, 9 errors, 419 subtests passed in 145.40s
exit=1
```

t0, for comparison: `80 failed, 1399 passed, 2 skipped, 9 errors, 419 subtests passed`.

```
new failures vs t0:   29
fixed since t0:        0
$ diff p04_handoff_allowlist_ids.txt new_failures_ids_only.txt
(empty)  -> EXACT MATCH
```

**No test was weakened** — 0 tests moved from failing to passing, so nothing was
disabled or relaxed to clear a failure — and the 29 new failures are exactly the 29 ids
individually enumerated in `exceptions/source_move.v1.yaml` under `p04_handoff_allowlist`,
grouped by their three root causes (18 test-helper `REPO_ROOT` computed from the
installed package, 9 D07/D08/D09 engine-root resource lookup, 2 production `egress.py`
policy-file resolution). No unnamed or additional failure exists.
`test_baseline_compare_detects_changed_behavior` is absent from the failure set, which
retires the previously recorded commit-sequencing residual by direct evidence.

**Two honest qualifications, neither hidden:**

1. *The first attempt at this run was discarded.* The fresh venv initially lacked
   `libcst`, `tomli`, `tomli_w`, `PyYAML-ft`, `build` and `pyproject_hooks`, producing 2
   collection errors. The environment was pinned to be identical to the earlier run's
   (`diff` of `pip list --format=freeze` is empty) and the suite re-run. The exact
   package set is recorded at `evidence/verification/test_environment_freeze.txt`. This
   is disclosed rather than silently retried.
2. *The tested tree is not literally the final submitted tree.* It cannot be: a tree
   cannot contain the log of the test run over itself. The exact, complete difference —
   in both directions, plus content changes on paths present in both — is enumerated at
   `evidence/verification/tested_tree_vs_submitted_tree.txt`. It consists of: the files
   added after the run (this report, `t5_final_tree/`, `evidence/ledger/`,
   `evidence/digest_manifest.json`, `evidence/verification/`, `prior_runs/README.md`,
   and the gate's own `QA/` round-1 files); the relocation of `t1/`,
   `t2_post_compatibility_correction/` and `t4_recovery/` into `prior_runs/`; and content
   edits to exactly three files — `exceptions/source_move.v1.yaml`,
   `execution/P03/execution_log.jsonl` and its counter.

   Every one of those paths is under `plans_internal/refactor_repo/`, and the difference
   is proven test-inert rather than asserted:
   `evidence/verification/checkpoint_docs_are_test_inert.txt` records that
   `plans_internal/refactor_repo/checkpoints/` contains **0 `.py` files**, that
   `testpaths = ["tests"]`, and that the only reference to `plans_internal` anywhere in
   `tests/` is `tests/refactor_repo/codemod/test_rewrite_runtime_imports.py:331`, which
   reads `plans_internal/refactor_repo/inventory/20260816_074507` — a directory this
   delta does not touch at all (it appears nowhere in the path ledger).

Three superseded intermediate runs (`t1`, `t2_post_compatibility_correction`,
`t4_recovery`) are retained under `prior_runs/` with a README stating explicitly that
they are *not* this checkpoint's Test 7 evidence, and why.

### 3.8 Test 8 — Independent Codex QA accepts the P03 checkpoint — **QA_PENDING**

Not claimed, not asserted, and deliberately not evaluated by this document. This
checkpoint is the artifact submitted to that gate. The gate holds the verdict; its
result will exist only as a separate gate-generated verdict and verification receipt
bound to this checkpoint's immutable digest.

Three sessions exist. None of their verdicts is reused or reinterpreted here. The first terminated `QA_FAILED /
MAX_ITERATIONS_EXHAUSTED` and is preserved at
`superseded_sessions/QA-2026-08-16-exhausted/`. The second, `01a00c05-…`, ran two rounds
and was retired for the configuration reasons in §1.3; it is preserved at
`superseded_sessions/QA-2026-08-16-session2-retired/`. The third is the current session,
opened fresh against the clarified criteria and running on the `exec` transport; this is
its round 2, and its round 1 produced the digest-coverage fix described in §1.3 and §2.4.

---

## 4. Prerequisites, non-targets, stop conditions, rollback

**Non-targets, verified untouched.** P03 explicitly does not do resource-loading
semantics, repository-root redesign, fixture/output cleanup, schema IDs,
`pyproject.toml`, product prose, test-tree organization, or subsystem decomposition. The
path ledger contains no `pyproject.toml`, no `schemas/` entry, no `readme.md` or docs
prose, and no test-tree move — only import rewrites inside `tests/runtime/`.

**Stop conditions.** Evaluated before the first move and recorded there (§3.2), not
reconstructed afterwards. The condition did not fire; the recorded reason is quoted
above verbatim.

**No successor authority borrowed.** Formally checked in §3.1 against the amended
ownership contract: 0 mutations touch a path actively owned by another prompt. The 29
resource/root defects belonging to P04 are handed over by exact test id and left
unfixed, which is the observable form of not borrowing P04's authority.

**Rollback, actually executed — twice, and once for real.** It was first rehearsed:

```
$ git stash push --include-untracked -m p03-rollback-rehearsal
--- at rollback point ---
status lines:        0
index tree:   8ffe8e2f45fe9f1317846ab23aaca37f0bac4e47
ccacad3 tree: 8ffe8e2f45fe9f1317846ab23aaca37f0bac4e47
runtime/ files present: 69
$ git stash pop
WORKING TREE BYTE-IDENTICAL AFTER ROLLBACK REHEARSAL
```

It was then genuinely performed: to fix round-1's Test 2 finding, the entire code delta
was rolled back with `git reset --hard ccacad3 && git clean -fd`, verified back at
`ccacad3`'s tree `8ffe8e2f…` with all 69 `runtime/` files restored, and the move was
redone forwards from there. The rollback procedure is therefore not a claim in this
document; it is a step this checkpoint actually took and recovered from.

One honest detail from the rehearsal: `git stash pop` restores content but not staging,
so rename records reverted to delete+add in the index until `git add -A` was re-run; a
digest-of-digests over every file in the worktree proved nothing was lost.

---

## 5. Residuals, exceptions, and what is not claimed

The exceptions ledger holds 10 residuals. Classification of everything P03 touched or
left behind:

| Class | Count | Where |
|---|---|---|
| Codemod residuals, all classified | 51 diagnostics / 32 files | §3.4, `evidence/test4_residual_classification.txt` |
| Failures handed to P04, by exact id | 29 | §3.7, `p04_handoff_allowlist` |
| Resolved during this recovery | 2 (commit-sequencing artifact; pre-move reconciliation) | §3.7, §3.2 |
| Open recorded exceptions | **0** | — |
| Silent residuals | **0** | — |

**P03 does not claim:** that it is complete; that `QA_PASSED` has been obtained; that
resource/root-relative loading is correct under true installation (P04's 29 ids); that
frozen Plan 26/27 archival evidence scripts were reconciled (untouched, out of scope);
that any commit exists (none does); or that the tested tree is literally the final
submitted tree (§3.7 qualification 2 states exactly how they differ and why it cannot
affect a test result).

---

## 6. Operator-authorized amendments, disclosed

### 6.1 Compatibility correction (pre-existing, 2026-08-16)

Granted after QA round 2 of the superseded session found 6 non-P04 regressions P03 could
not lawfully resolve. Scope: exactly 6 files —
`tests/refactor_repo/test_packaging_skeleton.py`,
`tests/refactor_repo/codemod/test_rewrite_runtime_imports.py`,
`tools/refactor_repo/baseline.py`, and 3 Plan-26 receipt files — updated only to follow
the completed move, preserving their original behavioral assertions rather than
disabling any test. Not a grant over their parent directories. The prompt's amendment
comment and the manifest's `compatibility_correction_note` record it.

### 6.2 QA-protocol clarification (this recovery, 2026-08-16)

Granted after the independent postmortem classified the QA failure
`SPECIFICATION_DEFICIENT`. Scope: exactly one new path,
`plans_internal/refactor_repo/prompts/checkpoint_qa_criteria.v1.md`, to clarify
criterion 7 only.

```
checkpoint_qa_criteria.v1.md  sha256 bfd035a29b675df9718dc694a945ff1a4e901f2b3d8e653541a2b98b2cc48a42  (before)
                              sha256 8963b43f143290c2cf2e32c7aa97523d829657aeec9a2224b1aa3040a3c53f7e  (after)
$ diff <pre-amendment lines 1-20> <amended lines 1-20>
(empty)   # header and criteria 1-6 byte-identical
```

The pre-amendment file is preserved verbatim at
`evidence/criteria_amendment/checkpoint_qa_criteria.v1.PRE_AMENDMENT.md`, with the full
amendment diff beside it, so verdicts issued against the earlier text remain
interpretable.

Criterion 7 now states, as sub-clauses 7.1–7.6, that the submitted checkpoint must
identify itself as `QA_PENDING`; must not claim completion or `QA_PASSED`; must publish
an immutable final digest that the gate evaluates; that `QA_PASSED` is recorded only in
a separate gate-generated verdict and verification receipt; that the external verified
receipt satisfies the completion gate without modifying the reviewed checkpoint; and
that any post-verdict completion summary must reference the immutable digest and the
receipt and must not replace or mutate the reviewed artifact.

**The substance of criterion 7 is preserved, not waived.** The clarified text keeps the
original prohibitions on claiming completion with missing evidence, incomplete
collection, failed commands, or an unavailable QA transport, and adds an explicit
non-waiver paragraph: independent QA remains mandatory, a checkpoint asserting
completion before a witnessed verified receipt exists is still defective, and a missing,
unwitnessed, unverifiable, or digest-mismatched receipt still blocks completion. What
changed is only *where* the passing result lives — in the gate's receipt rather than
inside the artifact the gate is judging.

### 6.3 Ownership contract amendment

`path_ownership_model` was added to the resolved manifest as described in §3.1. It
narrows nothing and widens nothing: no prompt gained a path, and the prohibition on
borrowing successor authority is restated as an absolute invariant.

---

## 7. Journal and completion gates

| Gate | State |
|---|---|
| `require_valid_journal` | 52 records, execution-log-v2 shape |
| `require_zero_unclosed_starts` | **0 unclosed** |
| `require_all_tests_pass` | Tests 1–7 **PASS**, each with literal evidence; Test 8 `QA_PENDING` |
| `require_authorized_paths_only` | **0 unauthorized** of 250 paths |

The completion gate as a whole is therefore **not yet satisfied**, and this checkpoint
does not claim it is: Test 8 is pending the independent gate's separate receipt.

Three journal disclosures, all in the record rather than only here:

1. `ACT-019` was left unclosed by the original execution, in both the provisional commit
   and the preserved worktree. It is closed by `ACT-024`, recorded explicitly as a
   **late** closure rather than backdated, with its true result (round 3 returned
   `ROUND_OPEN`, not a pass).
2. While recording `ACT-031` a tooling slip emitted one malformed record
   (`status: completed`, `closes: null`) that violated the pairing contract. It was
   removed and replaced with a valid started/completed pair reusing the same id, within
   the same recovery step and before any commit or QA submission. `ACT-032`'s notes
   record this. No other journal line was altered, reordered, or pruned.
3. The journal is a verified strict append-only extension of the version captured in
   `ee8922a`: its first 19 records are byte-identical, sha256
   `b7d8b00aa398e4b78d430839b00f7d7c51acff7dfb74e172164f184639f0153e`.

## 8. Successor

P03 unblocks **P04 only**. P04's inbound contract is the 29 exact test ids in
`p04_handoff_allowlist`, grouped by their three root causes, plus the process obligation
recorded during this recovery: capture the pre-mutation reconciliation into the
checkpoint evidence directory *before* the first mutating action, not after.
