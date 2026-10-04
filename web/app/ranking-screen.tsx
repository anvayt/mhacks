"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  adoptSession,
  billCovers,
  currentEstimate,
  errorText,
  gradeStatus,
  gradeText,
  imessageUrl,
  sessionIsHome,
  usd,
  usageHue,
  usdRange,
  type Estimate,
} from "./flow-api";
import { ApiError, save } from "./lib/api";
import styles from "./ranking-screen.module.css";
import { ScoreBoost } from "./score-boost";

const pct = (x: number) => Math.round(x * 100);

/** P3's bands on percentile_city (the share of scored Ann Arbor homes this one beats). */
function cityRank(p: number): { head: string; sub: string } {
  if (p >= 0.75) return { head: `Top ${Math.max(1, 100 - pct(p))}%`, sub: "Most efficient in Ann Arbor." };
  if (p < 0.25) return { head: `Bottom ${Math.max(1, pct(p))}%`, sub: "Least efficient in Ann Arbor." };
  return { head: "Middle 50%", sub: "Right in the middle of the spectrum." };
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
  // Signed in and this isn't the saved home yet: offer to save it (it replaces the old home, so only on a click).
  const [home, setHome] = useState<"hidden" | "offer" | "saving" | "saved">("hidden");
  const [homeNote, setHomeNote] = useState<string | null>(null);

  useEffect(() => {
    currentEstimate()
      .then((est) => {
        setE(est);
        sessionIsHome()
          .then((is) => setHome(is === false ? "offer" : "hidden"))
          .catch((err) => {
            if (err instanceof ApiError && err.status === 401) {
              save("token", null); // expired login: the grade works without it
              save("user", null);
            }
          });
      })
      .catch((err) => setError(errorText(err)));
    const enable = window.setTimeout(() => setNextReady(true), 5400);
    return () => window.clearTimeout(enable);
  }, []);

  async function saveHome() {
    setHome("saving");
    setHomeNote(null);
    try {
      await adoptSession();
      setHome("saved");
    } catch (err) {
      setHome("offer");
      setHomeNote(`This home wasn't saved: ${errorText(err)}`);
    }
  }

  const b = e?.building;
  const rank = e?.percentile_city != null ? cityRank(e.percentile_city) : null;
  const range = e ? usdRange(e.bill.annual) : null;
  const co2 = e?.co2_t?.p50 != null ? e.co2_t : null;
  const hidden = e?.hidden_rent_usd_mo;
  const session = encodeURIComponent(e?.session_id ?? "");

  return (
    <main className={`hero ranking reveal board-screen ${styles.screen}`} style={usageHue(e?.percentile_city)}>
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
              <Link className="ghost-action" href={`/watch?session=${session}`}>
                Watch your report
                <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
              </Link>
              <a className="ghost-action" href={imessageUrl(session)}>
                Continue in iMessage
                <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
              </a>
              {home !== "hidden" ? (
                <button className="ghost-action" type="button" disabled={home !== "offer"} onClick={saveHome}>
                  {home === "saved" ? "Saved as your home ✓" : home === "saving" ? "Saving…" : "Save this as my home"}
                </button>
              ) : null}
            </div>
          ) : null}
        </header>
        {homeNote ? (
          <p className="ranking-notice" role="status">
            {homeNote}
          </p>
        ) : null}
        <p className="ranking-notice" aria-live="polite">
          {error ? (
            <>
              {error} <Link href="/address">Enter an address</Link>
            </>
          ) : e ? (
            `Predicted from city records and your answers · ${billCovers(e)} only · not a measured bill`
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
                  More efficient than {Math.min(99, pct(e.percentile_peers))}% of same-type homes ({b?.type ?? "same building type"}).
                </p>
              ) : null}
              {range ? (
                <p className="ranking-detail">
                  {e.bill.building_annual ? "You pay for cooling" : "Heating + cooling"}: {range} a year
                  {e.bill.annual.p10 != null && e.bill.annual.p50 != null ? `, most likely ${usd(e.bill.annual.p50)}` : ""}.
                </p>
              ) : null}
              {usdRange(e.bill.building_annual) ? (
                <p className="ranking-detail">
                  The building&apos;s heating + cooling, which the grade rates: {usdRange(e.bill.building_annual)} a year.
                </p>
              ) : null}
              {hidden != null ? (
                <p className="ranking-detail">
                  {hidden >= 0 ? `+${usd(hidden)}/mo hidden rent vs` : `${usd(-hidden)}/mo less than`} a typical same-size
                  unit{e.bill.building_annual ? " (cooling only)" : ""}.
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
                <p className="ranking-grade">{gradeText(e)}</p>
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
        {e ? <ScoreBoost session={e.session_id} /> : null}
        <button className="ghost-action ranking-next" type="button" disabled={!nextReady || !e} onClick={onNext}>
          Next
          <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
        </button>
      </div>
    </main>
  );
}
