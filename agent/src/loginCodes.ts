import type { Api } from "./api.ts";

export type SendText = (handle: string, text: string) => Promise<void>;

/** Duo-style web sign-in: text each queued code within seconds, then ack it so it's sent once. Codes live 10 minutes
 *  and the API only lists unsent, unexpired ones, so a failed send is simply retried on the next poll. */
export class LoginCodeSender {
  private running: Promise<void> | null = null;
  constructor(private api: Api, private send: SendText, private log = console.warn) {}
  poll(): Promise<void> {
    if (this.running) return this.running;
    this.running = this.run().finally(() => { this.running = null; });
    return this.running;
  }
  private async run() {
    const due = await this.api.loginOutbox();
    if (!due.ok) { if (due.code !== "not_served") this.log(`[login codes] poll failed (${due.code})`); return; }
    for (const item of due.data) {
      try { await this.send(item.handle, item.text); }
      catch { this.log("[login codes] transport failed; will retry on the next poll."); continue; }
      const ack = await this.api.loginSent(item.login_id);
      if (!ack.ok) this.log(`[login codes] sent but not acknowledged (${ack.code}); it may be texted again.`);
    }
  }
  start(everyMs = 3000) {
    const timer = setInterval(() => { void this.poll().catch(() => this.log("[login codes] poll failed; will retry.")); }, everyMs);
    timer.unref(); return () => clearInterval(timer);
  }
}
