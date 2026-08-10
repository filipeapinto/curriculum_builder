# Gate Rerun Flakiness (Phases 4-5) — Implementation Plan v1

*Revised in place after focused QA round 1 (`qa/plan_qa.v1.md`, CHANGES REQUIRED —
3 Critical, 4 High) and round 2 (`qa/plan_qa.v2.md`, CHANGES REQUIRED — 1 Critical,
2 High). Round-1 findings 1-7 are addressed in Phases A, B, C, D and E; round-2
findings R2-1 (retry mechanism neutrality), R2-2 (re-raise blast radius through the
root gate) and R2-3 (incomplete silent-swallow census) are addressed in Phases B, C
and F. The revision notes in each phase name the finding each change answers.*

## Status and objective

Planning only; no implementation is authorized by this document's creation.

Gate verdicts produced by `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5`
change between reruns with no intervening change to gate code. This plan makes a
gate verdict a function of **committed repository state alone**, so that every
remaining `FAIL` is a real defect. It does that in four ordered movements: build a
read-only rerun-differ that measures flakiness before anything is changed (Phase A),
fix the three confirmed causes the differ must then show are gone (Phases B-D), remove
the concurrency that produces them (Phase E), and re-measure with the same instrument
(Phase F).

The causes are not hypothesised. They were found in `tests/results/`, which holds 274+
recorded runs, and each is cited with file:line and with the result records that show
the flip.

**Boundary — what this plan does not do.** It does not change what any gate
*checks*, does not relax any acceptance criterion, and does not delete or rewrite a
gate to make it stop failing. It does not reduce the set of files any detector
currently scans on committed content. It does not touch `runtime/`, `curricula/`,
`meta_prompt/`, or `policy/` except where a file must be added to `.gitignore` or
staged. It does not prune `tests/results/` (see "Confirmed non-causes"). Latent
defects that are not observed flakiness sources are recorded and deliberately left
alone (see "Explicitly out of scope").

## Architectural end state

Four invariants must be true when this plan is complete. Each is checkable.

1. **Verdict determinism.** For a fixed commit and an **unchanged worktree**, N
   sequential runs of `./tests/run_gates.sh <phase>` produce byte-identical `status`
   fields for every gate id, for phases 4 and 5, for N >= 5. "Unchanged" is the
   operative condition, not "clean": the worktree carries a large pre-existing staged
   changeset (prerequisite 0a) which must survive this plan, so `FR-P0-CLEAN` will
   report a *deterministic* `FAIL` throughout, and a deterministic `FAIL` satisfies
   this invariant. (QA observation 1.)
2. **Committed-state dependence.** No gate verdict depends on a file that is untracked
   or gitignored, **except** the two gates whose declared purpose is to observe
   uncommitted state — `FR-P0-CLEAN` (`fr_p0_structure.py:589-597`) and
   `FR-P0-HISTORY`. Generated and untracked roots are outside every production scan
   root. (QA observation 2.)
3. **Detector coverage is not reduced.** For every detector, the set of hits reported
   against *tracked* files is identical before and after this plan. Removing volatile
   state from the scan must remove only untracked and gitignored paths, never a
   committed one.
4. **Transient-failure distinguishability.** An external command or file read that
   fails from environmental I/O rather than repository content is retried within a
   declared bound; if it still fails, the resulting `FAIL` record carries an explicit
   machine-readable marker, and a read that is *silently skipped* is never allowed to
   turn an under-scanned run into a `PASS`. The four gate outcomes (`PASS`, `FAIL`,
   `SKIPPED`, `BLOCKED`) remain exactly four — harness rule 2 is not amended, and no
   fifth outcome is introduced.

## Exact work

### 0. Fail-fast prerequisites (run before any edit)

These are checks, not changes. If any fails, stop and report — do not work around it.

- **0a. Baseline worktree is recoverable.** Run `git status --porcelain` and
  `git stash list`. The repository currently has a large staged changeset (`runtime/`,
  `plans/`, `docs/` and others) and untracked files. Record the full output verbatim
  into the result file before touching anything. **Stop** if `git status` is not
  readable. Never run `git stash`, `git checkout`, `git restore`, `git clean`, or
  `git reset` against this worktree at any point in this plan — the staged work is
  not this plan's and must survive it untouched.
- **0b. The differ can run at all.** `./tests/run_gates.sh 4` must complete and write
  a result file. It may legitimately report `FAIL`s; it must not abort with `HALTED`.
  **Stop** if it HALTs, because a HALTed run produces no per-gate records and Phase A
  cannot measure anything.
- **0c. Environment capture.** Record `df -h .`, the filesystem personality, the
  Python version, and the `jsonschema` version into the result file. Established at
  planning time: the repository is on local APFS (`/dev/disk3s5`, `Macintosh HD`) at
  **93% capacity with ~16 GiB free** — the `Operation timed out` failures in
  Phase B are therefore local I/O stalls under disk and concurrency pressure, not a
  network mount. If the implementer's `df` shows a *network or synced* volume
  instead, **stop and report**: the Phase B remediation is calibrated to the local-FS
  diagnosis and must be re-derived, not stretched to cover a different cause.
- **0d. No concurrent gate run.** Confirm no other `runner.py` process is live
  (`pgrep -f "gates/runner.py"`). **Stop** if one is, because Phase A's measurement is
  invalid while a second runner is contending for `.git/index`.
- **0e. No ambient harness overrides.** Confirm `FR_PHASE`, `FR_GATE_REGISTRY`,
  `FR_RESULTS_DIR` and `FR_GATES_DIR` are unset in the environment
  (`fr_p0_structure.py:756`, `runner.py:44`, `common.py:40,315`). **Stop** if any is
  set — each silently changes verdicts and would invalidate every measurement.

### 1. Phase A — Build the rerun differ (read-only, changes no gate)

The instrument comes first. Nothing in Phases B-E may be called fixed without it.

