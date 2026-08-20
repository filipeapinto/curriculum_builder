# SOTA research-plan contract

This reference specializes the mandatory `../../sota-plan-execute/references/sota-family-contract.md`. The family contract prevails; plans may only strengthen it.

A plan must define:

1. Primary research question and intended decision.
2. Scope, exclusions, assumptions, and evidence boundary.
3. Preliminary study or other calibration step when evidence volume or method is uncertain.
4. Research method, searches, eligibility, appraisal, extraction, synthesis, and challenge.
5. Dependency flow showing order, parallelism, feedback, and approval gates.
6. Data flow showing inputs, roles, evidence products, transfers, and controls.
7. Roles and separation of deterministic work, model judgment, independent challenge, and human authority. Assign every non-human role to its installed SOTA role skill and embed that role's inputs, outputs, responsibilities, and authority boundary.
8. The actual model/tool/human allocation selected using `research-model-allocation-policy.v1.yaml`, plus approved deviations and their reasons. Execution must not require the policy file.
9. A workload-derived budget. For every numeric ceiling include derivation, confidence, measurement mechanism, warning threshold, hard stop, and behavior when measurement is unavailable.
10. Required outputs, provenance, verification, acceptance criteria, and human approval state.
11. Textual equivalents for diagrams when their meaning is not fully present in surrounding prose or tables.
12. Version, predecessor, date, status, and a concise version note.
13. The originating issue or accepted report, plus the synchronized issue/report version when planning discovered material new scope.

The plan must distinguish proposed actions from completed work and attributed claims from verified evidence. It must not imply that plan approval occurred unless the human owner explicitly granted it.

The approved plan must be the sole execution contract. Supporting research artifacts may provide evidence or history, but they must not contain instructions that the executor needs in order to run the plan.

Every version must be standalone. It must restate the complete current contract and remain usable when prior versions cannot be opened. A version note may summarize changes, but a diff, “unchanged from vN,” or a predecessor link cannot carry operative content.

Planning may refine a remedy, but it must not silently expand the issue. A newly proposed skill, artifact, method, control, risk, acceptance criterion, or authority boundary that materially changes remediation scope requires a preserved, self-contained update to the originating issue or issue-confirmation report before the plan is issued. Label planning discoveries as such; do not promote them to verified defects without evidence.
