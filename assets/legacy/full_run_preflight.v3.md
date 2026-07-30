# v3 full-curriculum preflight

## Result: FAIL — do not run the 35-lab generation

Checked on 2026-07-27.

- The curriculum manifest contains 35 labs, `L01` through `L35`.
- The v3 L01 contract fixture passes.
- The L01 disconnected identification map uses the polarity-neutral `l01_unpowered_power_path.v2.json`; the earlier v1 remains only as a regression fixture for rejected output.
- No verified deterministic profiles exist for `L02` through `L35`.
- `run_curriculum.py` still loads `component_lab_orchestrator_prompt_v2.md`, uses the obsolete v2 schemas, and contains parallel fan-out / forced-block code.

Running all labs now would either execute the obsolete workflow or require the model to invent unverified breadboard topology, pinouts, or connection geometry. Both outcomes violate the v3 contract.

## Required work before a real all-35 test

1. Build a new serial v3 runner; preserve the old v2 runner unchanged.
2. Add verified component/board profiles and primary-source evidence for every lab that needs a deterministic map.
3. Run the v3 runner's zero-model all-35 preflight.
4. Run an all-35 scripted dry integration test that exercises revisions, retry, and acceptance.
5. Run a real L01 generation, inspect it, then run the remaining labs serially.
