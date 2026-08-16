"""P02 — syntax-aware import/qualified-name codemod: ``runtime`` -> ``curriculum_factory``.

This tool performs a mechanical, LibCST-based rewrite of Python import statements
and qualified-name usages that reference the production import root package
(``runtime``), retargeting them to the packaging-skeleton name established by P01
(``curriculum_factory``). It never touches structured configuration (TOML/JSON/YAML;
owned by P02S), prose/documentation, or files outside the roots it is pointed at,
and it never moves files.

Design (spec v8, P02 prompt goal):

* Import-statement rewriting is *structural*: only the leftmost dotted component of
  an ``import``/``from ... import`` module path is renamed, and only when the import
  is absolute (``ImportFrom.relative`` empty) and that leftmost component is exactly
  ``old_root``. Relative imports (``from . import x``, ``from .sibling import y``) are
  never touched -- they are not references to the top-level production root.
* Usage-site rewriting is *scope-aware*, not textual: a bare ``Name`` node whose text
  equals ``old_root`` is only renamed when LibCST's ``QualifiedNameProvider`` (which is
  itself built on ``ScopeProvider``, i.e. real binding resolution, not regex) reports
  that this specific occurrence resolves, via an import, to ``old_root`` or
  ``old_root.<anything>``. A local variable or parameter literally named ``runtime``
  that shadows the import, an attribute access whose *attribute* (not base) happens to
  be spelled ``runtime``, and a keyword-argument name spelled ``runtime`` all resolve to
  either a non-IMPORT source or no qualified name at all, and are therefore left
  untouched by construction -- no special-casing is required for these explicit
  non-targets; the scope resolution already excludes them.
* String literals and comments are never inspected as identifiers by a CST parser
  (they are not ``Name`` nodes / are lexer trivia), so they are untouched by
  construction as well, *except* that literal string arguments to two recognized
  dynamic-import call shapes (``importlib.import_module(...)``, ``__import__(...)``)
  are inspected read-only to raise an actionable diagnostic (never rewritten, since
  rewriting inside a string changes program behavior in a way this tool cannot verify
  is what the caller of ``import_module`` intended).
* Any construct this tool cannot classify safely (malformed Python; a dynamic-import
  call whose argument is not a literal string) produces a nonzero-severity diagnostic
  and, in apply mode, that whole file is left unmodified (fail closed) even if other
  parts of the same file contained safe candidates.

Pinned parser dependency: this tool requires exactly ``libcst==1.8.2`` (see
``EXPECTED_LIBCST_VERSION`` below) and refuses to run under any other version. P02's
authorized_paths do not include any requirements file (owned by P01/P02S), so this
pin cannot be recorded in ``requirements/plan26.in``/``.lock`` from within this prompt;
it is instead enforced here, in the one file P02 is authorized to write, and recorded
as a residual for a requirements-owning prompt to formalize. See the P02 checkpoint
report for the full rationale.
"""

from __future__ import annotations

import argparse
import difflib
import importlib.metadata
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Union

import libcst as cst
from libcst.metadata import (
    MetadataWrapper,
    PositionProvider,
    QualifiedNameProvider,
    QualifiedNameSource,
)

# --- pinned parser dependency (see module docstring) ---
EXPECTED_LIBCST_VERSION = "1.8.2"
try:
    _installed_libcst_version = importlib.metadata.version("libcst")
except importlib.metadata.PackageNotFoundError:
    _installed_libcst_version = "unknown"
if _installed_libcst_version != EXPECTED_LIBCST_VERSION:
    raise RuntimeError(
        "tools/refactor_repo/rewrite_runtime_imports.py requires libcst=="
        f"{EXPECTED_LIBCST_VERSION} exactly (pinned, see module docstring); found "
        f"{_installed_libcst_version!r}. Install the pinned version "
        f"(e.g. `python3 -m pip install --user libcst=={EXPECTED_LIBCST_VERSION}`) "
        "before running this tool."
    )

