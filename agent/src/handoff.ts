// Website → iMessage handoff (P2-04 decision: the web's "Continue in iMessage" opens P4's onboarding page).
// The page carries ?session=<API session id> into the pre-filled first text as "ref <id>", and the agent
// reads it back to resume that session (GET /session/{id}, PLAN.md §10 additive).
import { OPENER } from "./photon.ts";

/** API session ids we accept in a URL or a text: short, URL-safe, no spaces. */
export const SESSION_ID = /^[A-Za-z0-9_-]{4,64}$/;
const REF_IN_TEXT = /\bref[:\s#]+([A-Za-z0-9_-]{4,64})\b/i;

export const validSession = (s: string | null | undefined): string | null => (s && SESSION_ID.test(s) ? s : null);

/** The pre-filled first text. Text only (no link), so Apple doesn't flag it as junk. */
export const openerFor = (session?: string | null) => (session ? `${OPENER} (ref ${session})` : OPENER);

/** The session id in an inbound text like "Hi Hidden Rent! … (ref abc123)", or null. */
export const refInText = (text: string): string | null => text.match(REF_IN_TEXT)?.[1] ?? null;
