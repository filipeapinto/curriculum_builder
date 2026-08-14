from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from runtime.curriculum_factory_graph import (CurriculumFactoryGraph, FactoryGraphFailure,
                                              NODE_IDS, PROMPT_FILES)
from runtime.factory_state import FactoryStateError, FactoryStateStore
from runtime.io import sha256_file


ENGINE = Path(__file__).resolve().parents[2]
MANIFEST = ENGINE / "curricula/arduino_kit/arduino_kit_curriculum.v5.yaml"
SHIPPED_L01 = ENGINE / "outputs/arduino_kit_run_v2/L01"


class FakeCapabilities:
    def prove(self, root: Path, *, full_run: bool) -> dict:
        return {"status": "PASS", "fake": True, "full_run": full_run}


class FakeWorker:
    def __init__(self, family: str):
        self.family = family

    def probe(self, workspace: Path) -> dict:
        return {"status": "PASS"}

    def _decision(self, activation_id: str, job: str) -> dict:
        model = "gpt-5.4" if self.family == "openai" else "fake-review-model-x1"
        return {
            "task_id": activation_id, "task_class": job, "risk": "high",
            "candidate_pool": [model], "decided_model": model, "executed_model": model,
            "reasoning_effort": "max" if self.family == "azure" else "high",
            "pro_mode": self.family == "azure", "quality_gate": ["bounded artifact"],
            "decision_rationale": "test transport for controller integration",
            "evidence_inputs": ["authorized_input.json"], "escalate_when": [],
            "substitution": None, "status": "approved_to_run",
        }

    def run(self, *, activation_id: str, job: str, prompt_path: Path,
            request: dict, output_schema: dict, workspace: Path):
        workspace.mkdir(parents=True, exist_ok=False)
        if job == "research_unit_sources":
            if request["mode"] == "DISCOVER":
                result = {"sources": [{
                    "url": "https://example.com/primary", "publisher": "Example Authority",
                    "title": "Primary reference", "claim_scope": "bounded unit facts",
                    "why_primary": "published by the original authority",
                }]}
            else:
                record = request["allowed_retrieval_results"][0]
                result = {"sources": [{
                    "retrieval_result_id": record["retrieval_result_id"],
                    "source_title": "ELEGOO kit listing", "publisher": "ELEGOO",
                    "exact_locator": "Included 9 V battery with DC connector",
                    "supported_facts": ["The kit includes a 9 V battery with DC connector."],
                    "claim_scope": "kit inventory only",
                }], "unresolved": []}
        elif job == "create_unit_domain_data":
            result = json.loads((SHIPPED_L01 / "workers/lab.json").read_text())["domain"]
        elif job == "write_unit_content":
            result = json.loads((SHIPPED_L01 / "workers/lab.json").read_text())
        elif job == "create_unit_visuals":
            result = {
                "filename": "safe_disconnected_setup.svg",
                "svg": ("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" "
                        "height=\"800\"><rect width=\"1200\" height=\"800\" fill=\"white\"/>"
                        "<text x=\"80\" y=\"160\" font-size=\"54\">Battery lead disconnected</text>"
                        "</svg>"),
                "role": "subject_identification", "supports_section": "identification",
                "alt_text": "A clearly labelled disconnected battery lead beside the kit.",
            }
        elif job in {"review_unit", "review_workbook"}:
            result = {"findings": [], "page_results": [
                {"page_number": item["page_number"], "result": "PASS", "notes": "clear"}
                for item in request["pages"]], "verdict": "PASS"}
        elif job == "repair_unit_artifact":
            result = request["parent_artifact"]
        else:
            raise AssertionError(f"unexpected model job: {job}")
        result_path = workspace / "result.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        receipt = {
            "family": self.family, "decision": self._decision(activation_id, job),
            "output_sha256": sha256_file(result_path),
        }
        return result, receipt


