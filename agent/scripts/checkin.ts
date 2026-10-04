import { env } from "../src/env.ts";
import { httpApi } from "../src/api.ts";
import { mockApi } from "../src/mockApi.ts";
import { Accounts } from "../src/accounts.ts";
import { phoneTransport } from "../src/transport.ts";
import { ReceiptStore, ReminderPoller } from "../src/reminders.ts";

const demo = process.argv.includes("--demo");
const handle = process.argv.slice(2).find((x) => !x.startsWith("--"));
if (!handle) throw new Error(`Usage: npm run ${demo ? "remind-now" : "checkin"} -- <phone>`);
const api = env.useMockApi ? mockApi() : httpApi(env.apiBaseUrl, fetch, console.warn, env.agentApiKey);
const account = await new Accounts(api).resolve({ handle });
if (!account.ok) throw new Error(account.message);
let transport: Awaited<ReturnType<typeof phoneTransport>> | undefined;
const send = async (to: string, text: string) => {
  if (env.agentTerminal) { console.log(`Terminal only (no text sent): ${text}`); return; }
  transport ??= await phoneTransport(); await transport.send(to, text);
};
try {
  if (demo) {
    const r = await api.reminderDemo(account.data.user_id); if (!r.ok) throw new Error(r.message);
    await send(r.data.handle, `[demo reminder${api.mock ? "; demo data" : ""}]\n${r.data.text_hint}`);
    console.log("Demo reminder does not count toward the daily cap; /sent was not called.");
  } else {
    const check = await api.checkin(account.data.user_id); if (!check.ok) throw new Error(check.message);
    const due = await api.remindersDue(); if (!due.ok) throw new Error(due.message);
    const reminder = due.data.find((r) => r.user_id === account.data.user_id && r.kind === "checkin");
    if (!reminder) console.log("Check-in queued. No message sent: server quiet hours, preferences, pause/stop or daily cap apply.");
    else if (env.agentTerminal) { console.log(`Terminal preview only: ${reminder.text_hint}`); console.log("No text sent and /sent was not called."); }
    else await new ReminderPoller(api, send, new ReceiptStore(env.reminderReceipts)).deliver(reminder);
  }
} finally { if (transport) await transport.app.stop(); }
