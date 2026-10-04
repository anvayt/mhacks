"use client";

import { useEffect, useState } from "react";
import { MapCanvas } from "./MapCanvas";
import { costColor } from "./format";
import styles from "./hidden-rent-map.module.css";
import type { Focus, MapWidgetData } from "./types";

export interface HiddenRentMapProps {
  data: MapWidgetData;
  /** Index into `data.steps` (0 = public record only); colors the selected building by its current estimate. */
  step?: number;
  /** Controlled camera focus; omit to let the widget manage it (starts on all of Ann Arbor). */
  focus?: Focus;
  onFocusChange?: (focus: Focus) => void;
  /** Building id (city footprint OBJECTID) to highlight, e.g. while hovering an address in a list outside the map. */
  highlightId?: number | null;
  /** Fires with the building under the cursor on the map (null when none), so outside lists can follow along. */
  onHoverBuilding?: (id: number | null) => void;
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

export function HiddenRentMap({
  data,
  step = 0,
  focus: focusProp,
  onFocusChange,
  highlightId,
  onHoverBuilding,
  className,
}: HiddenRentMapProps) {
  const [innerFocus, setInnerFocus] = useState<Focus>("city");
  const focus = focusProp ?? innerFocus;
  const setFocus = (f: Focus) => {
    if (focusProp === undefined) setInnerFocus(f);
    onFocusChange?.(f);
  };
  const [mapHover, setMapHover] = useState<number | null>(null);
  const reducedMotion = useReducedMotion();
  const hasSimilar = data.similar.items.length > 0;

  const foci: { id: Focus; label: string }[] = [
    { id: "city", label: "Ann Arbor" },
    ...(hasSimilar ? [{ id: "similar" as const, label: "Similar" }] : []),
    { id: "block", label: "Block" },
    { id: "building", label: "Building" },
  ];

  return (
    <section className={`${styles.root} ${className ?? ""}`} aria-label={`Map of ${data.address}`}>
      <MapCanvas
        data={data}
        focus={focus}
        homeColor={homeColorFor(data, step)}
        highlightId={highlightId ?? mapHover}
        onHoverBuilding={(id) => {
          setMapHover(id);
          onHoverBuilding?.(id);
        }}
        reducedMotion={reducedMotion}
      />

      <div className={styles.focus} role="group" aria-label="Map view">
        {foci.map((f) => (
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
        <span className={styles.legendItem}>
          <i className={styles.legendRamp} />
          this home: cheaper → pricier
        </span>
        {hasSimilar && (
          <span className={styles.legendItem}>
            <i className={styles.legendDot} />
            similar
          </span>
        )}
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
