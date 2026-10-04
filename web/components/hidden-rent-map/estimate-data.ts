import { apiFetch } from "@/app/lib/api";

type Band = { p10: number | null; p50: number; p90: number | null };

export interface Estimate {
  session_id: string;
  building: { address: string; sqft: number | null; type: string };
  grade: string;
  grade_span?: string[];
  locked?: boolean;
  score: number;
  percentile_peers: number;
  hidden_rent_usd_mo: number | null;
  // building_annual: present when heat is included in the rent; annual is then the renter's cooling only
  bill: { annual: Band; building_annual?: Band; note?: string };
  co2_t: { p10: number | null; p50: number; p90: number | null } | null;
  badges?: string[];
}
export const getSession = (id: string) => apiFetch<Estimate>(`/session/${encodeURIComponent(id)}`);
export const money = (n: number) => new Intl.NumberFormat("en-US", {style:"currency", currency:"USD", maximumFractionDigits:0}).format(n);
export function gradeLabel(e: Estimate): string {
  const span = e.grade_span;
  return span && span.length > 1 ? `${span[0]}–${span[span.length - 1]}` : e.grade;
}
const range = (a: Band) => a.p10 != null && a.p90 != null ? `${money(a.p10)}–${money(a.p90)}/yr` : "Range not available";
export const annualRange = (e: Estimate) => range(e.bill.annual);
/** Eyebrow over bill.annual: cooling only when heat is included in the rent. */
export const billLabel = (e: Estimate) =>
  e.bill.building_annual ? "PREDICTED · YOUR COOLING (HEAT IS IN YOUR RENT)" : "PREDICTED · HEATING + COOLING ONLY";
/** Second line when heat is included: the building's heating + cooling behind the grade. */
export function buildingLine(e: Estimate): string | null {
  const b = e.bill.building_annual;
  return b ? `Building's predicted heating + cooling: ${money(b.p50)}/yr (${range(b)})` : null;
}
export function peerLabel(e: Estimate): string {
  return `More efficient than ${Math.floor(e.percentile_peers * 100)}% of same-type homes`;
}
export function hiddenRent(e: Estimate): string {
  if (e.hidden_rent_usd_mo == null) return "Unavailable";
  return `${e.hidden_rent_usd_mo > 0 ? "+" : e.hidden_rent_usd_mo < 0 ? "−" : ""}${money(Math.abs(e.hidden_rent_usd_mo))}/mo`;
}
export function carbon(e: Estimate): string {
  return e.co2_t?.p50 != null ? `${e.co2_t.p50.toFixed(1)} t CO₂/yr` : "CO₂ unavailable";
}