DEFAULT_OLD_ROOT = "runtime"
DEFAULT_NEW_ROOT = "curriculum_factory"

# Recognized dynamic-import call shapes. Each entry is a predicate over a Call node's
# callee dotted path (as resolved structurally, not via scope -- these are stdlib
# names almost never shadowed, and P00's inventory found none shadowed in this repo).
_DYNAMIC_IMPORT_CALLEES = {
    ("importlib", "import_module"),
    ("__import__",),
}


# --------------------------------------------------------------------------- #
# Diagnostics
# --------------------------------------------------------------------------- #

@dataclass
class Diagnostic:
    file: str
    line: int
    column: int
    kind: str
    severity: str  # "info" | "warning" | "unsafe" | "blocker"
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "kind": self.kind,
            "severity": self.severity,
            "detail": self.detail,
        }


UNSAFE_SEVERITIES = {"unsafe", "blocker"}


# --------------------------------------------------------------------------- #
# Dotted-path helpers
# --------------------------------------------------------------------------- #

def _dotted_parts(node: Union[cst.Name, cst.Attribute]) -> list[str]:
    if isinstance(node, cst.Name):
        return [node.value]
    if isinstance(node, cst.Attribute):
        return _dotted_parts(node.value) + [node.attr.value]  # type: ignore[arg-type]
    raise TypeError(f"not a dotted module path node: {type(node)!r}")


def _rename_root(
    node: Union[cst.Name, cst.Attribute], old_root: str, new_root: str
) -> Union[cst.Name, cst.Attribute]:
    """Rename only the leftmost (root) component of a dotted Name/Attribute chain."""
    if isinstance(node, cst.Name):
        if node.value == old_root:
            return node.with_changes(value=new_root)
        return node
    if isinstance(node, cst.Attribute):
        return node.with_changes(value=_rename_root(node.value, old_root, new_root))  # type: ignore[arg-type]
    return node


def _literal_string_value(node: cst.BaseExpression) -> Optional[str]:
    if isinstance(node, cst.SimpleString):
        try:
            return node.evaluated_value  # type: ignore[return-value]
        except Exception:
            return None
    if isinstance(node, cst.ConcatenatedString):
        left = _literal_string_value(node.left)
        right = _literal_string_value(node.right)
        if left is not None and right is not None:
            return left + right
        return None
    return None


def _callee_dotted_path(func: cst.BaseExpression) -> Optional[tuple[str, ...]]:
    if isinstance(func, cst.Name):
        return (func.value,)
    if isinstance(func, cst.Attribute):
        try:
            return tuple(_dotted_parts(func))
        except TypeError:
            return None
    return None


# --------------------------------------------------------------------------- #
# Transformer
# --------------------------------------------------------------------------- #

