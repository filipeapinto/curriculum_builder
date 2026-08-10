# Plan 21 graph/runtime targeted closure addendum

## Closure verdict

**FAILED_TARGETED_CLOSURE — 1 Critical and 3 High findings remain
unresolved.** This addendum is limited to the Critical/High findings in
`graph_runtime.review.v3.md`, as permitted by the one-addendum rule at
`graph_engineered_subscription_execution.plan.v1.yaml:499-508`. It is not a
fourth full review. The revised package closes several subparts of every
finding, and both shipped commands pass, but independent counterexamples still
violate the controller's claimed hash-recomputation, single-use resume,
contract-resolution, and compiled phase-ledger invariants. Under the exit rule
at `graph_engineered_subscription_execution.plan.v1.yaml:502-508`, the current
version remains unapproved and requires a new version.

## Frozen-byte basis

The following SHA-256 values identify the principal bytes tested:

| Artifact | SHA-256 |
|---|---|
| `graph_engineered_subscription_execution.plan.v1.yaml` | `171af5dff71d33331f263bf73c84219790209700cd15d403f63ee207805b561e` |
| `graph_engineered_subscription_execution.schema.v1.json` | `7fc6b3eb604d49fb11d7b78779665f403371e2455b35010370b57531cc10d209` |
| `contracts/phase_result.schema.v1.json` | `70d502020bc0cae1aaa26dfff80ab942c25dbe58854abb39b0fe2640c213b44d` |
| `contracts/continuation.schema.v1.json` | `615a3608ae978a5ce581adb75f8a68a1f4179cf92f08b36006c5ec6b22bb270d` |
| `contracts/resume_command.schema.v1.json` | `82626de57def478915e7fae19262a344ace000f6b7111879b0c161df67b2318e` |
| `contracts/phase_ledger.schema.v1.json` | `235d9b207f32a813afc1587401f960ce787c4574e64b270b410e13f43a9e45a3` |
| `contracts/coverage_denominator.schema.v1.json` | `0b37a0b5136d46d2a6931bd1ee678e912fa1806c50b2ea128878d830ffb67cec` |
| `tools/validate_plan.py` | `e82034cc638183e46456ba2310cef14bda75ea56eeadb66ed69fb63221f0d01d` |
| `prompts/P_ALL_graph_orchestrator.prompt.v1.md` | `ea1dce8e30df89c3664daada43a32417bb2d8c133224c54b2d42de48f6ddfa8d` |
| `prompts/P0_contract_and_evidence_freeze.prompt.v1.md` | `f85f57cabb54318d75e5caaa78eabadd7e81b6a682ec2e29d2a68d82cf6dbb05` |
| `prompts/P1_graph_ir_and_static_compiler.prompt.v1.md` | `1a31e6abe737d9ee4dfa55a40ed88cd30632f00bc60657258db4ef9629976f8f` |
| `prompts/P3_durable_graph_runtime.prompt.v1.md` | `cb3f1e3e050542a3f73f73ce8e1214ef462d57a679195378fd448916ffbbbba9` |

The controller's canonical `sha256(json.dumps(sorted(set),
sort_keys=True,separators=(",",":")))` required-set digests for the exact
current node declarations are:

| Node | Tests | Required-test-set digest | Artifacts | Required-artifact-set digest |
|---|---:|---|---:|---|
| P0 | 12 | `82ecf90b9d8c1562984f3d74953bb4485be60624b14dda0e31354b7ad055dac6` | 7 | `6b63c8353d057478c13534141772dc2c3c5d84196173ffc1e03fbfec830d6474` |
| P1 | 15 | `e9c816e46d274ab6c0f5cd54be85267138d99dd184ee10aa122ecd50c259e136` | 6 | `f33c9a456dc17ad4d062a2d6c0bc22bd856a350c40985961e0da77704ea0bf4c` |
| P2 | 18 | `4d8b05c77043e928dfda78f697ead63a2af941ef5fd07f938301af8d9dbcacd2` | 6 | `208285fd3f990e7e7e1fd259946b4272aa1446efccbd9ccc5bb5ebf959ea9a02` |
| P3 | 21 | `60165888c22903edb36f3f912d92b50402e5bf7f8dbdd3e8eaf433dd65e9e45f` | 8 | `c7ada6ad6af3ff607c2e938016af66a62f96ebca7a7389a6c5312bdb8fa8e5ad` |
| P4 | 24 | `7cf3dc4a6342d6ebca21b80b55a5a2f8143dab82b4f264f1fad2990ea256cf91` | 5 | `768fdaf6007b7f013bd32a3dbd436c7c90dda1b16e0335a4603dcae7e171c0d9` |
| P5 | 22 | `1bee67960c37d0264e39f152b38c852427fefc769b14fab8cd082288a454c651` | 4 | `17efb3a7a310963dbfab6f35ac5fdac06bc20654c53a42c47c3d9d991814980c` |
| P6 | 24 | `5a8f869cd49594c462d8a12266e0a751c90695b388d8d509a9137b3dc6ba19f7` | 5 | `fdfac4b71d731bb62ed4f24d918815320701b3fa8c9bd587dd0130682a8c60bf` |

## Commands and independent probes

Both shipped commands passed from the repository root:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py
plan21_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py --self-test
plan21_bootstrap=PASS
```

