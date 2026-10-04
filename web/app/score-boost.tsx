"use client";

// Grade screen: "Raise your score" (what to change, the projected effect, and why) + "Stay on track" (text opt-in).
// Reads only existing anonymous-by-session API routes, so it needs no backend change and nothing is stored:
//   GET /commitments/suggested?session_id=…   ranked actions with each one's projected score/grade/$/CO₂
//   POST /projection {session_id, commitment_ids}   one composed what-if for the selected actions
//   GET /me/{user_id} (signed in only)   current reminder settings
import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, apiFetch, load } from "./lib/api";
import styles from "./board/board.module.css";

type Suggestion = {
  catalog_id: string;
  title: string;
  who_acts: string;
  pending_model: boolean;
  grh_points?: number | null;
  grh_item?: string | null;
  note?: string;
  projected: { usd_saved_yr: number; co2_kg_saved_yr: number; score_delta: number; new_grade: string; label: string } | null;
};
type Side = { score: number; grade: string; percentile_city?: number | null; building_annual_usd?: number };
type Projection = {
  current: Side;
  projected: Side & { label: string };
  delta: { score: number; usd_saved_yr: number; co2_kg_saved_yr: number; building_heating_usd_saved_yr: number; building_cooling_usd_saved_yr: number };
  modeled: string[];
  not_modeled: string[];
};
type Prefs = { channel: string; cadence: string; hour_local: number; paused: boolean };

const SHOW = 3; // the top modeled actions, ranked by the API (CO₂ avoided per net dollar)
const money = (n: number) => `$${Math.round(Math.abs(n)).toLocaleString("en-US")}`;
const kg = (n: number) => `${Math.round(n).toLocaleString("en-US")} kg`;
const OUTAGE: Record<string, string> = {
  model_unavailable: "Our cost model is starting up, so we can't price changes right now. Try again in a minute.",
  not_found: "This report expired. Look up the address again to see what would raise your score.",
};
const message = (err: unknown) =>
  err instanceof ApiError ? OUTAGE[err.code] ?? err.message : "Something went wrong. Try again.";
const who = (w: string) => (w === "renter" ? "You can do this" : w === "landlord" ? "Ask your landlord" : "You start it; your landlord does it");

/** Plain-words reason: the score ranks the building's heating + cooling cost per sq ft against same-type homes. */
function why(p: Projection): string {
  const parts: string[] = [];
  const h = p.delta.building_heating_usd_saved_yr, c = p.delta.building_cooling_usd_saved_yr;
  if (h) parts.push(`heating ${h > 0 ? "drops" : "rises"} by ${money(h)}`);
  if (c) parts.push(`cooling ${c > 0 ? "drops" : "rises"} by ${money(c)}`);
  const change = parts.length ? `Our model re-ran your home with these changes: ${parts.join(" and ")} a year.` : "";
  return `${change} Your score ranks this home's heating + cooling cost per square foot against same-type Ann Arbor homes, so a lower cost moves you up the ranking.`.trim();
}

