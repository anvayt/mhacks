"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { currentEstimate, gradeStatus, usd, usdRange, type Estimate } from "./flow-api";
import { ApiError } from "./lib/api";
import styles from "./ranking-screen.module.css";

const pct = (x: number) => Math.round(x * 100);

/** "Top 6%" / "Bottom 3%" of every scored Ann Arbor home (percentile_city = share this home beats). */
function cityRank(p: number): { head: string; sub: string } {
  return p >= 0.5
    ? { head: `Top ${Math.max(1, 100 - pct(p))}%`, sub: "Most efficient in Ann Arbor." }
    : { head: `Bottom ${Math.max(1, pct(p))}%`, sub: "Least efficient in Ann Arbor." };
}

/** "built 1970 (Ann Arbor benchmarking)", or "built around 1964 (neighborhood median)" for a census median. */
function built(b: Estimate["building"]): string | null {
  if (b.year_built == null) return null;
  return /median/i.test(b.year_built_source ?? "")
    ? `Built around ${b.year_built} (neighborhood median)`
    : `Built ${b.year_built}${b.year_built_source ? ` (${b.year_built_source})` : ""}`;
}

export function RankingScreen({ onNext }: { onNext: () => void }) {
  const [nextReady, setNextReady] = useState(false);
  const [e, setE] = useState<Estimate | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    currentEstimate()
      .then(setE)
      .catch((err: ApiError) => setError(err.message));
    const enable = window.setTimeout(() => setNextReady(true), 5400);
    return () => window.clearTimeout(enable);
  }, []);

  const b = e?.building;
  const rank = e?.percentile_city != null ? cityRank(e.percentile_city) : null;
  const range = e ? usdRange(e.bill.annual) : null;
  const co2 = e?.co2_t?.p50 != null ? e.co2_t : null;
  const hidden = e?.hidden_rent_usd_mo;
  const session = encodeURIComponent(e?.session_id ?? "");

  return (
    <main className={`hero ranking reveal ${styles.screen}`}>
      <div className="hero-decor" aria-hidden="true">
        <img className="halo" src="/hero/halo.svg" alt="" />
        <img className="orbit" src="/hero/orbit.svg" alt="" />
        <img className="texture" src="/hero/texture.svg" alt="" />
      </div>
      <div className="ranking-inner">
        <header className="ranking-toolbar">
          <p>Rental dossier / Ann Arbor, Michigan / {b?.address ?? "No listing supplied"}</p>
          {e ? (
            <div className="ranking-actions">
              <Link className="ghost-action" href={`/compare?a=${session}`}>
                Compare listing
                <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
              </Link>
              <Link className="ghost-action" href={`/share?session=${session}`}>
                Share preview
                <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
              </Link>
            </div>
          ) : null}
        </header>
        <p className="ranking-notice" aria-live="polite">
          {error ? (
            <>
              {error} <Link href="/address">Enter an address</Link>
            </>
          ) : e ? (
            "Predicted from city records and your answers · heating + cooling only · not a measured bill"
          ) : (
            "Loading your grade…"
          )}
        </p>
        {e ? (
          <section className="ranking-body" aria-live="polite">
            <div className="ranking-copy score-reveal">
              {rank ? (
                <>
                  <h1>{rank.head}</h1>
                  <p className="ranking-subhead">{rank.sub}</p>
                </>
              ) : null}
              {e.percentile_peers != null ? (
                <p className="ranking-detail">
                  More efficient than {pct(e.percentile_peers)}% of same-type homes ({b?.type ?? "same building type"}).
                </p>
              ) : null}
              {range ? (
                <p className="ranking-detail">
                  Heating + cooling: {range} a year
                  {e.bill.annual.p10 != null && e.bill.annual.p50 != null ? `, most likely ${usd(e.bill.annual.p50)}` : ""}.
                </p>
              ) : null}
              {hidden != null ? (
                <p className="ranking-detail">
                  {hidden >= 0
                    ? `+${usd(hidden)}/mo hidden rent vs a typical same-size unit.`
                    : `${usd(-hidden)}/mo less than a typical same-size unit.`}
                </p>
              ) : null}
              {e.bill.note ? <p className="ranking-detail">{e.bill.note}</p> : null}
              <p className="ranking-source">
                {[
                  b?.type && b.sqft != null
                    ? `${b.type}, ${Math.round(b.sqft).toLocaleString("en-US")} sq ft${b.sqft_estimated ? " (estimated)" : ""}`
                    : null,
                  b && built(b),
                  "Ranked against scored Ann Arbor homes",
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            </div>
            <aside className="ranking-card score-reveal score-reveal-late">
              <p className="eyebrow">Predicted score</p>
              <div className="ranking-score">
                <p className="ranking-number">{e.score ?? "—"}</p>
                <p className="ranking-grade">{e.grade ?? "—"}</p>
              </div>
              <div className="ranking-score-labels">
                <p>Out of 100</p>
                <p>{gradeStatus(e)}</p>
              </div>
              <div className="ranking-rule" />
              {co2 ? (
                <p className="ranking-awaiting">
                  CO₂: about {co2.p50!.toFixed(1)} t a year
                  {co2.p10 != null && co2.p90 != null ? ` (${co2.p10.toFixed(1)}–${co2.p90.toFixed(1)})` : ""}
                </p>
              ) : null}
              {e.badges.length ? (
                <p className="ranking-awaiting">🏅 {e.badges.map((x) => x.replace(/-/g, " ")).join(", ")}</p>
              ) : null}
            </aside>
          </section>
        ) : null}
        <button className="ghost-action ranking-next" type="button" disabled={!nextReady || !e} onClick={onNext}>
          Next
          <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
        </button>
      </div>
    </main>
  );
}
