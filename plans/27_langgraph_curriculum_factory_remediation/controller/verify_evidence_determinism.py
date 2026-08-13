#!/usr/bin/env python3
"""Verify a Run 27 evidence-determinism contract by rerunning its declared commands.

The contract format and every claim checker live in `contracts.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from contracts import cli  # noqa: E402

main = cli("evidence_determinism", __doc__ or "")

if __name__ == "__main__":
    sys.exit(main())
