---
name: graph-system-document
description: Creates or updates the detailed architecture and operations guide for a graph-based AI system as one self-contained, diagram-rich HTML page — boundary, components, graph and route behavior, node and tool contracts, state, models and prompts, deployment, configuration, security, observability, operations and recovery — written only from inspected evidence, with declared/observed/inferred/unknown kept visibly apart, run paths and failure loops drawn as generated SVG rather than described, and deterministic gates for secrets, links, self-containment, accessibility, coverage and freshness. Use this whenever someone wants real documentation of a running or planned agent system: "document this pipeline", "write the architecture doc for our LangGraph app", "we need a runbook and system guide for the orchestrator", "onboard a new maintainer onto this agent", "update the system doc, the graph changed", "what does an operator need to know to run this?", "produce an ops guide for the multi-agent workflow", "make the system doc something people will actually read", or when a design review, handover, audit or on-call rotation needs a document that does not require reading the repo to trust. Also use it proactively whenever someone is about to hand-write architecture documentation for a system with nodes, routes, prompts or agents — prose written from memory is exactly how a guide ends up asserting that declared behavior was observed, inventing security controls nobody implemented, and hiding missing evidence behind confident writing. Not for diagramming a plan or proposal (that is plan-infographic) and not for rendering an already-compiled manifest as a picture (that is graph-doc-graph-visualize, which this skill calls when a manifest exists).
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Documenting a graph-based system so a maintainer can trust it

The deliverable is one guide that a design reviewer, a maintainer, or an
authorized operator can act on **without reconstructing the system from the
repository**. That is the whole bar. Everything below serves it.

Ship it as **one self-contained HTML page** — no CDN, no remote font, no linked
image, no required JavaScript. That format is not decoration: it is what lets
the run path be a diagram instead of a paragraph, the evidence state be visible
at a glance instead of buried in a sentence, and the whole thing still open on a
laptop with no network during the incident it was written for.

Three forces pull against each other here, and holding all three is the skill:

- **Depth is mandatory.** A short, tidy document that omits deployment, state
  handling, failure paths or recovery has not been simplified — it has been
  hollowed out, and the reader will find out at 3am.
- **It has to be read.** Depth nobody gets through bought nothing. Thirteen
  identical grey sections and eight-column tables are a wall; the reader
  abandons it and goes back to the repo, which is the outcome this skill exists
  to prevent.
- **Process is not mandatory.** Use the least expensive workflow that produces
  that depth. Add a control only when it mitigates a consequence, a disclosure
  risk, or an audit requirement you can name. Handoff artifacts, claim
  registries and approval steps for harmless drafting are cost without a reader.

The failure this skill exists to prevent is not a thin document. It is a
**confident** one: plausible completion where evidence ran out, declared
behavior narrated as if it had been observed, generic security controls the
system never implemented, a graph node inferred from the order of paragraphs in
a README. Those defects are invisible in the prose and expensive in production —
and a handsome page makes them *more* persuasive, not less, which is why the
evidence discipline below is non-negotiable in exchange for the visual budget.

## The six stages

Run these internally. A stage does not need a persisted artifact just to hand
work to the next one — that is bookkeeping, not evidence.

**1 · Frame.** Establish the system, the audience, the deliverable, which
sources you may read, where output may be written, what may not be disclosed,
and whether this is creation or update. Ask only about gaps that would change
the result or make it unsafe — guessing the audience is recoverable, guessing
that an internal endpoint is publishable is not.

**2 · Inspect.** Read the code, prompts, graph definitions, schemas,
configuration, deployment material, tests, traces, policies and runbooks.
Follow dependencies as far as explaining behavior requires. Record what you
could not read as much as what you could.

Build the register in code, not prose:

```bash
python3 <skill-dir>/scripts/source_register.py 'src/**/*.py' 'prompts/**' \
  deploy/ --root . --json .doc-run/sources.json --md .doc-run/sources.md
```

It records path, git revision, freshness and digest per file, and reports
patterns that matched nothing — those are evidence gaps, and it will tell you
so rather than let them vanish.

**3 · Model.** Reconstruct architecture, execution paths, state, interfaces,
dependencies, controls, failure behavior and operational procedure. Resolve
conflicts where evidence allows; where it does not, the conflict itself is a
finding worth writing down. Leave the stage only when every material assertion
is supported, qualified, or explicitly marked unknown.

