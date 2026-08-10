#!/usr/bin/env python3
"""
qa_gate.py — the only sanctioned channel between Claude and the Codex QA authority.

Why this exists as a script rather than as instructions: a QA gate that Claude can
satisfy by describing a review it did not run is not a gate. Every Codex call, every
verdict, and every round boundary is written here, by this process, from the raw
output of `codex exec`. Claude supplies the artifact and the fixes; it never supplies
the verdict.

Subcommands
  start   Open a QA session on an artifact and run round 1.
  round   Run the next round against the SAME Codex session (resume).
  verify  Re-walk the recorded chain against Codex's own session file and emit the
          terminal verdict. This is the value the calling prompt is allowed to trust.
  postmortem  On a failed run, ask a fresh Codex session whether the artifact was
          deficient, the criteria were, or the two parties simply failed to converge.
  status  Human-readable summary of where a QA session stands.

Exit codes
  0   QA_PASSED
  1   QA_FAILED      (artifact defective, non-convergence, or integrity breach)
  2   QA_ERROR       (Codex unreachable or unusable — inconclusive, NOT a failure)
  3   usage / local state error
  10  ROUND_OPEN     (a round finished, findings remain, the loop continues)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SEVERITY_ORDER = {"minor": 1, "major": 2, "blocker": 3}
DEFAULT_THRESHOLD = "blocker"
DEFAULT_MAX_ITERATIONS = 5
DEFAULT_TIMEOUT_SECONDS = 900
DEFAULT_RETRIES = 2
STALL_LIMIT = 2  # identical finding sets this many rounds running = non-convergence

GENESIS = "GENESIS"
SCHEMA_PATH = Path(__file__).with_name("verdict.schema.json")
BRIDGE_PATH = Path(__file__).with_name("codex_bridge.mjs")
DEFAULT_TRANSPORT = "app-server"

PASSED, FAILED, ERROR, USAGE, ROUND_OPEN = 0, 1, 2, 3, 10


# --------------------------------------------------------------------------- utils

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def die(msg: str, code: int = USAGE):
    print(json.dumps({"state": "QA_ERROR" if code == ERROR else "USAGE_ERROR",
                      "reason": msg}, indent=2))
    sys.exit(code)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# ------------------------------------------------------------------- artifact versions

VERSION_RE = re.compile(r"^(?P<base>.+)\.v(?P<n>\d+)(?P<ext>\.[^.]+)?$")


def parse_version(path: Path):
    """Return (base, version_number, extension) for a `name.vN.ext` artifact."""
    m = VERSION_RE.match(path.name)
    if not m:
        die(f"artifact must be named <name>.v<N>.<ext>, got '{path.name}'. The gate "
            f"writes each fix as the next version and moves the predecessor to "
            f"deprecated/, so it needs to know which version it is starting from. "
            f"Rename it (e.g. '{path.stem}.v1{path.suffix}') and rerun.")
    return m.group("base"), int(m.group("n")), m.group("ext") or ""


def next_version_path(path: Path) -> Path:
    base, n, ext = parse_version(path)
    return path.parent / f"{base}.v{n + 1}{ext}"


def sync_exec_dir(qa_dir: Path, artifact: Path, state) -> Path:
    """
    Give Codex a writable copy of the artifact to actually run.

    Reviewing source without executing it is the weakest part of a read-only gate —
    a reviewer that can run the thing finds defects that inference misses. But a
    reviewer with write access to the real tree could alter the artifact under
    review or the log recording it, so it gets a copy in its own directory instead.
    The real artifact and QA/ stay outside anything it can write to.

    The directory persists across rounds because `exec resume` inherits its working
    directory, and that is useful anyway — a test harness Codex writes in round 1 is
    still there in round 2. Only the files copied from the artifact tree are refreshed,
    so a superseded version can never be reviewed by mistake.
    """
    exec_dir = qa_dir / "exec"
    exec_dir.mkdir(parents=True, exist_ok=True)
    for name in state.get("exec_copied", []):
        stale = exec_dir / name
        if stale.is_file():
            stale.unlink()
        elif stale.is_dir():
            shutil.rmtree(stale, ignore_errors=True)
    copied = []
    for src in sorted(artifact.parent.iterdir()):
        if src.name in ("QA", "deprecated"):
            continue
        dest = exec_dir / src.name
        if src.is_dir():
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(src, dest)
        elif src.is_file():
            shutil.copy2(src, dest)
        else:
            continue
        copied.append(src.name)
    state["exec_copied"] = copied
    return exec_dir


# ------------------------------------------------------------------------- QA layout

class Session:
    """The on-disk QA session living beside the artifact."""

    def __init__(self, qa_dir: Path):
        self.qa_dir = qa_dir
        self.rounds_dir = qa_dir / "rounds"
        self.state_path = qa_dir / "session.json"

    @property
    def state(self):
        if not self.state_path.exists():
            die(f"no QA session at {self.qa_dir} — run `start` first")
        return read_json(self.state_path)

    def save(self, state) -> None:
        write_json(self.state_path, state)

    def round_paths(self, n: int):
        p = self.rounds_dir
        tag = f"round-{n:02d}"
        return {
            "request": p / f"{tag}.request.md",
            "response": p / f"{tag}.response.json",
            "events": p / f"{tag}.events.jsonl",
            "stderr": p / f"{tag}.stderr.txt",
            "meta": p / f"{tag}.meta.json",
        }


# ---------------------------------------------------------------------- codex plumbing

def find_rollout(session_id: str):
    """
    Codex writes its own session file. We never write here; it is the witness. The
    filename is `rollout-<timestamp>-<id>.jsonl`; matching only that shape means a file
    that merely mentions the id elsewhere in its name cannot satisfy this.
    """
    root = Path.home() / ".codex" / "sessions"
    if not root.is_dir():
        return None
    hits = list(root.rglob(f"rollout-*-{session_id}.jsonl"))
    return hits[0] if hits else None


def parse_events(events_path: Path):
    """Pull thread id and token usage out of the --json event stream."""
    thread_id, usage = None, {}
    if not events_path.exists():
        return thread_id, usage
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "thread.started" and ev.get("thread_id"):
            thread_id = ev["thread_id"]
        if ev.get("type") == "turn.completed" and isinstance(ev.get("usage"), dict):
            usage = ev["usage"]
    return thread_id, usage


def run_codex_exec(prompt: str, paths, session_id, cwd: Path, timeout: int, retries: int,
                    model=None, writable: bool = False):
    """
    Invoke Codex via `codex exec`. Round 1 opens a session; later rounds resume it so
    Codex carries its own memory of every verdict it has issued — that memory is what
    makes a fabricated round detectable.

    Returns (verdict_dict, meta_dict) or raises CodexUnavailable.
    """
    paths["request"].write_text(prompt, encoding="utf-8")

    base = ["codex", "exec"]
    if session_id:
        base += ["resume"]
    base += ["--json", "--skip-git-repo-check",
             "--output-schema", str(SCHEMA_PATH),
             "-o", str(paths["response"])]
    if model:
        base += ["-m", model]
    if session_id:
        # `exec resume` rejects -s and -C: the resumed session inherits the sandbox
        # and working directory it was opened with. That is why the sandbox choice is
        # fixed at `start` and the execution directory stays put across rounds.
        base += [session_id]
    else:
        base += ["-s", "workspace-write" if writable else "read-only", "-C", str(cwd)]
    base += [prompt]

    last_error = None
    for attempt in range(1, retries + 2):
        if paths["response"].exists():
            paths["response"].unlink()
        started = _dt.datetime.now(_dt.timezone.utc)
        try:
            with paths["events"].open("w", encoding="utf-8") as out, \
                 paths["stderr"].open("w", encoding="utf-8") as err:
                proc = subprocess.run(
                    base,
                    stdin=subprocess.DEVNULL,  # closed: Codex must never block on input
                    stdout=out,
                    stderr=err,
                    timeout=timeout,
                    check=False,
                )
            exit_code = proc.returncode
        except FileNotFoundError:
            raise CodexUnavailable("CODEX_NOT_INSTALLED",
                                   "`codex` is not on PATH; QA cannot be performed")
        except subprocess.TimeoutExpired:
            last_error = ("CODEX_TIMEOUT", f"no response within {timeout}s "
                                           f"(attempt {attempt})")
            continue

        duration = (_dt.datetime.now(_dt.timezone.utc) - started).total_seconds()
        thread_id, usage = parse_events(paths["events"])

        if exit_code != 0:
            tail = paths["stderr"].read_text(encoding="utf-8", errors="replace")[-600:]
            last_error = (f"CODEX_EXIT_{exit_code}", tail.strip() or "no stderr")
            continue

        if not paths["response"].exists() or not paths["response"].read_text().strip():
            last_error = ("CODEX_EMPTY_RESPONSE", "process exited 0 but wrote no verdict")
            continue

        raw = paths["response"].read_text(encoding="utf-8")
        try:
            verdict = json.loads(raw)
        except json.JSONDecodeError as exc:
            last_error = ("CODEX_MALFORMED_VERDICT", f"{exc}; first 400 chars: {raw[:400]}")
            continue

        meta = {
            "attempt": attempt,
            "exit_code": exit_code,
            "duration_seconds": round(duration, 2),
            "transport": "exec",
            "session_id": thread_id or session_id,
            "thread_id": thread_id or session_id,
            "turn_id": None,
            "usage": usage,
            "model": model,
            "effort": None,
            "plugin_version": None,
            "plugin_lib_path": None,
            "argv": base[:-1] + ["<prompt>"],
            "started_at": started.isoformat(),
            "response_sha256": sha256_text(raw),
            "request_sha256": sha256_text(prompt),
        }
        return verdict, meta

    raise CodexUnavailable(*last_error)


def run_codex_app_server(prompt: str, paths, thread_id, cwd: Path, timeout: int, retries: int,
                         model=None, effort=None, writable: bool = False,
                         thread_name: str = None):
    """
    Invoke Codex via the openai-codex plugin's app-server transport, through the
    codex_bridge.mjs sidecar. Round 1 opens a persistent thread; later rounds resume it
    by thread id, so Codex carries its own memory of every verdict it has issued and a
    rollout file keyed by that thread id is Codex's own record of the exchange.

    Returns (verdict_dict, meta_dict) or raises CodexUnavailable.
    """
    paths["request"].write_text(prompt, encoding="utf-8")

    request = {
        "cwd": str(cwd),
        "promptFile": str(paths["request"]),
        "outputSchemaFile": str(SCHEMA_PATH),
        "resumeThreadId": thread_id,
        "sandbox": "workspace-write" if writable else "read-only",
        "model": model,
        "effort": effort,
        "persistThread": True,
        "threadName": thread_name,
        "timeoutMs": timeout * 1000,
    }

    last_error = None
    for attempt in range(1, retries + 2):
        started = _dt.datetime.now(_dt.timezone.utc)
        try:
            proc = subprocess.run(
                ["node", str(BRIDGE_PATH)],
                input=json.dumps(request),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout + 30,  # hard backstop behind the bridge's own timeoutMs
                check=False,
            )
        except FileNotFoundError:
            raise CodexUnavailable("NODE_NOT_INSTALLED",
                                   "`node` is not on PATH; the app-server transport "
                                   "cannot run")
        except subprocess.TimeoutExpired:
            last_error = ("CODEX_TIMEOUT", f"bridge process exceeded the {timeout + 30}s "
                                           f"backstop (attempt {attempt})")
            continue

        duration = (_dt.datetime.now(_dt.timezone.utc) - started).total_seconds()
        paths["events"].write_text(proc.stdout, encoding="utf-8")
        paths["stderr"].write_text(proc.stderr, encoding="utf-8")

        try:
            bridge_result = json.loads(proc.stdout) if proc.stdout.strip() else None
        except json.JSONDecodeError as exc:
            last_error = ("CODEX_BRIDGE_ERROR",
                          f"bridge did not return JSON: {exc}; "
                          f"stderr: {proc.stderr.strip()[-400:]}")
            continue

        if bridge_result is None:
            last_error = ("CODEX_BRIDGE_ERROR",
                          f"bridge produced no output; stderr: {proc.stderr.strip()[-400:]}")
            continue

        if not bridge_result.get("ok"):
            err = bridge_result.get("error") or {}
            last_error = (err.get("reason", "CODEX_BRIDGE_ERROR"), err.get("detail", "no detail"))
            continue

        raw = bridge_result.get("finalMessage") or ""
        try:
            verdict = json.loads(raw)
        except json.JSONDecodeError as exc:
            last_error = ("CODEX_MALFORMED_VERDICT", f"{exc}; first 400 chars: {raw[:400]}")
            continue

        paths["response"].write_text(raw, encoding="utf-8")

        plugin = bridge_result.get("plugin") or {}
        resolved_thread_id = bridge_result.get("threadId") or thread_id
        meta = {
            "attempt": attempt,
            "exit_code": bridge_result.get("status", 0),
            "duration_seconds": round(duration, 2),
            "transport": "app-server",
            "session_id": resolved_thread_id,
            "thread_id": resolved_thread_id,
            "turn_id": bridge_result.get("turnId"),
            "usage": {},
            "model": model,
            "effort": effort,
            "plugin_version": plugin.get("version"),
            "plugin_lib_path": plugin.get("libPath"),
            "argv": ["node", str(BRIDGE_PATH), "<request on stdin>"],
            "started_at": started.isoformat(),
            "response_sha256": sha256_text(raw),
            "request_sha256": sha256_text(prompt),
        }
        return verdict, meta

    raise CodexUnavailable(*last_error)


def invoke_codex(cfg, prompt: str, paths, resume_id, cwd: Path, thread_name: str = None):
    """
    Dispatch to the configured transport. A session's transport is fixed at `start`
    and recorded in its config; a session created before this switch existed has no
    `transport` key and continues on the exec path it was opened with.
    """
    transport = cfg.get("transport") or "exec"
    timeout = cfg["timeout_seconds"]
    retries = cfg["retries"]
    writable = bool(cfg.get("allow_execution"))
    if transport == "exec":
        return run_codex_exec(prompt, paths, resume_id, cwd, timeout, retries,
                              model=cfg.get("model"), writable=writable)
    if transport == "app-server":
        return run_codex_app_server(prompt, paths, resume_id, cwd, timeout, retries,
                                    model=cfg.get("model"), effort=cfg.get("effort"),
                                    writable=writable, thread_name=thread_name)
    raise CodexUnavailable("BAD_TRANSPORT", f"unknown transport '{transport}'")


class CodexUnavailable(Exception):
    def __init__(self, reason: str, detail: str):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


# ------------------------------------------------------------------- prompt assembly

SEVERITY_GUIDE = """\
blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.
"""

ROLE = """\
You are the independent QA authority for the artifact below. A Claude agent authored
it and will act on whatever you find, but the verdict is yours alone. Claude cannot
overrule you, and a Claude claim that something passed carries no weight here.

