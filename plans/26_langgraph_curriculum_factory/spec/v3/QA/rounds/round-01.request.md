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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v3.md
Version: round 1 of at most 5
SHA-256: 419d1e91d197e967302dab62e356c3fefa861d45585a089bf29b616264f66d87

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# QA criteria — Plan 26 LangGraph Curriculum Factory spec v3 (N20-recovery transport correction)

The artifact under review is
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v3.md`.
It is a corrected version of
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`
(sha256 `99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`,
unchanged and immutable). v2 was itself independently QA-verified and
user-approved (`plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`);
that approval covered v2's production **architecture** decision (Claude
authors/repairs six jobs; Codex independently judges two jobs) and is not
reopened here. What v3 corrects is a defect in v2's **transport mechanics**
for the Claude jobs, discovered live by the `N20_PROVIDER_TRANSPORT` node's
`BLOCKED` attempt
(`plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json`,
findings N20-F03 through N20-F06) and specified in
`plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v1.md`'s
"Correction design, 1. Correct the specification."

A correct v3 satisfies every criterion below. Attempt to falsify each one
against the actual text of the artifact — do not accept a claim the artifact
makes about itself without checking it against the cited section. Where a
criterion asks you to compare v3 against v2, you have read-only access to
both files in the live repository.

## Criteria (SPEC3-T00–SPEC3-T08)

1. **SPEC3-T00 — Historical immutability.** Neither
   `langgraph_curriculum_factory.spec.v1.md` (sha256
   `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`) nor
   `langgraph_curriculum_factory.spec.v2.md` (sha256
   `99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`) was
   edited, moved, or deleted. No Run 27 N00–N20 result, evidence file,
   receipt, patch, log, policy, schema, model-job configuration, runtime
   code, test, or implementation-graph file was changed by this artifact's
   author. (Verify directly against the live repository.)
2. **SPEC3-T01 — Zero literal retired-provider identifiers.** Search the
   complete v3 document case-insensitively for `gemini` and `google` (as
   substrings, so this also catches `GEMINI_API_KEY`, `GOOGLE_API_KEY`,
   `google-generativeai`, `gemini-3-pro-preview`, and any file path containing
   either word). There must be **zero** matches. This is stricter than v2's
   own SPEC-T02 criterion, which tolerated historical-narrative and
   prohibition-statement occurrences; v3 must convey the identical historical
   facts and prohibitions using no literal retired-provider or retired-family
   name anywhere in its own active text, deferring the specific historical
   name to v1/v2 (unchanged, immutable, and available by cross-reference)
   where institutional memory needs it.
3. **SPEC3-T02 — Architecture not reopened.** v3's production provider
   *architecture* — M01–M04, M06, M08 via Claude/Anthropic; M05, M07 via
   Codex/OpenAI; family-mismatch-is-system-failure; the five-proof-class
   preflight; the `anthropic`/`openai`/`primary_source_hosts` authorization
   classes — is byte-for-byte unchanged in substance from v2 (§6.3, §7.1
   items 1–3, §7.4). Only the mechanics named in criteria 4–7 below may
   differ. Flag any architectural drift as a defeat of this criterion.
4. **SPEC3-T03 — CLI-schema projection.** v3 requires a deterministic
   CLI-schema projection of each job's canonical output schema — computed by
   code, not per-activation, stripping `$schema` and rejecting external
   `$ref` — transmitted inline as JSON text to `--json-schema` for Claude
   jobs, never as a file path. The unmodified canonical schema remains the
   sole post-execution admission authority. The receipt separately binds a
   canonical-schema digest and a CLI-schema-projection digest.
5. **SPEC3-T04 — stdin projection delivery.** v3 requires the canonical
   authorized-input projection for a Claude job to be transmitted inline on
   the process's stdin (JSON-encoded together with the instruction), not
   read by the worker from a staged workspace file — and explicitly reasons
   why: an empty `--tools` list leaves the worker with no file-reading tool.
   `authorized_input.json` may still be staged for receipt/audit hashing, but
   the specification must not claim the worker reads it.
6. **SPEC3-T05 — stream-json per-turn identity.** v3 requires
   `--output-format stream-json --verbose` for Claude jobs and requires
   executed-model identity to be extracted from the per-turn assistant
   event's `message.model` field, explicitly prohibiting extraction from the
   final envelope's aggregate `modelUsage` map (and states why: a live probe
   found that map is not guaranteed single-entry).
7. **SPEC3-T06 — observed tool/MCP closure.** v3 requires D03 to prove tool
   and MCP-server closure by directly inspecting the stream-json
   initialization event's tool and server lists, and explicitly states that
   `--tools ""`/`--setting-sources ""` alone is not sufficient proof (a live
   probe found MCP servers still listed under `--setting-sources ""`).
   `ready: true` must be impossible on flag-only evidence for this class.
8. **SPEC3-T07 — no topology/reducer/retry/denominator/persistence/repair/
   terminal change.** Compare v3 and v2 structurally outside §0 (header/
   supersession), §2 (authority/historical narrative, retired-term
   neutralization only), §6.3/§7 (this correction's actual scope), §17.2/§19/
   §20.2 (new adversarial rows/traceability rows/prerequisite-status updates
   documenting this correction). Every other section — the node catalogue,
   edges/guards, checkpointing/resume, targeted repair, acceptance
   denominators, terminal design, filesystem layout, CLI contract, test
   layers — must be unchanged in substance from v2.
9. **SPEC3-T08 — honest resolution status.** v3 does not claim this
   correction was independently QA-verified by itself (that is this gate's
   job, not the artifact's own claim), does not claim user approval of v3,
   and does not claim or imply that Run 27 implementation may proceed. Any
   language describing prior live proof (e.g., the stream-json identity
   field, the MCP-listing finding) must attribute it honestly to the N20
   attempt or this correction's own live check, not assert it as an
   already-approved production guarantee beyond what was actually observed.

## Falsification targets

Specifically attempt to falsify each of these claims against the artifact
text:

- v3 does not merely rename "Gemini"/"Google" occurrences with a find/replace
  that breaks grammar, drops a prohibition's force, or accidentally weakens a
  MUST/MUST NOT into something softer.
- v3's corrected Claude invocation shape (§7.2) is internally consistent: the
  code block's flags match the prose explanation, and neither contradicts the
  stdin-delivery and stream-json-identity requirements stated elsewhere in
  the document (§7.1, §17.2, §19).
- v3 does not silently drop the `USER_DECISION_REQUIRED-01` resolution
  (Claude model/effort per job) that v2 recorded as resolved via the approved
  `spec_approval.v1.yaml`.
- v3 does not introduce a new provider, credential, endpoint, or fallback not
  present in v2's approved architecture.
- v3's new adversarial-test rows (§17.2) and traceability rows (§19) name
  concrete, checkable test IDs consistent with criteria 4–7, not vague
  aspirational language.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
nine numbered criteria above (a stated criterion fails on a realistic reading
of the artifact, not merely a stylistic quibble). Anything you notice that
does not defeat a numbered criterion belongs in observations, not findings.

## Where to spend your attention
Verify the nine SPEC3 criteria in the criteria file, especially SPEC3-T01 (zero literal gemini/google occurrences, stricter than v2), SPEC3-T02 (architecture unchanged from v2), and SPEC3-T03-T06 (the four transport-mechanics corrections: inline CLI-schema projection, stdin projection delivery, stream-json per-turn identity extraction, observed tool/MCP closure). Ground findings in the actual text of v3 and in a diff against v2 where relevant.

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