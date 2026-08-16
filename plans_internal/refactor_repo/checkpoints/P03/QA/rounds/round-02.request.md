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
- Round 1 (2026-08-16T19:53:26.187306+00:00): you returned FAIL with 1 finding(s) at threshold: Six relied-on deliverables lack the required immutable SHA-256 digest


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder_wt/p03-recovery/plans_internal/refactor_repo/checkpoints/P03/P03_recovery_checkpoint.v4.md
Version: round 2 of at most 5
SHA-256: cab7aceecf0ae62e0e7eafaefa97f959d68396b9cdf215c1485b03bf33744de1

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# Refactor checkpoint QA criteria v1

The gated checkpoint report must satisfy every condition below.

1. It identifies the executing prompt, the specification version, the baseline
   commit, the starting dirty state, and the exact artifact version being judged.
2. It lists every changed, created, moved, and deleted path and demonstrates that
   each change is within the prompt's authorized mutation boundary. Pre-existing
   user changes remain byte-for-byte outside the checkpoint delta.
3. It records every prompt TEST with its exact command or inspection procedure,
   exit status, material output, and a PASS or FAIL conclusion supported by that
   evidence. A skipped, unavailable, or inconclusive check is not PASS.
4. It demonstrates the prompt's prerequisites, explicit non-targets, stop
   conditions, and rollback procedure were honored. No successor prompt's mutation
   authority may be borrowed by the current checkpoint.
5. It identifies residual old identities, paths, imports, output consumers, schema
   references, or failures relevant to the prompt and classifies each as resolved,
   a recorded exception, pre-existing, or a blocker. Silent residuals are defects.
6. It includes the post-change git status and a reviewable diff or immutable digest
   for every deliverable, plus the verification result at the rollback checkpoint.
7. It does not claim completion when evidence is missing, collection is incomplete,
   commands failed, or the QA transport is unavailable. Completion additionally
   requires a witnessed and verified `QA_PASSED` result, which is established by the
   gate rather than asserted inside the artifact the gate is judging:

   7.1 The checkpoint submitted for review must identify itself as `QA_PENDING`.
   7.2 It must not claim completion and must not claim `QA_PASSED`. Asserting either
       inside the submitted checkpoint is itself a defect under this criterion.
   7.3 It must publish an immutable final digest (sha256) of the exact submitted
       checkpoint and of every deliverable it relies on. The independent QA gate
       evaluates that digest-identified checkpoint and nothing else.
   7.4 `QA_PASSED` is recorded only in a separate, gate-generated verdict and
       verification receipt produced by the sanctioned gate channel. The executing
       agent never writes that verdict, and no part of it is written into the
       submitted checkpoint.
   7.5 That external verified receipt, bound to the checkpoint's immutable digest,
       satisfies the completion gate on its own. Satisfying the completion gate must
       not require modifying, re-versioning, or re-submitting the reviewed checkpoint.
       A submitted checkpoint is therefore never required to contain the result of the
       review it is undergoing.
   7.6 Any post-verdict completion summary, commit message, ledger entry, or status
       report must reference the immutable checkpoint digest and the QA receipt, and
       must not replace, mutate, or supersede the reviewed artifact.

   Criterion 7 is not waived by this clarification. Independent QA remains mandatory,
   a checkpoint asserting completion before a witnessed verified `QA_PASSED` receipt
   exists is still defective, and a missing, unwitnessed, unverifiable, or
   digest-mismatched receipt still blocks completion.

---