Two failure modes are equally bad, so hold both in mind:

Passing something broken. Someone downstream depends on this working.

Failing something sound. Reviewers under pressure to be useful invent defects — they
flag what they would have done differently and dress it as a defect. That wastes
rounds and buries the real finding. The severity threshold below is not a suggestion
about tone; it is the definition of what counts as a finding at all.

Anything you notice that does not defeat a stated criterion goes in `observations`.
Observations are recorded permanently and never block. Use them freely — that is
where your judgement about taste, hardening, and alternatives belongs. What must not
happen is a preference being promoted to a finding to justify a FAIL.

A finding must name the criterion it defeats. If you cannot point at one, you have an
observation.
"""

HONESTY_BLOCK = """\
## Before you assess anything: audit the record

You have been in this session since round 1. You remember what you actually said.

Below is the round history as it appears on disk. Claude assembled the artifact and
the fixes; the file record could be wrong, whether by error or by convenience. Compare
it against your own memory and report in `honesty_audit`:

- `rounds_you_recall` — how many verdicts you personally issued, counted from your own
  memory of this conversation, not from the history below.
- `prior_rounds_consistent` — false if the history below attributes to you any verdict
  you did not give, claims a round that did not happen, or reports a finding of yours
  as resolved when you never saw it resolved.
