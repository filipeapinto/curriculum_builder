# Plan 21 previous-plan observations

Version: `1.0`  
Recorded: `2026-08-10`  
Source plan: `plans/21_graph_engineered_subscription_execution`  
Successor context: `plans/22_graph_eng_evol_01`

## 1. Purpose and interpretation

This document records the observations produced by the Plan 21 design and QA
run. It is evidence for Plan 22; it is not a Plan 22 strategy, specification,
or approval decision.

The failed run was a **design-package convergence run**, not an implementation
run of P0 through P6. Plan 21 never passed final QA, was never approved for
execution, and must not be cited as runtime proof. Its validators, fixtures,
review probes, and QA dispositions are planning evidence only.

The final authoritative disposition is
`plans/21_graph_engineered_subscription_execution/qa/version3_final_disposition.md`.
Versions 1 through 3 are frozen failed designs. Their defects must be preserved
as regression evidence rather than repaired in place or silently discarded.

## 2. Evidence basis

These observations synthesize the following Plan 21 evidence classes:

- the v1, v2, and v3 plan manifests, schemas, contracts, validators, prompts,
  addenda, and append-only planning logs;
- the Plan 20 gap assessment and August 2026 graph-engineering rubric;
- three independent QA perspectives: graph/runtime, prompt/subscription/
  security, and historical-regression/repository review;
- the v1 targeted closure reviews, the fresh v2 and v3 reviews, and their final
  dispositions;
- deterministic bootstrap/self-tests and independent adversarial probes;
- live repository observations captured by QA, including authentication state,
  lifecycle vocabulary, historical requirements, and dirty-file overlap.

Where a declaration conflicts with an executable counterexample, the
counterexample is stronger evidence. Where a component test conflicts with an
assembled-path test, the assembled-path result is stronger evidence.

## 3. Outcome chronology

### 3.1 Version 1

Version 1 established the base graph, contracts, phase prompts, and validator.
Its bootstrap and self-test passed, but review found approval-path and routing
bypasses. Material observations included:

- a schema-valid `PASS` could contain empty test and artifact evidence and
  still select a success edge;
- shared pause/interrupt states allowed originless or cross-phase resume,
  including a path capable of bypassing P3 through P5;
- no declared controller cleanly owned creation of resume events;
- the baseline run-status vocabulary contradicted the live repository and the
  lifecycle Plan 21 claimed to preserve;
- outcome guards did not bind legal failure classes and reasons, allowing a
  factory defect to masquerade as a prerequisite pause;
- exact required tests, artifacts, and subtasks were not consistently owned by
  compiled controller state;
- content hashes were accepted as shaped strings without recomputing source
  bytes;
- registry membership did not prove that schemas and resolvers existed or
  resolved to the required type/cardinality;
- resume provenance and single-use behavior were descriptive or in-memory,
  rather than one durable atomic protocol;
- phase-ledger completeness could be self-denominated by the ledger itself;
- the baseline did not represent all live unit states exactly.

All three targeted closure addenda failed. Version 1 was frozen as
`UNAPPROVED_REQUIRES_NEW_VERSION`.

### 3.2 Version 2

Version 2 used a typed overlay and added stronger evidence, resume, sandbox,
registry, and ledger concepts. It closed some v1 shapes but moved several
defects to new boundaries:

- correctly hashed evidence bytes could still be semantically unrelated to the
  compiled test;
- explicit failure content could still be admitted in insufficiently composed
  paths;
- resume consumption was returned in memory rather than committed by a shared
  compare-and-swap store;
- sandbox engines, denial logs, and claimed isolation lacked an external signed
  authority;
- ledgers carried output hashes without resolving and validating output bytes;
- registry keys improved while registry value semantics remained weak;
- the overlay was validated as a delta but was not reliably applied into one
  normalized effective graph;
- the v2 overlay did not actually replace the inherited P0/P4 state port, so
  base and overlay semantics could disagree.

All three fresh v2 reviews found Critical/High bypasses. Version 2 was frozen as
`CHANGES_REQUIRED_SUPERSEDED_BY_V3`.

### 3.3 Version 3

Version 3 bound 45 inherited behavioral files under a canonical bundle digest
and added signed receipts, stronger registries, SQLite resume consumption,
external-trust and sandbox records, composite state, exact subtask sets, and
more adversarial mutations. Its shipped bootstrap and self-test both passed.