A fact restated in two places is two chances to be wrong, not one extra
confirmation. Before Write, or as a last pass before Verify, find every fact
the draft states more than once — an edge list, a node's inbound/outbound
count, a state-machine's legal transitions, an artifact's shape — and check
both statements against each other and against the source. A silent mismatch
between two sections is exactly the kind of conflict this stage exists to
catch; tag it `conflicting` rather than letting the second mention quietly
overrule the first. The same pass catches uneven depth between comparable
items: if one node's or artifact's I/O is documented down to its schema and a
sibling of similar importance gets only a name — or one terminal
outcome/exit code gets a full worked payload and a sibling outcome of equal
operational weight gets only a label — either match the depth or say why the
difference is real. Re-run this pass after any late edit, not only once
before the first Verify: a fix made to resolve one contradiction can silently
introduce another if the surrounding claims aren't re-checked too.

A table that claims exhaustive coverage — "every node," "the full N-member
set," a predecessor/successor column meant to make every ID lookupable — is a
correctness claim about completeness itself, and spot-fixing one reported row
leaves the same claim false everywhere else it wasn't checked. Derive that
kind of table from the union of every distinct edge-declaring structure in
the code (static guard tables, dynamic dispatch tuples, unconditional edges,
retry/resume/retest destination sets), not by patching the specific row a
reviewer happened to name. A script that mechanically unions those sources
and diffs the result against the drafted table is worth writing once a table
like this exists; re-derive it wholesale after any edit that touches routing,
rather than trusting the previous version's row was already exhaustive.
introduce another if the surrounding claims aren't re-checked too.

**4 · Write.** Produce the guide, plus only the visuals that materially improve
understanding. Start from `assets/guide_template.html` — a skeleton carrying the
page structure, evidence chips, callouts, print stylesheet and figure styling,
not a form to fill. Delete what does not apply (with a stated reason), expand
what carries the system's real complexity, and remove every `<!-- FILL -->`
before shipping; the verifier fails on any that survive.

Render diagrams rather than plotting them by hand:

```bash
python3 <skill-dir>/scripts/diagram_svg.py --print-schema   # spec format
python3 <skill-dir>/scripts/diagram_svg.py run-path.json >> guide-fragment.html
```

It takes a small JSON spec — `flow`, `stack` or `sequence` — computes the
layout from the content, routes repair and failure back-edges through a gutter
beneath the flow, and emits a complete `<figure>`: inline SVG plus caption,
scope, evidence status and a text-equivalent table. Then it inspects its own
render for clipping, overlap and orphan nodes and refuses to emit a broken one.
Paste the figure straight into the page.

**5 · Verify.**

```bash
python3 <skill-dir>/scripts/verify_doc.py --doc docs/system-guide.html \
  --allow-dir docs --attempt-state .doc-run/repair.json \
  --json .doc-run/verify.json
```

This settles the mechanical gates: secrets, link and anchor resolution, remote
resources, output containment, coverage of the required areas, figure captions
and text equivalents, alt text and SVG labelling, `lang`/viewport/title, leftover
placeholders, evidence labels, presence of a verification section. It
deliberately does **not** judge accuracy, usefulness or whether the page is
pleasant to read — read for those yourself, against the audience you framed in
stage 1, and open the file in a browser before you hand it over.

**6 · Deliver.** Writing a *new* file inside the authorized location needs no
permission — asking for it is friction with no risk behind it. Before
**overwriting an existing deliverable or publishing anywhere external**, show a
concise change-and-risk summary and get approval. Hand over the guide plus a
compact verification summary: sources inspected, freshness, checks run,
unresolved gaps, and whether the next action needs approval.

Use deterministic code for discovery, hashing, diffs, schema parsing, link
checking, secret scanning, diagram layout and retry counting. Model tokens spent
narrating bookkeeping — or nudging SVG coordinates — are tokens not spent
understanding the system.

## When the answer is not an HTML page

