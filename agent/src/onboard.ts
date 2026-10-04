// Judge onboarding page. Run: npm run onboard
// QR (/qr.svg) → this page → enter phone → Photon allowlists it → Hidden Rent texts them first (src/intro.ts),
// so their own Hidden Rent number (one per user in the shared pool) is waiting in Messages. "Open Messages" is the fallback.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { networkInterfaces } from "node:os";
import { pathToFileURL } from "node:url";
import QRCode from "qrcode";
import { env } from "./env.ts";
import { openerFor, validSession } from "./handoff.ts";
import { createSharedUser, normalizePhone, redirectUrl, type SharedUser } from "./photon.ts";

export type Register = (phone: string, name?: string) => Promise<SharedUser>;
/** Ask the agent to text the intro. True when it did (or did within the last 10 minutes). Never throws. */
export type Intro = (phone: string, session: string | null, line: string) => Promise<boolean>;

/** The agent process holds the only Spectrum connection; it listens on 127.0.0.1 only. */
export const postIntro = (port: number): Intro => async (phone, session, line) => {
  try {
    const res = await fetch(`http://127.0.0.1:${port}/intro`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, session, line }), // line: their assigned number, for the contact card
      signal: AbortSignal.timeout(8000),
    });
    return res.ok;
  } catch {
    return false;
  }
};

/** Mock for USE_MOCKS=1: no Photon call; the redirect becomes a plain sms: link with the opener. */
export const mockRegister: Register = async (phone) => ({
  id: "mock-user",
  phoneNumber: phone,
  assignedPhoneNumber: "+15550000000",
});

const page = (body: string) => `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hidden Rent</title>
<style>
  :root { color-scheme: light dark; --bg:#f7f7f2; --fg:#1b1f1d; --muted:#5a625e; --accent:#1f7a4d; --card:#fff; }
  @media (prefers-color-scheme: dark) { :root { --bg:#121513; --fg:#eef1ee; --muted:#a3aba6; --accent:#4cc38a; --card:#1c201e; } }
  body { margin:0; background:var(--bg); color:var(--fg); font:17px/1.45 system-ui,-apple-system,sans-serif; }
  main { max-width:420px; margin:0 auto; padding:40px 16px; }
  .card { background:var(--card); border-radius:16px; padding:24px; box-shadow:0 1px 3px #0002; }
  h1 { font-size:28px; margin:0 0 8px; } p { color:var(--muted); margin:0 0 20px; }
  label { display:block; font-weight:600; margin:14px 0 6px; }
  input { width:100%; box-sizing:border-box; font-size:18px; padding:12px; border-radius:10px; border:1px solid #8886; background:transparent; color:inherit; }
  button, .button { display:block; box-sizing:border-box; margin-top:20px; width:100%; font-size:18px; font-weight:600; padding:14px; border:0; border-radius:12px; background:var(--accent); color:#fff; text-align:center; text-decoration:none; }
  small { display:block; margin-top:16px; color:var(--muted); overflow-wrap:anywhere; }
  .center { text-align:center; }
  /* QR always fits its box: the SVG scales to the card's width (no fixed pixel size). */
  .qr { width:100%; max-width:320px; margin:0 auto; padding:12px; box-sizing:border-box; background:#fff; border-radius:12px; }
  .qr svg { display:block; width:100%; height:auto; }
  @media (max-width:360px) { main { padding:16px 12px; } .card { padding:16px; } h1 { font-size:24px; } }
  @media print {
    :root { --bg:#fff; --fg:#000; --muted:#333; --card:#fff; }
    body { background:#fff; } main { max-width:none; padding:0; }
    .card { box-shadow:none; border:2px solid #000; max-width:5in; margin:0.5in auto; break-inside:avoid; }
    .noprint { display:none; }
  }
</style></head><body><main><div class="card">${body}</div></main></body></html>`;

const esc = (x: string) => x.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

const form = (session: string | null) => page(`<h1>What's your hidden rent?</h1>
<p>${session ? "Pick up your report in iMessage." : "Text our agent a rental listing and get the energy bill the listing doesn't show."}</p>
<form method="post" action="/join">${session ? `\n  <input type="hidden" name="session" value="${esc(session)}">` : ""}
  <label for="phone">Your iPhone number</label>
  <input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(734) 555-0123" required>
  <label for="name">First name (optional)</label>
  <input id="name" name="name" autocomplete="given-name">
  <button type="submit">Text me</button>
</form>
<small>We only use your number to let it text our agent during MHacks 2026.</small>`);

