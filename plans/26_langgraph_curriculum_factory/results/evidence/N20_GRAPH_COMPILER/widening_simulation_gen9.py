"""Simulate P-N20-001's described future: a downstream node widens the compiled
graph beyond binding_inventory() by adding extra nodes/edges (e.g. D16-D23/M06).
Prove the new subset-based assertions still hold, and that the OLD exact-equality
assertion this patch replaced would have failed under the same widening -- so the
fix is not a no-op and is verified by construction, not by reproducing a failure
that does not exist in this workspace yet.
"""
import tempfile
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from runtime.langgraph_factory import graph as G
from runtime.langgraph_factory.state import FactoryInput, FactoryOutput, FactoryState, RuntimeContext

root = Path(tempfile.mkdtemp(prefix="n20_widen_"))
compiled = G.build_curriculum_factory_graph(engine_root=Path(".").resolve(), output_root=root)
bindings = G.binding_inventory()

# Build a second, hand-widened graph the way a future N31 merge would: extra
# nodes registered and wired beyond binding_inventory()'s frozen 32.
builder = StateGraph(FactoryState, context_schema=RuntimeContext, input_schema=FactoryInput, output_schema=FactoryOutput)
G.register_skeleton(builder, bindings)

def _extra(state, context):
    return {}

builder.add_node("D16_REDUCE_UNIT_EVIDENCE", _extra)
builder.add_edge("D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE")
from runtime.langgraph_factory.persistence import open_checkpoint_saver
saver, _ = open_checkpoint_saver(root)
widened = builder.compile(checkpointer=saver, name=G.GRAPH_NAME)

drawn = set(widened.get_graph().nodes) - {START, END}
skeleton_required = set(G._skeleton_required_nodes()) | set(bindings)

# NEW assertion (what the patched tests now check): subset holds under widening.
assert skeleton_required <= drawn, "NEW subset assertion unexpectedly failed under widening"
print("NEW subset assertion (skeleton_required <= compiled_nodes): PASSED under widening")

# OLD assertion (what the frozen tests checked before this patch): exact equality
# would have broken the moment any downstream node legitimately widened the graph.
old_ok = (drawn == set(bindings))
assert not old_ok, "OLD exact-equality assertion unexpectedly still held -- widening simulation is not exercising the scenario"
print("OLD exact-equality assertion (compiled_nodes == binding_inventory()): FAILED under widening, as expected -- this is exactly why P-N20-001 was needed")
