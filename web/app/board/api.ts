import { ApiError } from "../lib/api";

export type Band = { p10?: number | null; p50: number; p90?: number | null };
export type Estimate = {
  session_id: string; building: { address: string; sqft: number; type: string };
  bill: { annual: Band; building_annual?: Band; band_method?: string; note?: string; covers?: string };
  score: number; grade: string; grade_span?: string[]; locked?: boolean; badges?: string[];
};
export type Snapshot = { id: string; source: string; grade: string; grade_span?: string[]; score: number; bill_annual: Band; created_at: string; label?: string; provisional?: boolean };
export type Position = {
  current: { score: number; grade: string; percentile_city: number; rank: number; of: number };
  projected: { rank?: number; score: number; percentile_city?: number; percentile?: number; label: string } | null;
  neighbors: { rank: number; score: number; cost_per_sqft: number }[];
  model_version?: string; current_source?: string; projection_reason?: { code: string; message: string } | null;
};
export type Suggestion = {
  catalog_id: string; title: string; who_acts: string; pending_model: boolean; grh_points?: number | null; note?: string;
  projected: { usd_saved_yr: number; co2_kg_saved_yr: number; new_grade: string; label: string } | null;
};
export type Commitment = { id: string; catalog_id: string; title: string; status: string; evidence: string; target_date?: string };
export type Projection = {
  projected: { score: number; grade: string; percentile_city: number; bill_annual: Band; building_annual_usd?: number; co2_kg_yr: Band; label: string };
  delta: { usd_saved_yr: number; co2_kg_saved_yr: number }; label: string; model_version?: string;
};
export type PublicBoard = {
  best: { benchmark_id: number; name: string; score: number; grade: string; source?: string; demo?: boolean }[];
  worst_blocks: { geoid: string; area_type: string; building_count: number; excess_usd_per_sqft: number; demo?: boolean }[];
};
export type VerifiedBoard = { entries: { rank: number; alias?: string; geoid?: string; value: number; unit: string; demo: boolean }[]; empty_reason: string | null; metric_note?: string };
export type Calibration = {
  extracted?: { estimated_from_amount?: boolean; note?: string };
  pct_vs_expected_for_weather: number; streak_months: number; badges: string[]; verified?: boolean;
  snapshot?: Snapshot | null; note?: string; noise_floor?: number | null;
  bill_signal?: { grade: string; score: number; provisional?: boolean; label?: string } | null;
  impact?: { co2_kg_avoided: number; usd_saved: number } | null;
};
export type Fixes = {
  fixes: { item: string; grh_points: number; usd_saved_yr: number | null; co2_kg_saved: number | null; unpriced?: boolean }[];
  landlord_email: string | { subject?: string; body?: string };
};
export const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
export const kg = (value: number) => `${Math.round(value).toLocaleString("en-US")} kg`;
export function errorText(error: unknown): string {
  if (error instanceof ApiError) return [error.message, error.hint].filter(Boolean).join(" ");
  return error instanceof Error ? error.message : "Something went wrong. Try again.";
}
export const gradeSpan = (grade: string, span?: string[]) => span?.length ? (span.length > 1 ? `${span[0]}–${span[span.length - 1]}` : span[0]) : grade;
export function billRange(band: Band) {
  return band.p10 != null && band.p90 != null ? `${money(band.p10)}–${money(band.p90)}/yr (P10–P90)` : `About ${money(band.p50)}/yr; range unavailable`;
}
