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

## Required content

Cover every area below, or mark it not applicable **with a reason**. Missing
evidence is documented as a gap, never a silent omission — that distinction is
what makes the document trustworthy at all.

| Area | The guide must explain |
|---|---|
| Purpose and boundary | Users and actors, intended outcomes, owned responsibilities, entry/exit interfaces, external systems, exclusions, assumptions. |
| Architecture | Components, responsibilities, dependencies, data movement, trust boundaries, and how the parts compose into a system. |
| Graph behavior | Entries, nodes/stages, routes, branches, loops, joins, termination, human or external handoffs, failure paths — and whether the graph is framework-defined or prompt-orchestrated. |
| Node and tool contracts | Purpose, inputs, outputs, model or prompt behavior, tools and side effects, timeouts, retries, repair, failure and terminal semantics. |
| State and data | Important fields, types, validation, readers and writers, lineage, persistence and checkpoints, mutation/merge rules, versioning, redaction, retention. |
| Route contracts | Source, destination, trigger or guard, decision mechanism, state transferred, fallback, resulting outcome. |
| Models and prompts | Model roles, selection and fallback, prompt responsibilities, structured outputs, limits, configuration that changes behavior. |
| Deployment | Environments, hosting model, runtime topology, services, workers, stores, queues, networks, ingress/egress, scaling, HA, external dependencies. |
| Configuration and release | Parameters, defaults and allowed values, source and scope, sensitivity, behavioral effect, reload behavior, build and promotion path, migrations, flags, rollback, compatibility. |
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
