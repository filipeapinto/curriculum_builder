# QA post-mortem — QA_PASSED

**Classification:** ARTIFACT_DEFICIENT  
**Confidence:** high  
**Rounds:** 4 of 5  
**Terminal reason:** CONVERGED — Codex passed the artifact at round 4

## Reasoning

This did converge—at round 4. The first three failures were caused by real, reproducible enforcement gaps in the artifact, each of which allowed runtime behavior forbidden by PKGV2-T01/T05/T06 while validation still succeeded. The criteria explicitly required wrong binding to be “structurally impossible” and T10 to provide automated proof, so testing duplicate and argparse-supported argument forms remained within scope rather than introducing a new standard. The successive findings reflect incomplete fixes: round 1 exposed missing semantic checks, round 2 exposed duplicate-option precedence, and round 3 showed that the duplicate fix did not cover equals-form arguments. Round 4 passed after parsing and validation were aligned with argparse semantics. There is no evidence of an integrity breach, contradictory specification, or unresolved process dispute.

## Evidence

- Round 1 identified two reproducible proof gaps: “changing N20’s scan argument to `N30_PREFLIGHT_EGRESS` produced `wrong_node_accepted True`, and changing N40’s result write to the parent `results/` root produced `parent_result_path_accepted True`.” The reviewer simultaneously stated that “T00–T09” were confirmed, isolating the deficiency to the required T10 automated proof.
- Round 2 confirms the round-1 defects were actually repaired: “simple wrong-node and wrong-graph substitutions and parent-root result/evidence writes are now rejected.” It then demonstrates a remaining artifact gap: “argparse uses the last occurrence,” while the validator “inspect[s] only the first occurrence,” producing `duplicate_node_accepted True` and `duplicate_graph_accepted True`.
- Round 3 shows that the round-2 repair was incomplete rather than ignored: the fix “correctly rejects omitted flags, simple value substitutions, and separated-token duplicate flags,” but checks such as `command.count("--node")` did not recognize argparse-supported `--node=...` and `--graph=...` forms. Direct mutations again produced `equals_duplicate_node_accepted True` and `equals_duplicate_graph_accepted True`.
- The duplicate-form findings were grounded in the stated criteria. PKGV2-T01 required the defect class to be “structurally impossible,” while round 3 explained that argparse would apply the final equals-form override and make “N20 scan the parent graph or N30’s write set” despite the validator passing.
- Round 4 establishes resolution and convergence: “the validator now parses scanner arguments using argparse-compatible semantics and rejects omitted, wrong, separated-duplicate, equals-duplicate, and abbreviated duplicate node/graph bindings.” The reviewer therefore returned `PASS` with no findings.
- The review record remained consistent throughout. Every honesty audit reports `prior_rounds_consistent:true`; round 4 says, “The round history matches all three verdicts I issued.” Nothing supports an integrity breach.
- The repeated prompt observation did not cause scope drift or block passage. Rounds 2–4 consistently noted that the prompts cite the deprecated package-local graph, but treated it as non-blocking because “their ownership and read-only claims match the active graph” and it “does not defeat a numbered criterion.”

## Recommendation

Accept the round-4 pass. Preserve regression tests covering wrong values and all argparse-equivalent override forms—separated duplicates, equals-form duplicates, and abbreviations—and centralize validation through the same argument parser used at runtime. Also update the stale prompt command examples as non-blocking cleanup, but do not reopen the QA gate solely for that observation.

---

Analysed by an independent Codex session (`019ffc86-0d1d-7632-bab2-8447b6a1f8bf`), separate from the review session (`019ffc3b-6379-7ef3-839d-759ed5c7fc9c`).