---
name: qa-gate-codex-run
description: Run an independent, unfakeable QA gate on an artifact by having Codex verify it across bounded iterations, where Codex holds the only verdict and audits Claude's account of every earlier round from its own session memory. Returns QA_PASSED, QA_FAILED, or QA_ERROR to the calling prompt, logs every message exchanged, versions the artifact on each fix, and on failure has a fresh Codex session diagnose whether the artifact was deficient, the criteria were, or the two parties simply failed to converge. Use this skill WHENEVER a deliverable needs checking by something other than the agent that produced it — and especially when the user says "QA this", "gate this", "verify this independently", "have Codex check it", "get a second opinion before we ship", "I don't want you marking your own homework", "make sure this actually works", "run it past Codex until it passes", or asks for a pass/fail sign-off on a file. Also use proactively when a prompt or plan calls for a QA, verification, sign-off, or acceptance step and the only available checker would otherwise be Claude itself. Accepts a focus message to keep the reviewer on what matters and a severity threshold so it reports only defects that would genuinely stop the artifact working. Not for reviewing GitHub pull requests (use /review) and not for authoring tests.
---

# QA gate: Codex verifies, Claude fixes

## Why this skill exists

Claude cannot QA its own work. Not because it lacks the skill, but because it is the
wrong party — under pressure to be finished, an agent reviewing its own artifact
reliably concludes the artifact is fine. The observed failure isn't a subtly wrong
review; it's "I checked it myself and it looked correct", with no check having
occurred.

So the verdict here comes from Codex, and it is routed through
`scripts/qa_gate.py` — the only sanctioned channel. That script builds every prompt,
invokes Codex itself, and writes each verdict from Codex's own structured output.
Claude supplies the artifact and the fixes. Claude never supplies the verdict, and
never writes into `QA/`.

By default the gate talks to Codex through the openai-codex plugin's app-server
transport, via a thin sidecar (`scripts/codex_bridge.mjs`) that imports the plugin's
`runAppServerTurn` directly — not the plugin's own `/codex` CLI, which cannot resume a
specific thread or enforce a schema-shaped verdict. `--transport exec` shells out to
`codex exec` instead, kept as a rollback lever. Both transports produce the same
tamper-evident log described below; a session's transport is fixed at `start` and
recorded in `session.json`, and `round` refuses to switch it mid-session.

Two mechanisms make a fabricated review detectable rather than merely discouraged:

**One Codex session across all rounds.** Round 1 opens a session; every later round
resumes it, so Codex carries its own memory of every verdict it has issued. Before
assessing anything in round N, it is shown the round history on disk and asked to
compare it against what it actually said. A round that never happened, or a verdict
attributed to it that it never gave, gets named — not because Claude reported it, but
because Codex contradicts the record from the other side.

**Codex's own session file as witness.** Every run leaves a rollout file under
`~/.codex/sessions/` written by the Codex process itself, on both transports, holding
each turn's exact prompt, exact response, and the sandbox and working directory it
actually ran under. `verify` checks the log against it — not just that a verdict was
witnessed, but that the exact request text was (`REQUEST_NOT_WITNESSED` if not), that
the verdict binds to the specific turn id the round recorded rather than merely
appearing somewhere in the file, and that the sandbox and working directory Codex's
own record shows match what the round claims (`SANDBOX_MISMATCH` if not). A QA session
that never happened has no witness, and a hash chain over fabricated content — however
internally consistent — fails there.

Neither is unforgeable by a determined adversary with shell access. Both defeat the
real failure mode: shortcutting under pressure, late in a long loop.

## Running the gate

Bind the script path once; everything below uses it.

```bash
QA=<this-skill-dir>/scripts/qa_gate.py
```

### 1. Establish what "correct" means

This is the input that decides whether the loop converges, and it deserves real
thought before the first call. A reviewer given a vague standard substitutes its own
taste, and taste is inexhaustible — that is the mechanism behind a reviewer that
"finds issues that aren't issues". It is usually not being difficult; it has nothing
firmer to hold.

Write criteria as observable conditions someone could check:

> 1. `revenue_by_customer(path)` returns a dict mapping each customer to the sum of
>    their `amount` values.
> 2. It works when a customer appears once and when they appear on several rows.
> 3. It does not raise on any well-formed input matching that shape.