1. Add `tests/flakiness/rerun_differ.py` (new directory; it is under `tests/`, so it
   is already outside every production scan root by `PRODUCTION_EXCLUDED_TOP_LEVEL`
   at `tests/gates/common.py:55` — verify this rather than assume it).
2. It takes `--phase <N> --runs <K>` and invokes `./tests/run_gates.sh <N>` K times
   **sequentially, never in parallel**, waiting for each to exit before starting the
   next. Parallel invocation is the very condition Phase E fixes and would corrupt
   the measurement.
3. After each run it locates that run's result file by capturing the `results:` line
   the runner prints at `tests/gates/runner.py:167` — **not** by globbing
   `tests/results/` for the newest file, which would misattribute under concurrency.
4. **Worktree-change detection.** Before and after each run, record `git rev-parse
   HEAD` and a sha256 of `git status --porcelain`. If either differs across a run, the
   run is marked `INVALID` and excluded from the stability computation, with the
   changed paths reported. This is not pedantry: the one recorded `FR-P2-DEFERRED`
   cascade (see Phase C) was caused by a **tracked policy file being read mid-edit**,
   and without this check that case is indistinguishable from harness flakiness and
   would be misattributed to whichever fix ran most recently. (QA finding 1.)
5. It emits `tests/flakiness/rerun_report.<phase>.json` containing, per gate id: the
   K verdicts in order, a `stable` boolean, the `INVALID` runs excluded, and for each
   differing run the `detail` string, whether that detail matches a transient-I/O
   signature, and the run's `class_drift` array.
6. It must not write anywhere outside `tests/flakiness/` and the result files the
   runner itself writes. It must not modify, delete, or reorder anything in
   `tests/results/`.
7. Add `tests/flakiness/*.json` to `.gitignore` with a retained `.gitkeep`, matching
   the existing pattern at `.gitignore:1-5` so that "report written" and "worktree
   clean" stay simultaneously satisfiable (harness rule 4).

### 2. Phase B — Transient external I/O is retried, marked, and never silently swallowed

**Evidence.** 88 of the 274 recorded runs contain an `Operation timed out` failure.
Counted by gate, the transient-external `FAIL`s are: `FR-P0-NOSTALE` 50,
`FR-P0-HARNESS` 21, `FR-P1-GITKEEP` 19, `FR-P0-CLEAN` 18, `FR-P0-HISTORY` 7,
`FR-P3-CAPS-OWNED` 6, `FR-P0-PARSE` 4, `FR-P2-GATEITEMS` 3, `FR-P0-PLANREF` 2,
`FR-P2-NOVALUES` 2, `FR-P0-REGISTRY` 2, and one each on `FR-P2-SEL-MAPPED`,
`FR-P3-SPLIT`, `FR-P4-ALL-VALIDATE`, `FR-P4-CHECK-MAPPING`,
`FR-P2-CONTRACT-VERSIONED`, `FR-P5-DERIVATION`, `FR-P5-RECEIPT-HASH`. (QA
observation 3 supplied the three the first draft omitted.) The cleanest pair:
`gate_results.p4.20260731T211216.489767Z.json` records `FR-P0-CLEAN PASS (worktree
clean)` and `gate_results.p4.20260731T211216.637483Z.json`, **148 ms later on the same
repository state**, records `FR-P0-CLEAN FAIL — external: git status could not be run
— fatal: .git/index: unable to map index file: Operation timed out`. When the affected
gate is `FR-P0-HARNESS` (21 occurrences), every other gate in the run goes `BLOCKED` —
which is exactly the reported symptom of a phase-4/5 gate that passed before and
fails now.

Note that `check_clean` at `tests/gates/fr_p0_structure.py:589-597` is *correct* to
refuse to read a failed `git` as clean; the defect is that the harness has no way to
tell that failure apart from a dirty worktree. Do not weaken that check.

1. In `tests/gates/common.py`, add a module-level `TRANSIENT_IO_SIGNATURES` frozenset
   containing the observed signatures: `unable to map index file`, `mmap failed`,
   `Operation timed out`, and `errno 60`. Match case-insensitively against combined
   stderr/stdout, and against `str(exc)` for raised exceptions.
2. Add a module-level `RETRYABLE_READONLY_COMMANDS` allowlist naming only the
   read-only external commands the harness runs: `git ls-files`, `git status`,
   `git log`, `git rev-list`. **Retry is never applied to a command outside this
   allowlist** — in particular not to `Evidence.run` invocations of
   `verify_domain.py` at `tests/gates/fr_p5_verifier.py:111,123`, whose idempotency
   the harness does not own.
3. **Put the retry in a module-level helper, not inside `Evidence.run`.** Add
   `_run_retryable(argv, cwd=None) -> subprocess.CompletedProcess` at module level in
   `tests/gates/common.py`. It runs the command and, when the argv is on the allowlist
   **and** the failure matches a transient signature, retries up to 2 further times
   with 250 ms and 1000 ms sleeps, returning the last `CompletedProcess` and the retry
   count. It touches no `Evidence` and records no mechanism at all.

   `Evidence.run` (`tests/gates/common.py:274-282`) then becomes: `self._record(
   "execution")` exactly as today, followed by a call to `_run_retryable`, with each
   retry appended to `self.notes`. The `_record("execution")` call stays where it is
   and stays unconditional — the retry adds nothing to the mechanism set, because
   the mechanism is recorded by the caller, once, before the helper is reached.
   Phase D depends on mechanism sets being stable.

   **Why a module-level helper rather than retry logic inside `Evidence.run`:**
   `production_files()` (Phase C step 1) must also make a retried `git` call, and it
   cannot go through `Evidence` — it takes no `Evidence` parameter at
   `common.py:75` and none of its five call sites (`fr_p1_retention.py:165`,
   `fr_p2_selector.py:234,333,550`, `selftest.py:241`) has one to pass. Threading
   `Evidence` into it would route a `git` call through `Evidence.run` and stamp
   `execution` onto four gates whose declared `claim_class` does not contain it —
   `FR-P1-SCHEMA-RETENTION` `tree+text` (`registry.py:125`),
   `FR-P2-CONTRACT-VERSIONED` `tree+text+schema+parse` (`:135`), `FR-P2-DEFERRED`
   `parse+text+mapping` (`:143`), `FR-P2-SEL-MAPPED` `tree+text+mapping` (`:167`) —
   making `_class_drift_sweep` (`runner.py:196-231`) rewrite `FR-P0-REGISTRY` `PASS`
   → `FAIL` on **every** run, a permanent failure that Phase D step 3 forbids
   unwinding. The helper is the only shape that is simultaneously retried and
   mechanism-neutral. (QA round-2 finding 1.)