class _RuntimeImportRewriter(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (QualifiedNameProvider, PositionProvider)

    def __init__(self, filename: str, old_root: str, new_root: str) -> None:
        super().__init__()
        self.filename = filename
        self.old_root = old_root
        self.new_root = new_root
        self.diagnostics: list[Diagnostic] = []
        self.rewrite_count = 0
        self._new_root_import_seen_at_top_level = False

    # -- position helper --
    def _pos(self, node: cst.CSTNode) -> tuple[int, int]:
        try:
            pos = self.get_metadata(PositionProvider, node)
            return pos.start.line, pos.start.column
        except KeyError:
            return 0, 0

    def _add(self, node: cst.CSTNode, kind: str, severity: str, detail: str) -> None:
        line, col = self._pos(node)
        self.diagnostics.append(
            Diagnostic(self.filename, line, col, kind, severity, detail)
        )

    # -- import statement (definition-site) rewriting --
    def leave_ImportAlias(
        self, original_node: cst.ImportAlias, updated_node: cst.ImportAlias
    ) -> cst.ImportAlias:
        name = original_node.name
        if not isinstance(name, (cst.Name, cst.Attribute)):
            return updated_node
        try:
            parts = _dotted_parts(name)
        except TypeError:
            return updated_node
        if parts[0] != self.old_root:
            return updated_node
        new_name = _rename_root(updated_node.name, self.old_root, self.new_root)  # type: ignore[arg-type]
        self.rewrite_count += 1
        self._add(
            original_node,
            "rewrite_import",
            "info",
            f"import target '{'.'.join(parts)}' -> "
            f"'{self.new_root}{'.'.join([''] + parts[1:])}'",
        )
        return updated_node.with_changes(name=new_name)

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        module = original_node.module
        if module is None:
            return updated_node  # relative-only ("from . import x"): explicit non-target
        if original_node.relative:
            return updated_node  # relative import: explicit non-target, never rewritten
        try:
            parts = _dotted_parts(module)  # type: ignore[arg-type]
        except TypeError:
            return updated_node
        if parts[0] != self.old_root:
            return updated_node
        new_module = _rename_root(updated_node.module, self.old_root, self.new_root)  # type: ignore[arg-type]
        self.rewrite_count += 1
        self._add(
            original_node,
            "rewrite_import",
            "info",
            f"from-import module '{'.'.join(parts)}' -> "
            f"'{self.new_root}{'.'.join([''] + parts[1:])}'",
        )
        return updated_node.with_changes(module=new_module)

    # -- usage-site (qualified-name) rewriting --
    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        if original_node.value != self.old_root:
            return updated_node
        qnames = self.get_metadata(QualifiedNameProvider, original_node, set())
        import_matches = [
            qn
            for qn in qnames
            if qn.source == QualifiedNameSource.IMPORT
            and (qn.name == self.old_root or qn.name.startswith(self.old_root + "."))
        ]
        if import_matches:
            self.rewrite_count += 1
            self._add(
                original_node,
                "rewrite_reference",
                "info",
                f"qualified-name usage resolved via import to "
                f"'{import_matches[0].name}' -- renamed leaf to '{self.new_root}'",
            )
            return updated_node.with_changes(value=self.new_root)
        non_import_matches = [qn for qn in qnames if qn.name != self.old_root or qn.source != QualifiedNameSource.IMPORT]
        if qnames and not import_matches:
            # Bound to something other than an import of old_root (e.g. a local
            # variable or parameter shadowing the package name): explicit non-target.
            self._add(
                original_node,
                "non_target_shadowed",
                "info",
                f"identifier '{self.old_root}' resolves to a non-import binding "
                f"({sorted(qn.source.name for qn in qnames)}); left untouched "
                "(ambiguous/shadowed, not the production import root)",
            )
        return updated_node

    # -- dynamic import diagnostics (read-only; never rewritten) --
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        callee = _callee_dotted_path(original_node.func)
        if callee not in _DYNAMIC_IMPORT_CALLEES:
            return updated_node
        if not original_node.args:
            return updated_node
        first_arg = original_node.args[0].value
        literal = _literal_string_value(first_arg)
        if literal is not None:
            first_component = literal.split(".")[0]
            if first_component == self.old_root:
                self._add(
                    original_node,
                    "dynamic_import_literal",
                    "warning",
                    f"dynamic import call {'.'.join(callee)}({literal!r}) references "
                    f"'{self.old_root}' via a string literal; not rewritten "
                    "(dynamic import targets are read-only diagnostics, never mutated)",
                )
        else:
            self._add(
                original_node,
                "dynamic_import_unresolvable",
                "unsafe",
                f"dynamic import call {'.'.join(callee)}(...) has a non-literal "
                "argument; the effective module name cannot be classified safely "
                "and this file is not modified",
            )
        return updated_node


def _find_duplicate_new_root_imports(module: cst.Module, new_root: str) -> list[tuple[int, int, str]]:
    """Detect >1 top-level import binding the bare new_root name after rewriting."""
    hits: list[tuple[int, int, str]] = []
    wrapper = MetadataWrapper(module)
    positions = wrapper.resolve(PositionProvider)
    count = 0
    last_pos = None
    for stmt in module.body:
        if not isinstance(stmt, cst.SimpleStatementLine):
            continue
        for small in stmt.body:
            if isinstance(small, cst.Import):
                for alias in small.names:
                    if isinstance(alias.name, cst.Name) and alias.name.value == new_root and alias.asname is None:
                        count += 1
                        pos = positions.get(stmt)
                        last_pos = (pos.start.line, pos.start.column) if pos else (0, 0)
    if count > 1 and last_pos is not None:
        hits.append((last_pos[0], last_pos[1], f"{count} top-level 'import {new_root}' statements present after rewrite"))
    return hits


# --------------------------------------------------------------------------- #
# Single-source API (used directly by fixture tests)
# --------------------------------------------------------------------------- #

@dataclass
class RewriteResult:
    filename: str
    original_source: str
    new_source: str
    changed: bool
    unsafe: bool
    diagnostics: list[Diagnostic] = field(default_factory=list)
    parse_error: Optional[str] = None


def rewrite_source(
    source: str,
    *,
    filename: str = "<string>",
    old_root: str = DEFAULT_OLD_ROOT,
    new_root: str = DEFAULT_NEW_ROOT,
) -> RewriteResult:
    try:
        module = cst.parse_module(source)
    except cst.ParserSyntaxError as error:
        diag = Diagnostic(filename, getattr(error, "raw_line", 0) or 0,
                           getattr(error, "raw_column", 0) or 0,
                           "parse_error", "unsafe", f"malformed Python: {error}")
        return RewriteResult(filename, source, source, False, True, [diag], str(error))

    wrapper = MetadataWrapper(module)
    rewriter = _RuntimeImportRewriter(filename, old_root, new_root)
    try:
        new_module = wrapper.visit(rewriter)
    except Exception as error:  # pragma: no cover - defensive fail-closed path
        diag = Diagnostic(filename, 0, 0, "transform_error", "unsafe",
                           f"codemod transform raised {type(error).__name__}: {error}")
        return RewriteResult(filename, source, source, False, True, [diag], None)

    diagnostics = list(rewriter.diagnostics)
    for line, col, detail in _find_duplicate_new_root_imports(new_module, new_root):
        diagnostics.append(Diagnostic(filename, line, col, "duplicate_import_after_rewrite", "warning", detail))

    unsafe = any(d.severity in UNSAFE_SEVERITIES for d in diagnostics)
    new_source = new_module.code
    changed = new_source != source
    if unsafe:
        # Fail closed: an unsafe construct anywhere in the file withholds the whole
        # file's changes, even if other candidates in it were individually safe.
        return RewriteResult(filename, source, source, False, True, diagnostics, None)
    return RewriteResult(filename, source, new_source, changed, False, diagnostics, None)


# --------------------------------------------------------------------------- #
# Residual-reference postcondition scan (read-only)
# --------------------------------------------------------------------------- #

def scan_residuals(
    source: str,
    *,
    filename: str = "<string>",
    old_root: str = DEFAULT_OLD_ROOT,
    new_root: str = DEFAULT_NEW_ROOT,
    check_unexpected_new_root: bool = False,
) -> list[Diagnostic]:
    """Read-only postcondition scan: report any remaining import-bound reference to
    old_root, and optionally check for unexpected new_root references, without
    mutating anything."""
    diagnostics: list[Diagnostic] = []
    try:
        module = cst.parse_module(source)
    except cst.ParserSyntaxError as error:
        return [Diagnostic(filename, getattr(error, "raw_line", 0) or 0,
                            getattr(error, "raw_column", 0) or 0,
                            "parse_error", "unsafe", f"malformed Python: {error}")]

    class _Scanner(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (QualifiedNameProvider, PositionProvider)

        def visit_Name(self_inner, node: cst.Name) -> None:
            # Check for old_root residuals
            if node.value == old_root:
                qnames = self_inner.get_metadata(QualifiedNameProvider, node, set())
                if any(
                    qn.source == QualifiedNameSource.IMPORT
                    and (qn.name == old_root or qn.name.startswith(old_root + "."))
                    for qn in qnames
                ):
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(
                            filename, pos.start.line, pos.start.column,
                            "residual_old_reference", "blocker",
                            f"'{old_root}' reference still import-bound after rewrite pass",
                        )
                    )
            # Check for unexpected new_root references (only if enabled)
            elif check_unexpected_new_root and node.value == new_root:
                qnames = self_inner.get_metadata(QualifiedNameProvider, node, set())
                if any(
                    qn.source == QualifiedNameSource.IMPORT
                    and (qn.name == new_root or qn.name.startswith(new_root + "."))
                    for qn in qnames
                ):
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(
                            filename, pos.start.line, pos.start.column,
                            "unexpected_new_reference", "blocker",
                            f"unexpected '{new_root}' reference; check that it was authorized or produced by rewrite",
                        )
                    )

        def visit_ImportAlias(self_inner, node: cst.ImportAlias) -> None:
            if isinstance(node.name, (cst.Name, cst.Attribute)):
                try:
                    parts = _dotted_parts(node.name)
                except TypeError:
                    return
                if parts[0] == old_root:
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(filename, pos.start.line, pos.start.column,
                                   "residual_old_reference", "blocker",
                                   f"import statement still targets '{'.'.join(parts)}'")
                    )
                elif check_unexpected_new_root and parts[0] == new_root:
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(filename, pos.start.line, pos.start.column,
                                   "unexpected_new_reference", "blocker",
                                   f"unexpected import statement targets '{'.'.join(parts)}'; check authorization")
                    )

        def visit_ImportFrom(self_inner, node: cst.ImportFrom) -> None:
            if node.module is not None and not node.relative:
                try:
                    parts = _dotted_parts(node.module)  # type: ignore[arg-type]
                except TypeError:
                    return
                if parts[0] == old_root:
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(filename, pos.start.line, pos.start.column,
                                   "residual_old_reference", "blocker",
                                   f"from-import statement still targets '{'.'.join(parts)}'")
                    )
                elif check_unexpected_new_root and parts[0] == new_root:
                    pos = self_inner.get_metadata(PositionProvider, node)
                    diagnostics.append(
                        Diagnostic(filename, pos.start.line, pos.start.column,
                                   "unexpected_new_reference", "blocker",
                                   f"unexpected from-import statement targets '{'.'.join(parts)}'; check authorization")
                    )

    wrapper = MetadataWrapper(module)
    wrapper.visit(_Scanner())
    return diagnostics


