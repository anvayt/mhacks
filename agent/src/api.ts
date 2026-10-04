// Client for our /api (PLAN.md §10). The agent only repeats numbers from these responses (PLAN.md §0 rule 4).

export interface Band {
  p10: number | null;
  p50: number | null;
  p90: number | null;
}

export type Option = string | { id?: string; value?: string; label?: string; text?: string };

export interface Question {
  id: string;
  text: string;
  options: Option[];
}

/** The §10 estimate shape plus the integration's additive fields. Fields the API hasn't built yet are null/empty. */
export interface Estimate {
  session_id: string | null;
  building: {
    address?: string;
    type?: string | null;
    sqft?: number | null;
    sqft_estimated?: boolean;
    year_built?: number | null;
    year_built_source?: string | null;
  };
  bill: { annual: Band; seasonal?: Partial<Record<"winter" | "spring" | "summer" | "fall", Band>> };
  co2_t?: Band | null;
  score?: number | null;
  grade?: string | null;
  grade_span?: string[];
  locked?: boolean;
  percentile_peers?: number | null;
  percentile_city?: number | null;
  hidden_rent_usd_mo?: number | null;
  badges?: string[];
  questions?: Question[];
  heating_cooling?: {
    building?: { heating_fuel?: string | null };
    accuracy?: { seasonal_gas_median_abs_error?: { all?: number | null } | null; basis?: string | null };
  };
}

export type EstimateRequest = ({ url: string } | { address: string }) & { unit_sqft?: number };

export interface AnswerRequest {
  session_id: string;
  question_id: string;
  answer: string;
}

export type ApiResult = { ok: true; data: Estimate } | { ok: false; code: string; message: string; hint?: string };

export interface Api {
  /** True for the in-process mock: replies get labelled as demo data. */
  readonly mock: boolean;
  estimate(req: EstimateRequest): Promise<ApiResult>;
  answer(req: AnswerRequest): Promise<ApiResult>;
}

export const UNREACHABLE =
  "Got it! Our estimate engine isn't reachable right now. " +
  "Send it again in a bit and you'll get the heating and cooling cost for that place.";

/** The real /api over HTTP. 422/503 bodies are {detail: {code, message, hint?}}. */
export function httpApi(baseUrl: string, fetchFn: typeof fetch = fetch): Api {
  async function post(path: string, body: unknown, timeoutMs: number): Promise<ApiResult> {
    let res: Response;
    try {
      res = await fetchFn(`${baseUrl}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch {
      return { ok: false, code: "unreachable", message: UNREACHABLE };
    }
    const data = await res.json().catch(() => null);
    if (res.ok && data) return { ok: true, data };
    const d = data?.detail;
    if (d && typeof d === "object" && typeof d.message === "string") {
      return { ok: false, code: d.code ?? String(res.status), message: d.message, hint: d.hint ?? undefined };
    }
    if (res.status === 404 || res.status === 405) return { ok: false, code: "not_served", message: UNREACHABLE };
    return { ok: false, code: String(res.status), message: UNREACHABLE };
  }
  return {
    mock: false,
    // the first look-up of a new area downloads its weather history once
    estimate: (req) => post("/estimate", req, 200_000),
    answer: (req) => post("/answer", req, 60_000),
  };
}