The three final independent reviews still failed. The final status was
`UNAPPROVED_FINAL_QA_FAILED`. The package remained non-executable and could not
be represented as state-of-the-art compliant.

## 4. Observations about what worked

The following Plan 21 results are useful and should not be lost merely because
the package failed overall.

### 4.1 The graph-engineering direction was materially better than Plan 20

- Plan 21 treated the workflow as a machine-readable graph rather than a prose
  checklist around a monolithic bridge.
- It separated graph IR, typed state, prompts, execution, evaluation, durable
  runtime, release, and failure routes.
- It distinguished execution topology from authorized context flow.
- It used explicit nodes, edges, guards, terminal outcomes, repair cycles,
  interrupts, pauses, and resume semantics.
- It made `GOAL -> TEST -> LOOP` the standard node-prompt structure.
- It required compiler/static checks, path tests, fault injection, independent
  evaluation, trace provenance, and safe evolution.

### 4.2 The research and assessment frame remains useful

- The Plan 20 gap assessment gave a concrete baseline rather than assuming the
  predecessor was already adequate.
- The August 2026 rubric GE-01 through GE-14 covered explicit IR, atomic typed
  nodes, guards, compiled topology, typed state, durable execution, isolation,
  evaluation, recovery, provenance, path/fault testing, process evaluation,
  and safe evolution.
- GE-14 already recognized that prompt/topology candidates should be evaluated
  offline, versioned, compiled, and explicitly promoted while active runs stay
  pinned. Plan 21 stated this principle but did not use it as the governing
  authoring process for its own successive prompt graph.

### 4.3 Several controls became genuinely stronger

- The 45-file inherited behavioral base was selected and digest-bound
  correctly in v3.
- Obvious prompt-map, subtask-map, additional-output, output-collision, and
  registry owner/type mutations were rejected.
- Ed25519 signature verification and fixed evidence locations provided stronger
  structure than bare hashes.
- Explicit `FAIL` assertion shapes were rejected in the narrow v3 receipt
  validator.
- Exact test and subtask denominators were introduced for important paths.
- The v3 SQLite `BEGIN IMMEDIATE` primitive produced one winner under two
  connections and rejected cold replay after reopening.
- Composite P0 state repaired the inherited-vs-target lifecycle distinction at
  the plan-contract level.
- The live run vocabulary and historical unit-state vocabulary were recovered
  rather than overwritten by invented replacements.
- The package preserved exact historical concerns: issues 001 through 007,
  three-unit `--all` plus cold resume, four isolated workbook reviews and their
  negative cases, RT-7 scope and dirty-overlap handling, and a format-aware
  historical census.
- Subscription-only execution distinguished authentication, entitlement,
  included allocation, separately billed credits/overage, API fallback,
  usage-based seats, and provider identity instead of treating “logged in” as
  sufficient proof.
- Codex identity observations were driver-bound and did not claim more model
  identity certainty than the available evidence supported.
- Failed versions and review reports were frozen, preserving an audit trail.

### 4.4 Independent review added real value

- Reviewers did not accept green bootstrap output as dispositive.
- Independent probes found attack paths absent from shipped self-tests.
- The three review perspectives converged on common systemic defects—runtime
  authority, constructibility, trust, provenance, and composition—even when
  they used different witnesses.
- Concrete witnesses such as empty evidence, copied receipts, `/etc/hosts`,
  stale events, resolver swaps, shared outputs, colliding idempotency keys,
  arbitrary resume IDs, magic-prefix binaries, and self-asserted UIDs converted
  vague risk into reproducible failure evidence.

## 5. Final v3 technical failure observations

### 5.1 Runtime authority remained injectable

The compiler-owned command, test, artifact, subtask, and effective-node
registries were not materialized and consumed as one immutable runtime object.
Critical admission functions still accepted caller-provided maps.

Consequences observed by QA:

- a caller could shrink P6 to one test and one artifact;
- a caller could substitute subject, command, artifact-path, media-type, or
  schema mappings;
- an event with a stale run, wrong node, wrong attempt, wrong graph digest, and
  incomplete envelope could be admitted through the v3 evidence path;