4. **Retry the file reads that actually raise.** Apply the same bounded retry to all
   three read sites, not just one:
   - `common.py:291` — `_deserialize`'s `path.read_text(encoding="utf-8")`. This is
     the path `FR-P0-PARSE` takes (`check_parse` at `fr_p0_structure.py:437-446` →
     `parse_error` → `ev.parse` → `_deserialize`), and its recorded detail is
     `FR-P0-PARSE FAIL (34 files parsed) — policy/deferred.v1.yaml:
     builtins.TimeoutError: [Errno 60]`. `FR-P3-CAPS-OWNED` and `FR-P2-GATEITEMS`
     reach it too.
   - `selftest.py:117` — `json.loads(path.read_text(...))`, the origin of
     `FR-P0-HARNESS`'s 21 bare `TimeoutError`s. This is the **root** gate; each of
     those 21 blocks the entire run.
   - `common.py:121` — `read_named`, the `errors="replace"` read used by
     `production_files()` consumers.

   The first draft named only `common.py:121`, which none of the recorded failures
   reach; roughly 25 of the ~40 raised-exception transients would have gone unretried
   and unmarked. (QA finding 4.)
5. **Close the silent-swallow path, which flakes toward `PASS` — at all six sites,
   and only where a swallow can cause a false `PASS`.** The pattern
   `except (OSError, UnicodeDecodeError): continue` over a *production* scan root
   occurs at six sites, not the three the first revision named. `TimeoutError` is a
   subclass of `OSError`, so under exactly the `[Errno 60]` conditions above a file
   drops out of the scan with no note and no mechanism change. `FR-P0-NOSTALE`
   currently has 8 real hits; a transient failure on `runtime/session_bridge.py`
   alone would silence 5 of them and could turn a genuine `FAIL` into a stable,
   green, **wrong** `PASS`. (QA round-1 finding 6.)

   The full census, each verified to be reached from a real gate body:

   | Site | Detector | Consuming gate |
   | --- | --- | --- |
   | `fr_p0_structure.py:266-269` | `scan_for_stale` | `FR-P0-NOSTALE` (+ root gate, see below) |
   | `fr_p2_selector.py:239-242` | `live_v1_references` | `FR-P2-CONTRACT-VERSIONED` |
   | `fr_p2_selector.py:293-296` | `dangling_rt_references` | `FR-P2-DEFERRED` |
   | `fr_p1_retention.py:109` | `retention_gate_violations` (scan from `:165-166`) | `FR-P1-SCHEMA-RETENTION` |
   | `fr_p2_selector.py:555` | reverse `owner-without-id` scan (`:550`) | `FR-P2-SEL-MAPPED` |
   | `fr_p5_engine.py:183` | `engine_domain_violations` (`:256`, over `engine_files()`) | `FR-P5-ENGINE-GENERIC` |

   The three added sites are not vacuous: `fr_p1_retention.py:109` is **armed** —
   `schemas/deprecated/` holds 4 retired schemas and the recorded detail is
   `PASS (4 files, 4 retired)`, so a swallowed read there is a missed
   `retired-schema-still-referenced` hit; `fr_p2_selector.py:555` is a *different*
   site from `:239`/`:293` and `FR-P2-SEL-MAPPED` is on this plan's own
   transient-`FAIL` list; `fr_p5_engine.py:183` is a live phase-5 production scan.
   (QA round-2 finding 3.) `fr_p3_calibration.py:145,376` carry the same pattern but
   are reached only with single-element fixture lists and are therefore **excluded by
   evidence, not by oversight** — record that exclusion rather than silently omitting
   them.

   **Re-raise only where a swallow can cause a false `PASS`.** An unconditional
   re-raise is wrong: `scan_for_stale` also has a caller inside the **root** gate —
   `_selftest_scan_isolation`, self-test (f) at `selftest.py:238-245`, which calls
   `common.production_files()` and `structure.scan_for_stale(scanned)` with no
   `Evidence`. An exception there propagates out of `gate_harness` (whose
   `try/finally` at `selftest.py:126-135` only removes the scratch dir), is caught at
   `runner.py:130-131`, fails `FR-P0-HARNESS`, and takes **every** dependent gate to
   `BLOCKED` — turning one transient read into the exact whole-run symptom this plan
   exists to remove. It also buys nothing there: self-test (f) only asserts that no
   scanned path and no hit lies under `tests/`, so a dropped file cannot produce a
   false `PASS` of any substance. The same applies to `Fixture` detector calls
   (`fr_p0_structure.py:307` and the equivalents), where `Fixture.evaluate`
   (`common.py:353-357`) would convert the raise into a non-matching `matched_error`
   and report "rejected for a different reason than declared" — a misleading fixture
   verdict for an I/O fault. (QA round-2 finding 2.)

   So: give each of the six detectors an explicit `strict: bool = False` parameter
   (or `on_read_error`). After the bounded retry from step 4 is exhausted, a
   `strict=True` caller re-raises; a `strict=False` caller keeps today's `continue`
   **and appends a note naming the skipped path**, so even the exempt path is never
   silent. Pass `strict=True` from the production gate bodies — `check_stale`,
   `check_deferred`, the `FR-P2` production paths, `fr_p1_retention.py:166` and
   `fr_p5_engine.py:256`. Pass `strict=False` from `selftest.py:244` and from every
   `Fixture` detector invocation. State in the code comment that `scan_for_stale` has
   a root-gate caller and that self-test (f) is deliberately exempt, so a later
   editor does not "tidy" the parameter away.

   For the record, the re-raise is safe against today's tree in the ordinary case:
   all files returned by `production_files()` read cleanly through `read_named`
   (`errors="replace"` makes `UnicodeDecodeError` unreachable, and there are no
   broken symlinks or unreadable files in the scan root), so nothing that
   legitimately raises today is being correctly skipped. The defect being fixed is
   the transient case; the defect being avoided is the blast radius.
