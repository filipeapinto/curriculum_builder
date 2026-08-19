# Independent challenge and dispositions

Challenger: separate ephemeral `gpt-5.5`, xhigh session. Challenge receipt was generated from the frozen report, evidence matrix, benchmark summary/protocol, and all 180 receipts. Final acceptance authority remains human.

| ID | Severity | Disposition | Resolution |
|---|---|---|---|
| `CH-001` | blocker | **Rejected with evidence** | The challenger input omitted `full-protocol-approval.md`; that file records the human's repeated approval, selected route/model/auth/prices/ceilings/tool policy, and preflight requirement. The benchmark authorization stands. The omission is recorded as a challenge-input defect. |
| `CH-002` | blocker | **Accepted/corrected** | Claims are narrowed: application/server tools were disabled and observed web-tool use was zero, but Claude's internal structured-output machinery emitted `tool_use` and an auxiliary Haiku entry on one failed run. Single-model/no-tool operation is therefore not claimed. |
| `CH-003` | blocker | **Accepted/corrected** | Decision downgraded from constrained pilot to **defer adoption; research-only advisory experiments**. Representative artifacts, independent labels, and uncertainty estimates are prerequisites to any operational pilot. |
| `CH-004` | major | **Accepted/corrected** | Report now separates 42 live/provider receipts per condition from 18 controller simulations and publishes class denominators/outcomes. |
| `CH-005` | major | **Accepted/corrected** | Schema validity is no longer treated as semantic consistency. A future controller must enforce `PASS ⇒ findings=[]` and validate finding/criterion semantics before operational use. Existing state metrics are retained but qualified. |
| `CH-006` | major | **Accepted/corrected** | Digest/provenance state is declared controller-owned. Reviewer integrity objections cannot create a blocking finding without controller evidence. The observed unsupported digest objection remains counted as a false block. |
| `CH-007` | major | **Accepted/corrected** | Reliability language and pilot recommendation are withdrawn. Only invocation feasibility is established. |
| `CH-008` | major | **Accepted/corrected** | Deterministic tests, static analysis, rubric repair, human adjudication, panels, remote isolation, and external append-only logging are added as required alternatives for the next study. |
| `CH-009` | major | **Accepted/corrected** | Any current use is restricted to non-adversarial, non-authoritative research advice. High-consequence use requires separate execution identity and remote append-only receipts. |
| `CH-010` | major | **Accepted/corrected** | Cost is labeled client-estimated/incremental, not billing-grade. Price/auth/rate-limit revalidation is required before further live work. |
| `CH-011` | major | **Accepted/corrected** | Cross-condition ranking is qualified because system prompts, provider implementations, caching, tokenization, and structured-output mechanisms differ. Frozen corpus/schema were identical, but workload equivalence was not proven. |
| `CH-012` | major | **Accepted/corrected** | Evidence strength is downgraded where mutable external docs or cross-task research generalization is involved. The source register and retrieval date exist, but archived captures and item-level extracts do not. |

## Corrected terminal synthesis

The local Claude CLI route is technically feasible and can be made fail-closed at the controller boundary. The completed benchmark does **not** justify operational adoption or a high-consequence pilot. The appropriate decision is **defer**, while permitting non-authoritative research-only advisory experiments under the existing controls. Human acceptance of this corrected conclusion remains pending.
