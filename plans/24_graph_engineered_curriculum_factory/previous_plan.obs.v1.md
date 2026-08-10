# Plan 24 predecessor observations

1. Plan 23's objective was to evolve and promote prompt graphs, not to build or
   run a curriculum factory.
2. Plan 23's success terminal could be reached without producing a unit, PDF,
   workbook, or curriculum release.
3. Plan 23 explicitly excluded curriculum and rendered-output quality from
   candidate fitness, so its QA boundary could not establish product quality.
4. Plan 23's graph mechanics—typed nodes, separate context edges, reducers,
   bounded loops, immutable identity, and fail-closed terminals—remain useful
   as implementation controls.
5. Plan 19 correctly defined the missing production loop: live worker
   execution, unit state, manifest orchestration, workbook release, and
   end-to-end evidence.
6. Plan 21 added valuable graph IR, compilation, execution, resume, evidence,
   and authority-separation ideas, but its planning and assurance surface grew
   much larger than the product proof.
7. The current `runtime/run_curriculum.py` still refuses live capability and
   generation paths; its working path is deterministic simulation.
8. The repository contains useful runtime modules for controller behavior,
   routing, checks, logging, rendering, lifecycle state, and workbook assembly,
   so Plan 24 extends and reconciles existing code rather than starting a
   parallel framework.
9. Active prose and policy contain historical drift, including controller and
   review descriptions that do not all describe the same runtime. P0 must
   establish one executable authority before implementation.
10. A curriculum factory is proven by autonomous curriculum artifacts and raw
    evidence, not by plans, prompts, route probes, simulations, diagrams, or
    self-reported readiness.
11. Graph engineering is the means: manifest compilation, typed activation,
    code-owned guards, bounded repair, isolated context, and durable state.
12. The product boundary is non-negotiable: supplied curriculum in; accepted
    units and, for full runs, an accepted workbook out.
