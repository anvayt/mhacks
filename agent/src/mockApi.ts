// In-process stand-in for /estimate + /answer until P2-04 serves sessions, questions and grades (USE_MOCK_API=1).
// Shaped like PLAN.md §10. Its numbers are made up for wiring only; the agent labels every mock reply "demo data".
import { MockPhase2 } from "./mockPhase2.ts";
import type { Api, ApiResult, Band, Calibration, Estimate, EstimateRequest, Fixes, Question } from "./api.ts";

// P2's real questions (api/app/estimate.py QUESTIONS): {value, label} options, values not always 1..n.
const QUESTIONS: Question[] = [
  { id: "heating_fuel", text: "Is the heat gas or electric, or included in your rent?", options: [{ value: "gas", label: "Gas" }, { value: "electric", label: "Electric" }, { value: "included", label: "Heat is included in my rent" }] },
  { id: "window_panes", text: "Are the windows single-, double- or triple-pane?",
    options: [{ value: "1", label: "Single-pane" }, { value: "2", label: "Double-pane" }, { value: "3", label: "Triple-pane" }] },
  { id: "floor_level", text: "Is the unit on the ground floor, a middle floor or the top floor?",
    options: [{ value: "0", label: "Ground floor" }, { value: "1", label: "Middle floor" }, { value: "2", label: "Top floor" }] },
];
const SKIP = new Set(["skip", "not sure", "unsure", "idk", "dont know", "don't know", "i don't know"]);

/** Like P2's _parse: an option value, label words, or skip (null); undefined = bad_answer. */
function parseAnswer(q: Question, raw: string): string | null | undefined {
  const a = raw.trim().toLowerCase();
  if (SKIP.has(a)) return null;
  const opts = q.options as { value: string; label: string }[];
  const byValue = opts.find((o) => o.value === a);
  if (byValue) return byValue.value;
  const hits = opts.filter((o) => o.label.toLowerCase().split(/[^a-z0-9]+/).some((w) => w && a.split(/[^a-z0-9]+/).includes(w)));
  return hits.length === 1 ? hits[0].value : undefined;
}

// Each answer narrows the band and the grade span; the last one locks the grade (PLAN.md §5 "lock in your grade").
const STAGES: { halfWidth: number; span: string[] }[] = [
  { halfWidth: 600, span: ["B", "C", "D"] },
  { halfWidth: 380, span: ["B", "C"] },
  { halfWidth: 240, span: ["B", "C"] },
  { halfWidth: 140, span: ["B"] },
];

const band = (p50: number, half: number): Band => ({ p10: p50 - half, p50, p90: p50 + half });

function build(sessionId: string, sqft: number, sqftEstimated: boolean, answered: Set<string>, address: string, skipped = new Set<string>(), values: Record<string, string> = {}): Estimate {
  const stage = STAGES[Math.min(answered.size, STAGES.length - 1)];
  const p50 = Math.round(1.6 * sqft);
  const open = QUESTIONS.filter((q) => !answered.has(q.id) && !skipped.has(q.id));
  const locked = stage.span.length === 1 || open.length === 0;
  const result: Estimate = {
    session_id: sessionId,
    building: { address, type: "Multi-Family with 2 - 4 Units", sqft, sqft_estimated: sqftEstimated, year_built: 1962, year_built_source: "mock" },
    bill: {
      annual: band(p50, stage.halfWidth),
      seasonal: {
        winter: band(Math.round(p50 * 0.62), stage.halfWidth * 0.6),
        spring: band(Math.round(p50 * 0.12), stage.halfWidth * 0.15),
        summer: band(Math.round(p50 * 0.16), stage.halfWidth * 0.15),
        fall: band(Math.round(p50 * 0.1), stage.halfWidth * 0.1),
      },
    },
    co2_t: band(2.1, 0.4),
    score: 68,
    grade: stage.span[0],
    grade_span: stage.span,
    locked,
    percentile_peers: 0.68,
    percentile_city: 0.71,
    hidden_rent_usd_mo: 22,
    badges: Number(values.window_panes) >= 2 ? ["double-pane-club"] : [],
    answers: values,
    questions: locked ? [] : open,
  };
  if (values.heating_fuel === "included") {
    result.bill.building_annual = result.bill.annual;
    result.bill.annual = band(Math.round(p50 * .16), Math.round(stage.halfWidth * .16));
    result.bill.seasonal = { winter: band(0, 0), spring: band(0, 0), summer: result.bill.annual, fall: band(0, 0) };
    result.bill.note = "Heat is paid by your landlord: your bill shows cooling only; the grade still rates the building.";
    result.hidden_rent_method = "Demo cooling-only comparison.";
  }
  return result;
}

