"use client";
import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { API, load } from "@/app/lib/api";
import { getSession, money, gradeLabel, annualRange, hiddenRent, carbon, peerLabel, type Estimate } from "@/components/hidden-rent-map/estimate-data";
import styles from "./compare.module.css";

type Side = "a" | "b";
interface Battle { a: Estimate; b: Estimate; winner: Side; diff_usd_yr: number; confident: boolean }
export default function ComparePage() {
  const session = useSearchParams().get("a");
  const [values, setValues] = useState({a:"", b:""});
  const [sizes, setSizes] = useState({a:"", b:""});
  const [errors, setErrors] = useState({a:"", b:"", general:""});
  const [battle, setBattle] = useState<Battle | null>(null);
  const [busy, setBusy] = useState(false);
  const [prefilling, setPrefilling] = useState(false);
  useEffect(() => {
    if (!session) return;
    let active = true; setPrefilling(true);
    getSession(session).then((e) => { if(active) { setValues((v) => ({...v, a:e.building.address})); setSizes((v) => ({...v, a:String(e.building.sqft)})); }}).catch((e) => { if(active) setErrors((x) => ({...x,a:e.message})); }).finally(() => { if(active) setPrefilling(false); });
    return () => { active = false; };
  }, [session]);
  async function submit(event: FormEvent) {
    event.preventDefault(); setErrors({a:"",b:"",general:""}); setBattle(null); setBusy(true);
    try {
      const listings = (["a","b"] as Side[]).map((side) => ({[/^https?:\/\//i.test(values[side].trim()) ? "url" : "address"]: values[side].trim(), ...(sizes[side] ? {unit_sqft:Number(sizes[side])} : {})}));
      const token = load("token");
      const response = await fetch(`${API}/compare`, {method:"POST", headers:{"Content-Type":"application/json", ...(token ? {Authorization:`Bearer ${token}`} : {})}, body:JSON.stringify({listings})});
      const body = await response.json().catch(() => null);
      if (!response.ok) {
        const d = body?.detail;
        const side = d?.listing === "a" || d?.listing === "b" ? d.listing as Side : "general";
        setErrors((x) => ({...x,[side]: `${d?.message ?? "We couldn't compare these listings. Try again."}${d?.hint ? ` ${d.hint}` : ""}`}));
      } else setBattle(body as Battle);
    } catch { setErrors((x) => ({...x,general:"The Hidden Rent API isn't reachable right now. Your listings are still here; try again."})); }
    finally { setBusy(false); }
  }
  return <main className={styles.page}>
    <nav className={styles.nav}><Link href="/">Hidden Rent ↗</Link><span>Rental dossiers / Listing battle</span></nav>
    <header className={styles.header}><p>SAME SEARCH. A DIFFERENT BILL.</p><h1>Put them<br /><em>head to head.</em></h1><p>Compare the heating + cooling hiding behind two listings.</p></header>
    <form onSubmit={submit}>
      <div className={styles.grid}>{(["a","b"] as Side[]).map((side) => {
        const e = battle?.[side]; const winner = battle?.winner === side && battle.diff_usd_yr > 0;
        return <section key={side} className={`${styles.card} ${winner ? styles.winner : ""}`} aria-label={`Listing ${side.toUpperCase()}`}>
          <div className={styles.cardTop}><h2>Listing {side.toUpperCase()}</h2>{winner && <span className={styles.badge}>★ Lower predicted bill</span>}</div>
          <label htmlFor={`listing-${side}`}>Address or listing link</label>
          <input id={`listing-${side}`} required value={values[side]} onChange={(event) => { setValues((v) => ({...v,[side]:event.target.value})); setBattle(null); }} placeholder={side === "a" ? "624 Church St, Ann Arbor, MI" : "1022 S Forest Ave, Ann Arbor, MI"} aria-invalid={!!errors[side]} aria-describedby={errors[side] ? `error-${side}` : undefined} disabled={busy || prefilling} />
          <label htmlFor={`size-${side}`}>Unit size, sq ft <span>(optional)</span></label>
          <input id={`size-${side}`} type="number" min="100" max="10000" value={sizes[side]} onChange={(event) => { setSizes((v) => ({...v,[side]:event.target.value})); setBattle(null); }} placeholder="Use public record" disabled={busy} />
          {errors[side] && <p className={styles.error} role="alert" id={`error-${side}`}>{errors[side]}</p>}
          {e ? <div className={styles.results}>
            <p className={styles.eyebrow}>PREDICTED · HEATING + COOLING ONLY</p>
            <div className={styles.gradeRow}><strong className={styles.grade}>{gradeLabel(e)}</strong><p>{e.locked === false ? `Point estimate ${e.grade}; answers can change it.` : "Your predicted efficiency grade."}<br />{peerLabel(e)}</p></div>
            <p className={styles.annual}>{money(e.bill.annual.p50)}<span>/year</span></p><p className={styles.range}>{annualRange(e)} · estimated range</p>
            <dl className={styles.stats}><div><dt>Hidden rent vs same-type median</dt><dd>{hiddenRent(e)}</dd></div><div><dt>Predicted carbon</dt><dd>{carbon(e)}</dd></div></dl>
            <p className={styles.note}>{e.building.address} · {e.building.sqft.toLocaleString()} sq ft. {e.bill.note}</p>
            <Link className={styles.cardLink} href={`/share?session=${encodeURIComponent(e.session_id)}`}>Share this dossier ↗</Link>
          </div> : <p className={styles.placeholder}>Two places. Their real public records. A clearer decision.</p>}
        </section>;
      })}</div>
      {errors.general && <p className={styles.generalError} role="alert">{errors.general}</p>}
      <button className={styles.submit} type="submit" disabled={busy || prefilling}>{busy ? "Comparing real estimates…" : prefilling ? "Loading Listing A…" : "Reveal the hidden difference ↗"}</button>
    </form>
    {battle && <section className={styles.reveal} aria-live="polite"><p>THE HIDDEN DIFFERENCE</p><h2>{battle.diff_usd_yr === 0 ? "The same predicted annual bill." : `Listing ${battle.winner === "a" ? "B" : "A"} costs ${money(battle.diff_usd_yr)}/yr more to live in.`}</h2><p>For predicted heating + cooling. Rent and other utilities are excluded.</p><strong>{battle.confident ? "The estimated cost ranges do not overlap." : "Too close to call within our uncertainty"}</strong><p>Different unit sizes and unknown equipment can affect this comparison. Grades compare efficiency per square foot; the winner compares total annual cost.</p></section>}
  </main>;
}
