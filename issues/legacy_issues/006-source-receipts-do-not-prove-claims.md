# P1 - Validate that cited sources support generated claims, not only that files exist

## Problem

The current receipt gate recomputes a hash for an asset/source but never tests whether the cited bytes support the generated claim or the exact device/variant being taught. Schema-valid, hash-valid assertions can therefore be invented, over-specific, or attached to the wrong subject.

## Evidence

- `runtime/checks.py:45-61` verifies paths and SHA-256 values only.
- `runtime/session_bridge.py:256-261` records `RECEIPT-HASH-RESOLVES: PASS` and performs no claim-entailment or source-scope check.
- L03 declares a “typical jumper wire current rating” with `absolute_max: 1 A` (`L03/workers/lab.json:302-305`). Its cited page says a good-quality breadboard is generally limited to around 2 A (`L03/sources/source_01.html:1885`) and does not establish a 1 A rating for the exact kit jumper wires.
- The same L03 source is a general solderless-breadboard guide and does not establish that the named “breadboard expansion board” is in the kit, yet the adult-verification block claims it is (`L03/workers/lab.json:207-208`).
- L04 turns a tutorial for another meter into exact claims about the lesson's unidentified meter; see issue 004.
- All four units can call the same whole-kit photo a resolving exact-fact visual even when the subject is absent or too small to identify.

## Acceptance criteria

- Every externally supported claim records a bounded claim, source locator (section/line/page/figure), exact subject/variant, and evidence scope.
- A deterministic check confirms the locator resolves and the quoted/structured evidence is present in the cached source.
- Safety-critical and numeric claims require an explicit technical entailment review; hash resolution alone is never sufficient.
- Device-specific claims fail when the cited source is generic or for a different model unless the claim is explicitly model-independent and justified as such.
- Derived/conservative limits record the derivation and all premises; they are not attributed directly to a source that states a different number.
- Visual receipts additionally prove that the named subject/feature is visible in the shipped crop.
- Regression fixtures cover wrong-device citations, unsupported numbers, out-of-scope source reuse, and a valid exact-model claim.