6. If retries are exhausted, the gate still `FAIL`s — but `Evidence` must expose a
   `transient_external` flag, and `_record` at `tests/gates/runner.py:178-193` must
   include it in the JSON record. **Do not add a fifth outcome and do not convert
   these to `PASS`**; invariant 4 and harness rule 2 both forbid it. The marker exists
   so Phase F's differ can prove the residue is environmental, and so a human reading
   a `FAIL` knows which kind it is.

### 3. Phase C — Generated and untracked state leaves the verdict path

**Evidence, part 1 — the production scan root reads volatile state.**
`production_files()` at `tests/gates/common.py:75-101` walks `REPO_ROOT` excluding
only `{"tests", "plans", ".git"}` (`common.py:55`). It therefore reads `outputs/`
(448 files, gitignored at `.gitignore:11-15`), `.claude/` (57 files when this plan was
first drafted, 69 at round-2 QA, 79 today — only 12 of which are tracked), and
`.pytest_cache/` (5 files) — **the clear majority of the ~660 files it returns are
run-generated or tool-generated volatile state, and the count itself moves between
runs, which is the point**. Its consumers are
`fr_p1_retention.py:165`, `fr_p2_selector.py:234,333,550`, and the root gate's
self-test at `tests/gates/selftest.py:241`. The detectors at
`fr_p2_selector.py:297-299` and `:557-559` flag any `RT-<n>` or `SEL-<name>` token not
declared in `policy/deferred.v1.yaml` / `policy/checks.v1.yaml`. Run today,
`dangling_rt_references` over `production_files()` returns **live hits that are
entirely under untracked `.claude/` agent-workspace subtrees** — 3 at first drafting
(all under `.claude/skills/plan-create-workspace/iteration-1/**`), 4 at round-2 QA
(the fourth being `RT-11` at
`.claude/skills/llm_learning_agents/references/repo_conventions.md`, also untracked).
The count is volatile by construction; what is stable, and what matters, is that
`git ls-files` returns nothing for any of them. Do not pin an expected count.

