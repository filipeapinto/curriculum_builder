# GOAL

Make evidence reproducible and audit claims mechanically derivable. Correct the
evidence/artifact/persistence and requirements-lineage portions of PM-12, PM-16,
PM-20, and PM-24. N10 owns controller protocol behavior; N30 owns CLI evidence
generation. Findings in those files route back to their owner and invalidate
descendants rather than being rewritten here.

# TEST

1. Find required tests or runtime operations that write stable evidence paths
   containing temporary paths, timestamps, random identifiers, platform noise,
   or ordering variance. Normalize nondeterminism or move output to immutable
   run/attempt-scoped paths.
2. Run every affected command twice from equivalent inputs and require equal
   stable bytes or distinct correctly bound run-scoped evidence. No later node
   may restore earlier bytes to satisfy a hash.
3. Make human reports derive material claims from the exact receipted artifacts.
   Add a negative test for the historical false claim that workbook registration
   existed when the production call site did not.
4. Prove the controller reads schema-bound JSON results only and keeps domain
   verdicts distinct from node admission outcomes and Run 27 terminals.
5. Label every audit source as normative, superseded, historical evidence, or
   implementation observation.
6. Add a requirements-lineage denominator beginning with current user approval,
   approved v2, Plans 20–22, retained product requirements, code, tests, and
   product evidence. The final audit must fail if any layer is omitted.
7. Prove receipt history is append-only, descendant invalidation is visible, and
   re-admission cannot erase the original attempt/reason.
8. Run affected evidence, receipt, controller, CLI, and audit tests twice.
9. Emit determinism comparisons, lineage matrix, and schema-valid result.

N50 owns only the three evidence/artifact/persistence modules, their two exact
tests, and its two versioned contracts. It may execute controller and CLI tests
read-only but cannot edit their files. Remove every retired-provider reference
from its owned active persistence test and keep the zero-occurrence test scan
green.

# LOOP

Repair the source of nondeterminism or claim drift, not the recorded hash. Any
test that writes evidence owns cleanup only inside its fresh temporary/run scope.
Rerun twice after every repair. Stop with `BLOCKED` if reproducibility requires
mutating historical Run 26 evidence.
