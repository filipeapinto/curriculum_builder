# RC9 deterministic validation

All commands ran from `/Users/filipepinto/Projects/curriculum_builder` on 2026-08-14.

## N20 full verification

```
$ python3 -m pytest -q tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_model_nodes.py tests/runtime/test_plan26_egress.py tests/runtime/test_capabilities.py tests/runtime/test_curriculum_factory_graph.py tests/runtime/test_plan26_adversarial.py tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_lock_drift.py
489 passed, 1 skipped, 140 subtests passed in 28.31s
exit_code=0
```

## N30 CLI and production path

```
$ python3 -m pytest -q tests/runtime/test_plan26_cli.py tests/runtime/test_run_curriculum.py
62 passed, 27 subtests passed in 31.13s
exit_code=0
```

## N30 D03/D06B capability slice

```
$ python3 -m pytest -q tests/runtime/test_plan26_deterministic_nodes.py -k 'D03 or capability or D06B'
18 passed, 234 deselected in 0.13s
exit_code=0
```

## Execution-package v8 suite

```
$ python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py
175 passed in 11.49s
exit_code=0
```

## Active plan validator

```
$ python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py
{"graph_id":"plan27_langgraph_curriculum_factory_remediation","order":["N00_SPEC_APPROVAL_GATE","N10_HARNESS_PROTOCOL","N20_PROVIDER_TRANSPORT","N30_PREFLIGHT_EGRESS","N40_INTEGRATION_OWNERSHIP","N50_EVIDENCE_AUDIT_CONTROLS","N60_ADVERSARIAL_REGRESSION","N70_LIVE_UNIT_PROOF","N80_LIVE_WORKBOOK_PROOF","N90_REQUIREMENTS_FINAL_AUDIT"],"valid":true}
exit_code=0
```

## Active scoped scanners

```
N20: {"mode":"node","node_id":"N20_PROVIDER_TRANSPORT","ok":true,"scanned_files":35,"violations":[]}
N30: {"mode":"node","node_id":"N30_PREFLIGHT_EGRESS","ok":true,"scanned_files":6,"violations":[]}
```

## Proven baseline exception

The legacy parent-package N10 result validator reports a changed-file hash mismatch for
`plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py`.
The active v8 package test proves this classification against unmodified `HEAD`: the
live file and `git show HEAD:<path>` both hash to
`9ce7fe5b187620968ce289f73bbfc48a38ed1262386c25dc15116d0d8b3b2436`.
The historical N10 result recorded the older hash
`be50925aa5508310a505c438f979597402e006ef3e03746ad186b2451c045e4c`.