HTML is the default because system guides are long, visual and read under
pressure. It is not a policy that everything becomes a web page. Write Markdown
instead when the artifact is short enough to hold in one screen, when it is
consumed by a tool or another agent rather than a person, when the repository's
review process depends on readable diffs of the prose, or when the user asks
for it. `assets/guide_template.md` is the skeleton for that case, and
`verify_doc.py` gates either format; the content and evidence requirements do
not change with the container. Say which format you chose and
why in one line, and move on — this is not a decision worth a paragraph.

## Evidence discipline

Every claim in the guide belongs to one of four states, and conflating the
first two is the most common way these documents mislead.

| Label | Means | Treatment |
|---|---|---|
| **Declared** | A design, config, policy, prompt, schema or runbook says so. | Never imply it executed successfully. |
| **Observed** | A trace, test or log demonstrates it. | Name the scope, version or time — and the paths that were *not* exercised. |
| **Inferred** | Follows from inspected evidence, but is neither stated nor executed. | Show the reasoning. Do not dress it as observation. |
| **Unknown / conflicting** | Evidence absent, insufficient, stale or contradictory. | Preserve the uncertainty and say what it costs the reader or operator. |

Label where it matters — a section, a table row, a diagram element, an
important claim. Sentence-level claim IDs are not required by default; they are
an escalation (see `references/assurance.md`).

Never expose secrets, credentials, private endpoints, restricted data, or
implementation detail the framing put out of bounds. Documenting *that* a
credential exists and where it is managed is right; documenting its value never
is.

**Four things not to do**, because each is a specific way these guides go
wrong: do not infer formal nodes or edges from narrative order alone; do not
treat declared behavior as proof of execution; do not invent generic security
controls that sound standard; do not conceal missing evidence behind polished
prose. Silence reads as coverage.

## Concreteness: a name is not documentation

A diagram box or table row that says `model_jobs.v1.yaml — 8 frozen jobs` or
`--engine-root / --curriculum` tells an operator the thing exists. It does not
tell them what it looks like, what a real value is, or how to use it — and an
operator who cannot answer "what do I actually type / put in this file" has
not been documented to, no matter how many boxes are on the page. This is a
specific way confident-but-useless output happens: every node in the required
content areas is present, every label carries an evidence chip, and the guide
is still unusable, because "declared: source-fetch allowlist + digest" is a
description of a file, not the file.

For every input, configuration file, CLI surface, prompt/schema pair, or
parameter that the guide names as something an operator or maintainer
interacts with, show a **worked example** somewhere in the guide, near where
it is first named — not just its label:

- A **file-shaped input or config** (a manifest, a policy file, a job
  registry, a prompt) gets a short real excerpt — pulled from an actual file
  in the repository, a fixture, or a test — not an invented one. If the real
  file is large, quote the smallest slice that shows its shape (one job entry
  out of eight, one profile out of a host allowlist), and say where the rest
  lives.
- A **CLI surface or invocation** gets at least one fully worked example with
  real, plausible values filled in — not only the flag names, and not only a
  placeholder like `PATH` for every argument. Show what the operator's
  terminal actually looks like for the common case, then vary it for the
  other modes.
- A **parameter, flag or config key** gets its actual accepted values, default,
  and what changes when it's set — read from the argument parser, schema or
  validation code, not paraphrased from a comment.
- Pull these examples from `tests/`, `fixtures/`, sample data already in the
  repository, or the validation code's own accepted/rejected shapes — that
  keeps them both real and free to write (see Evidence discipline: an example
  copied from a fixture is `observed`; one you invented to illustrate a shape
  is `inferred`, and must say so).
- When more than one real example is available, prefer the one that shows the
  field or file **populated and in active use** over a minimal or empty
  fixture. A degenerate example (`"providers": {}`) technically satisfies "an
  example exists" but teaches the reader nothing about the common case — if
  only a degenerate example is available, say so explicitly rather than
  letting it stand in silently for the real thing.
- The **final deliverable's location and shape** — where completed output
  actually lands under the output root, and its filename or directory
  pattern — is exactly as concrete as any input. An operator who finishes a
  run must be able to find what they produced without guessing; "collect
  artifacts from the output root" is a name, not an example.

