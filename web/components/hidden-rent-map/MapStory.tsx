"use client";

import { LookalikeStrip } from "./LookalikeStrip";
import { buildingTypeLabel, num, signedUsd, usd } from "./format";
import styles from "./hidden-rent-map.module.css";
import type { Focus, MapWidgetData, Season } from "./types";

const MI_FIRST_ENERGY_CODE = 1977;
const SEASONS: Season[] = ["winter", "spring", "summer", "fall"];

export interface MapStoryProps {
  data: MapWidgetData;
  step: number;
  onStepChange: (step: number) => void;
  /** Section headings move the map to what they describe. */
  onFocus?: (focus: Focus) => void;
  className?: string;
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className={styles.stat}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function Heading({ children, focus, onFocus }: { children: string; focus: Focus; onFocus?: (f: Focus) => void }) {
  return (
    <h3 className={styles.storyHeading}>
      {onFocus ? (
        <button type="button" onClick={() => onFocus(focus)}>
          {children} <span aria-hidden="true">↗</span>
        </button>
      ) : (
        children
      )}
    </h3>
  );
}

export function MapStory({ data, step: rawStep, onStepChange, onFocus, className }: MapStoryProps) {
  const steps = data.steps;
  const step = Math.min(Math.max(rawStep, 0), steps.length - 1);
  const now = steps[step];
  const b = data.building;
  const bg = data.block_group;
  const width = (i: number) => {
    const cloud = steps[i].lookalikes;
    return cloud.p90 != null && cloud.p10 != null ? cloud.p90 - cloud.p10 : 0;
  };
  const narrower = width(0) > 0 ? Math.round((1 - width(step) / width(0)) * 100) : 0;
  const seasonMax = Math.max(1, ...steps.flatMap((s) => SEASONS.map((k) => s.estimate.seasons[k])));

  return (
    <div className={`${styles.story} ${className ?? ""}`}>
      <section className={styles.storyCol}>
        <Heading focus="building" onFocus={onFocus}>
          The building
        </Heading>
        <div className={styles.stats}>
          {b.height_ft != null && <Stat value={`${b.height_ft.toFixed(1)} ft`} label="roof height" />}
          {b.stories != null && <Stat value={`${b.stories}`} label="floors" />}
          <Stat value={`${num(b.floor_area_sqft)} sq ft`} label="floor area" />
          <Stat
            value={`${num(b.unit_sqft)} sq ft`}
            label={/median|estimat|not measured/i.test(b.unit_sqft_source) ? "this unit (estimated)" : "this unit"}
          />
        </div>
        <p className={styles.fine}>Treated as {buildingTypeLabel(b.building_type)}.</p>
      </section>

      <section className={styles.storyCol}>
        <Heading focus="block" onFocus={onFocus}>
          The block
        </Heading>
        <div className={styles.stats}>
          {bg.median_year_built != null && <Stat value={`${bg.median_year_built}`} label="typical rental built" />}
          {bg.median_year_built != null && (
            <Stat
              value={bg.median_year_built < MI_FIRST_ENERGY_CODE ? "Before" : "After"}
              label={`Michigan's ${MI_FIRST_ENERGY_CODE} energy code`}
            />
          )}
        </div>
        {bg.gas_heat_share != null && bg.electric_heat_share != null && (
          <div
            className={styles.split}
            aria-label={`${Math.round(bg.electric_heat_share * 100)}% electric heat, ${Math.round(
              bg.gas_heat_share * 100,
            )}% gas heat`}
          >
            <span className={styles.splitElec} style={{ flexBasis: `${bg.electric_heat_share * 100}%` }}>
              {Math.round(bg.electric_heat_share * 100)}% electric
            </span>
            <span className={styles.splitGas} style={{ flexBasis: `${bg.gas_heat_share * 100}%` }}>
              {Math.round(bg.gas_heat_share * 100)}% gas
            </span>
          </div>
        )}
        <p className={styles.fine}>Heating fuel on this block. We assume {steps[0].estimate.heating_fuel} until you answer.</p>
      </section>

      <section className={`${styles.storyCol} ${styles.storyWide}`}>
        <Heading focus="city" onFocus={onFocus}>
          Homes like yours
        </Heading>
        <LookalikeStrip steps={steps} step={step} />
        <div className={styles.stats} aria-live="polite">
          <Stat value={usd(now.estimate.annual_usd)} label="per year, heating + cooling" />
          {now.lookalikes.count > 0 && <Stat
            value={num(now.lookalikes.count)}
            label={`similar homes${step > 0 && narrower > 0 ? `, range ${narrower}% narrower` : ""}`}
          />}
        </div>
        <ul className={styles.seasons} aria-label="Estimate by season">
          {SEASONS.map((s) => (
            <li key={s}>
              <span className={styles.seasonBar} style={{ height: `${(now.estimate.seasons[s] / seasonMax) * 100}%` }} />
              <strong>{usd(now.estimate.seasons[s])}</strong>
              <span>{s}</span>
            </li>
          ))}
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
                      {signedUsd(delta)}/yr{ s.lookalikes.count > 0 ? ` · ${num(steps[i - 1].lookalikes.count)} → ${num(s.lookalikes.count)} homes` : "" }
                    </em>
                  </span>
                ) : next ? (
                  <button type="button" className={styles.qButton} onClick={() => onStepChange(i)}>
                    {s.answer_label}
                  </button>
                ) : null}
              </li>
            );
          })}
        </ol>
        {step > 0 && (
          <button type="button" className={styles.reset} onClick={() => onStepChange(0)}>
            Start over
          </button>
        )}
        <p className={styles.fine}>
          Held-out seasonal gas median absolute error: {Math.round(now.estimate.typical_error * 100)}%.
          {" "}{data.accuracy_basis} Method: {now.estimate.method}.
        </p>
      </section>
    </div>
  );
}
