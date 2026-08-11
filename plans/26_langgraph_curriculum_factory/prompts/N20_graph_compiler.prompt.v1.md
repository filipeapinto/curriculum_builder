# GOAL

Implement `N20_GRAPH_COMPILER` after N10 and N11 pass. Build the single root
`StateGraph` and compile it once as `plan26_curriculum_factory` with the exact
D00–D98/M01–M08 catalogue and section 8 edges/guards.

Use typed state/reducers, `START`, `END`, conditional edges, explicit product
loops, and `Send` only for denominator-first map work. Do not use subgraphs,
automatic product retry policies, a second controller, or model-selected edges.
Compile-time checks bind stable node IDs, state projections, output channels,
prompt/schema/routes, and graph digest.

# TEST

1. Exact node/edge catalogue compiles with one START and only D98→END.
2. Missing/duplicate/dangling/unreachable node or edge fails compilation.
3. Every cycle crosses a deterministic counter/exhaustion guard.
4. Models have no edge to acceptance, routing, reduction, resume, or terminal authority.
5. Source and visual fan-outs use supported `Send` worker→barrier patterns;
   mixed static/dynamic joins are rejected.
6. Empty fan-out subsets and arbitrary manifest lengths remain legal.
7. Identical bindings yield identical graph digest; semantic drift changes it.
8. Production imports contain no handwritten fallback controller.

Write `results/N20_GRAPH_COMPILER.result.v1.md` with topology, guard/authority
report, graph digest, commands, and hashes.

# LOOP

Fix one registration, edge, guard, binding, or topology test. Rerun tests 1–5
and digest tests. Stop if a model must choose control flow, a loop is unbounded,
or correct implementation requires a second production graph/controller.