Not "the parser should be robust and well-written". Pass these as `--criteria-file`
(preferred — it lands in the log verbatim) or `--criteria`.

If the artifact already states its own acceptance criteria, point at that section
rather than paraphrasing it.

If Codex needs source material to check the artifact's claims against — an RFQ, a
spec, an upstream API contract — pass it with `--ground path/to/file.md` (repeatable)
or `--ground-dir path/to/dir` for everything under a directory. Grounding sources are
evidence for checking claims, never a second criteria list; the prompt says so
explicitly so the reviewer doesn't promote a source into a standard the artifact was
never asked to meet. Each source is hashed every round and folded into the chain, so
`verify` reports `GROUNDING_CHANGED` naming the file and the round if one is edited
mid-run — a verdict earned against one version of a source must not be carried by a
different one.

### 2. Open the session and run round 1

Artifacts are submitted as `<name>.v1.<ext>`. The gate refuses an unversioned name
rather than guessing, because each fix is written as the next version with the
predecessor moved to `deprecated/` — it has to know where the lineage starts. If the
consuming system needs a fixed filename (`Dockerfile`, `Makefile`, `package.json`),
gate `Dockerfile.v1` and copy the passing version into place afterwards.

```bash
python3 "$QA" start \
  --artifact path/to/artifact.v1.md \
  --criteria-file path/to/criteria.md \
  --focus "Correctness of the aggregation logic. Ignore typing and docstrings." \
  --threshold blocker \
  --max-iterations 5
```

`--focus` narrows where Codex spends attention. It does not lower the bar for what
counts as a defect there — a blocker found outside the focus area is still a blocker,
which is deliberate; a focus message should not be able to hide a real fault.

`--allow-execution` lets Codex **run** the artifact rather than only read it. Reading
code and running it disagree more often than reviewers expect, and the defects that
survive a careful read are exactly the ones execution catches — in testing, a read-only
pass cleared a function whose behaviour on negative inputs violated a stated criterion,
and the same gate with execution caught it in round 1 with the failing input and output
quoted as evidence. Use it whenever correctness is a runtime property.

It is opt-in because it gives Codex a writable sandbox. That sandbox is a *copy*, at
`QA/exec/`, refreshed from the artifact each round — the real artifact and the QA log
sit outside anything Codex can write to, so a reviewer cannot alter what it is judging
or the record of having judged it. `verify` separately confirms the artifact that
passed is still byte-identical to the one that was reviewed.

`--threshold` is the sharper control, and it is what stops the reviewer escalating
preferences into blockers:

| Level | Meaning |
|---|---|
| `blocker` | The artifact cannot satisfy a stated criterion, with a nameable trigger and consequence. **Default.** |
| `major` | A criterion holds on the happy path but a realistic condition defeats it. |
| `minor` | Quality, style, hardening. The criterion still holds. |

Every finding must name the criterion it defeats. Anything Codex notices that doesn't
defeat one goes to `observations` — recorded permanently, never blocking. That outlet
matters: a reviewer with nowhere to put a genuine misgiving tends to promote it to a
blocker to make it count.

### 3. The loop

`start` and `round` print JSON and exit with a code you should branch on:

| Exit | State | What to do |
|---|---|---|
| `10` | `ROUND_OPEN` | Findings remain. Fix them, write the next version, run `round`. |
| `0` | `QA_PASSED` | Done. Run `verify`, then report to the caller. |
| `1` | `QA_FAILED` | Terminal. Run `postmortem`, then report failure to the caller. |
| `2` | `QA_ERROR` | Codex unusable. Inconclusive — see below. |

On `ROUND_OPEN`, fix the findings and write the **next version** beside the artifact —
`report.v2.md` after `report.v1.md`. Don't edit in place; the log is read against the
lineage later, and an artifact that mutated under a verdict makes the transcript
unreadable. The script moves the superseded version into `deprecated/` for you, and
rejects a version that isn't newer or that renames the artifact mid-session.

```bash
python3 "$QA" round --qa-dir <artifact-dir>/QA --artifact path/to/artifact.v2.md
```

### 4. When a finding is wrong

Codex is the authority, not an oracle. It can misread the artifact or call something a
blocker that the criteria don't support. Contest it instead of complying:

