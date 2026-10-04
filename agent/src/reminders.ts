import { chmodSync, existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import type { Api, Reminder } from "./api.ts";

export type SendReminder = (handle: string, text: string) => Promise<void>;
type Receipts = Record<string, "sending" | "delivered" | "acknowledged">;

/** No handles, addresses or texts on disk. A crash during delivery fails closed to avoid a duplicate text. */
export class ReceiptStore {
  readonly ids: Receipts;
  constructor(private path: string) {
    this.ids = existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : {};
    if (!this.ids || Array.isArray(this.ids) || typeof this.ids !== "object" || Object.values(this.ids).some((s) => !["sending", "delivered", "acknowledged"].includes(s))) throw new Error("Invalid reminder receipt file; refusing proactive sends.");
    if (existsSync(path)) chmodSync(path, 0o600);
  }
  set(id: string, state?: Receipts[string]) {
    if (state) this.ids[id] = state; else delete this.ids[id];
    mkdirSync(dirname(this.path), { recursive: true, mode: 0o700 });
    const tmp = `${this.path}.${process.pid}.tmp`;
    writeFileSync(tmp, JSON.stringify(this.ids), { mode: 0o600 });
    renameSync(tmp, this.path); chmodSync(this.path, 0o600);
  }
}

/** The API alone enforces opt-in, local quiet hours, one/day, pause and stop. One serialized 5-minute poller. */
export class ReminderPoller {
  private running: Promise<void> | null = null;
  constructor(private api: Api, private send: SendReminder, private receipts: ReceiptStore, private log = console.warn) {}
  poll(): Promise<void> {
    if (this.running) return this.running;
    this.running = this.run().finally(() => { this.running = null; });
    return this.running;
  }
  private async acknowledge(id: string) {
    const result = await this.api.reminderSent(id);
    if (result.ok) this.receipts.set(id, "acknowledged");
    else this.log(`[reminders] delivery recorded; acknowledgement will retry (${result.code})`);
  }
  private async run() {
    for (const [id, state] of Object.entries(this.receipts.ids)) if (state === "delivered") await this.acknowledge(id);
    if (Object.values(this.receipts.ids).includes("sending")) { this.log("[reminders] proactive delivery paused pending manual receipt recovery after an uncertain send."); return; }
    if (Object.values(this.receipts.ids).includes("delivered")) return; // Server caps are stale until delivery is acknowledged.
    const due = await this.api.remindersDue();
    if (!due.ok) { this.log(`[reminders] poll failed (${due.code})`); return; }
    for (const reminder of due.data) await this.deliver(reminder);
  }
  async deliver(reminder: Reminder) {
    const id = reminder.reminder_id;
    if (this.receipts.ids[id] === "delivered") { await this.acknowledge(id); return; }
    if (this.receipts.ids[id] === "acknowledged") return;
    if (Object.values(this.receipts.ids).some((state) => state === "sending" || state === "delivered")) {
      this.log("[reminders] proactive delivery paused pending receipt recovery or acknowledgement.");
      return;
    }
    this.receipts.set(id, "sending");
    try { await this.send(reminder.handle, `${this.api.mock || reminder.demo ? "[demo data]\n" : ""}${reminder.text_hint}`); }
    catch { this.receipts.set(id); this.log("[reminders] transport failed; queued for a later poll."); return; }
    this.receipts.set(id, "delivered");
    await this.acknowledge(id);
  }
  start() {
    void this.poll().catch(() => this.log("[reminders] poll failed; inspect delivery receipts."));
    const timer = setInterval(() => { void this.poll().catch(() => this.log("[reminders] poll failed; will retry.")); }, 5 * 60_000);
    timer.unref(); return () => clearInterval(timer);
  }
}
