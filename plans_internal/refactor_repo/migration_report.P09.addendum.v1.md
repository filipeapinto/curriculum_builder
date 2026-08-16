# Test-tree decision addendum

`tests/runtime/` is retained. Its 34 files exercise runtime behavior across unit,
integration, contract, and adversarial layers and share fixtures/imports. The directory
is nested under the `tests` package, does not create `tests/curriculum_factory`, and
cannot replace the installed top-level `curriculum_factory` package. The Plan 26
workflow and gate script therefore require no path rewrite. See
`test_tree_decision.v1.yaml` for the measured classification and removal condition.
