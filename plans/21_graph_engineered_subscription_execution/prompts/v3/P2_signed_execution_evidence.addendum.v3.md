# GOAL

Launch model canaries only after external trust and an allowlisted executable
sandbox engine are proven. Produce controller-signed semantic test receipts;
plain files or claimed DENIED logs are not evidence.

# TEST

- Verify engine registry and receipt signatures against P0-pinned external
  keys; require executable allowlisted binary bytes and existing resolved roots.
- Each escape probe is actually executed and yields a signed deterministic
  receipt bound to command, subject, assertions, timestamps, and output hashes.
- Claude/Codex subscription-only rules from v2 remain mandatory. Current Claude
  logout or absent external trust selects `PAUSED_PREREQUISITE` without writes.

# LOOP

Repair only adapter/controller code. Never create an authority, engine registry,
or passing receipt in a model workspace. Retry transient calls only; otherwise
pause the external prerequisite or route a factory defect to `SYSTEM_FAILURE`.
