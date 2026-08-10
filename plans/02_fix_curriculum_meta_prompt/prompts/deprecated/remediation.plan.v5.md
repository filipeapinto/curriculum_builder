# Plan: make the curriculum creator executable unattended, and reusable for a second curriculum — v5

Supersedes `remediation.plan.v4.md`, and through it `v3`, `v2` and `v1`.
v4's structure, its isolation redesign, its "established by execution" discipline and its
baselines were correct and are carried forward unchanged except where a fix below required
amendment. Codex reviewed v4 and returned PLAN INSUFFICIENT with eleven findings. **v5
closes three of them by instruction — F1, F5 and F7 — and deliberately carries the other
eight open.** §11 records both sets: what changed, and what is knowingly outstanding. The
three closed are the two Codex called structural and the one it called hidden:

- **F1** — §2.1 offered `CODEX_HOME` redirection and transcript teardown as equal remedies.
  Redirection is not a remedy at all under §2's own established fact. A boundary was
  asserted rather than established, which is the v1/v2 failure mode in miniature.
- **F5** — criterion 11's oracle was unspecified: a fixed site list would be the right
  answer for the wrong reason, a model call would reintroduce v3's defect 6 under a new
  number.
- **F7** — §1's second goal clause had no success criterion at all.

## 1. Goal — WHY

Take `curriculum_creator` to a state where `prompts/meta_curriculum_prompt.prompt.v5.md`
can be started by a human and left alone until it reaches a terminal state, and where a
second curriculum in a different domain reuses the machinery without editing it.

Both clauses are gated. The first by criteria 1–11, the second by criterion 12 (§3.4).

## 2. The isolation mechanism — capability, not convention

This is the section both prior plans got wrong, so it comes first.

**Established by execution, 2026-07-29:**

| Test | Result |
|---|---|
| Worker with `-C <own dir>` **and** `-s read-only`, asked to read a sibling's verdict by absolute path | **Read it. 0 ms.** Working directory is not a boundary. |
| Worker with `-s read-only`, asked to write inside its root and to `/tmp` | **`BLOCKED`. Neither file appeared.** Write capability is genuinely removed. |

So reads cannot be restricted, but **writes can be removed entirely**. Isolation therefore
comes from ensuring there is nothing to read:

1. Every reviewer runs under `-s read-only`. It cannot create a verdict file, a signal
   file, a temp artifact, or anything else, anywhere — proven above, not asserted.
2. Verdicts return on **stdout only**, captured by the controller process.
3. The controller holds all four verdicts of a pass in memory and persists **nothing**
   until every reviewer in that pass has returned.
4. **During a pass the action log records only `sha256(verdict)`, never verdict content.**
   This closes the hole Codex found in v2: the log's `result`/`notes` fields would
   otherwise disclose reviewer A's finding to reviewer B, defeating the barrier through
   the audit trail itself. Content is written after the barrier; the hash proves the
   post-barrier content is the same verdict that was returned.
5. A **retry is a fresh sealed pass.** No prior-attempt verdict, checkpoint, or stdout
   capture is on disk while a retry runs.
6. **Resume** may not restart mid-pass. If a run is interrupted during a review pass, the
   whole pass re-runs; partial verdicts are discarded, never persisted for reuse.
7. Passes are **sequential, not parallel**. Plan verdicts are persisted only after
   `PLAN_DECISION`; a QA reviewer therefore sees them as authorized prior artifacts, which
   is intended, and never sees a sibling's QA verdict, which is not.

### 2.1 The writer inventory — every writer, not only the sandboxed one

The premise "there is nothing to read" holds only if **every** writer in the process tree
is accounted for. `-s read-only` removes the *reviewer's* write capability. It says nothing
about writes performed by the **controller's own** `codex exec` invocation on the
reviewer's behalf.

| Writer | Channel | Status |
|---|---|---|
| Reviewer process | any file, anywhere | **Closed** — `BLOCKED`, established by execution |
| Controller | action log `result`/`notes` | **Closed** — hash-only during a pass (§2 rule 4) |
| Controller | in-memory verdict buffer | **Closed** — never persisted before the barrier (§2 rule 3) |
| `codex exec` runtime | rollout / session transcript, believed `~/.codex/sessions/*.jsonl` | **OPEN — not established** |

**The open channel, stated plainly.** `codex exec` is believed to persist a per-session
rollout transcript containing the reviewer's prompt and its returned verdict. That write is
the controller's side effect, not the reviewer's, so `-s read-only` does not prevent it —
while §2's own finding is that a reviewer can read the entire filesystem. If the transcript
exists and is readable, reviewer B can read reviewer A's verdict out of A's transcript and
the barrier is gone.

**This has not been verified.** An attempt to read `~/.codex` in this session was stopped by
a permission gate, so no claim about it appears in any "established by execution" table in
this plan. It is an unestablished channel, and it must be established **before**
implementation, not after.

**Resolution path**, in order:

1. **Establish by execution** whether `codex exec` writes a session transcript, where, with
   what permissions, and whether it contains verdict content. Record the result in
   `plans/baseline.v4.md` in the same form as the two tests above.

2. **If it does, exactly two things can close it, and they are not equals.**

   - **Teardown — the only local fix.** The transcript does not exist on disk while any
     sibling reviewer in the same pass is running. This is the same mechanism as the rest
     of §2 — there is nothing to read — and it is the only remedy that follows from an
     established fact. It becomes rule 8 in §2 and flips the §2.1 row to Closed.
   - **An OS-enforced read boundary.** A second OS user owning the transcript directory at
     mode `700`, or a container. This is **not** a local fix: it is the §2 fallback, a new
     dependency, and it is escalated (§8) and decided **before** implementation.

