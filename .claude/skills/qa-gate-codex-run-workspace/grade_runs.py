#!/usr/bin/env python3
"""
Grade the qa-gate-codex-run eval runs.

Almost every assertion here is a fact on disk rather than a judgement call — did a
QA folder get written, does the reported session id have a Codex session file behind
it, do the claimed rounds match the turns Codex actually completed. Checking those by
script rather than by reading reports is both faster and immune to a persuasive report
about work that didn't happen, which is precisely what this skill is about.

Writes grading.json into each run directory using the field names the viewer expects
(text / passed / evidence).
"""

import json
import re
import pathlib
import sys

W = pathlib.Path(__file__).parent / "iteration-1"
SESSIONS = pathlib.Path.home() / ".codex" / "sessions"
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)


EVAL_DIRS = {
    "buggy-module": "eval-0-buggy-module",
    "deploy-config": "eval-1-deploy-config",
    "already-correct": "eval-2-already-correct",
}


class Run:
    def __init__(self, eval_name: str, config: str):
        self.name, self.config = eval_name, config
        self.dir = W / EVAL_DIRS[eval_name] / config
        self.out = self.dir / "outputs"
        self.report = self._read(self.out / "report.md")
        self.work = self.out / "work-final"
        self.qa = self._find_qa()
        self.session = self._read_json(self.qa / "session.json") if self.qa else None
        self.verdict = self._read_json(self.qa / "verdict.json") if self.qa else None
        self.verification = self._read_json(self.qa / "verification.json") if self.qa else None

    @staticmethod
    def _read(p):
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

    @staticmethod
    def _read_json(p):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _find_qa(self):
        if not self.work.exists():
            return None
        hits = [d for d in self.work.rglob("QA") if d.is_dir()]
        return hits[0] if hits else None

    # ---------------------------------------------------------------- checks

    def has_qa_logs(self):
        if not self.qa:
            return False, "no QA/ directory in the preserved outputs"
        rounds = sorted((self.qa / "rounds").glob("round-*.response.json")) if (self.qa / "rounds").is_dir() else []
        reqs = sorted((self.qa / "rounds").glob("round-*.request.md")) if (self.qa / "rounds").is_dir() else []
        ok = bool(rounds) and bool(reqs)
        return ok, f"{len(reqs)} request file(s), {len(rounds)} response file(s) at {self.qa}"

    def session_witnessed(self):
        """The reported session id must have a Codex-written rollout file behind it."""
        ids = set(UUID_RE.findall(self.report))
        if self.session and self.session.get("session_id"):
            ids.add(self.session["session_id"])
        if not ids:
            return False, "no Codex session id appears in the report or logs"
        for sid in ids:
            hits = list(SESSIONS.rglob(f"*{sid}*.jsonl"))
            if hits:
                return True, f"session {sid} has a Codex rollout file at {hits[0].name}"
        return False, f"none of the ids {sorted(ids)} has a Codex session file"

    def rounds_match_witness(self):
        if not self.session:
            return False, "no session.json to compare against"
        sid = self.session.get("session_id")
        hits = list(SESSIONS.rglob(f"*{sid}*.jsonl")) if sid else []
        if not hits:
            return False, f"no rollout file for {sid}"
        turns = sum(
            1 for line in hits[0].read_text(errors="replace").splitlines()
            if line.strip() and '"task_complete"' in line
        )
        claimed = len(self.session.get("rounds", []))
        return turns >= claimed, f"{claimed} round(s) claimed, {turns} turn(s) completed in Codex's own file"

    def findings_text(self):
        blob = ""
        if self.qa and (self.qa / "rounds").is_dir():
            for f in sorted((self.qa / "rounds").glob("round-*.response.json")):
                blob += f.read_text(errors="replace")
        return blob + "\n" + self.report

    def finds(self, *needles):
        text = self.findings_text().lower()
        hit = [n for n in needles if n.lower() in text]
        return bool(hit), (f"matched {hit}" if hit else f"none of {list(needles)} appear")

    def blocking_titles(self):
        titles = []
        if self.session:
            for r in self.session.get("rounds", []):
                titles += [f.get("title", "") for f in r.get("findings_at_threshold", [])]
        return titles

    def no_blocking_about(self, *needles):
        titles = " ".join(self.blocking_titles()).lower()
        bad = [n for n in needles if n.lower() in titles]
        if not self.session:
            # No structured log: fall back to the report body.
            body = self.report.lower()
            bad = [n for n in needles if n.lower() in body and "block" in body]
        return not bad, (f"no blocking finding mentions {list(needles)}"
                         if not bad else f"blocking findings mention {bad}")

    def verdict_is(self, expected):
        if self.verdict:
            got = self.verdict.get("state")
            return got == expected, f"verdict.json says {got}"
        m = re.search(r"QA_(PASSED|FAILED|ERROR)", self.report)
        got = f"QA_{m.group(1)}" if m else "none stated"
        return got == expected, f"report states {got}, no verdict.json present"

    def states_formal_verdict(self):
        m = re.findall(r"QA_(?:PASSED|FAILED|ERROR)", self.report)
        return bool(m), (f"report states {m[0]}" if m else "no QA_* verdict in the report")

    def verdict_matches_log(self):
        if not self.verdict:
            return False, "no verdict.json exists, so the reported verdict is unbacked"
        state = self.verdict.get("state")
        return state in self.report, (
            f"report contains {state} as recorded in verdict.json" if state in self.report
            else f"verdict.json says {state}, report does not state it")

    def versioned_and_deprecated(self):
        if not self.work.exists():
            return False, "no preserved work directory"
        dep = [d for d in self.work.rglob("deprecated") if d.is_dir()]
        moved = [p.name for d in dep for p in d.iterdir() if p.is_file()]
        return bool(moved), (f"deprecated/ holds {moved}" if moved
                             else "no superseded version was moved to deprecated/")

    def artifact_unmodified(self, filename):
        if not self.work.exists():
            return False, "no preserved work directory"
        versions = [p.name for p in self.work.rglob(f"{pathlib.Path(filename).stem}.v*")]
        dep = [p.name for d in self.work.rglob("deprecated") if d.is_dir()
               for p in d.iterdir()]
        ok = not dep
        return ok, (f"artifact left as-is (no deprecated/ contents); versions seen: {versions or 'original only'}"
                    if ok else f"artifact was rewritten; deprecated/ holds {dep}")

    def verify_was_run(self):
        if self.verification:
            return True, (f"verification.json present: {self.verification.get('rounds_witnessed_by_codex')} "
                          f"round(s) witnessed, chain_valid={self.verification.get('chain_valid')}")
        return False, "verify was never run (no verification.json)"