I then imported the frozen validator in a no-write Python probe and exercised
`validate_phase_event`, `validate_resume`, `validate`,
`validate_phase_ledger`, and `validate_denominator` directly. The probe used a
P6 event with the exact 24-test/5-artifact sets above and independently mutated
one invariant at a time. Results:

```text
REJECTED: empty PASS; failing PASS; missing/extra test; wrong test-set digest;
          wrong artifact-set digest; stale run, attempt, graph, prompt, policy,
          schema, route, execution-contract, predecessor-event, or checkpoint
ACCEPTED: PASS with every event/evidence/artifact content hash replaced by an
          arbitrary but well-shaped digest

REJECTED: stale resume execution-contract, graph, prompt, policy, schema,
          route, checkpoint; missing local schema; unknown contract; future
          artifact producer
ACCEPTED: identical resume first use; identical resume second use; identical
          resume when current.consumed_continuation_ids already names it;
          registry entry whose schema_ref does not exist; registry entry whose
          resolver does not exist

ACCEPTED: complete one-subtask P6 phase ledger whose only required subtask is
          self-declared by that ledger; identical complete-ledger revalidation

REJECTED: denominator aggregate mismatch; duplicate id within one category
ACCEPTED: arbitrary source_digest; changed record source_hash without changing
          source_digest; the same id reused across categories
```

These are independent counterexamples beyond the shipped self-test. No Plan 21
source artifact was modified by the probes.

## V3 Critical/High dispositions

| V3 finding | Closure disposition |
|---|---|
| 1. Critical — evidence-free/failing PASS | **UNRESOLVED.** Empty/failing/partial/extra sets and stale bindings are now rejected, but fabricated evidence and artifact hashes are still accepted without recomputation. |
| 2. High — unbound/unowned resume | **UNRESOLVED.** Ownership and provenance bindings are now explicit, but single use is not enforced: the same command passes repeatedly and passes while listed as consumed. |
| 3. High — unresolved/future artifact and state references | **UNRESOLVED.** Local, unknown-symbol, and future-producer checks are fixed, but registry entries are never resolved against their schema or resolver path. |
| 4. High — unchecked idempotency | **UNRESOLVED.** Phase/subtask key grammar and ledger state are typed, but each ledger chooses its own required-subtask denominator, so a phase can omit committed work and declare completion. |

### 1. Critical — PASS still trusts fabricated content hashes

**Resolved subparts.** The phase schema now makes test/artifact collections
nonempty and constrains PASS evidence (`contracts/phase_result.schema.v1.json:28-29,40-47`).
The controller helper binds run, attempt, graph, prompt, policy, schema, route,
execution contract, predecessor event, and checkpoint; it also enforces exact
test/artifact identities and their set digests (`tools/validate_plan.py:48-70`).
The independent probe confirmed every stale binding and every empty, failing,
missing, extra, or wrong-set-digest mutation is rejected.

**Unresolved Critical defect.** `validate_phase_event()` receives no artifact or
evidence bytes and performs no hash recomputation. After exact-set comparison,
its only PASS content check is status plus non-null evidence hash
(`tools/validate_plan.py:64-70`). Indeed, the shipped positive fixture labels
all-zero hashes valid and admits them (`tools/validate_plan.py:539-553`). The
independent probe replaced the event id and every evidence/artifact value with a
different arbitrary 64-hex digest; admission still succeeded. The manifest and
orchestrator explicitly promise `artifact_hash_recompute`
(`graph_engineered_subscription_execution.plan.v1.yaml:31-43,482`;
`prompts/P_ALL_graph_orchestrator.prompt.v1.md:17-25,34-37`), but the only
shipped pre-P0 controller implementation merely trusts the submitted digests
and self-asserted `artifact_hashes_valid: true` field. Because this admitted
event alone selects PASS, the original evidence-backed-acceptance property is
not enforced.

**Required closure in a new version.** Admission must receive canonical
artifact/evidence locations or bytes, recompute every digest, recompute the
event id from the canonical event body, and reject nonexistent, unreadable,
mismatched, or out-of-scope evidence. Add byte-flip, nonexistent-evidence,
fabricated-hash, and forged-event-id mutations to the shipped self-test.

### 2. High — resume provenance is bound, but continuation consumption is not

**Resolved subparts.** `PHASE_CONTROLLER` now owns continuations and commands
(`graph_engineered_subscription_execution.plan.v1.yaml:31-43`). Continuations
carry source event/checkpoint, run/node/next-attempt, and all pinned digests
(`contracts/continuation.schema.v1.json:4-10`), and commands bind the exact
continuation digest (`contracts/resume_command.schema.v1.json:4-6`). The helper
correctly rejected every independently altered current digest, source,
run/phase, command binding, and attempt (`tools/validate_plan.py:73-91`).

