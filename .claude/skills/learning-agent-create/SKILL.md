---
name: learning-agent-create
description: Turns one recommended reviewer agent from a sota_agents.v<N>.json scan into the artifact set that actually constitutes a review agent in this repo — a check id in the right inventory, a failure-ledger entry, an accept/reject fixture pair built from the defect the agent exists to catch, a detector plus gate or an honest deferred obligation, and a dossier carrying its provenance. Use this skill whenever someone wants a recommended reviewer, judge, gate or QA check actually built and wired into the curriculum pipeline — for example "create the agents sota_agents.v1.json recommends", "add the rendering conformance gate", "wire recommendation 3 into the pipeline", "turn this SOTA recommendation into a real check", "we need a Bloom's verifier agent, build it", "implement the reviewer agents from the research scan", or "what would it take to actually add the safety dry-run reviewer?". Also use it proactively whenever someone is about to hand-roll a new reviewer, judge, gate or pedagogy check for generated curriculum content — an agent built outside this pattern is one whose execution status, verdict authority and fixture evidence were each decided ad hoc, and this repo's own failure ledger records what that costs. Not for researching *which* agents to add — that is `learning-agent-research`, and this skill consumes the recommendations it has already verified rather than re-verifying them.
---

# Creating a review agent in curriculum_builder

This skill is a factory. Its input is one recommendation object from a
`sota_agents.v<N>.json` array — the shape `learning-agent-research` produces:

```
{agent, function, what_makes_it_sota, role_in_curriculum_builder, issues_resolved, sources[]}
```

Its output is a real agent in this repository, created the same way every time.

**An agent here is not a prose persona.** Nothing in this repo reads one. An
agent is a **check id with a home, a subject, a detector, and an honest
execution status** — six artifacts, listed in
`references/repo_conventions.md` with the exact contract each must satisfy.
Read that file before writing anything; the contracts are enforced by gates
that will reject a near-miss.

**Handed a whole array?** Build them one at a time, cheapest-and-most-
deterministic first, running the gate suite between each. The order is not
bookkeeping: a deterministic check often makes a later judged one
unnecessary or much narrower — a section that fails a JSON-shape check never
needed four judges to score its prose — and each agent you add changes the
answer to "does an id for this already exist?" for the ones after it.

Two rules carry most of the value here, and both exist because of specific
ways this repo has already been burned.

1. **Never advertise a check you cannot execute.** This repo's own inventory
   header states it: *"Being listed here is not being executed, and the two
   are never conflated."* Every id resolves either to a gate that runs it
   (`verified_by: FR-…`) or to the deferred obligation that would
   (`deferred: RT-…`) — never to nothing, and never to both. The failure
   this prevents is `A5` in `policy/failures.v1.yaml`, and it is precisely
   the failure that produced the recommendations you are now implementing:
   the run under review shipped four broken lessons past a check set that
   *looked* complete. Adding five more inert ids would reproduce the defect
   while appearing to fix it.

2. **The reject fixture reproduces the defect the recommendation names.**
   `issues_resolved` tells you exactly what shipped wrong. Build the reject
   fixture to be that, and assert the specific error code the detector emits
   for it. A fixture that merely fails proves the detector fails on
   *something*; a fixture that fails with the named code proves it catches
   *this*. That is the difference between evidence and decoration, and it is
   why every `Fixture(kind="reject", …)` in `tests/gates/` carries an
   `expected_error`.

## Step 1 — Read the repo, not the recommendation's account of it

The recommendation was written by a research scan that read output artifacts,
not this codebase. Its `role_in_curriculum_builder` is a hypothesis about
where the agent plugs in. Check it against what is actually there:

- `policy/checks.v1.yaml` and every `curricula/*/checks.v1.yaml` — does an id
  for this already exist? Several recommendations describe checks this repo
  has already named (and sometimes already deferred).
- `policy/deferred.v1.yaml` — is the gap already recorded as an `RT-` id
  with a stated blocker?
- `policy/failures.v1.yaml` — is the defect already in the ledger?
- `policy/limits.v1.yaml` — the budget any model-calling agent must fit.

If the check already exists, **amend it rather than adding a competing id.**
Two ids running at the same point on the same input for the same reason are
one agent with a naming problem, and the inventory has no way to tell you
which one is authoritative.

## Step 2 — Reconcile with decisions this repo already made

A recommendation is an argument from the outside literature. This repo has
its own recorded, measured reasons for how it works, and where the two
disagree, the disagreement is the finding — do not silently implement the
recommendation over the top of a decision someone already made and wrote down.

The worked example is real: `REV-JUDGE-SINGLE-CROSS-FAMILY`'s note records
that a twelve-judge panel was retired here because nine cross-family judges
supplied about 2.18 effective votes, the best single judge matched the full
panel, and deterministic checks beat judges by 1.2x to 7x where both were
measured. A recommendation asking for a judge *panel* is therefore not a
straightforward addition — it is a proposal to reverse that.

When you find a conflict, write it down in the dossier: what the
recommendation argues, what the repo already decided, which evidence you
followed and why. Then build the agent this repo can defend. An agent whose
rationale contradicts a note in the file it lives in will be removed by the
next person who reads both.