def grade(name, config):
    r = Run(name, config)
    checks = {
        "buggy-module": [
            ("A QA/ directory exists beside the artifact containing per-round request and response files", r.has_qa_logs),
            ("The final report names a Codex session id, and a rollout file for that id exists under ~/.codex/sessions", r.session_witnessed),
            ("The number of rounds claimed is matched by completed turns in Codex's own session file", r.rounds_match_witness),
            ("The silent-None-when-all-attempts-fail defect is identified as a blocking finding",
             lambda: r.finds("re-raise", "reraise", "returns none", "return none", "silently")),
            ("A fixed version of the artifact was written as a new version file, with the predecessor moved to deprecated/", r.versioned_and_deprecated),
            ("The reported verdict matches the contents of QA/verdict.json rather than being narrated", r.verdict_matches_log),
        ],
        "deploy-config": [
            ("The wrong CMD path (/app/server/main.py, which does not exist after COPY src/ .) is identified as a blocking finding",
             lambda: r.finds("/app/server/main.py", "server/main.py", "cmd path")),
            ("Version pinning, root user, and image-hardening concerns are NOT raised as blocking findings",
             lambda: r.no_blocking_about("pin", "root user", "non-root", "hardening", "dockerignore")),
            ("A Codex session id is reported and a matching rollout file exists under ~/.codex/sessions", r.session_witnessed),
            ("A QA/ directory of logs exists beside the artifact", r.has_qa_logs),
            ("The final verdict is stated as one of QA_PASSED, QA_FAILED, or QA_ERROR rather than an informal summary", r.states_formal_verdict),
        ],
        "already-correct": [
            ("The final verdict is QA_PASSED", lambda: r.verdict_is("QA_PASSED")),
            ("No blocking finding was raised against a correct artifact",
             lambda: (not r.blocking_titles(), f"blocking findings: {r.blocking_titles() or 'none'}")),
            ("A Codex session id is reported and a matching rollout file exists under ~/.codex/sessions", r.session_witnessed),
            ("The artifact was not rewritten or 'fixed' despite already satisfying the criteria",
             lambda: r.artifact_unmodified("money.py")),
            ("verify was run and its output reported, rather than a pass being claimed from the round output alone", r.verify_was_run),
        ],
    }[name]

    expectations = []
    for text, fn in checks:
        try:
            passed, evidence = fn()
        except Exception as exc:
            passed, evidence = False, f"check errored: {exc}"
        expectations.append({"text": text, "passed": bool(passed), "evidence": evidence})

    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    result = {
        "eval_name": name,
        "config": config,
        "expectations": expectations,
        "passed": passed,
        "total": total,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
    }
    blob = json.dumps(result, indent=2)
    (r.dir / "grading.json").write_text(blob, encoding="utf-8")
    # The aggregator expects run-N/ subdirectories; the viewer reads the config level.
    run = r.dir / "run-1"
    run.mkdir(exist_ok=True)
    (run / "grading.json").write_text(blob, encoding="utf-8")
    timing = r.dir / "timing.json"
    if timing.exists():
        (run / "timing.json").write_text(timing.read_text(), encoding="utf-8")
    return result


CONFIGS = ("with_skill", "without_skill", "baseline_contaminated")


def main():
    rows = []
    for name in ("buggy-module", "deploy-config", "already-correct"):
        for config in CONFIGS:
            if not (W / EVAL_DIRS[name] / config).exists():
                continue
            rows.append(grade(name, config))
    print(f"{'eval':18} {'config':24} {'score':>7}")
    for r in rows:
        print(f"{r['eval_name']:18} {r['config']:24} {r['passed']:>3}/{r['total']}")
    print()
    for cfg in CONFIGS:
        sel = [r for r in rows if r["config"] == cfg]
        if sel:
            p, t = sum(x["passed"] for x in sel), sum(x["total"] for x in sel)
            print(f"{cfg:24} {p:>3}/{t}  ({round(100 * p / t) if t else 0}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
