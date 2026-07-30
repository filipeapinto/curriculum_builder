# Negative fixture for FR-P0-NOSTALE

This file exists to be flagged. It carries the literal `assets/calibration.v1.yaml`,
a path this refactor retires, and the stale-path detector must report
`stale-path:assets/` **when pointed at this file**.

The same detector pointed at the production scan root set must not see this file at
all — that is self-test (f), and it is why harness rule 7 excludes `tests/**` entire.