This is not a mandate to document everything exhaustively down to every field.
It is a mandate that whatever the guide *does* claim an operator needs to
touch, it shows rather than merely names. A figure or table introducing a set
of inputs should be followed by, or linked to, the place in the guide where at
least one of them is shown concretely — a reader should never have to leave
the guide and go read the source to find out what a "frozen job" or a
"retrieval profile" actually contains.

## Naming and disambiguation

A system accumulates codenames, generation labels, ID prefixes and short
overloaded words faster than a first-time reader can track them. Two specific
failures recur and are cheap to prevent — cheap enough that leaving them in is
a documentation defect, not an acceptable simplification:

- **Collision with an unrelated repo concept.** If an internal codename could
  plausibly be mistaken for something else that exists in the repository — a
  directory, a file, a different subsystem — because it shares a word (a
  runtime generation called "Plan 26" versus a top-level `plans/` directory),
  say explicitly, at first use, that they are unrelated. Check for this during
  Inspect: a quick grep of the codename against the repository's top-level
  names is enough to catch it before a reader has to.
- **Reuse of one word for two mechanisms.** If the same term legitimately
  means two different things in the system (a structural "unreachable
  frontier" versus a checkpoint "resume frontier"), never let the guide use
  the bare word for both without a qualifier at each use.

Two more apply to vocabulary generally:

- If a term is used as a defined technical unit with a specific system
  meaning narrower than its everyday sense ("activation", "episode",
  "correlation key", "frozen"), define it once — in prose, not just a
  diagram legend — before or at its first use, and keep reusing that same
  definition rather than letting the reader infer its scope from context.
- Introduce any naming or ID convention that a diagram depends on (prefixes,
  ID formats, generation numbers) in prose *before* the first figure that
  uses it, not after. A reader should never meet an unexplained ID and have
  to hold it in suspension until a later section defines the scheme.

A glossary built only from the terms the writer already suspects are
confusing will miss the ones that aren't obviously jargon but are load-bearing
anyway — a gating concept used in a dozen node contracts is a bigger gap
undefined than a codename used twice. Before shipping, do one mechanical
pass over the draft: list every bolded or `coded` term that recurs across
three or more sections or drives a routing/admission decision, and check each
one against the glossary. A term failing that check is exactly the kind of
gap a reader can't route around by re-reading harder.

## Required content

Cover every area below, or mark it not applicable **with a reason**. Missing
evidence is documented as a gap, never a silent omission — that distinction is
what makes the document trustworthy at all.

| Area | The guide must explain |
|---|---|
| Purpose and boundary | Users and actors, intended outcomes, owned responsibilities, entry/exit interfaces, external systems, exclusions, assumptions. |
| Architecture | Components, responsibilities, dependencies, data movement, trust boundaries, how the parts compose into a system — and, for each input the system reads at its boundary, a worked example of what that input actually contains (see Concreteness). |
| Graph behavior | Entries, nodes/stages, routes, branches, loops, joins, termination, human or external handoffs, failure paths — and whether the graph is framework-defined or prompt-orchestrated. |
| Node and tool contracts | Purpose, inputs, outputs, model or prompt behavior, tools and side effects, timeouts, retries, repair, failure and terminal semantics for every node that appears in a diagram, route table or run-path narrative — an ID the reader meets in a figure but cannot look up is a gap, not an acceptable abbreviation — with a real example input/output or invocation for at least the nodes a maintainer is most likely to touch or debug. |
| State and data | Important fields, types, validation, readers and writers, lineage, persistence and checkpoints, mutation/merge rules, versioning, redaction, retention. |
| Route contracts | Source, destination, trigger or guard, decision mechanism, state transferred, fallback, resulting outcome. |
| Models and prompts | Model roles, selection and fallback, prompt responsibilities, structured outputs, limits, configuration that changes behavior. |
| Deployment | Environments, hosting model, runtime topology, services, workers, stores, queues, networks, ingress/egress, scaling, HA, external dependencies. |
| Configuration and release | Parameters, defaults and allowed values (as real values, not "see config"), source and scope, sensitivity, behavioral effect, reload behavior, build and promotion path, migrations, flags, rollback, compatibility. |
| Security and privacy | Identity, authn, authz, privileged access, data classes, protection, secrets handling, isolation, network controls, audit, retention, incident ownership, and verified gaps. |
| Observability | Health and success signals, logs, metrics, traces, dashboards, run identifiers, alerts, thresholds, ownership, blind spots. |
| Operations and recovery | Prerequisites and roles, safe start/stop/trigger procedures, expected output, prohibited actions, triage, retry, resume, rollback, restore, backup, escalation, and the conditions under which an operator must stop. |
| Limitations and verification | Sources inspected and excluded, freshness, conflicts, unknowns, untested paths, assumptions, known risks, and what would invalidate this guide. |

`references/content-standard.md` expands each area with the questions a reader
actually arrives with and the shortfalls that keep recurring. Read it when an
area is unfamiliar, when the system is large, or when a section feels like it
is coming out generic — generic is the symptom of writing from expectation
instead of evidence.

## Visuals

Draw a diagram when a relationship costs the reader more in prose than in
pixels; use prose or a table when it does not. A system containing a graph does
not automatically require a picture of it, and two or three diagrams is usually
the right number for a guide — each extra one is a maintenance burden forever.

| Reader question | Archetype | Usually lands in |
|---|---|---|
| What runs, in what order, and where does it go wrong? | `flow` | Graph behavior |
| What are the parts, and which side of a boundary is each on? | `stack` | Architecture, deployment |
| Who does what to whom, in what order? | `sequence` | Operations and recovery |

- **Draw the failure paths.** A flow with only the happy path tells a reader in
  an incident that they are off the map. Repair and failure edges are their own
  edge kinds, and back-edges get routed through a gutter so the loops stay
  readable instead of crossing the forward flow.
- Every visual carries a title, a takeaway, its scope, its evidence status and a
  text equivalent — `diagram_svg.py` emits all five, so the cheap path is also
  the compliant one. No meaning may rest on color alone.
- A visual may not invent a component, edge, control, bound, parameter effect,
  execution result or confidence level. It renders the evidence; it is not a
  second opinion about the system. Mixed evidence in one picture is normal —
  nodes read from a graph definition are `declared`, the path a trace exercised
  is `observed`.
- When the renderer reports overlap, clipping or an orphan node, treat it as a
  finding about the spec. An orphan usually means an edge exists that you have
  not found in the evidence yet.

When the system already has a compiled workflow manifest,
`graph-doc-graph-visualize` renders it and self-inspects the result; prefer it
over re-specifying the graph by hand. Other renderers (D2, Graphviz, Mermaid)
are allowed, but anything you use must end up inline in the page — a linked
image breaks the self-containment the format exists for.

`references/html-craft.md` covers page rhythm, when a diagram earns its place,
engagement that is not decoration, and the anti-patterns. Read it when the page
is coming out uniform or you are inventing layout the template does not have.

## Updating an existing guide

### Filename and version

A guide's identity is its filename: `<system>_system_guide.v<N>.<ext>` (for
example `curriculum_factory_system_guide.v1.html`). Find the existing guide by
that pattern rather than assuming a fixed name — a directory can hold more
than one system's guide.

