// What the agent texts back. PLAN.md §0 rule 4: the agent only says numbers returned by our API
// (POST /estimate at API_BASE_URL); every figure below is copied from that response, never computed here.
import { env } from "./env.ts";

export const WELCOME =
  "Hi, I'm Hidden Rent 🏠 I show the energy bill a rental listing doesn't.\n\n" +
  "Paste a Zillow, Redfin or Apartments.com link, or type an Ann Arbor address, and I'll grade it.";

export const NOT_LIVE =
  "Got it! Our estimate engine isn't reachable right now. " +
  "Send it again in a bit and you'll get the heating and cooling cost for that place.";

// Any link goes to the API, which knows every listing and map site (and says when a link has no address).
const LINK = /https?:\/\/\S+/i;
const ADDRESS = /\d+\s+\S+.*\b(st|street|ave|avenue|rd|road|dr|drive|blvd|ln|lane|ct|court|way|pl|place)\b/i;

const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

/** Pick the reply for an inbound text: a link or address gets the real estimate, anything else the welcome. */
export async function replyFor(text: string, fetchFn: typeof fetch = fetch): Promise<string> {
  if (!LINK.test(text) && !ADDRESS.test(text)) return WELCOME;
  let res: Response;
  try {
    res = await fetchFn(`${env.apiBaseUrl}/estimate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(LINK.test(text) ? { url: text } : { address: text }),
      signal: AbortSignal.timeout(200_000), // first look-up of a new area downloads its weather history once
    });
  } catch {
    return NOT_LIVE;
  }
  const data = await res.json().catch(() => null);
  if (res.status === 422 && data?.detail?.message) {
    return data.detail.hint ? `${data.detail.message} (Is it ${data.detail.hint}?)` : data.detail.message;
  }
  return res.ok && data ? estimateText(data) : NOT_LIVE;
}

/** Word a /estimate response. Only fields of the response; grade and questions arrive with P2-04 / P4-02. */
export function estimateText(e: any): string {
  const b = e.building;
  const s = e.bill.seasonal;
  const err = e.heating_cooling.accuracy?.seasonal_gas_median_abs_error?.all;
  return [
    `🏠 ${b.address}`,
    `${b.type}, ${Math.round(b.sqft).toLocaleString("en-US")} sq ft${b.sqft_estimated ? " (estimated)" : ""}, built ${b.year_built}`,
    `Heating + cooling in a typical year: ${usd(e.bill.annual.p50)}`,
    `Winter ${usd(s.winter.p50)} · Spring ${usd(s.spring.p50)} · Summer ${usd(s.summer.p50)} · Fall ${usd(s.fall.p50)}`,
    err != null ? `Median error vs real Ann Arbor meters: ${Math.round(err * 100)}%` : "",
    "Your grade and the questions to ask the landlord are coming soon.",
  ]
    .filter(Boolean)
    .join("\n");
}

/** The text to answer, or null to stay quiet (reactions, typing, read receipts...).
 *  iMessage can deliver a pasted link as a "richlink" instead of "text", so both count. */
export function inboundText(content: { type: string; text?: unknown; url?: unknown }): string | null {
  if (content.type === "text" && typeof content.text === "string") return content.text;
  if (content.type === "richlink" && typeof content.url === "string") return content.url;
  return null;
}
