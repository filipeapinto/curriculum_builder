<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole
     · owns: ## Deliverables -->

## Deliverables

```text
V7/                                          the only authorized write root
  component_lab_orchestrator_prompt.v7.md    concise runtime contract; delegates to controller and workers
  readme.md                                  derivation, authority, test categories, preflight, run/resume commands
  remediation_report.md                      every id in failures.v1.yaml → correction, proving test, result, residual risk
  canonical_curriculum.yaml + .schema.json   derived from the curriculum manifest, with source hash recorded
  automation/  prompts/  routing/  schemas/  renderers/  tests/  test_results/
```

v7 authors its own artifact schemas under `V7/schemas/`. No legacy artifact schema
is supplied and none is a contract to satisfy — decompose a lab into whatever
artifacts the controller can validate without a model, and justify that
decomposition in `remediation_report.md`.

v7's own runtime contract is expected to be short in the same way this one is: the
orchestrator prompt states the mission and the order of work, and the rules that
need room live beside it as named assets it lists. What must never be split is
ownership — one rule, one file, and a table saying which.
