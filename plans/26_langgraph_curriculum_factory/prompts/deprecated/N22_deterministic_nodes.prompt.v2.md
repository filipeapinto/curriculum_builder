# GOAL

Implement `N22_DETERMINISTIC_NODES` after N11/N12. Implement every deterministic
node D00–D98 as a real bounded callable, including sole ownership of D98 terminal
validation/writing in `runtime/langgraph_factory/terminal.py`.

Each node enforces its exact projection, typed update, reducer authority,
failure class, and outgoing-guard inputs. Adapt Plan 25 deterministic product
logic without orchestration loops. D98 accepts only a deterministic terminal
candidate and supporting current evidence; unit and workbook graph nodes may
feed D98 but may not implement or bypass it.

# TEST

1. Exactly one real implementation per D node; D98 and terminal module have N22 as sole owner.
2. Projection/update fields equal the frozen catalogue.
3. Expected failures are typed; unexpected failures route system failure.
4. Manifest closure/order is neutral for 1, 7, and 41-unit DAGs.
5. Retrieval/admission/check/render/page/evidence paths fail closed on stale inputs.
6. Repair plans are one-owner/one-boundary with descendants/retests/bounds.
7. D22/D32 cannot propose success without complete denominators; D98 independently
   rejects invalid unit, workbook, failure, pause, interrupt, or success candidates.
8. D98 writes exactly one episode terminal and is the only node connected to END.
9. Static scan finds no curriculum constants or second terminal writer.

Write `results/N22_DETERMINISTIC_NODES.result.v1.md` with node ownership,
D98 truth table, adapter disposition, commands, and hashes.

# LOOP

Patch one deterministic callable, adapter, or terminal guard. Rerun catalogue,
authority, D98 truth-table, and sole-writer tests. Stop if another graph node must
own terminal.py or any adapter retains orchestration authority.
