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
        curriculum = runtime.resolve_curriculum(args.curriculum)
        if args.preflight or args.test_static:
            print(json.dumps(runtime.static_preflight(curriculum), indent=2))
            return 0
        if args.test_live_capabilities:
            raise RuntimeFailure("LIVE-CAPABILITY-CYCLE-REQUIRED",
                                 "live route proof is intentionally separate from deterministic simulation")
        lab_id = args.lab_id
        if args.test_golden_l01:
            _, manifest = runtime.validated_manifest(curriculum)
            lab_id = manifest["labs"][0]["id"]
        if args.test_simulated_all or args.test_golden_l01:
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
        raise RuntimeFailure("LIVE-GENERATION-NOT-PREFLIGHTED",
                             "generation is refused until --test-live-capabilities succeeds")
    except RuntimeFailure as error:
        print(json.dumps({"terminal_state": error.terminal_state, "failure_id": error.failure_id,
                          "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
