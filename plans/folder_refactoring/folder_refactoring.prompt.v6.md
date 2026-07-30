# Execute the folder-refactoring plan v6

## Goal

Implement `folder_refactoring.plan.v6.md` through phases 0–4. Finish only when every gate
active at the current phase passes, no gate is `BLOCKED`, every `.reject.` fixture fails
for its declared reason and every `.accept.` fixture validates, every review approves,
results are recorded, and the worktree is clean. Preserve unrelated changes. Never weaken
a requirement and never report an unexecuted check as passing.

Two verdicts, never interchanged: **`BLOCKED`** is a gate-level outcome — a gate whose
dependency failed or was itself blocked, propagating transitively. **`HALTED`** is the
run-level verdict when a phase cannot be approved, whatever the cause.

## Agents

- **Coordinator:** assigns work, enforces phase order, and owns commits.
- **Implementer:** makes the current phase's changes.
- **Validator:** independently runs the harness and verifies its result record.
- **Reviewer:** independently checks the diff against the plan.

Only the coordinator changes Git history. Keep implementation, validation, and review
separate.

## Loop

Read `AGENTS.md` and the complete v6 plan. For each phase `N`:

1. The implementer completes phase `N`. In phase 0, follow §9's seven steps in order —
   write `tests/gates/registry.py` declaring **all 31 gates with their `depends_on`**
   first, and stage `schema/`→`schemas/` with four confirmed `R100` lines from
   `git diff --cached --name-status -M100%` *before* applying any §10 content edit.
2. The reviewer returns `APPROVE` or actionable findings.
3. Fix findings and repeat review until approved.
4. The coordinator creates the phase's **candidate commit**. Gates run against a commit,
   never a dirty tree: `FR-P0-HISTORY` reads `HEAD` and `FR-P0-CLEAN` requires an empty
   `git status`.
5. The validator runs `./tests/run_gates.sh N` and inspects the new JSON result.
6. Validation passes only when `FR-P0-HARNESS` ran first as the graph root and passed,
   all gates with `activation_phase <= N` pass, **no gate is `BLOCKED`**, every later
   registered gate is recorded `SKIPPED (activates at phase M)`, every `.reject.` fixture
   fails for its declared reason, every `.accept.` fixture validates, results are
   written, and the worktree is clean.
7. On failure, the implementer fixes the cause, the reviewer rechecks the diff, the
   coordinator **amends** the unshared candidate commit, and validation repeats from 5.
8. Advance only after review returns `APPROVE` and validation returns `PASS`.

After phase 4, run `./tests/run_gates.sh 4` and review the complete result. Repeat the
same correction loop until both agents approve.

## Standing constraints

- **Order is declared, not assumed.** Gates run in dependency order, ties broken by ID.
  Never reorder by renaming a gate. A missing edge is a defect in the graph, not in the
  gate: **add or correct `depends_on`**, record it as `gate_impl_fix`, and have the
  reviewer re-check it. Never **remove** an edge to let a gate run before its
  prerequisite. A gate whose dependency failed or was blocked is `BLOCKED (dependency …)`
  — never rerun in isolation and reported as a pass.
- **`FR-P0-HARNESS` is the root.** If it fails, report `HALTED` and report no other
  gate's outcome from that run — they are unreliable.
- **Phase 2 authors before it checks.** `FR-P2-CONTRACT-VERSIONED` and `FR-P2-DEFERRED`
  must pass before any gate that reads `decided_model`, `executed_model`, `action_kind`,
  `decision_id` or an `RT-` id means anything. Never edit
  `routing_decision.schema.v1.json` or `execution_log.schema.v1.json` in place — v2 is
  additive; v1 stays byte-unchanged so accepted work still resolves.
- **Retained is not authorized.** The meta prompt's authorized-input table names the four
  `policy/routing/*.yaml` manifests and the two `v2` schemas, and no `v1` contract. It is
  not a whitelist — other legitimate inputs stay. The `v1` contracts belong in the
  separate retained-contracts table, retirable under `RT-6`.
- **Conditions key on types, not words.** `decision_id` is required by
  `action_kind: model_call`, never by a substring of free-text `action`.
- **Patterns, not values — every text gate, not just one.** `FR-P3-CAPS-OWNED`,
  `FR-P2-NOVALUES`, `FR-P3-NO-LITERALS` and `FR-P3-SPLIT` all match a declared anchored
  `prose_pattern`. Never make any of them scan bare values — `1`, `2`, `9`, `high`,
  `low`, `required` would flag the whole repository. A term with no pattern fails; do not
  skip it. Each carries an `.accept.` fixture proving an incidental occurrence is not a
  hit.
- **A production scan never reads `tests/**`.** That includes `tests/gates/**`: a
  detector must contain the literals it searches for, so scanning its own source makes
  every stale-path gate fail on itself.
- **Claim discipline (harness rule 6).** Every gate's claim class is an ordered set,
  printed joined by `+`, and must equal the mechanisms its implementation actually used —
  understating fails `FR-P0-REGISTRY` (d) exactly as overstating does. No gate claims
  `execution` of a controller or routing runtime: none exists. Never write, in a report or
  a document, that the selector is enforced or that the check suite is fully executed.
- **`MAPPED, NOT EXECUTED` is a count with an identifier, never a pass.** Report the count
  from `FR-P4-CHECK-MAPPING` and the `RT-` ids it cites.
- **Never let a production scan read `tests/**` or `plans/**` (harness rule 7).** If a
  detector flags a file anywhere under either, its scan roots are wrong — a gate
  *implementation* defect. But the exclusion bans **globbing and grepping**, not opening
  a **named** file: `FR-P0-REGISTRY`, `FR-P0-TREE`, `FR-P0-HISTORY`, `FR-P2-DEFERRED`,
  `FR-P4-AGREEMENT` and `FR-P4-CHECK-MAPPING` all legitimately read `registry.py` or a
  named section of the active plan. Do not "fix" them by removing those reads.
  `FR-P0-PLANREF` is the further exception: it *does* glob `plans/folder_refactoring/`,
  but for version relationships only, never for path literals.
- **Fixing a gate versus weakening it.** A gate's implementation may be corrected when it
  misreads its subject: a wrong scan root, a bad regex, a misparsed path. Record it as
  `gate_impl_fix` with a one-line reason and have the reviewer re-check it. A gate's
  **acceptance criteria** — pass conditions, `expected_error`, claim class — may never be
  relaxed to make a failing repository pass. `depends_on` is the third category above:
  addable and correctable, never removable. If the repository is what is wrong, fix the
  repository or return `HALTED`.
- **Scope.** Layout, placement, references, the three phase-2 contracts, and the harness.
  Not curriculum content. Anything in §12 is a separate decision — surface it under its
  `RT-` id, do not act on it.

Return `APPROVED` only when the plan's final approval conditions hold. Otherwise return
`HALTED`, naming the failing gate id and its stated failure meaning — and, where the
cause is external or needs a decision, the exact blocker or decision required.