3. **`CODEX_HOME` redirection is not a remedy, and must not be recorded as one.** §2
   established that a reviewer reads any absolute path it is given. Moving the transcript to
   a "controller-owned" directory does not make it unreadable to a process running as the
   same user — there is no such thing as "outside a reader's reach" on this machine, which
   is precisely what §2 proved. Redirection has exactly one legitimate role: it makes the
   transcript location **deterministic and known**, so that teardown can find it without
   guessing and so that §2.2 Half A can enumerate it. It is therefore specified **as a
   precondition of teardown, never as a boundary**.

   v4 offered redirection as an alternative to teardown. That was a boundary asserted rather
   than established — v1 and v2 both died of exactly this — and it silently collapsed into
   the OS-boundary option that §2 says requires escalation. Corrected here.

4. **If neither teardown nor an OS-enforced boundary is workable:** an accepted-and-
   documented exposure, written into §8's risk table with the accepting decision named —
   not a silence.

Until step 1 returns, §2's guarantee is stated as **conditional on the transcript channel**.

### 2.2 How the guarantee is proven — two halves, both required

`tools/check_isolation.py` has **two independent halves**. Criterion 5 is green only when
both are green.

**Half A — deterministic probe, no model.** A plain subprocess (`sh`/`python3`) launched
under **identical sandbox flags** to a reviewer (`-s read-only --skip-git-repo-check`,
stdin closed). It is a fixed script, not a prompt. It attempts, and records the result of,
every action the adversarial reviewer is asked to attempt:
- write inside its own root; write to `/tmp`; write to the output root; append to the action log
  — **every one must return `BLOCKED`**;
- enumerate the output root, `/tmp`, the log, and — once §2.1 step 1 resolves, at the
  location redirection has made deterministic — the transcript path, and fail if **any
  verdict-shaped artifact or any verdict content** is present at probe time. This is the
  positive form of "there is nothing to read", and it does not depend on anything a model
  chooses to do.

**Half B — model-driven adversarial reviewer.** A real pass in which one reviewer is
deliberately instructed to write its verdict to disk, to `/tmp`, and to any reachable path;
to read any sibling verdict it can find; and — added in v4 — **to hunt for a
controller-produced transcript of a sibling reviewer** and read a verdict out of it. Fails
if any write succeeds, if verdict content appears in the log before the barrier, or if the
reviewer obtains a sibling's verdict by any route.

**Why both.** A model that fails to find a leak is indistinguishable from no leak. Half B's
failure mode is a false PASS — the exact failure mode this plan exists to eliminate — and it
is nondeterministic and costs real model calls. Half A cannot be talked out of trying. Half B
can find channels Half A's author did not think of. **A green from Half B alone is not
acceptance** (§8).

**If `-s read-only` proves insufficient** — for example if a worker route needs write
access for an unrelated reason — the fallback is a container or a second OS user, decided
**before** implementation, not after. That is a new dependency and is escalated (§8).

## 3. Success criteria — WHY

v2's criteria failed twice over: criterion 1 exited 0 on the defective tree (so its pass/
fail contract was inverted), and criteria 2–9 failed only because `tools/` did not exist —
the right answer for the wrong reason. v3 states an **expected exit code** for each, and
Step 1 requires each validator to fail *by detecting its defect*, evidenced by its
diagnostic output, not by being absent. v3's own failure was different: two criteria were
written wider than any tool could satisfy, so a green was only reachable by editing the plan.
**v4 added a third requirement: any criterion that scans the repository must state its scope
by named path, never by an adjective.** **v5 adds two more: every criterion names its oracle
and says whether it is deterministic or model-driven (§3.3); and every clause of §1's goal
has at least one criterion (§3.4).**

All commands run from `curriculum_creator/`. Criteria 1–11 keep v4's numbering exactly, so
every cross-reference in §5, §7, §9 and §10 remains valid; 12 is appended.

| # | Command | Now | Done | Detects | Oracle |
|---|---|---|---|---|---|
| 1 | `rg -F -q '3[0-5]' schema/` | exit 0 — 2 hits, `curriculum.schema.v4.json:215` and `:222` | **exit 1** | hardcoded lab-count regexes | deterministic |
| 2 | `python3 tools/check_inputs_have_schemas.py` | exit 1 + names each unvalidated input | exit 0 | an input the prompt requires but no validator covers | deterministic |
| 3 | `python3 tools/check_external_paths.py` | exit 1 + names all **five** in-scope sites (§3.1) | exit 0 | an outside reference, within the declared scan scope, that is neither repointed nor on the `declared_external_reads` allowlist | deterministic |
| 4 | `python3 -m pytest tests/test_log_pairing.py -q` | exit ≠0 | exit 0 | 6 pairing failures, against the **production** pairing function, imported not reimplemented | deterministic |
| 5 | `python3 tools/check_isolation.py` | exit 1 | exit 0 — **both halves** | Half A: any write not `BLOCKED`, or any verdict-shaped artifact/content readable at probe time. Half B: adversarial reviewer writes, reads a sibling, leaks through the log, or reads a sibling verdict out of a controller-produced transcript | **Half A deterministic, Half B model — both required (§2.2)** |
| 6 | `python3 tools/check_checks_executed.py` | exit 1 | exit 0 | a check id with no executing test, or a test that passes vacuously | deterministic |
| 7 | `python3 tools/check_domain_dispatch.py` | exit 1 | exit 0 | a full lab failing either layer, or an unregistered `domain_id` being accepted | deterministic |
| 8 | `python3 tools/check_runtime_authority.py` | exit 1 — **8 live files, 24 references** (§3.2) | exit 0 | a **live** reference to a retired runtime artifact, within the declared scan scope | deterministic |
| 9 | `python3 tools/check_one_authority.py` | exit 1 — supplies defined in calibration **and** the manifest | exit 0 | two **files** claiming the same fact, against a declared fact catalog | deterministic |
| 10 | `python3 tools/check_calibration_semantics.py` | exit 1 — `pedagogy_caps.concrete_before_abstract` has no `enforced_by` entry; `enforced_by.success_criterion_voice` names a pointer that does not resolve from the schema root | exit 0 | **within one file**, the rules JSON Schema cannot express: cap↔`enforced_by` key correspondence, `enforced_by` pointers that resolve, duplicate ids in an id-bearing array, and `[min, max]` ranges with `min > max` | deterministic |
| 11 | `python3 tools/check_doc_claims.py` | exit 1 — **8 sites in 4 files** (§3.3) | exit 0 | documentation asserting a capability the implementation does not have: prose claiming a reviewer is prevented from **reading** a sibling verdict, and any stated reviewer cardinality disagreeing with the prompt's twelve | **deterministic — no model call; lexical classifier gated by a fixture corpus (§3.3)** |
| 12 | `python3 tools/check_domain_reuse.py` | exit 1 — `schema/domain/` does not exist; no second domain registered; no machinery manifest | exit 0 | the machinery being **edited** to accommodate a second domain — any machinery file's content hash changing between "before the fixture domain" and "after a fixture lab in it validates" (§3.4) | deterministic |