## Step 3 — Decide placement, and the id

**Which inventory.** If the check's subject is one curriculum's files, or it
asserts something only one subject means (fuse behaviour, breadboard
topology, a specific kit's parts), it belongs in
`curricula/<name>/checks.v1.yaml`. Otherwise it is the engine's and belongs
in `policy/checks.v1.yaml`. Getting this backwards is `G3` — the leak this
repo spent a phase closing, where the engine's inventory held one
curriculum's file paths as the subjects of its checks.

**The id** is `SCREAMING-KEBAB`, matches `^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$`, and
is never `FR-`-prefixed — `FR-` ids are refactor gates, and the prefixes are
what keeps checks and gates apart. Name it for what it asserts, not for the
agent archetype it came from: `RENDER-NO-RAW-STRUCTURED` reads better in a
failure report than `STRUCTURED-OUTPUT-CONFORMANCE-GATE`.

## Step 4 — Decide the verdict design before writing any code

Four decisions, all of which end up visible in `asserts`. The reasoning for
each is in `references/verdict_design.md`; read it before deciding, because
getting these wrong produces an agent that is either toothless or
overconfident, and both are expensive to unwind.

- **Deterministic or judged?** Prefer the cheapest detector that catches the
  defect. Recommendation 5 in the reference scan — *is this section still raw
  JSON?* — catches the systemic root cause of an entire failed run and costs
  one `json.loads()`. Spending a model call to discover that is a choice you
  have to justify.
- **Flags or blocks?** A check blocks only when a wrong verdict cannot
  manufacture the failure. `TEXT-BLOOM-VERBS` flags and never blocks because
  human raters agree with each other on Bloom level 46.58% of the time; a
  blocking check built on that would be a coin flip with the force of a
  schema.
- **Which stage?** `static`, `deterministic`, `golden`, `logger`, or
  `live-capability`. Cheap deterministic checks run before anything expensive
  reviews content that is not yet well-formed.
- **Executed or deferred?** Honestly. If the subject does not exist yet — no
  renderer, no generated unit, no second model family available — the answer
  is `deferred`, with a `blocked_by` that names the real blocker.

## Step 5 — Write the artifacts

In this order, because each references the previous.
`references/repo_conventions.md` gives the exact fields and a worked example
end to end.

1. **Failure entry** in `policy/failures.v1.yaml`, from `issues_resolved`:
   the defect, its consequence, the correction, `verified_by`, and a
   `checks: [<YOUR-ID>]` list. This makes the ledger the file that *states
   the rule*, which is what an inventory `owner` has to be.
2. **Inventory entry** in the inventory Step 3 chose.
3. **Release row** advertising the id at its stage. An id that leaves a
   release table and gains no surface of its own has quietly stopped being
   claimed — that happened here to four ids, and the gate could not see it.
4. **Fixture pair** under `tests/fixtures/`, named
   `<slug>.reject.<ext>` and `<slug>.accept.<ext>`, the reject one built from
   `issues_resolved`.
5. **Detector and gate**, or the **deferred entry**. The detector is a pure
   function returning `list[str]` of `problem-code: human message`; the gate
   wraps it with `Evidence`, the fixture pair, and a one-line stdout summary
   that states its own coverage without overstating it.
6. **Dossier** at `docs/agents/<CHECK-ID>.md` from `assets/agent_card.md`,
   carrying `what_makes_it_sota` and `sources` as provenance.

On provenance: those sources were fetched and verified by the scan that
produced the recommendation. **Do not re-verify them and do not add new
ones** — this skill has no research step and no web access. Carry them
across verbatim, attributed to the scan and dated, so a later reader can tell
a checked citation from one this factory invented.

## Step 6 — Validate

```bash
python3 <skill-dir>/scripts/validate_agent.py <CHECK-ID>
```

This is a preflight, not the authority: it checks the artifact set is
complete and internally consistent — the entry parses, the owner path
exists, exactly one of `verified_by`/`deferred` is present and resolves, a
release pattern advertises the id at its stage, referenced fixtures exist,
and a dossier is present.

The authority is the repo's own suite:

```bash
./tests/run_gates.sh 5
```

Run it and fix what it reports. Do not weaken a gate, a fixture or an
`asserts` string to obtain a pass — `DRIFT-NO-WEAKENING` exists because that
is the tempting move, and a gate edited to accept the thing it was built to
reject is worse than no gate, since it now certifies the defect.

## Logging

Append to `action_log.jsonl` as you go rather than reconstructing at the end.

```bash
python3 <skill-dir>/scripts/log_action.py <log-path> \
  action=decision check_id=RENDER-NO-RAW-STRUCTURED \
  choice="deterministic, blocking, gate-1" \
  reason="json.loads() settles it; a wrong verdict cannot manufacture this failure"
```

The decisions in Steps 2-4 are the ones worth logging in full. Someone will
later ask why an agent flags instead of blocks, or why it sits in the
curriculum's inventory rather than the engine's, and the answer needs to be
recoverable from the record rather than re-derived from scratch.
