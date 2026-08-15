# Run 27 N90 independent final-audit criteria

The artifact passes only if all observable conditions below hold. A preference or possible future enhancement is not a blocker.

1. It starts authority at the current user-approved corrected specification SHA-256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`, then covers retained Plans 20–22/product requirements, implementation, tests, and product evidence without treating historical files as current authority.
2. It accounts for every PM-01 through PM-24 identifier, including identifiers consolidated by postmortem v2, and every CA-01 through CA-12; no item disappears and activation-only unavailability remains open rather than misreported resolved.
3. Its N00–N80 outcomes and result SHA-256 values equal the grounded V9 results. N00–N60 must be PASSED; N70 and N80 must be NOT_AVAILABLE. It must not claim UNIT_ACCEPTED, COMPLETE, or live product bytes.
4. It identifies the implemented provider map as Claude/Anthropic for M01–M04/M06/M08 and Codex/OpenAI for M05/M07, subscription CLI only, with no fallback/API-key/direct-model-HTTP activation.
5. It reports the witnessed independent RC29 qa-gate result only if state is QA_PASSED, reason CONVERGED, chain_valid true, problems empty, and the stated session/chain identifiers match grounded verification/session files.
6. It reports the final regression denominator accurately: runtime 1370 passed, 2 explicitly classified unrelated skips, 419 subtests; Run 27 package 83 passed; whole-tree scan 67 files and zero violations; ownership 75/75; evidence determinism 2/2; requirements lineage 8/8.
7. It separates exactly three conclusions: specification authority, implementation conformance, and product activation. Implementation may pass while activation remains unavailable.
8. It recommends exactly `REMEDIATION_VERIFIED_NOT_ACTIVATED`. `ACTIVATED` would be false because N70/N80 are not PASSED; `BLOCKED` would be false absent an implementation/integrity/evidence/convergence defect.
9. It does not waive the Claude availability blocker, recommend credentials/provider substitution, or use Plan 26/v8 history as provider-correctness or activation proof.