Criteria 8 and 11 exist because Codex showed defects that survive every other criterion: a
prompt that keeps pointing at a retired artifact, and documentation that asserts a mechanism
the system does not implement. Criterion 10 exists because v3 retracted v2's schema-based
fixes and assigned the replacement to a tool that nothing ran. Criterion 12 exists because
v4's §1 promised domain reuse and no criterion tested it.

Codex's GREEN LIGHT is not a criterion. It is the exit condition of Step 8.

### 3.1 Criterion 3 — scan scope and per-site disposition

**In scope:** every path-like literal under `assets/`, `schema/` and `routing/` that resolves
outside `CREATOR`. These are the runtime *data* inputs.

**Excluded, by name, not by adjective:**

| Excluded path | Reason |
|---|---|
| `assets/legacy/**` | the failed v3 generator and runner. The prompt (`…v5.md:64`) declares them as evidence to *cite by path and line*, never to open as data. Their `work/elegoo_labs/templates/**` literals are quotations of a dead system. |
| `plans/**` | plans and superseded analyses; historical prose |
| `prompts/meta_curriculum_prompt.prompt.v5.md:22–29` | the `ROOT`/`PRIOR_V4`/`PRIOR_V5`/`V7` block. This is the run's own addressing frame and output tree, not a read of foreign data. **If any step is ever specified to read `PRIOR_V4` or `PRIOR_V5`, that read joins `declared_external_reads` and this exclusion narrows.** |
| `readme.md`, `how_it_works.md`, `pedagogy.md`, `infographic.prompt.v1.md`, `how_it_works.typ` | operator documentation describing the output tree; not runtime inputs |

**The allowlist** is a file, not prose: `assets/external_reads.v1.yaml`, declared in the
prompt's input inventory and schema-validated. It must agree with
`prompts/meta_curriculum_prompt.prompt.v5.md:70`, which today declares exactly two outside
reads (`~/.codex/config.toml`, and network datasheet fetches by `RESEARCH`). Criterion 3
fails if the file and that line disagree.

**All five in-scope sites, verified 2026-07-29, with disposition:**

| Site | Target | Disposition | Reason |
|---|---|---|---|
| `assets/curriculum.v4.yaml:20` | `work/elegoo_labs/templates/kit_references/…/official_kit_photo.jpg` | **repoint** → `assets/official_kit_photo.jpg` | the file is present in `CREATOR`; the pointer is simply stale. *(v3 said line 19; line 19 is the `evidence:` key, line 20 carries the path.)* |
| `assets/l01_unpowered_power_path.json:6` | same | **repoint** | same |
| `assets/fixtures/l01_polarity_asserted.reject.json:6` | same | **repoint** | same; the fixture must reject for its intended reason, not for a broken path |
| `assets/failures.v1.yaml:52` | `work/elegoo_labs/templates_v5/test_results/meta_execution_state.json` | **remove the path**, keep the sentence | line 53 already says *"cited, not read — the diagnoses below are complete"*. A pointer that is never read, to a file outside `CREATOR` that may not exist, is stale history. Replace with a non-path provenance string; the B1–B4 diagnoses below it are self-contained and unaffected. |
| `assets/routes.v1.yaml:15` | `/Users/filipepinto`, `~/.codex/config.toml` | **allowlist** | it is one of the two reads the prompt already declares at `…v5.md:70`. It is a real, bounded, read-only dependency: it determines the sandbox trust level that makes every route work. Repointing it would be a fiction. |

### 3.2 Criterion 8 — scan scope

A **live reference** is a reference in a runtime artifact, in operator documentation, or in
the prompt — anything a reader or a process would follow. A **historical mention** is a
reference in a plan, a superseded analysis, or changelog prose. Criterion 8 fails on live
references only. Without this the criterion is unreachable: 13 files reference
`controller.v1.yaml` or `lab.schema.v3.json` today, including `remediation.plan.v3.md`
itself, and the cheapest way to turn Step 7 green would be to edit the plan.

**In scope (live):** `assets/**` (excluding `assets/legacy/**`), `schema/**`, `prompts/**`,
`routing/**`, and the root operator documents `readme.md`, `how_it_works.md`, `pedagogy.md`,
`infographic.prompt.v1.md`, `how_it_works.typ`.

**Excluded (historical), by name:**

| Excluded path | Reason |
|---|---|
| `plans/**` | `remediation.plan.v{1,2,3,4,5}.md`, `redundancy.analysis.v1.md`, `baseline.v4.md`. A plan that records what was retired must be able to name it. |
| `assets/legacy/**` | quoted evidence from the failed v3 system |
| The retired files themselves, while they exist: `assets/controller.v1.yaml`, `schema/lab.schema.v3.json` | a file's own `$id` is not a live pointer. Moot after Step 7 deletes them. |
| `how_it_works.png`, `.pytest_cache/**` | binary render; tool cache |

**Live sites now, verified 2026-07-29 — 8 files, 24 references:**
`prompts/meta_curriculum_prompt.prompt.v5.md` (5: 60, 101, 106, 120, 268),
`assets/calibration.v1.yaml` (8: 3, 69–75), `assets/checks.v1.yaml` (1: 77),
`readme.md` (3: 34, 53, 86), `how_it_works.md` (2: 80, 106),
`how_it_works.typ` (2: 149, 430), `infographic.prompt.v1.md` (2: 31, 82),
`pedagogy.md` (1: 3).
Excluded now: `plans/redundancy.analysis.v1.md` (52), `plans/remediation.plan.v1.md` (3),
`v2` (3), `v3` (3), `schema/lab.schema.v3.json` (1, self-`$id`). 8 + 5 = 13 files. ✔