**Correction to the first draft (QA finding 1).** The first draft cited
`gate_results.p4.20260802T020605.174698Z.json` as proof that `outputs/` caused a
phase-4 cascade. That record's actual detail is `deferred-id-unresolved:RT-9 **at
policy/deferred.v1.yaml**` — a *tracked policy file caught mid-edit*, not an
`outputs/` leak, and `git log -S"RT-9" -- policy/deferred.v1.yaml` returns nothing,
confirming the token was in an uncommitted working state. No `outputs/` file has ever
produced a dangling id. That record is therefore reclassified here as a
**worktree-changed-mid-run** case, which is what Phase A step 4 exists to detect and
exclude, and it is *not* offered as justification for any exclusion. The cascade
mechanism it demonstrates is nonetheless real and unchanged: `FR-P2-DEFERRED FAIL`
takes `FR-P4-CHECK-MAPPING` and then `FR-P4-AGREEMENT` to `BLOCKED` via the dependency
edges at `tests/gates/registry.py:260,276`, and 25 seconds later all five are `PASS`
again. Across the 274 runs, `FR-P2-DEFERRED` flips 19 times and `FR-P4-AGREEMENT` 19
times. The justification for the Phase C change is invariant 2 — gitignored and
untracked state must not sit in the verdict path — plus the three live untracked hits
above, not that one record.

**Evidence, part 2 — untracked worktree state.** `FR-P0-CLEAN` flips **85 times**
across 274 runs (136 PASS / 116 FAIL). `./.DS_Store` and `./docs/.DS_Store` exist, are
untracked, and are **not** in `.gitignore`; Finder rewrites them spontaneously.
`.pytest_cache/` is likewise untracked and unignored.

**Evidence, part 3 — a load-bearing fixture is not committed.**
`tests/fixtures/time_limit_present.reject.yaml` is referenced at
`tests/gates/fr_p4_policy_schemas.py:42` and consumed by `FR-P4-AGREEMENT` at
`:363-370`, but `git ls-files` returns nothing for it. `Fixture.evaluate` at
`common.py:351-354` converts the `FileNotFoundError` into a non-matching
`matched_error`, so `gate_result` returns `ok=False`. `FR-P4-AGREEMENT` passes on this
machine and cannot pass on a fresh clone.

1. **Restrict `production_files()` to git-tracked content — do not extend
   `PRODUCTION_EXCLUDED_TOP_LEVEL`.** The first draft proposed adding `outputs`,
   `.claude` and `.pytest_cache` to that frozenset. That is wrong and QA proved it:
   `_tracked_production_files()` at `fr_p0_structure.py:283-292` applies **the same
   constant** at `:287`, so extending it also narrows `FR-P0-NOSTALE`. `.claude` holds
   12 tracked, committed files (added in HEAD commit `4e3a779`), and the exclusion
   would have silenced 3 of `FR-P0-NOSTALE`'s 8 current real hits — the
   `stale-path:assets/` findings in
   `.claude/skills/curriculum-concept-visualization/SKILL.md:62` and
   `references/layouts.md:4,46` — which are violations in committed content that the
   detector exists to report. (QA finding 2.)

   Instead, intersect the `production_files()` walk with `git ls-files`, so both scan
   roots derive from one source of truth: *tracked content, minus rule 7's
   exclusions*. This removes `outputs/` (gitignored), `.pytest_cache/` (untracked),
   `.DS_Store` (untracked), and `.claude/skills/plan-create-workspace/**` (untracked)
   while preserving every tracked `.claude/` file. `PRODUCTION_EXCLUDED_TOP_LEVEL` is
   left exactly as it is, so no named normative set is narrowed and the warning at
   `common.py:50-54` is respected rather than overridden.

   **Exact implementation — mechanism-neutral, retried, and non-silent.**
   `production_files()` calls the Phase B step 3 module-level helper **directly**:
   `_run_retryable(["git", "-c", "core.quotePath=false", "ls-files", "-z"])`, then
   splits on `\0`. It does **not** take an `Evidence`, does not call `Evidence.run`,
   and records **no mechanism** — preserving its documented contract that
   "enumerating a directory solely to select the files to scan is not `tree`"
   (`common.py:76-80`). This is the only shape that is both retried and
   mechanism-neutral; routing it through `Evidence.run` instead would stamp
   `execution` onto four gates and fail `FR-P0-REGISTRY` deterministically on every
   run (see Phase B step 3). (QA round-2 finding 1.)

   `-z` with `core.quotePath=false` is required, not cosmetic: `git ls-files`
   otherwise quotes non-ASCII paths, and a name-based intersection would silently
   drop them. There are zero such paths today (`git ls-files | grep -c '^"'` = 0), so
   this closes a latent hole before it opens. (QA round-2 observation.)

   **When `git ls-files` fails after retries, `production_files()` must raise** — it
   must **not** fall back to an untracked walk, because that would silently restore
   the volatile scan root this phase exists to remove, and it must not return a
   partial or empty list, because an empty scan root is a false `PASS` for every
   consuming detector. The raise is an `OSError` subclass carrying the git stderr, so
   it reaches `runner.py:130-131`, becomes a `FAIL` for the consuming gate, and — via
   Phase B step 6 — carries `transient_external: true`. Note the consequence at
   `selftest.py:241`: this puts a retried `git` dependency inside the root gate's
   self-test (f), which has none today. That exposure is accepted deliberately and
   bounded by the Phase B retry plus the Phase E lock (which removes the concurrent
   `.git/index` contention that produced every recorded `git` timeout); Phase F step 3
   must confirm that no `FR-P0-HARNESS` failure in the post-fix sample originates from
   this call. If Phase F shows any, **stop and report** rather than proceeding — the
   root gate must not become a new transient dependency.

   State the coupling in the code comment: `production_files()` now depends on
   `git ls-files`, which is subject to the Phase B transient failures, which is why
   Phase B is ordered before Phase C and why the call is routed through
   `_run_retryable`.
2. **Prove coverage did not shrink.** Before and after the step-1 change, run all six
   census detectors from Phase B step 5 over their scan roots and diff the hit lists.
   Every hit on a **tracked** path must be identical; only untracked and gitignored
   paths may disappear. Expected concretely: `FR-P0-NOSTALE`'s 8 hits stay 8;
   `dangling_rt_references` **drops to 0** — stated as "to 0", not "from 3 to 0",
   because its current hits all come from untracked agent workspaces under `.claude/`
   whose count changes between runs (it was 3 at first drafting and 4 at round-2 QA).
   **If any tracked-path hit disappears, stop** — invariant 3 is violated.
3. **Prove mechanism sets did not change.** Capture `mechanisms_used` for
   `FR-P1-SCHEMA-RETENTION`, `FR-P2-CONTRACT-VERSIONED`, `FR-P2-DEFERRED` and
   `FR-P2-SEL-MAPPED` from a result record before Phase B and again after Phase C.
   They must be **byte-identical**, and `_class_drift_sweep` must report
   `class_drift: []` on an otherwise-passing run. A non-empty `class_drift` here means
   the `git` call leaked an `execution` mechanism into a consumer — **stop**, because
   the next symptom is a permanent `FR-P0-REGISTRY` `FAIL` that Phase D step 3 forbids
   unwinding. (QA round-2 finding 1.)
4. **Declare the change where rule 7 is stated.** The statement of record is
   `plans/folder_refactoring/folder_refactoring.plan.v6.md:502-506`, the numbered item
   `7.` beginning "**A production scan never reads a fixture — or a detector.**" It
   enumerates the exclusion set as "`tests/**` entire ... plus `plans/**` and
   `.git/**`". The first draft pointed at `:820`/`:871` and
   `folder_refactoring.prompt.v6.md:88`, none of which enumerate the set, and
   prescribed a grep for the literal `rule 7`, which cannot find `:502-506` because
   that paragraph does not contain the string. (QA finding 5.) Update `:502-506` to
   state that the production set is drawn from tracked content, and update the comment
   at `common.py:50-54` to match. Do not grep; go to the named lines.
5. Add `.DS_Store` and `.pytest_cache/` to `.gitignore`. (With step 1 in place these
   no longer reach `production_files()`; gitignoring them is what stops them flipping
   `FR-P0-CLEAN`.) The first draft's proposed filename-based binary filter at
   `common.py:96` is **dropped as unnecessary** — the tracked-content restriction
   already removes `.DS_Store` from the scan.
6. Stage `tests/fixtures/time_limit_present.reject.yaml` with exactly
   `git add tests/fixtures/time_limit_present.reject.yaml`. **Never `git add -A` or
   `git add .`** — the worktree carries a large staged changeset that is not this
   plan's (prerequisite 0a). Do not create the commit; stage and report, leaving the
   commit to the human who owns the changeset.
7. Re-check the other phase-4/5 fixtures for the same defect: for every fixture path
   literal in `fr_p4_policy_schemas.py` and the four `fr_p5_*.py` gates, confirm
   `git ls-files` returns it. Report any other untracked one rather than assuming
   this was the only case.

### 4. Phase D — A transiently-aborted gate no longer also fails `FR-P0-REGISTRY`

**This phase was re-derived from the recorded `class_drift` field after QA finding 3
showed the first draft's three target sites accounted for at most 1 of 83 recorded
drift events.**

**Evidence.** `_class_drift_sweep` at `tests/gates/runner.py:196-231` compares each
gate's declared `claim_class` against the mechanisms it actually reported and, at
`:224-228`, rewrites `FR-P0-REGISTRY` from `PASS` to `FAIL` on any mismatch.
`FR-P0-REGISTRY` flips 51 times across 274 runs, and **61 of its 64 recorded `FAIL`s
are class-drift**. The drift events, tallied across every result file, are:

```
FR-P0-NOSTALE 50, FR-P1-GITKEEP 19, FR-P1-DOC 7, FR-P1-SCHEMA-RETENTION 2,
FR-P2-GATEITEMS 1, FR-P2-SEL-MAPPED 1, FR-P3-SPLIT 1, FR-P4-CHECK-MAPPING 1,
FR-P5-DERIVATION 1, FR-P5-RECEIPT-HASH 1
```

**53 of the 62 runs carrying non-empty `class_drift` also contain `Operation timed
out`**, and the two dominant contributors — `FR-P0-NOSTALE` (50) and `FR-P1-GITKEEP`
(19) — match Phase B's transient-I/O tallies for those gates *exactly*. The mechanism
is `runner.py:130-135`: a gate that raises mid-way is caught, converted to `FAIL`, and
its **partial** mechanism set is still written to `RUN_STATE`, which the sweep then
reads as drift. One transient timeout therefore fails two gates.

The remaining, content-caused drift is **already resolved in the current tree** and
needs no work: `FR-P1-DOC` (7 events) no longer exists — `grep -c FR-P1-DOC
tests/gates/registry.py` returns 0 — and `FR-P1-SCHEMA-RETENTION`'s declaration was
corrected to `tree+text` at `registry.py:125`, which is why the recorded drift string
`declared tree, reported text+tree` can no longer occur. The last run with any drift
is `gate_results.p5.20260802T132721.102859Z.json`; the six most recent runs all record
`class_drift: []`.

Accordingly, the first draft's Phase D is **withdrawn in full**: the three
mechanism-recording sites (`fr_p5_verifier.py:151-154`,
`fr_p4_policy_schemas.py:87-96`, `:189-191`) produced 0, 0 and 1 drift events
respectively, and the phase-4/phase-5 asymmetry claim is unsupported — two of those
three sites are `activation_phase: 4` gates that run identically at both phases.

1. In `runner.py`, mark records for gates that terminated by raising. The `except`
   at `runner.py:130-131` already knows this; carry an `aborted: true` into `_record`.
2. Have `_class_drift_sweep` skip gates whose record is `aborted` — alongside its
   existing skip of non-`PASS`/`FAIL` records at `runner.py:209`. A gate that crashed
   part-way did not *report* an incomplete mechanism set; it never finished reporting.
   It is already `FAIL`, so nothing is concealed, and the sweep stops manufacturing a
   second, unrelated failure from one transient read.
3. Do **not** weaken or delete the sweep for gates that ran to completion, and do
   **not** edit any `claim_class` in `registry.py` to match observed behaviour. The
   sweep is a real invariant; the defect is that it was being fed partial data.
4. Add a regression assertion that `FR-P0-REGISTRY`'s verdict is identical between
   `run_gates.sh 4` and `run_gates.sh 5` on one unchanged commit. Place it in the
   Phase A differ, not in a gate, so it cannot itself become a new flaky gate. This is
   retained as a *check*, not as a claim about a known asymmetry.

### 5. Phase E — Concurrent runs cannot corrupt each other

**Evidence.** `_results_path` at `tests/gates/runner.py:78-86` is a check-then-write
TOCTOU: two runners can both observe `candidate.exists()` as false and write the same
path. The harness's own self-test (e), `_selftest_no_overwrite` at
`selftest.py:222-234`, asserts exactly this property and lives inside the **root**
gate, so losing the race fails everything. Concurrent invocation is observed, not
theoretical: `gate_results.p4.20260731T211216.489767Z.json` and
`...211216.637483Z.json` are 148 ms apart, and that is the same pair whose
`.git/index` contention produced the Phase B `FR-P0-CLEAN` flip.

1. Replace the `exists()`/write sequence with an atomic create:
   `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`, incrementing the counter on
   `FileExistsError`.
2. Add an advisory run lock named **exactly `tests/results/.run.lock`**, acquired with
   `O_EXCL` at the start of `run()` and released in a `finally`. The name must **not**
   match `*.json`: `selftest.py:116-117` does `json.loads` on every `*.json` in the
   results directory and self-test (e) asserts the count is exactly 2
   (`selftest.py:228,232`), so a `.json` lockfile would raise in self-test (c) and
   miscount in self-test (e) — both inside the root gate, taking every gate to
   `BLOCKED`. The first draft said only "follow `.gitignore:1-5`", whose sole
   `tests/results/` pattern is `*.json`, and would have led an implementer straight
   into this. (QA finding 7.)
3. Add a dedicated `.gitignore` line `tests/results/.run.lock` — do not rely on
   `tests/results/*.json` — so `FR-P0-CLEAN` cannot be dirtied by the harness's own
   lock.
4. If the lock is held, exit with a distinct non-zero code and a message naming the
   holding PID (written into the lockfile). **Do not block and do not force-remove a
   held lock** — a stale lock is a condition to report, not to clear automatically.
5. Placement inside `tests/results/` is safe for the self-tests: `_run` at
   `selftest.py:101-109` always sets `FR_RESULTS_DIR` to a per-case scratch directory,
   so a child runner never contends with the parent's lock, and
   `_selftest_no_overwrite`'s two `_run` calls are sequential. Verify this rather than
   assume it.

### 6. Phase F — Re-measure with the Phase A instrument

1. Re-run the differ for phase 4 and phase 5, K = 10 each, sequentially.
2. Compare against the Phase A baseline report. Every gate must be `stable`, ignoring
   runs marked `INVALID` by Phase A step 4.
3. Confirm the directional checks separately, since a stable green result can hide
   them: (a) no `FAIL` lacks a `transient_external` marker unless it is a real
   defect; (b) **no file was silently dropped from any scan** — enumerate the six
   census sites from Phase B step 5 and show that each production (`strict=True`)
   caller re-raises and each exempt (`strict=False`) caller now appends a note naming
   the skipped path, so the claim is *checkable per site* rather than asserted for the
   run as a whole. `fr_p3_calibration.py:145,376` are recorded as excluded by evidence
   (fixture-only callers). (QA round-1 finding 6, round-2 finding 3.); (c) **no
   `FR-P0-HARNESS` failure in the sample originates from the `git ls-files` call
   introduced into `production_files()` by Phase C step 1** — if any does, stop and
   report per Phase C step 1 rather than proceeding. (QA round-2 findings 1 and 2.)
4. Any gate still unstable must be reported with its `transient_external` marker and
   its `detail`s. A residual instability that is genuinely environmental is a valid,
   honestly-reported outcome — **a plan run that cannot reach zero flips must say so
   rather than lowering K, rerunning until a clean sample appears, or excluding the
   offending gate.**

## Verification sequence

1. Prerequisites 0a-0e all pass; baseline `git status --porcelain` recorded verbatim.
   Pass = recorded, no `HALTED`, no concurrent runner, local filesystem confirmed, no
   ambient `FR_*` overrides.
2. Phase A differ runs at phases 4 and 5, K = 10, before any fix. Pass = two baseline
   reports exist and at least one gate is recorded unstable (if none is, the
   instrument is not measuring what the 274 result files show, and the plan stops).
3. Phase B: re-run the differ. Pass = the count of `FAIL`s carrying a transient-I/O
   signature is strictly lower than baseline; any that remain carry
   `transient_external: true`; a forced read failure in `scan_for_stale` called with
   `strict=True` produces a `FAIL`, not a silently smaller hit list; **and the same
   forced failure injected at `selftest.py:244` (`strict=False`) leaves
   `FR-P0-HARNESS` `PASS` with a note naming the skipped path — it must not take the
   run to `BLOCKED`**. Repeat both directions for all six census sites. (QA round-2
   findings 2 and 3.)
4. Phase C: `python3 -c` over `common.production_files()` reports zero paths under
   `outputs/`, `.pytest_cache/`, `.claude/skills/plan-create-workspace/`, and zero
   `.DS_Store` — while still returning the 12 tracked `.claude/` files. The
   before/after detector diff from Phase C step 2 shows identical tracked-path hits
   (`FR-P0-NOSTALE` still 8). The Phase C step 3 mechanism capture is byte-identical
   for `FR-P1-SCHEMA-RETENTION`, `FR-P2-CONTRACT-VERSIONED`, `FR-P2-DEFERRED` and
   `FR-P2-SEL-MAPPED`, and `class_drift` is `[]` on an otherwise-passing run.
   `FR-P0-HARNESS` passes. `git ls-files
   tests/fixtures/time_limit_present.reject.yaml` returns the path.
5. Phase D: across 10 paired runs, no record has non-empty `class_drift` attributable
   to an aborted gate, and `FR-P0-REGISTRY` has the same verdict at phase 4 and phase
   5. A gate that runs to completion with genuinely mismatched mechanisms must still
   produce drift — verify with a deliberate temporary mismatch, reverted immediately.
6. Phase E: two runners launched 100 ms apart both write distinct result files, or
   the second exits with the lock code — never a corrupted or overwritten file.
   Self-tests (c) and (e) still pass with `.run.lock` present in the results directory.
7. Phase F: differ reports every gate `stable` at K = 10 for both phases, or an
   honest residual is reported per Phase F step 4.

## Acceptance criteria

- `tests/flakiness/rerun_differ.py` exists, runs read-only against gate code, reports
  per-gate verdict stability for a given phase and K, and marks runs `INVALID` when
  the worktree changed mid-run.
- Baseline and post-fix differ reports both exist; the post-fix report shows zero
  unstable gates at phases 4 and 5 for K = 10, or names each residual with its
  `transient_external` marker and the reason it is environmental.
- `common.production_files()` returns no path under `outputs/`, `.pytest_cache/`, or
  `.claude/skills/plan-create-workspace/`, and no `.DS_Store`, **while still
  returning every tracked `.claude/` file**.
- The before/after detector diff shows an identical set of hits on tracked paths;
  `FR-P0-NOSTALE`'s 8 current hits are all still reported.
- `PRODUCTION_EXCLUDED_TOP_LEVEL` at `common.py:55` is unchanged.
- The bounded retry lives in a module-level `_run_retryable` in `common.py`;
  `production_files()` calls it directly and records **no** mechanism, and
  `Evidence.run`'s single `_record("execution")` at `common.py:275` is unchanged.
  `mechanisms_used` for `FR-P1-SCHEMA-RETENTION`, `FR-P2-CONTRACT-VERSIONED`,
  `FR-P2-DEFERRED` and `FR-P2-SEL-MAPPED` are byte-identical to their pre-plan values,
  and no run reports a `class_drift` entry caused by this plan's changes.
- `production_files()` raises rather than falling back to an untracked walk when
  `git ls-files` fails after retries, and its `git` invocation uses `-z` with
  `core.quotePath=false`.
- All six silent-swallow sites (`fr_p0_structure.py:266-269`,
  `fr_p2_selector.py:239-242`, `:293-296`, `:555`, `fr_p1_retention.py:109`,
  `fr_p5_engine.py:183`) carry the `strict` distinction: production callers re-raise
  after retries, and `selftest.py:244` plus every `Fixture` detector call remain
  exempt and note the skipped path. A forced read failure inside self-test (f) does
  **not** take the run to `BLOCKED`.
- `folder_refactoring.plan.v6.md:502-506` and `common.py:50-54` agree on how the
  production scan root is derived.
- `tests/fixtures/time_limit_present.reject.yaml` is staged for commit.
- `FR-P0-REGISTRY` returns the same verdict at phase 4 and phase 5 on one commit, and
  no `class_drift` entry originates from a gate that aborted.
- Gate outcomes remain exactly `PASS`, `FAIL`, `SKIPPED`, `BLOCKED`. No gate's
  criteria were relaxed, no `claim_class` in `registry.py` was edited to match
  observed behaviour, and no gate was deleted or disabled.
- `git status --porcelain` shows the pre-existing staged changeset from prerequisite
  0a still present and unmodified.

## Stop conditions and result

Stop on:

- **A `HALTED` run at prerequisite 0b** — there are no per-gate records to measure.
- **A concurrent runner at 0d, an ambient `FR_*` override at 0e**, or a held run lock
  in any later phase.
- **A non-local filesystem at 0c** — the Phase B diagnosis was derived for local APFS
  under disk pressure and must be re-derived, not stretched.
- **Any tracked-path detector hit disappearing at Phase C step 2** — invariant 3 is
  violated and the scan-root change is wrong.
- **Any new `class_drift` entry at Phase C step 3**, or any change to the four
  consumers' `mechanisms_used` — the `git` call has leaked an `execution` mechanism
  and the next symptom is a permanent `FR-P0-REGISTRY` `FAIL`.
- **Any `FR-P0-HARNESS` failure traceable to the `git ls-files` call in
  `production_files()`, or to a re-raise inside self-test (f)** — the root gate must
  not become a new transient dependency; report rather than proceeding.
- **Any impulse to reach green by weakening a check**: relaxing a gate's criteria,
  editing a `claim_class` to match observed mechanisms, extending
  `PRODUCTION_EXCLUDED_TOP_LEVEL`, deleting or disabling a gate, lowering K, or
  rerunning until a clean sample appears. Each is a stop condition, not a step.
- **Any operation that would touch the pre-existing staged changeset**: `git stash`,
  `git checkout`, `git restore`, `git reset`, `git clean`, `git add -A`, `git add .`,
  or `git commit`. If the work appears to require one, stop and report.
- **Discovery of a flakiness cause outside Phases B-E** — record it and report; do not
  expand this plan's scope mid-execution.

Write `plans/_eval_gf_ws/_eval_gf_ws.result.v1.md` recording: the verbatim
prerequisite 0a `git status --porcelain` baseline and the 0c/0e environment capture;
the baseline differ reports for phases 4 and 5; the before/after detector hit diff
from Phase C step 2; every path created, changed, or staged; the per-phase test
results from the execution test plan; the post-fix differ reports; and every remaining
unstable gate with its `detail` and `transient_external` marker. Append the execution
outcome to `plans/_eval_gf_ws/plans.log.md`.

## Confirmed non-causes (do not chase these)

Recorded so the implementer does not spend effort re-deriving them. QA independently
re-verified every item in this section.

- **`tests/results/` growth is not a cause.** 274+ files, and no gate reads the
  directory. `RESULTS_DIR` appears only at `common.py:40`, `runner.py:34,79,81,85`,
  and `selftest.py:106`; the self-test globs a `tempfile.mkdtemp` scratch dir, not the
  real one. It is gitignored, so it does not dirty `FR-P0-CLEAN` either. Do not prune
  it as part of this plan.
- **Filesystem enumeration order is not a cause.** Every enumeration site is sorted:
  `common.py:94,101,175,179,226,429`, `fr_p4_policy_schemas.py:63`,
  `fr_p5_verifier.py:56-62`, `fr_p5_unit.py:72-78`, `fr_p5_engine.py:81`. There is no
  `os.listdir` in `tests/`.
- **Dict/set iteration order is not a cause.** Every "first problem wins" site sorts
  first (`fr_p4_policy_schemas.py:203,210`, `fr_p5_engine.py:192,220`,
  `fr_p5_unit.py:453,487,527`), and `runner.py`'s `records` dict is populated in
  topological order. `PYTHONHASHSEED` is not reachable.
- **Randomness is not a cause.** No `random`, `uuid`, or bare `hash()` anywhere in
  `tests/gates/`. Digests are `hashlib.sha256`.
- **Runner parallelism is not a cause.** `runner.py:111` is a plain sequential loop.
  The concurrency problem in Phase E is *concurrent invocations*, not intra-run
  threading.
- **Under-declared mechanism recording in the phase-4/5 gates is not a cause.**
  `fr_p5_verifier.py:151-154` and `fr_p4_policy_schemas.py:87-96` have produced zero
  recorded drift events; `fr_p4_policy_schemas.py:189-191` has produced one. See
  Phase D.

## Explicitly out of scope (recorded, not fixed here)

- **Lexical version sort at `fr_p5_verifier.py:62`.** `sorted(entry.glob(MANIFEST_GLOB))[-1]`
  sorts lexically, so `...v10.yaml` would sort before `...v5.yaml` and
  `FR-P5-VERIFIER-REQUIRED` and `FR-P5-DOMAIN-CONSTRAINED` (via
  `fr_p5_manifest.py:43`) would keep validating v5. `common.py:534-538` does this
  correctly by parsing the integer. Latent — no curriculum has reached v10 — and a
  correctness defect, not a rerun-flakiness one. Needs its own plan before any
  curriculum reaches v10.
- **`jsonschema` first-error stability.** `common.py:303-306` reports only
  `errors[0]`, and `FR-P4-FIXTURE-BITES` pins an exact message
  (`fr_p4_policy_schemas.py:393`). Deterministic on a pinned library version, so it is
  not a rerun flake; it is an upgrade hazard.
- **`fr_p5_verifier.py:117` reads only `proc.stdout`**, so a child dying on stderr
  (e.g. missing `yaml`/`jsonschema`) is misreported as `verifier-fixture-refused`.
  `FR-P5-VERIFIER-REQUIRED` depends on `FR-P0-SCHEMA`, not `FR-P0-DEPS`
  (`registry.py:343`). A real defect, but an environment-completeness one rather than
  a rerun flake.
- **`FR_PHASE` / `FR_GATE_REGISTRY` / `FR_RESULTS_DIR` / `FR_GATES_DIR` overrides.**
  These change verdicts but are the documented self-test mechanism. Prerequisite 0e
  stops the run if any is ambiently set; hardening them further is out of scope.
