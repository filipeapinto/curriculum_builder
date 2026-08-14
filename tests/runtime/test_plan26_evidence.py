from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from runtime.langgraph_factory.artifacts import (
    AcceptedImmutable,
    ArtifactConflict,
    ArtifactStore,
    ArtifactStream,
    HeadAdvanceError,
    PathEscape,
    VersionRecord,
    bytes_digest,
    canonical_json_bytes,
    file_digest,
)
from runtime.langgraph_factory.evidence import (
    GENESIS_HASH,
    LOG_NAMES,
    EvidenceCorrupt,
    EvidenceError,
    EvidenceLog,
    EvidenceStore,
    audit_log_file,
)


def _unlock(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: -len(p.parts)):
        if path.is_symlink():
            continue
        try:
            os.chmod(path, 0o755 if path.is_dir() else 0o644)
        except OSError:
            pass


class Plan26StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "output_root"
        self.outside = self.base / "outside"
        self.outside.mkdir(parents=True)
        self.store = ArtifactStore(self.root)
        self.stream = ArtifactStream(scope="units", channel="domain", unit_id="U01")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(_unlock, self.base)

    def admit(self, data: bytes, version: int, parent: str | None, key: str) -> VersionRecord:
        return self.store.admit_version(
            self.stream, data=data, version=version, parent_hash=parent, idempotency_key=key
        )


