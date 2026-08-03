# Gate Rerun Flakiness (Phases 4-5) Plan v1 — Focused QA (Round 3)

## Verdict

**CHANGES REQUIRED — 0 Critical, 3 High.** The plan's empirical core holds up under
independent re-derivation: I re-tallied the result corpus and reproduced 88 runs
carrying `Operation timed out`, the per-gate transient tally exactly as printed, 62
runs with non-empty `class_drift` of which 53 also timed out, the drift histogram
(`FR-P0-NOSTALE` 50, `FR-P1-GITKEEP` 19, `FR-P1-DOC` 7, …), `FR-P0-CLEAN` 85 flips,
61 of 64 `FR-P0-REGISTRY` `FAIL`s class-drift-caused, and both cited 148 ms-apart
records. Every load-bearing file:line I checked is correct (`common.py:55,75-101,121,
275,291`, `runner.py:78-86,130-131,167,196-231`, `selftest.py:116-117,228,232,241,244`,
`registry.py:125,135,143,167,260,276,343`, `folder_refactoring.plan.v6.md:502-506`,
and all eight `except (OSError, UnicodeDecodeError)` sites — the census of six plus
two excluded is complete, I found no ninth). I applied the Phase C scan-root change
to a live copy of the tree: it drops `production_files()` from 671 to 110 paths,
takes `dangling_rt_references` to exactly 0, removes no tracked path, and leaves
`FR-P0-NOSTALE`'s 8 hits (3 under tracked `.claude/`) untouched — the mechanism is
sound and the round-2 remediation is correct. What blocks approval is three things
the plan gets wrong at the edges: an unimplementable note requirement at the exempt
`strict=False` call sites whose obvious implementation permanently fails
`FR-P0-REGISTRY` (verified by execution), a retry allowlist that does not match the
one argv Phase C mandates, and a declared invariant that a scan root outside
`production_files()` already violates today.

## Findings

### 1. High — the `strict=False` "note the skipped path" requirement has no note channel, and the obvious implementation permanently fails `FR-P0-REGISTRY`

