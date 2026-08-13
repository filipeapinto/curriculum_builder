# Run 27 N20 recovery plan v2

## Decision

The specification correction passed. Preserve its passing artifact and QA evidence.
The first execution-package correction did not pass and also mutated three v1 files.
Recover the v1 bytes exactly, preserve that failed package and QA session, then create
the corrected execution package in a separate versioned directory.

No production implementation is authorized by this plan.

## Phase A — restore admitted v1 bytes

Restore these exact byte identities before doing any other package work:

| Path | Required SHA-256 |
|---|---|
| `plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py` | `cb530b326bb68964976b5b074fefa43392af83bd5c3c6a76f744991d30b066ee` |
| `plans/27_langgraph_curriculum_factory_remediation/tools/validate_plan.py` | `9f534ba3597d331c6ba6c64551004bf01044fb221298aaccd914d476cdf396d0` |
| `plans/27_langgraph_curriculum_factory_remediation/tools/validate_result.py` | `0beef6ed7c5f7bbba3adf50818c53d86dd5cff1f5cefd2abbd8c629a8f229cec` |

The two validator originals are the corresponding `HEAD` blobs. The checker original
is recoverable from the N10 subagent transcript:

`/Users/filipepinto/.claude/projects/-Users-filipepinto-Projects-curriculum-builder/f7a4ba23-1a53-4fe7-b833-697bb8423c39/subagents/agent-an10-harness-77eaa8bf4b4b8a08.jsonl`

Reconstruct the checker from that transcript's original `Write` event followed by its
two N10 `Edit` events. Do not infer or rewrite its logic. The required digest is the
authority.

After restoration, run the original N10 validation command. It must return `valid:
true`. If any target digest or N10 validation differs, stop.

## Phase B — preserve failed correction evidence

Do not modify or resume:

- `implementation.graph.v2.yaml` at digest
  `f297d6528375eeeda5b97a54d654997a65f5d0c7100cf50b54d71c4ca4763b1a`;
- the existing root `QA/` session `019ffbfc-edce-7750-a58a-a008cefbd95e`;
- its round-1 `PKG-QA-001` finding;
- any v1 N00–N20 result or evidence file.

Treat them as the immutable failed package-correction attempt.

## Phase C — retain the passing specification correction

Retain, without editing:

`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`

Required SHA-256:

`e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`

Retain its witnessed two-round independent `QA_PASSED` session
`019ffbeb-3f45-7440-a83e-aa560938dc98`. Re-run its `verify` command read-only and
require a valid witnessed pass.

## Phase D — create an isolated execution package v2

Create the corrected package only under:

`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/`

It must contain its own:

- `implementation.graph.v1.yaml` (graph semantic version 2);
- changed node prompts;
- node-scoped scanner entry point;
- plan/result validator entry points;
- QA criteria and `QA/` evidence;
- validation evidence and future result/evidence root declarations.

It may import unchanged v1 controller libraries read-only, but it must not edit them.
Every changed behavior requires a versioned entry point inside `execution_package_v2/`.

### Required graph corrections

1. Bind `source_spec` to the passing specification artifact and digest in Phase C.
2. Use a new future result/evidence root; never reuse v1 N00–N20 paths.
3. Move `runtime/langgraph_factory/egress.py` and
   `tests/runtime/test_plan26_egress.py` from N30's write set to N20's write set.
4. N30 lists the N20-owned egress boundary as read-only input.
5. Give every active writable path exactly one owner; reject overlap.
6. N20–N50 invoke the package-v2 scanner with both:
   `--graph <execution-package-v2 graph path>` and `--node <exact node ID>`.
7. N60 alone invokes the package-v2 scanner in complete active-tree mode.
8. Every package-v2 validator and controller command receives or defaults to the
   package-v2 graph. No command may silently load `implementation.graph.v1.yaml` from
   the parent v1 package.
9. The package-v2 plan validator must reject a node-scoped scanner command that omits
   the package-v2 graph binding.

### Required scanner behavior

Node mode scans the intersection of the named node's declared writable active files
with the existing production/test scan roots. It ignores plan scaffolding already
excluded by those scopes. It may narrow by ownership only; it may not weaken term,
credential, guard-region, or occurrence rules. Complete-tree mode preserves the
original production plus active-test semantics.

### Required tests

Prove at minimum:

- original v1 checker and validators retain the Phase-A hashes;
- original N10 result validates;
- package-v2 node mode loads the package-v2 graph;
- N20 node mode includes its newly owned egress implementation and test;
- N20 node mode ignores a later node's owned file;
- a seeded violation in an N20-owned file fails N20;
- the same violation and a later-node violation both fail complete-tree mode;
- N60 is the only node using complete-tree mode;
- no package-v2 write path overlaps another node;
- no runtime, policy, active schema, or production test file was modified during
  package authoring.

## Phase E — independent QA

Start a fresh `qa-gate-codex-run` session in `execution_package_v2/QA/` using the
default app-server transport. Do not reuse or alter the failed root `QA/` session.

The QA criteria must treat v1 files and the failed correction attempt as immutable.
They must explicitly falsify graph-binding behavior, atomic N20 ownership, per-node
scan coverage, N60 whole-tree coverage, result/evidence versioning, source-spec
binding, and absence of production edits.

If QA finds a defect, repair through the gate's normal versioned lineage inside
`execution_package_v2/`; never edit a reviewed artifact in place. Run `verify` after a
pass.

## Terminal handoff

Stop after deterministic validation and witnessed independent QA. Report:

- confirmation of all three restored v1 hashes and valid N10 result;
- unchanged specification digest and verified QA session;
- the passing execution-package graph digest and verified QA session;
- complete changed-file list;
- exact invalidation/restart sequence.

Do not create approval records, approve either digest, edit production, restart N00,
or resume Run 27. Those actions require explicit user approval in a later turn.