- No file matching the pattern exists → this is a **creation**. Write `v1`.
- A file matching the pattern exists → this is an **update**. Read `N` from
  its filename, write the patched guide to `v<N+1>`, and leave `v<N-1>` and
  earlier in place — they are the diffable history, and deleting them defeats
  the point of versioning. Do not edit a versioned file in place.
- Record the new version number, the date, and a one-line summary of what
  changed in the guide's own "Limitations and verification" section. That is
  the guide's changelog; it does not need a separate file. Append the new row
  in chronological order — a changelog a reader has to re-sort to trust is a
  changelog that reads as untrustworthy.
- A version number lives in more than one place on the page — the filename,
  the header/title badge, the footer, and any "evidence basis: repository at
  `<rev>`" stamp are all claims about the same fact, and an update that
  touches the changelog table but leaves an older version number or an older
  commit hash sitting in the header or footer is a self-contradiction the
  reader meets before reaching a single word of content. Grep the whole page
  for the previous version string and the previous revision hash before
  shipping, and update every occurrence together, not just the table.
- If a changelog entry cites a running total (gaps closed to date, files
  inspected, whatever cumulative count), state it as a single carried-forward
  number — this version's total is last version's stated total plus this
  round's own delta, taken as already-settled fact, not re-derived by
  re-summing every prior round from scratch. State that arithmetic once. A
  sentence that restates the same total three different ways — as an opening
  count, then as a supporting sum, then as a closing figure — multiplies the
  chances one phrasing drifts from the other two, which is exactly how this
  defect has recurred even in versions written specifically to fix it. One
  number, stated once, is not a simplification here; it is the fix.

