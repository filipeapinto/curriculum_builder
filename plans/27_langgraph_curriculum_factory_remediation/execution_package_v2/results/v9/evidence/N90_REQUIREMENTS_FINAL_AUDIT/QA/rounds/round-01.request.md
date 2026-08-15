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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/evidence/N90_REQUIREMENTS_FINAL_AUDIT/QA/exec/N90_final_audit.v1.md
Version: round 1 of at most 3
SHA-256: 3f6633d0e3f853029ba3e586e5acfbd7fac950660c26c51b6a7222e22c3721d2

Read the file at that path. If it references other files needed to judge it,
read those too.

## You can run this, and you should

Your working directory is writable and holds a copy of the artifact and
the files beside it. Run the thing. Write a harness, execute it, probe the
edges, try the inputs you suspect. Nothing here is the real artifact, so
you cannot break anything that matters.

This is worth the effort because reading code and running it disagree more
often than reviewers expect — the defects that survive a careful read are
exactly the ones execution catches. A finding you have reproduced is worth
more than one you have inferred, so put what you observed in `evidence`:
the input, the output you got, the output the criteria required.

It cuts the other way too. If you suspected something, tested it, and it
held up, do not raise it — say so in `reasoning` instead. A suspicion that
survived a test is not a finding.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

# Run 27 N90 independent final-audit criteria

The artifact passes only if all observable conditions below hold. A preference or possible future enhancement is not a blocker.

1. It starts authority at the current user-approved corrected specification SHA-256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`, then covers retained Plans 20–22/product requirements, implementation, tests, and product evidence without treating historical files as current authority.
2. It accounts for every PM-01 through PM-24 identifier, including identifiers consolidated by postmortem v2, and every CA-01 through CA-12; no item disappears and activation-only unavailability remains open rather than misreported resolved.
3. Its N00–N80 outcomes and result SHA-256 values equal the grounded V9 results. N00–N60 must be PASSED; N70 and N80 must be NOT_AVAILABLE. It must not claim UNIT_ACCEPTED, COMPLETE, or live product bytes.
4. It identifies the implemented provider map as Claude/Anthropic for M01–M04/M06/M08 and Codex/OpenAI for M05/M07, subscription CLI only, with no fallback/API-key/direct-model-HTTP activation.
5. It reports the witnessed independent RC29 qa-gate result only if state is QA_PASSED, reason CONVERGED, chain_valid true, problems empty, and the stated session/chain identifiers match grounded verification/session files.
6. It reports the final regression denominator accurately: runtime 1370 passed, 2 explicitly classified unrelated skips, 419 subtests; Run 27 package 83 passed; whole-tree scan 67 files and zero violations; ownership 75/75; evidence determinism 2/2; requirements lineage 8/8.
7. It separates exactly three conclusions: specification authority, implementation conformance, and product activation. Implementation may pass while activation remains unavailable.
8. It recommends exactly `REMEDIATION_VERIFIED_NOT_ACTIVATED`. `ACTIVATED` would be false because N70/N80 are not PASSED; `BLOCKED` would be false absent an implementation/integrity/evidence/convergence defect.
9. It does not waive the Claude availability blocker, recommend credentials/provider substitution, or use Plan 26/v8 history as provider-correctness or activation proof.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v9.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc29/QA/verification.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc29/QA/session.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N00_SPEC_APPROVAL_GATE.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N10_HARNESS_PROTOCOL.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N20_PROVIDER_TRANSPORT.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N30_PREFLIGHT_EGRESS.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N40_INTEGRATION_OWNERSHIP.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N50_EVIDENCE_AUDIT_CONTROLS.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N60_ADVERSARIAL_REGRESSION.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N70_LIVE_UNIT_PROOF.result.v1.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v9/N80_LIVE_WORKBOOK_PROOF.result.v1.json

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Independent blocker-level verification of the N90 authority, receipt, PM/CA, live-unavailability, and sole-terminal claims. Execute grounded validators where useful; do not request product activation when the grounded live results are NOT_AVAILABLE.

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
Echo nothing; this is for the record only: GENESIS

Respond only in the required JSON shape.