- the artifact registry could authorize an arbitrary absolute path;
- graph-base and overlay declarations could both validate without producing one
  normalized, digest-bound effective graph.

Observation: a registry is not authoritative merely because the plan calls it
“compiled.” Authority exists only when the runtime loads a frozen compiled
artifact and refuses competing caller input.

### 5.2 Evidence was cryptographically stronger but semantically substitutable

Signed receipts proved that particular bytes were signed; they did not always
prove that the compiled test command ran or that the bytes were relevant to the
required assertion.

Observed bypasses included:

- `command_digest` was carried but not compared with the compiler-owned command;
- stdout/stderr digests were signed but their source bytes were not always
  resolved and recomputed;
- one valid signed P6-T01 receipt could be copied into the paths for all P6
  tests because inner and outer test identities were not composed correctly;
- valid but unrelated content could satisfy weak semantic checks;
- `/etc/hosts` could be accepted as Markdown because it contained a comment
  marker, or as an unconstrained octet stream;
- an artifact contract could omit a semantic schema/type-specific verifier;
- well-shaped or signed hashes could describe nonexistent, unrelated, or
  wrong-command evidence.

Observation: provenance without semantic binding authenticates the wrong fact
more reliably; it does not establish correctness.

### 5.3 The provenance graph was unconstructible

The v3 event, evidence manifest, phase ledger, and subtask receipts attempted to
contain one another's final content hashes/IDs. The effective dependency was a
cryptographic cycle:

```text
event ID -> ledger hash -> receipt hashes -> event ID / manifest ID
manifest ID -> ledger hash -> receipt hashes -> event ID / manifest ID
```

No provisional identity, detached commitment, two-phase finalization, or
cycle-breaking canonicalization rule existed. Satisfying the contracts would
require finding coupled SHA-256 fixed points.

Observation: individually valid schemas and validators do not prove that a set
of content-addressed records has a constructive serialization order. A complete
from-scratch constructor is mandatory evidence for a provenance design.

### 5.4 Effective graph compilation was declarative rather than materialized

V3 checked exact overlay constants and some inherited relationships, but it did
not consistently apply base plus overlays and emit a single normalized graph
whose digest governed execution.

Observed consequences:

- runtime admission could use maps other than those declared by the plan;
- same-type resolver swaps passed even when they changed semantic meaning;
- declarations could be internally checked in parallel without proving the
  final composed node contract;
- inherited ports and overlay replacements had previously diverged.

Observation: validating a patch and validating a base are not equivalent to
validating the applied result.

### 5.5 Registry validation checked shape more strongly than meaning

The validators improved rejection of unknown names, wrong owners, missing local
schemas, obvious type errors, and future artifact producers. Residual failures
included:

- registry entries whose schema or resolver did not exist;
- resolver swaps to a different field with the same broad JSON type;
- no proof that the resolved value had the exact consuming-port cardinality and
  semantics;
- caller-supplied artifact contracts and paths;
- insufficient binding from registry output to runtime admission.

Observation: name membership, owner labels, and broad types are necessary but
not sufficient. Every registry entry must be executable as a typed resolution
against the compiled effective graph.

### 5.6 Trust separation was self-attested

The v3 trust checker compared actual authority-root ownership with a claimed
`authority_uid`, then compared that value with a separately claimed
`model_uid`. It did not obtain the model worker's credential from an actual
launcher/process observation.

A process running under the real owner UID could pass by claiming a different
model UID. Therefore the nominal controller/model separation was not proven.

Observation: comparing two fields supplied by the same trust document is not
independent identity evidence. Trust must be rooted in observed OS/process,
launcher, service, or externally signed capability evidence outside model
write authority.

### 5.7 Sandbox proof did not prove sandbox execution

V3 improved sandbox schemas, signed registries/profiles/probes, root existence,
and denial assertions. Residual bypasses included:

- a file with ELF/Mach-O magic bytes could be treated as an engine without
  proving that it was a runnable expected engine;
- a signed probe receipt from a stale run/attempt could be accepted;
- policy fields did not completely constrain readable/writable root purposes;
- controller output or credential-root relationships were not fully excluded;
- signed metadata could describe a probe without proving that the declared
  engine and exact policy executed it.

Observation: signatures authenticate the signer, not the physical truth of the
execution. Engine-specific launch and observation must bind binary, profile,
command, process credential, run/attempt, exit/signal, and denial evidence.

