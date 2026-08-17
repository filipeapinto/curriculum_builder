#!/usr/bin/env python3
"""Deterministic quality gates for a system-documentation deliverable.

Runs the checks that code settles better than reading does: secret exposure,
link and asset resolution, output containment, coverage of the required content
areas, presence of evidence labels and a verification summary. Judgement checks
— accuracy against evidence, operational usefulness, whether a diagram is
misleading — are deliberately *not* here; they need a reader, not a regex.

Handles HTML and Markdown deliverables, detected from the extension. HTML gets
the extra gates that decide whether a page still works in the situation it was
written for: nothing loaded over the network, readable with JavaScript off, a
language and a viewport declared, and every visual sitting in a figure with a
caption and a text equivalent.

Usage:
    python3 verify_doc.py --doc GUIDE.html [--allow-dir DIR] [--root DIR]
        [--areas-na "graph behavior:no graph in this system"]
        [--json REPORT.json] [--attempt-state STATE.json]

Exit 0 when every gate passes (warnings allowed), 1 when a gate fails, 2 on
usage error. With --attempt-state, tracks repeat failures across runs so the
two-attempt repair bound is enforced by the file rather than by memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

# Required content areas from the specification. Each is (canonical name,
# regexes that a heading may use to claim it). Coverage here is a smoke test for
# *structure*; it cannot tell you the section is any good.
AREAS: list[tuple[str, list[str]]] = [
    ("purpose and boundary", [r"purpose", r"scope", r"boundar", r"what this system (is|does)"]),
    ("architecture", [r"architect", r"components?\b", r"system design"]),
    ("graph behavior", [r"graph", r"execution (flow|path)", r"orchestrat", r"control flow"]),
    ("node and tool contracts", [r"node", r"tool", r"agent contract", r"stage contract"]),
    ("state and data", [r"state\b", r"data model", r"schema", r"persistence"]),
    ("route contracts", [r"rout", r"edge", r"transition", r"branch"]),
    ("models and prompts", [r"model", r"prompt", r"llm", r"inference"]),
    ("deployment", [r"deploy", r"environment", r"topolog", r"hosting", r"infrastructure"]),
    ("configuration and release", [r"config", r"release", r"parameter", r"feature flag", r"rollback"]),
    ("security and privacy", [r"securit", r"privacy", r"auth", r"access control", r"secret"]),
    ("observability", [r"observab", r"monitor", r"logging", r"metric", r"telemetry", r"alert"]),
    ("operations and recovery", [r"operat", r"runbook", r"recover", r"incident", r"troubleshoot"]),
    ("limitations and verification", [r"limitation", r"verification", r"gap", r"unknown",
                                      r"assumption", r"what would invalidate"]),
]

SECRET_PATTERNS: list[tuple[str, str]] = [
    ("private key block", r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    ("aws access key id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("github token", r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    ("slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ("openai/anthropic style key", r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}\b"),
    ("google api key", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("jwt", r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
    ("bearer credential", r"(?i)\b(?:authorization|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{20,}"),
    ("assigned secret literal", r"(?i)\b(?:api[_-]?key|secret|password|passwd|token|client[_-]?secret)"
                               r"\s*[:=]\s*['\"][^'\"\s${}<>]{8,}['\"]"),
    ("connection string with password", r"(?i)\b[a-z][a-z0-9+.\-]*://[^\s/@:]+:[^\s/@]{4,}@"),
]

# Placeholders that look like secrets on purpose and are the correct way to
# document one. Flagging these would teach the writer to stop documenting
# configuration at all, which is the opposite of what the gate is for.
PLACEHOLDER = re.compile(
    r"(?i)(\$\{[^}]*\}|<[^>\s]{2,}>|\bREDACTED\b|\bEXAMPLE\b|\bPLACEHOLDER\b|\bCHANGEME\b|"
    r"\bYOUR[_-]|\bxxx+\b|\*{4,}|\.{3,}|\bdummy\b|\bsample\b|\bfake\b|\bnot[_-]?a[_-]?real\b)")

EVIDENCE_LABELS = re.compile(r"(?i)\b(declared|observed|inferred|unknown|conflicting)\b")
CODE_FENCE = re.compile(r"^\s*(```|~~~)")

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
HTML_DROP = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
HTML_HEADING = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.S | re.I)
HTML_TAG = re.compile(r"<[^>]+>")
REMOTE = re.compile(r"^(?:https?:)?//", re.I)


def _tagless(fragment: str) -> str:
    return re.sub(r"\s+", " ", HTML_TAG.sub(" ", fragment)).strip()


def _line_of(text: str, idx: int) -> int:
    return text[:idx].count("\n") + 1


def _load(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _strip_code(text: str) -> str:
    """Blank out fenced code so link/heading scans ignore samples, keeping line count."""
    out, inside = [], False
    for line in text.splitlines():
        if CODE_FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return "\n".join(out)


def _slug(text: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", text.strip().lower())
    return re.sub(r"[\s_]+", "-", s)


def check_secrets(text: str, path: str) -> list[dict]:
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, pat in SECRET_PATTERNS:
            for m in re.finditer(pat, line):
                frag = m.group(0)
                if PLACEHOLDER.search(frag):
                    continue
                findings.append({
                    "gate": "security-and-disclosure", "severity": "fail",
                    "id": f"secret:{name}:{lineno}",
                    "message": f"{path}:{lineno} possible {name} exposed",
                    "hint": "replace with a placeholder, a reference to where the value "
                            "lives, or remove it; describe the control, not the credential",
                })
    return findings


def check_links(text: str, doc_path: str, root: str) -> list[dict]:
    body = _strip_code(text)
    headings = {_slug(h) for h in re.findall(r"^#{1,6}\s+(.+?)\s*$", body, re.M)}
    headings |= set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', text))
    findings, external = [], 0
    doc_dir = os.path.dirname(os.path.abspath(doc_path))
    seen: set[str] = set()
    for m in re.finditer(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", body):
        target = m.group(1)
        lineno = body[:m.start()].count("\n") + 1
        if target.startswith(("http://", "https://", "mailto:")):
            external += 1
            continue
        key = f"{target}@{lineno}"
        if key in seen:
            continue
        seen.add(key)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
        if target:
            resolved = os.path.normpath(os.path.join(doc_dir, target))
            if not os.path.exists(resolved):
                findings.append({
                    "gate": "links-and-outputs", "severity": "fail",
                    "id": f"link:{target}",
                    "message": f"{doc_path}:{lineno} link target does not exist: {target}",
                    "hint": "an asset the guide promises but does not ship is a broken "
                            "promise to the reader; render it or drop the reference"})
        elif anchor and _slug(anchor) not in headings and anchor not in headings:
            findings.append({
                "gate": "links-and-outputs", "severity": "fail",
                "id": f"anchor:{anchor}",
                "message": f"{doc_path}:{lineno} internal anchor resolves to no heading: #{anchor}"})
    for m in re.finditer(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?", body):
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(doc_dir, src))):
            findings.append({
                "gate": "links-and-outputs", "severity": "fail", "id": f"image:{src}",
                "message": f"{doc_path} embeds a missing image: {src}"})
    if external:
        findings.append({"gate": "links-and-outputs", "severity": "info",
                         "id": "link:external-count",
                         "message": f"{external} external link(s) not fetched (no network access assumed)"})
    return findings


def check_alt_text(text: str, doc_path: str) -> list[dict]:
    out = []
    for m in re.finditer(r"!\[\s*\]\(([^)\s]+)", text):
        out.append({"gate": "rendered-quality", "severity": "fail",
                    "id": f"alt:{m.group(1)}",
                    "message": f"{doc_path} image {m.group(1)} has no alt text",
                    "hint": "every visual needs a text equivalent; a reader who cannot see "
                            "it must still get the takeaway"})
    return out


def check_coverage(headings: str, na: dict[str, str]) -> list[dict]:
    headings = headings.lower()
    findings = []
    for name, pats in AREAS:
        if name in na:
            findings.append({"gate": "scope-and-completeness", "severity": "info",
                             "id": f"area-na:{name}",
                             "message": f"'{name}' declared not applicable: {na[name]}"})
            continue
        if not any(re.search(p, headings) for p in pats):
            findings.append({
                "gate": "scope-and-completeness", "severity": "fail",
                "id": f"area:{name}",
                "message": f"no heading covers required content area '{name}'",
                "hint": "cover it, or pass --areas-na \"" + name + ":<reason>\" and state "
                        "that reason in the guide; missing evidence is a documented gap, "
                        "never a silent omission"})
    return findings


def check_evidence_and_summary(text: str, doc_path: str, headings: str) -> list[dict]:
    findings = []
    labels = len(EVIDENCE_LABELS.findall(text))
    if labels == 0:
        findings.append({
            "gate": "accuracy-and-evidence", "severity": "fail", "id": "evidence:none",
            "message": f"{doc_path} carries no evidence labels at all",
            "hint": "label where it matters — declared vs observed vs inferred vs unknown. "
                    "Undifferentiated prose reads as if everything was verified equally"})
    elif labels < 5:
        findings.append({"gate": "accuracy-and-evidence", "severity": "warn",
                         "id": "evidence:sparse",
                         "message": f"only {labels} evidence label(s) found; check that "
                                    f"claims about execution are distinguished from claims "
                                    f"about design"})
    if not re.search(r"(?i)(verification|limitations|source register|"
                     r"what was inspected|evidence summary)", headings):
        findings.append({
            "gate": "scope-and-completeness", "severity": "fail", "id": "summary:missing",
            "message": f"{doc_path} has no verification / limitations section",
            "hint": "the run must record what was inspected, freshness, checks performed, "
                    "and unresolved gaps — inside the guide or beside it"})
    return findings


def check_links_html(text: str, doc_path: str) -> list[dict]:
    """Resolve every local reference, and refuse anything fetched over a network.

    A guide is read during the incident it documents, on a laptop that may have
    no route to the internet and a proxy that eats CDNs. A stylesheet, font or
    image loaded remotely is a section of the document that silently disappears
    exactly when it is needed, so remote *resources* fail here while ordinary
    <a> links out to the world are fine.
    """
    body = HTML_COMMENT.sub("", text)
    ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', body))
    doc_dir = os.path.dirname(os.path.abspath(doc_path))
    findings, external = [], 0

    for m in re.finditer(r'<(\w+)\b[^>]*?\b(href|src)=["\']([^"\']*)["\']', body, re.I):
        tag, attr, target = m.group(1).lower(), m.group(2).lower(), m.group(3).strip()
        line = _line_of(body, m.start())
        is_resource = attr == "src" or (tag == "link" and attr == "href")
        if not target or target.startswith(("data:", "mailto:", "javascript:")):
            continue
        if REMOTE.match(target) or target.startswith(("http://", "https://")):
            if is_resource:
                findings.append({
                    "gate": "self-containment", "severity": "fail",
                    "id": f"remote:{target}",
                    "message": f"{doc_path}:{line} loads a remote resource: {target}",
                    "hint": "inline it. A guide that needs the network to render is "
                            "unreadable in the outage it was written for"})
            else:
                external += 1
            continue
        if target.startswith("#"):
            if target[1:] not in ids:
                findings.append({
                    "gate": "links-and-outputs", "severity": "fail",
                    "id": f"anchor:{target[1:]}",
                    "message": f"{doc_path}:{line} internal link goes nowhere: {target}",
                    "hint": "a dead nav link in a sidebar is how a reader concludes the "
                            "whole document is stale"})
            continue
        path, _, anchor = target.partition("#")
        if path and not os.path.exists(os.path.normpath(os.path.join(doc_dir, path))):
            findings.append({
                "gate": "links-and-outputs", "severity": "fail", "id": f"link:{path}",
                "message": f"{doc_path}:{line} link target does not exist: {path}"})
    if external:
        findings.append({"gate": "links-and-outputs", "severity": "info",
                         "id": "link:external-count",
                         "message": f"{external} external link(s) not fetched "
                                    f"(no network access assumed)"})
    return findings


def check_visuals_html(text: str, doc_path: str) -> list[dict]:
    """Every visual must survive not being seen.

    The reader who cannot see the diagram — screen reader, greyscale print,
    someone skimming on a phone — has to get the same claim out of the page. So
    a visual needs a caption that says what it means, and a text equivalent that
    carries the same facts. `diagram_svg.py` emits both; hand-written figures
    forget the second one about half the time.
    """
    body = HTML_COMMENT.sub("", text)
    findings = []

    figures = [(m.start(), m.group(0))
               for m in re.finditer(r"<figure\b.*?</figure>", body, re.S | re.I)]
    covered = []
    for start, frag in figures:
        covered.append((start, start + len(frag)))
        line = _line_of(body, start)
        name = _tagless(re.search(r"<figcaption\b.*?</figcaption>", frag, re.S | re.I).group(0)
                        )[:40] if re.search(r"<figcaption", frag, re.I) else f"figure@{line}"
        if not re.search(r"<figcaption\b", frag, re.I):
            findings.append({
                "gate": "rendered-quality", "severity": "fail", "id": f"figcaption:{line}",
                "message": f"{doc_path}:{line} figure has no <figcaption>",
                "hint": "a diagram without a stated takeaway makes the reader guess what "
                        "it proves, and they will guess generously"})
            continue
        if not re.search(r"<(table|details|dl|ol|ul)\b", frag, re.I):
            findings.append({
                "gate": "rendered-quality", "severity": "fail", "id": f"equiv:{line}",
                "message": f"{doc_path}:{line} figure '{name}' has no text equivalent",
                "hint": "add the table or <details> listing the same nodes/edges/rows; "
                        "diagram_svg.py emits one for you"})
        if not EVIDENCE_LABELS.search(frag):
            findings.append({
                "gate": "accuracy-and-evidence", "severity": "warn", "id": f"figev:{line}",
                "message": f"{doc_path}:{line} figure '{name}' states no evidence status",
                "hint": "a diagram reads as verified fact unless it says otherwise"})
        if not re.search(r'\b(scope|from|source|@|rev)\b', frag, re.I):
            findings.append({
                "gate": "accuracy-and-evidence", "severity": "warn", "id": f"figscope:{line}",
                "message": f"{doc_path}:{line} figure '{name}' names no scope or source"})

    def inside_figure(idx: int) -> bool:
        return any(a <= idx <= b for a, b in covered)

    for m in re.finditer(r"<svg\b[^>]*>", body, re.I):
        tag = m.group(0)
        line = _line_of(body, m.start())
        if not inside_figure(m.start()):
            findings.append({
                "gate": "rendered-quality", "severity": "fail", "id": f"svg-loose:{line}",
                "message": f"{doc_path}:{line} inline <svg> sits outside a <figure>",
                "hint": "wrap it so it carries a caption, takeaway, scope and text "
                        "equivalent like every other visual"})
        end = body.lower().find("</svg>", m.start())
        frag = body[m.start():end if end > 0 else m.end()]
        if 'role="img"' not in tag and "role='img'" not in tag:
            findings.append({"gate": "rendered-quality", "severity": "warn",
                             "id": f"svg-role:{line}",
                             "message": f"{doc_path}:{line} inline <svg> has no role=\"img\""})
        if not re.search(r"<title\b", frag, re.I) and "aria-label" not in tag:
            findings.append({
                "gate": "rendered-quality", "severity": "fail", "id": f"svg-title:{line}",
                "message": f"{doc_path}:{line} inline <svg> has no <title> or aria-label",
                "hint": "to a screen reader this is currently a blank space where the "
                        "architecture was"})

    for m in re.finditer(r"<img\b[^>]*>", body, re.I):
        tag, line = m.group(0), _line_of(body, m.start())
        alt = re.search(r'\balt=["\']([^"\']*)["\']', tag)
        if not alt or not alt.group(1).strip():
            findings.append({
                "gate": "rendered-quality", "severity": "fail", "id": f"alt:{line}",
                "message": f"{doc_path}:{line} <img> has no alt text"})
        if not inside_figure(m.start()):
            findings.append({"gate": "rendered-quality", "severity": "warn",
                             "id": f"img-loose:{line}",
                             "message": f"{doc_path}:{line} <img> sits outside a <figure>"})
    return findings


def check_html_hygiene(text: str, doc_path: str) -> list[dict]:
    findings = []
    if not re.search(r"<html\b[^>]*\blang=", text, re.I):
        findings.append({"gate": "rendered-quality", "severity": "fail", "id": "html:lang",
                         "message": f"{doc_path} <html> declares no lang",
                         "hint": 'add lang="en" (or the real language) — assistive '
                                 "technology needs it to pronounce the page"})
    if not re.search(r'<meta[^>]+name=["\']viewport["\']', text, re.I):
        findings.append({"gate": "rendered-quality", "severity": "fail", "id": "html:viewport",
                         "message": f"{doc_path} has no viewport meta",
                         "hint": "without it the page is unreadable on the phone an "
                                 "on-call engineer actually has in their hand"})
    if not re.search(r"<title\b[^>]*>\s*\S", text, re.I):
        findings.append({"gate": "rendered-quality", "severity": "fail", "id": "html:title",
                         "message": f"{doc_path} has no <title>"})
    if re.search(r"<script\b", text, re.I):
        findings.append({
            "gate": "rendered-quality", "severity": "warn", "id": "html:script",
            "message": f"{doc_path} contains <script> — confirm the page is still "
                       f"complete and navigable with JavaScript disabled",
            "hint": "static-first: JS may enhance, never carry content"})
    if re.search(r"@media\s+print", text, re.I) is None:
        findings.append({"gate": "rendered-quality", "severity": "warn", "id": "html:print",
                         "message": f"{doc_path} has no print stylesheet; runbooks get "
                                    f"printed and collapsed sections print collapsed"})
    if "<!-- FILL" in text or "FILL:" in text:
        findings.append({"gate": "scope-and-completeness", "severity": "fail",
                         "id": "html:placeholder",
                         "message": f"{doc_path} still contains template FILL placeholders",
                         "hint": "an unfilled placeholder shipped as documentation is a "
                                 "section the reader will trust and find empty"})
    return findings


def check_containment(doc_path: str, allow_dir: str | None) -> list[dict]:
    if not allow_dir:
        return []
    doc = os.path.abspath(doc_path)
    allowed = os.path.abspath(allow_dir)
    if os.path.commonpath([doc, allowed]) != allowed:
        return [{"gate": "links-and-outputs", "severity": "fail", "id": "output:outside",
                 "message": f"{doc} is outside the authorized output location {allowed}"}]
    return []


def bound_repair(findings: list[dict], state_path: str) -> dict:
    """Enforce the two-attempt repair bound with a file instead of recollection."""
    fail_ids = sorted(f["id"] for f in findings if f["severity"] == "fail")
    if not fail_ids:
        # A pass has nothing to repair. Recording it as a recurring "failure
        # signature" would make two clean runs in a row look like a stuck loop.
        return {"failure_signature": None, "attempts_at_this_signature": 0,
                "repair_budget": 2}
    sig = hashlib.sha256("\n".join(fail_ids).encode()).hexdigest()[:16]
    state = {}
    if os.path.exists(state_path):
        try:
            state = json.load(open(state_path))
        except (OSError, json.JSONDecodeError):
            state = {}
    history = state.get("history", [])
    attempts = sum(1 for h in history if h == sig) + 1
    history.append(sig)
    state.update({"history": history, "last_signature": sig})
    os.makedirs(os.path.dirname(os.path.abspath(state_path)) or ".", exist_ok=True)
    with open(state_path, "w") as fh:
        json.dump(state, fh, indent=2)
    verdict = {"failure_signature": sig, "attempts_at_this_signature": attempts,
               "repair_budget": 2}
    if attempts > 2:
        verdict["directive"] = ("STOP repairing. The same failure set has survived two "
                                "attempts. Report it to the user as an unresolved gap "
                                "instead of spending more tokens.")
    elif attempts == 2 and len(history) > 1 and history[-2] == sig:
        verdict["directive"] = ("Output is unchanged since the last attempt. One more try "
                                "at most, and only with a different approach.")
    return verdict


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--allow-dir")
    ap.add_argument("--areas-na", action="append", default=[],
                    metavar="AREA:REASON",
                    help="mark a content area not applicable, with a reason")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--attempt-state")
    args = ap.parse_args()

    if not os.path.isfile(args.doc):
        print(f"error: no such document: {args.doc}", file=sys.stderr)
        return 2

    na: dict[str, str] = {}
    valid = {n for n, _ in AREAS}
    for item in args.areas_na:
        name, _, reason = item.partition(":")
        name = name.strip().lower()
        if name not in valid:
            print(f"error: unknown content area '{name}'. Valid: {sorted(valid)}",
                  file=sys.stderr)
            return 2
        na[name] = reason.strip() or "(no reason given — a reason is required)"

    text = _load(args.doc)
    is_html = (args.doc.lower().endswith((".html", ".htm"))
               or text.lstrip()[:60].lower().startswith("<!doctype html"))
    findings: list[dict] = []
    findings += check_secrets(text, args.doc)

    if is_html:
        # The evidence legend names all four labels by definition; counting it
        # would let a page pass the evidence gate without labelling a single claim.
        body_only = re.sub(r'<(ul|ol|div)\b[^>]*class=["\'][^"\']*legend[^"\']*["\'].*?</\1>',
                           " ", text, flags=re.S | re.I)
        prose = HTML_TAG.sub(" ", HTML_DROP.sub(" ", HTML_COMMENT.sub(" ", body_only)))
        headings = "\n".join(_tagless(m.group(2)) for m in HTML_HEADING.finditer(text))
        findings += check_links_html(text, args.doc)
        findings += check_visuals_html(text, args.doc)
        findings += check_html_hygiene(text, args.doc)
    else:
        prose = text
        headings = "\n".join(re.findall(r"^#{1,6}\s+(.+?)\s*$", _strip_code(text), re.M))
        findings += check_links(text, args.doc, args.root)
        findings += check_alt_text(text, args.doc)

    findings += check_coverage(headings, na)
    findings += check_evidence_and_summary(prose, args.doc, headings)
    findings += check_containment(args.doc, args.allow_dir)

    fails = [f for f in findings if f["severity"] == "fail"]
    warns = [f for f in findings if f["severity"] == "warn"]
    report = {"document": args.doc, "format": "html" if is_html else "markdown",
              "passed": not fails,
              "counts": {"fail": len(fails), "warn": len(warns),
                         "info": len(findings) - len(fails) - len(warns)},
              "findings": findings}
    if args.attempt_state:
        report["repair"] = bound_repair(findings, args.attempt_state)

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)) or ".", exist_ok=True)
        with open(args.json_out, "w") as fh:
            json.dump(report, fh, indent=2)

    for f in findings:
        print(f"[{f['severity'].upper():4}] {f['gate']}: {f['message']}")
        if f.get("hint") and f["severity"] == "fail":
            print(f"        → {f['hint']}")
    print(f"\n{'PASS' if not fails else 'FAIL'}: {len(fails)} failure(s), "
          f"{len(warns)} warning(s) in {args.doc}")
    if "repair" in report and report["repair"].get("directive"):
        print(f"\nREPAIR BOUND: {report['repair']['directive']}")
    print("\nDeterministic gates only. Accuracy against evidence, operational usefulness "
          "and whether a diagram misleads still need a reader.")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
