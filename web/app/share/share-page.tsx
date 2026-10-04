"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { load } from "@/app/lib/api";
import { getSession, gradeLabel, annualRange, billLabel, buildingLine, money, hiddenRent, carbon, peerLabel, type Estimate } from "@/components/hidden-rent-map/estimate-data";
import { qrMatrix } from "./qr";
import { shareImage } from "./share-image";
import styles from "./share.module.css";

export default function SharePage() {
  const param = useSearchParams().get("session");
  const [stored,setStored] = useState<string | null>();
  useEffect(() => { if (!param) setStored(load("session")); }, [param]);
  const session = param ?? stored; // undefined while the saved session loads
  const [estimate,setEstimate] = useState<Estimate | null>(null);
  const [error,setError] = useState("");
  const [status,setStatus] = useState("");
  const [busy,setBusy] = useState(false);
  const [attempt,retry] = useState(0);
  const [origin,setOrigin] = useState("");
  const [canShare,setCanShare] = useState(false);
  useEffect(() => { setOrigin(window.location.origin); setCanShare(!!navigator.share); }, []);
  useEffect(() => {
    if (!session) return;
    let active = true; setEstimate(null); setError("");
    getSession(session).then((e) => { if(active) setEstimate(e); }).catch((e) => { if(active) setError(e.message); });
    return () => { active = false; };
  }, [session,attempt]);
  const qr = useMemo(() => origin ? qrMatrix(origin) : null, [origin]);
  async function exportCard(share = false) {
    if (!estimate || !origin) return;
    setBusy(true); setStatus("");
    try {
      const blob = await shareImage(estimate,origin);
      const file = new File([blob],"hidden-rent-dossier.png",{type:"image/png"});
      if (share && navigator.share) {
        if (navigator.canShare?.({files:[file]})) await navigator.share({title:"My Hidden Rent dossier",text:"Predicted heating + cooling. Check your place.",files:[file]});
        else await navigator.share({title:"My Hidden Rent dossier",text:"Check the heating + cooling hidden in your next home.",url:origin});
        setStatus("Share sheet opened.");
      } else {
        const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href=url; a.download=file.name; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
        setStatus("PNG downloaded. Your card includes a scannable check-yours link.");
      }
    } catch (e) { if (!(e instanceof Error && e.name === "AbortError")) setStatus(e instanceof Error ? e.message : "Sharing failed. Try downloading the PNG."); }
    finally { setBusy(false); }
  }
  return <main className={styles.page}>
    <nav className={styles.nav}><Link href="/">Hidden Rent ↗</Link><span>Your rental dossier / Share</span>{session && <Link href={`/map?session=${encodeURIComponent(session)}`}>Explore the map ↗</Link>}</nav>
    <header className={styles.header}><p>THE BILL BEHIND THE LISTING.</p><h1>Make the<br /><em>hidden visible.</em></h1></header>
    {session === null ? <div className={styles.notice}>Check a listing first to create a real share card. <Link href="/">Check your place ↗</Link></div> : error ? <div className={styles.notice} role="alert"><p>{error}</p><button onClick={() => retry(attempt + 1)}>Try again</button> <Link href="/">Check another listing ↗</Link></div> : !estimate ? <div className={styles.notice} role="status">Loading your saved estimate…</div> : <>
      <article className={styles.card} aria-label="Shareable predicted energy dossier">
        <div className={styles.cardTop}><strong>HIDDEN RENT</strong><span>ANN ARBOR, MI</span></div>
        <p className={styles.eyebrow}>{billLabel(estimate)}</p><h2>{estimate.building.address}</h2>
        <strong className={styles.grade}>{gradeLabel(estimate)}</strong>
        <p className={styles.gradeNote}>{estimate.locked === false ? `Point grade ${estimate.grade} · your answers can still change the grade` : "Your predicted efficiency grade"}</p>
        <p className={styles.percentile}>{peerLabel(estimate)}</p>
        <div className={styles.bill}><strong>{money(estimate.bill.annual.p50)}<span>/year</span></strong><p>{annualRange(estimate)} · estimated range</p>{buildingLine(estimate) && <p>{buildingLine(estimate)}</p>}</div>
        <dl className={styles.stats}><div><dt>Hidden rent vs same-type median</dt><dd>{hiddenRent(estimate)}</dd></div><div><dt>Predicted carbon</dt><dd>{carbon(estimate)}</dd></div></dl>
        {estimate.bill.note && <p className={styles.billNote}>{estimate.bill.note}</p>}
        <div className={styles.qrRow}><div><h3>Check yours ↗</h3><p>{origin.replace(/^https?:\/\//,"")}</p><p>Typical weather. Not a bill.<br />Rent + other utilities excluded.</p></div>{qr && <a href={origin} aria-label="Check your place"><svg role="img" aria-label={`QR code linking to ${origin}`} viewBox={`0 0 ${qr.size} ${qr.size}`} className={styles.qr} shapeRendering="crispEdges"><rect width={qr.size} height={qr.size} fill="white" /><path fill="#11121a" d={qr.cells.map(([x,y]) => `M${x} ${y}h1v1h-1z`).join("")} /></svg></a>}</div>
      </article>
      <div className={styles.actions}><button onClick={() => exportCard()} disabled={busy}>{busy ? "Preparing card…" : "Download PNG ↓"}</button>{canShare && <button onClick={() => exportCard(true)} disabled={busy}>Share card ↗</button>}</div>
      <p className={styles.status} role="status">{status || "Your QR links to this site so friends can check their own place."}</p>
    </>}
  </main>;
}
