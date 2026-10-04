"use client";
import { useState, type FormEvent } from "react";
import { apiFetch, ApiError } from "../lib/api";
import { billRange, errorText, gradeSpan, money, type Calibration, type Fixes } from "./api";
import styles from "./board.module.css";

function lastMonth() {
  const now = new Date();
  const format = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  return { start: format(new Date(now.getFullYear(), now.getMonth() - 1, 1)), end: format(new Date(now.getFullYear(), now.getMonth(), 0)) };
}
async function jpeg(file: File): Promise<string> {
  const url = URL.createObjectURL(file);
  try {
    const img = new Image(); img.src = url;
    await img.decode().catch(() => { throw new Error("That photo could not be opened. Choose a JPEG or PNG, or type the gas usage instead."); });
    const canvas = document.createElement("canvas");
    let scale = Math.min(1, 1800 / Math.max(img.width, img.height));
    for (let attempt = 0; attempt < 5; attempt++) {
      canvas.width = Math.max(1, Math.round(img.width * scale)); canvas.height = Math.max(1, Math.round(img.height * scale));
      const ctx = canvas.getContext("2d"); if (!ctx) throw new Error("Photo conversion is unavailable. Type the gas usage instead.");
      ctx.fillStyle = "white"; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const data = canvas.toDataURL("image/jpeg", .82);
      if (data.length <= 2 * 1024 * 1024) return data;
      scale *= .72;
    }
    throw new Error("That photo is too large. Try a closer crop, or type the gas usage instead.");
  } finally { URL.revokeObjectURL(url); }
}
export function BillCheck({ sessionId, propertyId, onChecked }: { sessionId: string; propertyId: string | null; onChecked: (result: Calibration) => Promise<void> }) {
  const [mode, setMode] = useState<"therms" | "ccf" | "amount">("therms");
  const [usage, setUsage] = useState(""); const [kwh, setKwh] = useState("");
  const [dates, setDates] = useState(lastMonth); const [photo, setPhoto] = useState<string | null>(null);
  const [photoName, setPhotoName] = useState(""); const [readingPhoto, setReadingPhoto] = useState(false);
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const [result, setResult] = useState<Calibration | null>(null); const [amountResult, setAmountResult] = useState(false);
  const [fixes, setFixes] = useState<Fixes | null>(null); const [fixError, setFixError] = useState(""); const [copied, setCopied] = useState(false);
  async function loadFixes() { setFixError(""); try { setFixes(await apiFetch<Fixes>(`/fixes/${encodeURIComponent(sessionId)}`)); } catch (e) { setFixError(errorText(e)); } }
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setFixes(null); setResult(null);
    try {
      const input = photo ? { bill_image_base64: photo } : mode === "amount" ? { amount_usd: Number(usage) } : { therms: Number(usage), gas_unit: mode };
      const checked = await apiFetch<Calibration>("/calibrate", { body: { session_id: sessionId, ...(propertyId ? { property_id: propertyId } : {}), ...input, ...dates, ...(kwh ? { kwh: Number(kwh) } : {}) } });
      setResult(checked); setAmountResult(!photo && mode === "amount");
      await onChecked(checked); await loadFixes();
    } catch (e) {
      const typing = e instanceof ApiError && ["unreadable_bill", "bad_bill", "vision_unavailable"].includes(e.code);
      setError(errorText(e) + (typing ? " You can remove the photo and type the gas usage and dates instead." : ""));
    } finally { setBusy(false); }
  }
  const email = typeof fixes?.landlord_email === "string" ? fixes.landlord_email : fixes?.landlord_email ? [fixes.landlord_email.subject, fixes.landlord_email.body].filter(Boolean).join("\n\n") : "";
  return <section className={styles.section} aria-label="Monthly bill check">
    <form onSubmit={submit} className={styles.section}>
      <label className="eyebrow" htmlFor="gas-usage">Gas used this month (therms or ccf, on your DTE bill)</label>
      <div className="choice-row">{(["therms", "ccf", "amount"] as const).map(m => <button className="control choice" type="button" key={m} aria-pressed={mode === m} onClick={() => setMode(m)}>{m === "amount" ? "$ amount instead" : m}</button>)}</div>
      {mode === "amount" && <p className="board-note">Estimated from your bill amount. Exact therms or ccf give a better check; fixed charges and other services can affect the estimate.</p>}
      <div className={styles.grid}>
        <label className={styles.input}>{mode === "amount" ? "Gas bill amount ($)" : `Gas usage (${mode})`}<input id="gas-usage" type="number" inputMode="decimal" min="0.01" step="any" required={!photo} disabled={!!photo} value={usage} onChange={e => setUsage(e.target.value)} /></label>
        <label className={styles.input}>Electricity kWh (optional; stored, not compared)<input type="number" inputMode="decimal" min="0" step="any" value={kwh} onChange={e => setKwh(e.target.value)} /></label>
        <label className={styles.input}>Billing start<input type="date" required value={dates.start} onChange={e => setDates({ ...dates, start: e.target.value })} /></label>
        <label className={styles.input}>Billing end<input type="date" required min={dates.start} value={dates.end} onChange={e => setDates({ ...dates, end: e.target.value })} /></label>
      </div>
      <label className={styles.input}>Optional bill photo<input type="file" accept="image/*" disabled={busy || readingPhoto} onChange={async e => {
        const file = e.target.files?.[0]; if (!file) return; setReadingPhoto(true); setError(""); setPhoto(null);
        try { setPhoto(await jpeg(file)); setPhotoName(file.name); } catch (err) { setError(errorText(err)); } finally { setReadingPhoto(false); e.target.value = ""; }
      }} /></label>
      {readingPhoto && <p role="status">Preparing a smaller JPEG…</p>}
      {photo && <div className={styles.actions}><span className="board-note">Photo ready: {photoName}. Converted to JPEG under 2 MB. The API reads the usage and dates.</span><button type="button" className="control choice" onClick={() => setPhoto(null)}>Remove photo</button></div>}
      <button type="submit" className="action" disabled={busy || readingPhoto}>{busy ? "Checking your bill…" : "Check my bill"}</button>
    </form>
    {error && <p role="alert" className={`${styles.status} ${styles.error}`}>{error}</p>}
    <div aria-live="polite">{result && <div className={styles.section}>
      <p><strong>{Math.abs(result.pct_vs_expected_for_weather).toLocaleString("en-US", { maximumFractionDigits: 1 })}% {result.pct_vs_expected_for_weather < 0 ? "below" : "above"} normal for this weather</strong></p>
      <p>{result.streak_months} months in a row below normal 🔥</p>
      {amountResult && <p className="board-note">Estimated from your bill amount.</p>}
      <p className="board-note">{result.verified ? "Verified gas reduction." : "Early signal, not verified savings."} {result.note}</p>
      {result.impact && <p>{result.impact.co2_kg_avoided.toLocaleString()} kg CO₂ avoided · {money(result.impact.usd_saved)} saved in this verified period.</p>}
      {!!result.badges?.length && <p>Badges: {result.badges.map(b => b.replaceAll("-", " ")).join(" · ")}</p>}
      {result.snapshot?.source === "bill_regrade" && <p><strong>{result.snapshot.provisional ? "Provisional bill signal" : "Monthly grade"} {gradeSpan(result.snapshot.grade, result.snapshot.grade_span)}</strong> · {result.snapshot.label ?? (result.snapshot.provisional ? "Early signal; current grade unchanged" : "from your bill, adjusted for weather")}<br />{billRange(result.snapshot.bill_annual)}{result.snapshot.provisional && <><br />Your current grade and rank stay unchanged.</>}</p>}
      {!result.snapshot && <p className="board-note">Your predicted grade stays unchanged. Sign in to save this home and its monthly bill history.</p>}
    </div>}</div>
    {fixError && <p role="alert">Fixes: {fixError} <button type="button" onClick={loadFixes}>Retry fixes</button></p>}
    {fixes && <section className={styles.section}><h2 className="eyebrow">Fixes for this home</h2><ul className={styles.list}>{fixes.fixes.map(f => <li key={f.item}>{f.item} · {f.grh_points} GRH points{!f.unpriced && f.usd_saved_yr != null && f.co2_kg_saved != null ? ` · projected ${money(f.usd_saved_yr)}/yr and ${Math.round(f.co2_kg_saved)} kg CO₂/yr saved` : " · tip; savings not modeled"}</li>)}</ul>
      {email && <><h3 className="eyebrow">Landlord email draft</h3><pre className={styles.email}>{email}</pre><button className="control choice" type="button" onClick={async () => { try { await navigator.clipboard.writeText(email); setCopied(true); } catch { setFixError("Copy is unavailable. Select the draft text and copy it."); } }}>{copied ? "Copied" : "Copy email draft"}</button></>}
    </section>}
  </section>;
}