### 3.3 Criterion 11 — the claims, where they are, and what decides them

**Scan scope:** `prompts/**`, `assets/**` (excluding `assets/legacy/**`), and the root
operator documents. Excluded by name: `plans/**`, `assets/legacy/**`, `how_it_works.png`.

**Rule A — mechanism.** Any prose asserting a reviewer *cannot read* / *cannot open* a
sibling verdict, or that a reviewer's *authorized input paths* are what prevents it, fails.
§2 established that reads cannot be restricted; the implemented mechanism is prevention of
**writing**, so nothing exists to be read. A claim of read-prevention is a claim of a
capability the system does not have.

Statements of the *outcome* — "never sees another reviewer's verdict", "no shared verdicts",
"none reads another's verdict" — remain true under §2 and pass. The distinction the tool
enforces is **mechanism vs. outcome**.

**Rule B — cardinality.** Any stated reviewer count that disagrees with the prompt's
authority (`…v5.md:110`, `:269` — twelve per lab; `checks.v1.yaml:154` REV-COUNT-TWELVE —
4 plan, 4 QA, 4 PDF) fails.

#### 3.3.1 Rule A's oracle — deterministic, no model call

`check_doc_claims.py` makes **no model call**. Criterion 5 needed a Half A/Half B split
because "did an adversary find a leak" is not decidable by inspection. "Does this sentence
assert read-prevention" *is* decidable, because the assertion is carried by a closed set of
lexical forms: a modal of inability, or an access-control noun. The tool is therefore a
deterministic classifier, not a judgment:

- **Trigger forms (fail)** — within one sentence of a reviewer / sibling / verdict referent:
  `cannot read`, `can't read`, `cannot open`, `cannot scan`, `cannot reach`, `unable to
  read`, `no access to`, `authorized input path`(`s`), `authorized input set`, `input set can
  reach`, `a test must fail if such a path exists`.
- **Outcome forms (pass)** — a statement of what does not happen, naming no preventing
  capability: `never sees`, `no shared verdicts`, `none reads another's verdict`,
  `does not receive`.
- **The discriminator** is whether the sentence names *the thing that prevents* — a
  capability, a path set, an access rule — or only *what does not occur*.

**Why this is not a site list.** A tool keyed to today's eight sites exits 0 the moment those
eight are edited, while a ninth paraphrase written next week passes unseen. That is "the
right answer for the wrong reason", which §7 forbids. So Rule A is proven by a **fixture
corpus**, `tests/fixtures/doc_claims/`, and criterion 11 fails if any fixture is
misclassified:

- false-mechanism paraphrases **not present in the tree today**, which must fail;
- outcome statements, including the three `how_it_works.typ` lines, which must pass;
- near-misses — read-prevention asserted about a non-reviewer subject, such as a learner or
  a renderer — which must pass, because the claim is not about reviewer isolation.

The eight sites in the table below are the **baseline**. The fixture corpus is the **proof**.

**Residual limit, stated rather than hidden.** Lexical detection cannot catch an arbitrary
paraphrase that avoids the vocabulary entirely. The trigger list is therefore a declared,
extensible vocabulary, and any new false-mechanism phrasing found in review is added to both
the vocabulary and the fixture corpus in the same change. This residual is in §8.

**All 8 failing sites now, verified 2026-07-29:**

| Site | Claim | Rule |
|---|---|---|
| `how_it_works.md:67–68` | "A worker cannot scan prior versions, cannot read sibling outputs" | A |
| `how_it_works.md:245–248` | "a reviewer's authorized input paths do not include any sibling reviewer's verdict file. It cannot read the others because it cannot open the files." | A |
| `prompts/meta_curriculum_prompt.prompt.v5.md:115–116` | "a reviewer's authorized input paths must not include any sibling's verdict file, and a test must fail if such a path exists" — **the runtime authority states the false mechanism** | A |
| `assets/checks.v1.yaml:156–161` | check `REV-ISOLATED`: "no reviewer's authorized input set can reach any sibling reviewer's output" | A |
| `infographic.prompt.v1.md:80` | "none can read another's verdict" | A |
| `how_it_works.md:244` | "Four plan reviewers and four QA reviewers" — 8 | B |
| `how_it_works.md:355` | "four plan reviews, four QA/PDF reviews" — 8, and conflates the QA and PDF passes | B |
| `infographic.prompt.v1.md:80` | "8 per lab" | B |

`how_it_works.typ:321, 379, 408` say "isolated — none reads another's verdict" — outcome, not
mechanism, and therefore passing. The `.typ` and `.png` are renders of `how_it_works.md` and
are regenerated after it is corrected; they are not separately authored.

### 3.4 Criterion 12 — second-domain reuse, and what "without editing it" means operationally

§1's goal has two clauses. The first — unattended execution — is covered by criteria 1–11.
The second — "a second curriculum in a different domain reuses the machinery without editing
it" — had **no criterion in v4**. Criterion 7 proves the *dispatch mechanism* exists,
exercised against `electronics`, the only domain that exists anywhere in scope. A mechanism
that has never dispatched to a second target is not evidence of reuse, and §4's "architecture
is sound" is an assumption standing in for a test — which this plan's own standard forbids
everywhere else.

**The fixture domain.** `schema/domain/fixture_mechanics.schema.v1.json` — a deliberately
minimal second domain (simple machines: lever, pulley, inclined plane), registered in
`schema/domain/registry.v1.json` with its own `domain_id` and version. It is a **test
artifact, not a second curriculum.** Authoring a real second curriculum stays out of scope;
what is in scope is proving the machinery does not have to change to accept one. This keeps
the criterion cheap and the goal claim honest — §1 promises reusable machinery, not two
delivered curricula.

**The machinery manifest.** `tools/check_domain_reuse.py` operationalizes "without editing
it" as content identity, not as a judgment call:

