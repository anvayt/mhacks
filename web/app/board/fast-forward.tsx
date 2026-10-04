"use client";

// "⏩ Fast-forward" (tasks/P2-FF-fast-forward.md): a SIMULATION of savings adding up if the commitments are kept.
// Every number is POST /simulate/fast-forward's; nothing is stored, and the real grade, rank and streak never move.
import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../lib/api";
import { errorText, kg, money } from "./api";
import boardStyles from "./board.module.css";
import styles from "./fast-forward.module.css";

type Simulation = {
  label_text: string; simulated_habit_streak: number; not_modeled: string[];
  totals: { days: number; end_date: string; usd_saved: number; kg_co2_saved: number };
  commitments: { catalog_id: string; title: string; modeled: boolean }[];
};
type Totals = { usd: number; kg: number };
const SPANS = [["1 day", 1], ["1 week", 7], ["1 month", 30]] as const;
const ZERO: Totals = { usd: 0, kg: 0 };
// One simulated day is cents, so small sums keep them.
const usd = (v: number) => (Math.abs(v) < 10 ? `$${v.toFixed(2)}` : money(v));
const kgText = (v: number) => (Math.abs(v) < 10 ? `${v.toFixed(1)} kg` : kg(v));
const longDate = (iso: string) => new Date(`${iso}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

/** Counts from the last shown totals to the new ones in 1.2 s; at once under prefers-reduced-motion. */
function useCountUp(target: Totals | null): Totals {
  const [shown, setShown] = useState<Totals>(ZERO);
  const from = useRef<Totals>(ZERO);
  useEffect(() => {
    const goal = target ?? ZERO;
    if (!target || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      from.current = goal; setShown(goal); return;
    }
    const start = from.current, t0 = performance.now();
    let frame = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / 1200), e = 1 - (1 - p) ** 3;
      const next = { usd: start.usd + (goal.usd - start.usd) * e, kg: start.kg + (goal.kg - start.kg) * e };
      from.current = next; setShown(next);
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target?.usd, target?.kg]);
  return shown;
}

export function FastForward({ sessionId, propertyId, catalogIds, ready, blocked }: {
  sessionId: string; propertyId: string | null; catalogIds: string[]; ready: boolean; blocked?: string;
}) {
  const [days, setDays] = useState<number | null>(null);
  const [result, setResult] = useState<Simulation | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const shown = useCountUp(result && { usd: result.totals.usd_saved, kg: result.totals.kg_co2_saved });
  const selection = catalogIds.join(",");
  // A different selection or home makes an old simulation stale: back to the real view.
  useEffect(() => { setDays(null); setResult(null); setError(""); }, [selection, propertyId, sessionId]);

  async function run(n: number) {
    setDays(n); setBusy(true); setError("");
    try {
      setResult(await apiFetch<Simulation>("/simulate/fast-forward", {
        body: { ...(propertyId ? { property_id: propertyId } : { session_id: sessionId }), days: n, catalog_ids: catalogIds },
      }));
    } catch (e) { setError(errorText(e)); setDays(null); } finally { setBusy(false); }
  }
  const tips = result?.commitments.filter((c) => !c.modeled).map((c) => c.title) ?? [];

  return <div className={styles.ff}>
    <h3 className="eyebrow">⏩ Fast-forward</h3>
    <div className={`choice-row ${styles.row}`} role="group" aria-label="Fast-forward the simulation">
      {SPANS.map(([label, n]) => <button key={n} type="button" className="control choice" aria-pressed={days === n} disabled={!ready || busy} onClick={() => run(n)}>{label}</button>)}
      <button type="button" className="control choice" disabled={busy || (days === null && !result)} onClick={() => { setDays(null); setResult(null); setError(""); }}>Reset</button>
    </div>
    {!ready && <p className="board-note">{blocked ?? "Pick a modeled commitment to see savings add up."}</p>}
    {ready && !result && <p className="board-note">{busy ? "Fast-forwarding…" : "Simulated · projected if you keep your commitments. Nothing is saved."}</p>}
    {error && <p role="alert" className={`${boardStyles.status} ${boardStyles.error}`}>{error}</p>}
    {result && <div className={styles.result}>
      <div className={styles.counters} aria-hidden="true">
        <p><span className={`ranking-number ${styles.number}`}>{usd(shown.usd)}</span><span className="eyebrow">saved</span></p>
        <p><span className={`ranking-number ${styles.number}`}>{kgText(shown.kg)}</span><span className="eyebrow">CO₂ avoided</span></p>
      </div>
      <p className="eyebrow">{longDate(result.totals.end_date)} · simulated</p>
      <p className={styles.streak}>Day {result.simulated_habit_streak} 🔥 (simulated)</p>
      <p className="board-note"><strong>{result.label_text}.</strong> Typical-weather days (1991–2020): a January day saves more than an October day. Your real grade, rank and streak don&apos;t change.{tips.length ? ` Not modeled (count $0): ${tips.join(", ")}.` : ""}</p>
    </div>}
    <p className={styles.srOnly} aria-live="polite">{result ? `Simulated: after ${result.totals.days} day${result.totals.days === 1 ? "" : "s"}, about ${usd(result.totals.usd_saved)} and ${kgText(result.totals.kg_co2_saved)} of CO₂ saved, projected if you keep your commitments.` : ""}</p>
  </div>;
}
