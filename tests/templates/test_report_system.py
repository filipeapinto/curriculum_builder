from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "templates/report-system/build/assemble_report.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("assemble_report", BUILDER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_issued_report_templates_are_fresh_standalone_builds():
    builder = load_builder()
    cases = (
        ("issue-report.template.v10.source.html", "issue-report.template.v10.html"),
        ("issue.template.v2.source.html", "issue.template.v2.html"),
    )
    for source_name, output_name in cases:
        source = ROOT / "templates/report-system/sources" / source_name
        output = ROOT / "templates" / output_name
        rendered = builder.assemble(source)
        assert output.read_text(encoding="utf-8") == rendered
        assert 'data-report-system="v1"' in rendered
        assert "{{{REPORT_SYSTEM_CSS}}}" not in rendered


def test_component_includes_expand_without_consuming_report_placeholders(tmp_path):
    builder = load_builder()
    source = tmp_path / "component.source.html"
    source.write_text("{{> report-header}}", encoding="utf-8")
    rendered = builder.assemble(source)
    assert '<header class="report-hero">' in rendered
    assert "{{TITLE}}" in rendered
    assert "{{>" not in rendered
