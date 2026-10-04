import Link from "next/link";
import { IntroStats, type Stat } from "./intro-stats";
import styles from "./start-screen.module.css";

// Every number here is sourced (see SOURCES below); keep them in sync with the Devpost and pitch.
const STATS: Stat[] = [
  { value: "$1,914", label: "a year apart: what two similar Ann Arbor apartments cost to heat and cool", lead: true },
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
          <p className={`${styles.eyebrow} ${styles.enter}`} style={{ ["--d" as string]: "0.9s" }}>Hidden Rent · Ann Arbor, MI</p>
          <h1 className={`${styles.heading} ${styles.enter}`} style={{ ["--d" as string]: "1s" }}>
            The rent
            <br />
            you don&apos;t see.
          </h1>
          <p className={`${styles.mission} ${styles.enter}`} style={{ ["--d" as string]: "1.25s" }}>
            Helping renters <mark className={styles.hl}>see</mark> and <mark className={styles.hl}>cut</mark> their energy use, for{" "}
            <mark className={`${styles.hl} ${styles.blue}`}>the planet</mark> and <mark className={styles.hl}>their wallet</mark>, through{" "}
            <mark className={`${styles.hl} ${styles.blue}`}>friendly competition</mark>.
          </p>
          <IntroStats stats={STATS} startAfterMs={2300} />
          <div className={`${styles.actions} ${styles.enterCta}`}>
            <Link className={styles.start} href="/loading?next=/address">
              Find my hidden rent
              <img src="/hero/arrow-up-right.svg" alt="" width={18} height={18} />
            </Link>
            <div className={styles.secondaryWrap}>
              <Link className={styles.secondary} href="/about">
                See how it works →
              </Link>
              <span className={styles.secondaryNote}>How Hidden Rent scores a home in 3 steps</span>
            </div>
          </div>
          <p className={`${styles.sources} ${styles.enter}`} style={{ ["--d" as string]: "4.1s" }}>{SOURCES}</p>
        </section>
        {/* Purely visual: the one start action is the button. It leans toward the button when that button is hovered. */}
        <div className={`${styles.photo} ${styles.houseIn}`} aria-hidden="true">
          <img className={styles.ghostRed} src="/hero/house.png" alt="" />
          <img className={styles.ghostBlue} src="/hero/house.png" alt="" />
          <img className={styles.house} src="/hero/house.png" alt="" />
        </div>
      </div>
    </main>
  );
}
