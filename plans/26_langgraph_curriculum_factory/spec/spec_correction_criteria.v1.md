# QA criteria — Plan 26 LangGraph Curriculum Factory spec v2 (provider-architecture correction)

The artifact under review is
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`.
It is a corrected version of
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`
(sha256 `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`,
unchanged and immutable). v1's defect: it required Gemini for the M05/M07
review jobs even though the user's recorded, governing constraint is
subscription-only execution using Claude Code and ChatGPT Pro/Codex, with no
Gemini CLI, no Google credential, and no billed API key ever, for this
project. `post_morten/postmortem.v2.md` is the independently-reviewed
incident record that specifies exactly what the correction must contain
(its §8, "Corrected-specification minimum acceptance criteria," and its
required order of operations in §7).

A correct v2 satisfies every criterion below. Attempt to falsify each one
against the actual text of the artifact — do not accept a claim the artifact
makes about itself without checking it against the cited section.

## Criteria (SPEC-T00–SPEC-T10)

1. **SPEC-T00 — Historical immutability.** `langgraph_curriculum_factory.spec.v1.md`
   is unchanged (its sha256 must still be
   `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`). No
   forbidden runtime, test, plan-result, receipt, patch, log, policy, schema,
   model-job, or implementation-graph file was changed by this artifact's
   author. (You may verify this directly against the live repository, which
   you have read-only access to.)
2. **SPEC-T01 — Authority and supersession.** v2 explicitly orders governing
   user constraints, the active meta-prompt requirements, Plans 20–22, Plan
   25 product requirements, Plan 26 retained mechanics, and observed current
   code. Every retained or superseded provider decision cites its source and
   disposition.
3. **SPEC-T02 — Gemini elimination.** Search the complete v2 document
   case-insensitively for `gemini`, `google`, `GEMINI_API_KEY`,
   `GOOGLE_API_KEY`, and `gemini-3-pro-preview`. The only allowed occurrences
   are historical defect statements or explicit prohibitions. No occurrence
   may define a production job, provider, credential, authorization,
   endpoint, prerequisite, fallback, or activation remedy.
4. **SPEC-T03 — Subscription-only invariant.** v2 prohibits billed API keys,
   raw model HTTP APIs, custom provider endpoints, and hidden fallbacks, and
   requires Claude Code and Codex to operate through the user's
   subscription-backed authentication.
5. **SPEC-T04 — Cross-family role mapping.** All eight model jobs
   (M01–M08) have one explicit role, provider family, subscription driver,
   input boundary, output schema, identity claim, and failure disposition.
   Content-generating/mutating roles are Claude/Anthropic; independent
   judgment roles are Codex/OpenAI. Any intentional exception is separately
   justified and preserves different-family final judgment.
6. **SPEC-T05 — Complete consistency.** Every provider/model/transport/
   authentication occurrence in v2 — tables, prose, diagrams, acceptance
   denominators, adversarial cases, authorizations, prerequisites, resolved
   decisions, and checklists — agrees with the same corrected profile (Claude
   authors/repairs, Codex independently judges). Flag any stray v1 phrase
   that was not actually corrected.
7. **SPEC-T06 — Preflight truthfulness.** v2 makes `ready: true` impossible
   when a mandatory model driver cannot authenticate or demonstrate permitted
   subscription-backed operation. The exact N60 false-ready condition
   (preflight reported `ready: true` from executable-identity/hash/version
   proof alone, while a real Gemini call still failed with exit 41) is an
   explicit negative regression case in v2.
8. **SPEC-T07 — Data-boundary correction.** No Google/Gemini transmission
   authorization survives anywhere in v2, and the Claude/Codex staged inputs
   are explicit, least-privilege, content-aware, and approved before
   transmission.
9. **SPEC-T08 — LangGraph preservation.** Compare v1 and v2 structurally.
   Provider correction does not silently redesign the compiled graph,
   deterministic routing/acceptance, reducers, checkpoint/resume, repair
   bounds, artifact immutability, unit/workbook denominators, or terminal
   authority. (The only intended change to the D03 node and its edge-guard
   text is the disclosed strengthening from one capability-proof class into
   five explicit proof classes — that specific, named change is expected and
   correct, not a violation of this criterion.)
10. **SPEC-T09 — Honest lifecycle.** v2 states that specification approval
    precedes implementation remediation, that implementation tests do not
    equal activation, and that activation requires real authorized unit and
    workbook product proofs. v2 does not start or authorize Run 27 anywhere
    in its text.
11. **SPEC-T10 — Historical regressions.** v2 contains explicit controls (or
    an explicit, honest statement of why a given item is out of a
    specification's scope and deferred to a later implementation run,
    naming which later run/action owns it) for: Plan 25 false attribution;
    installed-CLI/authorization confusion; late provider feasibility; N60's
    false-ready preflight; unauthorized provider egress; production-topology
    reachability; descendant receipt invalidation; deterministic evidence;
    machine-readable status; and requirements-level final audit.

## Falsification targets

Specifically attempt to falsify each of these claims against the artifact
text:

- v2 fully removes Gemini as a production dependency rather than hiding it
  behind generic provider wording.
- v2 does not accidentally assign both generation and final judgment to
  OpenAI/Codex (check the M01–M08 table and the family-mismatch rule in
  §6.3/§10 of the artifact).
- v2 does not confuse the specification-review plugin (`qa-gate-codex-run`,
  used to review this very document) with the production model transport
  the specification defines for the compiled graph's M05/M07 nodes.
- v2 does not claim subscription entitlement or executed-model identity that
  the installed `claude`/`codex` drivers cannot actually be shown to prove.
- v2 does not weaken cross-family review, actual-page review, evidence
  denominators, or real-product activation requirements relative to v1.
- v2 does not use the current implementation (`runtime/langgraph_factory/`,
  still Gemini-configured) as authority to override the user's constraints.
- v2 is sufficiently complete to govern a later remediation plan without
  inventing provider decisions the repository's sources do not settle. Where
  it cannot settle one (the exact per-job Claude model/effort pin), check
  that it is marked as an explicit, precisely-named open decision
  (`USER_DECISION_REQUIRED-01`) rather than invented or silently deferred.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
eleven numbered criteria above (a stated criterion fails on a realistic
reading of the artifact, not merely a stylistic quibble). Anything you notice
that does not defeat a numbered criterion belongs in observations, not
findings.