### 5.8 Resume CAS worked as a primitive but not as a protocol

The SQLite concurrency primitive was a real success: it serialized competing
consumers and persisted rejection of cold replay. The assembled resume workflow
remained incomplete:

- arbitrary unsigned continuation, command, and authorization IDs could be
  consumed;
- validation of the signed/typed capability was not composed into the same
  transaction as consumption;
- there was no durable activation outbox or recoverable pending activation;
- a crash after consumption but before activation could permanently consume the
  capability without activating the node;
- earlier versions either ignored consumed state or returned consumption only
  in memory.

Observation: proving a CAS primitive does not prove safe resume. Authorization,
current checkpoint/generation validation, consumption, activation intent,
delivery, acknowledgement, and crash recovery form one protocol.

### 5.9 Subtask completeness and idempotency remained forgeable

The exact v3 subtask ID set and signed receipt paths were improvements, but
receipt semantics were not fully bound to compiler-owned subtask definitions.

Observed bypasses included:

- every declared subtask could reuse the same unrelated output file;
- every ledger entry could reuse one idempotency key;
- per-subtask output ownership and authorized sharing were not enforced;
- union/reconciliation of receipt outputs with the manifest was incomplete;
- command and output semantics were not bound tightly enough to the compiled
  subtask contract;
- earlier ledgers could choose their own required-subtask denominator.

Observation: exact IDs and signatures do not prove distinct work. Idempotency
keys, inputs, commands, outputs, and allowed sharing must be derived from and
checked against one immutable compiled subtask definition.

### 5.10 A required external-trust pause was not representable

V3 correctly recognized that missing external trust should pause before P2 and
that P0 could observe but not manufacture that trust. However, the inherited
phase-result schema, failure-class mapping, graph guard, and edge did not include
the new trust-unavailable prerequisite.

Consequences:

- the current missing-trust condition could not produce a schema-valid honest
  pause;
- using another failure class would misrepresent the cause;
- the written behavior and executable graph disagreed.

Observation: every new operational condition must be propagated through the
complete effective schema/guard/edge/continuation graph before it exists as a
real route.

## 6. Earlier-version failures that remain mandatory regressions

Even where v3 partially or fully repaired an earlier defect, Plan 22 must retain
the concrete failure as a permanent regression case.

### 6.1 Acceptance and evidence regressions

- empty-evidence `PASS`;
- missing, extra, duplicated, reordered, `NOT_RUN`, failing, or null-evidence
  tests;
- missing, extra, duplicated, reused, nonexistent, unreadable, or out-of-scope
  artifacts;
- fabricated but well-shaped hashes;
- real but unrelated bytes;
- explicit failure bytes presented as passing evidence;
- copied one-test receipt used for multiple test slots;
- wrong/no-op compiled command;
- wrong assertion denominator;
- stale run/node/attempt/checkpoint/graph/prompt/policy/schema/route binding;
- forged or unrecomputed event identity;
- schema-valid content that is semantically irrelevant.

### 6.2 Routing and status regressions

- originless resume;
- cross-run and cross-phase resume;
- P2 pause resuming directly to P6;
- interrupt resuming to a node other than its suspended origin;
- duplicated/replayed continuation or command;
- factory defects selecting prerequisite-pause edges;
- failure outcome/class/reason combinations not in the closed mapping;
- impossible or renamed baseline lifecycle vocabularies;
- confusion between unit `BLOCKED`, run-level status, plan prerequisite pause,
  interruption, convergence exhaustion, and system failure.

### 6.3 Compiler and contract regressions

- missing/future producer references;
- unresolved contract schemas or resolver paths;
- same-shape but semantically wrong resolver substitutions;
- base/overlay disagreement;
- overlay validation without applied effective-graph validation;
- caller-shrunk required-test/artifact/subtask maps;
- output collisions and undeclared additional outputs;
- self-denominated ledger completeness;
- arbitrary source-set digest or cross-category ID collision.

### 6.4 Durability and side-effect regressions

- in-memory-only resume consumption;
- double resume in the same process;
- double resume across cold processes;
- crash before and after every side effect or commit boundary;
- consumed-without-activation loss;
- repeated committed model calls or repository writes;
- skipped uncommitted subtasks;
- colliding phase/subtask idempotency keys;
- replay inferred from prompt prose rather than compiled state.

