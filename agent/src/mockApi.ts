// In-process stand-in for /estimate + /answer until P2-04 serves sessions, questions and grades (USE_MOCK_API=1).
// Shaped like PLAN.md §10. Its numbers are made up for wiring only; the agent labels every mock reply "demo data".
import type { Api, ApiResult, Band, Estimate, EstimateRequest, Question } from "./api.ts";

const QUESTIONS: Question[] = [
  { id: "windows", text: "Are the windows single-pane or double-pane?", options: ["single-pane", "double-pane", "not sure"] },
  { id: "floor", text: "Is the unit on the top, middle or ground floor?", options: ["top", "middle", "ground"] },
  { id: "insulation", text: "Has the landlord added insulation or air sealing since 2010?", options: ["yes", "no", "not sure"] },
];
// Each answer narrows the band and the grade span; the last one locks the grade (PLAN.md §5 "lock in your grade").
const STAGES: { halfWidth: number; span: string[] }[] = [
  { halfWidth: 600, span: ["B", "C", "D"] },
  { halfWidth: 380, span: ["B", "C"] },
  { halfWidth: 240, span: ["B", "C"] },
  { halfWidth: 140, span: ["B"] },
];

const band = (p50: number, half: number): Band => ({ p10: p50 - half, p50, p90: p50 + half });

function build(sessionId: string, sqft: number, sqftEstimated: boolean, answered: Set<string>, address: string): Estimate {
  const stage = STAGES[Math.min(answered.size, STAGES.length - 1)];
  const p50 = Math.round(1.6 * sqft);
  const locked = stage.span.length === 1;
  return {
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
    badges: answered.has("windows") ? ["double-pane-club"] : [],
    questions: locked ? [] : QUESTIONS.filter((q) => !answered.has(q.id)).slice(0, 3),
  };
}

export function mockApi(): Api {
  const sessions = new Map<string, { sqft: number; sqftEstimated: boolean; address: string; answered: Set<string> }>();
  let next = 1;
  return {
    mock: true,
    async estimate(req: EstimateRequest): Promise<ApiResult> {
      if ("url" in req && !/\d/.test(req.url)) {
        return { ok: false, code: "needs_address", message: "That link doesn't show the street address. What's the address?", hint: "715 Arbor St, Ann Arbor, MI" };
      }
      const address = "address" in req ? req.address : "Demo listing, Ann Arbor, MI";
      const id = `mock-${next++}`;
      const s = { sqft: req.unit_sqft ?? 850, sqftEstimated: req.unit_sqft == null, address, answered: new Set<string>() };
      sessions.set(id, s);
      return { ok: true, data: build(id, s.sqft, s.sqftEstimated, s.answered, s.address) };
    },
    async session(id: string): Promise<ApiResult> {
      // Stands in for a session the website created: unknown ids are made up on the spot.
      let s = sessions.get(id);
      if (!s) sessions.set(id, (s = { sqft: 850, sqftEstimated: false, address: "Demo listing from the website, Ann Arbor, MI", answered: new Set() }));
      return { ok: true, data: build(id, s.sqft, s.sqftEstimated, s.answered, s.address) };
    },
    async answer({ session_id, question_id }): Promise<ApiResult> {
      const s = sessions.get(session_id);
      if (!s) return { ok: false, code: "not_found", message: "That session expired. Send the listing again." };
      s.answered.add(question_id);
      return { ok: true, data: build(session_id, s.sqft, s.sqftEstimated, s.answered, s.address) };
    },
  };
}
