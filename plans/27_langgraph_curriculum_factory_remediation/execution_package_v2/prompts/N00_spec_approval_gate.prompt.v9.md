# GOAL

Recovery authority: `plans/26_langgraph_curriculum_factory/prompts/RUN27_GPT56_SOL_AUTONOMOUS_V8_RECOVERY_TO_N90.prompt.v1.md` requires autonomous live-descendant repair, affected-admission cascade, and retry through N90. Approved graph v8 is immutable at SHA-256 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`; its N00-N60 admissions and five failed N70 attempts remain historical. All fresh admissions after the attempt-5 ownership correction use graph v9 and `results/v9/`.

Prove that execution package v2 has one corrected, independently verified,
explicitly user-approved specification authority before any implementation
begins. This is package v2's counterpart of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N00_spec_approval_gate.prompt.v1.md`,
which gated the v1 attempt through its `BLOCKED` `N20_PROVIDER_TRANSPORT`
result, and of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N00_spec_approval_gate.prompt.v2.md`,
which gated the first, failed execution-package correction
(`implementation.graph.v2.yaml`, preserved immutable together with its QA
session and `PKG-QA-001` finding). Those v1 and v2 results and evidence
remain untouched, immutable, and readable as historical record — this node
does not supersede them in place, it gates a new, independent package.

This v9 live-defect recovery prompt succeeds `N00_spec_approval_gate.prompt.v8.md` after a genuine N70 execution exposed incomplete domain-contract freezing, surrogate verifier trust, missing invalid-v1 repair lineage, and missing physical artifact-store admission. It also preserves the earlier v6 correction, which was
itself a correct fix for N20V2-F01 (its own graph, `implementation.graph.v6.yaml`,
genuinely narrowed `retired_provider_test_scan.scan_roots` to the explicit
migration-owned union and dropped the two unrelated Gemini-pipeline test
files from N20's write set) but whose own graph carried an unrelated,
independently-found result-namespace defect: `implementation.graph.v6.yaml`'s
`result_pattern` was byte-identical to `implementation.graph.v5.yaml`'s own
(`execution_package_v2/results/{node_id}.result.v1.json`). Because N00 and
N10 are already ADMITTED (`PASSED`) with real results at
`execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json` and
`execution_package_v2/results/N10_HARNESS_PROTOCOL.result.v1.json`, and N20 is
already `BLOCKED` with real evidence at
`execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json`, a fresh
execution of any of these three nodes under graph v6 as originally built
would have validated against v6's own newer prompt/schema hashes and then
silently overwritten those exact same three historical files at their shared
path — violating this recovery lineage's repeated, explicit "preserve prior
attempts, never overwrite an admitted or blocked record" requirement. This is
a mechanical result-namespace engineering defect in the graph's own
`result_pattern` and every node's own result/evidence write paths, not a
specification or provider decision, and not a defect in N20's real,
independently-verified production implementation (preserved untouched). It is
fixed here: this prompt validates against this package's own package-scoped
`execution_package_v2/schemas/spec_approval.schema.v6.json` (which
const-locks the right specification and this package's own active graph, now
`implementation.graph.v9.yaml`, instead of v6), the corresponding
`execution_package_v2/contracts/spec_approval.v6.yaml` (which carries
forward, not reinvents, the exact approval already recorded in
`spec_approval.v3.yaml`, updated only for the new graph's path/digest and
schema version), and `implementation.graph.v9.yaml` genuinely declares schema
v4 in its own `rules.frozen_before_entry`, moves `result_pattern` and every
node's own result/evidence write paths under the versioned subdirectory
`execution_package_v2/results/v9/` (whose per-node filenames never coincide
with the flat per-node files directly under `execution_package_v2/results/`,
where the admitted/blocked N00/N10/N20 records permanently live), and
otherwise carries the N20V2-F01 scan-scope fix forward unchanged. The v6 prompt file, `spec_approval.schema.v3.json`,
`spec_approval.v3.yaml`, and `implementation.graph.v6.yaml` (preserved at
`deprecated/implementation.graph.v6.yaml`) are preserved unchanged as
historical record — this node does not reopen, edit, or supersede any of
them, `implementation.graph.v5.yaml` (at `deprecated/`), `spec_approval.schema.v2.json`,
`spec_approval.v2.yaml`, `N00_spec_approval_gate.prompt.v5.md`, or rc1-rc7
in place.

This node is a gate, not a specification-writing or graph-writing task. Do
not create, edit, approve, or repair the v4 specification artifact, this
package's own graph, QA evidence, an approval record, runtime, tests,
policy, or any Plan 26/Run 27 v1 or failed-v2 historical artifact. Its only
authorized writes are its own result and evidence directory under
`execution_package_v2/results/v9/`.

# TEST

1. Hash Plan 26 v1
   (`44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`) and
   v2 (`99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`)
   and require both to still match; neither is edited by this or any prior
   correction task.
2. Require the specification artifact
   `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`
   (sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`
   — physically named `.v4.md` by the QA gate's own round-lineage numbering
   after a round-1 fix; the document is specification v3 and its own header
   says so) to exist and to correct v2 at the exact hash above, not v1.