Amendment provenance (2026-08-16): criteria 1-6 are unchanged from the original v1
text, whose sha256 is `bfd035a29b675df9718dc694a945ff1a4e901f2b3d8e653541a2b98b2cc48a42`
and whose literal content is preserved at
`plans_internal/refactor_repo/checkpoints/P03/evidence/criteria_amendment/checkpoint_qa_criteria.v1.PRE_AMENDMENT.md`.
Criterion 7 was clarified under explicit operator authorization after the P03 QA
session `01a00b6a-8a98-7e30-a456-d574b9f40355` terminated `QA_FAILED /
MAX_ITERATIONS_EXHAUSTED` and an independent postmortem session
(`01a00be9-9be1-7480-afc5-5ddc6cec54d1`) classified the failure
`SPECIFICATION_DEFICIENT`: the original wording required the artifact under review to
already contain the successful result of that same review, so every revision produced
a new unverified artifact and the gate could never converge. That postmortem is
preserved at
`plans_internal/refactor_repo/checkpoints/P03/superseded_sessions/QA-2026-08-16-exhausted/postmortem.md`.
Verdicts issued against the pre-amendment text (P00, P00A, P02S and the superseded P03
session) remain interpretable against the preserved pre-amendment file.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder_wt/p03-recovery/plans_internal/refactor_repo/prompts/P03_source_move.prompt.v3.yaml
- /Users/filipepinto/Projects/curriculum_builder_wt/p03-recovery/plans_internal/refactor_repo/checkpoints/P03/superseded_sessions/QA-2026-08-16-exhausted/postmortem.md

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
SESSION CONTEXT, disclosed in full. This is the third QA session for P03, and it runs on the exec transport because the app-server transport returned QA_ERROR twice with zero rounds completed. Session 1 (01a00b6a) terminated QA_FAILED/MAX_ITERATIONS_EXHAUSTED and its independent postmortem (grounded here) classified it SPECIFICATION_DEFICIENT because criterion 7 required the artifact under review to already contain the result of that same review; criterion 7 was then clarified into a gate-action form, sub-clauses 7.1-7.6, with criteria 1-6 byte-unchanged. Session 2 (01a00c05) ran 2 rounds; its round-2 verdict RETIRED both of its round-1 findings, and it was then retired deliberately for two configuration defects it could not escape: qa_gate.py fixes --focus at start so every round re-published superseded digests, and two of its grounding sources necessarily change between rounds so verify would always report GROUNDING_CHANGED. Both prior sessions and all their rounds are preserved under checkpoints/P03/superseded_sessions/ and are cited in the checkpoint's sections 1.1, 1.2 and 1.3. No finding from either session was discarded; treat this as a fresh, independent assessment and hold nothing back because an earlier session retired something. DIGEST BINDING: do not rely on this focus text for digests. Read plans_internal/refactor_repo/checkpoints/P03/evidence/checkpoint_digest.json, which is written after every other deliverable is frozen and publishes the sha256 of the submitted report and of evidence/digest_manifest.json; verify both by re-hashing those files yourself. Under clarified criterion 7 the submitted checkpoint MUST declare QA_PENDING and MUST NOT contain a QA_PASSED result: do not treat the absence of a passing verdict inside the artifact as a defect, and do not require the artifact to be revised in order to record your verdict. Your verdict is the separate receipt. WHERE TO SPEND ATTENTION: whether the literal evidence under plans_internal/refactor_repo/checkpoints/P03/ actually supports each PASS conclusion. Specifically (a) that the Test 2 pre-move inspection genuinely preceded the first move, checked against execution journal ordering ACT-039/040 before ACT-041/042 and against evidence/premove_inspection/; (b) that the re-executed move really is equivalent to the reviewed delta, per evidence/move_execution/; (c) that the 237-path ledger and the 230-file digest manifest are complete and accurate for the current worktree state, including the gate-owned QA/ and deprecated/ paths the checkpoint discloses in section 2.4; (d) that the 29 new-vs-t0 failures in t5_final_tree/ really are exactly the p04_handoff_allowlist with no P03-caused regression hidden among them; and (e) that the ownership adjudication in the resolved manifest's path_ownership_model actually covers all 19 overlaps the scan reports.

This narrows where you look. It does not lower the bar for what you find
there, and a blocker spotted outside this area is still a blocker.

## Severity threshold: blocker

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `blocker` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: 4a364e9d0052bd50e28cd52f1d9e03fa770f8eb75296ff75f174537c4e4cd603

Respond only in the required JSON shape.