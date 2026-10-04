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
  bill: { annual: Band; note?: string | null };
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

export async function estimate(listing: string, unitSqft?: number): Promise<Estimate> {
  const input = /https?:\/\//i.test(listing) ? { url: listing } : { address: listing };
  const e = keep(await apiFetch<Estimate>("/estimate", { body: { ...input, ...(unitSqft ? { unit_sqft: unitSqft } : {}) } }));
  save("property", null); // a new session isn't the saved home until sign-in adopts it (POST /properties)
  return e;
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

export const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

/** "$301–$5,154" (p10–p90), or the p50 alone when the API has no band. */
export function usdRange(b: Band | null | undefined): string | null {
  if (b?.p50 == null) return null;
  return b.p10 != null && b.p90 != null ? `${usd(b.p10)}–${usd(b.p90)}` : usd(b.p50);
}

/** "B 🔒 locked" or "B–D · answer more to lock it". */
export function gradeStatus(e: Estimate): string {
  const span = e.grade_span ?? [];
  if (e.locked || span.length < 2) return `${e.grade ?? "—"} 🔒 locked`;
  return `${span[0]}–${span[span.length - 1]} · answer more to lock it`;
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

/** Make the current session the signed-in user's home (wave 6: POST /properties {user_id, session_id}). */
export async function adoptSession(): Promise<void> {
  const user_id = load("user");
  const session_id = load("session");
  if (!user_id || !session_id) return;
  const p = await apiFetch<{ property_id: string }>("/properties", { body: { user_id, session_id } });
  save("property", p.property_id);
}
