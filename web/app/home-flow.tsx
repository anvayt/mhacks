"use client";

// House at center (tap it to start) → the two energy slides → Find my hidden rent, unchanged.
import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import styles from "./start-screen.module.css";

const FADE_MS = 800;
const BALANCE_MS = 1200;

export function HomeFlow() {
  const [step, setStep] = useState(-1);
  const [leaving, setLeaving] = useState(false);
  const [blueShown, setBlueShown] = useState(false);
  const [blueLeaving, setBlueLeaving] = useState(false);
  const [armed, setArmed] = useState(false);
  const [phase, setPhase] = useState<"blue" | "red" | "balance">("blue");
  const [invite, setInvite] = useState(false);

  const start = () => {
    if (leaving) return;
    setLeaving(true);
    window.setTimeout(() => {
      setStep(0);
      setLeaving(false);
    }, 700);
  };

  useEffect(() => {
    if (step !== 0) return;
    const frame = requestAnimationFrame(() => setBlueShown(true));
    return () => cancelAnimationFrame(frame);
  }, [step]);

  useEffect(() => {
    if (step !== 1) return;
    const arm = requestAnimationFrame(() => setArmed(true));
    const cover = window.setTimeout(() => setPhase("red"), 60);
    return () => {
      cancelAnimationFrame(arm);
      window.clearTimeout(cover);
    };
  }, [step]);

  useEffect(() => {
    if (phase !== "balance") return;
    const show = window.setTimeout(() => setInvite(true), BALANCE_MS);
    return () => window.clearTimeout(show);
  }, [phase]);

  function leaveBlue() {
    if (blueLeaving) return;
    setBlueLeaving(true);
    window.setTimeout(() => setStep(1), FADE_MS);
  }

  if (step === -1) {
    return (
      <main className={styles.stage}>
        <button type="button" className={`${styles.houseButton} ${leaving ? styles.zoom : ""}`} onClick={start} aria-label="Start">
          <span className={styles.photo}>
            <img className={styles.ghostRed} src="/hero/house.png" alt="" />
            <img className={styles.ghostBlue} src="/hero/house.png" alt="" />
            <img className={styles.house} src="/hero/house.png" alt="" />
          </span>
        </button>
      </main>
    );
  }

  if (step === 0) {
    return (
      <main className="pitch dim-screen">
        <h1 className={blueLeaving ? "pitch-line hide" : blueShown ? "pitch-line show" : "pitch-line"}>
          Here&apos;s how much energy the average American thinks their heater uses.
        </h1>
        <button className="ghost-action pitch-next" type="button" onClick={leaveBlue}>
          Next
          <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
        </button>
      </main>
    );
  }

  const stops: CSSProperties =
    phase === "red"
      ? { "--blue-end": "-30%", "--red-start": "0%" }
      : phase === "balance"
        ? { "--blue-end": "35%", "--red-start": "65%" }
        : { "--blue-end": "100%", "--red-start": "130%" };

  return (
    <main className={`pitch pitch-shift dim-screen${armed ? " armed" : ""}${phase === "balance" ? " settling" : ""}`} style={stops}>
      <h1 className={phase === "balance" ? "pitch-line ride hide" : phase === "red" ? "pitch-line ride show" : "pitch-line ride"}>
        And here&apos;s how much energy it actually uses.
      </h1>
      <p className={invite ? "pitch-invite show" : "pitch-invite"}>
        Between those two is the energy and money a few questions can save.
      </p>
      {invite ? (
        <Link className={`${styles.start} ${styles.carry}`} href="/loading?next=/address">
          Find my hidden rent
          <img src="/hero/arrow-up-right.svg" alt="" width={18} height={18} />
        </Link>
      ) : (
        <button className={phase === "red" ? "ghost-action pitch-next" : "ghost-action pitch-next hide"} type="button" onClick={() => phase === "red" && setPhase("balance")} disabled={phase !== "red"}>
          Next
          <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
        </button>
      )}
    </main>
  );
}
