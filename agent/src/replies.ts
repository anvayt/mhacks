// What the agent texts back. PLAN.md §0 rule 4: every figure here is copied from an /api response, never computed.
import type { Band, Estimate, Option, Question } from "./api.ts";

export const WELCOME =
  "Hi, I'm Hidden Rent 🏠 I show the energy bill a rental listing doesn't.\n\n" +
  "Paste a Zillow, Redfin or Apartments.com link, or type an Ann Arbor address, and I'll grade it.";

export const UNIT_SIZE_QUESTION = "How big is the unit in sq ft? It's usually on the listing. (Or say skip.)";

// Any link goes to the API, which knows every listing and map site (and says when a link has no address).
export const LINK = /https?:\/\/\S+/i;
export const ADDRESS = /\d+\s+\S+.*\b(st|street|ave|avenue|rd|road|dr|drive|blvd|ln|lane|ct|court|way|pl|place)\b/i;

const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;
const pct = (x: number) => `${Math.round(x * 100)}%`;
const has = (b: Band | null | undefined): b is Band & { p50: number } => b != null && b.p50 != null;
const range = (b: Band & { p50: number }) =>
  b.p10 != null && b.p90 != null ? `${usd(b.p10)}–${usd(b.p90)}` : usd(b.p50);

/** "built 1939", or "built around 1965 (neighborhood median)" when the year is a census median, not this building's. */
function builtText(b: Estimate["building"]): string {
  if (b.year_built == null) return "";
  return /median/i.test(b.year_built_source ?? "") ? `, built around ${b.year_built} (neighborhood median)` : `, built ${b.year_built}`;
}

function gradeText(e: Estimate): string {
  if (!e.grade) return "";
  const score = e.score != null ? ` · score ${e.score}/100 (predicted)` : "";
  const span = e.grade_span ?? [];
  if (e.locked) return `Grade ${e.grade} 🔒${score}`;
  if (span.length > 1) return `Grade ${span[0]}–${span[span.length - 1]}: answer a few questions to lock it in${score}`;
  return `Grade ${e.grade}${score}`;
}

/** Accuracy from P1's accuracy.basis: "at least" on the ResStock path, and only for gas heat (it's a gas-meter error). */
function accuracyText(e: Estimate): string {
  const acc = e.heating_cooling?.accuracy;
  const err = acc?.seasonal_gas_median_abs_error?.all;
  if (err == null || e.heating_cooling?.building?.heating_fuel === "electric") return "";
  const atLeast = /at least/i.test(acc?.basis ?? "") ? "at least " : "";
  return `Typical error per season vs real Ann Arbor gas meters: ${atLeast}${pct(err)}`;
}

/** After an answer: just what changed (grade, range, badges), short enough for a text. */
export function updateText(e: Estimate, previous?: Estimate): string {
  return [gradeText(e), annualText(e, previous), badgesText(e)].filter(Boolean).join("\n");
}

function annualText(e: Estimate, previous?: Estimate): string {
  const annual = e.bill.annual;
  if (!has(annual)) return "";
  const prev = previous && has(previous.bill.annual) ? range(previous.bill.annual) : null;
  const was = prev && prev !== range(annual) ? ` (was ${prev})` : "";
  const most = annual.p10 != null && annual.p90 != null ? `, most likely ${usd(annual.p50)}` : "";
  return `Heating + cooling a year: ${range(annual)}${most}${was}`;
}

const badgesText = (e: Estimate) => (e.badges?.length ? `🏅 ${e.badges.map((x) => x.replace(/-/g, " ")).join(", ")}` : "");

/** Word an estimate. `previous` is the last estimate in this chat, so a change can quote both API numbers. */
export function estimateText(e: Estimate, previous?: Estimate): string {
  const b = e.building;
  const s = e.bill.seasonal ?? {};
  const lines: string[] = [];
  if (b.address) lines.push(`🏠 ${b.address}`);
  if (b.type && b.sqft != null) {
    lines.push(`${b.type}, ${Math.round(b.sqft).toLocaleString("en-US")} sq ft${b.sqft_estimated ? " (estimated)" : ""}${builtText(b)}`);
  }
  const grade = gradeText(e);
  if (grade) lines.push(grade);
  if (e.percentile_city != null) lines.push(`More efficient than ${pct(e.percentile_city)} of Ann Arbor rentals`);
  if (e.hidden_rent_usd_mo != null) {
    const h = e.hidden_rent_usd_mo;
    lines.push(h >= 0 ? `+${usd(h)}/mo hidden rent vs a typical same-size unit` : `${usd(-h)}/mo less than a typical same-size unit`);
  }
  const yearly = annualText(e, previous);
  if (yearly) lines.push(yearly);
  if (has(s.winter) && has(s.spring) && has(s.summer) && has(s.fall)) {
    lines.push(`Winter ${usd(s.winter.p50)} · Spring ${usd(s.spring.p50)} · Summer ${usd(s.summer.p50)} · Fall ${usd(s.fall.p50)}`);
  }
  if (has(e.co2_t)) lines.push(`CO₂: about ${e.co2_t.p50.toFixed(1)} t a year`);
  const badges = badgesText(e);
  if (badges) lines.push(badges);
  const acc = accuracyText(e);
  if (acc) lines.push(acc);
  return lines.join("\n");
}

export const optionLabel = (o: Option) => (typeof o === "string" ? o : o.label ?? o.text ?? o.value ?? o.id ?? "");
export const optionValue = (o: Option) => (typeof o === "string" ? o : o.value ?? o.id ?? o.label ?? o.text ?? "");

export function questionText(q: Question): string {
  const opts = q.options.map((o, i) => `${i + 1}) ${optionLabel(o)}`).join("  ");
  return opts ? `${q.text}\n${opts}\nReply with a number or the answer.` : q.text;
}

/** Match a texted answer to one of the question's options: "2", "double", "Double-pane"... null if unclear. */
export function matchOption(q: Question, text: string): Option | null {
  const t = text.trim().toLowerCase();
  if (!t) return null;
  const n = Number(t.replace(/[).]$/, ""));
  if (Number.isInteger(n) && n >= 1 && n <= q.options.length) return q.options[n - 1];
  const labels = q.options.map((o) => optionLabel(o).toLowerCase());
  const exact = labels.indexOf(t);
  if (exact >= 0) return q.options[exact];
  const hits = labels.flatMap((l, i) => (t.length >= 3 && (l.includes(t) || t.includes(l)) ? [i] : []));
  return hits.length === 1 ? q.options[hits[0]] : null;
}

/** The text to answer, or null to stay quiet (reactions, typing, read receipts...).
 *  iMessage can deliver a pasted link as a "richlink" instead of "text", so both count. */
export function inboundText(content: { type: string; text?: unknown; url?: unknown }): string | null {
  if (content.type === "text" && typeof content.text === "string") return content.text;
  if (content.type === "richlink" && typeof content.url === "string") return content.url;
  return null;
}
