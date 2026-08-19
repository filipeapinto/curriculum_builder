# Controlled vocabulary and threat map

| Term | Frozen calibration definition |
|---|---|
| Process independence | Reviewer executes in a distinct OS process or service invocation from the producer/controller. |
| Context independence | Reviewer receives only the frozen artifact, criteria, grounding, schema, and protocol prompt—not producer chain-of-thought, private history, or mutable working context. |
| Model-family diversity | Producer and reviewer use materially different model families; this is rated separately from vendor diversity. |
| Vendor diversity | Producer and reviewer are served by different model vendors. It does not prove uncorrelated errors or host integrity. |
| Host integrity | Confidence that the producer cannot alter reviewer inputs, outputs, witnesses, or controller state. A shared user account provides weak host integrity. |
| Authority | The component permitted to emit a gate result. The reviewer proposes a verdict; only the controller validates and records terminal state; only the human accepts the research recommendation. |
| Witness | Evidence external to the mutable verdict body that binds process/session/turn, request, response, model/settings, and artifact digest. |
| Fail closed | Unavailable, malformed, timed-out, over-budget, or unverifiable review becomes `QA_ERROR`, never PASS. |
| Prompt independence | Reviewer system/task prompt is frozen and digest-bound, and is not adaptively softened by the artifact producer. |

## Threat hypotheses

| Threat ID | Hypothesis | Required control/test |
|---|---|---|
| `TH-001` | Repository text can inject instructions through auto-loaded files. | Use `--bare`/safe isolated invocation, explicit prompt and tools, synthetic injection cases. |
| `TH-002` | Reviewer can mutate the authoritative artifact or verdict ledger. | Frozen copy, read-only/no tools, separate controller-owned append-only receipts. |
| `TH-003` | Vendor diversity is mistaken for independent correctness. | Score process, context, model family, vendor, and host integrity separately; measure correlated failures. |
| `TH-004` | Shared auth/session state leaks prior context. | New explicit session ID, no persistence, bare mode, record effective settings; never resume across cases. |
| `TH-005` | Schema-valid output is semantically ungrounded. | Require criterion IDs, evidence locations, digest binding, traps, and human reference labels. |
| `TH-006` | CLI success exit masks auth or internal-run failure. | Validate result subtype, schema, usage, session witness, stderr, and documented failure modes. |
| `TH-007` | Cost/timeout cannot be measured or terminated. | Provider usage fields, controller monotonic timeout, process-tree termination, hard cost ceilings. |
| `TH-008` | Same-host producer can forge local witnesses. | State limitation explicitly; evaluate remote append-only receipt/signing for higher assurance. |
| `TH-009` | Human labels or seeded corpus privilege one reviewer. | Blinded conditions, dual adjudication sample, fixed labels before calls, disagreement record. |
| `TH-010` | Version drift invalidates the adopted route. | Exact CLI/model/version capture and defined revalidation triggers. |

No unresolved terminology changes an eligibility rule. The distinction between process, context, model-family, vendor, and host independence is mandatory in every later comparison.
