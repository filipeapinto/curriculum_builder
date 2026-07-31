<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole -->

## Proving it

Six gates, in order. Record every result with a timestamp and a category label. Five
labels are the stage vocabulary `policy/checks.v1.yaml` owns — `logger`, `static`,
`deterministic`, `live-capability`, `golden` — and are never spelled differently here.
The sixth, `simulated`, is this prompt's own: it labels runs driven by fake workers,
and no check id carries it, because a simulated result is evidence about the
controller and never evidence about a lab.

| # | Gate | Check ids | Proves |
|---|---|---|---|
| 0 | **Logger** | `LOG-*` | append-only ordering, monotonic ids, start/completion pairing, concurrent-append safety, coverage of every checkpoint, and failure when an operation lacks its record. **Passes before any other v7 artifact exists.** |
| 1 | **Static** | `CAL-*`, `CUR-*`, `L01-*`, `SEL-*` | every one of those checks in `policy/checks.v1.yaml`, each backed by an executed assertion. A `SEL-*` id whose method is `execution` is reported `MAPPED, NOT EXECUTED` with its `RT-` id, never as covered |
| 2 | **Deterministic** | `LAB-*`, `REV-ISOLATED` | transitions, aggregation, block eligibility, failure classification, checkpoints, hashes, resource limits, circuit/prose/render consistency, terminal audits — plus every fixture marked `reject` in `policy/checks.v1.yaml`, each of which must fail validation |
| 3 | **Simulated** | — | fake workers drive clean acceptance, plan and artifact revision, malformed output, transient retry, repeated failure, legal block, system failure, interrupt and resume, then one clean pass over every lab |
| 4 | **Live capability** | `ROUTE-PROVEN` | one real preflight call on every route in `policy/routes.v1.yaml`, under the exact recorded invocation |
| 5 | **Golden L01** | `PDF-*`, `REV-COUNT-TWELVE`, `LAB-SCHEMA-VALID` | one complete lab: twelve reviews, sourced data, required visuals with resolving receipts, targeted revision evidence, PDF rendered and every page rasterized and inspected, forced interrupt and resume with before/after hashes, final controller audit |

Gate 1 exists because the previous build advertised six static checks and asserted
two. A meta-test must fail if any check id named in a result has no executed
assertion, or if any id in `policy/checks.v1.yaml` is never executed. Reporting a
check as present without running it is evidence misreporting — a drift stop, not a
bug.

Static and simulated coverage is never described as generated-lab coverage. Do not
start a live full run.

## Release gates

`META_ACCEPTED` requires all of:

- every deliverable in `meta_prompt/assets/deliverables.v1.md` present;
- gates 0–5 passing, with resume and PDF inspection proven;
- every check in `policy/checks.v1.yaml` executed, and every check id in every
  result backed by an executed assertion;
- every fixture marked `reject` in `policy/checks.v1.yaml` actually rejected, and
  every id declaring `fixture_expectation: reject` that names no fixture reported by
  id in `remediation_report.md` as advertised-but-unfixtured. Four do today:
  `LAB-BLOOM-DEPTH`, `LAB-POE-ORDER`, `LAB-CURRENT-MARGIN`, `LAB-VALUE-SOURCED`.
  Silence about them would be the misreporting gate B3 exists to catch;
- golden L01 validating against `schemas/lab.schema.v3.json`, all seven blocks;
- exactly twelve isolated reviewer invocations, with isolation proven structurally;
- every visual receipt hash resolving to an asset embedded in the accepted PDF;
- one real preflight call per route, with the sandbox policy recorded;
- every action paired and ordered, zero unpaired starts, totals agreeing across
  controller state, test results and log;
- every limit recorded with the numeric value in force;
- every id in `policy/failures.v1.yaml` mapped to a correction and a proving test;
- calibration divergences recorded, not resolved;
- immutable inputs unchanged; no unauthorized write; no unlogged model or tool call;
- no live generation beyond L01;
- no evidence-category misreporting.
