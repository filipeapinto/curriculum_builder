# GOAL

Implement resume as an atomic capability transition: the controller validates
an external signed authorization and appends the continuation ID to durable
consumed state before activating the suspended node.

# TEST

- Bind authorization, continuation, command, current checkpoint, run, node,
  next attempt, and all pinned digests exactly.
- Compare-and-swap the checkpoint and consumed set atomically; replaying the
  identical continuation or command fails in the same and a cold process.
- Crash before commit activates nothing; crash after commit cannot activate a
  second time. Model workspace permissions cannot create authorization bytes.

# LOOP

Repair only transaction, persistence, or authority resolution code and replay
the complete crash matrix. Never clear or overwrite consumed IDs. Two identical
failures route to `SYSTEM_FAILURE`.
