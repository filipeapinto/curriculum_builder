# Run 27 contracts

This directory intentionally does not contain `spec_approval.v1.yaml` yet.

After the corrected Plan 26 v2 specification has a witnessed, hash-chain-valid
independent `QA_PASSED` result, explicit user approval may be recorded at:

`plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`

The record must conform to `../schemas/spec_approval.schema.v1.json`, bind the
exact approved v2 and QA-verification digests, and authorize
`plan27_implementation_remediation`. An agent must not synthesize this record
from the existence of the Run 27 scaffold.

N40 and N50 may add versioned ownership and requirements-lineage contracts here
after N00 admits the approval and their predecessor nodes pass.
