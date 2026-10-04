"use client";

import { useEffect, useState } from "react";
import { MapCanvas } from "./MapCanvas";
import { costColor } from "./format";
import styles from "./hidden-rent-map.module.css";
import type { Focus, MapWidgetData } from "./types";

const FOCI: { id: Focus; label: string }[] = [
  { id: "city", label: "Ann Arbor" },
  { id: "block", label: "Block" },
  { id: "building", label: "Building" },
];

export interface HiddenRentMapProps {
  data: MapWidgetData;
  /** Index into `data.steps` (0 = public record only); colors the building by its current estimate. */
  step?: number;
  /** Controlled camera focus; omit to let the widget manage it (starts on all of Ann Arbor). */
  focus?: Focus;
  onFocusChange?: (focus: Focus) => void;
  className?: string;
}

function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const q = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(q.matches);
    const on = (e: MediaQueryListEvent) => setReduced(e.matches);
    q.addEventListener("change", on);
    return () => q.removeEventListener("change", on);
  }, []);
  return reduced;
}

/** Brand blue → red by where an estimate sits among the starting look-alike homes (p10 → p90). */
export function homeColorFor(data: MapWidgetData, step: number) {
  const start = data.steps[0].lookalikes;
  const s = data.steps[Math.min(Math.max(step, 0), data.steps.length - 1)];
  return costColor((s.estimate.annual_usd - start.p10) / Math.max(1, start.p90 - start.p10));
}

export function HiddenRentMap({ data, step = 0, focus: focusProp, onFocusChange, className }: HiddenRentMapProps) {
  const [innerFocus, setInnerFocus] = useState<Focus>("city");
  const focus = focusProp ?? innerFocus;
  const setFocus = (f: Focus) => {
    if (focusProp === undefined) setInnerFocus(f);
    onFocusChange?.(f);
  };
  const reducedMotion = useReducedMotion();

  return (
    <section className={`${styles.root} ${className ?? ""}`} aria-label={`Map of ${data.address}`}>
      <MapCanvas data={data} focus={focus} homeColor={homeColorFor(data, step)} reducedMotion={reducedMotion} />

      <div className={styles.focus} role="group" aria-label="Map view">
        {FOCI.map((f) => (
          <button
            key={f.id}
            type="button"
            aria-pressed={focus === f.id}
            className={styles.focusButton}
            onClick={() => setFocus(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className={styles.legend} aria-hidden="true">
        <span>cheaper</span>
        <span className={styles.legendRamp} />
        <span>pricier</span>
      </div>

      <details className={styles.sources}>
        <summary>Where these numbers come from</summary>
        <ul>
          {data.sources.map((s) => (
            <li key={s.label}>
              <a href={s.url} target="_blank" rel="noreferrer">
                {s.label}
              </a>
            </li>
          ))}
        </ul>
        <p>Predicted, typical-weather estimates, not a bill.</p>
      </details>
    </section>
  );
}
