#!/usr/bin/env node
/**
 * Fixture for test_bridge_flush.mjs. Runs in its own process (writeResultAndExit
 * calls process.exit) and writes a payload of the requested size through the real
 * helper from codex_bridge.mjs, so the test exercises the actual fix rather than a
 * reimplementation of it.
 */
import { writeResultAndExit } from "./codex_bridge.mjs";

const size = parseInt(process.argv[2] || "200000", 10);
const payload = JSON.stringify({ ok: true, finalMessage: "x".repeat(size) });
writeResultAndExit(0, payload);
