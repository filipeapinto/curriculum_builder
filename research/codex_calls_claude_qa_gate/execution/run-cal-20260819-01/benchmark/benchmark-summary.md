# Benchmark summary

Corpus: `CORPUS-SYN-20260819-01`, 30 cases × 3 conditions × 2 repetitions = 180 receipts. Corpus SHA-256: `b1ed0ef3db843d6f01f4f5f7d61feeb8d1c0ebd2f17bcbd2bd00594943c70138`.

| Condition | All-state accuracy (60) | Live/provider state accuracy (42) | Clear-defect recall (18) | PASS-case outcomes (18) | Measured cost |
|---|---:|---:|---:|---|---:|
| Claude Sonnet 5 | 81.7% | 73.8% | 18/18 | 13 PASS / 4 FAIL / 1 QA_ERROR | $1.08083 client-estimated |
| GPT-5.6 Sol | 90.0% | 85.7% | 18/18 | 17 PASS / 1 FAIL / 0 QA_ERROR | $0 incremental; ChatGPT auth |
| GPT-5.6 Terra | 90.0% | 85.7% | 18/18 | 16 PASS / 2 FAIL / 0 QA_ERROR | $0 incremental; ChatGPT auth |

Claude used about 257,280 input/cache tokens and 60,859 output tokens. Sol used 869,140 input/cache tokens and 6,447 output tokens. Terra used 1,149,535 input/cache tokens and 6,451 output tokens. Total input-like use was about 2.28M and output use about 73.8k, below plan ceilings.

Each condition has 42 live/provider receipts and 18 controller-simulated timeout, unavailable-reviewer, and digest-mismatch receipts. All simulations returned `QA_ERROR`. Clear seeded defects comprise known-blocker, major, and grounding-conflict classes (18 receipts per condition); all were returned as FAIL. The principal live errors were overblocking PASS cases and treating six ambiguous-criterion receipts as FAIL rather than `QA_ERROR`. Claude had one live structured-output retry exhaustion, correctly surfaced as `QA_ERROR` by the controller.

Receipts: `claude-sonnet-5.receipts.jsonl` SHA-256 `8718ca37422909e8b389ec6fba5f8343d0a1c5edc9f354f83a749ca27ccf10ce`; `gpt-5.6-sol.receipts.jsonl` SHA-256 `d2d7909d02ae66cb542d2bc2cd2520966531a73aea19315ea9927591ae1242d9`; `gpt-5.6-terra.receipts.jsonl` SHA-256 `b22673261cfd4b6384b98e592cd7a0ce87ab810c5aa77c945b620b23deb53903`.

Limitations: small synthetic corpus; templated triplicates are not independent samples; no production/customer data; no dual-human adjudication; simulations test controller behavior rather than provider behavior; no confidence intervals; shared-host integrity is weak. Schema validity did not guarantee semantic consistency: some PASS verdicts contained nonempty findings. Frozen artifact/schema bytes were shared, but system prompts, caching, tokenization, and structured-output implementations differed, so cross-condition workload equivalence is unproven.
