// Hidden Rent iMessage agent (Photon Spectrum). Run: npm run agent
// Without Photon credentials (or with AGENT_TERMINAL=1) it chats in the terminal instead.
import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";
import { env } from "./env.ts";
import { replyFor } from "./replies.ts";

const app = env.agentTerminal
  ? await Spectrum({ providers: [terminal.config()] })
  : await Spectrum({
      projectId: env.projectId,
      projectSecret: env.projectSecret,
      providers: [imessage.config()],
    });

console.log(`Hidden Rent agent listening on ${env.agentTerminal ? "terminal (mock)" : "iMessage"}`);

for await (const [space, message] of app.messages) {
  if (message.direction === "outbound" || message.content.type !== "text") continue;
  const text = message.content.text;
  console.log(`[${message.platform}] ${message.sender?.id ?? "unknown"}: ${text}`);
  try {
    await space.responding(() => space.send(replyFor(text)));
  } catch (err) {
    // One bad send (e.g. "Target not allowed for this project") must not kill the loop.
    console.error(`reply to ${message.sender?.id ?? "unknown"} failed:`, err);
  }
}