# --------------------------------------------------------------------------- #
# Filesystem driver
# --------------------------------------------------------------------------- #

def _iter_python_files(roots: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        if root.is_file() and root.suffix == ".py":
            files.add(root.resolve())
        elif root.is_dir():
            for path in root.rglob("*.py"):
                if "__pycache__" in path.parts:
                    continue
                files.add(path.resolve())
    return sorted(files)


def _relativize(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def run_dry_run(
    roots: list[Path], repo_root: Path, old_root: str, new_root: str
) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    files = _iter_python_files(roots)
    all_diagnostics: list[dict[str, Any]] = []
    diff_chunks: list[str] = []
    summary = {"files_scanned": 0, "files_would_change": 0, "files_unsafe": 0, "files_parse_error": 0}
    for path in files:
        rel = _relativize(path, repo_root)
        source = path.read_text(encoding="utf-8")
        result = rewrite_source(source, filename=rel, old_root=old_root, new_root=new_root)
        summary["files_scanned"] += 1
        if result.parse_error:
            summary["files_parse_error"] += 1
        if result.unsafe:
            summary["files_unsafe"] += 1
        if result.changed:
            summary["files_would_change"] += 1
            diff = difflib.unified_diff(
                source.splitlines(keepends=True),
                result.new_source.splitlines(keepends=True),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
            diff_chunks.append("".join(diff))
        all_diagnostics.extend(d.to_dict() for d in result.diagnostics)
    all_diagnostics.sort(key=lambda d: (d["file"], d["line"], d["column"], d["kind"]))
    return all_diagnostics, "".join(diff_chunks), summary


def run_apply(
    roots: list[Path], repo_root: Path, old_root: str, new_root: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = _iter_python_files(roots)
    all_diagnostics: list[dict[str, Any]] = []
    summary = {"files_scanned": 0, "files_changed": 0, "files_unsafe": 0, "files_parse_error": 0}
    for path in files:
        rel = _relativize(path, repo_root)
        source = path.read_text(encoding="utf-8")
        result = rewrite_source(source, filename=rel, old_root=old_root, new_root=new_root)
        summary["files_scanned"] += 1
        if result.parse_error:
            summary["files_parse_error"] += 1
        if result.unsafe:
            summary["files_unsafe"] += 1
        if result.changed:
            path.write_text(result.new_source, encoding="utf-8")
            summary["files_changed"] += 1
        all_diagnostics.extend(d.to_dict() for d in result.diagnostics)
    all_diagnostics.sort(key=lambda d: (d["file"], d["line"], d["column"], d["kind"]))
    return all_diagnostics, summary


def run_postcondition_scan(
    roots: list[Path], repo_root: Path, old_root: str, new_root: str,
    check_unexpected_new_root: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = _iter_python_files(roots)
    all_diagnostics: list[dict[str, Any]] = []
    summary = {"files_scanned": 0, "files_with_residuals": 0, "residual_count": 0}
    for path in files:
        rel = _relativize(path, repo_root)
        source = path.read_text(encoding="utf-8")
        diagnostics = scan_residuals(
            source, filename=rel, old_root=old_root, new_root=new_root,
            check_unexpected_new_root=check_unexpected_new_root,
        )
        summary["files_scanned"] += 1
        if diagnostics:
            summary["files_with_residuals"] += 1
            summary["residual_count"] += len(diagnostics)
        all_diagnostics.extend(d.to_dict() for d in diagnostics)
    all_diagnostics.sort(key=lambda d: (d["file"], d["line"], d["column"], d["kind"]))
    return all_diagnostics, summary


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["dry-run", "apply", "postcondition-scan"])
    parser.add_argument("--root", action="append", required=True, dest="roots",
                         help="File or directory to scan; may be repeated.")
    parser.add_argument("--repo-root", default=".", help="Root used to relativize reported paths.")
    parser.add_argument("--old-root", default=DEFAULT_OLD_ROOT)
    parser.add_argument("--new-root", default=DEFAULT_NEW_ROOT)
    parser.add_argument("--diagnostics-out", required=True, type=Path)
    parser.add_argument("--diff-out", type=Path, help="dry-run only: unified diff output path")
    parser.add_argument("--check-unexpected-new-root", action="store_true",
                         help="postcondition-scan only: report unexpected new-root references")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    roots = [Path(r).resolve() for r in args.roots]

    if args.mode == "dry-run":
        diagnostics, diff_text, summary = run_dry_run(roots, repo_root, args.old_root, args.new_root)
        if args.diff_out is not None:
            args.diff_out.write_text(diff_text, encoding="utf-8")
    elif args.mode == "apply":
        diagnostics, summary = run_apply(roots, repo_root, args.old_root, args.new_root)
    else:
        diagnostics, summary = run_postcondition_scan(
            roots, repo_root, args.old_root, args.new_root,
            check_unexpected_new_root=args.check_unexpected_new_root,
        )

    report = {
        "tool": "tools/refactor_repo/rewrite_runtime_imports.py",
        "libcst_version": EXPECTED_LIBCST_VERSION,
        "mode": args.mode,
        "old_root": args.old_root,
        "new_root": args.new_root,
        "summary": summary,
        "diagnostics": diagnostics,
    }
    args.diagnostics_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    unsafe_present = any(d["severity"] in UNSAFE_SEVERITIES for d in diagnostics)
    return 1 if unsafe_present else 0


if __name__ == "__main__":
    sys.exit(main())
