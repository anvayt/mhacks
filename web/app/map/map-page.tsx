"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { HiddenRentMap, MapStory, getMapWidgetData, type MapWidgetData, type Focus } from "@/components/hidden-rent-map";
import { USE_MOCKS } from "@/components/hidden-rent-map/data";
import styles from "./map.module.css";

export default function MapPage() {
  const session = useSearchParams().get("session");
  const [data, setData] = useState<MapWidgetData | null>(null);
  const [error, setError] = useState("");
  const [attempt, retry] = useState(0);
  const [step, setStep] = useState(0);
  const [focus, setFocus] = useState<Focus>("building");
  const [retrieved, setRetrieved] = useState("");
  useEffect(() => {
    setData(null); setError("");
    if (!session && !USE_MOCKS) return;
    const abort = new AbortController();
    getMapWidgetData(session ?? "demo", {signal:abort.signal}).then((d) => {
      setData(d); setStep(d.steps.length - 1); setRetrieved(new Date().toLocaleDateString("en-US", {year:"numeric",month:"short",day:"numeric"}));
    }).catch((e) => { if (!abort.signal.aborted) setError(e.message); });
    return () => abort.abort();
  }, [session, attempt]);
  return <main className={styles.page}>
    <nav className={styles.nav}><Link href="/">Hidden Rent ↗</Link><span>Ann Arbor / City atlas</span>{session && <Link href={`/share?session=${encodeURIComponent(session)}`}>Share dossier ↗</Link>}</nav>
    <header className={styles.header}><p>PUBLIC RECORDS. YOUR ANSWERS. ONE HOME.</p><h1>Your place<br /><em>in the city.</em></h1><p>Heating + cooling, revealed one answer at a time.</p></header>
    {!session && !USE_MOCKS ? <div className={styles.notice}>Start with a listing to see its map. <Link href="/">Check your place ↗</Link></div> : error ? <div className={styles.notice} role="alert"><p>{error}</p><button onClick={() => retry(attempt + 1)}>Try again</button> <Link href="/">Check another listing ↗</Link></div> : !data ? <div className={styles.notice} role="status">Finding your building and its real answer history…</div> : <>
      <div className={styles.address}><h2>{data.address}</h2><span>{USE_MOCKS ? "MOCK PREVIEW · " : ""}City footprint #{data.building.id}</span></div>
      <HiddenRentMap data={data} step={step} focus={focus} onFocusChange={setFocus} />
      <p className={styles.caption}>City of Ann Arbor footprints + ResStock predictions · retrieved {retrieved}. Grades compare heating + cooling cost per square foot within each building type. Unscored buildings are gray. Similar footprints are a geometric sample, not an efficiency ranking.</p>
      <div className={styles.history}><span>{step === 0 ? "Public record" : `Answer ${step} of ${data.steps.length - 1}`}</span><label htmlFor="map-step">Estimate history</label><input id="map-step" type="range" min="0" max={data.steps.length - 1} value={step} onChange={(e) => setStep(Number(e.target.value))} disabled={data.steps.length === 1} /><span>{data.steps[step].answer_label ?? "Before your answers"}</span></div>
      <MapStory className={styles.storyFrame} data={data} step={step} onStepChange={setStep} onFocus={setFocus} />
    </>}
  </main>;
}
