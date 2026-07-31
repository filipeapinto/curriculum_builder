# ELEGOO Meta-Curriculum Prompt — v6

Build and prove a curriculum generator. Do not write curriculum.

## Mission

Create `templates_v7/` — a deterministic controller plus small bounded worker
prompts — and prove it well enough that a full run needs nobody watching. Its
human-readable runtime contract is:

`V7/component_lab_orchestrator_prompt.v7.md`

Produce exactly one live lab, L01, as evidence the generator works. Nothing else.

The v3 generator failed eight overnight runs without producing one accepted lab.
Two rebuilds followed; the second stopped at `META_DRIFT_STOP` with four failed
gates. Every constraint in this contract traces to one of those failures, recorded
in `policy/failures.v1.yaml`.

## Write boundary

```text
CREATOR     = the directory containing this prompt's `meta_prompt/` folder
META_PROMPT = CREATOR/meta_prompt/meta_curriculum_builder.prompt.v6.md
ASSETS      = CREATOR/meta_prompt/assets
LEGACY      = CREATOR/plans/legacy_v3
OUTPUT_ROOT = supplied by --output-root; required, no default
V7          = OUTPUT_ROOT/templates_v7
```

`CREATOR` is **derived, never written down**: resolve it from this file's own
location. An absolute path here would be correct on exactly one machine and would
silently resolve to nothing on any clone, which is the failure this line replaces.

`OUTPUT_ROOT` is **required at invocation** and has no default. It is deliberately
outside `CREATOR`: the inputs are immutable and a run writes nothing into them.
Refusing to guess is the point — a default would eventually be a directory holding
someone else's evidence. `policy/controller.v1.yaml` already declares the flag.

Write only to `V7`. Everything else is immutable, `CREATOR` included. The v3, v4 and
v5 attempts are not named here as paths: they may not exist at any location, and
naming a directory that is not there protects nothing. They are never read, and every
diagnosis drawn from them is quoted in full in `policy/failures.v1.yaml`.

All names `V7` creates are lowercase, versioned `.vN` where versioned at all.

If `V7` exists at startup, stop as `META_SYSTEM_FAILURE` with failure id
`PRECONDITION-OUTPUT-ROOT-EXISTS`, before any artifact and before any model call.
Report the occupied path and the next free version name. Never auto-increment,
merge, delete or overwrite: choosing which evidence to keep is a human decision an
unattended run must not make. Fail closed rather than ask.

Never create a live dossier for any lab beyond L01 during this task.

## Assets

This file is deliberately short: it carries the mission, the boundary, the order of
work and the report. The rules that need room to be exact live in `ASSETS`, and they
bind exactly as this file does. A `section` asset is part of this contract and is
read whole, in the order below; **this file plus those six is the contract**, and a
rule is no weaker for having been written in the asset that had room for it.

| Asset | Kind | Carries |
|---|---|---|
| `meta_prompt/assets/inputs.v1.md` | section | every authorized input, the retained contracts, the precedence that settles disagreement, and the rule against a hardcoded lab count |
| `meta_prompt/assets/architecture.v1.md` | section | what the generator must be — code decides, models write, twelve isolated reviews — and what a lab must be |
| `meta_prompt/assets/routing.v1.md` | section | which model may serve which task, the invariants no data file can express, and what is stated rather than enforced |
| `meta_prompt/assets/proving.v1.md` | section | the six gates in order, and everything `META_ACCEPTED` requires |
| `meta_prompt/assets/logging.v1.md` | section | the action log, the convergence loop, the drift stops, and the three terminal states |
| `meta_prompt/assets/deliverables.v1.md` | section | what `V7` must contain when the run ends |
| `meta_prompt/assets/component_lab_template.v1.md` | companion | lab structure in prose — tone, child-language rules, safety baseline |
| `meta_prompt/assets/pedagogy.v1.md` | companion | why each pedagogy field exists, never what its value is |
| `meta_prompt/assets/model_selector_prompt.v1.md` | companion | the selector's own prompt, read by the selector call |

A `companion` is not part of this contract. It is an input, read where a section
asset says so and ranked where `meta_prompt/assets/inputs.v1.md` ranks it — below
every section, above the project prose.

Nothing else belongs in `ASSETS`. A file there that no row above names is prose with
no owner, and prose with no owner is how a contract acquires a second author.

## Execution

1. Resolve `CREATOR` from this file's location and read `--output-root`. Refuse to
   start if it was not supplied.
2. Read every `section` asset in the table above, in the order given. A run that
   begins before them is executing a fragment of its own contract.
3. Check the startup precondition: if `V7` exists, stop as `META_SYSTEM_FAILURE` with
   failure id `PRECONDITION-OUTPUT-ROOT-EXISTS`, before any artifact and before any
   model call.
4. Create `V7` and `V7/test_results/`, and nothing else. This is the only write that
   precedes the logger, and it exists because the logger must have somewhere legal to
   append: authorized writes are confined to `V7`, so `V7` has to exist before the
   first record can be written. Creating it is not logged, because the log does not
   exist yet; it is reconstructible from the directory's own timestamp.
5. Build the logger. Pass its proving tests before creating any other artifact. From
   this point on every action is logged before it is taken.
6. Validate every manifest against its schema. Read no value before it validates.
7. Write the v7 meta state; record authorized roots, and record the contract hash
   over this file and its `section` assets together.
8. Inspect `plans/legacy_v3/` and write failure→fix→test traceability for every id in
   `policy/failures.v1.yaml`.
9. Design v7: canonical data, controller, runtime prompt, worker contracts.
10. Implement controller, prompts, schemas, selector, renderers, audits, reports.
11. Run gates 1–3.
12. Run gate 4 — one real call per route.
13. Run gate 5 — golden L01, including forced interruption, resume, and page
    inspection of the shipped PDF.
14. Drift-audit before and after implementation, tests and revisions.
15. Revise only affected artifacts until a terminal state.
16. Write `V7/remediation_report.md` and the full-run command, only if earned.

Log the planned action before making any change. Use conservative documented
defaults; do not ask the user for ordinary implementation decisions. Stop before
exceeding any limit and preserve the safest resumable checkpoint. The gates, the
release conditions and the three terminal states this list ends in are stated in
`meta_prompt/assets/proving.v1.md` and `meta_prompt/assets/logging.v1.md`.

## Final response

Report: terminal state; `V7` and golden-L01 paths; write-scope and drift results;
every gate result; the golden PDF and resume outcome; the log path, hash, `ACT`/
`EXEC` totals and pairing result; each B1–B4 failure beside its evidence of
correction; meta-revision and resource totals; unresolved failures and the safest
restart point; and the full-run command only on `META_ACCEPTED`.

An `ACT` is appended when an action **starts** and again when it **ends**, so a
started record is not a completed one; an `EXEC` records a failure and closes the
start it terminates. Report the pairing, not the raw count, and do not present the
failure records as a general success log. Never claim the curriculum is
complete unless every lab has been live-generated and accepted and the final
audited workbook exists.
