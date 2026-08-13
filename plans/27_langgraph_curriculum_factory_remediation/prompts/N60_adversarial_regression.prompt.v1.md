# GOAL

Run the complete final-code verification and adversarial campaign before any
live curriculum transmission. This node may add only
`tests/runtime/test_plan27_adversarial.py` and
`plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py`.
It cannot edit controller, runtime, policy, earlier tests, or contracts;
production and owner-specific test defects route back to their owning node and
invalidate all descendants.

# TEST

1. Freeze the final graph/spec/code/test digests and enumerate the complete test
   denominator before running it.
2. Run the full runtime suite with no deleted, skipped, xfailed, filtered, or
   weakened test used to obtain success.
3. Include adversarial cases for unauthorized provider terms/routes, API-key
   activation, hidden fallback, same-family final judgment, false-ready
   preflight, staged-input escape, output-schema escape, identity overclaim,
   unreachable production topology, incomplete denominators, descendant receipt
   reuse, Markdown status spoofing, interrupted merge, nondeterministic evidence,
   false result claims, resume drift, and false completion.
4. Re-run focused suites for transport/model jobs, preflight/egress, production
   topology, unit/workbook repair, CLI, controller/receipts, and evidence.
5. Separate pre-existing unrelated failures only with a frozen pre-change
   baseline proving the same failure. Never label a new collection failure
   pre-existing without evidence.
6. Run the complete denominator a second time and prove required stable evidence
   does not drift.
7. Emit counts, exact commands/exits, skipped/failed census, evidence hashes, and
   a schema-valid result.

# LOOP

Route a controller/protocol finding to N10 and a production finding to N20,
N30, N40, or N50 by ownership; invalidate that node and every descendant,
repair there, and rerun forward. Do not patch upstream files under N60. N60 may
repair only its two newly owned adversarial files. Three identical unresolved
failures return `BLOCKED`.
