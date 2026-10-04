"use client";

import { useMemo } from "react";
import styles from "./hidden-rent-map.module.css";
import type { SurveyStep } from "./types";
import { usd } from "./format";

const BINS = 44;
const DOT = 6;

interface Props {
  steps: SurveyStep[];
  step: number;
}

/** Multiset match: which of the starting homes are still in the current step's sample. */
function survivors(all: number[], now: number[]): boolean[] {
  const left = new Map<number, number>();
  for (const v of now) left.set(v, (left.get(v) ?? 0) + 1);
  return all.map((v) => {
    const n = left.get(v) ?? 0;
    if (n > 0) left.set(v, n - 1);
    return n > 0;
  });
}

export function LookalikeStrip(props: Props) {
  const current = props.steps[props.step].lookalikes;
  if (!current.count || !current.usd_yr.length || current.p10 == null || current.p90 == null || !props.steps[0].lookalikes.usd_yr.length) {
    return <p className={styles.emptyCloud}>The similar-home distribution is not available yet (pending model data). Your real estimate and answer history are shown below.</p>;
  }
  return <PopulatedStrip {...props} />;
}

function PopulatedStrip({ steps, step }: Props) {
  const start = steps[0].lookalikes;
  const current = steps[step].lookalikes as typeof start & { p10: number; p90: number };
  const estimate = steps[step].estimate.annual_usd;

  // When the starting cloud was sampled, values can't be matched across steps; show the current sample only.
  const tracked = start.usd_yr.length === start.count;
  const base = tracked ? start.usd_yr : current.usd_yr;

  // Scale to the bulk of the starting homes (the priciest 3% stack in the last bin) plus every estimate.
  const { lo, hi } = useMemo(() => {
    const sorted = [...start.usd_yr].sort((a, b) => a - b);
    const p97 = sorted[Math.floor((sorted.length - 1) * 0.97)];
    const ests = steps.map((s) => s.estimate.annual_usd);
    const min = Math.min(sorted[0], ...ests);
    const max = Math.max(p97, ...ests);
    const pad = Math.max(1, (max - min) * 0.04);
    return { lo: Math.max(0, min - pad), hi: max + pad };
  }, [start.usd_yr, steps]);

  const pct = (v: number) => ((Math.min(Math.max(v, lo), hi) - lo) / (hi - lo)) * 100;

  const dots = useMemo(() => {
    const alive = tracked ? survivors(base, current.usd_yr) : base.map(() => true);
    const stackAll = new Array(BINS).fill(0);
    const stackAlive = new Array(BINS).fill(0);
    return base.map((v, i) => {
      const bin = Math.min(BINS - 1, Math.max(0, Math.floor(((v - lo) / (hi - lo)) * BINS)));
      const allSlot = stackAll[bin]++;
      const slot = alive[i] ? stackAlive[bin]++ : allSlot;
      return { key: i, left: ((bin + 0.5) / BINS) * 100, bottom: slot * (DOT + 1), alive: alive[i] };
    });
  }, [base, current.usd_yr, tracked, lo, hi]);

  const height = Math.max(...dots.map((d) => d.bottom)) + DOT + 4;
  const ticks = useMemo(() => {
    const step = (hi - lo) / 3 > 400 ? 500 : 250;
    const out: number[] = [];
    for (let t = Math.ceil(lo / step) * step; t <= hi - step * 1.3; t += step) out.push(t);
    return out;
  }, [lo, hi]);

  return (
    <figure className={styles.strip}>
      <div
        className={styles.stripPlot}
        style={{ height }}
        role="img"
        aria-label={`${current.count} similar homes. 8 in 10 cost between ${usd(current.p10)} and ${usd(
          current.p90,
        )} a year to heat and cool. Our estimate for this unit is ${usd(estimate)} a year.`}
      >
        {dots.map((d) => (
          <span
            key={d.key}
            className={`${styles.dot} ${d.alive ? "" : styles.dotGone}`}
            style={{ left: `${d.left}%`, bottom: d.bottom, width: DOT, height: DOT }}
          />
        ))}
        <span className={styles.estimateLine} style={{ left: `${pct(estimate)}%` }}>
          <span className={styles.estimateLabel}>This unit {usd(estimate)}</span>
        </span>
      </div>
      <div className={styles.rangeTrack}>
        <span
          className={styles.rangeBar}
          style={{ left: `${pct(current.p10)}%`, width: `${pct(current.p90) - pct(current.p10)}%` }}
        />
      </div>
      <div className={styles.axis}>
        {ticks.map((t) => (
          <span key={t} style={{ left: `${pct(t)}%` }}>
            {usd(t)}
          </span>
        ))}
        <span style={{ left: "100%", transform: "translateX(-100%)" }}>{usd(hi)}+</span>
      </div>
      <figcaption className={styles.stripCaption}>
        Each dot is a similar simulated home. Middle 8 in 10:{" "}
        <strong>
          {usd(current.p10)}–{usd(current.p90)}
        </strong>
        /yr
      </figcaption>
    </figure>
  );
}
