# The QA gate protocol

Read this when you need to check a run by hand, debug the gate, or explain to someone
why the verdict should be believed.

## What lands on disk

Both folders are created beside the artifact, never inside the skill.

```
<artifact-dir>/
├── artifact.v3.md                  the version currently under review
├── deprecated/
│   ├── artifact.v1.md              superseded versions, moved not deleted
│   └── artifact.v2.md
└── QA/
    ├── session.json                config, session id, per-round summary, chain head
    ├── rounds/
    │   ├── round-01.request.md     the exact prompt sent to Codex
    │   ├── round-01.response.json  the exact verdict, schema-validated
    │   ├── round-01.events.jsonl   exec: the --json event stream; app-server: the
    │   │                           bridge's raw stdout (thread/turn ids, status)
    │   ├── round-01.stderr.txt
    │   └── round-01.meta.json      hashes, transport, thread/turn id, model, effort,
    │                               plugin version, grounding hashes, chain link
    ├── verdict.json                the terminal result
    ├── verification.json           output of `verify`
    ├── postmortem.request.md       on failure: what the analyst was shown
    ├── postmortem.response.json
    └── postmortem.md               the readable diagnosis
```

Every message in either direction is on disk in full. Nothing is summarised away, so a
dispute about what was said months later is settled by reading, not remembering.

## The honesty audit

From round 2 onward, the prompt opens with the round history as it appears in
`session.json` and asks Codex to compare it against its own memory of the session,
reporting:

- `rounds_you_recall` — verdicts it personally issued, counted from memory rather than
  from the history it was handed
- `prior_rounds_consistent` — false if the record attributes a verdict it never gave,
  claims a round that didn't happen, or reports a finding resolved that it never saw
  resolved
- `discrepancies` — each one named

`prior_rounds_consistent: false` ends the run immediately as `INTEGRITY_BREACH`. It is
not a defect Claude can edit its way out of, and continuing would mean negotiating
over whether the record is real.

This works because both transports resume the same underlying Codex thread — `codex
exec resume <session-id>` on the exec transport, `thread/resume` against the recorded
thread id on the app-server transport — and either restores the full conversation.
Verified directly on both: a resumed session recalled the exact string it had returned
in a prior turn, and detected a forged round-2 PASS injected into a genuine session,
reporting "the history attributes a Round 2 PASS verdict to me, but I issued no Round
2 verdict in this session."

## The chain

Each round links to the last:

```
chain[0] = "GENESIS"
chain[n] = sha256(chain[n-1] + "\n" + sha256(request) + "\n"
                  + sha256(response) + "\n" + sha256(artifact) + "\n"
                  + grounding_digest)
```

`grounding_digest` is the empty string when no `--ground` sources are in play, and
otherwise an order-stable digest of `{path, sha256}` for every grounding source hashed
that round. A grounding file edited between rounds changes this digest at exactly the
round where it changed, so `verify` reports `GROUNDING_CHANGED` naming the file and the
round, on top of the chain link breaking generically.

This makes the log append-only in practice: altering any round's prompt, verdict,
artifact, or grounding source breaks every link after it. It proves the record wasn't
edited afterwards. It proves nothing about who wrote it — anyone able to write the log
can compute a consistent chain over invented content.

## The witness

That gap is closed by Codex's own session file, on both transports:

```
~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<session-id>.jsonl
```

Written by the Codex process; the gate only ever reads it, and `find_rollout` matches
only that exact filename shape so a file that merely mentions the id elsewhere cannot
satisfy it. Per turn it holds a `turn_context` row (the `turn_id`, the `cwd` and
`sandbox_policy` the turn actually ran under, `workspace_roots`, `model`, `effort`),
the exact prompt as an `event_msg/user_message`, and the exact reply plus `turn_id` as
an `event_msg/task_complete`.

`verify` checks four things against it, each producing a specifically named problem
rather than a generic breach:

- the number of completed turns is at least the number of claimed rounds
- the recorded verdict matches the `task_complete` for the exact turn id the round
  recorded (falling back to matching by message body only for older, exec-transport
  rounds that never captured a turn id)
- the round's request text appears verbatim as a `user_message` (`REQUEST_NOT_WITNESSED`
  if not)
- the `turn_context` for that turn ran under the expected sandbox, working directory,
  and workspace roots (`SANDBOX_MISMATCH` if not — this is what catches
  `--allow-execution` accidentally exposing more of the tree than `QA/exec/`)