```bash
python3 "$QA" round --qa-dir <artifact-dir>/QA \
  --rebuttal "CSV-002 assumes amounts may be blank. Criterion 3 scopes this to
              well-formed input, where amount is always present. Requesting it be
              reduced to an observation."
```

Codex adjudicates and may agree, reducing it to an observation. What it must not
become is negotiation: argue from the criteria, not from wanting to be finished. If
you find yourself rebutting the same finding twice, that is the signal the finding is
probably real. The stall detector agrees — an unchanged finding set across three
consecutive rounds ends the run as `NON_CONVERGENCE` rather than burning the budget.

### 5. Verify before reporting

```bash
python3 "$QA" verify --qa-dir <artifact-dir>/QA
```

This re-walks the hash chain and checks every recorded verdict against Codex's own
session file. **Its output is the only result the calling prompt should be given.**
A pass claimed without it is exactly the claim this skill exists to make impossible.

### 6. On failure, get the diagnosis

```bash
python3 "$QA" postmortem --qa-dir <artifact-dir>/QA
```

A **fresh** Codex session — not the review session, which was a party to the
disagreement, and not a Claude agent, which authored the artifact — reads the whole
exchange and classifies it:

- `ARTIFACT_DEFICIENT` — the findings were sound and unresolved. Do more work.
- `SPECIFICATION_DEFICIENT` — the criteria were vague, contradictory, or unreachable,
  so nothing could have passed. Fix the criteria and rerun.
- `PROCESS_FAILURE` — resolvable, and the two sides didn't. Talking past each other,
  reopening settled ground, scope drifting, or preferences escalated past threshold.
- `INTEGRITY_BREACH` — the record and Codex's memory disagreed.

Writes `QA/postmortem.md`. Report its classification alongside the failure — "QA
failed" and "QA failed because the criteria were unanswerable" call for very different
responses from the caller.

## When Codex can't be reached

`QA_ERROR` is a third outcome, deliberately not folded into `QA_FAILED`. Codex being
unreachable says nothing about the artifact, and a caller that treats the two alike
will either ship something unchecked or discard something sound.

The script retries, then reports one of `CODEX_NOT_INSTALLED`, `CODEX_TIMEOUT`,
`CODEX_EXIT_<n>`, `CODEX_EMPTY_RESPONSE`, `CODEX_MALFORMED_VERDICT`,
`SESSION_DISCONTINUITY`, `ROLLOUT_NOT_WRITTEN` (round 1 completed but left no witness),
`GROUNDING_MISSING` (a `--ground` source no longer exists), or, specific to the
app-server transport, `NODE_NOT_INSTALLED`, `CODEX_PLUGIN_NOT_FOUND`, and
`CODEX_PLUGIN_INCOMPATIBLE`. Report it verbatim and say plainly that the artifact is
**unverified** — not passed, not failed. Do not substitute your own review; an
unavailable gate is the single most tempting moment to, and the reason the state
exists at all.

## What Claude does not do here

These aren't ceremony — each corresponds to an observed way the gate gets hollowed out.

- Don't write anything into `QA/`. The script owns it. Hand-written files there are
  indistinguishable from forgery, so `verify` treats them as such.
- Don't report a verdict the script didn't print. Not a summary of what you expect
  Codex would say, not a verdict from a Claude subagent, not one from
  `codex:rescue` — that is a Claude subagent and can answer as itself without ever
  reaching Codex.
- Don't call Codex yourself for the verdict, on either transport. Prompt construction,
  including the honesty audit, is fixed in the script precisely so it can't be softened
  round to round.
- Don't treat `QA_ERROR` as a pass, and don't lower `--threshold` or loosen criteria
  mid-run to get one. Changing the standard to clear it is the same act as forging the
  verdict, with better manners.

## Output to the calling prompt

Report the `verify` output, then in prose:

```
QA <PASSED|FAILED|ERROR> — <reason>
Artifact:  <path to the version that was judged>
Rounds:    <n> of <max>   (witnessed by Codex: <n>)
Session:   <codex session id>
Evidence:  <path>/QA/            — every message sent and received
<on failure>  Diagnosis: <classification> — see <path>/QA/postmortem.md
```

## Reference

- `references/protocol.md` — the honesty protocol, log layout, chain construction,
  and how to check a run by hand without trusting either agent.
