# GOAL

Prove that Run 27's v2 execution package has one corrected, independently
verified, explicitly user-approved specification authority before any
implementation begins. This is the v2-package counterpart of
`N00_spec_approval_gate.prompt.v1.md`, which gated the v1 attempt through its
`BLOCKED` `N20_PROVIDER_TRANSPORT` result. That v1 attempt, and its N00/N10/N20
results and evidence, remain untouched, immutable, and readable as historical
record — this node does not supersede them in place, it gates a new package.

This node is a gate, not a specification-writing or graph-writing task. Do not
create, edit, approve, or repair the v3 specification, the v2 execution graph,
QA evidence, approval record, runtime, tests, policy, or any Plan 26/Run 27 v1
historical artifact. Its only authorized writes are its own result and
evidence directory under `results/v2/`.

# TEST

1. Hash Plan 26 v1
   (`44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`) and v2
   (`99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`) and
   require both to still match; neither is edited by this or any prior
   correction task.
2. Require the v3 specification
   (`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`
   — physically named `.v4.md` by the QA gate's own round-lineage numbering
   after a round-1 fix; the document is specification v3 and its own
   header says so)
   and its correction result to exist and to name it as correcting v2 at the
   exact hash above, not v1.
3. Read the v3 correction result's exact QA session, verdict, verification
   path, and hashes. Require witnessed, hash-chain-valid `QA_PASSED`; prose
   asserting that QA ran is not evidence.
4. Require the v2 execution package's own QA result (execution-package
   correctness, not the specification) to exist with the same witnessed,
   hash-chain-valid `QA_PASSED` discipline.
5. Require `implementation.graph.v2.yaml` to exist, to validate via
   `tools/validate_plan.py --graph plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml`,
   and to declare `source_spec` as the v3 specification path above.
6. Validate a new
   `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v2.yaml`
   against `schemas/spec_approval.schema.v1.json` with format checking
   enabled. (The schema itself is frozen and unversioned per
   `rules.frozen_before_entry`; only the approval record is new.)
7. Recompute digests and require exact equality across: the v3 specification
   file, the v3 correction result, the v3 QA verification artifact hash, the
   v2 execution graph file, the v2 execution-package QA verification artifact
   hash, and the four corresponding hashes bound inside
   `spec_approval.v2.yaml`.
8. Require the approval record to authorize `plan27_implementation_remediation`
   and to carry the exact Claude model/effort decision already supplied by
   the user for `USER_DECISION_REQUIRED-01`, unchanged from
   `spec_approval.v1.yaml`'s `approval_statement`.
9. Enumerate every `USER_DECISION_REQUIRED` item in v3. If any affects a
   node's intended implementation and lacks a separately recorded answer,
   block.
10. Prove no Run 27 v1 result, evidence file, receipt, patch, log, the v1
    execution graph, runtime, test, policy, or model-job file was changed by
    this node.
11. Record command output and hashes under
    `results/v2/evidence/N00_SPEC_APPROVAL_GATE/` and emit a JSON result
    conforming to
    `plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json`.

The only success outcome is `PASSED`. Missing, inconsistent, unverifiable, or
unapproved inputs produce `BLOCKED_SPEC_NOT_APPROVED`. An integrity or tool
defect produces `BLOCKED`.

# LOOP

Do not repair a failed approval gate. Re-run read-only checks once to rule out
a transient read error. If the same condition remains, write the honest
result and stop the graph. Never infer user approval from the existence of
this package's scaffold, from a prior agent's report of passing digests, or
from a request to prepare this package — approval binds the exact digests
recorded in `spec_approval.v2.yaml`, supplied by the user after seeing them,
not before.
