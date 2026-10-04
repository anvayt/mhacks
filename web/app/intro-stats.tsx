"use client";

// Homepage stats: count up once when they scroll into view, staggered, with a red→blue underline sweep.
// Reduced motion: final numbers immediately, no movement. No animation library.
import { useEffect, useRef, useState } from "react";
import styles from "./start-screen.module.css";

export type Stat = { value: string; label: string; lead?: boolean };

/** "$1,914" → {prefix "$", n 1914, suffix "", decimals 0}; "54.5%" → {"", 54.5, "%", 1}. */
function parse(v: string) {
  const m = v.match(/^([^\d]*)([\d,]*\.?\d+)(.*)$/);
  if (!m) return null;
  const num = m[2].replace(/,/g, "");
  return { prefix: m[1], n: Number(num), suffix: m[3], decimals: num.includes(".") ? num.split(".")[1].length : 0, comma: m[2].includes(",") };
}
const show = (p: NonNullable<ReturnType<typeof parse>>, x: number) =>
  `${p.prefix}${p.comma ? Math.round(x).toLocaleString("en-US") : x.toFixed(p.decimals)}${p.suffix}`;

function Counter({ value, run }: { value: string; run: boolean }) {
  const p = parse(value);
  const [text, setText] = useState(value);
  useEffect(() => {
    if (!p || !run) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return setText(value);
    let raf = 0;
    const t0 = performance.now(), dur = 1300;
    const tick = (t: number) => {
      const k = Math.min(1, (t - t0) / dur), eased = 1 - Math.pow(1 - k, 3);
      setText(show(p, p.n * eased));
      if (k < 1) raf = requestAnimationFrame(tick);
      else setText(value);
    };
    setText(show(p, 0));
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run, value]);
  return <span className={styles.value}>{text}</span>;
}

export function IntroStats({ stats }: { stats: Stat[] }) {
  const ref = useRef<HTMLUListElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!("IntersectionObserver" in window)) return setInView(true);
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setInView(true); io.disconnect(); } }, { threshold: 0.35 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <ul ref={ref} className={`${styles.stats} ${inView ? styles.inView : ""}`}>
      {stats.map((s, i) => (
        <li key={s.value} className={`${styles.stat} ${s.lead ? styles.lead : ""}`} style={{ ["--i" as string]: i }}>
          <Counter value={s.value} run={inView} />
          <span className={styles.sweep} aria-hidden="true" />
          <span className={styles.label}>{s.label}</span>
        </li>
      ))}
    </ul>
  );
}
