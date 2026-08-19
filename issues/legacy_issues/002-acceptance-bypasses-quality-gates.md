# P0 - Do not mark units `ACCEPTED` when mandatory quality gates did not run

## Problem

All four units have `terminal_state: "ACCEPTED"` even though the runtime did not execute the controls designed to catch exactly these failures.

Evidence:

- `runtime/session_bridge.py:176-186` tells the worker that `TEXT-READABILITY-BAND`, Bloom, derivation, and receipt checks are stable requirements.
- `runtime/session_bridge.py:256-261` records only schema validation, the domain verifier, and receipt-hash resolution. It does not execute readability, Bloom verb reporting, rendered derivation, PDF asset resolution, text legibility, or PDF visual review.
- `runtime/session_bridge.py:278-279` treats “rasterized and nonblank” as sufficient PDF inspection. A page full of raw JSON therefore passes.
- `runtime/session_bridge.py:284-292` unconditionally emits `ACCEPTED` after those limited checks.
- Every `outputs/arduino_kit_run_v2/L0X/results/unit_checks.json` contains only `DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`, and `RECEIPT-HASH-RESOLVES`.
- Every `acceptance.json` discloses that the cross-family judge was bypassed, yet still records `ACCEPTED`.

The claim “every executed automated check passed” is technically narrow but operationally misleading: required checks were omitted, and the terminal state hides that distinction.

## Expected behavior

Acceptance must be fail-closed. A required check that is absent, skipped, deferred, bypassed, or unable to inspect its real subject is not a pass.

## Acceptance criteria

- The runtime builds the required check set from policy and records one explicit result for every check: `PASS`, `FAIL`, or a non-accepting `NOT_RUN/BLOCKED` with reason.
- `TEXT-READABILITY-BAND` runs against the actual child-facing rendered text.
- `TEXT-BLOOM-VERBS` runs and records flags, even though flags are non-blocking.
- `DOC-DERIVED-FROM-SOURCE` validates rendered claims, not merely `lab["domain"] == domain`.
- `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, and `PDF-VISUAL-REVIEW` operate on the shipped PDF/rasterized pages.
- A required cross-family review cannot be converted into `ACCEPTED` merely by adding a divergence string. If a user-authorized bypass is supported, the terminal state must remain non-release/non-accepted.
- An integration fixture containing raw JSON, an irrelevant image, or clipped/unreadable text is rejected.
- Acceptance output identifies the policy/check-set version used, so omissions are auditable.
