#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [cliRoot, modelId] = process.argv.slice(2);
if (!cliRoot || !modelId) {
  throw new Error("usage: resolve_gemini_settings.mjs <gemini-cli-package-root> <model-id>");
}

const settingsModule = await import(pathToFileURL(path.join(cliRoot, "dist/src/config/settings.js")));
const coreRoot = path.join(cliRoot, "node_modules/@google/gemini-cli-core/dist");
const serviceModule = await import(pathToFileURL(path.join(coreRoot, "src/services/modelConfigService.js")));
const loaded = settingsModule.loadSettings(process.cwd());
const service = new serviceModule.ModelConfigService(loaded.merged.modelConfigs);
const resolved = service.getResolvedConfig({ model: modelId, overrideScope: "core" });

function fileAudit(layer) {
  const candidate = loaded[layer];
  if (!candidate) return null;
  const exists = fs.existsSync(candidate.path);
  return {
    path: candidate.path,
    exists,
    sha256: exists ? crypto.createHash("sha256").update(fs.readFileSync(candidate.path)).digest("hex") : null,
  };
}

process.stdout.write(JSON.stringify({
  model_id: modelId,
  resolved_model_config: resolved,
  effective_tools: loaded.merged.tools,
  effective_mcp: loaded.merged.mcp,
  effective_mcp_server_count: Object.keys(loaded.merged.mcpServers || {}).length,
  layers: {
    user: fileAudit("user"),
    workspace: fileAudit("workspace"),
    system: fileAudit("system"),
    systemDefaults: fileAudit("systemDefaults"),
  },
}, null, 2) + "\n");
