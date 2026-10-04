"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { API, apiFetch, load } from "@/app/lib/api";
import { getSession, gradeLabel, annualRange, billLabel, carbon, type Estimate } from "@/components/hidden-rent-map/estimate-data";
import styles from "./watch.module.css";

// ResStock building types (building.type) -> the Grok Imagine clip in /public/clips (api/scripts/make_clips.py)
const CLIP: Record<string, string> = {
  "Single-Family Attached": "duplex",
  "Multi-Family with 2 - 4 Units": "duplex",
  "Multi-Family with 5+ Units": "apartment",
};

export default function WatchPage() {
  const param = useSearchParams().get("session");
  const [stored, setStored] = useState<string | null>();
  useEffect(() => { if (!param) setStored(load("session")); }, [param]);
  const session = param ?? stored; // undefined while the saved session loads
  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [playing, setPlaying] = useState(false);
  const [audioFailed, setAudioFailed] = useState(false);
  const [progress, setProgress] = useState(0); // 0..1 through the narration
  const video = useRef<HTMLVideoElement>(null);
  const audio = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (!session) return;
    let active = true;
    getSession(session).then((e) => { if (active) setEstimate(e); }).catch((e) => { if (active) setError(e.message); });
    apiFetch<{ text: string }>(`/narration/${encodeURIComponent(session)}/script`)
      .then((r) => { if (active) setText(r.text); }).catch(() => {});
    return () => { active = false; };
  }, [session]);

  async function play() {
    const v = video.current, a = audio.current;
    if (playing) { v?.pause(); a?.pause(); setPlaying(false); return; }
    setPlaying(true);
    v?.play().catch(() => {});
    if (a && !audioFailed) await a.play().catch(() => setAudioFailed(true));
  }

  // Captions: the sentence the voice is on, by its share of the script's characters (good enough for one voice).
  const sentences = text.match(/[^.?!]+[.?!]+/g)?.map((s) => s.trim()) ?? (text ? [text] : []);
  let at = 0, current = 0;
  sentences.forEach((s, i) => { if (progress * text.length >= at) current = i; at += s.length + 1; });
  const clip = CLIP[estimate?.building.type ?? ""] ?? "house";
  const enc = encodeURIComponent(session ?? "");

  return <main className={styles.page}>
    <nav className={styles.nav}><Link href="/">Hidden Rent ↗</Link><span>Your rental dossier / Watch</span>{session && <Link href={`/share?session=${enc}`}>Share card ↗</Link>}</nav>
    {session === null ? <div className={styles.notice}>Check a listing first, then come back to watch its report. <Link href="/">Check your place ↗</Link></div>
      : error ? <div className={styles.notice} role="alert">{error} <Link href="/">Check another listing ↗</Link></div>
      : !estimate ? <div className={styles.notice} role="status">Loading your report…</div> : <>
      <h1 className={styles.title}>{estimate.building.address}</h1>
      <figure className={styles.player}>
        <div className={styles.stage}>
          <video ref={video} className={styles.video} src={`/clips/${clip}.mp4`} poster={`/clips/${clip}.jpg`}
            muted loop playsInline preload="metadata" aria-hidden="true" />
          <div className={styles.overlay}>
            <div className={styles.grade}><span>Grade</span><strong>{gradeLabel(estimate)}</strong></div>
            <dl className={styles.stats}>
              <div><dt>{billLabel(estimate).replace("PREDICTED · ", "")}</dt><dd>{annualRange(estimate)}</dd></div>
              <div><dt>Carbon</dt><dd>{carbon(estimate)}</dd></div>
            </dl>
          </div>
          <button type="button" className={`${styles.play} ${playing ? styles.playing : ""}`} onClick={play}
            aria-label={playing ? "Pause the report" : "Play the report"}>{playing ? "❚❚" : "▶ Play report"}</button>
        </div>
        <audio ref={audio} src={`${API}/narration/${enc}`} preload="none" onError={() => setAudioFailed(true)}
          onTimeUpdate={(e) => { const a = e.currentTarget; if (a.duration) setProgress(a.currentTime / a.duration); }}
          onEnded={() => { video.current?.pause(); setPlaying(false); setProgress(1); }} />
        <figcaption className={styles.credit}>Illustration generated with Grok Imagine, not this building. Narration by Grok Voice.</figcaption>
      </figure>
      {audioFailed && <p className={styles.notice} role="status">Audio unavailable. The captions below have the full report.</p>}
      <section className={styles.captions} aria-live="polite" aria-label="Captions">
        {sentences.length ? sentences.map((s, i) => <span key={i} className={playing && !audioFailed && i === current ? styles.now : undefined}>{s} </span>)
          : <span>Captions unavailable.</span>}
      </section>
      <p className={styles.links}><Link href="/grade">Back to your report ↗</Link></p>
    </>}
  </main>;
}
