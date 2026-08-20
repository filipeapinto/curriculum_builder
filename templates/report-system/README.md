# Report system

This directory is the canonical source for the shared look and feel of HTML reports.

## Contract

- Edit design tokens in `styles/report-tokens.v1.css`.
- Edit shared layout and component rules in `styles/report-system.v1.css`.
- Put reusable HTML fragments in `components/`.
- Put uncompiled report templates in `sources/`.
- Generate standalone HTML with `build/assemble_report.py`.
- Never edit an issued report merely to pick up a design-system change. Create its next version.

Generated reports inline the versioned CSS and expanded components. They therefore remain portable,
printable, and stable when copied or archived.

## Build

```sh
python3 templates/report-system/build/assemble_report.py \
  templates/report-system/sources/issue-report.template.v10.source.html \
  templates/issue-report.template.v10.html
```

Source templates use `{{> component-name}}` for component inclusion. Ordinary report placeholders,
such as `{{TITLE}}`, are preserved for the report author or rendering system.
