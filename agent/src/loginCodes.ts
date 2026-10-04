import type { Api } from "./api.ts";

export type SendText = (handle: string, text: string) => Promise<void>;
const MAX_TRIES = 3; // then stop: the website's "text us login <code>" fallback still works

/** Duo-style web sign-in: text each queued code within seconds, then ack it so it's sent once. Codes live 10 minutes
 *  and the API only lists unsent, unexpired ones, so a failed send is retried on the next poll (up to MAX_TRIES).
 *  A text that went out but wasn't acked only retries the ack, never the text. */
export class LoginCodeSender {
  private running: Promise<void> | null = null;
  // ponytail: in-memory, so a restart between a send and its ack can text that code once more
  private delivered = new Set<string>();
  private failures = new Map<string, number>();
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
      const id = item.login_id;
      if (!this.delivered.has(id)) {
        const failed = this.failures.get(id) ?? 0;
        if (failed >= MAX_TRIES) continue;
        try { await this.send(item.handle, item.text); this.delivered.add(id); }
        catch {
          this.failures.set(id, failed + 1);
          this.log(failed + 1 < MAX_TRIES ? "[login codes] transport failed; will retry on the next poll." : "[login codes] transport failed; giving up on this code.");
          continue;
        }
      }
      const ack = await this.api.loginSent(id);
      if (ack.ok) this.delivered.delete(id);
      else this.log(`[login codes] sent but not acknowledged (${ack.code}); retrying the ack, not the text.`);
    }
  }
  start(everyMs = 3000) {
    console.log(`[login codes] texting web sign-in codes; polling every ${everyMs / 1000} s`);
    const timer = setInterval(() => { void this.poll().catch(() => this.log("[login codes] poll failed; will retry.")); }, everyMs);
    timer.unref(); return () => clearInterval(timer);
  }
}