// Printable table card (PLAN.md §11 demo idea 8). Print from the browser.
const card = (qrSvg: string, publicUrl: string) =>
  page(`<h1 class="center">What's your apartment's hidden rent?</h1>
<p class="center">Scan, text us a listing, get the energy bill it doesn't show.</p>
<div class="qr">${qrSvg}</div>
<small class="center">${esc(publicUrl.replace(/^https?:\/\//, ""))}</small>
<small class="center noprint">Print this page (⌘P). The QR scales to the card.</small>`);

const mask = (phone: string) => `•••-•••-${phone.slice(-4)}`;

// No auto-redirect: on a laptop Messages can't send, so the text we send first is the way in.
const joined = (texted: boolean, assigned: string, location: string) =>
  page(`<h1>${texted ? "Check your Messages" : "Almost there"}</h1>
<p>${texted ? "Hidden Rent just texted you from your own Hidden Rent number." : "Tap Open Messages on your iPhone to text Hidden Rent."}</p>
${assigned ? `<p>Your Hidden Rent number ends in <strong>${esc(mask(assigned))}</strong>. Save it as a contact.</p>` : ""}
<a class="button" href="${esc(location)}">Open Messages</a>
<small>On a laptop? Open the text on your phone instead.</small>`);

const errorPage = (msg: string) =>
  page(`<h1>Hmm.</h1><p>${msg}</p><a href="/">Try again</a>`);

async function readForm(req: IncomingMessage): Promise<URLSearchParams> {
  let raw = "";
  for await (const chunk of req) {
    raw += chunk;
    if (raw.length > 10_000) break;
  }
  return new URLSearchParams(raw);
}

export function createHandler(register: Register, mock: boolean, publicUrl: string, intro: Intro = async () => false) {
  return async (req: IncomingMessage, res: ServerResponse) => {
    const url = new URL(req.url ?? "/", "http://x");
    const html = (status: number, body: string) =>
      res.writeHead(status, { "Content-Type": "text/html; charset=utf-8" }).end(body);

    if (req.method === "GET" && url.pathname === "/") return html(200, form(validSession(url.searchParams.get("session"))));

    if (req.method === "GET" && url.pathname === "/card") {
      // no width: the SVG keeps only its viewBox, so CSS sizes it to the card
      const svg = (await QRCode.toString(publicUrl, { type: "svg", margin: 2 })).replace(/ width="\d+" height="\d+"/, "");
      return html(200, card(svg, publicUrl));
    }
    if (req.method === "GET" && url.pathname === "/qr.svg") {
      const svg = await QRCode.toString(publicUrl, { type: "svg", margin: 2, width: 512 });
      return res.writeHead(200, { "Content-Type": "image/svg+xml" }).end(svg);
    }

    if (req.method === "POST" && url.pathname === "/join") {
      const fields = await readForm(req);
      const phone = normalizePhone(fields.get("phone") ?? "");
      const session = validSession(fields.get("session"));
      const opener = openerFor(session);
      if (!phone) return html(400, errorPage("That doesn't look like a phone number. Use the one your iMessage is on."));
      try {
        const user = await register(phone, fields.get("name")?.trim() || undefined);
        console.log(`allowlisted phone ending ${phone.slice(-4)}${mock ? " (mock)" : ""}`);
        const location = mock ? `sms:&body=${encodeURIComponent(opener)}` : redirectUrl(user.id, opener);
        return html(200, joined(await intro(phone, session, user.assignedPhoneNumber), user.assignedPhoneNumber, location));
      } catch (err) {
        console.error("register failed:", err);
        return html(502, errorPage("We couldn't add your number (our free plan holds 10 phones). Ask us at the table and we'll text you from the demo phone."));
      }
    }

    html(404, errorPage("Page not found."));
  };
}

// Only start the server when run directly (tests import createHandler).
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const register: Register = env.useMocks
    ? mockRegister
    : (phone, name) => createSharedUser(env, phone, name);
  const intro: Intro = env.useMocks ? async () => false : postIntro(env.introPort);
  createServer(createHandler(register, env.useMocks, env.publicUrl, intro)).listen(env.onboardPort, () => {
    console.log(`Onboarding page on http://localhost:${env.onboardPort} (${env.useMocks ? "MOCK Photon" : "real Photon"})`);
    console.log(`QR for ${env.publicUrl}: http://localhost:${env.onboardPort}/qr.svg (printable card: /card)`);
    // Phones on the same Wi-Fi can use the LAN address if the venue network allows it; otherwise use a tunnel.
    const lan = Object.values(networkInterfaces()).flat().find((i) => i && i.family === "IPv4" && !i.internal);
    if (lan) console.log(`Same-Wi-Fi fallback: http://${lan.address}:${env.onboardPort} (set PUBLIC_URL to it or to a tunnel URL)`);
  });
}
