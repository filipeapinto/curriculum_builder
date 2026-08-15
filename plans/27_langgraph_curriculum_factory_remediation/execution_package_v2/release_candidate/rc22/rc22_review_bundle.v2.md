# Run 27 RC22 review artifact v2 — RC23 repaired production bytes

This is version 2 of the artifact reviewed in RC22 QA round 1. The full preserved
repair record is
`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc23/rc23_review_bundle.v1.md`;
its claims and source paths are incorporated here for round-history continuity.

RC22 round 1 correctly failed with `RC22-QA-001` and `RC22-QA-002`. The production
bytes now close both findings:

1. D02 applies a closed import policy to the entry point and every declared Python
   dependency. It rejects interpreter reflection/dynamic builtins on reference,
   dynamic/native/process/network import roots, private interpreter attributes,
   import/module registries, and exec/spawn/fork/system/popen/kill surfaces. Declared
   local Python imports must use safe identifier roots and cannot shadow forbidden
   roots. The exact reviewer probes for indirect eval, dynamic ctypes import,
   `os.fork`, and dependency-indirect-eval now stop at D02. The real Arduino verifier
   still reaches `effective_run_compiled` with its legitimate `re.compile` use.
2. The trusted runtime guard now wraps `utime`, `mkfifo`, and `mknod` on both `os`
   and `posix`, in addition to the earlier path operations. Permanent host regressions
   require identical candidate/contract digests, return codes, output digests, and
   FAIL verdicts before and after an undeclared engine path is renamed for `chdir`,
   `utime`, and `mkfifo`. D02 also refuses `os` in admitted verifier source.

Executed after the final repair bytes:

- package/focused combined: 986 passed;
- full runtime: 1363 passed, 2 skipped, 419 subtests passed;
- Plan 26 N13: freshly PASSED, no stale receipts;
- plan validation: valid N00→N90 order;
- integration ownership: 75/75 valid;
- Python compilation and whitespace validation: passed.

Authority is unchanged: graph v8
`c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`;
graph v9 `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`;
schema v6 `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`;
contract v6 `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`;
spec `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.

All carried-forward staging, immutability, replay, repair, retrieval, subscription-
only CLI, model-assignment, topology, terminal, and no-billed-API constraints remain
unchanged. RC22 round 1's FAIL remains preserved and is not approval evidence.
