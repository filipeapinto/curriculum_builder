# N90_FINAL_AUDIT result

status: PASSED

## VERDICT: `IMPLEMENTED_NOT_ACTIVATED`

Independent audit against the live repository at
`/Users/filipepinto/Projects/curriculum_builder`. Every receipt hash was
recomputed with the controller's own digest algorithm, the complete
`tests/runtime` suite was rerun end-to-end with the mandated interpreter
(`/tmp/plan26_n30_verify/bin/python`), the single-production-path and
forbidden-import claims were re-grepped directly against current code, and
all eight core runtime invariants were re-derived from source by an
independent, read-only agent with no access to this session's context (so it
could not simply restate a prior claim). No claim in this report rests on
trusting a prior node's or a prior N90 attempt's prose without direct
re-verification.

---

## 1. Spec-to-implementation traceability (TEST item 1)

Spec audited: `spec/langgraph_curriculum_factory.spec.v1.md`, sha256
`44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` (matches
the hash N60 recorded as its own input — unchanged since).
`contracts/traceability_matrix.v1.md` and `contracts/node_ownership.v1.md`
(frozen N00 artifacts, hashes verified current in section 2) map every
normative spec section and QA-criteria line to one owning N-node. The
independent invariant-audit agent additionally sampled the spec and
`qa_criteria.v3.md` directly for red flags (`NotImplementedError`, TODO
markers, references to nonexistent functions) rather than trusting the
matrix's own coverage claim: none found. The two `graph.py:117-118` string
hits are literals inside an anti-placeholder detector
(`PLACEHOLDER_SOURCE_MARKERS`), not real stubs. Spec section 20.2's
external-activation prerequisites (live credentials, sandbox proof) are
correctly modeled as activation conditions, not implementation gaps — this
is exactly the distinction the spec's own `IMPLEMENTED_NOT_ACTIVATED`
vocabulary exists to express. No spec/QA line was found without
implementation evidence.

## 2. Node results, receipts, and hash integrity (TEST item 2)

