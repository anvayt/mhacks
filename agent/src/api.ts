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
  bill: { annual: Band; building_annual?: Band; note?: string; seasonal?: Partial<Record<"winter" | "spring" | "summer" | "fall", Band>> };
  co2_t?: Band | null;
  score?: number | null;
  grade?: string | null;
  grade_span?: string[];
  locked?: boolean;
  percentile_peers?: number | null;
  percentile_city?: number | null;
  hidden_rent_usd_mo?: number | null;
  hidden_rent_method?: string;
  answers?: Record<string, unknown>;
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

/** POST /calibrate (PLAN.md §10). Assumed: pct is in percent (-12 = 12% below normal); asked P2 to confirm. */
export interface Calibration {
  pct_vs_expected_for_weather: number;
  streak_months: number;
  badges: string[];
  estimate: Estimate;
  /** P1: |pct| > noise_floor. Only winter months (Dec–Feb) are judged; null otherwise. */
  meaningful?: boolean | null;
  /** Percent: P1's typical winter-month error for this estimate path (null outside winter). */
  noise_floor?: number | null;
  note?: string;
  bill_id?: string;
  verified?: boolean;
  snapshot?: { source: string; grade: string; provisional?: boolean; label: string } | null;
  bill_signal?: { grade: string; score: number; annual_usd: number; label: string };
  extracted?: { estimated_from_amount?: boolean; note?: string };
}

export type CalibrateRequest = { session_id: string; property_id?: string } & (
  | { bill_image_base64: string }
  | { therms: number; gas_unit?: "therms" | "ccf"; kwh?: number; start: string; end: string }
  | { amount_usd: number; kwh?: number; start: string; end: string }
);

export interface Account { user_id: string; created: boolean; current_property_id: string | null }
export interface Property { id: string; user_id: string; address: string; session_id: string; active: boolean }
export interface Me {
  user_id: string; current_property_id: string | null; properties: Property[];
  current_estimate: Estimate | null;
  current_grade?: { source: string; grade: string; score: number; bill_annual: Band; label?: string } | null;
  pending_checkin: Checkin | null; calendar_connected: boolean;
  timezone: string; reminder_prefs: { channel: string; cadence: string; hour_local: number; paused: boolean };
  habit_streak?: { current: number; best: number; checked_in_today: boolean };
}
export interface Checkin { property_id: string; address: string; created_at: string; message_hint: string }
export interface Suggestion {
  catalog_id: string; title: string; who_acts: string; pending_model: boolean;
  grh_points: number | null; note?: string;
  projected: { usd_saved_yr: number | null; co2_kg_saved_yr: number | null; score_delta: number | null; new_grade: string | null; label: string } | null;
}
export interface Commitment { id: string; user_id: string; property_id: string; catalog_id: string; title: string; status: string; evidence: string; target_date?: string | null; calendar_event_id?: string | null }
export interface Projection {
  label: string;
  current: { grade: string; score: number; bill_annual: Band; co2_kg_yr: Band };
  projected: { grade: string; score: number; bill_annual: Band; co2_kg_yr: Band; label: string };
  delta: { usd_saved_yr: number | null; co2_kg_saved_yr: number | null; score: number | null; label: string };
  modeled: string[]; not_modeled: string[];
}
export interface Reminder { reminder_id: string; user_id: string; handle: string; kind: "checkin" | "task" | "weather"; text_hint: string; property_id: string; commitment_id?: string; demo?: boolean }
/** POST /reminders/inbound: the reminder this text answers (delivered since the last inbound, today or yesterday). */
export interface ReplyingTo { reminder_id: string; kind: Reminder["kind"]; local_date: string; commitment_id?: string }
export interface ReminderState { user_id?: string; stopped: boolean; paused: boolean; unanswered?: number; reminder_prefs?: Me["reminder_prefs"]; replying_to?: ReplyingTo | null }
/** POST /habits/{user_id}/checkin and GET /habits/{user_id} (+ checkins): the daily habit streak. */
/** POST /simulate/fast-forward: a simulation (never usage) of savings adding up if the commitments are kept. */
export interface FastForward {
  label: "simulated_projected_if_kept"; label_text: string;
  totals: { days: number; end_date: string; usd_saved: number; kg_co2_saved: number };
  commitments: { catalog_id: string; title: string; modeled: boolean }[]; not_modeled: string[];
  real_habit_streak: number; simulated_habit_streak: number;
}
export interface HabitStreak { current: number; best: number; checked_in_today: boolean; last_checkin_date: string | null; badges?: string[] }
export interface CalendarConnection { auth_url: string; mock: boolean; message?: string }
export interface CalendarReminder { reminder_id: string; event_id: string; html_link: string | null; mock: boolean }
export type PropertyRequest = { user_id: string } & ({ session_id: string } | EstimateRequest);

