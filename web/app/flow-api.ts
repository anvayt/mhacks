// W1 flow calls (address → survey → phone sign-in → grade). Every number the screens show comes from these responses.
import { ApiError, apiFetch, load, save } from "./lib/api";

export type Band = { p10: number | null; p50: number | null; p90: number | null };
export type Option = { value: string; label: string };
export type Question = { id: string; text: string; options: Option[] };
export type Estimate = {
  session_id: string;
  building: {
    address?: string | null;
    type?: string | null;
    sqft?: number | null;
    sqft_estimated?: boolean;
    year_built?: number | null;
    year_built_source?: string | null;
  };
  bill: { annual: Band; building_annual?: Band; note?: string | null }; // building_annual: heat is in the rent
  co2_t: Band | null;
  score: number | null;
  grade: string | null;
  grade_span: string[] | null;
  locked: boolean;
  percentile_peers: number | null;
  percentile_city: number | null;
  hidden_rent_usd_mo: number | null;
  badges: string[];
  questions: Question[];
  answers?: Record<string, string>;
};

// ponytail: module cache so client-side navigation between screens skips a refetch; a reload uses GET /session/{id}.
let latest: Estimate | null = null;

function keep(e: Estimate): Estimate {
  latest = e;
  save("session", e.session_id);
  return e;
}

/** P4's onboarding page; with a session it pre-fills "(ref <id>)" so the iMessage agent resumes this report. */
export const ONBOARD = process.env.NEXT_PUBLIC_ONBOARD_URL ?? "http://localhost:8787";
export const imessageUrl = (session?: string | null) =>
  session ? `${ONBOARD.replace(/\/$/, "")}/?session=${encodeURIComponent(session)}` : ONBOARD;

export const listingInput = (listing: string) => (/https?:\/\//i.test(listing) ? { url: listing } : { address: listing });

/** A new lookup becomes the current session; the saved home (`property`) only moves on an explicit save. */
export const estimate = async (listing: string, unitSqft?: number) =>
  keep(await apiFetch<Estimate>("/estimate", { body: { ...listingInput(listing), ...(unitSqft ? { unit_sqft: unitSqft } : {}) } }));

// Outages get plain copy; never the API's internal detail (model URLs, exception names).
const OUTAGE: Record<string, string> = {
  model_unavailable: "Our cost model is starting up. Try again in a minute.",
  lookup_unavailable: "The address lookup isn't answering right now. Try again in a minute.",
};

/** What to show for a failed call: outage copy, the listing's hint for needs_address, else the API's message. */
export function errorText(err: unknown): string {
  if (!(err instanceof ApiError)) return "Something went wrong. Try again.";
  if (OUTAGE[err.code]) return OUTAGE[err.code];
  if (err.code === "needs_address" && err.hint) return `${err.message} The listing only says: ${err.hint}.`;
  return err.message;
}

export const answer = async (questionId: string, value: string) =>
  keep(await apiFetch<Estimate>("/answer", { body: { session_id: load("session"), question_id: questionId, answer: value } }));

/** The current session's latest body, or an ApiError("no_session") when there's none on this device. */
export async function currentEstimate(): Promise<Estimate> {
  const id = load("session");
  if (!id) throw new ApiError(404, "no_session", "Start with a listing link or address.");
  return latest?.session_id === id ? latest : keep(await apiFetch<Estimate>(`/session/${encodeURIComponent(id)}`));
}

/** Multi-unit buildings and townhouses get sq ft from floor area ÷ units, so ask for the listing's number. */
export const needsUnitSize = (e: Estimate) => !!e.building.sqft_estimated && e.building.type !== "Single-Family Detached";

/** What the renter's bill.annual covers: cooling only when heat is included in the rent (wave 6). */
export const billCovers = (e: Estimate) => (e.bill.building_annual ? "cooling" : "heating + cooling");

export const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

/** "$301–$5,154" (p10–p90), or the p50 alone when the API has no band. */
export function usdRange(b: Band | null | undefined): string | null {
  if (b?.p50 == null) return null;
  return b.p10 != null && b.p90 != null ? `${usd(b.p10)}–${usd(b.p90)}` : usd(b.p50);
}

/** The grade as the API can stand behind it: "B", or the span "D–F" whenever more than one grade is possible. */
export function gradeText(e: Estimate): string {
  const span = e.grade_span ?? [];
  return span.length > 1 ? `${span[0]}–${span[span.length - 1]}` : (e.grade ?? "—");
}

/** Next to the grade: "🔒 locked", "answer more to lock it", or a span no answer can narrow. */
export function gradeStatus(e: Estimate): string {
  if ((e.grade_span ?? []).length < 2) return "🔒 locked";
  return e.locked ? "locked: no answer narrows it" : "answer more to lock it";
}

// Phone login (POST /auth/web/start → text "login <code>" → poll GET /auth/web/{login_id}).
export type WebLogin = {
  login_id: string;
  code: string;
  text_body: string;
  redirect_url: string;
  assigned_number_masked: string | null;
  expires_at: string;
};
export type WebLoginStatus = { status: "pending" | "verified" | "expired"; user_id?: string; token?: string };

export const startLogin = (phone: string) => apiFetch<WebLogin>("/auth/web/start", { body: { phone } });
export const loginStatus = (id: string) => apiFetch<WebLoginStatus>(`/auth/web/${encodeURIComponent(id)}`);

/** Make the current session the signed-in user's home (wave 6: POST /properties {user_id, session_id}).
 *  This archives their previous home, so it runs only right after a fresh sign-in or on "Save this as my home". */
export async function adoptSession(): Promise<void> {
  const user_id = load("user");
  const session_id = load("session");
  if (!user_id || !session_id) return;
  const p = await apiFetch<{ property_id: string }>("/properties", { body: { user_id, session_id } });
  save("property", p.property_id);
}

/** Signed in, and is the current session already their saved home? null when not signed in. */
export async function sessionIsHome(): Promise<boolean | null> {
  const user_id = load("user");
  if (!load("token") || !user_id) return null;
  const me = await apiFetch<{ current_property_id: string | null; properties: { id: string; session_id: string }[] }>(
    `/me/${encodeURIComponent(user_id)}`,
  );
  const home = me.properties.find((p) => p.id === me.current_property_id);
  save("property", home?.id ?? null);
  return home?.session_id === load("session");
}
