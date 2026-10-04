import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/** Explicit environment wins; nonempty agent file values override root file values. */
export function loadEnvFiles(paths: string[], target: NodeJS.ProcessEnv = process.env) {
  for (const path of paths) {
    if (!existsSync(path)) continue;
    for (const line of readFileSync(path, "utf8").split("\n")) {
      const m = line.match(/^\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (!m || target[m[1]] !== undefined) continue;
      const raw = m[2];
      const value = /^["']/.test(raw) ? raw.slice(1, raw.lastIndexOf(raw[0])) : raw.replace(/\s+#.*$/, "");
      if (value) target[m[1]] = value; // Blank example-file keys do not mask the root secret.
    }
  }
}
loadEnvFiles(["../.env", "../../.env"].map((relative) => fileURLToPath(new URL(relative, import.meta.url))));

const flag = (name: string) => ["1", "true", "yes"].includes((process.env[name] ?? "").toLowerCase());

export const env = {
  projectId: process.env.PHOTON_PROJECT_ID ?? "",
  projectSecret: process.env.PHOTON_PROJECT_SECRET ?? "",
  publicUrl: process.env.PUBLIC_URL || `http://localhost:${process.env.ONBOARD_PORT || 8787}`,
  onboardPort: Number(process.env.ONBOARD_PORT || 8787),
  agentApiKey: process.env.AGENT_API_KEY ?? "",
  terminalPhone: process.env.AGENT_TERMINAL_PHONE || "+12025550164",
  reminderReceipts: process.env.REMINDER_RECEIPTS || fileURLToPath(new URL("../../data/agent-reminder-receipts.json", import.meta.url)),
  apiBaseUrl: process.env.API_BASE_URL || "http://localhost:8000", // PLAN.md §10: the /api the agent calls
  get hasPhoton() {
    return Boolean(this.projectId && this.projectSecret);
  },
  get useMocks() {
    return flag("USE_MOCKS") || !this.hasPhoton;
  },
  get useMockApi() {
    return flag("USE_MOCK_API");
  },
  get agentTerminal() {
    return flag("AGENT_TERMINAL") || !this.hasPhoton;
  },
};
