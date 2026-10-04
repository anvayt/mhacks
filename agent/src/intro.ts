// Photon's shared pool gives each user their own Hidden Rent number, so we text first: the onboarding page
// (a separate process) POSTs {phone, session, line} to the agent process, the only one holding the Spectrum connection.
// The listener binds 127.0.0.1 only, so nothing new is reachable from the internet.
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { contact, type ContentBuilder } from "spectrum-ts";
import { nativeContactCard } from "spectrum-ts/providers/imessage";
import { accountHandle } from "./accounts.ts";
import type { Api } from "./api.ts";
import { validSession } from "./handoff.ts";
import type { SendText } from "./loginCodes.ts";
import { normalizePhone } from "./photon.ts";

const THROTTLE_MS = 10 * 60_000; // at most one intro per phone per 10 minutes
const HELLO = "Hi, I'm Hidden Rent 👋 This is your Hidden Rent number. Save it as a contact.";
/** No links: a link in a first text trips Apple's junk filter. */
export const INTRO = `${HELLO} Text me any Ann Arbor address or a Zillow/Redfin/Apartments.com link and I'll estimate what heating and cooling will cost.`;
export const resumeIntro = (address?: string) =>
  `${HELLO} I have your report${address ? ` for ${address}` : ""} from the website. Reply anything to pick up where you left off.`;

const PHOTO = new URL("../assets/hidden-rent.png", import.meta.url);

/** A tap-to-save contact for this user's own Hidden Rent line (each user gets a different one). No URL in it. */
export const hiddenRentCard = (line: string) =>
  contact({
    name: { formatted: "Hidden Rent", first: "Hidden", last: "Rent" },
    phones: [{ value: line, type: "mobile" }],
    org: { name: "Hidden Rent" },
    note: "Heating & cooling cost for any Ann Arbor rental. Text an address.",
    photo: { mimeType: "image/png", read: () => readFile(PHOTO) },
  });

/** Our card with their line's number; else the line's own iMessage card. Returns which one went out. */
export async function shareCard(space: { send(content: ContentBuilder): Promise<unknown> }, line?: string | null): Promise<"contact" | "native"> {
  if (line) {
    try { await space.send(hiddenRentCard(line)); return "contact"; }
    catch { console.warn("[intro] contact card failed; sharing the line's own card instead"); }
  }
  await space.send(nativeContactCard());
  return "native";
}

export type SendCard = (handle: string, line?: string | null) => Promise<unknown>;

export class Intros {
  private sentAt = new Map<string, number>();
  // ponytail: in-memory, so a restart forgets pending resumes; the "Open Messages" opener still carries "(ref id)"
  private resumes = new Map<string, string>();
  constructor(private send: SendText, private api: Pick<Api, "session">, private card: SendCard = async () => {}, private now = Date.now) {}

  /** Text the intro, then the contact card, unless this phone got one in the last 10 minutes.
   *  Remembers the session for the next inbound text. `line` is the user's assigned Hidden Rent number. */
  async intro(phone: string, session: string | null, line?: string | null): Promise<"sent" | "throttled"> {
    const handle = accountHandle(phone);
    if (session) this.resumes.set(handle, session);
    const now = this.now();
    for (const [h, t] of this.sentAt) if (now - t >= THROTTLE_MS) this.sentAt.delete(h);
    if (this.sentAt.has(handle)) return "throttled";
    this.sentAt.set(handle, now); // set before sending: a failed or slow send still counts, so we never double-text
    let text = INTRO;
    if (session) {
      const r = await this.api.session(session).catch(() => null);
      text = resumeIntro(r?.ok ? r.data.building.address : undefined);
    }
    await this.send(handle, text);
    // Card after the text, in the background: the page isn't kept waiting on a photo upload, and it never fails the intro.
    void this.card(handle, line).catch(() => console.warn(`[intro] contact card to ***${handle.slice(-4)} failed; the text went out`));
    return "sent";
  }

  /** The website session this handle should resume (once), or null. */
  take(handle: string): string | null {
    const key = accountHandle(handle);
    const session = this.resumes.get(key) ?? null;
    this.resumes.delete(key);
    return session;
  }

  /** POST /intro {phone, session?, line?} on 127.0.0.1:port. 200 sent/throttled, 400 bad input, 502 send failed. */
  serve(port: number) {
    const server = createServer(async (req, res) => {
      const reply = (status: number, body: object) => res.writeHead(status, { "Content-Type": "application/json" }).end(JSON.stringify(body));
      let phone: string | null = null;
      try { // never let a bad request or a failed send take the agent down
        if (req.method !== "POST" || req.url !== "/intro") return reply(404, { error: "not_found" });
        let raw = "";
        for await (const chunk of req) { raw += chunk; if (raw.length > 2_000) return reply(413, { error: "too_large" }); }
        const body = JSON.parse(raw) as { phone?: unknown; session?: unknown; line?: unknown };
        phone = typeof body.phone === "string" ? normalizePhone(body.phone) : null;
        if (!phone) return reply(400, { error: "bad_phone" });
        const session = validSession(typeof body.session === "string" ? body.session : null);
        const line = typeof body.line === "string" ? normalizePhone(body.line) : null;
        reply(200, { status: await this.intro(phone, session, line) });
      } catch {
        console.warn(`[intro] ${phone ? `send to ***${phone.slice(-4)} failed` : "bad request"}`);
        if (!res.headersSent) reply(phone ? 502 : 400, { error: phone ? "send_failed" : "bad_request" });
      }
    });
    server.on("error", (err) => console.warn(`[intro] listener error: ${err.message}`));
    server.listen(port, "127.0.0.1", () => console.log(`[intro] onboarding intros on 127.0.0.1:${port}`));
    return server;
  }
}
