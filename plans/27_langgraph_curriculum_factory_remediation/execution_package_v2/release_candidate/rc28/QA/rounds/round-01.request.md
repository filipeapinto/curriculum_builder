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
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc28/QA/exec/rc28_review_bundle.v1.md
Version: round 1 of at most 5
SHA-256: 93c1c0828e1b5aa4b806fa5f83d9bacf524789447636d5c66af98ef308588301

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

# RC28 independent correctness criteria

Complete every check before verdict. Report only release-blocking correctness findings
with a defeated criterion, reproducible trigger, consequence, and observed evidence.

1. Recompute all five authority hashes; preserve V8 history and distinct V9 state and
   result lineage; validate the plan, ownership contract, and complete-tree scan.
2. Run the active Arduino D01→D02 case and every named invalid-source regression. The
   active case must compile; every invalid case must stop before verifier execution.
3. Inspect equivalent aliases and module exports. The closed allowed module set must
   not grant code, native, process, network, OS, or mutable package authority.
4. Confirm every verifier fixture is re-hashed and schema-valid at D02, the candidate
   is validated from the same frozen schema bytes at D08, and declared-byte drift or
   staging races fail closed.
5. Run chdir/utime/mkfifo/lchmod invariance, candidate immutability, declared drift,
   external staging, staged conflict, and mutable parent-site-package tests.
6. Confirm the child uses `-I -S` without `PYTHONPATH` or package-directory grants;
   its receipt must bind the interpreter and every file-backed runtime module and
   refuse package, unstaged-engine, missing, changed, or malformed module records.
7. Confirm unchanged repository bytes/metadata cannot change the same candidate and
   frozen contract result, while changed declared or evaluated bytes stop execution.
8. Run immutable-failure, bounded-repair, exact-lineage, ArtifactStore, and
   D08/D09/D12/D20 replay/idempotence regressions.
9. Confirm exact-host retrieval/redirect rules, subscription CLI routes, model
   assignments, topology, and terminal outcomes match the governing specification.
10. Confirm package/focused and full-runtime suites plus the current Plan 26 N13
    receipt; then prove fresh isolated graph-v9 state supports genuine N00→N90 through
    the N70 and N80 product gates.

## Grounding sources
Absolute paths; read whichever of these bear on the criteria above.

- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v9.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v6.json
- /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/contracts/spec_approval.v6.yaml
- /Users/filipepinto/Projects/curriculum_builder/plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md

These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.


## Where to spend your attention
Validate the final-byte D02/D08 contract and the two RC27 attack classes. Execute the exact adversarial regressions, inspect equivalent bypasses and evaluated-byte receipts, verify lineage/plan/ownership, and complete every criterion before verdict.

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