**Evidence.** Phase B step 5 requires that "a `strict=False` caller keeps today's
`continue` **and appends a note naming the skipped path**, so even the exempt path is
never silent", and this is promoted to an acceptance criterion ("`selftest.py:244`
plus every `Fixture` detector call remain exempt and note the skipped path") and to
verification step 3 ("leaves `FR-P0-HARNESS` `PASS` with a note naming the skipped
path").

Every exempt call site passes no `Evidence`, so there is nothing to note into:

| Exempt site | Call |
| --- | --- |
| `tests/gates/selftest.py:244` | `structure.scan_for_stale(scanned)` — ev omitted |
| `tests/gates/fr_p0_structure.py:307` | `scan_for_stale([fixture])` — ev omitted |
| `tests/gates/fr_p2_selector.py:349` | `dangling_rt_references(defined, [reject])` — the function has no `ev` parameter at all (`:290`) |
| `tests/gates/fr_p1_retention.py:182,187` | `retention_gate_violations([reject], [citing])` — ev defaults to `None` |
| `tests/gates/fr_p5_engine.py:217` | `engine_domain_violations([path], …)` — ev omitted |

`selftest.py:244` is the one exempt site where the *caller* holds an `Evidence`
(`_selftest_scan_isolation(ev)`), so it is the site an implementer will reach for.
Doing so is fatal, because `scan_for_stale`'s `ev` parameter controls recording as
well as reading (`fr_p0_structure.py:267,272` — `ev.text_of` and `ev.search` both
record `text`). I ran it against the real tree:

```
mechanisms WITHOUT ev in scan_for_stale: ['execution', 'mapping']   declared: ['execution', 'mapping']
mechanisms WITH    ev in scan_for_stale: ['execution', 'mapping', 'text']
drift? True
```

`FR-P0-HARNESS`'s declared `claim_class` is `execution+mapping` (`registry.py:35`), so
`_class_drift_sweep` (`runner.py:211-214,224-228`) would rewrite `FR-P0-REGISTRY`
`PASS` → `FAIL` on **every** run.

**Impact.** The requirement cannot be satisfied as written. The implementation that
looks like it satisfies it produces exactly the permanent `FR-P0-REGISTRY` failure the
plan names as a stop condition ("Any new `class_drift` entry … the next symptom is a
permanent `FR-P0-REGISTRY` `FAIL`"), and Phase D step 3 forbids unwinding it. The
alternative — quietly dropping the note — makes acceptance criterion "All six
silent-swallow sites … `selftest.py:244` plus every `Fixture` detector call remain
exempt and note the skipped path" and verification step 3 unmeetable.

**Minimal required remediation.** Specify the note channel as an `Evidence`-free
out-parameter, e.g. `scan_for_stale(paths, ev=None, *, strict=False, skipped:
list[str] | None = None)` (same shape for the other five detectors), with the exempt
callers passing a local list and reporting it in their own result text. State
explicitly that **no exempt call site may be given an `Evidence` in order to obtain a
note**, and give the reason (recording `text` on `FR-P0-HARNESS` is class drift), so
the trap is closed the same way Phase B step 3 closes the `production_files()` one.

### 2. High — the retry allowlist does not match the `git` argv Phase C mandates, so the git call introduced into the root gate is not retried

**Evidence.** Phase B step 2: "Add a module-level `RETRYABLE_READONLY_COMMANDS`
allowlist naming only the read-only external commands the harness runs: `git
ls-files`, `git status`, `git log`, `git rev-list`. **Retry is never applied to a
command outside this allowlist**."

Phase C step 1 then specifies the invocation as
`_run_retryable(["git", "-c", "core.quotePath=false", "ls-files", "-z"])`. Its first
two tokens are `git`, `-c` — it does not carry any of the four allowlisted prefixes.
Every other harness `git` call does (`fr_p0_structure.py:281,513,524,546,593`,
`fr_p1_retention.py:56`), so this is the single invocation the allowlist misses, and
it is the new one.

That call is placed inside the root gate: `production_files()` is reached from
`_selftest_scan_isolation` at `selftest.py:241`, and Phase C step 1 requires
`production_files()` to **raise** when `git ls-files` fails. The plan's sole
justification for accepting that exposure is "bounded by the Phase B retry plus the
Phase E lock", and it makes an unbounded version a stop condition ("Any
`FR-P0-HARNESS` failure traceable to the `git ls-files` call in `production_files()`
… the root gate must not become a new transient dependency").

**Impact.** Implemented literally, Phase C adds an **unretried** `git` call whose
failure raises out of `gate_harness` (whose `try/finally` at `selftest.py:126-135`
only removes the scratch dir), is caught at `runner.py:130-131`, fails
`FR-P0-HARNESS`, and takes every gate to `BLOCKED` — a net *increase* in blast radius
over today, where a `git ls-files` failure fails only `FR-P0-NOSTALE`
(`fr_p0_structure.py:281-283`). The 21 recorded `FR-P0-HARNESS` transients show this
gate is already the one that hurts most.

**Minimal required remediation.** State the allowlist match rule explicitly: match on
`argv[0] == "git"` plus the **first non-option token** (skipping `-c <k>=<v>` and
other global options), and add the `git -c core.quotePath=false ls-files -z` argv to
the plan's own worked example so the implementer cannot key the match on `argv[:2]`.

### 3. High — invariant 2 is unmeetable: `FR-P3-CAPS-OWNED` reads untracked state through a scan root no phase touches, and is failing on it right now

**Evidence.** Invariant 2 is declared as an architectural end state that "must be true
when this plan is complete" and is "checkable": "No gate verdict depends on a file
that is untracked or gitignored, **except** … `FR-P0-CLEAN` … and `FR-P0-HISTORY`.
Generated and untracked roots are outside every production scan root." Phase C
delivers this only for `common.production_files()`.

`check_caps` does not use `production_files()`. It has its own scan root at
`tests/gates/fr_p3_calibration.py:52`:

```python
CAP_SCAN_ROOTS = ("meta_prompt", "docs", "policy")
```

and rglobs it directly at `:410-414`, reading each file with `ev.text_of(path)` at
`:416`. `docs/` currently holds 40 untracked files, and the most recent phase-5 run
records:

```
FR-P3-CAPS-OWNED FAIL (7 caps, 7 patterns, 75 files scanned, 0 unowned copies) —
unowned-cap-copy:new_terms_per_lab at docs/research/rendering_gap_scan/readability_metrics_as_rendering_canary.md;
unowned-cap-copy:success_criterion_voice at docs/research/sota_scan_test/bloom_alignment_objective_validation.md
```

`git ls-files` returns nothing for either path. Across today's ten phase-5 runs the
gate reads `PASS, PASS, PASS, FAIL, FAIL, FAIL, FAIL, FAIL, FAIL, FAIL` — an observed
rerun flip driven purely by untracked working-tree state, i.e. the same defect class
Phase C exists to remove. The plan mentions `fr_p3_calibration.py` only to exclude
`:145,376` from the swallow census; `CAP_SCAN_ROOTS` appears nowhere in it.

**Impact.** Invariant 2 and the objective "every remaining `FAIL` is a real defect"
are both false at completion: `FR-P3-CAPS-OWNED` will still be a `FAIL` produced
entirely by uncommitted scratch files, and will still flip whenever those files come
and go. Phase F's "every gate must be `stable`" would also be reported against a gate
whose stability is a function of what the implementer happens to have left in
`docs/`.

**Minimal required remediation.** Either (a) bring `check_caps`' `targets` selection
under the same tracked-content restriction Phase C applies to `production_files()`
(the two-line change is at `fr_p3_calibration.py:410-414`), listing it as a Phase C
step with the same before/after tracked-hit diff; or (b) narrow invariant 2 in the
"Architectural end state" section to the `production_files()` scan root only, and
record `CAP_SCAN_ROOTS` explicitly under "Explicitly out of scope" with the two live
untracked hits above as its evidence. Do not leave the invariant stated in its
current unrestricted form.

## Observations (non-blocking)

- **Phase B step 3's supporting claim about `production_files()`' call sites is
  false.** It states that "none of its five call sites (`fr_p1_retention.py:165`,
  `fr_p2_selector.py:234,333,550`, `selftest.py:241`) has one to pass". All five have
  an `Evidence` in scope (`check_schema_gate(ev)`, `live_v1_references(ev)` called
  with `ev` at `fr_p2_selector.py:188`, `check_deferred(ev)`, `check_sel_mapped` —
  which uses `ev.text_of` at `:554` — and `_selftest_scan_isolation(ev)`). The
  conclusion it supports (module-level helper, mechanism-neutral) is independently
  correct on the class-drift argument, so the approach does not change, but the
  sentence should be struck rather than left as a fact a later reader relies on.
- **`_run_retryable`'s return type is stated twice and inconsistently:** the signature
  is `-> subprocess.CompletedProcess`, the prose says it returns "the last
  `CompletedProcess` **and the retry count**", and Phase C step 1 consumes it as a
  bare `CompletedProcess` ("then splits on `\0`"). Pick one.
- **The 21 `FR-P0-HARNESS` transients are attributed to `selftest.py:117` without
  direct evidence.** The recorded detail is the bare string `TimeoutError: [Errno 60]
  Operation timed out` with no traceback (`runner.py:131` formats only
  `type(exc).__name__: exc`), and `gate_harness` has several other raise-capable I/O
  sites (`_write_case`'s `write_text` at `selftest.py:82,86`, `SELFTEST_DIR.mkdir` at
  `:123`, `subprocess.run` at `:114`, `read_text()` at `:287`). Retrying only `:117`
  may leave some of the 21 unaddressed; Phase F step 4's honest-residual clause covers
  the outcome, but the attribution should be marked as inferred.
- **Phase E's lock path is only safe under a `RESULTS_DIR`-relative reading.** Step 2
  says the lock is "named **exactly `tests/results/.run.lock`**"; step 5's safety
  argument ("`_run` … always sets `FR_RESULTS_DIR` to a per-case scratch directory, so
  a child runner never contends with the parent's lock") is valid only if the path is
  derived from `common.RESULTS_DIR` (`common.py:40`). A literal hardcode would make
  every child runner spawned by `selftest.py:114` find the parent's lock held, write
  no result file, and fail `FR-P0-HARNESS` deterministically. Worth one clarifying
  clause.
- **The Phase A stop condition may fire and halt the plan before any fix.** Verification
  step 2 says "at least one gate is recorded unstable (if none is … the plan stops)".
  The transient-I/O signature has not recurred in the last 40 recorded runs (0/40; 0/13
  today, 10/137 on 2026-08-02, against 65/92 on 2026-07-31), and `FR-P0-CLEAN` is now a
  deterministic `FAIL`. A clean baseline is a plausible outcome, and it would stop the
  plan rather than validate the instrument. Consider making it a recorded diagnostic
  plus a required minimum sample size rather than a hard stop.
- **Phase C's tracked-content restriction removes more than the four roots the plan
  names.** Measured on the current tree, the 561 dropped paths are `outputs/` 448,
  `.claude/` 67, `docs/` 37, `.pytest_cache/` 5, `curricula/` 3 (three untracked
  `arduino_kit/l0{2,3,4}*.v1.json`), `.DS_Store` 1. All are untracked or gitignored, so
  invariant 3 holds and no tracked hit is lost (verified: `dangling_rt_references` 9 → 0,
  `live_v1_references` 0 → 0, no tracked path leaves the set, nothing new enters it).
  The plan's narrative naming only `outputs/`, `.pytest_cache/`, `.DS_Store` and
  `.claude/skills/plan-create-workspace/**` understates it; the untracked `curricula/`
  lessons in particular are worth naming since a reader will expect `curricula/` to be
  in the verdict path.
