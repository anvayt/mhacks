import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

// Node 20.10 has no --env-file-if-exists, so load agent/.env by hand.
// Real environment variables win over the file.
const envPath = fileURLToPath(new URL("../.env", import.meta.url));
if (existsSync(envPath)) {
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*(#.*)?$/);
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

const flag = (name: string) => ["1", "true", "yes"].includes((process.env[name] ?? "").toLowerCase());

export const env = {
  projectId: process.env.PHOTON_PROJECT_ID ?? "",
  projectSecret: process.env.PHOTON_PROJECT_SECRET ?? "",
  publicUrl: process.env.PUBLIC_URL || `http://localhost:${process.env.ONBOARD_PORT || 8787}`,
  onboardPort: Number(process.env.ONBOARD_PORT || 8787),
  apiBaseUrl: process.env.API_BASE_URL || "http://localhost:8000", // PLAN.md §10: the /api the agent calls
  get hasPhoton() {
    return Boolean(this.projectId && this.projectSecret);
  },
  get useMocks() {
    return flag("USE_MOCKS") || !this.hasPhoton;
  },
  get agentTerminal() {
    return flag("AGENT_TERMINAL") || !this.hasPhoton;
  },
};