class ArtifactAdmissionTests(Plan26StoreTestCase):
    def test_admitted_artifact_is_inside_root_and_hash_addressed(self):
        data = b'{"unit": "U01", "kind": "domain"}'
        record = self.admit(data, 1, None, "domain-v1")

        blob = self.store.resolve(record.artifact_path)
        self.assertTrue(blob.is_file())
        self.assertTrue(blob.resolve().is_relative_to(self.root.resolve()))
        self.assertEqual(record.content_hash, hashlib.sha256(data).hexdigest())
        self.assertEqual(blob.name, record.content_hash)
        self.assertEqual(file_digest(blob), record.content_hash)
        self.assertEqual(blob.read_bytes(), data)
        self.assertEqual(
            record.artifact_path, "units/U01/versions/domain/blobs/" + record.content_hash
        )
        self.assertTrue(self.store.verify_artifact(record))

        stored = json.loads(self.store.resolve(self.stream.record_path(1)).read_text())
        self.assertEqual(stored["record_hash"], record.record_hash)
        self.assertEqual(stored["record"]["parent_hash"], None)
        self.assertEqual(stored["record"]["version"], 1)

    def test_head_advances_only_to_a_declared_child_of_the_current_head(self):
        v1 = self.admit(b"v1", 1, None, "k1")
        v2 = self.admit(b"v2", 2, v1.content_hash, "k2")
        v3 = self.admit(b"v3", 3, v2.content_hash, "k3")

        self.assertIsNone(self.store.current_head(self.stream))
        with self.assertRaises(HeadAdvanceError):
            self.store.advance_head(self.stream, v2)
        self.assertIsNone(self.store.current_head(self.stream))

        self.store.advance_head(self.stream, v1)
        self.assertEqual(self.store.current_head(self.stream).record_hash, v1.record_hash)

        with self.assertRaises(HeadAdvanceError):
            self.store.advance_head(self.stream, v3)
        self.assertEqual(self.store.current_head(self.stream).version, 1)

        self.store.advance_head(self.stream, v2)
        self.assertEqual(self.store.current_head(self.stream).version, 2)

        forged = VersionRecord(
            stream_id=v3.stream_id,
            scope=v3.scope,
            unit_id=v3.unit_id,
            channel=v3.channel,
            version=3,
            parent_hash=v1.content_hash,
            content_hash=v3.content_hash,
            byte_size=v3.byte_size,
            artifact_path=v3.artifact_path,
            idempotency_key=v3.idempotency_key,
            record_hash=v3.record_hash,
        )
        with self.assertRaises(HeadAdvanceError):
            self.store.advance_head(self.stream, forged)
        self.assertEqual(self.store.current_head(self.stream).version, 2)

    def test_mutation_and_path_escape_fail_before_any_byte_is_written(self):
        v1 = self.admit(b"v1", 1, None, "k1")
        receipt_hash = bytes_digest(b"receipt")
        self.store.accept(
            self.stream, receipt_hash=receipt_hash, files={"receipt.json": b'{"ok":true}'}
        )
        accepted = self.store.resolve(
            f"units/U01/accepted/{receipt_hash}/receipt.json"
        )
        self.assertTrue(self.store.is_write_protected(accepted.relative_to(self.root).as_posix()))
        self.assertEqual(accepted.stat().st_nlink, 1)
        blob = self.store.resolve(v1.artifact_path)
        self.assertNotEqual(accepted.stat().st_ino, blob.stat().st_ino)

        with self.assertRaises(AcceptedImmutable):
            self.store.put_bytes(
                f"units/U01/accepted/{receipt_hash}/receipt.json", b"TAMPERED"
            )
        with self.assertRaises(AcceptedImmutable):
            self.store.put_bytes(
                f"units/U01/accepted/{receipt_hash}/receipt.json", b"TAMPERED", overwrite=True
            )
        with self.assertRaises(AcceptedImmutable):
            self.store.put_bytes(f"units/U01/accepted/{receipt_hash}/extra.json", b"EXTRA")
        with self.assertRaises(AcceptedImmutable):
            self.store.accept(
                self.stream, receipt_hash=receipt_hash, files={"receipt.json": b"DIFFERENT"}
            )
        self.assertEqual(accepted.read_bytes(), b'{"ok":true}')
        self.assertFalse(self.store.resolve(f"units/U01/accepted/{receipt_hash}/extra.json").exists())

        with self.assertRaises(ArtifactConflict):
            self.admit(b"MUTATED", 1, None, "k1-other")
        self.assertEqual(self.store.read_version(self.stream, 1).content_hash, v1.content_hash)

        with self.assertRaises(ArtifactConflict):
            self.admit(b"v2", 2, bytes_digest(b"not-the-parent"), "k2")
        self.assertFalse(self.store.resolve(self.stream.record_path(2)).exists())

        escape_target = self.base / "escape.txt"
        with self.assertRaises(PathEscape):
            self.store.put_bytes("../escape.txt", b"ESCAPED")
        self.assertFalse(escape_target.exists())

        absolute_target = self.outside / "absolute.txt"
        with self.assertRaises(PathEscape):
            self.store.put_bytes(str(absolute_target), b"ESCAPED")
        self.assertFalse(absolute_target.exists())

        (self.root / "evil").symlink_to(self.outside, target_is_directory=True)
        symlink_target = self.outside / "via_symlink.txt"
        with self.assertRaises(PathEscape):
            self.store.put_bytes("evil/via_symlink.txt", b"ESCAPED")
        self.assertFalse(symlink_target.exists())

        (self.root / "evil_file.json").symlink_to(self.outside / "leaf.txt")
        with self.assertRaises(PathEscape):
            self.store.put_bytes("evil_file.json", b"ESCAPED")
        self.assertFalse((self.outside / "leaf.txt").exists())

    def test_equal_replay_is_idempotent_and_conflicting_duplicate_fails(self):
        first = self.admit(b"payload", 1, None, "replay-key")
        replay = self.admit(b"payload", 1, None, "replay-key")
        self.assertEqual(first, replay)

        records_dir = self.store.resolve(f"{self.stream.versions_dir}/records")
        blobs_dir = self.store.resolve(f"{self.stream.versions_dir}/blobs")
        keys_dir = self.store.resolve(f"{self.stream.versions_dir}/keys")
        self.assertEqual(len(list(records_dir.iterdir())), 1)
        self.assertEqual(len(list(blobs_dir.iterdir())), 1)
        self.assertEqual(len(list(keys_dir.iterdir())), 1)

        with self.assertRaises(ArtifactConflict):
            self.admit(b"different payload", 1, None, "replay-key")
        with self.assertRaises(ArtifactConflict):
            self.admit(b"different payload", 1, None, "another-key")
        self.assertEqual(len(list(records_dir.iterdir())), 1)
        self.assertEqual(len(list(blobs_dir.iterdir())), 1)

        v1 = self.store.advance_head(self.stream, first)
        self.assertEqual(self.store.current_head(self.stream), v1)

    def test_crash_between_staging_and_rename_leaves_no_partial_artifact(self):
        v1 = self.admit(b"committed", 1, None, "k1")
        self.store.advance_head(self.stream, v1)
        head_before = self.store.current_head(self.stream)

        interrupted = b"interrupted write that never completed"
        staged = self.store.stage(interrupted)
        final_relative = self.stream.blob_path(bytes_digest(interrupted))
        final_path = self.store.resolve(final_relative)

        self.assertTrue(staged.is_file())
        self.assertFalse(final_path.exists())

        crashed = ArtifactStore(self.root)
        recovered = crashed.recover_staging()

        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0]["content_hash"], bytes_digest(interrupted))
        self.assertFalse(final_path.exists())
        self.assertFalse(staged.exists())
        self.assertEqual(crashed.current_head(self.stream), head_before)
        self.assertTrue(crashed.verify_artifact(v1))
        self.assertEqual(
            (self.root / recovered[0]["quarantine_path"]).read_bytes(), interrupted
        )
        self.assertEqual(crashed.recover_staging(), [])

        completed = b"completed after restart"
        completed_relative = self.stream.blob_path(bytes_digest(completed))
        committed = crashed.commit(crashed.stage(completed), completed_relative)
        self.assertTrue(committed.is_file())
        self.assertEqual(file_digest(committed), bytes_digest(completed))
        self.assertEqual(crashed.resolve(completed_relative).read_bytes(), completed)
        self.assertEqual(crashed.recover_staging(), [])


