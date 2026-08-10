#!/usr/bin/env node
/**
 * Regression test for the codex_bridge.mjs stdout-truncation bug found 2026-08-10.
 *
 * The bridge used to do `process.stdout.write(json); process.exit(0)`. process.exit()
 * does not wait for a pending write on a piped stdout to flush, so output past the
 * kernel pipe buffer (64 KiB on Linux/macOS) could be cut off mid-write — the same
 * shape of failure qa_gate.py surfaced as CODEX_BRIDGE_ERROR / CODEX_TURN_FAILED on
 * large verdicts.
 *
 * This spawns the real writeResultAndExit from codex_bridge.mjs (in a child process,
 * since it calls process.exit) with a payload well past 64 KiB, and asserts the full
 * output survives intact.
 *
 * Run directly: node scripts/test_bridge_flush.mjs
 */
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(here, "_bridge_flush_fixture.mjs");
const SIZE = 200000; // comfortably past the 64 KiB pipe buffer that truncated live runs

const proc = spawnSync(process.execPath, [fixture, String(SIZE)], { encoding: "utf-8" });

let failures = 0;
function check(cond, msg) {
  if (cond) {
    console.log(`ok - ${msg}`);
  } else {
    failures++;
    console.error(`FAIL - ${msg}`);
  }
}

check(proc.status === 0, `fixture exits 0 (got ${proc.status}, stderr: ${proc.stderr.slice(0, 300)})`);
check(proc.stdout.length > 0, "fixture produced stdout");
check(
  proc.stdout.length >= SIZE,
  `stdout is at least ${SIZE} bytes, not truncated at a pipe-buffer boundary ` +
    `(got ${proc.stdout.length})`
);

let parsed = null;
try {
  parsed = JSON.parse(proc.stdout);
} catch (err) {
  check(false, `stdout is complete, parseable JSON, not cut off mid-write (${err.message})`);
}
if (parsed !== null) {
  check(true, "stdout is complete, parseable JSON, not cut off mid-write");
  check(
    typeof parsed.finalMessage === "string" && parsed.finalMessage.length === SIZE,
    `finalMessage is the full ${SIZE}-character payload, not truncated ` +
      `(got ${parsed.finalMessage ? parsed.finalMessage.length : "n/a"})`
  );
}

if (failures > 0) {
  console.error(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
