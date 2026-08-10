# Plan 21 version 2 final disposition

Status: `CHANGES_REQUIRED_SUPERSEDED_BY_V3`

All three fresh v2 reviews independently found Critical/High bypasses. Correctly
hashed but semantically unrelated or explicit-FAIL bytes could stand in for test
evidence; resume consumption was returned in memory rather than committed by a
shared compare-and-swap store; sandbox engines and DENIED logs were not rooted
in an external signed authority; ledgers did not resolve output bytes; registry
value types and effective overlays were incompletely compiled; and the v2
addendum did not replace the inherited P0/P4 state port.

Version 2 remains immutable historical evidence. Version 3 is the only active
candidate and binds all inherited behavioral files by a canonical bundle hash.