/** One fix. P2 leaves a number null when it can't price it (no invented numbers), and usd_saved_yr can be negative. */
export interface Fix {
  item: string;
  grh_points: number;
  co2_kg_saved: number | null;
  usd_saved_yr: number | null;
  cost_usd: number | null;
  rebate_usd: number | null;
  new_grade: string | null;
  unpriced?: boolean;
}

/** GET /fixes/{session_id} (PLAN.md §10). */
export interface Fixes {
  fixes: Fix[];
  grh_points_now: number;
  grh_points_after: number;
  grh_points_required?: number;
  landlord_email: string;
}

export type ApiResult<T = Estimate> = { ok: true; data: T } | { ok: false; code: string; message: string; hint?: string };

export interface Api {
  /** True for the in-process mock: replies get labelled as demo data. */
  readonly mock: boolean;
  estimate(req: EstimateRequest): Promise<ApiResult>;
  answer(req: AnswerRequest): Promise<ApiResult>;
  /** GET /session/{id} (P2-04 additive): the current estimate of a session started on the website. */
  session(id: string): Promise<ApiResult>;
  calibrate(req: CalibrateRequest): Promise<ApiResult<Calibration>>;
  fixes(sessionId: string): Promise<ApiResult<Fixes>>;
  authPhone(req: { phone: string; photon_user_id?: string; session_id?: string }): Promise<ApiResult<Account>>;
  confirmLogin(req: { code: string; phone: string }): Promise<ApiResult<{ user_id: string }>>;
  me(id: string): Promise<ApiResult<Me>>;
  patchMe(id: string, req: { pending_checkin?: null; reminder_prefs?: Partial<Me["reminder_prefs"]> }): Promise<ApiResult<Me>>;
  property(req: PropertyRequest): Promise<ApiResult<{ property_id: string; estimate: Estimate; active: boolean }>>;
  checkin(userId: string): Promise<ApiResult<Checkin>>;
  suggestions(propertyId: string): Promise<ApiResult<{ commitments: Suggestion[] }>>;
  commitments(propertyId: string): Promise<ApiResult<{ commitments: Commitment[] }>>;
  commit(req: { user_id: string; property_id: string; catalog_id: string; target_date?: string }): Promise<ApiResult<Commitment>>;
  updateCommitment(id: string, status: "completed" | "dismissed"): Promise<ApiResult<Commitment>>;
  projection(req: { property_id: string; commitment_ids: string[] }): Promise<ApiResult<Projection>>;
  remindersDue(): Promise<ApiResult<Reminder[]>>;
  reminderSent(id: string): Promise<ApiResult<ReminderState>>;
  reminderInbound(userId: string): Promise<ApiResult<ReminderState>>;
  reminderControl(userId: string, action: "stop" | "pause" | "resume"): Promise<ApiResult<ReminderState>>;
  reminderDemo(userId: string, kind?: Reminder["kind"]): Promise<ApiResult<Reminder>>;
  habitCheckin(userId: string, req: { date?: string; commitment_id?: string; source: "imessage" }): Promise<ApiResult<HabitStreak>>;
  habits(userId: string): Promise<ApiResult<HabitStreak>>;
  fastForward(req: { property_id: string; days: number }): Promise<ApiResult<FastForward>>;
  calendarConnect(userId: string): Promise<ApiResult<CalendarConnection>>;
  calendarReminder(req: { user_id: string; commitment_id: string; start?: string; cadence: "once" | "daily" | "weekly" }): Promise<ApiResult<CalendarReminder>>;

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

export function checkCalibration(c: unknown): { fatal: string[]; warnings: string[] } {
  if (!isObj(c)) return { fatal: ["body is not an object"], warnings: [] };
  const fatal = isNum(c.pct_vs_expected_for_weather) ? [] : ["pct_vs_expected_for_weather missing"];
  const warnings: string[] = [];
  if (!isNum(c.streak_months)) warnings.push("streak_months missing");
  if (!Array.isArray(c.badges)) warnings.push("badges is not an array");
  if (c.estimate != null) warnings.push(...checkEstimate(c.estimate).fatal.map((w) => `estimate: ${w}`));
  return { fatal, warnings };
}

export function checkFixes(f: unknown): { fatal: string[]; warnings: string[] } {
  if (!isObj(f)) return { fatal: ["body is not an object"], warnings: [] };
  const fatal: string[] = [];
  const warnings: string[] = [];
  if (!Array.isArray(f.fixes)) fatal.push("fixes is not an array");
  else {
    f.fixes.forEach((x: any, i: number) => {
      if (!isObj(x) || typeof x.item !== "string") warnings.push(`fixes[${i}].item missing`);
    });
  }
  if (typeof f.landlord_email !== "string") warnings.push("landlord_email missing");
  if (!isNum(f.grh_points_now) || !isNum(f.grh_points_after)) warnings.push("grh_points_now/after missing");
  return { fatal, warnings };
}

/** The agent words "Day N 🔥, best B" only from these numbers. */
export function checkHabit(h: unknown): { fatal: string[]; warnings: string[] } {
  if (!isObj(h)) return { fatal: ["body is not an object"], warnings: [] };
  const fatal = ["current", "best"].filter((k) => !isNum(h[k]) || h[k] < 0).map((k) => `${k} missing`);
  if (typeof h.checked_in_today !== "boolean") fatal.push("checked_in_today missing");
  return { fatal, warnings: [] };
}

/** A fast-forward reply only words a body that says it's a simulation and carries the totals and real streak. */
export function checkFastForward(f: unknown): { fatal: string[]; warnings: string[] } {
  if (!isObj(f)) return { fatal: ["body is not an object"], warnings: [] };
  const fatal = f.label === "simulated_projected_if_kept" ? [] : ["label is not simulated_projected_if_kept"];
  if (!isObj(f.totals) || !isNum(f.totals.usd_saved) || !isNum(f.totals.kg_co2_saved) || !isNum(f.totals.days)) fatal.push("totals missing");
  if (!isNum(f.real_habit_streak)) fatal.push("real_habit_streak missing");
  if (!Array.isArray(f.commitments)) fatal.push("commitments is not an array");
  return { fatal, warnings: [] };
}

type Check = (body: unknown) => { fatal: string[]; warnings: string[] };

export type Logger = (msg: string) => void;

export const UNREACHABLE =
  "Got it! Our estimate engine isn't reachable right now. " +
  "Send it again in a bit and you'll get the heating and cooling cost for that place.";

/** The real /api over HTTP. 422/503 bodies are {detail: {code, message, hint?}}. */
export function httpApi(baseUrl: string, fetchFn: typeof fetch = fetch, log: Logger = console.warn, agentKey = ""): Api {
  async function call<T = Estimate>(
    method: "GET" | "POST" | "PATCH",
    path: string,
    body: unknown,
    timeoutMs: number,
    check: Check = checkEstimate,
  ): Promise<ApiResult<T>> {
    let res: Response;
    try {
      res = await fetchFn(`${baseUrl}${path}`, {
        method,
        // All texters share this server's IP, including on public API routes.
        headers: { "Content-Type": "application/json", ...(agentKey ? { "X-Agent-Key": agentKey } : {}) },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch {
      return { ok: false, code: "unreachable", message: UNREACHABLE };
    }
    const data = await res.json().catch(() => null);
    if (res.ok) {
      const { fatal, warnings } = check(data);
      for (const w of warnings) log(`[contract] ${method} ${path}: ${w} (PLAN.md §10)`);
      if (fatal.length) {
        log(`[contract] ${method} ${path}: ${fatal.join("; ")} (PLAN.md §10); not replying with numbers`);
        return { ok: false, code: "contract_mismatch", message: CONTRACT_ERROR };
      }
      return { ok: true, data: data as T };
    }
    const d = data?.detail;
    if (d && typeof d === "object" && typeof d.message === "string") {
      return { ok: false, code: d.code ?? String(res.status), message: d.message, hint: d.hint ?? undefined };
    }
    if (res.status === 404 || res.status === 405) return { ok: false, code: "not_served", message: UNREACHABLE };
    return { ok: false, code: String(res.status), message: UNREACHABLE };
  }
  const generic: Check = (body) => ({ fatal: isObj(body) || Array.isArray(body) ? [] : ["body missing"], warnings: [] });
  const accountCall = <T>(method: "GET" | "POST" | "PATCH", path: string, body?: unknown) => call<T>(method, path, body, 200_000, generic);
  return {
    mock: false,
    // the first look-up of a new area downloads its weather history once
    estimate: (req) => call("POST", "/estimate", req, 200_000),
    answer: (req) => call("POST", "/answer", req, 60_000),
    session: (id) => call("GET", `/session/${encodeURIComponent(id)}`, undefined, 30_000),
    // a vision model reads the bill photo, so give it time
    calibrate: (req) => call<Calibration>("POST", "/calibrate", req, 120_000, checkCalibration),
    fixes: (id) => call<Fixes>("GET", `/fixes/${encodeURIComponent(id)}`, undefined, 60_000, checkFixes),
    authPhone: (req) => accountCall("POST", "/auth/phone", req),
    confirmLogin: (req) => accountCall("POST", "/auth/web/confirm", req),
    me: (id) => accountCall("GET", `/me/${encodeURIComponent(id)}`),
    patchMe: (id, req) => accountCall("PATCH", `/me/${encodeURIComponent(id)}`, req),
    property: (req) => accountCall("POST", "/properties", req),
    checkin: (user_id) => accountCall("POST", "/checkins/trigger", { user_id }),
    suggestions: (id) => accountCall("GET", `/commitments/suggested/${encodeURIComponent(id)}`),
    commitments: (id) => accountCall("GET", `/commitments?property_id=${encodeURIComponent(id)}`),
    commit: (req) => accountCall("POST", "/commitments", req),
    updateCommitment: (id, status) => accountCall("PATCH", `/commitments/${encodeURIComponent(id)}`, { status }),
    projection: (req) => accountCall("POST", "/projection", req),
    remindersDue: () => accountCall("GET", "/reminders/due"),
    reminderSent: (id) => accountCall("POST", `/reminders/${encodeURIComponent(id)}/sent`),
    reminderInbound: (user_id) => accountCall("POST", "/reminders/inbound", { user_id }),
    reminderControl: (id, action) => accountCall("POST", `/reminders/${encodeURIComponent(id)}/${action}`),
    reminderDemo: (user_id, kind) => accountCall("POST", "/reminders/demo-send", { user_id, ...(kind ? { kind } : {}) }),
    habitCheckin: (id, req) => call<HabitStreak>("POST", `/habits/${encodeURIComponent(id)}/checkin`, req, 30_000, checkHabit),
    habits: (id) => call<HabitStreak>("GET", `/habits/${encodeURIComponent(id)}`, undefined, 30_000, checkHabit),
    // one composed model run, like /projection
    fastForward: (req) => call<FastForward>("POST", "/simulate/fast-forward", req, 120_000, checkFastForward),
    calendarConnect: (user_id) => accountCall("POST", "/calendar/connect", { user_id }),
    calendarReminder: (req) => accountCall("POST", "/calendar/reminders", req),
  };
}