1. Hash every machinery file into `plans/machinery.manifest.v1.json` —
   `schema/lab.core.schema.v1.json`, the registry loader, `engine/**`, `tools/**`,
   `assets/checks.v1.yaml`, `assets/limits.v1.yaml`, `assets/routes.v1.yaml`, the pipeline
   definition.
2. Add the fixture domain and validate a full fixture lab in it, through **both** layers,
   exactly as criterion 7 does for `electronics`.
3. Re-hash. **Criterion 12 fails if any machinery hash changed**, and fails if the fixture
   lab does not validate.

The registry data and the domain schema itself are deliberately **outside** the manifest:
adding a domain is *data*, and that is the entire claim. If accepting the second domain
requires touching `lab.core.schema.v1.json` or any tool, the core/domain split is theatre and
the criterion says so — which is exactly the defect Codex named in its v1 review (§9).

## 4. Context & assumptions — WHY

**Established by execution**

| Fact | Evidence |
|---|---|
| `-C` does not contain a worker | sibling verdict read by absolute path, 0 ms |
| `-s read-only` removes write capability | `BLOCKED`; no file created inside root or in `/tmp` |
| `codex exec` needs `--skip-git-repo-check` | `ROOT` is not a git repo |
| `codex exec` needs `< /dev/null` | otherwise blocks on stdin forever at 0.02s CPU, appearing alive |
| Only typst renders PDF; only `pdftoppm` rasterizes | no TeX engine, no importable Python PDF library |
| ImageGen has no proven invocation | never established |
| `uniqueItems` cannot enforce unique object ids | two objects differing elsewhere but sharing an `id` both validate |
| JSON Schema cannot compare `[min, max]` | no cross-element comparison in draft 2020-12 |
| `minProperties` cannot require key **correspondence** | `calibration.schema.v1.json` sets `minProperties: 7` on `enforced_by`; `calibration.v1.yaml` has 7 entries and validates, yet `pedagogy_caps.concrete_before_abstract` is unenforced because `power.permitted_inputs` occupies the seventh slot. Counting is not matching. |

**Not established — see §2.1**

| Open question | Why it is not in the table above |
|---|---|
| Does `codex exec` persist a readable session transcript containing verdict content? | reading `~/.codex` was stopped by a permission gate. No claim is made either way. Resolving it is a precondition of Step 4. |

The three JSON Schema limits above were v2's proposed fixes for the duplicate-id, inverted-
range and cap-enforcement concerns. All were wrong. In v4 **all three are code checks inside
`tools/check_calibration_semantics.py`** (criterion 10), which is a *within-file* semantic
checker. `tools/check_one_authority.py` (criterion 9) is a *cross-file* checker: two files
claiming the same fact. v3 left the split between these two tools unstated; this is it.

**Assumptions**
- Architecture is sound. Four reviews, forty-plus findings, none saying the design is wrong.
  **Narrowed in v5:** the core/domain split is no longer assumed sound — criterion 12 tests it.
- Learner age band 9+; pedagogy caps derive from it.

## 5. Steps — HOW

### Step 1: Build the validators, prove each detects its defect
- **Does:** Writes the **ten** `tools/` scripts (§6), `tests/test_log_pairing.py` and the
  `tests/fixtures/doc_claims/` corpus (§3.3.1). Each validator must fail against the current
  tree **and print the specific defect it found**. A validator failing because a file is
  missing is not evidence — that was v2's error.
- **Where a rule has no live defect** — criterion 10's duplicate-id and inverted-range rules
  have none today (ids are unique; `[2,6]` and `[1,3]` are ordered) — the rule is proven by an
  **adversarial fixture and a mutation test**, and the baseline records that explicitly. A
  sub-rule with neither a live defect nor a mutation test is an unproven sub-rule.
- **Criterion 11 additionally requires its fixture corpus to be green before its baseline
  counts.** A classifier that agrees with today's eight sites but misclassifies a fixture
  paraphrase is the right answer for the wrong reason.
- **Produces:** `tools/`, `tests/`, and `plans/baseline.v4.md` recording each validator's
  exit code and diagnostic output against the current tree, plus the §2.1 transcript finding.
- **Owner:** this session. **Parallel?** yes.

### Step 2: Two decisions — **BLOCKS EVERYTHING DOWNSTREAM**
- **2a — Supply authority.** Three files define supplies: `calibration.power`,
  `curriculum.kit_power_profile`, and the proposed domain profile. Choose one; delete the
  others' claim; update calibration's schema to match. *Recommendation: the domain profile.*
- **2b — Controller boundary.** v2 left this dangling: Step 7 referenced an engine option
  Step 2 no longer contained. Decide now — (i) author a full transition/guard/retry contract
  in YAML, or (ii) write the engine in Python with an independently specified public
  behavioural contract, `engine/` declared in the prompt's input inventory with a hash and
  compatibility rule. *Recommendation: (ii).*
- **Owner:** user, then this session.

### Step 3: Mechanical corrections
Two lab-id regexes (`curriculum.schema.v4.json:215`, `:222`); **all five external references
of §3.1 dispositioned** — three kit-photo paths repointed to `assets/official_kit_photo.jpg`,
`failures.v1.yaml:52`'s dead provenance path removed, `routes.v1.yaml:15` added to
`assets/external_reads.v1.yaml` with its reason; the allowlist file authored and made to agree
with `…v5.md:70`; **reviewer cardinality corrected to twelve** at `how_it_works.md:244`,
`:355` and `infographic.prompt.v1.md:80`; `readme.md` refreshed; `how_it_works.typ`/`.png`
regenerated; canonical naming convention verified repository-wide. Duplicate ids, range
ordering and cap enforcement move to code checks (criterion 10), not schema constraints.
- **Verified by:** 1, 3, 8, 11 *(11 for cardinality only; its mechanism half is Step 4)*.

