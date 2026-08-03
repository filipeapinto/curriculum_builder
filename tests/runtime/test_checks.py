from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from runtime.checks import (CheckFailure, check_derivation, check_receipts, pdf_page_count,
                            rasterize_and_check_nonblank)


ENGINE = Path(__file__).resolve().parents[2]


class DeterministicCheckTests(unittest.TestCase):
    def test_l01_domain_verifier_accepts_declared_domain(self):
        result = subprocess.run(["python3", "curricula/arduino_kit/verify_domain.py", "--domain",
                                 "curricula/arduino_kit/fixtures/domain_unpowered_path.accept.json"],
                                cwd=ENGINE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_derivation_one_parent_and_mismatch(self):
        unit = {"domain": {"fact": {"value": "disconnected"}},
                "derived": [{"domain_pointer": "/fact/value", "rendered_value": "disconnected"}]}
        self.assertEqual(check_derivation(unit)[0]["value"], "disconnected")
        unit["derived"][0]["rendered_value"] = "powered"
        with self.assertRaises(CheckFailure):
            check_derivation(unit)

    def test_receipt_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "map.svg"
            asset.write_text("<svg/>")
            digest = hashlib.sha256(asset.read_bytes()).hexdigest()
            unit = {"visual_receipts": [{"embedded_as": "map.svg", "file_hash": digest}]}
            self.assertEqual(check_receipts(unit, root)[0]["sha256"], digest)
            unit["visual_receipts"][0]["file_hash"] = "0" * 64
            with self.assertRaises(CheckFailure):
                check_receipts(unit, root)

    @unittest.skipUnless(shutil.which("pandoc") and shutil.which("pdftoppm") and shutil.which("pdfinfo"),
                         "PDF toolchain unavailable")
    def test_shipped_pdf_page_count_and_raster_nonblank(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "unit.md"
            source.write_text("# Draft unit\n\nThis page is visibly nonblank.\n")
            pdf = root / "unit.pdf"
            result = subprocess.run(["pandoc", str(source), "--pdf-engine=typst", "-V",
                                     "mainfont=Helvetica", "-o", str(pdf)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(pdf_page_count(pdf), 1)
            pages = rasterize_and_check_nonblank(pdf, root / "pages")
            self.assertEqual(len(pages), 1)


if __name__ == "__main__":
    unittest.main()
