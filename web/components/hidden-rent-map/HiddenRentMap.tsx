"use client";

import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { LookalikeStrip } from "./LookalikeStrip";
import { MapCanvas } from "./MapCanvas";
import { buildingTypeLabel, costColor, num, signedUsd, usd } from "./format";
import styles from "./hidden-rent-map.module.css";
import type { Chapter, MapWidgetData, Season } from "./types";

const MI_FIRST_ENERGY_CODE = 1977;
const INK = "#11121a";
const CHAPTERS: { id: Chapter; label: string }[] = [
  { id: "building", label: "The building" },
  { id: "block", label: "The block" },
  { id: "answers", label: "Your answers" },
];
const SEASONS: Season[] = ["winter", "spring", "summer", "fall"];

export interface HiddenRentMapProps {
  data: MapWidgetData;
  /** Controlled chapter; omit to let the widget manage it. */
  chapter?: Chapter;
  defaultChapter?: Chapter;
  onChapterChange?: (chapter: Chapter) => void;
  /** Index into `data.steps` (0 = public record only). Controlled when set. */
  step?: number;
  defaultStep?: number;
  /** Called when the user answers the next question or starts over. */
  onStepChange?: (step: number) => void;
  className?: string;
}

function useControllable<T>(value: T | undefined, initial: T, onChange?: (v: T) => void) {
  const [inner, setInner] = useState(initial);
  const current = value ?? inner;
  const set = (v: T) => {
    if (value === undefined) setInner(v);
    onChange?.(v);
  };
  return [current, set] as const;
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

export function HiddenRentMap({
  data,
  chapter: chapterProp,
  defaultChapter = "building",
  onChapterChange,
  step: stepProp,
  defaultStep = 0,
  onStepChange,
  className,
}: HiddenRentMapProps) {
  const [chapter, setChapter] = useControllable(chapterProp, defaultChapter, onChapterChange);
  const [rawStep, setStep] = useControllable(stepProp, defaultStep, onStepChange);
  const step = Math.min(Math.max(rawStep, 0), data.steps.length - 1);
  const reducedMotion = useReducedMotion();
  const tabsId = useId();
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const start = data.steps[0].lookalikes;
  const now = data.steps[step];
  const t = (now.estimate.annual_usd - start.p10) / Math.max(1, start.p90 - start.p10);
  const homeColor = chapter === "answers" ? costColor(t) : INK;

  const onTabKey = (e: KeyboardEvent, i: number) => {
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    const next = (i + d + CHAPTERS.length) % CHAPTERS.length;
    setChapter(CHAPTERS[next].id);
    tabRefs.current[next]?.focus();
  };

  return (
    <section className={`${styles.root} ${className ?? ""}`} aria-label={`Energy story for ${data.address}`}>
      <div className={styles.mapPane}>
        <MapCanvas data={data} chapter={chapter} homeColor={homeColor} reducedMotion={reducedMotion} />
        <p className={styles.mapAddress}>{data.address}</p>
        {chapter === "answers" && (
          <div className={styles.legend} aria-hidden="true">
            <span>cheaper</span>
            <span className={styles.legendRamp} />
            <span>pricier</span>
            <small>than similar homes</small>
          </div>
        )}
      </div>

      <div className={styles.panel}>
        <div role="tablist" aria-label="Story chapters" className={styles.tabs}>
          {CHAPTERS.map((c, i) => (
            <button
              key={c.id}
              ref={(el) => {
                tabRefs.current[i] = el;
              }}
              role="tab"
              id={`${tabsId}-${c.id}-tab`}
              aria-controls={`${tabsId}-${c.id}`}
              aria-selected={chapter === c.id}
              tabIndex={chapter === c.id ? 0 : -1}
              className={styles.tab}
              onClick={() => setChapter(c.id)}
              onKeyDown={(e) => onTabKey(e, i)}
            >
              <span className={styles.tabNum}>0{i + 1}</span>
              {c.label}
            </button>
          ))}
        </div>

        <div
          role="tabpanel"
          id={`${tabsId}-${chapter}`}
          aria-labelledby={`${tabsId}-${chapter}-tab`}
          className={styles.chapter}
        >
          {chapter === "building" && <BuildingChapter data={data} />}
          {chapter === "block" && <BlockChapter data={data} />}
          {chapter === "answers" && <AnswersChapter data={data} step={step} setStep={setStep} />}
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
          <p>All costs are predicted, typical-weather estimates, not a bill.</p>
        </details>
      </div>
    </section>
  );
}

function BuildingChapter({ data }: { data: MapWidgetData }) {
  const b = data.building;
  return (
    <>
      <p className={styles.kicker}>Measured from the sky</p>
      {b.height_ft != null && (
        <p className={styles.bigStat}>
          {b.height_ft.toFixed(1)} <span>ft tall</span>
        </p>
      )}
      <p className={styles.body}>
        A plane flew over Ann Arbor with a laser scanner (LiDAR) and measured the height of every roof. Combined with
        the city&apos;s outline of the building, that tells us how much space there is to heat.
      </p>
      <ol className={styles.equation} aria-label="How we size the building">
        <li>
          <strong>{num(b.footprint_sqft)} sq ft</strong>
          <span>ground footprint</span>
        </li>
        <li aria-hidden="true">×</li>
        <li>
          <strong>{b.stories ?? "?"} floors</strong>
          <span>{b.stories_source.startsWith("LiDAR") ? "from the LiDAR height" : "city record, fits the height"}</span>
        </li>
        <li aria-hidden="true">≈</li>
        <li>
          <strong>{num(b.floor_area_sqft)} sq ft</strong>
          <span>of floor, matched to buildings that report theirs</span>
        </li>
      </ol>
      <p className={styles.body}>
        We treat it as {buildingTypeLabel(b.building_type)} and size this unit at{" "}
        <strong>{num(b.unit_sqft)} sq ft</strong>
        {b.unit_sqft_source.includes("median") ? ", a typical Michigan rental (the listing's size replaces it)" : ""}.
      </p>
      <p className={styles.why}>Why it matters: more floor and more outside wall means more air to keep warm.</p>
    </>
  );
}

function BlockChapter({ data }: { data: MapWidgetData }) {
  const bg = data.block_group;
  const year = bg.median_year_built;
  const assumed = data.steps[0].estimate.heating_fuel;
  const gas = bg.gas_heat_share;
  const elec = bg.electric_heat_share;
  const majority = gas != null && elec != null ? (gas >= elec ? "gas" : "electric") : null;
  return (
    <>
      <p className={styles.kicker}>Your block, from the census</p>
      {year != null && (
        <>
          <p className={styles.bigStat}>
            {year} <span>typical year rentals here were built</span>
          </p>
          <Timeline year={year} />
          <p className={styles.body}>
            {year < MI_FIRST_ENERGY_CODE
              ? `That's ${MI_FIRST_ENERGY_CODE - year} years before Michigan's first building energy code (${MI_FIRST_ENERGY_CODE}), so insulation and air-sealing were up to the builder.`
              : `That's after Michigan's first building energy code (${MI_FIRST_ENERGY_CODE}).`}{" "}
            When the listing doesn&apos;t say, we use the year from the census for this block.
          </p>
        </>
      )}
      {gas != null && elec != null && (
        <>
          <div className={styles.split} aria-label={`${Math.round(elec * 100)}% electric heat, ${Math.round(gas * 100)}% gas heat`}>
            <span className={styles.splitElec} style={{ flexBasis: `${elec * 100}%` }}>
              {Math.round(elec * 100)}% electric
            </span>
            <span className={styles.splitGas} style={{ flexBasis: `${gas * 100}%` }}>
              {Math.round(gas * 100)}% gas
            </span>
          </div>
          <p className={styles.body}>
            How homes on this block are heated.{" "}
            {majority === assumed
              ? `Until you tell us, we assume ${assumed} heat, the most common here.`
              : `Until you tell us, we assume ${assumed} heat.`}{" "}
            That&apos;s the first question we ask.
          </p>
        </>
      )}
      <p className={styles.fine}>Census block group {bg.geoid}, dashed on the map.</p>
    </>
  );
}

function Timeline({ year }: { year: number }) {
  const lo = 1900;
  const hi = new Date().getFullYear();
  const x = (y: number) => `${((y - lo) / (hi - lo)) * 100}%`;
  return (
    <div className={styles.timeline} aria-hidden="true">
      <span className={styles.timelineLine} />
      <span className={styles.timelineMark} style={{ left: x(year) }}>
        <i />
        built {year}
      </span>
      <span className={`${styles.timelineMark} ${styles.timelineCode}`} style={{ left: x(MI_FIRST_ENERGY_CODE) }}>
        <i />
        energy code {MI_FIRST_ENERGY_CODE}
      </span>
      <span className={styles.timelineEnd} style={{ left: 0 }}>
        {lo}
      </span>
      <span className={styles.timelineEnd} style={{ right: 0 }}>
        today
      </span>
    </div>
  );
}

function AnswersChapter({
  data,
  step,
  setStep,
}: {
  data: MapWidgetData;
  step: number;
  setStep: (s: number) => void;
}) {
  const steps = data.steps;
  const now = steps[step];
  const width = (i: number) => steps[i].lookalikes.p90 - steps[i].lookalikes.p10;
  const narrower = Math.round((1 - width(step) / width(0)) * 100);
  const seasonMax = Math.max(1, ...steps.flatMap((s) => SEASONS.map((k) => s.estimate.seasons[k])));
  return (
    <>
      <p className={styles.kicker}>Homes like yours</p>
      <p className={styles.body}>
        The U.S. Department of Energy&apos;s lab (NREL) simulated {num(data.lookalikes.pool_size)} Michigan homes in
        detail. <strong>{num(steps[0].lookalikes.count)}</strong> look like this one: {data.lookalikes.rule}. Each
        answer keeps only the homes that match it.
      </p>

      <LookalikeStrip steps={steps} step={step} />

      <div className={styles.readout} aria-live="polite">
        <div>
          <strong>{usd(now.estimate.annual_usd)}</strong>
          <span>our yearly heating + cooling estimate</span>
        </div>
        <div>
          <strong>{num(now.lookalikes.count)}</strong>
          <span>similar homes{step > 0 && narrower > 0 ? `, range ${narrower}% narrower` : ""}</span>
        </div>
      </div>

      <ul className={styles.seasons} aria-label="Estimate by season">
        {SEASONS.map((s) => {
          const v = now.estimate.seasons[s];
          return (
            <li key={s}>
              <span className={styles.seasonBar} style={{ height: `${(v / seasonMax) * 100}%` }} />
              <strong>{usd(v)}</strong>
              <span>{s}</span>
            </li>
          );
        })}
      </ul>

      <ol className={styles.questions}>
        {steps.slice(1).map((s, j) => {
          const i = j + 1;
          const done = i <= step;
          const next = i === step + 1;
          const delta = s.estimate.annual_usd - steps[i - 1].estimate.annual_usd;
          return (
            <li key={s.id} className={done ? styles.qDone : next ? styles.qNext : styles.qLater}>
              <span className={styles.qText}>{s.question}</span>
              {done ? (
                <span className={styles.qAnswer}>
                  {s.answer_label}
                  <em>
                    {signedUsd(delta)}/yr · {num(steps[i - 1].lookalikes.count)} → {num(s.lookalikes.count)} homes
                  </em>
                </span>
              ) : next ? (
                <button type="button" className={styles.qButton} onClick={() => setStep(i)}>
                  Answer: {s.answer_label}
                </button>
              ) : null}
            </li>
          );
        })}
      </ol>
      {step > 0 && (
        <button type="button" className={styles.reset} onClick={() => setStep(0)}>
          Start over
        </button>
      )}
      <p className={styles.fine}>
        How sure are we? Tested on real metered Ann Arbor buildings, half of our estimates land within ±
        {Math.round(now.estimate.typical_error * 100)}% of the real bill.
      </p>
    </>
  );
}