class EvidenceChainTests(Plan26StoreTestCase):
    def setUp(self):
        super().setUp()
        self.evidence = EvidenceStore(self.root)

    def activation_payload(self, index: int, phase: str) -> dict:
        return {
            "run_id": "run-1",
            "episode_id": "ep-1",
            "activation_id": f"ACT-{index:03d}",
            "node_id": "D08",
            "phase": phase,
        }

    def seed(self, count: int = 5) -> EvidenceLog:
        log = self.evidence.log("activations")
        for index in range(1, count + 1):
            log.append(self.activation_payload(index, "ACT" if index % 2 else "EXEC"))
        return log

    def test_chain_is_ordinal_linked_and_audits_clean(self):
        log = self.seed(4)
        result = log.audit()
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.record_count, 4)
        self.assertEqual(result.high_water_mark, 4)
        self.assertIsNone(result.broken_ordinal)

        records = log.records()
        self.assertEqual([r["ordinal"] for r in records], [1, 2, 3, 4])
        self.assertEqual(records[0]["prev_hash"], GENESIS_HASH)
        for previous, current in zip(records, records[1:]):
            self.assertEqual(current["prev_hash"], previous["record_hash"])
        self.assertEqual(log.high_water_mark(), 4)

        report = self.evidence.write_audit_report()
        self.assertTrue(report.is_file())
        self.assertEqual(json.loads(report.read_text())["report"]["status"], "PASS")
        self.assertEqual(self.evidence.write_audit_report(), report)
        self.assertEqual(
            self.evidence.high_water_marks(),
            {name: (4 if name == "activations" else 0) for name in LOG_NAMES},
        )

    def test_audit_detects_deletion_insertion_reorder_and_byte_change(self):
        log = self.seed(5)
        pristine = log.path.read_bytes()
        lines = pristine.decode("utf-8").splitlines()

        cases = {
            "deletion": ("\n".join(lines[:2] + lines[3:]) + "\n", 3),
            "reorder": ("\n".join(lines[:2] + [lines[3], lines[2]] + lines[4:]) + "\n", 3),
            "insertion": ("\n".join(lines[:2] + [lines[1]] + lines[2:]) + "\n", 3),
            "byte_change": (
                "\n".join(lines[:2] + [lines[2].replace("D08", "D09")] + lines[3:]) + "\n",
                3,
            ),
            "truncation": ("\n".join(lines[:4]) + "\n" + lines[4][:20], 5),
        }
        for label, (mutated, broken_ordinal) in cases.items():
            with self.subTest(attack=label):
                log.path.write_text(mutated, encoding="utf-8")
                result = log.audit()
                self.assertEqual(result.status, "FAIL")
                self.assertEqual(result.broken_ordinal, broken_ordinal)
                self.assertEqual(result.high_water_mark, broken_ordinal - 1)
                self.assertIsNotNone(result.reason)
                with self.assertRaises(EvidenceCorrupt):
                    log.append(self.activation_payload(99, "ACT"))

        log.path.write_bytes(pristine)
        self.assertEqual(log.audit().status, "PASS")
        self.assertEqual(log.append(self.activation_payload(6, "EXEC")).ordinal, 6)

        appended = audit_log_file(log.path, log_name="activations")
        self.assertEqual((appended.status, appended.high_water_mark), ("PASS", 6))

    def test_product_evidence_cannot_be_fabricated_from_checkpoint_or_fixture(self):
        for name, function in (
            ("admit_version", ArtifactStore.admit_version),
            ("accept", ArtifactStore.accept),
            ("verify_artifact", ArtifactStore.verify_artifact),
            ("append", EvidenceLog.append),
        ):
            with self.subTest(api=name):
                params = set(inspect.signature(function).parameters)
                self.assertEqual(
                    params
                    & {
                        "content_hash",
                        "record_hash",
                        "ordinal",
                        "prev_hash",
                        "checkpoint",
                        "checkpoint_tuple",
                        "state_snapshot",
                        "trust",
                        "trusted",
                        "skip_verify",
                        "fixture",
                    },
                    set(),
                )

        activations = self.evidence.log("activations")
        activations.append(self.activation_payload(1, "ACT"))
        for forged in ("ordinal", "prev_hash", "record_hash", "schema"):
            with self.subTest(forged_field=forged):
                with self.assertRaises(EvidenceError):
                    activations.append({**self.activation_payload(2, "EXEC"), forged: 1})
        self.assertEqual(activations.audit().high_water_mark, 1)

        checkpoints = self.evidence.log("checkpoints")
        checkpoints.append(
            {
                "run_id": "run-1",
                "episode_id": "ep-1",
                "checkpoint_id": "cp-1",
                "checkpoint_ns": "",
                "state_digest": bytes_digest(b"state"),
                "evidence_ordinal": 1,
                "claimed_activations": 500,
                "claimed_artifact_hash": bytes_digest(b"artifact that was never admitted"),
            }
        )
        self.assertEqual(checkpoints.audit().high_water_mark, 1)
        self.assertEqual(
            activations.audit().high_water_mark,
            1,
            "a checkpoint record must not advance the activation evidence chain",
        )

        with self.assertRaises(EvidenceError):
            checkpoints.append({"run_id": "run-1", "episode_id": "ep-1", "checkpoint_id": "cp-2"})

        phantom = VersionRecord(
            stream_id=self.stream.stream_id,
            scope="units",
            unit_id="U01",
            channel="domain",
            version=1,
            parent_hash=None,
            content_hash=bytes_digest(b"artifact that was never admitted"),
            byte_size=42,
            artifact_path=self.stream.blob_path(
                bytes_digest(b"artifact that was never admitted")
            ),
            idempotency_key="phantom",
            record_hash=bytes_digest(b"whatever"),
        )
        self.assertFalse(self.store.verify_artifact(phantom))
        self.assertIsNone(self.store.read_version(self.stream, 1))

        real = self.admit(b"real domain bytes", 1, None, "real-key")
        self.assertTrue(self.store.verify_artifact(real))
        blob = self.store.resolve(real.artifact_path)
        os.chmod(blob, 0o644)
        blob.write_bytes(b"swapped out from under the record")
        self.assertFalse(
            self.store.verify_artifact(real),
            "verification must recompute from bytes, never trust the record",
        )

        index_log = self.evidence.log("index")
        with self.assertRaises(EvidenceError):
            index_log.append({"run_id": "run-1", "episode_id": "ep-1", "key": "k"})

    def test_evidence_paths_are_contained_and_reject_unknown_logs(self):
        for name in LOG_NAMES:
            log = self.evidence.log(name)
            self.assertTrue(log.path.resolve().is_relative_to(self.root.resolve()))
            self.assertEqual(log.path.parent.name, "evidence")
        with self.assertRaises(EvidenceError):
            self.evidence.log("../../etc/passwd")
        with self.assertRaises(EvidenceError):
            EvidenceLog(self.root, "not_a_log")

    def test_canonical_serialization_rejects_non_finite_numbers(self):
        with self.assertRaises(ValueError):
            canonical_json_bytes({"value": float("nan")})
        with self.assertRaises(ValueError):
            self.evidence.log("events").append(
                {
                    "run_id": "run-1",
                    "episode_id": "ep-1",
                    "kind": "test",
                    "node_id": "D00",
                    "value": float("inf"),
                }
            )
        self.assertEqual(self.evidence.log("events").audit().record_count, 0)

    def test_audit_report_never_claims_a_log_event_that_was_never_appended(self):
        """Permanent regression guard for the historical false claim (PM-11/PM-12,
        'unit/workbook topology implemented but not registered in
        build_curriculum_factory_graph()'): a human-facing report must derive every
        material claim from the exact receipted artifact, never from an assumption
        that some code path fired. Seed only the 'activations' log (a real call
        site that did execute); 'executions' is never appended to (the historical
        defect's shape: a registration/execution path that was never actually
        wired into the production call site). The audit report must show
        executions.record_count == 0 and status PASS (an untouched log is
        honestly empty, not silently reported as having recorded anything), and
        must carry no field capable of asserting a claim beyond what
        record_count/status/high_water_mark/file_digest already, mechanically,
        say about the real bytes on disk.
        """
        self.seed(3)
        report_path = self.evidence.write_audit_report()
        report = json.loads(report_path.read_text(encoding="utf-8"))["report"]
        self.assertEqual(report["logs"]["activations"]["record_count"], 3)
        self.assertEqual(report["logs"]["activations"]["status"], "PASS")
        self.assertEqual(report["logs"]["executions"]["record_count"], 0)
        self.assertEqual(report["logs"]["executions"]["status"], "PASS")
        self.assertIsNone(report["logs"]["executions"]["file_digest"])
        self.assertEqual(
            set(report["logs"]["executions"]),
            {"log_name", "status", "record_count", "high_water_mark",
             "broken_ordinal", "reason", "file_digest"},
        )


if __name__ == "__main__":
    unittest.main()
