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
  /** GET /session/{id} (P2-04 additive): the current estimate of a session started on the website. */
  session(id: string): Promise<ApiResult>;
}

export const CONTRACT_ERROR = "Something went wrong on our side reading that answer. Try again in a bit.";

const isObj = (x: unknown): x is Record<string, any> => typeof x === "object" && x !== null && !Array.isArray(x);
const isNum = (x: unknown) => typeof x === "number" && Number.isFinite(x);

/** Check an /estimate or /answer body against PLAN.md §10. `fatal` problems mean the agent can't word a reply. */
export function checkEstimate(e: unknown): { fatal: string[]; warnings: string[] } {
  const fatal: string[] = [];
  const warnings: string[] = [];
  if (!isObj(e)) return { fatal: ["body is not an object"], warnings };
  if (!isObj(e.building)) fatal.push("building missing");
  if (!isObj(e.bill) || !isObj(e.bill.annual) || !isNum(e.bill.annual.p50)) fatal.push("bill.annual.p50 missing");
  if (!("session_id" in e)) warnings.push("session_id key missing");
  if (e.questions != null && !Array.isArray(e.questions)) warnings.push("questions is not an array");
  if (Array.isArray(e.questions)) {
    e.questions.forEach((q: any, i: number) => {
      if (!isObj(q) || typeof q.id !== "string" || typeof q.text !== "string" || !Array.isArray(q.options)) {
        warnings.push(`questions[${i}] needs {id, text, options[]}`);
      }
    });
  }
  if (e.grade_span != null && !Array.isArray(e.grade_span)) warnings.push("grade_span is not an array");
  return { fatal, warnings };
}

export type Logger = (msg: string) => void;

export const UNREACHABLE =
  "Got it! Our estimate engine isn't reachable right now. " +
  "Send it again in a bit and you'll get the heating and cooling cost for that place.";

/** The real /api over HTTP. 422/503 bodies are {detail: {code, message, hint?}}. */
export function httpApi(baseUrl: string, fetchFn: typeof fetch = fetch, log: Logger = console.warn): Api {
  async function call(method: "GET" | "POST", path: string, body: unknown, timeoutMs: number): Promise<ApiResult> {
    let res: Response;
    try {
      res = await fetchFn(`${baseUrl}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch {
      return { ok: false, code: "unreachable", message: UNREACHABLE };
    }
    const data = await res.json().catch(() => null);
    if (res.ok) {
      const { fatal, warnings } = checkEstimate(data);
      for (const w of warnings) log(`[contract] ${method} ${path}: ${w} (PLAN.md §10)`);
      if (fatal.length) {
        log(`[contract] ${method} ${path}: ${fatal.join("; ")} (PLAN.md §10); not replying with numbers`);
        return { ok: false, code: "contract_mismatch", message: CONTRACT_ERROR };
      }
      return { ok: true, data: data as Estimate };
    }
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
    estimate: (req) => call("POST", "/estimate", req, 200_000),
    answer: (req) => call("POST", "/answer", req, 60_000),
    session: (id) => call("GET", `/session/${encodeURIComponent(id)}`, undefined, 30_000),
  };
}
