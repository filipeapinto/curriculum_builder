# The contract's asset set

The live asset set, declared here and compared against `EXPECTED` in
`tests/meta_prompt_source.py` in both directions.

Why it is a separate file at all: a shape declared in one place is self-certifying.
Whoever deletes an asset and its row in the prompt's own table can delete its line in
`EXPECTED` in the same edit, and every check stays green. Two declarations that must
agree make that a three-file edit, which is visible.

This is a weaker authority than a document maintained for another purpose — it sits
beside the module it checks, and one person can still edit both. It is the strongest
version that costs nothing outside `tests/`. If the asset set ever grows past the three
rows below, the declaration is worth moving somewhere with an independent reason to be
correct.

`section` assets compose into the contract; `companion` assets are inputs a worker
reads. `curriculum.prompt.v1.md` states its own rules, so there are no `section` rows —
a `section` row appearing here is a contract that has been split again.

| Asset | Kind |
|---|---|
| `meta_prompt/assets/unit_prose.v1.md` | companion |
| `meta_prompt/assets/pedagogy.v1.md` | companion |
| `meta_prompt/assets/model_selector_prompt.v1.md` | companion |
