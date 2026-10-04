// Hidden Rent iMessage agent (Photon Spectrum). Run: npm run agent
// Without Photon credentials (or with AGENT_TERMINAL=1) it chats in the terminal instead.
import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";
import { env } from "./env.ts";
import { httpApi } from "./api.ts";
import { Conversations } from "./conversation.ts";
import { mockApi } from "./mockApi.ts";
import { inbound } from "./replies.ts";

async function start() {
  if (env.agentTerminal) return Spectrum({ providers: [terminal.config()] });
  try {
    return await Spectrum({
      projectId: env.projectId,
      projectSecret: env.projectSecret,
      providers: [imessage.config()],
    });
  } catch (err) {
    console.error(`Could not connect to Photon: ${err instanceof Error ? err.message : err}`);
    console.error("Check PHOTON_PROJECT_ID / PHOTON_PROJECT_SECRET in agent/.env (npm run doctor), or set AGENT_TERMINAL=1.");
    process.exit(1);
  }
}

const app = await start();

const conversations = new Conversations(env.useMockApi ? mockApi() : httpApi(env.apiBaseUrl));
console.log(
  `Hidden Rent agent listening on ${env.agentTerminal ? "terminal (mock)" : "iMessage"}, ` +
    `API ${env.useMockApi ? "MOCK (USE_MOCK_API=1)" : env.apiBaseUrl}`,
);

for await (const [space, message] of app.messages) {
  if (message.direction === "outbound") continue;
  const input = inbound(message.content);
  if (input === null) continue;
  console.log(`[${message.platform}] ${message.sender?.id ?? "unknown"}: ${input.kind === "text" ? input.text : `[photo ${input.mimeType}]`}`);
  try {
    await space.responding(async () => {
      for (const m of await conversations.respond(space.id, input)) await space.send(m);
    });
  } catch (err) {
    // One bad send (e.g. "Target not allowed for this project") must not kill the loop.
    console.error(`reply to ${message.sender?.id ?? "unknown"} failed:`, err);
  }
}