### Step 4: Implement isolation per §2, and make the documentation say what is true
- **First, resolve §2.1.** Establish whether `codex exec` writes a readable session
  transcript containing verdict content, and record the result in `plans/baseline.v4.md`. If
  it does, close it by **teardown before the next reviewer in the pass starts** — with
  `CODEX_HOME` redirection used only to make the transcript location deterministic, never as
  the boundary itself — and add the closure as rule 8 in §2. If teardown cannot work, the
  remedy is an OS-enforced read boundary, which is a **new dependency and escalates** (§8);
  it is not a local implementation choice. **This precedes the rest of Step 4**;
  implementing the barrier while a controller-side writer is unaccounted for is building on
  v2's premise.
- Then: reviewers under `-s read-only`; stdout-only capture; in-memory barrier; hash-only
  logging during a pass; retry as fresh sealed pass; resume forbidden mid-pass; sequential
  passes.
- **Then rewrite every Rule A site in §3.3** so the documented mechanism is the implemented
  one — prevention of *writing*, not prevention of *reading*. This includes
  `prompts/meta_curriculum_prompt.prompt.v5.md:115–116` (the runtime authority) and the
  `REV-ISOLATED` assertion in `assets/checks.v1.yaml:156–161`, which must be restated as
  "no reviewer's verdict exists on disk while any sibling in the same pass is running", and
  its `stage` re-pointed at `check_isolation.py`.
- **Verified by:** 5, 11. **Depends on:** Step 2b, and §2.1 step 1.

### Step 5: Domain split with real dispatch, proven against a second domain
`lab.core.schema.v1.json` + `schema/domain/electronics.schema.v1.json` +
`schema/domain/registry.v1.json` mapping `domain_id` → schema + version. Seven visual roles
required, with a waiver schema and negative tests. **Then the fixture domain of §3.4** —
`schema/domain/fixture_mechanics.schema.v1.json`, registered, with a fixture lab that
validates through both layers — and `plans/machinery.manifest.v1.json` hashed before and after
it is added. Adding a domain must change **data only**.
- **Verified by:** 7, 12. **Depends on:** Step 2a.

### Step 6: Schemas, and the rules schemas cannot express
Schemas for `limits`, `routes`, `checks`, `failures`, `pipeline`, `external_reads`. In code:
fixture existence, `UNPROVEN` route not cited by a gate, declared supply id present and
`verified_official` in the selected domain profile, `unclosed_starts` computed, duplicate
ids, range ordering, cap↔`enforced_by` correspondence and pointer resolution. The
log-pairing function is written **once** and imported by both the controller and the test —
v2's version let the test verify a different implementation.
- **Verified by:** 2, 4, 6, 9, 10. **Depends on:** Steps 2a, 5.

### Step 7: Migrate the runtime contract completely, then retire
Prompt, `checks.v1.yaml`, `calibration.v1.yaml`'s `enforced_by` map and header,
`readme.md`, `how_it_works.md`, `pedagogy.md`, `infographic.prompt.v1.md` and the `.typ`
render updated in one pass — **all 8 live files / 24 references of §3.2**;
`assets/controller.v1.yaml` and `schema/lab.schema.v3.json` deleted, not merely superseded.
Exit condition: criterion 8 exits 0 **against the scope declared in §3.2**, with `plans/**`
and `assets/legacy/**` excluded — editing this plan can never turn it green. Also:
bootstrap log root, ordering, persistence and resume semantics; a named deterministic
model-selection algorithm covering availability, substitution and ties, with a test;
imagegen proven by a real preflight or removed with the visual contract revised; PDF
acceptance given a defined pixel metric with fixtures and a test command; the pipeline
encoding four PDF-review invocations.
- **Verified by:** 6, 8, 10.

### Step 8: Re-review
Submit to Codex; verify each finding independently before accepting it.

## 6. Artifacts — HOW

```text
curriculum_creator/
  tools/                                   10 scripts
    check_inputs_have_schemas.py           criterion 2
    check_external_paths.py                criterion 3  — scope per §3.1
    check_isolation.py                     criterion 5  — Half A probe + Half B adversary
    check_checks_executed.py               criterion 6
    check_domain_dispatch.py               criterion 7
    check_runtime_authority.py             criterion 8  — scope per §3.2
    check_one_authority.py                 criterion 9  — cross-file
    check_calibration_semantics.py         criterion 10 — within-file
    check_doc_claims.py                    criterion 11 — deterministic, per §3.3.1
    check_domain_reuse.py                  criterion 12 — machinery-hash identity, §3.4
  tests/test_log_pairing.py                1 test, criterion 4
  tests/fixtures/doc_claims/               criterion 11's proof corpus
  plans/baseline.v4.md                     validator baseline + §2.1 transcript finding
  plans/machinery.manifest.v1.json         criterion 12's before/after hash set
  schema/lab.core.schema.v1.json
  schema/domain/{registry,electronics}.v1.json
  schema/domain/fixture_mechanics.schema.v1.json   second domain, test artifact
  schema/{limits,routes,checks,failures,pipeline,external_reads}.schema.v1.json
  assets/domain/electronics.v1.yaml        sole supply authority
  assets/external_reads.v1.yaml            declared_external_reads; must agree with …v5.md:70
  engine/                                  if Step 2b = (ii); declared with hash
  RETIRED: assets/controller.v1.yaml, schema/lab.schema.v3.json
```

**Counts, recounted from §3 and this section:** 12 criteria = 10 tools + 1 `rg` command
(criterion 1) + 1 pytest test (criterion 4). Ten tools, one test, one fixture corpus.

## 7. Verification — HOW

The **twelve** commands in §3, run from `curriculum_creator/`, with the stated exit codes.

Six disciplines, each from a specific past failure:

- **A validator must fail by detecting, not by being absent.** v2's criteria 2–9 exited on
  missing files.
- **Exit codes are stated explicitly.** v2's criterion 1 exited 0 on the broken tree.
- **Tests import the production implementation.** A test that reimplements the rule proves
  only that the test agrees with itself.
- **A repository-wide criterion states its scope by named path.** v3's criterion 8 said
  "any reference … repository-wide" and was therefore unreachable, with the cheapest green
  being an edit to the plan. §3.1, §3.2, §3.3 and §3.4 name every excluded path.