- `discrepancies` — name each one specifically.

If your memory and the record disagree, say so plainly. That disagreement matters more
than this round's verdict, and it is the one thing nobody else can check for us.

### Round history on disk
{history}
"""

REBUTTAL_BLOCK = """\
## Rebuttal raised this round

Claude did not change the artifact in response to the following finding(s); it argues
they should not block. Adjudicate in `rebuttal_response`. You are free to agree — a
finding you now judge below threshold should simply be reissued as an observation.
You are equally free to hold your ground. Being argued with is not evidence of being
wrong, and neither is being argued with repeatedly.

{rebuttal}
"""


GROUNDING_NOTE = """\
These sources are evidence, not requirements. Use them to check whether the artifact's
claims are true. A finding must still name the criterion it defeats. A disagreement
between the artifact and a source that no criterion covers is an observation.
"""


def build_prompt(cfg, artifact_path: Path, artifact_sha: str, round_no: int,
                 history, rebuttal, chain_prev: str, grounding=None) -> str:
    parts = [ROLE, ""]

    if round_no > 1:
        parts += [HONESTY_BLOCK.format(history=history or "(none recorded)"), ""]

    parts += [
        "## The artifact under review",
        f"Path: {artifact_path}",
        f"Version: round {round_no} of at most {cfg['max_iterations']}",
        f"SHA-256: {artifact_sha}",
        "",
        "Read the file at that path. If it references other files needed to judge it,",
        "read those too.",
        "",
    ]

    if cfg.get("allow_execution"):
        parts += [
            "## You can run this, and you should",
            "",
            "Your working directory is writable and holds a copy of the artifact and",
            "the files beside it. Run the thing. Write a harness, execute it, probe the",
            "edges, try the inputs you suspect. Nothing here is the real artifact, so",
            "you cannot break anything that matters.",
            "",
            "This is worth the effort because reading code and running it disagree more",
            "often than reviewers expect — the defects that survive a careful read are",
            "exactly the ones execution catches. A finding you have reproduced is worth",
            "more than one you have inferred, so put what you observed in `evidence`:",
            "the input, the output you got, the output the criteria required.",
            "",
            "It cuts the other way too. If you suspected something, tested it, and it",
            "held up, do not raise it — say so in `reasoning` instead. A suspicion that",
            "survived a test is not a finding.",
            "",
        ]

    parts += [
        "## What correct means",
        "This is the whole standard. Nothing outside it is grounds for a finding.",
        "",
        cfg["criteria"].strip(),
        "",
    ]

    if grounding:
        parts += [
            "## Grounding sources",
            "Absolute paths; read whichever of these bear on the criteria above.",
            "",
        ]
        parts += [f"- {g['path']}" for g in grounding]
        parts += ["", GROUNDING_NOTE, ""]

    if cfg.get("focus"):
        parts += [
            "## Where to spend your attention",
            cfg["focus"].strip(),
            "",
            "This narrows where you look. It does not lower the bar for what you find",
            "there, and a blocker spotted outside this area is still a blocker.",
            "",
        ]

    parts += [
        f"## Severity threshold: {cfg['threshold']}",
        "",
        SEVERITY_GUIDE,
        f"Only findings of severity `{cfg['threshold']}` or above may cause a FAIL.",
        "Return PASS when nothing at or above that bar survives your own scrutiny,",
        "even if the artifact is not what you would have written.",
        "",
    ]

    if rebuttal:
        parts += [REBUTTAL_BLOCK.format(rebuttal=rebuttal.strip()), ""]

    parts += [
        "## Continuity token",
        f"Echo nothing; this is for the record only: {chain_prev}",
        "",
        "Respond only in the required JSON shape.",
    ]
    return "\n".join(parts)


def render_history(rounds) -> str:
    if not rounds:
        return "(none recorded)"
    lines = []
    for r in rounds:
        blockers = [f["title"] for f in r.get("findings_at_threshold", [])]
        lines.append(
            f"- Round {r['round']} ({r['timestamp']}): you returned "
            f"{r['verdict']} with {len(blockers)} finding(s) at threshold"
            + (": " + "; ".join(blockers) if blockers else "")
        )
    return "\n".join(lines)


# ------------------------------------------------------------------------ chain + eval

def chain_next(prev: str, request_sha: str, response_sha: str, artifact_sha: str,
              grounding_sha: str = "") -> str:
    return sha256_text(f"{prev}\n{request_sha}\n{response_sha}\n{artifact_sha}\n{grounding_sha}")


def grounding_digest(grounding) -> str:
    """Order-stable digest of a round's grounding sources, empty for no grounding."""
    if not grounding:
        return ""
    return sha256_text("\n".join(f"{g['path']}:{g['sha256']}" for g in grounding))


