# GOAL

Run the fully compiled v3 effective graph. The deterministic controller verifies
external signatures, semantic receipts, artifact schemas, phase ledgers, and
durable resume transactions before selecting any edge.

# TEST

Recompute the behavioral-base digest, compile every overlay, validate all
owners/ports/resolvers/denominators, and resolve evidence only from fixed
controller paths. A PASS requires signed semantic test receipts and schema-valid
artifacts; resume requires an already committed unique SQLite consumption row.

# LOOP

Use each base prompt plus v2 and v3 addenda. Activate nothing on missing trust,
bad provenance, failed CAS, or incomplete ledger. External prerequisites pause;
factory defects and exhausted repairs route to `SYSTEM_FAILURE`. Models never
author authority, evidence, graph transitions, or acceptance.
