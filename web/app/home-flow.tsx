"use client";

// Homepage: the house alone at center (tap it to start) → it zooms in → a two-slide fact slideshow
// (text top-left, two consistent numbers bottom-right) → the mission and the one primary action.
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import styles from "./start-screen.module.css";

type Fact = { kicker: string; text: string; numbers: { value: string; label: string; tone: "red" | "blue" }[]; source: string };

// Every number is sourced from the repo's own data and factors; the two on each slide share a unit/basis.
const FACTS: Fact[] = [
  {
    kicker: "The bill behind the listing",
    text: "Two similar Ann Arbor apartments. Same kind of building, about the same size. The listings never mention what it costs to keep them warm in winter and cool in summer.",
    numbers: [
      { value: "$265", label: "a year to heat and cool, 624 Church St", tone: "blue" },
      { value: "$2,179", label: "a year to heat and cool, 1022 S Forest Ave", tone: "red" },
    ],
    source: "Hidden Rent model estimates, heating + cooling only, priced with EIA Michigan rates.",
  },
  {
    kicker: "Every bit of gas counts twice",
    text: "Buildings make up about 68% of Ann Arbor's emissions. Every unit of gas a leaky apartment burns costs the renter money and puts carbon in the air.",
    numbers: [
      { value: "$0.91", label: "per ccf of natural gas in Michigan", tone: "blue" },
      { value: "5.5 kg", label: "of CO₂ per ccf of natural gas burned", tone: "red" },
    ],
    source: "EIA Michigan residential gas, marginal price, 12-month average; EPA 5.306 kg CO₂/therm × 1.037 therm/ccf; A2ZERO.",
  },
];
const SLIDE_MS = 6500;

export function HomeFlow() {
  // -1 = the house; 0..FACTS.length-1 = fact slides; FACTS.length = the mission + start
  const [step, setStep] = useState(-1);
  const [leaving, setLeaving] = useState(false);
  const last = FACTS.length;

  const next = useCallback(() => setStep((s) => Math.min(last, s + 1)), [last]);
  const start = () => {
    if (leaving) return;
    setLeaving(true); // the house zooms in, then the first fact
    window.setTimeout(() => { setStep(0); setLeaving(false); }, 700);
  };

  // auto-advance the fact slides; →/Enter/Space advance, Esc skips to the end
  useEffect(() => {
    if (step < 0 || step >= last) return;
    const t = window.setTimeout(next, SLIDE_MS);
    return () => window.clearTimeout(t);
  }, [step, last, next]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (step < 0 || step >= last) return;
      if (["ArrowRight", "Enter", " "].includes(e.key)) { e.preventDefault(); next(); }
      if (e.key === "Escape") setStep(last);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [step, last, next]);

  if (step === -1) {
    return (
      <main className={styles.stage}>
        <button type="button" className={`${styles.houseButton} ${leaving ? styles.zoom : ""}`} onClick={start} aria-label="Start" tabIndex={-1}>
          <span className={styles.photo}>
            <img className={styles.ghostRed} src="/hero/house.png" alt="" />
            <img className={styles.ghostBlue} src="/hero/house.png" alt="" />
            <img className={styles.house} src="/hero/house.png" alt="" />
          </span>
        </button>
        <button type="button" className={`${styles.startHouse} ${leaving ? styles.fadeOut : ""}`} onClick={start}>
          Start
          <img src="/hero/arrow-up-right.svg" alt="" width={18} height={18} />
        </button>
      </main>
    );
  }

  if (step < last) {
    const f = FACTS[step];
    return (
      <main className={styles.slide} onClick={next} key={step}>
        <section className={styles.wall}>
          <p className={styles.kicker}>{f.kicker}</p>
          <p className={styles.wallText}>{f.text}</p>
        </section>
        <section className={styles.numbers} aria-label="Key numbers">
          {f.numbers.map((n, i) => (
            <div key={n.value} className={styles.number} style={{ ["--i" as string]: i }}>
              <span className={`${styles.value} ${n.tone === "red" ? styles.red : styles.blue}`}>{n.value}</span>
              <span className={styles.numLabel}>{n.label}</span>
            </div>
          ))}
          <p className={styles.source}>{f.source}</p>
        </section>
        <nav className={styles.progress} aria-label="Slides" onClick={(e) => e.stopPropagation()}>
          {FACTS.map((_, i) => <span key={i} className={i === step ? styles.dotOn : styles.dot} />)}
          <button type="button" className={styles.skip} onClick={() => setStep(last)}>Skip</button>
        </nav>
        <div className={styles.timer} style={{ ["--ms" as string]: `${SLIDE_MS}ms` }} aria-hidden="true" />
      </main>
    );
  }

  return (
    <main className={styles.final}>
      <p className={styles.eyebrow}>Hidden Rent · Ann Arbor, MI</p>
      <h1 className={styles.heading}>The rent<br />you don&apos;t see.</h1>
      <p className={styles.mission}>
        Helping renters <mark className={styles.hl}>see</mark> and <mark className={styles.hl}>cut</mark> their energy use, for{" "}
        <mark className={`${styles.hl} ${styles.hlBlue}`}>the planet</mark> and <mark className={styles.hl}>their wallet</mark>, through{" "}
        <mark className={`${styles.hl} ${styles.hlBlue}`}>friendly competition</mark>.
      </p>
      <div className={styles.actions}>
        <Link className={styles.start} href="/loading?next=/address">
          Find my hidden rent
          <img src="/hero/arrow-up-right.svg" alt="" width={18} height={18} />
        </Link>
        <span className={styles.secondaryWrap}>
          <Link className={styles.secondary} href="/about">See how it works →</Link>
          <span className={styles.secondaryNote}>How Hidden Rent scores a home in 3 steps</span>
        </span>
      </div>
      <button type="button" className={styles.replay} onClick={() => setStep(0)}>↺ Replay the facts</button>
    </main>
  );
}