def at_threshold(findings, threshold: str):
    bar = SEVERITY_ORDER[threshold]
    return [f for f in findings
            if SEVERITY_ORDER.get(str(f.get("severity", "")).lower(), 0) >= bar]


def fingerprint(findings) -> str:
    keys = sorted(
        f"{f.get('id', '')}|{re.sub(r'[^a-z0-9]+', '', str(f.get('title', '')).lower())}"
        for f in findings
    )
    return sha256_text("\n".join(keys))


# ------------------------------------------------------------------------- the rounds

def execute_round(sess: Session, state, artifact: Path, rebuttal) -> int:
    round_no = state["rounds_completed"] + 1
    cfg = state["config"]

    if round_no > cfg["max_iterations"]:
        return finalize(sess, state, FAILED, "MAX_ITERATIONS_EXHAUSTED",
                        f"reached the {cfg['max_iterations']}-round limit without a PASS")

    if not artifact.exists():
        die(f"artifact not found: {artifact}")

    artifact_sha = sha256_file(artifact)
    paths = sess.round_paths(round_no)
    paths["request"].parent.mkdir(parents=True, exist_ok=True)

    if cfg.get("allow_execution"):
        cwd = sync_exec_dir(sess.qa_dir, artifact, state)
        review_path = cwd / artifact.name
        sess.save(state)
    else:
        cwd = artifact.parent
        review_path = artifact

    grounding_paths = cfg.get("grounding") or []
    missing_grounding = [p for p in grounding_paths if not Path(p).exists()]
    if missing_grounding:
        return finalize(sess, state, ERROR, "GROUNDING_MISSING",
                        f"grounding source(s) no longer exist: {', '.join(missing_grounding)}")
    grounding = [{"path": p, "sha256": sha256_file(Path(p))} for p in grounding_paths]

    prompt = build_prompt(
        cfg, review_path, artifact_sha, round_no,
        render_history(state["rounds"]), rebuttal, state["chain"], grounding,
    )

    try:
        verdict, meta = invoke_codex(
            cfg, prompt, paths,
            resume_id=state.get("thread_id") or state.get("session_id"),
            cwd=cwd,
            thread_name=f"QA gate: {artifact.name}",
        )
    except CodexUnavailable as exc:
        return finalize(sess, state, ERROR, exc.reason, exc.detail)

    if not state.get("session_id"):
        state["session_id"] = meta["session_id"]
        state["thread_id"] = meta.get("thread_id") or meta["session_id"]
    elif meta["session_id"] and meta["session_id"] != state["session_id"]:
        return finalize(sess, state, ERROR, "SESSION_DISCONTINUITY",
                        f"expected session {state['session_id']}, "
                        f"Codex reported {meta['session_id']}")

    audit = verdict.get("honesty_audit") or {}
    findings = verdict.get("findings") or []
    blocking = at_threshold(findings, cfg["threshold"])

    rollout = find_rollout(state["session_id"])
    if round_no == 1 and rollout is None:
        return finalize(sess, state, ERROR, "ROLLOUT_NOT_WRITTEN",
                        f"round 1 completed but no Codex session file appeared for "
                        f"{state['session_id']}; a round that leaves no rollout cannot "
                        f"be witnessed later")

    meta.update({
        "round": round_no,
        "cwd": str(cwd),
        "artifact_path": str(artifact),
        "artifact_sha256": artifact_sha,
        "grounding": grounding,
        "chain_prev": state["chain"],
        "chain": chain_next(state["chain"], meta["request_sha256"],
                            meta["response_sha256"], artifact_sha,
                            grounding_digest(grounding)),
        "rollout_file": str(rollout or ""),
        "timestamp": now_iso(),
    })
    write_json(paths["meta"], meta)

    state["chain"] = meta["chain"]
    state["rounds_completed"] = round_no
    state["rounds"].append({
        "round": round_no,
        "timestamp": meta["timestamp"],
        "verdict": verdict.get("verdict"),
        "artifact_path": str(artifact),
        "artifact_sha256": artifact_sha,
        "findings_at_threshold": [
            {"id": f.get("id"), "title": f.get("title"), "severity": f.get("severity"),
             "criterion_ref": f.get("criterion_ref")} for f in blocking
        ],
        "observations_count": len(verdict.get("observations") or []),
        "chain": meta["chain"],
    })
    sess.save(state)

    # Dishonesty is terminal. It is not a defect Claude can edit its way out of, and
    # continuing the loop would mean negotiating over whether the record is real.
    if audit.get("prior_rounds_consistent") is False:
        return finalize(sess, state, FAILED, "INTEGRITY_BREACH",
                        "Codex does not recognise the recorded history: "
                        + "; ".join(audit.get("discrepancies") or ["unspecified"]))

    if verdict.get("verdict") == "PASS" and not blocking:
        return finalize(sess, state, PASSED, "CONVERGED",
                        f"Codex passed the artifact at round {round_no}")

    fp = fingerprint(blocking)
    if fp == state.get("last_fingerprint") and blocking:
        state["stall_count"] = state.get("stall_count", 0) + 1
    else:
        state["stall_count"] = 0
    state["last_fingerprint"] = fp
    sess.save(state)

    if state["stall_count"] >= STALL_LIMIT:
        return finalize(sess, state, FAILED, "NON_CONVERGENCE",
                        f"the same finding set has stood for {state['stall_count'] + 1} "
                        "consecutive rounds; further rounds would not change it")

    if round_no >= cfg["max_iterations"]:
        return finalize(sess, state, FAILED, "MAX_ITERATIONS_EXHAUSTED",
                        f"{len(blocking)} finding(s) still at threshold after "
                        f"{round_no} rounds")

    report_open(sess, round_no, verdict, blocking, cfg)
    return ROUND_OPEN


