# Calibration budget ledger

| Measure | Ceiling | Used | Result |
|---|---:|---:|---|
| Unique candidate sources | 24 | 24 | hard ceiling reached; no further candidate collection |
| Benchmark receipts | 180 | 180 | hard ceiling reached; no further benchmark calls |
| Live/provider calls | subset of 180 | 126 benchmark + bounded canary/challenge calls | benchmark ceiling compliant; preflight/challenge recorded separately |
| Model input/output | 6.0M / 1.5M | benchmark ≈2.28M / 73.8k | compliant |
| Paid spend | $250 total / $125 Claude | $1.08083 client-estimated Claude; $0 incremental Codex subscription | compliant; not billing-grade |
| Retries | 1 per failed call; 20 total | 1 diagnostic Claude retry; preflight path corrections did not reach inference | compliant |
| Researcher elapsed time | tracked by wall clock | <1 hour | below global 40-hour ceiling |

The source warning threshold (20) was crossed while completing the fixed six-family × four-candidate design. Optional source discovery stopped at 24. One candidate returned HTTP 404 and one was an obvious query false positive; both remain in the register. Benchmark work stopped at exactly 180 receipts. Independent challenge consumed separate research-model usage but did not alter benchmark metrics.
