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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc17/QA/exec/rc17_review_bundle.v1.md
Version: round 1 of at most 5
SHA-256: 73c403299355897adb81b0258d3e7fc7b5bdd9d5305709e7613e048a7fe43e44

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

# RC17 independent QA criteria

Report only blocker findings: each finding must name the criterion it defeats,
a reproducible trigger, and the consequence. Style and optional hardening are
observations.

1. Historical integrity: graph v8 retains SHA-256
   `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
   v9 retains distinct graph/contract/schema/prompt/result/state lineage.
2. Package coherence: every v9 package binding and digest recomputes, the real
   plan validator passes, and ownership remains exact and non-ambiguous.
3. Complete freeze: D02 binds every curriculum-owned domain input used by M02 or
   D08. Missing declarations, escape, duplicates, oversize, and byte drift fail
   before entry; the complete digest identifies the effective run.
4. Race-free staging: D08 must verify source bytes while copying them into a
   contract-and-candidate-addressed snapshot, preserve the required relative
   layout, reject staged conflicts, and execute only staged entry/dependency/
   fixture bytes plus the exact candidate.
5. Closed sandbox: the verifier runs outside the engine working directory under
   no-network, no-model-auth, no-model-scratch rules. It has neither byte nor
   metadata access to undeclared curriculum/engine files, including engine-root
   and ancestor-directory metadata; no engine metadata exemptions are permitted.
6. Replay invariance: any add/remove/rename/content change to undeclared repository
   paths and any post-D02 declared drift cannot change the same candidate/frozen
   contract verdict. Declared drift fails before execution; undeclared repository
   state is unobservable.
7. Bounded authoring: D07/M02 sees only admitted claims and verified staged inputs,
   with no admission or verifier authority.
8. Repair/replay: invalid first candidates stay immutable/non-head; repairs target
   exact bytes, remain bounded, preserve lineage, and revalidate exact repaired
   heads. D08/D09/D12/D20 physical admission and cross-node replay remain correct.
9. Regression proof: focused, package, and full-runtime suites pass, including six
   RC13 triggers and the RC14–RC16 byte/direct-metadata/ancestor-metadata attacks.
10. Security/architecture preservation: exact-host retrieval, SSRF/redirect checks,
    tool-closed subscription CLIs, model assignments, topology, terminals, and
    no-billed-API/no-provider-SDK constraints remain intact.
11. Entry safety: no blocker may make a fresh graph-v9 N00→N90 cascade dishonest,
    unverifiable, or unable to execute the real N70/N80 path.

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

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Reproduce RC14 byte drift, RC15 direct metadata, and RC16 ancestor-directory metadata attacks against the staged frozen snapshot. Verify the verifier executes only staged bytes outside the engine with no engine metadata exemption, then assess fresh graph-v9 N00-to-N90 entry safety. Report only genuine blockers.

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