def report_open(sess: Session, round_no: int, verdict, blocking, cfg) -> None:
    print(json.dumps({
        "state": "ROUND_COMPLETE",
        "round": round_no,
        "codex_verdict": verdict.get("verdict"),
        "rounds_remaining": cfg["max_iterations"] - round_no,
        "findings_at_threshold": blocking,
        "observations": verdict.get("observations") or [],
        "rebuttal_response": verdict.get("rebuttal_response") or "",
        "reasoning": verdict.get("reasoning") or "",
        "next": ("Fix the findings, write the next artifact version, and run "
                 "`round`. To contest a finding instead of fixing it, pass "
                 "--rebuttal."),
        "response_file": str(sess.round_paths(round_no)["response"]),
    }, indent=2, ensure_ascii=False))


def finalize(sess: Session, state, code: int, reason: str, detail: str) -> int:
    label = {PASSED: "QA_PASSED", FAILED: "QA_FAILED", ERROR: "QA_ERROR"}[code]
    verdict = {
        "state": label,
        "reason": reason,
        "detail": detail,
        "artifact": state.get("artifact_current"),
        "rounds_completed": state["rounds_completed"],
        "max_iterations": state["config"]["max_iterations"],
        "session_id": state.get("session_id"),
        "thread_id": state.get("thread_id") or state.get("session_id"),
        "transport": state["config"].get("transport") or "exec",
        "rollout_file": str(find_rollout(state["session_id"]) or "")
        if state.get("session_id") else "",
        "chain": state["chain"],
        "qa_dir": str(sess.qa_dir),
        "finalized_at": now_iso(),
    }
    state["terminal"] = verdict
    sess.save(state)
    write_json(sess.qa_dir / "verdict.json", verdict)
    print(json.dumps(verdict, indent=2, ensure_ascii=False))
    return code


# ------------------------------------------------------------------------- subcommands

def cmd_start(args) -> int:
    artifact = Path(args.artifact).resolve()
    if not artifact.exists():
        die(f"artifact not found: {artifact}")
    parse_version(artifact)  # rejects an unversioned name before any Codex call

    criteria = (Path(args.criteria_file).read_text(encoding="utf-8")
                if args.criteria_file else args.criteria)
    if not criteria or not criteria.strip():
        die("pass criteria are required: without a definition of correct, a reviewer "
            "substitutes its own taste and the loop never converges "
            "(--criteria or --criteria-file)")

    grounding_paths, seen = [], set()
    for p in (args.ground or []):
        gp = Path(p).resolve()
        if not gp.is_file():
            die(f"grounding source not found: {gp}")
        if str(gp) not in seen:
            seen.add(str(gp))
            grounding_paths.append(str(gp))
    for d in (args.ground_dir or []):
        gd = Path(d).resolve()
        if not gd.is_dir():
            die(f"grounding directory not found: {gd}")
        for f in sorted(gd.rglob("*")):
            if f.is_file() and str(f) not in seen:
                seen.add(str(f))
                grounding_paths.append(str(f))

    qa_dir = artifact.parent / "QA"
    sess = Session(qa_dir)
    if sess.state_path.exists() and not args.force:
        existing = read_json(sess.state_path)
        if not existing.get("terminal"):
            die(f"a QA session is already open at {qa_dir}; use `round` to continue "
                f"or --force to start over")
        archive = qa_dir.parent / "deprecated" / f"QA-{existing.get('opened_at', 'prior')}"
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(qa_dir), str(archive))

    (artifact.parent / "deprecated").mkdir(exist_ok=True)
    sess.rounds_dir.mkdir(parents=True, exist_ok=True)

    state = {
        "opened_at": now_iso().replace(":", "-"),
        "artifact_original": str(artifact),
        "artifact_current": str(artifact),
        "session_id": None,
        "chain": GENESIS,
        "rounds_completed": 0,
        "rounds": [],
        "stall_count": 0,
        "last_fingerprint": None,
        "exec_copied": [],
        "terminal": None,
        "config": {
            "criteria": criteria,
            "focus": args.focus or "",
            "threshold": args.threshold,
            "max_iterations": args.max_iterations,
            "timeout_seconds": args.timeout,
            "retries": args.retries,
            "model": args.model,
            "effort": args.effort,
            "transport": args.transport,
            "allow_execution": bool(args.allow_execution),
            "grounding": grounding_paths,
        },
    }
    sess.save(state)
    return execute_round(sess, state, artifact, rebuttal=None)


