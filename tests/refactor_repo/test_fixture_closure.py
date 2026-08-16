import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_outputs_is_ignored_and_contains_no_durable_fixture():
    gitignore = (ROOT / ".gitignore").read_text().splitlines()
    assert "outputs/" in gitignore
    output = ROOT / "outputs"
    assert not output.exists() or not any(output.iterdir())


def test_fixture_disposition_records_empty_inventory():
    ledger = (ROOT / "plans_internal/refactor_repo/fixture_dispositions.v1.yaml").read_text()
    assert "arduino_kit_run_v2" in ledger
    assert "no source byte was deleted" in ledger


def test_run_fixture_manifest_is_bidirectionally_closed():
    fixture = ROOT / "tests/fixtures/refactor_repo/arduino_kit_run_v2"
    manifest = json.loads((fixture / "fixture_manifest.json").read_text())
    declared = {entry["path"] for entry in manifest["files"]}
    actual = {path.relative_to(fixture).as_posix() for path in fixture.rglob("*") if path.is_file()}
    assert actual == declared | {"fixture_manifest.json"}
    for entry in manifest["files"]:
        path = fixture / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        assert entry["consumer"] and entry["requirement"]
