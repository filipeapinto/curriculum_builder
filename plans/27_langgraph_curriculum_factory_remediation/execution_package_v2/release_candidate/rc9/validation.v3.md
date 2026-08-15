# RC9 deterministic validation — correction round 3

All commands ran from `/Users/filipepinto/Projects/curriculum_builder` on
2026-08-14 after adding the direct production-urllib regression required by
round 2. The complete round-2 validation remains preserved at
`validation.v2.md`; only affected surfaces were rerun here.

## Direct production opener plus full retrieval/D06B boundary

```
$ python3 -m pytest -q tests/runtime/test_plan26_egress.py::test_default_opener_validates_before_urllib_constructs_the_redirect tests/runtime/test_plan26_egress.py tests/runtime/test_plan26_deterministic_nodes.py
295 passed in 1.06s
exit_code=0
```

The new test imports and calls production `_default_opener`, lets its nested
`_Tracker.redirect_request` receive the downgrade URL, instruments the stdlib
superclass method, and proves callback denial occurs before urllib constructs or
would follow the redirect. Removing the callback or moving it after `super()`
changes the event trace and fails the test.

## N20 full verification

```
$ python3 -m pytest -q tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_model_nodes.py tests/runtime/test_plan26_egress.py tests/runtime/test_capabilities.py tests/runtime/test_curriculum_factory_graph.py tests/runtime/test_plan26_adversarial.py tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_lock_drift.py
493 passed, 1 skipped, 140 subtests passed in 27.04s
exit_code=0
```

## Execution-package v8 suite

```
$ python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py
175 passed in 11.78s
exit_code=0
```

Unaffected round-2 results remain valid and were independently recomputed in
that QA round: N30 CLI `62 passed, 27 subtests passed`; D03/D06B slice `18
passed, 234 deselected`; active plan `valid:true`; N20/N30 scans zero
violations; approved v7, modified recovery input, and graph-v8 digests matched.
