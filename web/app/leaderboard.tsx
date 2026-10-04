"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { endMove, startMove, usageHue } from "./flow-api";
import { apiFetch, ApiError, load, save } from "./lib/api";
import { BillCheck } from "./board/bill-check";
import { FastForward } from "./board/fast-forward";
import { ReminderSettings } from "./reminder-settings";
import { billRange, errorText, gradeSpan, kg, money, type Calibration, type Commitment, type Estimate, type Position, type Projection, type PublicBoard, type Snapshot, type Suggestion, type VerifiedBoard } from "./board/api";
import styles from "./board/board.module.css";
import { GradeMap } from "./grade-map";

function backgroundColorAt(position: number) {
  const mix = Math.min(1, Math.max(0, position));
  return `rgb(${[0x17, 0x3b, 0xfa].map((v, i) => Math.round(v + ([0xf2, 0x38, 0x33][i] - v) * mix)).join(", ")})`;
}
const percent = (value: number) => (value * 100).toLocaleString("en-US", { maximumFractionDigits: 1 });
const pin = (value: number) => `${Math.max(0, Math.min(100, (1 - value) * 100))}%`;
type Context = { sessionId: string; propertyId: string | null; userId: string | null; signed: boolean };

export function Leaderboard() {
  const router = useRouter();
  const [context, setContext] = useState<Context | null>(null);
  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [position, setPosition] = useState<Position | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [accepted, setAccepted] = useState<Commitment[]>([]);
  const [chosen, setChosen] = useState<string[]>([]);
  const [projection, setProjection] = useState<Projection | null>(null);
  const [publicBoard, setPublicBoard] = useState<PublicBoard | null>(null);
  const [verified, setVerified] = useState<VerifiedBoard | null>(null);
  const [targetDate, setTargetDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [optionError, setOptionError] = useState("");
  const [publicError, setPublicError] = useState("");
  const [notice, setNotice] = useState("");
  const [calendar, setCalendar] = useState<{ auth_url: string; mock: boolean; message?: string } | null>(null);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [habit, setHabit] = useState<{ current: number; best: number } | null>(null); // GET /me habit_streak, signed in only
  // The current API's projection model still uses the pre-bill session. Until it
  // supports calibrated projections, keep post-bill what-ifs out of the chart.
  const calibrated = snapshot?.source === "bill_regrade" || position?.current_source === "bill_regrade";
  const currentBill = snapshot?.bill_annual ?? estimate?.bill.building_annual ?? estimate?.bill.annual;

  async function fetchPosition(c: Context) {
    const path = c.propertyId ? `/leaderboard/position/${encodeURIComponent(c.propertyId)}` : `/leaderboard/position?session_id=${encodeURIComponent(c.sessionId)}`;
    const next = await apiFetch<Position>(path); setPosition(next); return next;
  }
  async function fetchSuggestions(c: Context) {
    setOptionError("");
    try {
      const path = c.propertyId ? `/commitments/suggested/${encodeURIComponent(c.propertyId)}` : `/commitments/suggested?session_id=${encodeURIComponent(c.sessionId)}`;
      const next = await apiFetch<{ commitments: Suggestion[] }>(path); setSuggestions(next.commitments);
    } catch (e) { setOptionError(errorText(e)); }
  }
  async function fetchPublic() {
    setPublicError("");
    const [hall, board] = await Promise.allSettled([apiFetch<PublicBoard>("/leaderboard"), apiFetch<VerifiedBoard>("/leaderboard?board=verified_cut")]);
    if (hall.status === "fulfilled") setPublicBoard(hall.value);
    if (board.status === "fulfilled") setVerified(board.value);
    setPublicError([hall, board].filter(x => x.status === "rejected").map(x => errorText((x as PromiseRejectedResult).reason)).join(" "));
  }
  async function initialize() {
    endMove(); // back on the board: a "Change address" trip that ended here is over
    setLoading(true); setError(""); setOptionError(""); setPosition(null); setProjection(null); setSnapshot(null); setSuggestions([]); setChosen([]);
    void fetchPublic();
    try {
      const query = new URLSearchParams(window.location.search);
      let sid = query.get("session_id") ?? query.get("session") ?? load("session");
      let pid = load("property"); const uid = load("user"); let signed = !!(uid && load("token"));
      type Me = { current_property_id: string | null; current_estimate?: Estimate; calendar_connected?: boolean; properties: { id: string; session_id: string }[]; habit_streak?: { current: number; best: number } };
      const me = signed ? await apiFetch<Me>(`/me/${encodeURIComponent(uid!)}`).catch(e => {
        // Expired or someone else's token: drop the stale sign-in and carry on anonymously with the stored session.
        if (!(e instanceof ApiError) || (e.status !== 401 && e.status !== 403)) throw e;
        save("token", null); save("user", null); save("property", null); signed = false; return null;
      }) : null;
      setHabit(me?.habit_streak ?? null);
      if (me) {
        setCalendarConnected(!!me.calendar_connected);
        const home = me.properties.find(p => p.id === me.current_property_id);
        // A different anonymous report must not borrow the signed home's history.
        if (home && (!sid || sid === home.session_id)) { pid = home.id; sid = home.session_id; }
        else pid = null;
        save("property", pid);
      } else pid = null;
      if (!sid) { setContext(null); return; }
      save("session", sid);
      const c = { sessionId: sid, propertyId: pid, userId: signed ? uid : null, signed };
      setContext(c);
      const e = await apiFetch<Estimate>(`/session/${encodeURIComponent(sid)}`); setEstimate(e);
      if (pid) {
        const history = await apiFetch<{ snapshots: Snapshot[]; commitments: Commitment[] }>(`/properties/${encodeURIComponent(pid)}/history`);
        const latest = history.snapshots.filter(s => !s.provisional && s.bill_annual && ["initial_estimate", "questionnaire", "bill_regrade", "manual_refresh"].includes(s.source)).sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
        setSnapshot(latest ?? null); setAccepted(history.commitments);
      } else setAccepted([]);
      await fetchPosition(c);
      await fetchSuggestions(c);
    } catch (e) { setError(errorText(e)); } finally { setLoading(false); }
  }
  useEffect(() => { void initialize(); }, []); // Loads the shared handoff once; Retry is explicit.

  async function toggle(id: string) {
    if (!context || busy || calibrated) return;
    const next = chosen.includes(id) ? chosen.filter(x => x !== id) : [...chosen, id];
    setChosen(next); setBusy("projection"); setOptionError(""); setProjection(null);
    try {
      // One model run per toggle: the ghost marker is /projection's own projected score/percentile. A saved home's
      // position only reads that stored projection (no re-run) for the same-type rank; anonymous what-ifs show no rank.
      const result = await apiFetch<Projection>("/projection", { body: { ...(context.propertyId ? { property_id: context.propertyId } : { session_id: context.sessionId }), commitment_ids: next } });
      if (context.propertyId) await fetchPosition(context);
      setProjection(next.length ? result : null);
    } catch (e) { setOptionError(errorText(e)); } finally { setBusy(""); }
  }
  async function commitChosen() {
    if (!context?.propertyId || !context.userId) return;
    setBusy("commit"); setOptionError("");
    try {
      for (const catalog_id of chosen) await apiFetch<Commitment>("/commitments", { body: { user_id: context.userId, property_id: context.propertyId, catalog_id, ...(targetDate ? { target_date: targetDate } : {}) } });
      const data = await apiFetch<{ commitments: Commitment[] }>(`/commitments?property_id=${encodeURIComponent(context.propertyId)}`);
      setAccepted(data.commitments); setNotice("Commitment saved. Your current grade stays unchanged until new evidence updates it.");
    } catch (e) { setOptionError(errorText(e)); } finally { setBusy(""); }
  }
  async function done(item: Commitment) {
    setBusy(item.id); setOptionError("");
    try {
      const next = await apiFetch<Commitment>(`/commitments/${encodeURIComponent(item.id)}`, { method: "PATCH", body: { status: "completed" } });
      setAccepted(items => items.map(c => c.id === next.id ? next : c)); setNotice("Reported done. A completed commitment is not verified savings; a later bill checks the result.");
    } catch (e) { setOptionError(errorText(e)); } finally { setBusy(""); }
  }
  async function connectCalendar() {
    if (!context?.userId) return; setBusy("calendar"); setOptionError("");
    try {
      const result = await apiFetch<{ auth_url: string; mock: boolean; message?: string }>("/calendar/connect", { body: { user_id: context.userId } });
      setCalendar(result); window.open(result.auth_url, "hidden-rent-calendar", "noopener,noreferrer");
      setNotice(result.mock ? "Demo calendar connection. No real calendar event will be created." : "Finish connecting in the new tab, then add a reminder here.");
    } catch (e) { setOptionError(errorText(e)); } finally { setBusy(""); }
  }
  async function calendarReminder(item: Commitment) {
    if (!context?.userId) return; setBusy("reminder"); setOptionError("");
    try {
      const result = await apiFetch<{ mock: boolean; message?: string }>("/calendar/reminders", { body: { user_id: context.userId, commitment_id: item.id, cadence: "once", ...(item.target_date ? { start: `${item.target_date}T18:00:00` } : {}) } });
      setNotice(result.mock ? "Demo calendar reminder saved (mock; no real event created)." : "Calendar reminder saved."); setCalendarConnected(true);
    } catch (e) { setOptionError(errorText(e)); } finally { setBusy(""); }
  }
  async function checked(result: Calibration) {
    setProjection(null); setChosen([]);
    if (result.snapshot && !result.snapshot.provisional && result.snapshot.source === "bill_regrade") setSnapshot(result.snapshot);
    if (context) {
      try { const next = await fetchPosition(context); setPosition({ ...next, projected: null }); }
      catch (e) { setError(errorText(e)); }
    }
    void fetchPublic();
  }

  const rankMismatch = !!(estimate?.bill.building_annual && snapshot && snapshot.source !== "bill_regrade" && snapshot.bill_annual.p50 !== estimate.bill.building_annual.p50);
  const current = rankMismatch ? null : position?.current;
  // A loaded position can contain an old saved ghost; only display a what-if run
  // made by this page against its current report, and never after bill regrading.
  const ghost = !calibrated && !rankMismatch && projection ? projection.projected : null;
  const percentile = ghost?.percentile_city ?? current?.percentile_city ?? .5;
  const sqft = estimate?.building.sqft;
  const sizeLabel = sqft != null ? `${sqft.toLocaleString()} sq ft` : "size unknown";
  const rows = estimate && current && currentBill ? [
    ...(sqft != null ? position!.neighbors.map((p, i) => ({ id: `peer-${i}`, annual: p.cost_per_sqft * sqft, rank: p.rank, you: false })) : []),
    { id: "you", annual: currentBill.p50, rank: current.rank, you: true },
  ].sort((a, b) => a.annual - b.annual) : [];
  const highest = Math.max(1, ...rows.map(p => p.annual));
  const heatIn = !!estimate?.bill.building_annual; // heat is in the rent: the renter's own $ is cooling only
  // Fast-forward simulates the toggled choices, plus the saved home's accepted ones when signed in.
  const ffIds = [...new Set([...(context?.propertyId ? accepted.filter(c => c.status !== "dismissed").map(c => c.catalog_id) : []), ...chosen])];
  const ffModeled = ffIds.some(id => suggestions.some(s => s.catalog_id === id && !s.pending_model && s.projected));
  return <main className={`hero ranking board-screen ${styles.screen}`} style={usageHue(percentile)}>
    <div className="hero-decor" aria-hidden="true"><img className="halo" src="/hero/halo.svg" alt="" /><img className="orbit" src="/hero/orbit.svg" alt="" /><img className="texture" src="/hero/texture.svg" alt="" /></div>
    <div className="ranking-inner">
      <p className="ranking-notice">Predicted heating + cooling · Ann Arbor city data</p>
      <section className="board">
        <h1 className="board-title">Same-type peers</h1>
        {habit && <p className="board-note">🔥 {habit.current}-day habit streak (best {habit.best})</p>}
        {loading && <p role="status">Loading your home, city rank and model-scored options…</p>}
        {error && <div role="alert" className={`${styles.status} ${styles.error}`}>{error} <button type="button" className="control choice" onClick={initialize} disabled={loading}>Retry</button> <Link href="/address">Try another address</Link></div>}
        {!loading && !context && !error && <p>Look up a home to see your predicted place. <Link href="/address">Find my hidden rent ↗</Link></p>}
        {estimate && <p className="board-note">{estimate.building.address} · {estimate.building.type} · {sizeLabel}</p>}
        {rankMismatch && estimate && <div className={styles.card}><p>Ranking is temporarily unavailable for this saved heat-included home. Its saved bill and building rank use different cost bases.</p><p>Predicted building grade {gradeSpan(estimate.grade, estimate.grade_span)} · score {estimate.score}/100. Building: {billRange(estimate.bill.building_annual!)}.</p><p className="board-note">Your bill: {billRange(estimate.bill.annual)}. {estimate.bill.note}</p></div>}
        {current && estimate && currentBill && <>
          <div className={styles.summary} aria-live="polite"><span><strong>Predicted {gradeSpan(current.grade, snapshot?.grade_span ?? estimate.grade_span)}</strong><br />Score {current.score}/100</span><span><strong>#{current.rank.toLocaleString()}</strong> of {current.of.toLocaleString()}<br />same-type city homes</span><span><strong>{percent(current.percentile_city)}%</strong><br />of all city homes cost more per sq ft</span></div>
          <p className="board-note">Building heating + cooling: {billRange(currentBill)}. {!snapshot || snapshot.source === "initial_estimate" || snapshot.source === "questionnaire" ? "P10–P90 range returned with this saved model estimate; typical-weather heating + cooling." : "Current bill range from the saved score snapshot."} {estimate.bill.note}</p>
          {heatIn && <p className="board-note">Your cooling bill (heat is in your rent): {billRange(estimate.bill.annual)}.</p>}
          {calibrated && <p className="board-note">Current monthly grade: from your bill, adjusted for weather. What-if projections are unavailable for this calibrated baseline; your current result remains visible.</p>}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 420px), 1fr))", gap: 24, alignItems: "start", width: "100%" }}>
            <ol className={`board-chart ${styles.chart}`} aria-label="Anonymized nearby ranks, annual cost at your unit size">{rows.map((p, i) => <li key={p.id} className={p.you ? "board-col you" : "board-col"}>
            <span className="board-value">{p.you ? money(p.annual) : <>≈ {money(p.annual)}<br />at your size</>}</span><span className={`board-track ${styles.track}`}><span className="board-bar" style={{ height: `${p.annual / highest * 100}%`, background: backgroundColorAt(i / Math.max(1, rows.length - 1)) }} />{p.you && ghost && <span className={styles.ghostBar} role="img" style={{ height: `${Math.min(100, (ghost.building_annual_usd ?? ghost.bill_annual.p50) / highest * 100)}%` }} aria-label={`Projected if completed: score ${ghost.score}, ${money(ghost.building_annual_usd ?? ghost.bill_annual.p50)} per year`} />}</span><span className="board-label">{p.you ? "You" : "Peer"}<br />#{p.rank.toLocaleString()}</span>
          </li>)}</ol>
            {context && <GradeMap session={context.sessionId} />}
          </div>
          {ghost && <p className="board-note">Dashed overlay: projected if completed · {money(ghost.building_annual_usd ?? ghost.bill_annual.p50)}/yr · score {ghost.score}{position?.projected?.rank != null ? ` · same-type rank #${position.projected.rank.toLocaleString()}` : ""}. Your solid bar stays fixed.</p>}
          <p className="board-note">Nearby ranks come from the API&apos;s scored city footprints of your building type. {sqft != null ? <>Peer bars scale their annual cost per sq ft to your {sizeLabel}.</> : "Peer cost bars are unavailable: size unknown."} Your bar stays at the current building estimate. If heat is included in rent, the chart still rates the building; your own bill is shown separately.</p>
          <div className={styles.rail} aria-label="Current and projected city percentiles"><span className={styles.marker} style={{ left: pin(current.percentile_city) }}>You · {percent(current.percentile_city)}%</span>{ghost && <span className={`${styles.marker} ${styles.ghost}`} style={{ left: pin(ghost.percentile_city) }}>Projected if completed<br />Score {ghost.score} · {percent(ghost.percentile_city)}%</span>}</div>
          <p className="board-note">The markers and page color use the API&apos;s percentile against all city homes. Blue is lower cost; red is higher cost. The same-type rank above stays fixed.</p>
          <details><summary>How this is calculated</summary><p className="board-note">Predicted heating + cooling from P1&apos;s model, ranked against Ann Arbor&apos;s cached city footprint scores. Rank and score compare the same building type; city percentile compares all types. Ranges express model uncertainty, not a guaranteed utility bill. {position?.model_version}</p></details>
        </>}
        {context && <section className={styles.section}>
          <h2 className="eyebrow">Commitments</h2>
          <p className="board-note">Choose a modeled option to see its projection. Completing an action does not change your current grade; a new bill checks the result.</p>
          {optionError && <p role="alert" className={`${styles.status} ${styles.error}`}>{optionError} <button type="button" onClick={() => fetchSuggestions(context)} disabled={!!busy}>Retry options</button></p>}
          <div className={styles.choices}>{suggestions.map(item => <button key={item.catalog_id} type="button" className={`control choice ${styles.choice}`} aria-pressed={chosen.includes(item.catalog_id)} disabled={item.pending_model || !item.projected || !!busy || calibrated || rankMismatch} onClick={() => toggle(item.catalog_id)}>
            <span>{item.title}</span><small>{item.who_acts}</small>
            {item.pending_model || !item.projected ? <small>Tip · savings not modeled yet</small> : <small>Projected if completed: {money(item.projected.usd_saved_yr)}/yr saved · {kg(item.projected.co2_kg_saved_yr)} CO₂/yr · {item.grh_points ?? "—"} GRH points</small>}
            {item.note && <small>{item.note}</small>}
          </button>)}</div>
          <div aria-live="polite">{busy === "projection" && <p>Re-running the model for your selected changes…</p>}{ghost && <div className={styles.card}><strong>Projected if completed: grade {ghost.grade} · score {ghost.score}/100{position?.projected?.rank != null ? ` · rank #${position.projected.rank.toLocaleString()}` : ""}</strong>{heatIn ? <><span>Your cooling bill (heat is in your rent): {billRange(ghost.bill_annual)}</span>{ghost.building_annual_usd != null && <span>Building heating + cooling: {money(ghost.building_annual_usd)}/yr</span>}</> : <span>{billRange(ghost.bill_annual)}</span>}<span>{money(projection!.delta.usd_saved_yr)}/yr {heatIn ? "off your cooling bill" : "saved"} and {kg(projection!.delta.co2_kg_saved_yr)} CO₂/yr saved</span><span className="board-note">{projection!.model_version}. Your current grade and “You” marker have not changed.</span></div>}</div>
          <FastForward sessionId={context.sessionId} propertyId={context.propertyId} catalogIds={ffIds} ready={ffModeled && !calibrated && !rankMismatch} blocked={calibrated || rankMismatch ? "Fast-forward isn't available for this home's current baseline yet." : undefined} />
          {context.propertyId && context.userId ? <><label className={styles.input}>Target date (optional)<input type="date" value={targetDate} onChange={e => setTargetDate(e.target.value)} /></label><button type="button" className="action" disabled={!chosen.length || !!busy || calibrated || rankMismatch} onClick={commitChosen}>{busy === "commit" ? "Saving…" : "Commit"}</button></> : <Link href="/signin" className="board-note">Sign in to save your commitments ↗</Link>}
          {accepted.filter(c => c.status !== "dismissed").map(item => <div className={styles.card} key={item.id}><strong>{item.title}</strong><span className="board-note">{item.status === "completed" ? "Reported done · awaiting bill evidence" : "Accepted"}{item.target_date ? ` · target ${item.target_date}` : ""}</span><div className={styles.actions}>{item.status === "accepted" && <button type="button" className="control choice" onClick={() => done(item)} disabled={!!busy}>Done</button>}{item.status === "accepted" && (calendar || calendarConnected) && <button type="button" className="control choice" onClick={() => calendarReminder(item)} disabled={!!busy}>Add calendar reminder</button>}</div></div>)}
          {!!accepted.length && context.signed && <div className={styles.actions}><button type="button" className="control choice" onClick={connectCalendar} disabled={!!busy}>Connect calendar (optional)</button>{calendar && <a href={calendar.auth_url} target="_blank" rel="noreferrer">{calendar.mock ? "Open demo calendar connection" : "Continue calendar connection"} ↗</a>}</div>}
          {notice && <p role="status" className={styles.status}>{notice}</p>}
        </section>}
        {context?.signed && <ReminderSettings />}
        {context && <section className={styles.section}>
          <h2 className="eyebrow">Current home</h2>
          <div className={styles.homeRow}><span>{estimate?.building.address ?? "Loading your home…"}</span>
            {/* Moving is the exception: back to the same address step new users start on. Nothing is cleared here; the new
                lookup becomes the session, and the grade screen saves it as the current home (POST /properties archives the old one). */}
            <button type="button" className={styles.linkButton} onClick={() => { startMove(); router.push("/address"); }}>I moved: change address</button></div>
          <h2 className="eyebrow">This month&apos;s bill</h2>
          <BillCheck key={context.sessionId} sessionId={context.sessionId} propertyId={context.propertyId} currentGrade={current ? gradeSpan(current.grade, snapshot?.grade_span ?? estimate?.grade_span) : estimate ? gradeSpan(estimate.grade, estimate.grade_span) : null} onChecked={checked} />
        </section>}
        <section className={styles.section}><h2 className="eyebrow">Hall of fame</h2><p className="board-note">Predicted scores. Names appear only for buildings in Ann Arbor&apos;s public energy benchmarking data.</p>{publicBoard && <ol className={styles.list}>{publicBoard.best.map(b => <li key={b.benchmark_id}>{b.name} · {b.grade} · score {b.score}{b.demo ? " · demo data" : ""}{b.source && <> · <a href={b.source} target="_blank" rel="noreferrer">Source ↗</a></>}</li>)}</ol>}
          <h3 className="eyebrow">Highest excess cost by block</h3>{publicBoard && <ul className={styles.list}>{publicBoard.worst_blocks.map(b => <li key={b.geoid}>{b.area_type.replaceAll("_", " ")} {b.geoid} · {b.building_count} buildings · ${b.excess_usd_per_sqft.toFixed(2)}/sq ft above type median{b.demo ? " · demo data" : ""}</li>)}</ul>}
        </section>
        <section className={styles.section}><h2 className="eyebrow">Biggest verified cut</h2>{verified?.empty_reason && <p className="board-note">{verified.empty_reason}</p>}{verified && <ol className={styles.list}>{verified.entries.map((e, i) => <li key={i}>#{e.rank} {e.alias ?? e.geoid} · {e.value}{e.unit === "percent" ? "%" : ` ${e.unit}`}{e.demo ? " · demo data" : ""}</li>)}</ol>}{verified?.metric_note && <p className="board-note">{verified.metric_note}</p>}{publicError && <p role="alert">{publicError} <button type="button" onClick={fetchPublic}>Retry city boards</button></p>}</section>
        {!context?.signed && <Link href="/signin">Sign in to save your home ↗</Link>}
      </section>
    </div>
  </main>;
}
