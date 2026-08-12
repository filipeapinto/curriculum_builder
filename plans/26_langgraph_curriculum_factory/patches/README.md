# Immutable Plan 26 prompt patches

Every `*.patch.v1.yaml` file in this directory is an append-only prompt or
context overlay bound to the SHA-256 digest of the active v3 graph manifest.
The controller composes applicable overlays when a node attempt starts and
records the complete patch chain in the attempt and receipt provenance.

Never edit or delete a patch after it has been used. Create a new `revoke`
record to roll one back. Use the controller's `create-patch` and `revoke-patch`
commands so creation fails if a filename already exists.

Prompt patches take effect only at node boundaries. They never alter a running
Claude call or rewrite a base prompt.
