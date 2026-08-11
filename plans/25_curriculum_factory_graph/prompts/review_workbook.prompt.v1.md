# Review the actual workbook

## Job

Independently review the actual assembled workbook and every rasterized page under
the frozen workbook rubric. Return workbook-owned findings only. You do not release,
repair, aggregate, or change accepted units.

## Authorized inputs

- activation envelope and validated routing decision;
- exact ordered accepted-unit coverage and immutable unit hashes;
- assembly manifest and assembled workbook bytes/hash;
- complete workbook page inventory and every page raster;
- current deterministic workbook results;
- frozen workbook rubric and randomized presentation order; and
- one structured output target.

Unit author history, unit repair history, sibling verdicts, mutable unit content,
expected release decision, and terminal state are excluded.

## Output

Write one `ReviewFindingSet`:

```text
{
  run_id, review_id, workbook_sha256, assembly_manifest_sha256,
  accepted_unit_hashes, rubric_sha256, page_denominator,
  findings: [{criterion_id, severity, artifact_owner: WORKBOOK,
              exact_location, observed_defect, required_correction,
              evidence_refs[]}],
  page_results: [{page_number, criterion_results[]}],
  verdict: PASS | REPAIR_REQUIRED
}
```

Review exact coverage as presented, front matter, TOC/navigation, pagination,
cross-unit continuity, visual/typographic consistency, accessibility, legibility,
blank/duplicate/stale pages, and assembly defects. Cover every page; do not sample.

## Bounds

- Findings must be workbook-owned. If a page exposes a suspected accepted-unit
  content defect, report it as an integrity escalation, not permission to edit the
  unit through workbook repair.
- Do not review the instructions that generated the workbook.
- Do not alter accepted unit content, hashes, or receipts.
- `PASS` is a review result, not `COMPLETE`; controller code owns release.
- Write no file except the declared review output.

Complete when every workbook page and every rubric item has a structured result.
