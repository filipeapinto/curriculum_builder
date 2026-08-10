#!/usr/bin/env node
/**
 * codex_bridge.mjs — the only thing qa_gate.py's app-server transport calls.
 *
 * Reads one JSON request on stdin, drives one turn through the resolved
 * openai-codex plugin's runAppServerTurn, and writes one JSON result on
 * stdout. No prompt text, no verdict logic, and no file writes live here —
 * everything that decides anything stays in qa_gate.py.
 *
 * Request (stdin):
 *   {
 *     "cwd": "/abs/path/to/QA/exec",
 *     "promptFile": "/abs/path/QA/rounds/round-01.request.md",
 *     "outputSchemaFile": "/abs/path/scripts/verdict.schema.json",
 *     "resumeThreadId": null,
 *     "sandbox": "read-only",
 *     "model": null,
 *     "effort": null,
 *     "persistThread": true,
 *     "threadName": "QA gate: <artifact name>",
 *     "timeoutMs": 900000
 *   }
 *
 * Result (stdout), always exactly one JSON object, exit 0 on ok:true:
 *   {
 *     "ok": true,
 *     "threadId": "...", "turnId": "...", "status": 0,
 *     "finalMessage": "<the schema-conformant verdict JSON>",
 *     "reasoningSummary": [], "commandExecutions": [], "touchedFiles": [],
 *     "error": null, "stderr": "",
 *     "plugin": { "version": "1.0.4", "libPath": "/abs/.../lib/codex.mjs" },
 *     "transport": "app-server"
 *   }
 * On failure: {"ok": false, "error": {"reason": "...", "detail": "..."}, "transport": "app-server"}, exit 1.
 */

import { readFileSync } from "node:fs";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const MIN_VERSION = [1, 0, 4];
const DEFAULT_TIMEOUT_MS = 900000;

class BridgeError extends Error {
  constructor(reason, detail) {
    super(`${reason}: ${detail}`);
    this.reason = reason;
    this.detail = detail;
  }
}

function parseVersion(v) {
  return v.split(".").map((n) => parseInt(n, 10) || 0);
}

function versionGte(a, b) {
  for (let i = 0; i < 3; i++) {
    if ((a[i] || 0) !== (b[i] || 0)) {
      return (a[i] || 0) > (b[i] || 0);
    }
  }
  return true;
}

/** Resolve the highest installed plugin version and require it meets MIN_VERSION. */
function resolvePluginLib() {
  const cacheRoot = path.join(os.homedir(), ".claude", "plugins", "cache", "openai-codex", "codex");
  let entries;
  try {
    entries = fs.readdirSync(cacheRoot, { withFileTypes: true });
  } catch (err) {
    throw new BridgeError("CODEX_PLUGIN_NOT_FOUND", `plugin cache not found at ${cacheRoot}: ${err.message}`);
  }
  const versions = entries
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .filter((name) => /^\d+\.\d+\.\d+$/.test(name))
    .sort((a, b) => (versionGte(parseVersion(a), parseVersion(b)) ? -1 : 1));
  if (versions.length === 0) {
    throw new BridgeError("CODEX_PLUGIN_NOT_FOUND", `no versioned plugin directories under ${cacheRoot}`);
  }
  const highest = versions[0];
  if (!versionGte(parseVersion(highest), MIN_VERSION)) {
    throw new BridgeError(
      "CODEX_PLUGIN_INCOMPATIBLE",
      `highest installed plugin version is ${highest}, need >= ${MIN_VERSION.join(".")}`
    );
  }
  const libPath = path.join(cacheRoot, highest, "scripts", "lib", "codex.mjs");
  if (!fs.existsSync(libPath)) {
    throw new BridgeError(
      "CODEX_PLUGIN_NOT_FOUND",
      `resolved plugin ${highest} has no scripts/lib/codex.mjs at ${libPath}`
    );
  }
  return { version: highest, libPath };
}

function readStdin() {
  return readFileSync(0, "utf-8");
}