def cmd_round(args) -> int:
    qa_dir = Path(args.qa_dir).resolve()
    sess = Session(qa_dir)
    state = sess.state

    if state.get("terminal"):
        die(f"this QA session already ended: {state['terminal']['state']} "
            f"({state['terminal']['reason']})")

    session_transport = state["config"].get("transport") or "exec"
    if args.transport and args.transport != session_transport:
        die(f"this session was opened on transport '{session_transport}'; an "
            f"exec-transport session and an app-server-transport session have no "
            f"common thread id to resume across, so '--transport {args.transport}' "
            f"is refused rather than silently ignored. Continue with `round` "
            f"unmodified, or start a new session on the transport you want.")

    prev = Path(state["artifact_current"])
    artifact = Path(args.artifact).resolve() if args.artifact else prev

    if artifact != prev:
        # A new version supersedes the old one; the old one moves aside rather than
        # disappearing, so the QA log stays readable against the lineage later.
        if not artifact.exists():
            die(f"artifact not found: {artifact}")
        prev_base, prev_n, _ = parse_version(prev)
        new_base, new_n, _ = parse_version(artifact)
        if new_base != prev_base:
            die(f"this session is reviewing '{prev_base}', but '{artifact.name}' is a "
                f"different artifact. Swapping the artifact mid-session would leave "
                f"the round history describing work that was never reviewed.")
        if new_n <= prev_n:
            die(f"'{artifact.name}' is not newer than '{prev.name}'. Each fix goes in "
                f"the next version so the log reads against a stable lineage.")
        if prev.exists():
            dep = prev.parent / "deprecated"
            dep.mkdir(exist_ok=True)
            shutil.move(str(prev), str(dep / prev.name))
        state["artifact_current"] = str(artifact)
        sess.save(state)
    elif not args.rebuttal:
        die("the artifact is unchanged since the last round. Either supply the new "
            "version with --artifact, or state why the findings should not block "
            "with --rebuttal. Re-submitting identical content without an argument "
            "just burns a round.")

    return execute_round(sess, state, Path(state["artifact_current"]), args.rebuttal)