export function mockApi(): Api {
  const sessions = new Map<string, { sqft: number; sqftEstimated: boolean; address: string; answered: Set<string>; skipped?: Set<string>; bills?: number; values?: Record<string, string> }>();
  const body = (id: string) => {
    const s = sessions.get(id)!;
    return build(id, s.sqft, s.sqftEstimated, s.answered, s.address, s.skipped, s.values);
  };
  let next = 1;
  const phase2 = new MockPhase2((req) => api.estimate(req), (id) => api.session(id));
  const api: Api = {
    ...phase2.methods,
    mock: true,
    async estimate(req: EstimateRequest): Promise<ApiResult> {
      if ("url" in req && !/\d/.test(req.url)) {
        return { ok: false, code: "needs_address", message: "That link doesn't show the street address. What's the address?", hint: "715 Arbor St, Ann Arbor, MI" };
      }
      const address = "address" in req ? req.address : "Demo listing, Ann Arbor, MI";
      const id = `mock-${next++}`;
      const s = { sqft: req.unit_sqft ?? 850, sqftEstimated: req.unit_sqft == null, address, answered: new Set<string>() };
      sessions.set(id, s);
      return { ok: true, data: body(id) };
    },
    async session(id: string): Promise<ApiResult> {
      // Stands in for a session the website created: unknown ids are made up on the spot.
      let s = sessions.get(id);
      if (!s) sessions.set(id, (s = { sqft: 850, sqftEstimated: false, address: "Demo listing from the website, Ann Arbor, MI", answered: new Set() }));
      return { ok: true, data: body(id) };
    },
    async calibrate(req): Promise<ApiResult<Calibration>> {
      const s = sessions.get(req.session_id);
      if (!s) return { ok: false, code: "not_found", message: "That session expired. Send the listing again." };
      s.bills = (s.bills ?? 0) + 1;
      const pct = s.bills === 1 ? -12 : -8; // below normal → streak grows
      return {
        ok: true,
        data: await phase2.bill(req, {
          pct_vs_expected_for_weather: pct,
          streak_months: s.bills,
          badges: ["weather-beater"],
          meaningful: true,
          noise_floor: 9.5,
          note: "Gas only: electricity (kWh) isn't compared with the weather yet.",
          estimate: build(req.session_id, s.sqft, s.sqftEstimated, s.answered, s.address, s.skipped, s.values),
        }),
      };
    },
    async fixes(sessionId: string): Promise<ApiResult<Fixes>> {
      const s = sessions.get(sessionId);
      if (!s) return { ok: false, code: "not_found", message: "That session expired. Send the listing again." };
      return {
        ok: true,
        data: {
          fixes: [
            { item: "Air sealing (blower-door tested)", grh_points: 9, co2_kg_saved: 410, usd_saved_yr: 160, cost_usd: null, rebate_usd: 500, new_grade: "B" },
            { item: "Cold-climate heat pump", grh_points: 35, co2_kg_saved: 900, usd_saved_yr: -120, cost_usd: 15400, rebate_usd: 4000, new_grade: "B" },
            { item: "ENERGY STAR low-e storm windows", grh_points: 4, co2_kg_saved: null, usd_saved_yr: null, cost_usd: null, rebate_usd: null, new_grade: null, unpriced: true },
          ],
          grh_points_now: 48,
          grh_points_after: 74,
          grh_points_required: 70,
          landlord_email:
            `Subject: Energy fixes for ${s.address}\n\nHi,\n\nI'm a tenant at ${s.address}. Air sealing and attic insulation ` +
            "would cut heating costs and earn points toward Ann Arbor's Green Rental Housing requirement. DTE rebates cover " +
            "part of the cost. Could we talk about scheduling them?\n\nThanks,",
        },
      };
    },
    async answer({ session_id, question_id, answer }): Promise<ApiResult> {
      const s = sessions.get(session_id);
      if (!s) return { ok: false, code: "not_found", message: "That session expired. Send the listing again." };
      const q = QUESTIONS.find((x) => x.id === question_id);
      if (!q) return { ok: false, code: "bad_answer", message: "I don't have that question. Answer one of the questions I sent, or say skip." };
      const v = parseAnswer(q, String(answer));
      if (v === undefined) {
        const labels = (q.options as { label: string }[]).map((o) => o.label);
        return { ok: false, code: "bad_answer", message: `Sorry, I didn't catch that. ${q.text} Reply ${labels.slice(0, -1).join(", ")} or ${labels.at(-1)}, or say skip.` };
      }
      if (v === null) (s.skipped ??= new Set()).add(question_id);
      else { s.answered.add(question_id); (s.values ??= {})[question_id] = v; }
      return { ok: true, data: body(session_id) };
    },
  };
  return api;
}
