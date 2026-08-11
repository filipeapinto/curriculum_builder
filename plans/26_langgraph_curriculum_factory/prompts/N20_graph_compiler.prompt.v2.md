# GOAL

Implement `N20_GRAPH_COMPILER` only after N10, N11, N22, and N23 pass. Build the
single root `StateGraph` from the real registered deterministic and model node
callables, then compile once as `plan26_curriculum_factory` with the exact
D00–D98/M01–M08 catalogue and section 8 edges/guards.

Use typed reducers, `START`, `END`, conditional edges, explicit product loops,
and `Send` only for denominator-first map work. Do not use placeholders, test
stubs, subgraphs, automatic product retries, a second controller, or model-
selected edges in the production compilation proof.

# TEST

1. The exact catalogue compiles against real N22/N23 callables with one START
   and only the real N22-owned D98 callable reaching END.
2. A missing, placeholder, test-only, duplicate, dangling, or unreachable
   callable/node/edge fails production compilation by stable ID.
3. Every cycle crosses a deterministic counter/exhaustion guard.
4. Models have no edge to acceptance, routing, reduction, resume, or terminal authority.
5. Source/visual fan-outs use supported `Send` worker→barrier patterns; mixed joins fail.
6. Empty subsets and arbitrary manifest lengths remain legal.
7. Identical real bindings yield identical digest; callable/schema/prompt drift changes it.
8. Production imports contain no handwritten fallback controller.

Write `results/N20_GRAPH_COMPILER.result.v1.md` with real binding inventory,
topology, guard/authority report, graph digest, commands, and hashes.

# LOOP

Fix one registration, binding, edge, guard, or topology test. Route a missing or
incorrect callable back to N22/N23 through its graph rework owner; never fabricate
a stub in N20. Stop if compilation must precede real callable ownership.

