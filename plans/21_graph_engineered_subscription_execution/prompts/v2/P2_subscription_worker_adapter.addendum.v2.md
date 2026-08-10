# GOAL

Make P2's subscription and sandbox proofs executable under v2. Authentication
still does not prove included-only metering, and hash-shaped sandbox claims do
not prove containment.

# TEST

- Recompute actual sandbox profile and engine bytes, OS owner/mode, resolved
  roots, and escape-probe evidence before either live model launch.
- Claude passes only with subscription OAuth, included allocation, billed
  credits/overage disabled, and API fallback disabled; Codex passes only with
  ChatGPT allocation, credits disabled, and API fallback disabled.
- Current Claude logout maps to `AUTHENTICATION_MISSING`; authenticated but
  unproven metering maps to `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`.

# LOOP

Repair only the driver, profile, or evidence owner and rerun both structural
and live canaries. Never replace missing source bytes with a claimed digest.
Repeated non-transient failure routes according to the frozen v1 taxonomy.
