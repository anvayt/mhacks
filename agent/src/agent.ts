// Hidden Rent iMessage agent (Photon Spectrum). Run: npm run agent
// Without Photon credentials (or with AGENT_TERMINAL=1) it chats in the terminal instead.
import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";
import { env } from "./env.ts";
import { inboundText, replyFor } from "./replies.ts";

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

console.log(`Hidden Rent agent listening on ${env.agentTerminal ? "terminal (mock)" : "iMessage"}`);

for await (const [space, message] of app.messages) {
  if (message.direction === "outbound") continue;
  const text = inboundText(message.content);
  if (text === null) continue;
  console.log(`[${message.platform}] ${message.sender?.id ?? "unknown"}: ${text}`);
  try {
    await space.responding(async () => space.send(await replyFor(text)));
  } catch (err) {
    // One bad send (e.g. "Target not allowed for this project") must not kill the loop.
    console.error(`reply to ${message.sender?.id ?? "unknown"} failed:`, err);
  }
}
