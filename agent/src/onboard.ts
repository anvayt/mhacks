// Judge onboarding page. Run: npm run onboard
// QR (/qr.svg) → this page → enter phone → Photon allowlists it → Messages opens with the opener pre-filled.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { networkInterfaces } from "node:os";
import { pathToFileURL } from "node:url";
import QRCode from "qrcode";
import { env } from "./env.ts";
import { OPENER, createSharedUser, normalizePhone, redirectUrl, type SharedUser } from "./photon.ts";

export type Register = (phone: string, name?: string) => Promise<SharedUser>;

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
  button { margin-top:20px; width:100%; font-size:18px; font-weight:600; padding:14px; border:0; border-radius:12px; background:var(--accent); color:#fff; }
  small { display:block; margin-top:16px; color:var(--muted); }
</style></head><body><main><div class="card">${body}</div></main></body></html>`;

const FORM = page(`<h1>What's your hidden rent?</h1>
<p>Text our agent a rental listing and get the energy bill the listing doesn't show.</p>
<form method="post" action="/join">
  <label for="phone">Your iPhone number</label>
  <input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(734) 555-0123" required>
  <label for="name">First name (optional)</label>
  <input id="name" name="name" autocomplete="given-name">
  <button type="submit">Open iMessage</button>
</form>
<small>We only use your number to let it text our agent during MHacks 2026.</small>`);

// Printable table card (PLAN.md §11 demo idea 8). Print from the browser.
const card = (qrSvg: string, publicUrl: string) =>
  page(`<h1 style="text-align:center">What's your apartment's hidden rent?</h1>
<p style="text-align:center">Scan, text us a listing, get the energy bill it doesn't show.</p>
<div style="max-width:320px;margin:0 auto;background:#fff;border-radius:12px">${qrSvg}</div>
<small style="text-align:center">${publicUrl.replace(/^https?:\/\//, "")}</small>`);

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

export function createHandler(register: Register, mock: boolean, publicUrl: string) {
  return async (req: IncomingMessage, res: ServerResponse) => {
    const url = new URL(req.url ?? "/", "http://x");
    const html = (status: number, body: string) =>
      res.writeHead(status, { "Content-Type": "text/html; charset=utf-8" }).end(body);

    if (req.method === "GET" && url.pathname === "/") return html(200, FORM);

    if (req.method === "GET" && (url.pathname === "/qr.svg" || url.pathname === "/card")) {
      const svg = await QRCode.toString(publicUrl, { type: "svg", margin: 2, width: 512 });
      if (url.pathname === "/card") return html(200, card(svg, publicUrl));
      return res.writeHead(200, { "Content-Type": "image/svg+xml" }).end(svg);
    }

    if (req.method === "POST" && url.pathname === "/join") {
      const form = await readForm(req);
      const phone = normalizePhone(form.get("phone") ?? "");
      if (!phone) return html(400, errorPage("That doesn't look like a phone number. Use the one your iMessage is on."));
      try {
        const user = await register(phone, form.get("name")?.trim() || undefined);
        console.log(`allowlisted ${phone} → user ${user.id}${mock ? " (mock)" : ""}`);
        const location = mock ? `sms:&body=${encodeURIComponent(OPENER)}` : redirectUrl(user.id);
        return res.writeHead(302, { Location: location }).end();
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
  createServer(createHandler(register, env.useMocks, env.publicUrl)).listen(env.onboardPort, () => {
    console.log(`Onboarding page on http://localhost:${env.onboardPort} (${env.useMocks ? "MOCK Photon" : "real Photon"})`);
    console.log(`QR for ${env.publicUrl}: http://localhost:${env.onboardPort}/qr.svg (printable card: /card)`);
    // Phones on the same Wi-Fi can use the LAN address if the venue network allows it; otherwise use a tunnel.
    const lan = Object.values(networkInterfaces()).flat().find((i) => i && i.family === "IPv4" && !i.internal);
    if (lan) console.log(`Same-Wi-Fi fallback: http://${lan.address}:${env.onboardPort} (set PUBLIC_URL to it or to a tunnel URL)`);
  });
}
