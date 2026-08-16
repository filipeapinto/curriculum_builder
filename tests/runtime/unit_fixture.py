"""Build a finalize-able unit output root without a network fetch or a model call.

`prepare()` cannot be used from a test: it fetches primary sources over the network and
refuses an output root outside the engine tree. This reproduces the on-disk shape it
leaves behind, so `finalize()` runs against a real directory with a real open logger ACT.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Any

from curriculum_factory.io import atomic_json, sha256_file
from curriculum_factory.logger import ExecutionLogger
from curriculum_factory.visual_maps import regenerate_assets

ENGINE = Path(__file__).resolve().parents[2]
CURRICULUM = ENGINE / "curricula/arduino_kit"

SOURCE_HTML = """<html><body>
<p>A good-quality breadboard is generally limited to around 2 A.</p>
<p>Each terminal strip joins five holes with one internal spring clip.</p>
<p>The MODEL-9000 meter uses a 10 A socket for high current.</p>
</body></html>"""


def lab_from_run(unit_id: str) -> dict[str, Any]:
    """The shipped unit as it stands in outputs/arduino_kit_run_v2, as a starting point."""
    return json.loads((ENGINE / "outputs/arduino_kit_run_v2" / unit_id / "workers/lab.json").read_text())


def build_run(root: Path, *, unit_id: str, lab: dict[str, Any],
              manifest_unit_ids: list[str] | None = None,
              regenerate: bool = True) -> tuple[Path, Path]:
    """Return `(run_root, unit_root)` for a unit `finalize()` can be pointed at."""
    run_root = Path(root) / "run"
    unit_root = run_root / unit_id
    (run_root / "results").mkdir(parents=True, exist_ok=True)
    ids = manifest_unit_ids or [unit_id]
    atomic_json(run_root / "results/gate_1_static_preflight.json",
                {"unit_ids": ids, "unit_count": len(ids), "status": "PASS"}, root=run_root)
    atomic_json(run_root / "meta_execution_state.json",
                {"authorized_roots": {"engine": str(ENGINE), "curriculum": str(CURRICULUM),
                                      "output_root": str(run_root)},
                 "manifest_sha256": "a" * 64, "prompt_sha256": "b" * 64}, root=run_root)

    inputs = unit_root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CURRICULUM / "domain.schema.v1.json", inputs / "domain.schema.json")
    shutil.copy2(CURRICULUM / "domain.schema.v1.json", inputs / "domain.schema.v1.json")
    shutil.copy2(ENGINE / "schemas/lab.schema.v4.json", inputs / "lab.schema.json")
    shutil.copy2(CURRICULUM / "verify_domain.py", inputs / "verify_domain.py")
    for dependency in ("kit_calibration.v1.yaml", "circuit_library.v1.yaml"):
        shutil.copy2(CURRICULUM / dependency, inputs / dependency)
    shutil.copy2(ENGINE / "policy/calibration.v1.yaml", inputs / "calibration.yaml")

    (unit_root / "sources").mkdir(parents=True, exist_ok=True)
    shipped_sources = ENGINE / "outputs/arduino_kit_run_v2" / unit_id / "sources"
    if shipped_sources.is_dir():
        for cached in shipped_sources.glob("source_*.html"):
            shutil.copy2(cached, unit_root / "sources" / cached.name)
    else:
        (unit_root / "sources/source_01.html").write_text(SOURCE_HTML, encoding="utf-8")
    shipped_manifest = ENGINE / "outputs/arduino_kit_run_v2" / unit_id / "inputs/manifest.yaml"
    if shipped_manifest.is_file():
        shutil.copy2(shipped_manifest, inputs / "manifest.yaml")
    (unit_root / "results").mkdir(parents=True, exist_ok=True)

    workers = unit_root / "workers"
    workers.mkdir(parents=True, exist_ok=True)
    atomic_json(workers / "domain.json", lab["domain"], root=unit_root)

    if regenerate:
        lab, _ = regenerate_assets(lab, CURRICULUM, unit_root, unit_id=unit_id)
    else:
        (unit_root / "assets").mkdir(parents=True, exist_ok=True)
    atomic_json(workers / "lab.json", lab, root=unit_root)

    atomic_json(unit_root / "input_freeze.json", {"files": [], "unit": {"id": unit_id}}, root=unit_root)
    logger = ExecutionLogger(unit_root, ENGINE / "schemas/execution_log.schema.v2.json")
    start_id = logger.start(action="Generate bounded unit domain and document with in-session model",
                            action_kind="model_call", decision_id=f"{unit_id}-in-session-authoring",
                            authorized_paths=[str(workers / "domain.json"), str(workers / "lab.json")],
                            trigger="test fixture", expected="schema-valid domain.json and lab.json")
    atomic_json(unit_root / "worker_request.json",
                {"role": "bounded unit author", "unit": {"id": unit_id}, "model_start_id": start_id},
                root=unit_root)
    atomic_json(unit_root / "interrupt_receipt.json",
                {"forced_interrupt": True,
                 "preserved_hashes": {"input_freeze": sha256_file(unit_root / "input_freeze.json"),
                                      "worker_request": sha256_file(unit_root / "worker_request.json")}},
                root=unit_root)
    return run_root, unit_root


def fill_visual_review(unit_root: Path, *, reviewer: str = "test reviewer",
                       verdict: str = "pass") -> None:
    """Answer every criterion in the structured reviewer verdict finalize() wrote."""
    path = unit_root / "review/visual_review.json"
    record = json.loads(path.read_text())
    record["reviewed"] = True
    record["reviewer"] = reviewer
    for group in ("pages", "visuals"):
        for item in record[group]:
            for key in list(item):
                if item[key] is None:
                    item[key] = verdict
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
