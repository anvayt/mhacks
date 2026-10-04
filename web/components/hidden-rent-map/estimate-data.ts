import { apiFetch } from "@/app/lib/api";

export interface Estimate {
  session_id: string;
  building: { address: string; sqft: number; type: string };
  grade: string;
  grade_span?: string[];
  locked?: boolean;
  score: number;
  percentile_peers: number;
  hidden_rent_usd_mo: number;
  bill: { annual: { p10: number | null; p50: number; p90: number | null }; note?: string };
  co2_t: { p10: number | null; p50: number; p90: number | null } | null;
  badges?: string[];
}
export const getSession = (id: string) => apiFetch<Estimate>(`/session/${encodeURIComponent(id)}`);
export const money = (n: number) => new Intl.NumberFormat("en-US", {style:"currency", currency:"USD", maximumFractionDigits:0}).format(n);
export function gradeLabel(e: Estimate): string {
  const span = e.grade_span;
  return span && span.length > 1 ? `${span[0]}–${span[span.length - 1]}` : e.grade;
}
export function annualRange(e: Estimate): string {
  const a = e.bill.annual;
  return a.p10 != null && a.p90 != null ? `${money(a.p10)}–${money(a.p90)}/yr` : "Range not available";
}
export function peerLabel(e: Estimate): string {
  return `More efficient than ${Math.round(e.percentile_peers * 100)}% of same-type homes`;
}
export function hiddenRent(e: Estimate): string {
  return `${e.hidden_rent_usd_mo > 0 ? "+" : e.hidden_rent_usd_mo < 0 ? "−" : ""}${money(Math.abs(e.hidden_rent_usd_mo))}/mo`;
}
export function carbon(e: Estimate): string {
  return e.co2_t?.p50 != null ? `${e.co2_t.p50.toFixed(2)} t CO₂/yr` : "CO₂ unavailable";
}
