# Conditional assurance: escalate on a named trigger, not on a feeling

The default six-stage workflow in SKILL.md is complete. It is not a reduced
version of something better — it is the workflow that satisfies the content and
quality requirements at the lowest cost.

Extra controls exist for real consequences: work that others will build on,
actions that destroy or publish, outputs that will be audited, jobs too large
for one session. Applying those controls to work with none of those properties
buys nothing and costs the reader their attention and the user their tokens.

**The rule:** if you propose escalating, name the trigger and name the control
it adds. Complexity without a stated risk or requirement is non-conforming — it
is the failure mode this specification was rewritten to remove.

## Triggers

### Shared design review, or others will operate on this document

**Add:** a persisted source register (`--json`, kept beside the deliverable);
traceability for the *important* claims — the ones a reader would act on;
named reader scenarios ("an on-call engineer at 3am with a failed run",
"a reviewer deciding whether to approve the new routing layer") checked against
the finished guide; a structured gap list rather than gaps scattered in prose.

**Do not add:** sentence-level claim records, or canonical handoff artifacts
between stages. Both are audit machinery. A reviewer wants to find the claim
that matters and see what it rests on, not read a registry.

### Overwrite, external publication, or sensitive disclosure

**Add:** human approval, presented as a concise semantic diff (what changed in
meaning, not what changed in bytes), plus disclosure findings and known risks.
This is the one place approval is genuinely load-bearing: overwriting destroys
reviewed work and publishing cannot be undone — content sent externally may be
cached or indexed even if deleted afterwards.

**Do not add:** approval before harmless drafting. Asking permission to write a
new file into the location the user already authorized is friction that trains
the user to approve without reading, which is exactly what you need them *not*
to do at the overwrite step.

### Regulated, contractual, safety-critical, or independently audited

**Add:** full claim-level provenance; canonical digests of inputs and outputs;
immutable approval records; independent review by someone other than the
author; complete render records for every visual produced; whatever conformance
fixtures the applicable standard requires.

**Do not add:** the assumption that these controls improve unrelated low-risk
work. They exist to make an external auditor's job possible. Imported into an
internal onboarding doc, they make it slower to write, longer to read, and no
more true.

### Large or resumable multi-session job

**Add:** compact persisted checkpoints — enough to resume without re-reading
everything. In practice: the source register JSON, the modelled findings per
area, and which content areas are done. Store them under a run directory
(`.doc-run/` or similar) and say where they are.

**Do not add:** separate skills per stage, or an expansive artifact schema,
unless another tool actually has to consume the output. Interoperability is a
requirement someone can point at; anticipated interoperability is not.

## What v11 held that v12 made conditional

An earlier version of this specification mandated three separate skills (plan,
create, update), canonical JSON handoff artifacts between them, exhaustive
claim records, graph manifests, and human approval of non-destructive drafting.
Those controls are not wrong; they are the maximum-assurance configuration.
They are available under the triggers above and are a reference library for
regulated work — not the default contract.

**The acceptance rule that constrains all of this:** a reader must receive the
same depth of system information the maximum-assurance version would have given
them, with less mandatory process. Simplification that removes architecture,
runtime, deployment, security, operational or evidence detail is not a
simplification — it is a different, worse document, and it does not conform.