3. Read that specification's own independent QA session
   (`plans/26_langgraph_curriculum_factory/spec/v3/QA/`, session
   `019ffbeb-3f45-7440-a83e-aa560938dc98`). Require witnessed,
   hash-chain-valid `QA_PASSED` by re-running the QA gate's own `verify`
   command read-only; prose asserting that QA ran is not evidence.
4. Require the approved release candidate's own QA result
   (`execution_package_v2/release_candidate/rc3/QA/`) to exist with the same
   witnessed, hash-chain-valid `QA_PASSED` discipline, verified the same way.
5. Require `execution_package_v2/implementation.graph.v9.yaml` to exist, to
   declare `version: 2`, to validate via
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`,
   and to declare `source_spec` as the specification path above.
6. Validate `execution_package_v2/contracts/spec_approval.v6.yaml` against
   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v6.json`
   with format checking enabled. This schema is *this package's own* frozen
   schema: it is declared in `implementation.graph.v9.yaml`'s own
   `rules.frozen_before_entry` (alongside `node_result.schema.v1.json`) —
   verify that declaration directly in the live graph file rather than
   trusting this prompt's own account of it. It is not the parent v1
   package's `spec_approval.schema.v1.json`, which remains that package's
   own frozen contract, exclusively, and is never loaded here.
7. Recompute digests and require exact equality across every value schema v6
   requires as a structured field, against live repository bytes: the
   specification file (`approved_spec_sha256`), its QA verification artifact
   hash (`spec_qa_verification_sha256`), the approved release candidate's
   manifest at the path `approved_rc_manifest` names
   (`approved_rc_manifest_sha256`), that release candidate's own QA
   verification artifact hash (`execution_package_qa_verification_sha256`),
   and this package's graph file at the path `approved_graph` names
   (`approved_graph_sha256`). A mismatch on any one of these is not a schema
   *shape* failure (JSON Schema cannot hash a file) — it is a validator-level
   integrity failure and must block exactly as a shape failure would.
8. Require the approval record's `approved_for` to equal
   `plan27_implementation_remediation` and its `model_assignments` to carry
   the exact Claude/Codex model and effort decision already supplied by the
   user for `USER_DECISION_REQUIRED-01`, unchanged from
   `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`'s
   `approval_statement`: `M01_RESEARCH_UNIT_SOURCES`,
   `M06_REPAIR_NAMED_UNIT_ARTIFACT`, and `M08_REPAIR_NAMED_WORKBOOK_DEFECT` =
   `claude-sonnet-5` at effort `xhigh`; `M02_CREATE_UNIT_DOMAIN_DATA`,
   `M03_WRITE_UNIT_CONTENT`, and `M04_CREATE_UNIT_VISUALS` = `claude-sonnet-5`
   at effort `high`; `M05_REVIEW_ACTUAL_UNIT` and `M07_REVIEW_ACTUAL_WORKBOOK`
   = `gpt-5.6-sol` at effort `xhigh`.
9. Enumerate every `USER_DECISION_REQUIRED` item in the specification. If
   any affects a node's intended implementation and lacks a separately
   recorded answer, block.
10. Prove no Run 27 v1 result, evidence file, receipt, patch, log, the v1
    execution graph, the failed `implementation.graph.v2.yaml` and its QA
    session, `implementation.graph.v5.yaml` (now preserved at
    `deprecated/implementation.graph.v5.yaml`), `implementation.graph.v6.yaml`
    (now preserved at `deprecated/implementation.graph.v6.yaml`),
    `spec_approval.schema.v1.json`, `spec_approval.v1.yaml`,
    `spec_approval.schema.v2.json`, `spec_approval.v2.yaml`,
    `spec_approval.schema.v3.json`, `spec_approval.v3.yaml`,
    `N00_spec_approval_gate.prompt.v5.md`, `N00_spec_approval_gate.prompt.v6.md`,
    rc1, rc2, rc3, rc4, rc5, rc6, rc7 (including each one's `QA/` session),
    `N20_PROVIDER_TRANSPORT`'s `BLOCKED` result and evidence under
    `implementation.graph.v5.yaml`, runtime, test, policy, or model-job file
    was changed by this node.
11. Record command output and hashes under
    `execution_package_v2/results/v9/evidence/N00_SPEC_APPROVAL_GATE/` and
    emit a JSON result conforming to
    `plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json`.

The only success outcome is `PASSED`. Missing, inconsistent, unverifiable, or
unapproved inputs produce `BLOCKED_SPEC_NOT_APPROVED`. An integrity or tool
defect produces `BLOCKED`.

# LOOP

Do not repair a failed approval gate. Re-run read-only checks once to rule
out a transient read error. If the same condition remains, write the honest
result and stop the graph. Never infer user approval from the existence of
this package's scaffold, from a prior agent's report of passing digests, or
from a request to prepare this package — approval binds the exact digests
recorded in the approval record, supplied by the user after seeing them, not
before.
