"""Simulate a stale DEFERRED_TOPOLOGY entry: a key whose node a downstream node
has since wired (so it now has compiled edges), left un-cleaned in the table.
Prove the patched test's filter still finds a valid victim (M07/M08) rather than
picking the now-wired stale key and failing to reproduce N20-NODE-UNDECLARED.
"""
import re
import tempfile
from pathlib import Path

from runtime.langgraph_factory import graph as G

root = Path(tempfile.mkdtemp(prefix="n20_deferred_"))
compiled = G.build_curriculum_factory_graph(engine_root=Path(".").resolve(), output_root=root)

wired_endpoints = {
    endpoint
    for source, target, _ in G.compiled_topology(compiled)["edges"]
    for endpoint in (source, target)
}

# Simulate M06 having been wired for real (as P-N20-001 describes N31 doing)
# while its DEFERRED_TOPOLOGY entry is left stale.
stale_deferred = dict(G.DEFERRED_TOPOLOGY)
wired_endpoints_simulated = wired_endpoints | {"M06_REPAIR_NAMED_UNIT_ARTIFACT"}

candidates = sorted(set(stale_deferred) - wired_endpoints_simulated)
print("DEFERRED_TOPOLOGY:", sorted(stale_deferred))
print("candidates after excluding the now-wired-but-stale M06 entry:", candidates)
assert candidates == ["M07_REVIEW_ACTUAL_WORKBOOK", "M08_REPAIR_NAMED_WORKBOOK_DEFECT"]
print("Dynamic filter correctly skips the stale wired entry and still finds a real victim: PASSED")

# And show what the OLD naive `sorted(...)[0]` would have picked -- the stale,
# now-wired key, which would NOT reproduce N20-NODE-UNDECLARED.
old_pick = sorted(stale_deferred)[0]
print(f"OLD naive picker would have chosen {old_pick!r}, which is wired in this simulation and would not raise N20-NODE-UNDECLARED")
assert old_pick == "M06_REPAIR_NAMED_UNIT_ARTIFACT"
