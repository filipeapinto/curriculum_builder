# Schema contract regression testing

## Why this thread

Running `curricula/arduino_kit/verify_domain.py` (this curriculum's own declared,
non-model domain verifier) against every domain content file in
`curricula/arduino_kit/` produces the identical rejection on all four:

```
domain-schema-invalid: <root>: 'component_identity', 'id', 'legal_coordinates',
'orientation', 'primary_sources', 'rail_topology', 'ratings',
'source_bundle_sha256' do not match any of the regexes: '^_(fixture|note)$'
domain-schema-invalid: <root>: 'electrical' is a required property
domain-schema-invalid: <root>: 'build_map' is a required property
```

`l01_unpowered_power_path.json` (committed 2026-07-30) and the newly drafted
`l02_breadboard_connectivity.v1.json`, `l03_jumper_wires_expansion.v1.json`,
`l04_multimeter_evidence.v1.json` (2026-08-02) all use the same superseded
shape — one that predates the commit that rewrote
`curricula/arduino_kit/domain.schema.v1.json` to require `electrical` and
`build_map` (`additionalProperties: false`). Meanwhile
`curricula/arduino_kit/fixtures/domain_unpowered_path.accept.json` already
uses the *current* shape correctly. No check in this repository runs the
domain verifier, or a JSON Schema validator, against every content file in
`curricula/arduino_kit/` on a schedule or on a schema change — it only runs
inside `runtime/session_bridge.py` during a live pipeline run
(`session_bridge.py:238,248`), and L02-L04 are not even wired into
`arduino_kit_curriculum.v5.yaml` yet, so nothing in the pipeline was ever
going to exercise them. The drift was invisible until this scan ran the
verifier by hand.

## Findings

**A schema registry's compatibility gate is the direct commercial-and-academic
analogue of what this repo is missing.** Confluent's Schema Registry "checks
compatibility before accepting the new version," comparing a candidate schema
against previously registered versions under a configured compatibility type
(BACKWARD/FORWARD/FULL, optionally transitive against all prior versions), and
rejects the registration outright if it fails
(Confluent, *Schema Evolution & Compatibility Types*,
docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html).
Implication for this pipeline: the direction of the check that's missing here
is backwards from Kafka's model — Confluent gates the *new schema* against
*existing data's expectations*; this repo needs the mirror image, gating
*existing content* against a *newly changed schema*, run automatically the
moment `domain.schema.v1.json` changes rather than only when a unit happens to
run through the pipeline.

**Consumer-driven contract testing is built specifically to catch a fixture
that has quietly stopped matching the real contract.** Pact generates a
contract "during the execution of the automated consumer tests" and verifies
it against the real provider, so it functions as "contract by example" rather
than a static, easily-stale specification (Pact, *Pact Docs* introduction,
docs.pact.io). Implication for this pipeline: `domain_unpowered_path.accept.json`
is exactly a consumer-driven contract fixture — but nothing re-runs it, or the
real content files, against the schema as the *provider* of truth on every
schema change. The fixture happening to be current is luck, not verification.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Confluent, *Schema Evolution & Compatibility Types*, Confluent Platform docs — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- Pact, *Introduction*, Pact Docs — https://docs.pact.io/

## Discarded

- https://medium.com/@gunashekarr11/contract-drift-schema-mismatch-detection-the-most-underrated-api-failure-in-modern-systems-c278a2914205 — SEO/content-farm style piece with no primary claim to verify; rejected on the source-quality bar without fetching.
- https://airbyte.com/data-engineering-resources/schema-drift-in-etl-pipelines, https://estuary.dev/blog/schema-drift/, https://bixtech.ai/schema-drift-in-variant-data-a-practical-guide-to-building-change-proof-pipelines/ — vendor blogs about ETL "schema drift" (a different problem: unannounced upstream data shape changes, not authored-content-vs-declared-schema drift); topic-adjacent but not on point, not fetched.
- https://dev.to/qa-leaders/anatomy-of-a-schema-drift-incident-5-real-patterns-that-break-production-274l, https://aiopsschool.com/blog/schema-drift/ — generic listicle/SEO-aggregator material, rejected on the source-quality bar without fetching.
- https://pactflow.io/blog/schemas-can-be-contracts/ — Pactflow's own commercial "Drift" product announcement; plausible secondary source but redundant with the primary Pact docs already verified, so not fetched to keep the thread from padding with a near-duplicate vendor claim.
