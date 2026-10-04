// Real API by default. Terminal mode never initializes Photon, even when its credentials are present.
import { createInterface } from "node:readline";
import { env } from "./env.ts";
import { httpApi } from "./api.ts";
import { Conversations } from "./conversation.ts";
import { mockApi } from "./mockApi.ts";
import { inbound } from "./replies.ts";
import { LoginCodeSender } from "./loginCodes.ts";
import { ReceiptStore, ReminderPoller } from "./reminders.ts";
import { phoneTransport } from "./transport.ts";

const api = env.useMockApi ? mockApi() : httpApi(env.apiBaseUrl, fetch, console.warn, env.agentApiKey);
const conversations = new Conversations(api);
console.log(`Hidden Rent: ${env.agentTerminal ? "terminal (no texts sent)" : "iMessage"}; API ${api.mock ? "MOCK / demo data" : env.apiBaseUrl}`);

if (env.agentTerminal) {
  console.log('Type an address, or /quit. Terminal account uses a fictional phone unless AGENT_TERMINAL_PHONE is set.');
  const lines = createInterface({ input: process.stdin, output: process.stdout, terminal: Boolean(process.stdin.isTTY) });
  // Never consume real users’ proactive queue by printing it to a terminal.
  // Explicit checkin/remind-now commands are available for isolated demo accounts.
  if (process.stdin.isTTY) lines.setPrompt("You> ");
  lines.prompt();
  for await (const line of lines) {
    if (line.trim() === "/quit") break;
    if (!process.stdin.isTTY) console.log(`You> ${line}`);
    try { for (const reply of await conversations.respond("terminal", { kind: "text", text: line }, { handle: env.terminalPhone })) console.log(`Hidden Rent> ${reply}`); }
    catch { console.error("That request failed. Please try again."); }
    lines.prompt();
  }
  lines.close();
} else {
  const { app, send } = await phoneTransport();
  const stopReminders = new ReminderPoller(api, send, new ReceiptStore(env.reminderReceipts)).start();
  const stopCodes = new LoginCodeSender(api, send).start(); // web sign-in codes, texted within seconds
  const stop = () => { stopReminders(); stopCodes(); };
  for (const signal of ["SIGINT", "SIGTERM"] as const) process.once(signal, () => { stop(); void app.stop(); });
  for await (const [space, message] of app.messages) {
    if (message.direction === "outbound") continue;
    const input = inbound(message.content);
    if (!input || !message.sender?.id) continue;
    // Spectrum sender.id is the Apple phone/email handle, not a Photon user UUID.
    try { await space.responding(async () => { for (const reply of await conversations.respond(space.id, input, { handle: message.sender!.id })) await space.send(reply); }); }
    catch { console.error("An inbound reply failed; the agent remains running."); }
  }
  stop();
}
