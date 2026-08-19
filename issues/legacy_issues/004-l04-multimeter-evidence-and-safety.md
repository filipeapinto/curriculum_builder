# P0 - Correct L04's multimeter evidence, device specificity, and core safety teaching

## Problem

L04 gives device-specific socket/current guidance without a verified image or manual for the actual meter and fails to state the curriculum's central safety rule clearly in the rendered lesson.

## Evidence

- The alleged identification image is the ELEGOO kit inventory photo and contains no multimeter (`L04/document/L04.md:178-180`).
- The frozen source is a SparkFun tutorial using a VC830L-style meter, not an identified learner-owned meter. The cached page itself says the tutorial is no longer current (`L04/sources/source_01.html:165`).
- The document says the mAVΩ socket “shares one small fuse across voltage, resistance, and currents under 200 mA” (`L04/document/L04.md:89`). The cached source supports a shared physical port and a fused 200 mA current range (`source_01.html:693`); it does not support the claim that voltage and resistance measurement paths share that current fuse.
- The document says the 10A socket is used “only above 200 mA” (`L04/document/L04.md:63,138`). The source recommends switching when current is close to or above 200 mA (`source_01.html:693`) and later recommends starting on 10A when potential current exceeds 100 mA (`source_01.html:784`). Those source-specific thresholds are already inconsistent enough that they must not be turned into a universal rule.
- The curriculum explicitly requires: “Current mode is never placed directly across a supply” (`curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:227`). The rendered learner/adult instructions never state that direct prohibition. It appears only in the hidden domain failure-mode object; the learner sees a vague self-explanation question (`L04/document/L04.md:90`).

For a beginner lesson, “some meters label the current sockets slightly differently” followed by “ask the adult” (`L04/document/L04.md:156-158`) is not an adequate substitute for model-specific verification.

## Acceptance criteria

- L04 names the exact meter model/variant used, or explicitly becomes a model-agnostic identification lesson with no model-specific thresholds or jack claims.
- A verified photograph/manual for that exact meter shows the socket labels, dial positions, limits, and fuse arrangement used in the lesson.
- Claims distinguish a shared physical jack from the internal measurement/fuse paths.
- Current-range selection guidance is derived from the exact manual and expected circuit, not a universal 200 mA threshold copied from a different meter.
- Child-facing and adult-facing instructions state directly that current mode is inserted in series and must never be placed across a supply.
- A prominent deterministic red-X visual shows the prohibited across-supply current-mode connection, as required by the manifest.
- A technical reviewer checks the final raster and records a verdict before acceptance.
- Existing L04 artifacts are withdrawn/regenerated; they must not remain `ACCEPTED`.