### 6.5 Trust, sandbox, and subscription regressions

- same actual UID with a different claimed UID;
- model-writable authority/evidence roots;
- fake executable recognized by magic prefix alone;
- stale or wrong-run sandbox probe receipt;
- readable credentials under an outside-broker claim;
- writable-root expansion, symlink escape, mount alias, or undeclared network
  destination;
- authentication mistaken for subscription entitlement;
- separately billed credits/overage or API fallback mistaken for included-only
  subscription execution;
- contradictory overrides or incomplete override registry;
- provider/model identity claims stronger than observable driver evidence.

### 6.6 Historical behavior regressions

- issues 001 through 007 losing an explicit test owner;
- raw JSON accepted as a rendered workbook;
- missing required checks or acceptance dominance;
- visual claims not grounded in real rendered evidence;
- L04 safety/evidence regressions;
- proof-of-execution or claim-entailment regressions;
- incomplete run lifecycle and resume behavior;
- fewer/more than the exact isolated reviewer set or shared reviewer state;
- loss of three-unit `--all` plus separate cold-process resume;
- weakened RT-7 exact scope, mirror, site, gate, or dirty-overlap behavior;
- census logic that ignores Markdown/YAML/anomalies/aggregates/later-fixed
  findings.

## 7. Process-level observations

### 7.1 Plan 21 optimized declarations before constructibility

The package grew rich schemas, manifests, promises, and invariants before one
minimal node could construct its complete evidence/provenance/resume path from
scratch. The circular commitment defect is the clearest result.

Observation: the first proof must be a minimal executable vertical slice, not a
complete multi-phase declaration.

### 7.2 Repairs were local while failures were compositional

Each version repaired the last discovered shape:

- bare hashes became signed receipts;
- weak replay checking became SQLite CAS;
- informal maps became more typed registries;
- inherited files became a digest-bound bundle.

Review then found defects at the new interfaces: signed-but-wrong commands,
CAS-without-authorization/outbox, typed-but-injectable registries, and
digest-bound-but-unapplied overlays.

Observation: component improvement can move rather than remove a vulnerability.
Every repair requires a complete assembled attack-path retest.

### 7.3 Additive overlays increased semantic surface area

V2 and v3 preserved earlier plans and added overlays/addenda. This protected
history but forced readers and validators to reconstruct effective semantics
across multiple files. Base and overlay ports, failure mappings, outputs, and
state could diverge.

Observation: immutable ancestry is useful, but each candidate must compile to a
single inspectable effective artifact. The runtime must consume that artifact,
not the ancestry chain.

### 7.4 Green self-tests were overfit to implemented checks

Every version could pass its shipped bootstrap/self-test while independent
review produced accepted counterexamples. The self-tests mainly demonstrated
that the validator enforced the cases the validator author anticipated.

Observation: self-tests are necessary developer evidence, not independent
fitness or approval evidence. Holdout mutations and externally authored
assembled witnesses are required.

### 7.5 QA happened after large candidate construction

Independent review was effective, but it evaluated large, already elaborate
packages. Critical architectural errors therefore invalidated substantial
downstream work.

Observation: adversarial review must occur at architectural commit points—data
authority, provenance order, trust root, and transactional resume—before the
full prompt suite is expanded.

### 7.6 Specification size did not correlate with assurance

Plan 21 accumulated plans, schemas, contracts, validators, prompts, addenda,
logs, review rounds, and mutations. Despite this rigor and volume, the final
system remained both bypassable and unconstructible.

Observation: assurance must reward demonstrated properties and penalize excess
semantic surface, duplicated authority, and verification complexity.

### 7.7 Declared ownership was not always operational ownership

Labels such as `PHASE_CONTROLLER`, “compiler-owned,” “external trust,” and
“signed runner” did not by themselves establish who created, loaded, verified,
or could mutate the decisive bytes.

Observation: ownership requires a concrete write path, read path, process
identity, immutable artifact, and rejection behavior.

### 7.8 The plan mixed design-package QA with future execution QA

Earlier review noted that the package described P6 convergence exhaustion for a
future executed graph but did not initially distinguish that from exhaustion of
the current pre-execution design review.

