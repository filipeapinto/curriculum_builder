from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_outputs_is_ignored_and_contains_no_durable_fixture():
    gitignore = (ROOT / ".gitignore").read_text().splitlines()
    assert "outputs/" in gitignore
    output = ROOT / "outputs"
    assert not output.exists() or not any(output.iterdir())


def test_fixture_disposition_records_empty_inventory():
    ledger = (ROOT / "plans_internal/refactor_repo/fixture_dispositions.v1.yaml").read_text()
    assert "children: []" in ledger
    assert "No output child was deleted" in ledger
