#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.controller import CurriculumRuntime, RuntimeFailure
from runtime.curriculum_factory_graph import CurriculumFactoryGraph
from runtime.model_worker import CodexWorker


def parser_for(runtime: CurriculumRuntime) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic curriculum runtime")
    parser.add_argument("--curriculum", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--lab-id")
    mode.add_argument("--all", action="store_true")
    parser.add_argument("--output-root")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--test-static", action="store_true")
    parser.add_argument("--test-simulated-all", action="store_true")
    parser.add_argument("--test-live-capabilities", action="store_true")
    parser.add_argument("--test-golden-l01", action="store_true")
    parser.add_argument("--model")
    for entries in runtime.limit_policy.values():
        if not isinstance(entries, dict):
            continue
        for value in entries.values():
            parser.add_argument(value["flag"], type=int, default=value["value"])
    parser.add_argument("--interrupt-after", choices=runtime.states)
    return parser


def main(argv: list[str] | None = None) -> int:
    runtime = CurriculumRuntime()
    args = parser_for(runtime).parse_args(argv)
    try:
        if args.preflight or args.test_static:
            supplied = Path(args.curriculum)
            supplied = supplied if supplied.is_absolute() else runtime.engine / supplied
            curriculum = runtime.resolve_curriculum(
                supplied.parent if supplied.resolve().is_file() else supplied)
            print(json.dumps(runtime.static_preflight(curriculum), indent=2))
            return 0
        lab_id = args.lab_id
        if args.test_golden_l01:
            curriculum = runtime.resolve_curriculum(args.curriculum)
            _, manifest = runtime.validated_manifest(curriculum)
            lab_id = manifest["labs"][0]["id"]
        if args.test_simulated_all or args.test_golden_l01:
            curriculum = runtime.resolve_curriculum(args.curriculum)
            if args.output_root:
                output = Path(args.output_root)
            else:
                default_outputs = runtime.engine / "outputs"
                default_outputs.mkdir(parents=True, exist_ok=True)
                output = Path(tempfile.mkdtemp(prefix="curriculum-runtime-sim-", dir=str(default_outputs))) / "run"
            result = runtime.simulate(curriculum, output, lab_id=lab_id,
                                      resume=args.resume, interrupt_after=args.interrupt_after)
            print(json.dumps(result, indent=2))
            return 0 if result["terminal_state"] in {"ACCEPTED", "INTERRUPTED"} else 2
        if not args.output_root:
            raise RuntimeFailure("PRECONDITION-OUTPUT-ROOT-REQUIRED",
                                 "live factory execution requires --output-root")
        if args.test_live_capabilities:
            raise RuntimeFailure(
                "PRECONDITION-CAPABILITY-MODE-REMOVED",
                "capabilities are now proved inside every fresh factory run before unit work")
        overrides = {}
        for entries in runtime.limit_policy.values():
            if not isinstance(entries, dict):
                continue
            for value in entries.values():
                flag = value["flag"].lstrip("-").replace("-", "_")
                overrides[flag] = getattr(args, flag)
        author = CodexWorker(runtime.engine, fallback_model=args.model)
        factory = CurriculumFactoryGraph(runtime.engine, author=author)
        result = factory.run(
            curriculum=args.curriculum, output_root=Path(args.output_root),
            lab_id=lab_id, all_units=args.all, resume=args.resume,
            limit_overrides=overrides)
        print(json.dumps(result, indent=2))
        return 0 if result.get("terminal") in {"UNIT_ACCEPTED", "COMPLETE", "INTERRUPTED"} else 2
    except RuntimeFailure as error:
        print(json.dumps({"terminal_state": error.terminal_state, "failure_id": error.failure_id,
                          "message": str(error)}), file=sys.stderr)
        return 2
    except Exception as error:
        print(json.dumps({"terminal": "SYSTEM_FAILURE", "failure_id": type(error).__name__,
                          "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
