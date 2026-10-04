import type { Calibration, FastForward, Projection, Suggestion } from "./api.ts";
import { calibrationText } from "./replies.ts";
const money = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;
const num = (n: number) => Math.round(n).toLocaleString("en-US");
// Small simulated sums keep their cents / tenths, so one day never reads "$0".
const smallMoney = (n: number) => (Math.abs(n) < 10 ? `$${n.toFixed(2)}` : money(n));
const smallNum = (n: number) => (Math.abs(n) < 10 ? n.toFixed(1) : num(n));

/** POST /simulate/fast-forward, worded as a simulation; every number is the API's. */
export function fastForwardText(f: FastForward): string {
  const kept = f.commitments.filter((c) => c.modeled).map((c) => c.title[0].toLowerCase() + c.title.slice(1));
  if (!kept.length) return 'Nothing to fast-forward yet: none of your commitments has modeled savings. Say "options" and pick one with numbers.';
  const what = `your commitment${kept.length > 1 ? "s" : ""} to ${kept.length > 1 ? `${kept.slice(0, -1).join(", ")} and ${kept.at(-1)}` : kept[0]}`;
  const days = `${f.totals.days} day${f.totals.days === 1 ? "" : "s"}`;
  return `Simulation, not real usage: if you keep ${what}, in ${days} you'd save about ${smallMoney(f.totals.usd_saved)} and ${smallNum(f.totals.kg_co2_saved)} kg CO₂ (projected). Your real streak stays ${f.real_habit_streak}.`;
}

export function suggestionsText(items: Suggestion[]): string {
  if (!items.length) return "No commitments are available for this home yet.";
  return ["Your options (effects are projected if completed):", ...items.map((x, i) => {
    const head = `${i + 1}) ${x.title} — ${x.who_acts}`;
    // A placeholder never borrows numbers from the catalog, even if a malformed body supplies them.
    if (x.pending_model || !x.projected) return `${head}. Tip only; this model can't price its effect here.${x.note ? `\n${x.note}` : ""}`;
    const p = x.projected;
    const figures = [p.usd_saved_yr == null ? "" : `${money(p.usd_saved_yr)}/yr less`, p.co2_kg_saved_yr == null ? "" : `${num(p.co2_kg_saved_yr)} kg CO₂/yr less`, x.grh_points == null ? "" : `${x.grh_points} GRH points`].filter(Boolean);
    return `${head}${figures.length ? `: ${figures.join(", ")}` : ""}.${x.note ? `\n${x.note}` : ""}`;
  }), 'Reply "do 1" or "do 1 and 3"; add "by YYYY-MM-DD" for a target date. Tips can be accepted but are excluded from the projection.'].join("\n");
}

export function projectionText(p: Projection): string {
  if (p.label !== "projected_if_completed" || p.projected.label !== "projected_if_completed") return "Your commitments are saved. Their projected effect isn't available yet.";
  if (!p.modeled.length) return "Saved as tips. The model can't price these commitments here, so there is no projected grade or saving.";
  const figures = [p.delta.usd_saved_yr == null ? "" : `${money(p.delta.usd_saved_yr)}/yr less`, p.delta.co2_kg_saved_yr == null ? "" : `${num(p.delta.co2_kg_saved_yr)} kg CO₂/yr less`].filter(Boolean);
  return `Projected if completed: grade ${p.projected.grade} (current grade ${p.current.grade})${figures.length ? `, about ${figures.join(" and ")}` : ""}. Your current grade hasn't changed.${p.not_modeled.length ? " Tips without modeled effects are excluded." : ""}`;
}

export function billResultText(c: Calibration, currentGrade?: string | null): string {
  const lines = [calibrationText(c)];
  if (c.extracted?.estimated_from_amount) lines.push(c.extracted.note ?? "Gas usage was estimated from your bill amount.");
  if (c.snapshot?.provisional && c.bill_signal) {
    lines.push(`This bill suggests grade ${c.bill_signal.grade}, but one bill is inside normal month-to-month variation, so ${currentGrade ? `your grade stays ${currentGrade}` : "your current grade doesn't change"}. Early signal only.`);
  } else if (c.snapshot?.source === "bill_regrade" && c.snapshot.provisional === false) {
    lines.push(`Current grade ${c.snapshot.grade} — from your bill, adjusted for weather.`);
  }
  if (c.verified === false) lines.push("This is not a verified reduction. Reported work needs a full later billing period beyond the model's error.");
  if (c.verified === true) lines.push("The API verified a weather-adjusted reduction for this home.");
  return lines.join("\n");
}
