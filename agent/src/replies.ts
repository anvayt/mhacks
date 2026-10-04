// What the agent texts back. PLAN.md §0 rule 4: the agent only says numbers
// returned by our API, so until /estimate is wired up (P4-02) it says none.

export const WELCOME =
  "Hi, I'm Hidden Rent 🏠 I show the energy bill a rental listing doesn't.\n\n" +
  "Paste a Zillow, Redfin or Apartments.com link, or type an Ann Arbor address, and I'll grade it.";

export const NOT_LIVE =
  "Got it! The estimate engine is still being built tonight (we're mid-hackathon). " +
  "Send it again in a bit and you'll get a grade, a $ range and the questions to ask your landlord.";

const LISTING_URL = /https?:\/\/\S*(zillow|redfin|apartments)\.com\S*/i;
const ADDRESS = /\d+\s+\S+.*\b(st|street|ave|avenue|rd|road|dr|drive|blvd|ln|lane|ct|court|way|pl|place)\b/i;

/** Pick the reply for an inbound text: a listing link or address gets NOT_LIVE, anything else the welcome. */
export function replyFor(text: string): string {
  return LISTING_URL.test(text) || ADDRESS.test(text) ? NOT_LIVE : WELCOME;
}

/** The text to answer, or null to stay quiet (reactions, typing, read receipts...).
 *  iMessage can deliver a pasted link as a "richlink" instead of "text", so both count. */
export function inboundText(content: { type: string; text?: unknown; url?: unknown }): string | null {
  if (content.type === "text" && typeof content.text === "string") return content.text;
  if (content.type === "richlink" && typeof content.url === "string") return content.url;
  return null;
}
