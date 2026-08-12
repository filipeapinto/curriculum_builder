# Plan 26 implementation prompt graph

This folder contains the implementation graph for
`spec/langgraph_curriculum_factory.spec.v1.md`.

The graph is a prompt-execution graph, not a replacement for the specified
LangGraph production runtime. Its nodes implement the specification in bounded,
dependency-aware units. Independent nodes may run concurrently; joins require
all declared predecessors; failures return to the owning node through explicit
rework edges.

Files:

- `implementation.graph.v3.yaml` — active node, edge, join, ownership, test-lane, and execution manifest.
- `deprecated/implementation.graph.v1.yaml` and `deprecated/implementation.graph.v2.yaml` — superseded graphs retained for audit.
- `prompts/*.prompt.vN.md` — one active implementation prompt per graph node; superseded versions are under `prompts/deprecated/`.
- `run.prompt.md` — validates and runs the prompt graph through Claude Sonnet.
- `prompt_graph_controller.py` — deterministic scheduler, cache, isolated-workspace launcher, verifier, and compact-receipt writer.
- `patches/*.patch.v1.yaml` — immutable prompt/context overlays and append-only revocations; base prompts are never rewritten.
- `prompt_patch.schema.v1.json` — immutable patch-record contract.
- `scheduler_receipt.schema.v2.json` — backward-compatible receipt contract with branch and patch provenance.
- `qa_criteria.v3.md` — active graph-wide implementation and product-proof criteria.
- `results/<node_id>.result.v1.md` — generated completion evidence.
- `results/v3/*.receipt.v1.json` — compact authoritative scheduler receipts; raw Markdown remains audit-only.

The implementation uses the exact LangGraph and SQLite-checkpointer contract in
the specification. It must not use LangChain chat-model wrappers, provider SDKs,
or direct model HTTP APIs. Model work remains through `codex exec` and `gemini`.

Run the commands in `run.prompt.md` to execute the graph. The controller uses
Claude Sonnet for implementation work and Python only for mechanical scheduling,
hashing, isolation, verification, and caching. The production system remains the
specified LangGraph runtime.

Version 2 closes the v1 sequencing gaps by requiring real N22/N23 callables
before N20 compilation and assigning D98 solely to N22 before N31/N32 execute.
It also assigns CI lock-drift enforcement to N10/N50 and runtime egress policing
to N13/N50. Superseded affected prompts are retained under `prompts/deprecated/`.

Version 3 preserves that topology while replacing LLM-administered scheduling
with deterministic execution. It adopts v2 passes only after focused verification,
isolates concurrent writers, caches by content, runs integration tests at joins,
and reserves the unchanged complete suite for N50 plus final receipt audit at N90.

## Safe prompt alteration and recovery

The active graph remains v3 because this is execution-harness plumbing, not a
node, edge, or production-state-schema change. Prompt alterations apply only
between attempts. The controller composes the base prompt with ordered immutable
patch records, binds them to the graph digest, and records base/effective prompt
and patch-chain hashes in each new attempt and receipt.

Every run and preflight creates a permanent local branch under
`.plan26-run/plan26/attempts/<node>/<attempt_id>/`. It contains the effective prompt,
baseline/start/final snapshots, retained repository, changed-file inventory,
outcomes, and pre-merge backups. A retry can fork that branch with
`run --node NODE --resume-attempt ATTEMPT_ID`; its parent is never modified.

Command logs are write-once and receive subprocess output while the command is
running. The append-only `results/v3/audit/events.v1.jsonl` records controller,
command, attempt, verification, merge, rollback, receipt, and patch lifecycle
events. Run `audit-anchor` once before resuming to hash-anchor all historical
receipts and logs. The read-only `postmortem` command reports the complete audit
inventory, including incomplete or interrupted attempts.

Create a reviewed overlay without rewriting its node prompt:

```sh
python3 plans/26_langgraph_curriculum_factory/prompt_graph_controller.py create-patch \
  --patch-id P-N50-001 --node N50_ADVERSARIAL_REGRESSION \
  --instructions-file /path/to/reviewed-instructions.md \
  --reason "trace-attributed finding" \
  --expected-effect "falsifiable expected result" --dry-run
```

Remove `--dry-run` only after reviewing the affected-node report. Never edit or
delete an issued patch; use `revoke-patch` to add an immutable rollback record.