All 15 node receipts (`results/v3/*.receipt.v1.json`) were independently
recomputed this attempt using `prompt_graph_controller.path_digest()` (the
controller's own sha256-file / sha256-of-sorted-tree algorithm), executed
directly against the live repository — not read from any prior attempt's
markdown. Full method and output:
`evidence/N90_FINAL_AUDIT/receipt_hash_verification.txt`.

| Node | Status | `result.v1.md` sha256 |
|---|---|---|
| N00_BASELINE_FREEZE | PASSED | `c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5` |
| N10_DEPENDENCY_API | PASSED | `1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658` |
| N11_STATE_REDUCERS | PASSED | `9633ac27f94f1fa97ebf50c0119eb76124f233c3f75311b07697b3281818a0e9` |
| N12_EVIDENCE_ARTIFACTS | PASSED | `6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f` |
| N13_TRANSPORT_AUTH | PASSED | `ae681c609bbc2e8dc4815a3fd9d15136ca57e9a1587f8dd5ca0a4a038b2e842a` |
| N20_GRAPH_COMPILER | PASSED | `46920dafcb930945ebe7a802e96c9feec1ade6a4f35a43ac84bc1bf8fd12bfef` |
| N21_PERSISTENCE_RESUME | PASSED | `cd8f08eac498c14370d31578b056d8e12477293dfad03378cb9680e106fd9841` |
| N22_DETERMINISTIC_NODES | PASSED | `a167b4a11d4f4b8c32f9d75bd23f98f8b373fac7d28e558124dd6a5461b535fb` |
| N23_MODEL_NODES | PASSED | `3fc92f0a9df3c9ffaf416aef49cb3ebd76b0f2e8fdad33d7bc3e65eeeabd3dd5` |
| N30_UNIT_GRAPH | PASSED | `98249a68aad16ef6fb8c576ecf5f0ad0ca99fc9a475c661bb522f9a145425c8f` |
| N31_REPAIR_ACCEPTANCE | PASSED | `325936e48371bf40a638f97d3a5c73137775cfe44f8c8582ee6cb5e048d4224c` |
| N32_WORKBOOK_TERMINALS | PASSED | `ceb509d327ccefb03d6d194ce5491279ac02a8ffa7a08574d4868078391399ce` |
| N40_CLI_CUTOVER | PASSED | `c4ae64eeb59a98f877ba49b2630253ce1b9149ef80325e92b6fa9f1067a144ea` |
| N50_ADVERSARIAL_REGRESSION | PASSED | `796e197370e486990f5d47636c8c714bbf62b5422de1bbad03cec72d546cfe7d` |
| N60_LIVE_PRODUCT_PROOF | NOT_AVAILABLE | `4d9e8ff47a0dc966e2fa54f71550be4ac66ed5f76f04229cabe0891ca7da2fd9` |

Result: **0 mismatches across all 15 receipts** (all declared outputs, files
and directory trees alike), with the working tree in its committed state.
`requirements/plan26.lock` sha256
`df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835` —
unchanged since N10, byte-identical across every citing node.

### Finding 1 — N40_CLI_CUTOVER evidence non-determinism (non-blocking, informational; per approved patch P-N90-001)

Two files in `results/evidence/N40_CLI_CUTOVER/` — `preflight_read_only.txt`
and `plan25_resume_refusal.txt` — are written by
`tests/runtime/test_plan26_cli.py::PreflightTests::test_preflight_read_only_evidence`
and `::test_plan25_root_refusal_evidence`, both of which open a
`tempfile.TemporaryDirectory()` and embed the resulting random path (and, for
the preflight test, the runtime's own `plan26-preflight-<random>` scratch
directory) into the evidence text via the CLI's own echoed JSON/stderr. This
means every rerun of the required, unchanged full suite regenerates these two
files with a different byte-stream, permanently unable to reproduce their
receipted bytes — a structural test artifact, not an implementation defect.

Verified directly this attempt: with the evidence tree in its committed
(receipted) state, 0 hash mismatches. After rerunning the full suite, `git
diff` shows exactly these two files changed, and in each case the only
difference is the random tempdir substring — confirmed by running the
affected tests twice in a row and diffing (see
`evidence/N90_FINAL_AUDIT/n40_evidence_drift_analysis.txt`). No other file,
field, or byte differs; no behavioral regression. Working tree restored to
committed state via `git checkout --` before finishing.

Per P-N90-001, this is recorded as non-blocking/informational, not routed as
a `cli_or_cutover` finding. Note: this audit's own verification found the
same structural drift also affects `plan25_resume_refusal.txt`, not only
`preflight_read_only.txt` as P-N90-001 names explicitly — but it is the
identical mechanism (a `tempfile.TemporaryDirectory()` path embedded in
CLI-echoed text by an N40-owned test), not a different kind of difference or
evidence of real behavioral regression, so it is treated under the same
non-blocking disposition the patch establishes.

### Finding 2 — N40/N50/N60 receipts predate later N20/N31/N32 rework (non-blocking; closed by direct re-verification)

`N40_CLI_CUTOVER`, `N50_ADVERSARIAL_REGRESSION`, and `N60_LIVE_PRODUCT_PROOF`
receipts carry `graph_digest 3c4177f9...`, while the live
`implementation.graph.v3.yaml` (and N20/N30/N31/N32's receipts) carry
`18d619bb...` — later patch rounds (commit `165555d`: `graph.py` +102,
`acceptance.py` +163, `repair.py` +96; commit `d27b7dc`: P-N20-002/P-N32-002)
postdate N40/N50/N60's original receipts. The manifest's own
`rules.invalidate_descendants_on_rework: true` implies these should have been
re-receipted; they were not — a harness/scheduler bookkeeping gap, not owned
by any curriculum N-node (no matching key exists in
`implementation.graph.v3.yaml`'s `rework_edges` block; this is scheduler
mechanics, outside the N-node ownership vocabulary).

Closed, not merely noted: this attempt independently reran the complete
regression suite and the production-path/invariant checks against the
**current, final, post-rework code** (not the stale receipt) — see sections
3–5. Full timeline: `evidence/N90_FINAL_AUDIT/receipt_provenance_timeline.txt`.
Non-blocking. Recommendation (process hygiene): the controller should
auto-invalidate descendant receipts when an ancestor's `graph_digest`
changes post-hoc, per its own stated rule.

## 3. Exactly one compiled LangGraph production path (TEST item 3)

- Single `StateGraph(...)`/`.compile(...)` pair: `runtime/langgraph_factory/graph.py:601,612`. No other occurrence in `runtime/langgraph_factory/*.py` (all other hits are unrelated `re.compile(...)` calls or comments).
- Single definition of `build_curriculum_factory_graph` (`graph.py:575`); exactly two call sites, both in `runtime/run_curriculum.py` (`:554` resume branch, `:570` fresh branch), both inside the CLI's one live-execution function (`_run_live`), both calling the identical function.
- No `langchain` (non-core; `langchain_core` is LangGraph's own dependency and excluded per `implementation.graph.v3.yaml`'s `forbidden_production_imports`), `langchain_openai`, `langchain_google_genai`, `openai`, or `google.generativeai` import anywhere under `runtime/`.
- `runtime/session_bridge.py` (Plan 25 legacy) remains on disk but is imported only by test files, never by `run_curriculum.py` or anything under `langgraph_factory/` — confirmed unreachable from production.
- Live `--help` (rerun this attempt) exposes exactly `--preflight | --unit | --all | --resume`, each requiring `--authorization` except read-only `--preflight` — no legacy path.

Full commands and output: `evidence/N90_FINAL_AUDIT/production_path_audit.txt`.

## 4. Eight-job / authority / denominator / repair / persistence / resume / terminal / CLI invariants (TEST item 4)

Delegated to an independent, read-only agent with no access to this
session's context, instructed to verify each invariant from source. All 8
PASS, each with file:line evidence. Full report:
`evidence/N90_FINAL_AUDIT/invariant_audit.txt`. Summary:

1. Eight model jobs, package-relative prompts/schemas, count enforced (`model_nodes.py:102-109`, `transport.py:158-161,44-47`) — **PASS**
2. Authority: `FORBIDDEN_MODEL_FIELDS` (`transport.py:58-64`) enforced at schema load and per-candidate (`transport.py:237-244,725,841`; `model_nodes.py:431,545,560`) — **PASS**
3. Denominators: `compute_unit_denominator` recomputes all 12 categories fresh per call (`acceptance.py:108-268,327,366`), rejects cross-unit/stale members by construction — **PASS**
4. Repair: `admit_repair_child` recomputes the diff itself, rejects stale parent hash, hard-fails on out-of-boundary pointers (`repair.py:883-957`) — **PASS**
5. Persistence/resume: real `SqliteSaver` (`persistence.py:538-545`); `validate_resume_inputs` refuses on any of 5 drift classes (`persistence.py:1011-1031`); resume refused outside resumable terminals (`persistence.py:1034-1039`) — **PASS**
6. Terminals: exactly 6 kinds (`nodes/terminal.py:48-108`); `write_terminal` independently re-derives and downgrades unsupported claims to `SYSTEM_FAILURE` (`nodes/terminal.py:396-500`) — **PASS**
7. CLI: one live path (`_run_live`), fresh/resume both call `build_curriculum_factory_graph` once each (`run_curriculum.py:554,570`); no simulation/session-bridge/Plan-25 reference reachable — **PASS**
8. Single `StateGraph`/`.compile`, no forbidden imports (`graph.py:601,612`) — **PASS**

## 5. Adversarial/regression completeness, no waived tests (TEST item 5)

N50's own receipt (`796e197370e4...`, PASSED) maps every spec 17.2
adversarial row to a named test (`tests/runtime/test_plan26_adversarial.py`,
26 tests, hash `0cbca18f412dd63b1c1a82fb535deb4ab50c8bcb8885fc02f2fa421d601c5a04`,
matches receipt exactly). Per Finding 2, this audit did not stop at that
receipt and independently reran the complete suite against current code:

```
/tmp/plan26_n30_verify/bin/python -m pytest -q tests/runtime -rs
```
```
SKIPPED [1] tests/runtime/test_plan26_lock_drift.py:220: pinned generator absent (needs pip==25.3, pip-tools==7.6.0); CI installs both
1246 passed, 1 skipped, 406 subtests passed in 142.51s (0:02:22)
```

Zero failures, zero errors, zero xfail/xpass. The one skip is an
environment-only gap (a pinned pip/pip-tools generator not installed on this
host; CI installs both per the test's own reason string), not a deleted,
weakened, or waived test. Full output: `evidence/N90_FINAL_AUDIT/full_suite_rerun.txt`.

## 6. Activation gate (TEST items 6–7)

- N50 status: **PASSED** (original receipt, reconfirmed live in section 5).
- N60 status: **NOT_AVAILABLE**. Its own evidence
  (`results/N60_LIVE_PRODUCT_PROOF.result.v1.md`) shows Codex is
  live-authenticated (ChatGPT subscription) and both provider hosts are
  network-reachable, but the Gemini CLI has no usable credential in this
  environment (`gemini-api-key` auth mode selected, `GEMINI_API_KEY`/
  `GOOGLE_API_KEY` unset, no Google account signed in) — a real,
  non-simulated probe failure (exit 41). No partial transmission was
  attempted; no curriculum artifact was produced or claimed. This is an
  external account/credential gap, not an implementation defect — the
  runtime, transport, and preflight code all report ready
  (`preflight_stdout.json`: `"ready": true`, all 6 capabilities PASS).
- `implementation.graph.v3.yaml`'s own terminal guard for
  `IMPLEMENTED_NOT_ACTIVATED` reads: "N50 passed, N60 is NOT_AVAILABLE, and
  N90 found no implementation defect." All three conditions hold.
- TEST item 6's condition for `ACTIVATED` (authorized live unit + full-release
  proof) is not met and was correctly not attempted.

## Findings summary / rework_edges

Both findings below are non-blocking and informational; neither is routed
through `rework_edges` because neither is a blocking finding (per LOOP,
rework keys are only emitted for blocking findings) and Finding 2 is not
owned by any curriculum N-node.

| Finding | Disposition |
|---|---|
| F1: N40_CLI_CUTOVER's `preflight_read_only.txt` and `plan25_resume_refusal.txt` cannot reproduce receipted bytes (tempfile-randomized path substring embedded by N40's own tests) | Non-blocking, informational per P-N90-001. Structural test artifact, not a code defect. Evidence tree restored to committed state. |
| F2: N40/N50/N60 receipts predate later N20/N31/N32 rework (`graph_digest` mismatch) | Non-blocking. Closed by direct re-verification: full suite, production path, and all 8 invariants reconfirmed against current, post-rework code. Process-hygiene recommendation only, no rework_edges key applies. |

Neither finding is a second or third occurrence of the same root cause under
this node's own prior cycles in a way that would force `BLOCKED` (F1 traces
to a structural, already-diagnosed, unfixable-by-any-node non-determinism
per P-N90-001; F2 is closed by this attempt's own direct re-verification, not
merely repeated). No finding blocks this verdict, and no ownership is
ambiguous.

## Verdict rationale

All 8 invariant classes pass on direct, current-code re-verification; the
complete regression/adversarial suite passes clean (1246 passed, 1 skipped
for an environment-only reason, 0 failures) against the live, final
(post-rework) code; the production path is singular with no forbidden import
or legacy fallback reachable; every receipted artifact hash is verified
current and valid (0 mismatches). N60 correctly reports `NOT_AVAILABLE` for a
genuine, evidenced external prerequisite (live Gemini credential) rather than
any implementation gap. Per TEST item 7 and the manifest's own terminal
guard, the truthful verdict is:

**`IMPLEMENTED_NOT_ACTIVATED`**
