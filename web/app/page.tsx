import Link from "next/link";
import styles from "./start-screen.module.css";

// Every number here is sourced (see SOURCES below); keep them in sync with the Devpost and pitch.
const STATS = [
  { value: "$1,914", label: "a year apart: what two similar Ann Arbor apartments cost to heat and cool" },
  { value: "68%", label: "of Ann Arbor's emissions come from buildings" },
  { value: "54.5%", label: "of Ann Arbor households rent, and sign without seeing the bill" },
  { value: "25,704", label: "Ann Arbor buildings already scored" },
];
const SOURCES =
  "Sources: Hidden Rent model estimates, heating + cooling only (624 Church St vs 1022 S Forest Ave); A2ZERO; U.S. Census ACS; City of Ann Arbor building footprints.";

export default function StartScreen() {
  return (
    <main className={styles.intro}>
      <div className={styles.grid}>
        <section className={styles.copy}>
          <p className={styles.eyebrow}>Hidden Rent · Ann Arbor, MI</p>
          <h1 className={styles.heading}>
            The rent
            <br />
            you don&apos;t see.
          </h1>
          <p className={styles.mission}>
            Helping renters see and cut their energy use, for the planet and their wallet, through friendly competition.
          </p>
          <ul className={styles.stats}>
            {STATS.map((s) => (
              <li key={s.value}>
                <span className={styles.value}>{s.value}</span>
                <span className={styles.label}>{s.label}</span>
              </li>
            ))}
          </ul>
          <div className={styles.actions}>
            <Link className={styles.start} href="/loading?next=/address">
              Find my hidden rent
              <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
            </Link>
            <Link className={styles.secondary} href="/about">
              How it works
            </Link>
          </div>
          <p className={styles.sources}>{SOURCES}</p>
        </section>
        <Link className={`start-photo ${styles.photo}`} href="/loading?next=/address" aria-label="Start: find my hidden rent">
          <img src="/hero/house.png" alt="" />
          <span className="start-photo-label">Start</span>
        </Link>
      </div>
    </main>
  );
}