Regeneration throws away correct, reviewed work and rewrites it into slightly
different words, which makes the diff unreadable and hides the real change.
Compare instead:

```bash
python3 <skill-dir>/scripts/source_register.py <same patterns> \
  --merge .doc-run/sources.json --json .doc-run/sources.json
```

Rows come back marked added / changed / unchanged / gone. Update the sections
and visuals those changes touch, recheck the dependencies of changed evidence,
re-render only affected visuals, and preserve unaffected material that is still
correct. Regenerate wholesale only when structural change makes that safer or
cheaper than surgery.

Keep the diagram specs beside the guide (`docs/assets/*.diagram.json` or
`.doc-run/`) so a changed route means editing four lines of JSON and re-pasting
one figure, rather than re-deriving a picture from scratch. A guide whose
diagrams are expensive to update is a guide whose diagrams go stale first, and a
stale diagram is believed longer than stale prose.

Do **not** preserve a claim or a visual whose supporting evidence is now stale
or contradicted — inherited text that no longer matches the system is worse
than an absent section, because it still reads as verified. Show a concise
semantic diff before overwriting or publishing.

## Quality gates

| Gate | Passes when |
|---|---|
| Scope and completeness | Applicable areas covered; exclusions and missing evidence explicit. |
| Accuracy and evidence | Material assertions trace to inspected evidence and are labeled correctly. Sample sources by default. |
| Concreteness | Every input, config file, CLI surface and parameter the guide introduces is paired with a real worked example (excerpt, invocation or value), not only a name and an evidence chip. |
| Security and disclosure | No secrets or prohibited detail; security claims describe evidence, not aspiration. |
| Operational usefulness | An authorized reader can understand state, perform routine actions, recognize failure, and find recovery or escalation. |
| Links and outputs | Internal links and anchors resolve; output stays inside the authorized location. |
| Self-containment | Nothing loads over the network; the page is complete with JavaScript off and prints legibly. |
| Rendered quality | Deliverable and visuals readable at intended viewports — no clipping, overlap, broken layout, or color-only meaning. Every visual has a caption, evidence status and text equivalent. |
| Freshness | The guide records what was inspected and when or at which version; stale evidence disclosed. |

`verify_doc.py` covers scope structure, disclosure, links, self-containment,
figure and alt-text discipline, page hygiene, leftover placeholders, evidence
labeling and containment; `diagram_svg.py` covers diagram geometry. Accuracy,
usefulness and whether the page is worth reading need you to read it and to open
it in a browser.

**Repair is bounded at two attempts for the same failure.** Stop earlier if the
output is unchanged or oscillating. `--attempt-state` tracks the failure
signature across runs and will tell you when to stop. A third attempt at the
same failure is almost never a fix — report it as an unresolved gap and let the
user decide. Burning tokens in a loop is not diligence.

## When to add more assurance

The default workflow above is complete. Escalate only on a named trigger, and
say which one when you do — complexity without a stated risk is the thing this
specification exists to remove. The trigger table, what each adds, and what
each specifically does *not* justify adding are in
`references/assurance.md`. Read it before proposing any extra control.

## What a run produces

1. The detailed architecture and operations guide — one self-contained HTML
   file (or Markdown, where that was the right call and you said why).
2. Its diagrams, inline, each with a takeaway, scope, evidence status and text
   equivalent; keep the specs that produced them if the guide will be maintained.
3. A compact verification summary — sources inspected, freshness, checks
   performed, unresolved gaps, and whether approval is needed next.

No JSON artifact is mandatory. The summary can live in the guide, in the reply
to the user, or beside the deliverable when maintenance will continue.

The acceptance test is a reader's, not a checklist's: **could a competent
maintainer or operator who has never seen this system act on the guide, and
tell the difference between what it verified and what it assumed?** A page that
looks authoritative and quietly fails the second half is worse than the plain
document it replaced.
