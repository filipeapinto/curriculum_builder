# Create a required unit visual

## Job

Create one assigned non-authoritative visual artifact for one manifest-declared
visual role. The controller invokes this job once per eligible visual brief. Exact
technical maps, wiring, values, geometry, polarity, and safety authority remain on
the deterministic-render branch and are never inferred here.

## Authorized inputs

- activation envelope and validated routing decision;
- one `VisualBrief` containing `visual_id`, role, purpose, placement, dimensions,
  format, accessibility constraints, and allowed source kind;
- only the exact accepted domain facts and pointers the brief must represent;
- only the admitted source assets and source facts assigned to this brief;
- required provenance fields; and
- one preallocated artifact target plus one provenance-response target.

Other unit prose, other visual briefs, author/reviewer history, check results, and
acceptance state are excluded.

## Output

Return exactly one JSON object conforming to the controller-staged
`output.schema.json`:

```text
{
  filename, svg, role, supports_section, alt_text
}
```

The visual must be relevant, legible at declared print size, free of decorative or
unsupported claims, accessible without color alone, and consistent with every parent
fact. Any text embedded in the asset must come from the brief exactly.

## Bounds

- Do not create an artifact for a different visual role.
- Do not invent, repair, or reinterpret technical facts.
- Do not substitute a generated picture for a required verified photograph or
  deterministic technical map.
- Do not compute or assert the final artifact hash or receipt validity; controller
  code does so from bytes.
- Do not declare the role complete, the visual accepted, or the unit successful.
- The `svg` field is the complete SVG payload. Do not write files; controller code
  writes the preallocated target, hashes its bytes, and creates provenance.

Complete when the one schema-valid response for the assigned visual is returned.
