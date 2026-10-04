// What the agent texts back. PLAN.md §0 rule 4: every figure here is copied from an /api response, never computed.
import type { Band, Calibration, Estimate, Fix, Fixes, Option, Question } from "./api.ts";

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

export const NEED_LISTING_FOR_BILL =
  "Send your listing link or address first so I know which home this bill is for, then send the bill again.";

/** After a bill: how it compares with what the weather predicts, plus streak and badges (all from /calibrate).
 *  P1 only judges winter months, and a difference inside its typical error isn't a real difference. */
export function calibrationText(c: Calibration): string {
  const p = Math.round(c.pct_vs_expected_for_weather);
  const dir = p < 0 ? "below" : "above";
  let first: string;
  if (c.meaningful === false) {
    const noise = c.noise_floor != null ? `, inside our typical ±${Math.round(c.noise_floor)}% error` : "";
    first = `📄 Your bill is within the normal range for this weather (${p > 0 ? "+" : ""}${p}% vs expected${noise}).`;
  } else if (c.meaningful === null) {
    first = `📄 Your bill is ${Math.abs(p)}% ${dir} what this month's weather predicts. Outside Dec–Feb that's a rough read, since heating doesn't dominate.`;
  } else {
    first = p === 0
      ? "📄 Your bill is right at normal for this weather."
      : `📄 Your bill is ${Math.abs(p)}% ${dir} normal for this weather${p < 0 ? " 🎉" : "."}`;
  }
  const lines = [first];
  if (c.streak_months > 0) lines.push(`🔥 ${c.streak_months}-month streak below normal`);
  if (c.badges?.length) lines.push(`🏅 ${c.badges.map((x) => x.replace(/-/g, " ")).join(", ")}`);
  return lines.join("\n");
}

// Ann Arbor Green Rental Housing: 70 checklist points through Jul 5, 2028 (PLAN.md §4). Used only if the API omits it.
const GRH_REQUIRED = 70;

/** One fix line: only the numbers the API priced; missing ones are left out, never shown as $0. */
function fixLine(x: Fix, i: number): string {
  const parts: string[] = [];
  if (x.usd_saved_yr != null) {
    parts.push(x.usd_saved_yr >= 0 ? `saves ${usd(x.usd_saved_yr)}/yr` : `costs ${usd(-x.usd_saved_yr)}/yr more to run`);
  }
  if (x.co2_kg_saved != null) parts.push(`${x.co2_kg_saved.toLocaleString("en-US")} kg CO₂/yr less`);
  if (x.cost_usd != null) parts.push(`costs ${usd(x.cost_usd)}${x.rebate_usd ? ` (${usd(x.rebate_usd)} rebate)` : ""}`);
  else if (x.rebate_usd) parts.push(`${usd(x.rebate_usd)} rebate`);
  parts.push(`+${x.grh_points} GRH pts`);
  return `${i + 1}) ${x.item}: ${parts.join(", ")}${x.new_grade ? ` → grade ${x.new_grade}` : ""}`;
}

/** Top fixes from /fixes, short enough for a text. The landlord email goes out as its own message. */
export function fixesText(f: Fixes): string {
  if (!f.fixes.length) return "No fixes to suggest for this place right now.";
  const lines = ["🔧 Top fixes:", ...f.fixes.slice(0, 3).map(fixLine)];
  if (f.grh_points_now != null && f.grh_points_after != null) {
    lines.push(`Green Rental Housing points: ${f.grh_points_now} → ${f.grh_points_after} (Ann Arbor requires ${f.grh_points_required ?? GRH_REQUIRED})`);
  }
  if (f.landlord_email) lines.push("I drafted an email to your landlord ↓");
  return lines.join("\n");
}

/** A typed bill ("52 therms 9/3 to 10/2", or CCF), for when the photo reader is down. null if it isn't one. */
export function parseTypedBill(
  text: string,
  today = new Date(),
): { therms: number; kwh?: number; start: string; end: string } | { error: string } | null {
  const gas = text.match(/(\d+(?:\.\d+)?)\s*(therms?|ccf)\b/i);
  if (!gas) return null;
  // 1 CCF = 1.037 therms (EIA FAQ "What are Ccf, Mcf, Btu, and therms?"; the same factor /api uses)
  const therms = /ccf/i.test(gas[2]) ? Math.round(Number(gas[1]) * 1.037 * 10) / 10 : Number(gas[1]);
  const kwh = text.match(/(\d+(?:\.\d+)?)\s*kwh\b/i);
  const dates = [...text.matchAll(/\b(\d{4})-(\d{1,2})-(\d{1,2})\b|\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/g)].map((m) => {
    if (m[1]) return { y: Number(m[1]), m: Number(m[2]), d: Number(m[3]) };
    const y = m[6] ? (m[6].length === 2 ? 2000 + Number(m[6]) : Number(m[6])) : undefined;
    return { y, m: Number(m[4]), d: Number(m[5]) };
  });
  if (dates.length < 2) return { error: "Send the billing dates too, like: 52 therms 9/3 to 10/2" };
  const iso = (x: { y: number; m: number; d: number }) => `${x.y}-${String(x.m).padStart(2, "0")}-${String(x.d).padStart(2, "0")}`;
  const [a, b] = dates.slice(0, 2);
  let endY = b.y ?? today.getFullYear();
  if (b.y == null && new Date(endY, b.m - 1, b.d) > today) endY -= 1; // a bill can't end in the future
  const startY = a.y ?? (a.m > b.m ? endY - 1 : endY); // Dec → Jan spans a new year
  const valid = (y: number, m: number, d: number) => m >= 1 && m <= 12 && d >= 1 && d <= 31 && y > 2000;
  if (!valid(startY, a.m, a.d) || !valid(endY, b.m, b.d)) return { error: "I couldn't read those dates. Try: 52 therms 9/3 to 10/2" };
  return { therms, ...(kwh ? { kwh: Number(kwh[1]) } : {}), start: iso({ y: startY, m: a.m, d: a.d }), end: iso({ y: endY, m: b.m, d: b.d }) };
}

export type Inbound =
  | { kind: "text"; text: string }
  | { kind: "photo"; mimeType: string; name?: string; read: () => Promise<Buffer> };

/** Classify an inbound Spectrum message: text (or a pasted link), a photo, or null to stay quiet. */
export function inbound(content: { type: string; text?: unknown; url?: unknown; mimeType?: unknown; name?: unknown; read?: unknown }): Inbound | null {
  const text = inboundText(content);
  if (text !== null) return { kind: "text", text };
  if (content.type === "attachment" && typeof content.mimeType === "string" && content.mimeType.startsWith("image/") && typeof content.read === "function") {
    const read = content.read as () => Promise<Buffer | Uint8Array>;
    return {
      kind: "photo",
      mimeType: content.mimeType,
      name: typeof content.name === "string" ? content.name : undefined,
      read: async () => Buffer.from(await read()),
    };
  }
  return null;
}

/** The text to answer, or null to stay quiet (reactions, typing, read receipts...).
 *  iMessage can deliver a pasted link as a "richlink" instead of "text", so both count. */
export function inboundText(content: { type: string; text?: unknown; url?: unknown }): string | null {
  if (content.type === "text" && typeof content.text === "string") return content.text;
  if (content.type === "richlink" && typeof content.url === "string") return content.url;
  return null;
}
