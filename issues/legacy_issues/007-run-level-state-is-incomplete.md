# P1 - Record an honest run-level state and coverage for partial executions

## Problem

The output root does not say whether the curriculum run is complete, intentionally paused, interrupted, or abandoned.

Evidence:

- `outputs/arduino_kit_run_v2/results/gate_1_static_preflight.json` records `unit_count: 35` and IDs L01-L35.
- Only L01-L04 directories exist.
- Each of those four units has its own `terminal_state: ACCEPTED`.
- `meta_execution_state.json` records only authorized roots and hashes; it has no run status, next unit, completed/remaining coverage, or resumption checkpoint.
- There is no assembled workbook or run-level acceptance/partial-run receipt.
- The root execution log contains only the logger concurrency probe, not lifecycle records explaining why generation stopped after L04.

A reader can easily mistake four accepted units for a successful execution even though 31 manifest units and final workbook assembly are absent. If the stop after L04 was intentional, that fact still needs a durable state record.

## Acceptance criteria

- The run root has a schema-validated lifecycle state with manifest count, completed IDs, blocked/failed IDs, remaining IDs, current/next unit, terminal reason, and resumable checkpoint.
- A partial run uses an explicit non-complete state such as `INTERRUPTED` or `PARTIAL`, never inference from directory contents.
- Run-level `ACCEPTED/COMPLETE` is impossible until all manifest units pass, the workbook is assembled, the shipped artifact is rasterized/reviewed, and coverage is audited.
- Root logging records unit transitions and the event/reason that stopped execution.
- Resume checks verify manifest/runtime hashes and continue from the recorded next unit without overwriting accepted artifacts.
- Tests cover a deliberate stop after four of 35 units and prove it cannot be mistaken for completion.
