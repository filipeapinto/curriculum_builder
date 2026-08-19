# P0 - Generate unit-specific, semantically correct visuals and usable evidence cards

## Problem

The visual pipeline creates three generic assets per lesson regardless of the lesson's declared visual roles.

### The “subject identification” image is irrelevant

`runtime/session_bridge.py:108-110` copies the first JPG found in the curriculum directory for every unit. The SHA-256 is therefore identical in L01-L04 (`8f9ab6...64efc`). It is an uncropped whole-kit inventory image, not a subject-identification visual.

This is especially severe in L04: the image contains no multimeter, while `L04/document/L04.md:178-180` labels it “Subject Identification” and the lesson tells the learner to find COM, mAVΩ, 10A, and the mode dial.

### The “maps” encode false relationships

`runtime/session_bridge.py:146-150` takes every seed terminal name, places the names in a vertical chain, and labels every edge `NOT CONNECTED`, regardless of `map_kind` or domain semantics.

- L02 depicts `terminal_strip_group -> centre_trench -> power_rail_segment` as one disconnected path instead of showing breadboard topology, five-hole connectivity, the trench, and rail breaks.
- L03 depicts `wire_endpoint_a` and `wire_endpoint_b` as not connected even though the lesson's key concept is that a jumper wire joins its two endpoints.
- L04 depicts COM, two alternative red-probe sockets, and the mode dial as a disconnected chain. These are choices/controls, not circuit nodes in series.

### The evidence cards are not evidence cards

All cards use the same three generic lines: “Trace each dashed teaching link,” “Tick each place you can identify,” and “Keep every connection open.” They contain no tick boxes and ignore each unit's own `domain.build_map.evidence_card.child_records`.

### Required roles are missing

The manifest requires four unit-specific roles per lesson (`curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:108-112,152-156,193-197,235-239`). The shipped units contain only the generic whole-kit photo, generic chain, and generic card. Missing examples include L02's cutaway clip illustration and rail-break warning, L03's endpoint diagram and loose-wire hazard, and L04's probe-placement diagram and current-mode red-X.

The PDFs also isolate the oversized inventory image and sparse diagrams on separate pages, producing large areas of wasted space and separating visuals from the text they are supposed to explain.

## Acceptance criteria

- Asset selection is driven by the unit's declared visual roles and verified sources, never filesystem sort order.
- Exact-identification images visibly contain the named subject and are cropped/annotated so a novice can find it.
- Deterministic renderers dispatch on the domain's `map_kind` and validated data model; unsupported map kinds fail rather than falling back to a generic chain.
- Connectivity, alternatives, physical separation, orientation, and “not connected” are rendered with distinct, truthful semantics.
- Evidence cards are usable forms generated from each unit's evidence fields, with real checkboxes/recording spaces and adult signoff where required.
- Every manifest visual role either resolves to a shipped asset or blocks the unit.
- Visuals are placed beside the steps/concepts they support.
- PDF visual review inspects every shipped page and rejects irrelevant, semantically false, illegible, or badly placed figures.
