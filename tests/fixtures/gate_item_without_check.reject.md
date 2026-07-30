# Negative fixture for FR-P2-GATEITEMS

A release table advertising a gate item backed by no check id in
`policy/checks.v1.yaml`. The build advertises coverage it does not have.

## Proving it

| # | Gate | Check ids | Proves |
|---|---|---|---|
| 0 | **Logger** | `LOG-*` | append-only ordering and pairing |
| 1 | **Static** | `CAL-*`, `CUR-*`, `L01-*`, `SEL-*` | the static checks |
| 2 | **Deterministic** | `LAB-*`, `REV-ISOLATED` | the deterministic checks |
| 3 | **Simulated** | `SIM-*` | fake workers drive every branch |
| 4 | **Live capability** | `ROUTE-PROVEN` | one real preflight call per route |
| 5 | **Golden L01** | `PDF-*`, `REV-COUNT-TWELVE`, `LAB-SCHEMA-VALID` | one complete lab |