**Unresolved High defect.** The typed runtime state has
`consumed_continuation_ids` (`contracts/runtime_state.schema.v1.json:18-22`),
but `validate_resume()` neither reads nor atomically updates it
(`tools/validate_plan.py:73-91`). The continuation schema instead requires the
immutable submitted record to say `consumed: false`
(`contracts/continuation.schema.v1.json:4-10`). The same continuation and
command therefore passed twice, and still passed when the supplied current
state included its id in `consumed_continuation_ids`. This directly contradicts
the single-use promise at
`graph_engineered_subscription_execution.plan.v1.yaml:43,483` and
`prompts/P_ALL_graph_orchestrator.prompt.v1.md:38-42`.

**Required closure in a new version.** Resume admission must perform one atomic
compare-and-set over `active_continuation_hash` and
`consumed_continuation_ids`, persist consumption before emitting RESUME, reject
an already consumed id/command id, and prove crash-before/crash-after behavior
in two cold processes. Add exact duplicate-command and consumed-state mutations
to the shipped self-test.

### 3. High — reference topology is fixed, but registry entries are not resolved

**Resolved subparts.** Exact artifact ownership and predecessor/context checks,
typed state predecessor checks, closed contract membership, and local-path
existence now execute at `tools/validate_plan.py:273-331`. Independent missing
local schema, unknown contract, and P1-consuming-P6 mutations were all rejected.

**Unresolved High defect.** A `contract://` consumer is accepted solely because
the key exists in `contract_registry` (`tools/validate_plan.py:303-305`). The
validator never iterates registry entries to prove `schema_ref` exists or that
`resolver` names a valid field of that schema/source. The plan schema only
requires arbitrary nonempty strings for those members
(`graph_engineered_subscription_execution.schema.v1.json:135-137`). Both a
nonexistent registry schema and nonexistent resolver mutation passed. Thus a
registered contract can still be structurally impossible even though the
current registry text looks plausible (`graph_engineered_subscription_execution.plan.v1.yaml:44-52`).

**Required closure in a new version.** Compile every registry entry: require an
existing schema/source, validate its owner, resolve the selector as an exact
typed path, and prove that the result's cardinality/type matches the consuming
port. Add missing-registry-schema and bad-resolver mutations to the shipped
self-test.

### 4. High — ledger keys are typed, but ledger completeness is self-denominated

**Resolved subparts.** Every node now carries the exact typed phase/subtask key
templates and replay policy (representative P6 at
`graph_engineered_subscription_execution.plan.v1.yaml:416-421`), and the plan
schema closes those expressions
(`graph_engineered_subscription_execution.schema.v1.json:139-148`). The ledger
schema types phase, attempt, execution-contract, subtask keys, input digests,
output hashes, and state (`contracts/phase_ledger.schema.v1.json:4-10`). The
helper rejects wrong phase keys, duplicate subtask ids, collided keys, stale
bindings, and false completion (`tools/validate_plan.py:104-123`).

**Unresolved High defect.** Neither a node nor compiled state declares the
required subtask-id set. The ledger supplies both `required_subtask_ids` and the
matching `subtasks`, and the helper compares only those two self-authored values
(`tools/validate_plan.py:114-123`). A P6 ledger containing one invented committed
subtask therefore passed as `complete: true`, although P6 is a multi-effect
phase and its required work exists only in prompt prose. This cannot establish
the plan invariant that committed subtasks are total before PASS
(`graph_engineered_subscription_execution.plan.v1.yaml:482,490`).

**Required closure in a new version.** Add an exact compiled
`required_subtask_ids` denominator to each node, include its digest in activation
state/event admission, pass the node/compiled denominator into ledger
validation, and reject missing, extra, renamed, reordered, or prompt-inferred
subtasks. Then cold-replay the exact ledger and prove committed operations are
observed rather than executed.

## Denominator cross-field check (v3 Medium, non-blocking to the C/H rule)

The former count and within-category duplicate-id defects are fixed by
`validate_denominator()` (`tools/validate_plan.py:94-101`), and the schema now
requires every named mutation kind
(`contracts/coverage_denominator.schema.v1.json:8-19`). The source binding is
still not relationally validated: arbitrary `source_digest`, a changed record
`source_hash` without a corresponding source-digest change, and an id reused in
another category all passed schema plus helper. This v3 Medium finding therefore
remains unresolved. A new version should define the canonical source-set digest,
recompute it, and explicitly choose and enforce either global or category-scoped
ID uniqueness.

## Final closure decision

The green bootstrap and self-test do not supply evidence-backed dispositions for
the accepted counterexamples above. Because all four v3 Critical/High findings
remain materially unresolved, the only conforming closure verdict is:

**FAILED_TARGETED_CLOSURE — UNAPPROVED_REQUIRES_NEW_VERSION.**