Observation: candidate-design status, execution-run status, phase status, and
curriculum-unit status need separate schemas and transitions.

## 8. Live environment and repository observations captured during QA

- At the time of the v3 prompt/subscription review, Claude authentication was
  absent (`loggedIn: false`, auth method `none`), while Codex reported ChatGPT
  login.
- Under Plan 21's own rules, no Claude live model call was permitted; the
  correct behavior was to pause before launch.
- External trust was not available as a valid instance, and P0 was not allowed
  to manufacture it.
- Several RT-7-related targets overlapped pre-existing dirty work. Plan 21
  correctly required an exact user authorization or prerequisite pause rather
  than overwriting those changes.
- The repository's run lifecycle used `IN_PROGRESS`, `PARTIAL`, `INTERRUPTED`,
  `BLOCKED`, and `COMPLETE`; an honest migration needed to preserve observed
  values while adding a distinct `SYSTEM_FAILURE` target where required.
- The unit vocabulary recovered during later QA included `ACCEPTED`,
  `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, and `SYSTEM_FAILURE`.

These are dated observations from the Plan 21 review. Plan 22 must re-probe
mutable environment facts rather than assume they are still current.

## 9. Cross-cutting causal observations

The failure was not one missing condition. It resulted from interacting causes:

1. **No minimal constructive proof.** Component validators existed before a
   complete valid object graph could be produced.
2. **Multiple authorities.** Plan declarations, overlays, runtime `current`
   maps, registries, receipts, and prompts could each influence the effective
   contract.
3. **Authentication substituted for meaning.** Signatures and hashes were
   sometimes treated as proof of relevance, command execution, or isolation.
4. **Local validation substituted for composition.** Correct primitives did
   not establish a correct end-to-end transaction or route.
5. **Self-authored evaluation corpus.** Shipped tests concentrated on known
   mutations and did not sufficiently challenge the validator's assumptions.
6. **Patch accumulation.** New overlays repaired symptoms while increasing the
   number of semantic joins at which defects could hide.
7. **Late architectural rejection.** Independent QA found foundational defects
   after the package had expanded across all phases.
8. **No optimization pressure for simplicity.** Candidate growth was not
   penalized even though complexity increased attack surface and review burden.

## 10. Observational constraints carried into Plan 22

The following are evidence-derived constraints, not yet the complete Plan 22
strategy:

- Plan 21 v1-v3 remain frozen and non-executable.
- Every concrete Plan 21 Critical/High witness must enter the inherited failure
  corpus.
- A candidate cannot receive fitness credit merely for passing its own
  bootstrap or schema validation.
- One minimal node must be constructible and revalidated end to end before the
  graph expands.
- Content-addressed records require an explicit acyclic production order and a
  from-scratch construction test.
- The compiler must emit one immutable normalized effective graph; runtime
  admission must consume it without caller-supplied denominator authority.
- Test, command, assertion, artifact, schema, state, guard, subtask, and
  idempotency semantics must be bound in that effective artifact.
- Trust claims must be anchored in independently observed execution identity,
  not differences between self-reported fields.
- Resume must be evaluated as one crash-safe authorization-to-activation
  protocol, not as a CAS helper.
- Evaluation must include component tests, composed attack paths, cold-process
  tests, crash injection, historical regressions, and unseen holdouts.
- Candidate comparison must account for security/correctness, constructibility,
  regression coverage, path efficiency, prompt/tool cost, and complexity.
- A new operational condition is incomplete until its schema, guard, edge,
  state, continuation, and test path are all present in the effective graph.
- Mutable environment facts—authentication, entitlement, installed engines,
  external authority, and dirty overlap—must be freshly observed at execution
  time.
- No candidate may describe itself as approved or state-of-the-art compliant
  while any Critical/High finding remains unresolved.

## 11. Bottom-line observation

Plan 21 demonstrated that a graph prompt system can be highly specified,
versioned, schema-valid, digest-bound, cryptographically signed, and green under
its own tests while still being unsafe to approve and impossible to execute as
specified.

The reusable achievement is the graph-engineering foundation and the rich
failure evidence. The central lesson is that Plan 22 must evolve candidates by
measured end-to-end behavior: construct first, attack the composition, preserve
every failure as selection pressure, and promote only a simpler or strictly
better candidate whose runtime consumes the exact artifact that was evaluated.
