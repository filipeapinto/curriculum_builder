from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from runtime.langgraph_factory import transport as tp


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: Path, engine: Path) -> dict[str, str]:
    return {"path": path.relative_to(engine).as_posix(), "sha256": sha(path)}


def transport_for(engine: Path, output: Path) -> tp.CliTransport:
    transport = object.__new__(tp.CliTransport)
    transport.engine_root = engine.resolve()
    transport.output_root = output.resolve()
    return transport


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rc19-verifier-probes-") as raw:
        temp = Path(raw).resolve()
        engine = temp / "engine"
        curriculum = engine / "curricula" / "synthetic"
        fixtures = curriculum / "fixtures"
        fixtures.mkdir(parents=True)
        output = engine / "outputs" / "run27" / "live_unit"
        output.mkdir(parents=True)

        undeclared = engine / "undeclared.txt"
        undeclared.write_text("four", encoding="utf-8")
        dependency = curriculum / "sidecars" / "declared.json"
        dependency.parent.mkdir()
        dependency.write_text('{"policy":"frozen"}\n', encoding="utf-8")
        reject = fixtures / "reject.json"
        accept = fixtures / "accept.json"
        reject.write_text("{}\n", encoding="utf-8")
        accept.write_text("{}\n", encoding="utf-8")
        entry = curriculum / "verify.py"
        entry.write_text(
            f'''from pathlib import Path
import argparse
p = argparse.ArgumentParser()
p.add_argument("--domain", type=Path, required=True)
a = p.parse_args()
if a.domain.name == "reject.json":
    print("synthetic-reject: expected fixture rejection")
    raise SystemExit(1)
if a.domain.name == "accept.json":
    raise SystemExit(0)
blocked = []
for name, path in (("file", Path({str(undeclared)!r})), ("directory", Path({str(engine)!r}))):
    try:
        path.stat()
    except PermissionError:
        blocked.append(name)
print("metadata-blocked:" + ",".join(blocked))
raise SystemExit(0 if blocked == ["file", "directory"] else 1)
''',
            encoding="utf-8",
        )

        contract = {
            "verifier": {
                "entry_point": ref(entry, engine),
                "invocation": "python3 curricula/synthetic/verify.py --domain <domain>",
                "dependencies": [ref(dependency, engine)],
                "must_reject": [
                    {"fixture": ref(reject, engine), "expected_code": "synthetic-reject"}
                ],
                "must_accept": [ref(accept, engine)],
                "proven": {"result": "all_fixtures_behaved"},
            }
        }
        candidate = {"probe": "metadata"}
        transport = transport_for(engine, output)
        root = tp.domain_verifier_work_root(engine_root=engine, output_root=output)
        first = transport.verify_domain(body=candidate, contract=contract)
        undeclared.rename(engine / "renamed-undeclared.txt")
        second = transport.verify_domain(body=candidate, contract=contract)

        contract_sha = tp.canonical_digest(contract)
        candidate_sha = tp.canonical_digest(candidate)
        work = root / contract_sha / candidate_sha
        profile = (work / "home" / "verifier.sb").read_text(encoding="utf-8")
        staged_dependency = work / "frozen" / dependency.relative_to(engine)
        conflict_result = "NOT_RUN"
        staged_dependency.write_text('{"policy":"conflict"}\n', encoding="utf-8")
        try:
            transport.verify_domain(body=candidate, contract=contract)
        except tp.VerifierFault as error:
            conflict_result = str(error)

        # Mutate a source after resolve_reference's first hash but before the
        # staging read. The second hash over copied bytes must refuse it.
        race_dependency = curriculum / "sidecars" / "race.json"
        race_dependency.write_text('{"generation":1}\n', encoding="utf-8")
        race_contract = json.loads(json.dumps(contract))
        race_contract["verifier"]["dependencies"] = [ref(race_dependency, engine)]
        original_work_root = tp.domain_verifier_work_root

        def mutate_between_hash_and_copy(*, engine_root: Path, output_root: Path) -> Path:
            race_dependency.write_text('{"generation":2}\n', encoding="utf-8")
            return original_work_root(engine_root=engine_root, output_root=output_root)

        tp.domain_verifier_work_root = mutate_between_hash_and_copy
        race_result = "NOT_RUN"
        try:
            transport.verify_domain(body=candidate, contract=race_contract)
        except tp.VerifierFault as error:
            race_result = str(error)
        finally:
            tp.domain_verifier_work_root = original_work_root

        print(json.dumps({
            "work_root_outside_engine": root != engine and engine not in root.parents,
            "work_root_outside_output": root != output and output not in root.parents,
            "first_result": first["result"],
            "second_result_after_undeclared_rename": second["result"],
            "same_candidate_sha256": first["candidate_sha256"] == second["candidate_sha256"],
            "first_output": first["candidate"]["output_excerpt"].strip(),
            "second_output": second["candidate"]["output_excerpt"].strip(),
            "staged_layout_preserved": staged_dependency == (
                work / "frozen/curricula/synthetic/sidecars/declared.json"
            ),
            "staged_entry_used": str(work / "frozen" / entry.relative_to(engine))
                in first["candidate"]["output_excerpt"] or first["result"] == "PASS",
            "network_denied": "(deny network*)" in profile,
            "engine_metadata_denied": (
                "(deny file-read-metadata" in profile and str(engine) in profile
            ),
            "engine_metadata_exemption_present": (
                f'(allow file-read* (subpath "{engine}"))' in profile
                or f'(literal "{engine}")' in profile
            ),
            "model_auth_or_scratch_present": any(token in profile for token in (
                str(Path.home() / ".codex" / "auth.json"),
                str(Path.home() / "Library" / "Keychains"),
                "/tmp/claude-",
            )),
            "staged_conflict_result": conflict_result,
            "copy_race_result": race_result,
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
