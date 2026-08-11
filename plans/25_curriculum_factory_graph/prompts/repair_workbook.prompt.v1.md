# Repair a named workbook defect

## Job

Create one new version of a workbook-owned artifact for the supplied named defects.
Accepted unit packages are immutable inputs and may not be changed.

## Authorized inputs

- activation envelope and validated routing decision;
- `repair_id`, attempt, maximum, named workbook finding set, and required retest
  order;
- one current workbook-owned parent artifact/version/hash;
- ordered immutable accepted-unit IDs, paths, and hashes;
- exact allowed workbook paths or fields; and
- one child-version output target and response contract.

Unit source/content/domain/visual write access, unit author history, sibling verdicts,
acceptance records as writable data, counters, and terminal state are excluded.

## Output

Return exactly one JSON object conforming to the controller-staged
`output.schema.json`:

```text
{
  front_matter_markdown, finding_ids_addressed[]
}
```

Only the supplied workbook-owned front-matter boundary is mutable in v1. The ordered
unit inputs are controller-owned and remain byte-unchanged.

## Bounds

- Never edit, regenerate, truncate, reorder, or replace accepted unit content or PDFs.
- Never edit the parent in place or expand the allowed boundary.
- Never write checks, reviews, coverage verdicts, release state, or terminal state.
- Do not assert that the defect passed. The controller reassembles, rerenders every
  page, rereviews, and audits.
- Write only the declared child and response targets.

Complete when the scoped child and change response are written. If the requested
correction would require a unit change, leave it unresolved and make no such change.