class InterruptingReviewer(FakeWorker):
    def run(self, **kwargs):
        if kwargs["job"] == "review_unit":
            raise KeyboardInterrupt()
        return super().run(**kwargs)


class FactoryStateTests(unittest.TestCase):
    def test_terminal_is_write_once_and_only_interrupt_can_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FactoryStateStore(Path(directory))
            store.initialize({"run_id": "r1"}, {"a": "b"}, {})
            store.write_terminal("INTERRUPTED", {"checkpoint": "c1"})
            with self.assertRaises(FactoryStateError):
                store.write_terminal("COMPLETE", {})
            store.resume_interrupted()
            self.assertIsNone(store.read()["terminal"])
            self.assertEqual(store.read()["terminal_history"][0]["terminal"], "INTERRUPTED")


class FactoryPackageTests(unittest.TestCase):
    def test_model_nodes_bind_exact_package_relative_prompts(self):
        graph = CurriculumFactoryGraph(ENGINE, author=FakeWorker("openai"),
                                       reviewer=FakeWorker("azure"),
                                       capabilities=FakeCapabilities())
        hashes = graph._require_package()
        self.assertEqual(set(PROMPT_FILES) | {"graph"}, set(hashes))
        self.assertTrue(all(path.parent == graph.package / "prompts"
                            for path in graph.prompts.values()))
        self.assertEqual(8, sum(node.startswith("M") for node in NODE_IDS))
        self.assertEqual(32, sum(node.startswith("D") for node in NODE_IDS))

    def test_package_is_exact_and_every_node_is_declared_in_graph(self):
        package = ENGINE / "plans/25_curriculum_factory_graph"
        expected = {
            "curriculum_factory.graph.v1.md", "run_curriculum_factory.prompt.v1.md",
            "qa_criteria.v1.md", "previous_plan.obs.v1.md",
            *{f"prompts/{name}" for name in PROMPT_FILES.values()},
        }
        actual = {str(path.relative_to(package)) for path in package.rglob("*") if path.is_file()}
        self.assertEqual(expected, actual)
        graph_text = (package / "curriculum_factory.graph.v1.md").read_text()
        for node in NODE_IDS:
            with self.subTest(node=node):
                self.assertIn(node, graph_text)
        runtime_text = (ENGINE / "runtime/curriculum_factory_graph.py").read_text()
        for forbidden in ("arduino_kit", '"L01"', "35"):
            self.assertNotIn(forbidden, runtime_text)

    def test_findings_are_routed_to_one_named_owner(self):
        review = {"findings": [{
            "criterion_id": "visual", "severity": "blocking",
            "artifact_owner": "unit_visual", "exact_location": "page 2",
            "observed_defect": "wrong label", "required_correction": "fix label",
        }]}
        owner, findings = CurriculumFactoryGraph._classify_unit_findings(
            ["PDF-VISUAL-REVIEW"], review)
        self.assertEqual("unit_visual", owner)
        self.assertEqual(1, len(findings))

    def test_exact_active_manifest_path_is_accepted(self):
        graph = CurriculumFactoryGraph(ENGINE, author=FakeWorker("openai"),
                                       reviewer=FakeWorker("azure"),
                                       capabilities=FakeCapabilities())
        curriculum, manifest = graph._resolve_curriculum_input(MANIFEST)
        self.assertEqual(MANIFEST.resolve(), manifest)
        self.assertEqual(MANIFEST.parent.resolve(), curriculum)


