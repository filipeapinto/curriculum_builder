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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc19/QA/exec/rc19_review_bundle.v1.md
Version: round 1 of at most 5
SHA-256: 200c434a43aa2f1a68da635948b69be2409cd36e78905305c137acdaf9ca7348

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

# RC19 independent QA criteria

Report only blocker findings, each naming the defeated criterion, reproducible
trigger, and consequence. A PASS is valid only after every required probe finishes;
reasoning that says review or probes remain underway is not a completed verdict.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 retains separate graph/contract/schema/prompt/result/state lineage.
2. Package coherence/ownership: active bindings and digests recompute; the real
   plan validator and exact ownership verifier pass.
3. Complete freeze: D02 binds every curriculum-owned input used by M02/D08;
   missing declarations, escape, duplicates, oversize, and drift fail pre-entry.
4. External race-free staging: for engine-nested production N70 output, the work
   root resolves outside engine and output roots. D08 verifies bytes during staging,
   preserves declared layout, rejects conflicts, and executes only staged frozen
   entry/dependency/fixture bytes plus the exact candidate.
5. Closed sandbox: cwd/staged files are external; no network/model-auth/model-scratch
   rules; no undeclared engine byte or metadata visibility, including file and
   directory/ancestor metadata; no engine metadata exemptions.
6. Replay invariance: declared drift fails before execution; undeclared repository
   add/remove/rename/content/metadata changes cannot alter the same candidate and
   frozen-contract verdict.
7. Bounded authoring/recovery: M02 has no verifier/admission authority; invalid first
   versions stay immutable/non-head; repair is exact, bounded, lineage-preserving,
   and exact-head revalidated.
8. Physical replay: D08/D09/D12/D20 persist canonical bytes before reads, replay
   idempotently, fail conflicts closed, and preserve repaired heads.
9. Regression proof: package, focused, and full-runtime suites pass, including all
   RC13 and RC14–RC17 attacks.
10. Security/architecture: exact-host retrieval, SSRF/redirect checks, tool-closed
    subscription CLIs, model assignments, topology, terminals, and no-billed-API/
    no-provider-SDK constraints remain intact.
11. Entry safety: a fresh graph-v9 N00→N90 cascade through real N70/N80 is honest,
    verifiable, and executable.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v9.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v6.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/contracts/spec_approval.v6.yaml
- /Users/filipepinto/Projects/curriculum_builder/schemas/curriculum.schema.v5.json
- /Users/filipepinto/Projects/curriculum_builder/curricula/arduino_kit/arduino_kit_curriculum.v5.yaml
- /Users/filipepinto/Projects/curriculum_builder/curricula/arduino_kit/verify_domain.py
- /Users/filipepinto/Projects/curriculum_builder/curricula/arduino_kit/domain.schema.v1.json
- /Users/filipepinto/Projects/curriculum_builder/curricula/arduino_kit/kit_calibration.v1.yaml
- /Users/filipepinto/Projects/curriculum_builder/curricula/arduino_kit/circuit_library.v1.yaml
- /Users/filipepinto/Projects/curriculum_builder/runtime/langgraph_factory/nodes/inputs.py
- /Users/filipepinto/Projects/curriculum_builder/runtime/langgraph_factory/transport.py
- /Users/filipepinto/Projects/curriculum_builder/tests/runtime/test_plan26_deterministic_nodes.py
- /Users/filipepinto/Projects/curriculum_builder/tests/runtime/test_plan26_transport.py
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc14/QA/rounds/round-01.response.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc15/QA/rounds/round-01.response.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc16/QA/rounds/round-01.response.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc17/QA/rounds/round-01.response.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc18/QA/rounds/round-01.response.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc18/QA/postmortem.md

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Complete every probe before verdict. Reproduce RC14-RC17 attacks against the prescribed engine-nested N70 output, verify the external work root and staged-byte race checks, inspect emitted sandbox rules for zero engine metadata exemptions, and assess honest fresh graph-v9 N00-to-N90 entry. Report only genuine blockers.

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