# GOAL

Prove that Run 27 has one corrected, independently verified, explicitly
user-approved specification authority before any implementation begins.

This node is a gate, not a specification-writing task. Do not create, edit,
approve, or repair the v2 specification, QA evidence, approval record, runtime,
tests, policy, or any Plan 26 historical artifact. Its only authorized writes
are its own result and evidence directory.

# TEST

1. Hash Plan 26 v1 and require exactly
   `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`.
2. Require the v2 specification and specification-correction result named by
   the Run 26 correction workflow.
3. Read the correction result's exact QA session, verdict, verification path,
   and hashes. Require witnessed, hash-chain-valid `QA_PASSED`; prose asserting
   that QA ran is not evidence.
4. Validate
   `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`
   against
   `plans/27_langgraph_curriculum_factory_remediation/schemas/spec_approval.schema.v1.json`
   with format checking enabled.
5. Recompute the v2 digest and require equality across the file, correction
   result, QA verification, and approval record.
6. Require the approval to authorize `plan27_implementation_remediation`.
7. Enumerate every `USER_DECISION_REQUIRED` item in v2. If any affects a node's
   intended implementation and lacks a separately recorded answer, block.
8. Prove no Run 26 v1 spec, result, receipt, patch, log, implementation graph,
   runtime, test, policy, or model-job file was changed by this node.
9. Record command output and hashes under
   `results/evidence/N00_SPEC_APPROVAL_GATE/` and emit a JSON result conforming
   to
   `plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json`.

The only success outcome is `PASSED`. Missing, inconsistent, unverifiable, or
unapproved inputs produce `BLOCKED_SPEC_NOT_APPROVED`. An integrity or tool
defect produces `BLOCKED`.

# LOOP

Do not repair a failed approval gate. Re-run read-only checks once to rule out a
transient read error. If the same condition remains, write the honest result and
stop the graph. Never infer user approval from the existence of this Run 27
folder or from a request to scaffold it.