def cmd_verify(args) -> int:
    """
    Recompute the chain and check it against Codex's own session file.

    The chain proves the log was not edited after the fact. The rollout file proves the
    rounds happened at all — Codex's process wrote it, this script never touches it. A
    fabricated round has to exist in both, consistently, or this reports a breach.
    """
    sess = Session(Path(args.qa_dir).resolve())
    state = sess.state
    problems, chain = [], GENESIS
    prev_grounding = {}

    for entry in state["rounds"]:
        n = entry["round"]
        meta_path = sess.round_paths(n)["meta"]
        if not meta_path.exists():
            problems.append(f"round {n}: meta file missing")
            continue
        meta = read_json(meta_path)
        for key, path in (("request_sha256", sess.round_paths(n)["request"]),
                          ("response_sha256", sess.round_paths(n)["response"])):
            if not path.exists():
                problems.append(f"round {n}: {path.name} missing")
            elif sha256_text(path.read_text(encoding="utf-8")) != meta.get(key):
                problems.append(f"round {n}: {path.name} does not match its recorded hash")
        round_grounding = meta.get("grounding") or []
        expected = chain_next(chain, meta.get("request_sha256", ""),
                              meta.get("response_sha256", ""),
                              meta.get("artifact_sha256", ""),
                              grounding_digest(round_grounding))
        if expected != meta.get("chain"):
            problems.append(f"round {n}: chain hash breaks here")
        chain = meta.get("chain", expected)

        # A grounding source recorded with a different hash than the previous round
        # named it was edited mid-run — the same failure the artifact hash guards
        # against, on the evidence side instead of the deliverable side.
        for g in round_grounding:
            prior_sha = prev_grounding.get(g["path"])
            if prior_sha is not None and prior_sha != g["sha256"]:
                problems.append(f"round {n}: GROUNDING_CHANGED — {g['path']} does not "
                                f"match the hash recorded in the previous round")
            prev_grounding[g["path"]] = g["sha256"]

    # The artifact that passed must be the artifact you still have. Without this, a
    # verdict earned by one version could quietly be carried by another. The expected
    # hash is read from the round's own meta.json — which the chain walk above already
    # ties to the request/response hashes — rather than from session.json's cached
    # copy of the same value, which sits outside the chain and is not protected by it.
    if state["rounds"]:
        last = state["rounds"][-1]
        last_meta_path = sess.round_paths(last["round"])["meta"]
        last_meta = read_json(last_meta_path) if last_meta_path.exists() else {}
        expected_artifact_sha = last_meta.get("artifact_sha256")
        final = Path(state.get("artifact_current") or "")
        if not final.exists():
            problems.append(f"the reviewed artifact {final} no longer exists")
        elif not expected_artifact_sha:
            problems.append(f"round {last['round']}: meta file missing "
                            f"artifact_sha256; cannot confirm the current artifact "
                            f"matches what was reviewed")
        elif sha256_file(final) != expected_artifact_sha:
            problems.append(f"{final.name} has been modified since round "
                            f"{last['round']} judged it")

    # The PASS/FAIL label under `terminal` is session.json bookkeeping written by this
    # script, not part of the hash chain above — nothing before this point stops an
    # edit to just that field. Recompute the outcome from the last round's own
    # chain-verified response instead of trusting the cached label, so a `terminal`
    # edited to claim QA_PASSED cannot survive a real Codex verdict that said otherwise.
    terminal = state.get("terminal")
    if state["rounds"] and terminal and terminal.get("state") == "QA_PASSED":
        last = state["rounds"][-1]
        resp_path = sess.round_paths(last["round"])["response"]
        if not resp_path.exists():
            problems.append(f"round {last['round']}: response file missing; the "
                            f"claimed QA_PASSED cannot be confirmed against Codex's "
                            f"own verdict")
        else:
            try:
                last_resp = json.loads(resp_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                problems.append(f"round {last['round']}: response file is not valid "
                                f"JSON; the claimed QA_PASSED cannot be confirmed")
            else:
                real_blocking = at_threshold(last_resp.get("findings") or [],
                                             state["config"]["threshold"])
                if last_resp.get("verdict") != "PASS" or real_blocking:
                    problems.append(
                        f"round {last['round']}: TERMINAL_STATE_MISMATCH — "
                        f"session.json claims QA_PASSED, but round {last['round']}'s "
                        f"own chain-verified response recorded "
                        f"verdict={last_resp.get('verdict')!r} with "
                        f"{len(real_blocking)} finding(s) at or above the "
                        f"'{state['config']['threshold']}' threshold")

    session_id = state.get("session_id")
    rollout = find_rollout(session_id) if session_id else None
    witnessed = 0
    if not session_id:
        problems.append("no Codex session id recorded — no round can be witnessed")
    elif rollout is None:
        problems.append(f"no Codex session file found for {session_id}; the rounds "
                        f"cannot be independently witnessed")
    else:
        task_complete_all = []
        task_complete_by_turn = {}
        turn_context_by_turn = {}
        user_messages = []
        for line in rollout.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            row_type = row.get("type")
            payload = row.get("payload") or {}
            if row_type == "turn_context":
                turn_id = payload.get("turn_id")
                if turn_id:
                    turn_context_by_turn[turn_id] = payload
            elif row_type == "event_msg" and payload.get("type") == "user_message":
                user_messages.append(payload.get("message") or "")
            elif row_type == "event_msg" and payload.get("type") == "task_complete":
                msg = payload.get("last_agent_message") or ""
                task_complete_all.append(msg)
                turn_id = payload.get("turn_id")
                if turn_id:
                    task_complete_by_turn[turn_id] = msg

        witnessed = len(task_complete_all)
        if witnessed < len(state["rounds"]):
            problems.append(
                f"the log claims {len(state['rounds'])} round(s) but Codex's own "
                f"session file records {witnessed} completed turn(s)")

        allow_execution = bool(state["config"].get("allow_execution"))
        expected_sandbox = "workspace-write" if allow_execution else "read-only"

        for entry in state["rounds"]:
            n = entry["round"]
            meta_path = sess.round_paths(n)["meta"]
            meta = read_json(meta_path) if meta_path.exists() else {}
            turn_id = meta.get("turn_id")

            # Verdict witness. When app-server recorded a turn id, the match is bound
            # to that exact turn; otherwise fall back to matching by message body, the
            # only signal older (exec-transport) sessions carry.
            resp = sess.round_paths(n)["response"]
            resp_body = resp.read_text(encoding="utf-8").strip() if resp.exists() else None
            if resp_body is not None:
                if turn_id:
                    recorded_msg = task_complete_by_turn.get(turn_id)
                    if recorded_msg is None:
                        problems.append(f"round {n}: no completed turn {turn_id} found "
                                        f"in Codex's own session file")
                    elif recorded_msg.strip() != resp_body:
                        problems.append(f"round {n}: the recorded verdict does not match "
                                        f"turn {turn_id} in Codex's own session file")
                elif not any(resp_body == r.strip() for r in task_complete_all):
                    problems.append(f"round {n}: the recorded verdict does not appear in "
                                    f"Codex's own session file")

            # Request witness. A forger who only avoids contradicting the response side
            # still has to explain a request that never happened.
            req = sess.round_paths(n)["request"]
            if req.exists():
                req_body = req.read_text(encoding="utf-8").strip()
                if not any(req_body == m.strip() for m in user_messages):
                    problems.append(f"round {n}: REQUEST_NOT_WITNESSED — the recorded "
                                    f"request does not appear as a user turn in Codex's "
                                    f"own session file")

            # Sandbox and cwd witness, from Codex's own record of what it ran under
            # rather than from our arguments.
            tc = turn_context_by_turn.get(turn_id) if turn_id else None
            if tc:
                actual_sandbox = (tc.get("sandbox_policy") or {}).get("type")
                if actual_sandbox != expected_sandbox:
                    problems.append(f"round {n}: SANDBOX_MISMATCH — turn ran under "
                                    f"sandbox '{actual_sandbox}', expected "
                                    f"'{expected_sandbox}'")
                expected_cwd = meta.get("cwd")
                actual_cwd = tc.get("cwd")
                if expected_cwd and actual_cwd and actual_cwd != expected_cwd:
                    problems.append(f"round {n}: SANDBOX_MISMATCH — turn ran in "
                                    f"'{actual_cwd}', expected '{expected_cwd}'")
                actual_roots = tc.get("workspace_roots") or []
                if expected_cwd and actual_roots not in ([expected_cwd], []):
                    problems.append(f"round {n}: SANDBOX_MISMATCH — workspace roots "
                                    f"{actual_roots} reach beyond the execution "
                                    f"directory {expected_cwd}")

    result = {
        "state": terminal["state"] if terminal and not problems else (
            "QA_FAILED" if problems else "QA_IN_PROGRESS"),
        "reason": "INTEGRITY_BREACH" if problems else (
            terminal["reason"] if terminal else "rounds still open"),
        "chain_valid": not problems,
        "rounds_claimed": len(state["rounds"]),
        "rounds_witnessed_by_codex": witnessed,
        "session_id": session_id,
        "rollout_file": str(rollout or ""),
        "problems": problems,
        "artifact": state.get("artifact_current"),
        "qa_dir": str(sess.qa_dir),
    }
    write_json(sess.qa_dir / "verification.json", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if problems:
        return FAILED
    if not terminal:
        return USAGE
    return {"QA_PASSED": PASSED, "QA_FAILED": FAILED, "QA_ERROR": ERROR}[terminal["state"]]


POSTMORTEM_ROLE = """\
A QA gate has just failed and you are the analyst. You were not part of it — that is
the point of asking you.

Below is the complete exchange: the criteria the artifact was held to, and every round
of review with its findings, rebuttals and verdicts. Read it as an investigator, not as
a participant, and answer one question: why did this not converge?

Four honest possibilities, and you should be genuinely willing to reach any of them:

The artifact really is deficient. The findings were sound, they were never fixed, and
the right response is more work on the artifact.

The specification was deficient. The pass criteria were vague, self-contradictory, or
demanded something unreachable. No artifact could have passed, and the reviewer was
left substituting its own standard because it had nothing firmer to hold. This is
easy to miss because the transcript reads like a normal disagreement.

The process failed. Both parties were capable of resolving this and did not — talking
past each other, reopening settled ground, scope drifting between rounds, or the
reviewer escalating preferences past the stated severity threshold and calling them
blockers.

The record was breached. What the reviewer remembers and what was written down do not
agree.

Tie every claim to a specific round and quote the text you are relying on. A
conclusion that cannot be traced back to the transcript is not usable — the people
reading this will act on it.
"""


def cmd_postmortem(args) -> int:
    """
    Analyse a failed run with a FRESH Codex session.

    Deliberately not the QA session and deliberately not a Claude agent: the QA session
    is a party to the disagreement, and Claude authored the artifact. Neither is
    positioned to judge whether the failure was the work or the process.
    """
    sess = Session(Path(args.qa_dir).resolve())
    state = sess.state
    terminal = state.get("terminal")
    if not terminal:
        die("this QA session has not finished; there is nothing to post-mortem yet")

    parts = [POSTMORTEM_ROLE, "",
             "## Outcome",
             f"{terminal['state']} — {terminal['reason']}: {terminal['detail']}",
             f"Rounds used: {state['rounds_completed']} of "
             f"{state['config']['max_iterations']}",
             f"Severity threshold in force: {state['config']['threshold']}", ""]
    if state["config"].get("focus"):
        parts += ["## Focus given to the reviewer", state["config"]["focus"], ""]
    parts += ["## Pass criteria the artifact was held to",
              state["config"]["criteria"], "", "## The exchange", ""]

    for entry in state["rounds"]:
        n = entry["round"]
        parts.append(f"### Round {n} — reviewer returned {entry['verdict']}")
        req = sess.round_paths(n)["request"]
        resp = sess.round_paths(n)["response"]
        if req.exists():
            text = req.read_text(encoding="utf-8")
            marker = "## Rebuttal raised this round"
            if marker in text:
                parts += ["Claude contested rather than fixed:",
                          text.split(marker, 1)[1].split("## Continuity")[0].strip(), ""]
        if resp.exists():
            parts += ["Reviewer response:", "```json",
                      resp.read_text(encoding="utf-8").strip(), "```", ""]

    prompt = "\n".join(parts)
    out_dir = sess.qa_dir
    paths = {
        "request": out_dir / "postmortem.request.md",
        "response": out_dir / "postmortem.response.json",
        "events": out_dir / "postmortem.events.jsonl",
        "stderr": out_dir / "postmortem.stderr.txt",
    }

    global SCHEMA_PATH
    original, SCHEMA_PATH = SCHEMA_PATH, Path(__file__).with_name("postmortem.schema.json")
    try:
        report, meta = invoke_codex(state["config"], prompt, paths, resume_id=None,
                                    cwd=sess.qa_dir,
                                    thread_name=f"QA postmortem: {sess.qa_dir.parent.name}")
    except CodexUnavailable as exc:
        print(json.dumps({"state": "QA_ERROR", "reason": exc.reason,
                          "detail": f"post-mortem could not run: {exc.detail}"}, indent=2))
        return ERROR
    finally:
        SCHEMA_PATH = original

    report["_meta"] = {
        "analysed_session": state.get("session_id"),
        "postmortem_session": meta["session_id"],
        "rollout_file": str(find_rollout(meta["session_id"]) or ""),
        "generated_at": now_iso(),
    }
    write_json(out_dir / "postmortem.json", report)

    md = [f"# QA post-mortem — {terminal['state']}", "",
          f"**Classification:** {report['classification']}  ",
          f"**Confidence:** {report['confidence']}  ",
          f"**Rounds:** {state['rounds_completed']} of "
          f"{state['config']['max_iterations']}  ",
          f"**Terminal reason:** {terminal['reason']} — {terminal['detail']}", "",
          "## Reasoning", "", report["reasoning"], "", "## Evidence", ""]
    md += [f"- {e}" for e in report.get("evidence", [])]
    md += ["", "## Recommendation", "", report["recommendation"], "",
           "---", "",
           f"Analysed by an independent Codex session "
           f"(`{meta['session_id']}`), separate from the review session "
           f"(`{state.get('session_id')}`)."]
    (out_dir / "postmortem.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "state": "POSTMORTEM_COMPLETE",
        "classification": report["classification"],
        "confidence": report["confidence"],
        "recommendation": report["recommendation"],
        "report": str(out_dir / "postmortem.md"),
    }, indent=2, ensure_ascii=False))
    return PASSED