class FactoryOneUnitIntegrationTests(unittest.TestCase):
    def test_l01_reaches_unit_accepted_only_with_actual_pdf_and_review(self):
        source_bytes = (SHIPPED_L01 / "sources/source_01.html").read_bytes()
        with tempfile.TemporaryDirectory(dir=ENGINE / "outputs") as directory:
            output = Path(directory) / "factory-run"
            graph = CurriculumFactoryGraph(
                ENGINE, author=FakeWorker("openai"), reviewer=FakeWorker("azure"),
                fetcher=lambda _url: source_bytes, capabilities=FakeCapabilities())
            with mock.patch("runtime.curriculum_factory_graph.readability_problems",
                            return_value=[]):
                result = graph.run(curriculum=MANIFEST, output_root=output, lab_id="L01")
            self.assertEqual("UNIT_ACCEPTED", result["terminal"], result)
            receipt = result["unit"]
            self.assertEqual("ACCEPTED", receipt["terminal_state"])
            self.assertTrue((output / "L01" / receipt["pdf"]).is_file())
            checks = json.loads((output / "L01/results/unit_checks.json").read_text())["checks"]
            self.assertTrue(all(not value.get("blocking", True) or value["result"] == "PASS"
                                for value in checks.values()))
            review = json.loads((output / "L01/review/unit_review.json").read_text())
            self.assertEqual(receipt["page_count"], len(review["page_results"]))
            self.assertEqual("PASS", review["verdict"])
            state = json.loads((output / "factory_state.json").read_text())
            self.assertEqual(["L01"], list(state["accepted_units"]))
            self.assertTrue(graph.store.events())

    def test_interrupted_review_resumes_without_overwriting_admitted_artifacts(self):
        source_bytes = (SHIPPED_L01 / "sources/source_01.html").read_bytes()
        with tempfile.TemporaryDirectory(dir=ENGINE / "outputs") as directory:
            output = Path(directory) / "resume-run"
            interrupted = CurriculumFactoryGraph(
                ENGINE, author=FakeWorker("openai"), reviewer=InterruptingReviewer("azure"),
                fetcher=lambda _url: source_bytes, capabilities=FakeCapabilities())
            with mock.patch("runtime.curriculum_factory_graph.readability_problems",
                            return_value=[]):
                first = interrupted.run(curriculum=MANIFEST, output_root=output, lab_id="L01")
            self.assertEqual("INTERRUPTED", first["terminal"])
            before = json.loads((output / "factory_state.json").read_text())
            domain_head = before["unit_heads"]["L01:domain"]
            domain_record = before["unit_artifacts"][f"L01:domain:v{domain_head}"]
            domain_hash = domain_record["sha256"]

            resumed = CurriculumFactoryGraph(
                ENGINE, author=FakeWorker("openai"), reviewer=FakeWorker("azure"),
                fetcher=lambda _url: source_bytes, capabilities=FakeCapabilities())
            with mock.patch("runtime.curriculum_factory_graph.readability_problems",
                            return_value=[]):
                second = resumed.run(curriculum=MANIFEST, output_root=output, resume=True)
            self.assertEqual("UNIT_ACCEPTED", second["terminal"], second)
            after = json.loads((output / "factory_state.json").read_text())
            self.assertEqual(domain_head, after["unit_heads"]["L01:domain"])
            self.assertEqual(domain_hash, sha256_file(output / domain_record["path"]))
            self.assertEqual("INTERRUPTED", after["terminal_history"][0]["terminal"])

    def test_workbook_assembly_rejects_inexact_accepted_coverage(self):
        with tempfile.TemporaryDirectory(dir=ENGINE / "outputs") as directory:
            output = Path(directory) / "coverage-run"
            output.mkdir()
            graph = CurriculumFactoryGraph(
                ENGINE, author=FakeWorker("openai"), reviewer=FakeWorker("azure"),
                capabilities=FakeCapabilities())
            graph.output = output
            graph.curriculum, graph.manifest_path = graph._resolve_curriculum_input(MANIFEST)
            _, graph.manifest = graph.runtime.validated_manifest(graph.curriculum)
            graph.store = FactoryStateStore(output)
            graph.store.initialize({"run_id": "coverage"}, {}, {})
            with self.assertRaisesRegex(FactoryGraphFailure, "accepted"):
                graph._assemble_workbook({}, {"front_matter_markdown": ""}, 1)


if __name__ == "__main__":
    unittest.main()