export function ScoreBoost({ session }: { session: string | null }) {
  const [items, setItems] = useState<Suggestion[] | null>(null);
  const [chosen, setChosen] = useState<string[]>([]);
  const [projection, setProjection] = useState<Projection | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    apiFetch<{ commitments: Suggestion[] }>(`/commitments/suggested?session_id=${encodeURIComponent(session)}`)
      .then((r) => setItems(r.commitments))
      .catch((err) => setError(message(err)));
  }, [session]);

  useEffect(() => {
    if (!session || !chosen.length) return setProjection(null);
    let live = true;
    setBusy(true);
    setError(null);
    apiFetch<Projection>("/projection", { body: { session_id: session, commitment_ids: chosen } })
      .then((p) => live && setProjection(p))
      .catch((err) => live && setError(message(err)))
      .finally(() => live && setBusy(false));
    return () => {
      live = false;
    };
  }, [session, chosen]);

  if (!session) return null;
  const modeled = (items ?? []).filter((s) => s.projected && !s.pending_model && s.projected.score_delta > 0).slice(0, SHOW);
  const tips = (items ?? []).filter((s) => !s.projected || s.pending_model).slice(0, 2);
  const toggle = (id: string) => setChosen((c) => (c.includes(id) ? c.filter((x) => x !== id) : [...c, id]));

  return (
    <section className="board" aria-labelledby="boost-heading" style={{ marginTop: 24 }}>
      <p className="eyebrow">What would change it</p>
      <h2 className="board-title" id="boost-heading">Raise your score</h2>
      {!items && !error && <p role="status" className="board-note">Running our model on changes for this home…</p>}
      {items && !modeled.length && (
        <p className="board-note">None of the changes we can model would raise this home&apos;s score. The tips below can still lower your bill.</p>
      )}
      {!!modeled.length && (
        <>
          <p className="board-note">Pick one or more to see the projected effect. Projected only: your current score stays until a real bill shows the change.</p>
          <div className={styles.choices}>
            {modeled.map((s) => (
              <button key={s.catalog_id} type="button" className={`control choice ${styles.choice}`} aria-pressed={chosen.includes(s.catalog_id)}
                disabled={busy} onClick={() => toggle(s.catalog_id)}>
                <span>{s.title}</span>
                <small>{who(s.who_acts)}</small>
                <small>
                  Score +{s.projected!.score_delta.toFixed(0)} → grade {s.projected!.new_grade} · {money(s.projected!.usd_saved_yr)}/yr ·{" "}
                  {kg(s.projected!.co2_kg_saved_yr)} CO₂/yr{s.grh_points ? ` · +${s.grh_points} Green Rental Housing points` : ""}
                </small>
              </button>
            ))}
          </div>
        </>
      )}
      <div aria-live="polite">
        {busy && <p className="board-note">Re-running the model for your selection…</p>}
        {projection && !busy && (
          <div className={styles.card}>
            <strong>
              Projected if completed: score {projection.current.score.toFixed(0)} → {projection.projected.score.toFixed(0)}
              {projection.current.grade !== projection.projected.grade ? ` (grade ${projection.current.grade} → ${projection.projected.grade})` : ` (grade ${projection.projected.grade})`}
            </strong>
            <span>
              {money(projection.delta.usd_saved_yr)}/yr {projection.delta.usd_saved_yr >= 0 ? "saved" : "more"} · {kg(projection.delta.co2_kg_saved_yr)} CO₂/yr avoided
            </span>
            <span className="board-note">
              <strong>Why:</strong> {why(projection)}
            </span>
            {projection.not_modeled.length > 0 && (
              <span className="board-note">Not modeled yet, so not counted: {projection.not_modeled.length} of your picks.</span>
            )}
          </div>
        )}
      </div>
      {!!tips.length && (
        <ul className="board-note" style={{ margin: 0, paddingLeft: 20, lineHeight: 1.7 }}>
          {tips.map((t) => (
            <li key={t.catalog_id}>
              {t.title} <span style={{ opacity: 0.75 }}>(tip: savings not modeled yet)</span>
              {t.note ? <> · {t.note}</> : null}
            </li>
          ))}
        </ul>
      )}
      {error && <p role="alert" className={`${styles.status} ${styles.error}`}>{error}</p>}
      <StayOnTrack />
    </section>
  );
}

/** The text opt-in: signed-out → sign up (and back here); signed-in → current reminder state + where to change it. */
function StayOnTrack() {
  const userId = load("user");
  const signedIn = !!(userId && load("token"));
  const [prefs, setPrefs] = useState<Prefs | null>(null);

  useEffect(() => {
    if (!signedIn) return;
    apiFetch<{ reminder_prefs: Prefs }>(`/me/${encodeURIComponent(userId!)}`)
      .then((me) => setPrefs(me.reminder_prefs))
      .catch(() => setPrefs(null));
  }, [signedIn, userId]);

  const on = prefs && prefs.cadence !== "off" && prefs.channel !== "none" && !prefs.paused;
  return (
    <div className={styles.section}>
      <p className="eyebrow">Stay on track</p>
      {!signedIn ? (
        <>
          <p className="board-note">
            Want a monthly text check-in? We&apos;ll ask if you still live here and check your bill against the weather, so you can see
            whether these changes actually worked. Only if you say yes; at most one text a day; reply STOP anytime.
          </p>
          <div className={styles.actions}>
            <Link className="action" href="/signin?next=/grade" style={{ textDecoration: "none" }}>
              Sign up for check-ins
              <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
            </Link>
          </div>
        </>
      ) : (
        <p className="board-note">
          {prefs == null
            ? "Text check-ins: loading…"
            : on
              ? `Text check-ins are on: ${prefs.cadence}, around ${prefs.hour_local % 12 === 0 ? 12 : prefs.hour_local % 12} ${prefs.hour_local < 12 ? "AM" : "PM"}.`
              : prefs.paused
                ? "Text check-ins are paused."
                : "Text check-ins are off."}{" "}
          <Link href="/board">{on ? "Change" : "Turn them on"} on your board ↗</Link>
        </p>
      )}
    </div>
  );
}
