import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_product_readme_uses_canonical_identity_and_live_paths():
    readme = (ROOT / "readme.md").read_text()
    assert readme.startswith("# Curriculum Factory\n")
    assert "`curriculum-factory`" in readme
    assert "`curriculum_factory`" in readme
    for relative in (
        "meta_prompt/curriculum.prompt.v1.md",
        "docs/images/png/curriculum_pipeline_infographic.v2.png",
        "docs/images/prompts/curriculum_pipeline_infographic.v2.prompt.md",
    ):
        assert (ROOT / relative).is_file(), relative


def test_test_tree_cannot_shadow_production_package():
    assert not (ROOT / "tests/curriculum_factory").exists()
    spec = importlib.util.find_spec("curriculum_factory")
    assert spec is not None and spec.origin
    assert "/tests/" not in spec.origin
