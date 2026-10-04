const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const count = new Intl.NumberFormat("en-US");

export const usd = (v: number) => money.format(Math.round(v));
export const num = (v: number) => count.format(Math.round(v));
export const signedUsd = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : "±"}${money.format(Math.abs(Math.round(v)))}`;

const BUILDING_TYPES: Record<string, string> = {
  "Single-Family Detached": "a detached house",
  "Single-Family Attached": "a townhouse",
  "Multi-Family with 2 - 4 Units": "a 2–4 unit building",
  "Multi-Family with 5+ Units": "an apartment building (5+ units)",
  "Mobile Home": "a mobile home",
};
export const buildingTypeLabel = (t: string) => BUILDING_TYPES[t] ?? t;

/** Brand blue (cheaper) → brand red (pricier), by position t ∈ [0, 1]. */
export function costColor(t: number): string {
  const c = Math.min(1, Math.max(0, t));
  const a = [0x17, 0x3b, 0xfa];
  const b = [0xf2, 0x38, 0x33];
  const mix = a.map((v, i) => Math.round(v + (b[i] - v) * c).toString(16).padStart(2, "0"));
  return `#${mix.join("")}`;
}
