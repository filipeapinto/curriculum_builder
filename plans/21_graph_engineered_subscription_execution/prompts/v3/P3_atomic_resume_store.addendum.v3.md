# GOAL

Persist continuation activation in the controller SQLite store using one
`BEGIN IMMEDIATE` compare-and-swap transaction before node activation.

# TEST

- Transaction checks expected checkpoint generation and inserts unique
  continuation, command, and authorization IDs, then increments generation.
- Two independent connections starting from the same snapshot yield exactly
  one commit and one rejection; cold restart preserves rejection.
- Crash before commit activates nothing; crash after commit sees consumed state
  and cannot activate twice. An in-memory returned set is insufficient.

# LOOP

Repair only store/transaction/activation ordering and rerun concurrent and cold
process crash tests. Never clear consumption rows. Exhaustion is
`SYSTEM_FAILURE`.