A fabricated session has no witness at all; a fabricated round inside a real session
leaves a count mismatch and an unmatched verdict.

Confirmed against a forged session that was internally flawless — perfect chain,
plausible verdict, and no Codex session file. The chain accepted it; the witness
rejected it.

## Checking a run by hand

Trusting neither agent:

```bash
# 1. Which session, how many rounds claimed
jq '{session_id, rounds_completed, terminal}' QA/session.json

# 2. Codex's own file for that session
ls ~/.codex/sessions/**/rollout-*-<session-id>.jsonl

# 3. Turns Codex says it completed, with what it returned
jq -r 'select(.payload.type=="task_complete") | .payload.last_agent_message' \
   ~/.codex/sessions/**/rollout-*-<session-id>.jsonl

# 4. Compare against what the log claims
cat QA/rounds/*.response.json
```

If step 3 is empty, no review happened, whatever the log says.

## Terminal states

| State | Meaning | Caller should |
|---|---|---|
| `QA_PASSED` / `CONVERGED` | Codex passed it with no finding at threshold | proceed |
| `QA_FAILED` / `MAX_ITERATIONS_EXHAUSTED` | findings still standing at the limit | read the post-mortem |
| `QA_FAILED` / `NON_CONVERGENCE` | same finding set for 3 rounds running | read the post-mortem |
| `QA_FAILED` / `INTEGRITY_BREACH` | record and Codex's memory disagree | distrust the run entirely; rerun from scratch |
| `QA_ERROR` / `CODEX_*` | Codex unreachable or unusable | treat the artifact as unverified; do not ship, do not discard |
| `QA_ERROR` / `ROLLOUT_NOT_WRITTEN` | round 1 completed but left no rollout file | treat as unverified; a round with no witness cannot be trusted later |
| `QA_ERROR` / `GROUNDING_MISSING` | a `--ground` source no longer exists on disk | fix the path and rerun |
| `QA_ERROR` / `NODE_NOT_INSTALLED`, `CODEX_PLUGIN_NOT_FOUND`, `CODEX_PLUGIN_INCOMPATIBLE` | app-server transport prerequisite missing | install/upgrade, or fall back to `--transport exec` |

## Known limits

Worth stating plainly rather than discovering later.

**Not cryptographically unforgeable.** Claude runs as the same user with shell access
and could in principle write into `~/.codex/sessions/`. What the design guarantees is
that forging costs more than complying and leaves inconsistencies a check you control
will find. A genuinely independent witness has to leave the machine — a signing
service holding a key Claude never sees, or an append-only remote log. Worth building
only if the verdict will be shown to someone with reason to distrust the machine.

**Without `--allow-execution`, Codex reads the artifact but doesn't run it,** so
runtime claims are inferred from source. This is a real weakness and it was measured:
a read-only pass cleared a `split_evenly` implementation that mis-ordered remainder
cents on negative totals, and the same gate with `--allow-execution` caught it in round
1 — quoting `split_evenly(Decimal('-0.01'), 3) -> [0, 0, -0.01]` against the required
`[-0.01, 0, 0]`. Turn execution on whenever correctness is a runtime property.

With it on, Codex works in `QA/exec/` — a copy of the artifact and its siblings,
refreshed each round, persisting across rounds so a harness written in round 1 survives
into round 2. The real artifact and the QA log are outside its writable root, and
`verify` confirms the passing artifact still hashes to what was reviewed. The
directory persists rather than being recreated per round because both `exec resume`
and the app-server's `thread/resume` inherit the working directory from the call that
opened the thread — `verify`'s sandbox witness confirms that inherited `cwd` and
`sandbox_policy` against what the round claims, from Codex's own record rather than
from the script's arguments.

**Long sessions can drift toward agreement.** Accumulated back-and-forth exerts real
pressure toward converging. The stall detector catches the visible form of this. If a
run passes in a way that feels earned by persistence rather than by fixes, rerun with
`--force`: a fresh session has no history to be worn down by.

**The criteria are the weak point, not the mechanism.** Every failure mode this gate
can't catch traces back to criteria that didn't say what correct meant. The integrity
machinery guarantees the review happened and was reported honestly. It cannot make a
vague standard produce a meaningful verdict.