async function main() {
  let request;
  try {
    request = JSON.parse(readStdin());
  } catch (err) {
    throw new BridgeError("BAD_REQUEST", `stdin was not valid JSON: ${err.message}`);
  }
  for (const field of ["cwd", "promptFile"]) {
    if (!request[field]) {
      throw new BridgeError("BAD_REQUEST", `request is missing required field '${field}'`);
    }
  }

  const { version, libPath } = resolvePluginLib();
  const mod = await import(pathToFileURL(libPath).href);
  const { runAppServerTurn, interruptAppServerTurn, readOutputSchema } = mod;
  if (typeof runAppServerTurn !== "function" || typeof interruptAppServerTurn !== "function") {
    throw new BridgeError(
      "CODEX_PLUGIN_INCOMPATIBLE",
      `resolved plugin ${version} at ${libPath} does not export the expected functions`
    );
  }

  let prompt;
  try {
    prompt = readFileSync(request.promptFile, "utf-8");
  } catch (err) {
    throw new BridgeError("BAD_REQUEST", `could not read promptFile ${request.promptFile}: ${err.message}`);
  }

  let outputSchema = null;
  if (request.outputSchemaFile) {
    try {
      outputSchema =
        typeof readOutputSchema === "function"
          ? readOutputSchema(request.outputSchemaFile)
          : JSON.parse(readFileSync(request.outputSchemaFile, "utf-8"));
    } catch (err) {
      throw new BridgeError(
        "BAD_REQUEST",
        `could not read outputSchemaFile ${request.outputSchemaFile}: ${err.message}`
      );
    }
  }

  let lastKnownThreadId = request.resumeThreadId || null;
  const onProgress = (update) => {
    const info = typeof update === "string" ? {} : update || {};
    if (info.threadId) {
      lastKnownThreadId = info.threadId;
    }
  };

  const timeoutMs = request.timeoutMs || DEFAULT_TIMEOUT_MS;
  let timedOut = false;
  let timer = null;

  const turnPromise = runAppServerTurn(request.cwd, {
    prompt,
    resumeThreadId: request.resumeThreadId || null,
    outputSchema,
    sandbox: request.sandbox || "read-only",
    model: request.model || null,
    effort: request.effort || null,
    persistThread: request.persistThread !== false,
    threadName: request.threadName || null,
    onProgress,
  });

  const timeoutPromise = new Promise((_, reject) => {
    timer = setTimeout(() => {
      timedOut = true;
      reject(new Error("timeout"));
    }, timeoutMs);
    timer.unref?.();
  });

  let result;
  try {
    result = await Promise.race([turnPromise, timeoutPromise]);
    clearTimeout(timer);
  } catch (err) {
    clearTimeout(timer);
    if (!timedOut) {
      throw new BridgeError("CODEX_TURN_FAILED", err instanceof Error ? err.message : String(err));
    }
    // Turn didn't finish in time. turnId is only known once the turn completes,
    // so an interrupt this early can only ever target the thread; a bare
    // threadId is enough for interruptAppServerTurn to report why it declined,
    // never a silent no-op.
    const interrupt = await interruptAppServerTurn(request.cwd, {
      threadId: lastKnownThreadId,
      turnId: null,
    }).catch((interruptErr) => ({
      attempted: true,
      interrupted: false,
      detail: interruptErr instanceof Error ? interruptErr.message : String(interruptErr),
    }));
    throw new BridgeError(
      "CODEX_TIMEOUT",
      `no response within ${timeoutMs}ms; interrupt ${interrupt.interrupted ? "sent" : "not confirmed"} ` +
        `(${interrupt.detail || "no detail"})`
    );
  }

  return {
    ok: true,
    threadId: result.threadId,
    turnId: result.turnId,
    status: result.status,
    finalMessage: result.finalMessage,
    reasoningSummary: result.reasoningSummary || [],
    commandExecutions: result.commandExecutions || [],
    touchedFiles: result.touchedFiles || [],
    error: result.error ?? null,
    stderr: result.stderr || "",
    plugin: { version, libPath },
    transport: "app-server",
  };
}

/**
 * process.exit() does not wait for a pending stdout write to flush. On a piped
 * stdout, write() past the kernel pipe buffer (64 KiB on Linux/macOS) can still be
 * in flight when exit() tears the process down, silently truncating the JSON the
 * parent is about to parse. Exiting from write()'s own callback, which only fires
 * once the data is actually flushed, is what makes this safe at any payload size.
 */
function writeResultAndExit(code, payload) {
  process.exitCode = code;
  process.stdout.write(payload, () => process.exit(code));
}

// Guarded so test_bridge_flush.mjs can import writeResultAndExit directly without
// also triggering main() (stdin read + plugin resolution), which only makes sense
// when this file is actually run as the CLI qa_gate.py invokes.
const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  main()
    .then((result) => {
      writeResultAndExit(0, JSON.stringify(result));
    })
    .catch((err) => {
      const reason = err instanceof BridgeError ? err.reason : "CODEX_BRIDGE_ERROR";
      const detail = err instanceof BridgeError ? err.detail : err?.stack || String(err);
      writeResultAndExit(1, JSON.stringify({ ok: false, error: { reason, detail }, transport: "app-server" }));
    });
}

export { writeResultAndExit };
