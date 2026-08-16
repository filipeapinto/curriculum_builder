# Curriculum Factory repository migration report

The distribution is `curriculum-factory`, the installed package is
`curriculum_factory`, and production code now resides in `src/curriculum_factory/`.
Repository-owned policy, schemas, curricula, and disposable output stay outside the
distribution and are accessed through explicit root inputs. Package-owned prompts,
schemas, and configuration are included in the wheel.

Completed repository work:

- created the buildable src-layout packaging skeleton and console entry points;
- applied parser-based Python and structured-data codemods with fixture and idempotence tests;
- moved production modules without subsystem redesign;
- replaced package-location root inference with explicit root/resource contracts;
- enforced the `outputs/` containment boundary;
- confirmed that `outputs/` contained no children requiring migration or deletion;
- preserved existing schema identifiers as versioned contracts and added resolution checks;
- updated the live README and recorded intentional historical/schema exceptions;
- retained `tests/runtime/` as the evidence-supported domain label without creating a package-mirroring test tree.

Verification uses `tools/refactor_repo/verify_release.py`, a fresh installed wheel,
artifact inspection, installed-origin checks, CLI smoke checks, refactor tests, and the
full suite. The external GitHub repository and checkout rename remains pending explicit
authorization; no remote, integration, secret, Pages, package, or downstream checkout
was changed.