def cmd_status(args) -> int:
    sess = Session(Path(args.qa_dir).resolve())
    state = sess.state
    print(json.dumps({
        "artifact": state.get("artifact_current"),
        "session_id": state.get("session_id"),
        "thread_id": state.get("thread_id") or state.get("session_id"),
        "transport": state["config"].get("transport") or "exec",
        "rounds_completed": state["rounds_completed"],
        "max_iterations": state["config"]["max_iterations"],
        "threshold": state["config"]["threshold"],
        "stall_count": state.get("stall_count", 0),
        "terminal": state.get("terminal"),
        "rounds": state["rounds"],
    }, indent=2, ensure_ascii=False))
    return PASSED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="open a QA session and run round 1")
    s.add_argument("--artifact", required=True)
    s.add_argument("--criteria", help="what a correct artifact looks like, as text")
    s.add_argument("--criteria-file", help="same, read from a file")
    s.add_argument("--focus", help="where Codex should concentrate its attention")
    s.add_argument("--ground", action="append",
                   help="a grounding source file, absolute or relative; repeatable. "
                        "Evidence for checking the artifact's claims, never a second "
                        "criteria list")
    s.add_argument("--ground-dir", action="append",
                   help="a directory whose files are all added as grounding sources; "
                        "repeatable")
    s.add_argument("--threshold", default=DEFAULT_THRESHOLD,
                   choices=list(SEVERITY_ORDER))
    s.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS)
    s.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    s.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    s.add_argument("--model", default=None)
    s.add_argument("--effort", default=None, choices=["none", "minimal", "low", "medium",
                                                       "high", "xhigh"],
                   help="reasoning effort for the app-server transport; ignored on exec")
    s.add_argument("--transport", default=DEFAULT_TRANSPORT,
                   choices=["app-server", "exec"],
                   help="app-server (default) routes through the openai-codex plugin's "
                        "app-server; exec shells out to `codex exec` and is kept as the "
                        "rollback lever")
    s.add_argument("--allow-execution", action="store_true",
                   help="let Codex run the artifact in a writable copy under QA/exec/ "
                        "instead of reviewing the source read-only. Finds defects that "
                        "inference misses; the real artifact stays outside its reach.")
    s.add_argument("--force", action="store_true",
                   help="archive an existing completed QA session and start fresh")
    s.set_defaults(fn=cmd_start)

    r = sub.add_parser("round", help="run the next round in the same Codex session")
    r.add_argument("--qa-dir", required=True)
    r.add_argument("--artifact", help="the new artifact version; omit only with --rebuttal")
    r.add_argument("--rebuttal", help="why a finding should not block, if not fixing it")
    r.add_argument("--transport", default=None, choices=["app-server", "exec"],
                   help="must match the transport the session was opened with; passing "
                        "a different one is refused rather than silently ignored")
    r.set_defaults(fn=cmd_round)

    v = sub.add_parser("verify", help="re-walk the chain against Codex's own session file")
    v.add_argument("--qa-dir", required=True)
    v.set_defaults(fn=cmd_verify)

    p = sub.add_parser("postmortem",
                       help="ask a fresh Codex session why a failed run did not converge")
    p.add_argument("--qa-dir", required=True)
    p.set_defaults(fn=cmd_postmortem)

    t = sub.add_parser("status", help="summarise an open QA session")
    t.add_argument("--qa-dir", required=True)
    t.set_defaults(fn=cmd_status)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