- **A criterion names its oracle, and a deterministic oracle is proven against unseen
  phrasings, not against today's known sites.** v4 left criterion 11's oracle unstated, so it
  could have been a fixed list of eight sites — the right answer for the wrong reason — or a
  model call, which would have reintroduced criterion 5's false-PASS defect under a new
  number. §3 states the oracle for all twelve; §3.3.1 states criterion 11's proof.
- **A remedy must follow from an established fact.** v4's `CODEX_HOME` redirection option
  contradicted §2's own finding that reads cannot be restricted. A remedy that only works
  given a boundary the plan says requires escalation is not a local fix, and must not be
  offered as one (§2.1 step 3).

## 8. Risks and escalation — HOW

| Risk | Mitigation |
|---|---|
| A validator passes on a defect | Step 1 baseline requires the diagnostic, not just the exit code |
| A sub-rule has no live defect to detect | adversarial fixture + mutation test, recorded in the baseline (criterion 10's duplicate-id and range rules) |
| Validators become a second unverified layer | each gets adversarial fixtures and a mutation test; production imports the same function |
| **Criterion 5 greens on the model half alone** | **not acceptance.** Half A is deterministic, model-free, and must be green independently. A pass recorded without Half A's output is a failed pass. |
| **Isolation leaks through a controller-produced transcript** | **open, not established (§2.1).** Resolve by execution before Step 4's implementation; then **teardown** (the only local fix) or an OS-enforced read boundary (escalates), or a documented accepted exposure. Redirection is not a remedy — §2.1 step 3. Half B hunts for it; Half A enumerates its location once redirection has made it deterministic. |
| **A remedy is offered that the plan's own facts do not support** | §7's sixth discipline; §2.1 step 3 names the one v4 contained |
| Isolation leaks through a channel not tested | the adversarial reviewer actively attempts write, read, log-leak and transcript-read; the deterministic probe independently asserts nothing readable exists |
| Documentation asserts a capability the system lacks | criterion 11 — the defect class that produced v1 and v2, now gated |
| **Criterion 11 misses a paraphrase outside its trigger vocabulary** | stated residual (§3.3.1). The vocabulary is declared and extensible; every new phrasing found in review is added to both the vocabulary and the fixture corpus in the same change. The fixture corpus, not the eight known sites, is what proves the rule. |
| **Domain reuse is asserted rather than tested** | criterion 12 — a second registered domain and a machinery hash manifest. If accepting it requires editing the core schema or any tool, the split is theatre and the criterion fails. |
| A criterion no step can satisfy | criteria 3, 8, 11 state their scan scope by named path; criterion 12 states its manifest set; Steps 3, 4, 5 and 7 disposition every listed site |
| `-s read-only` insufficient for some worker | escalate before implementing; container or second OS user is a dependency decision |
| Partial fix reported complete | demonstrated repeatedly; every criterion is a command with a stated exit code, run and shown |

**Escalate when:** Step 2a or 2b is undecided; **the §2.1 transcript channel is real and
teardown cannot close it** — the remaining remedy is an OS-enforced read boundary, which is a
new dependency, and accepting a residual exposure instead is a human decision, not this
session's; `-s read-only` cannot serve a required worker; **criterion 12 fails because
accepting the fixture domain requires editing `lab.core.schema.v1.json` or a tool** — that
invalidates the core/domain design, not just the implementation; imagegen cannot be proven
and the visual matrix must change; a finding contradicts a decision recorded here on purpose,
such as the calibration/prose divergence.

## 9. Traceability

**v1 → v2 → v3.** v2 claimed to address "five findings" when Codex's v1 review contained
six. All six are carried here: calibration/power contradiction (2a), incomplete runtime
migration (7), cross-artifact rules wrongly assigned to JSON Schema (6, 10), false lab-regex
criterion (3, §3), core/domain theatre and undeclared engine (5, 2b, **and now criterion
12**), insufficient success criteria (§3).

## 10. v3 → v4

| # | v3 defect | What changed in v4 |
|---|---|---|
| 1 | Criterion 8 unreachable — "any reference … repository-wide"; 13 files match today, including `remediation.plan.v3.md` itself, so the cheapest green was editing the plan | §3.2 defines *live reference* vs *historical mention* and names every excluded path (`plans/**`, `assets/legacy/**`, the retired files' own `$id`, `how_it_works.png`, `.pytest_cache/**`). Criterion 8's "Now" is 8 live files / 24 references. §5 Step 7's exit condition and §6 both restate the scope. New discipline in §7. |
| 2 | Step 3 could not close criterion 3 — it repointed 3 sites; the criterion covered 5. Line number wrong | Corrected `curriculum.v4.yaml:19` → `:20`. §3.1 enumerates all five sites with a disposition and a reason each. Step 3 widened to all five. Allowlist given a concrete home, `assets/external_reads.v1.yaml`, with a schema in Step 6. Scan scope named. |
| 3 | §2's leak inventory stopped one writer short — `codex exec`'s own session transcript is the **controller's** write, unaffected by the reviewer's `-s read-only` | New §2.1 writer inventory with the transcript row marked **OPEN — not established**, deliberately absent from every "established by execution" table. Named resolution path. §2.2 Half B's mandate widened to hunt transcripts. §8 risk row and escalation trigger added. Step 4 now begins with resolving it. |
| 4 | Nothing detected documentation asserting a capability that does not exist — v1's and v2's own failure mode | New criterion 11 + `tools/check_doc_claims.py`. §3.3 gives Rule A (mechanism vs. outcome) and Rule B (cardinality), with all 8 failing sites enumerated. Rewrite assigned to Step 4; cardinality stays in Step 3. |
| 5 | `check_calibration_semantics.py` shipped unverified | New criterion 10 with a verified "Now". Wired into Step 6 and Step 7. §4 gains the `minProperties` row and states the criterion 9 / criterion 10 split. |
| 6 | Criterion 5's only oracle was a model | §2.2 splits `check_isolation.py` into Half A (deterministic, model-free) and Half B (the model adversary). Criterion 5 is green only when both are. |

## 11. v4 → v5

Codex reviewed v4 and returned PLAN INSUFFICIENT with eleven findings. It independently
re-verified every v4 baseline it could check and confirmed all six v3 defects closed. **By
instruction, v5 closes three findings and carries eight open.**

### Closed in v5

| Codex finding | What changed in v5 |
|---|---|
| **F1** — §2.1 offered `CODEX_HOME` redirection and teardown as equal remedies. Redirection is incoherent under §2's own established fact: nothing is "outside the reach" of a reader shown able to read any absolute path. It collapses into the OS-boundary option that §2 says escalates — a boundary asserted, not established, which is the v1/v2 failure mode | §2.1's resolution path rewritten. **Teardown is named the only local fix.** An OS-enforced read boundary (separate uid at mode `700`, or a container) is named as the only alternative and is explicitly a new dependency that escalates. **Redirection is explicitly rejected as a remedy** (§2.1 step 3) and re-specified as a *precondition of teardown* — it makes the transcript location deterministic so teardown can find it and Half A can enumerate it. The same error was repeated in §8's risk row and escalation trigger and in Step 4; all three corrected. New sixth discipline in §7: *a remedy must follow from an established fact.* |
| **F5** — criterion 11's oracle was unspecified. A fixed list of today's 8 sites would be the right answer for the wrong reason (§7 forbids it); a model call would reintroduce v3's defect 6 under a new number | New §3.3.1. `check_doc_claims.py` makes **no model call** — it is a deterministic lexical classifier with a declared trigger vocabulary and a declared outcome vocabulary, discriminating on whether a sentence names *the thing that prevents* or only *what does not occur*. **It is not a site list:** Rule A is proven by a fixture corpus, `tests/fixtures/doc_claims/`, containing paraphrases absent from today's tree (must fail), outcome statements (must pass) and non-reviewer near-misses (must pass). The 8 known sites are the baseline; the corpus is the proof. Step 1 requires the corpus green before the baseline counts. The residual — a paraphrase outside the vocabulary — is stated in §3.3.1 and §8, not hidden. §3's criterion table gains an **Oracle** column for all twelve. |
| **F7** — §1's second goal clause ("a second curriculum in a different domain reuses the machinery without editing it") had no criterion. Criterion 7 proves the dispatch mechanism against `electronics`, the only domain in scope, and §4's "architecture is sound" stood in for a test | New **criterion 12** + `tools/check_domain_reuse.py` + §3.4. A deliberately minimal second domain, `schema/domain/fixture_mechanics.schema.v1.json`, registered and exercised with a fixture lab through both layers. "Without editing it" is operationalized as **content identity**: `plans/machinery.manifest.v1.json` hashes the core schema, registry loader, `engine/**`, `tools/**` and the runtime yaml before the domain is added and after its lab validates; criterion 12 fails if any hash changed. Registry data and the domain schema are deliberately outside the manifest — adding a domain must be *data only*. Wired into Step 5 ("Verified by: 7, 12"). §4's soundness assumption narrowed: the core/domain split is no longer assumed. §8 gains a risk row and an escalation trigger — a criterion-12 failure invalidates the design, not the implementation. Scoped as the cheap fix: a **test artifact, not a second curriculum.** |

### Carried open by decision — not addressed in v5

These are live Codex findings against v4 that v5 does **not** fix, recorded so they are not
mistaken for oversights and are not rediscovered as new:

| Codex finding | Class | Status |
|---|---|---|
| F2 — §2 never states whether the four reviewers *within* one pass run concurrently or sequentially; rule 7 only orders passes. Load-bearing for teardown's "before the next reviewer starts" | specification defect | open |
| F3 — no writer-inventory row for a controller checkpoint/resume-state file; Step 2b defers the engine, so the plan never says whether the checkpoint writer is the action log or a separate unaccounted writer | specification defect | open |
| F4 — §2.1 step 1 scopes the audit to "a session transcript", not `codex exec`'s complete write-set (caches, telemetry, crash dumps, temp files possibly outside `~/.codex`); Half A checks a fixed location list rather than tracing actual writes | specification defect | open |
| F6 — `plans/baseline.v4.md` is Step 1's central deliverable and the plan's evidentiary record, yet it is excluded from every scan scope; nothing gates whether its recorded exit codes and diagnostics are true | specification defect | open |
| F8 — §3.2's "13 files" omits this plan family's later members; the true count at v4 was 14, and is 15 with v5 on disk. Does not affect criterion 8's reachability (`plans/**` is excluded regardless), but it is an inexact claim stamped "verified" | specification defect | open |
| F9 — criterion 10 is wired to Step 6, but the `enforced_by` data fix lands in Step 7 (line 354), so Step 6 alone likely cannot turn it green; Step 3 disambiguates a split criterion explicitly and criteria 6/10 get no equivalent note | specification defect | open |
| F10 — Step 4 and Step 7 both write `assets/checks.v1.yaml`; nothing states Step 7 must preserve Step 4's `REV-ISOLATED` rewrite | implementation risk | open |
| F11 — criterion 10's scan target file is never named; `assets/calibration.v1.yaml` is implied by the tool name and its two example defects, not stated | specification defect | open |

**Baselines.** No baseline was re-verified for v5; all are carried from v4, where they were
established by execution on 2026-07-29 and independently confirmed by Codex — with the single
exception of the `13 files` count in §3.2, which is known inexact and is carried open as F8.
Criterion 12's "Now" (exit 1 — `schema/domain/` does not exist) was verified on 2026-07-29.

**Naming.** `plans/baseline.v4.md` keeps its v4 name deliberately: v5 changes no baseline, and
renaming the evidence file to match a plan version that re-verified nothing would misrepresent
when the evidence was taken.

**Numbering.** Criteria 1–11 keep v4's numbers exactly; 12 is appended. No cross-reference in
§5, §7, §9 or §10 required renumbering. Changed "Verified by" lines: Step 5 gains 12. Counts
recounted in §6: 12 criteria = 10 tools + 1 `rg` + 1 test.
