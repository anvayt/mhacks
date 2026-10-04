"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Leaderboard } from "./leaderboard";
import { RankingScreen } from "./ranking-screen";

const choices = [
  {
    id: "windows",
    text: "Windows",
    options: ["Single pane", "Double pane"],
  },
  {
    id: "floor",
    text: "Floor",
    options: ["Top", "Middle", "Ground"],
  },
  {
    id: "heating-fuel",
    text: "Heating fuel and who pays it",
    options: ["Natural gas", "Heat is included in my rent"],
  },
] as const;

const questions = [
  {
    id: "insulation-year",
    label: "Insulation or air-sealing work since this year",
  },
  {
    id: "this-month-gas-bill",
    label: "This month's gas bill",
  },
] as const;

function step(current: string, delta: number) {
  const parsed = Number.parseInt(current, 10);
  const base = Number.isNaN(parsed) ? 0 : parsed;
  return String(base + delta);
}

function SurveyStepper({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="field">
      <label className="eyebrow" htmlFor={id}>
        {label}
      </label>
      <div className="control">
        <input
          id={id}
          name={id}
          inputMode="numeric"
          autoComplete="off"
          value={value}
          onChange={(event) => {
            const next = event.target.value;
            if (next === "" || /^-?\d+$/.test(next)) onChange(next);
          }}
        />
        <span className="stepper-arrows">
          <button type="button" aria-label={`Increase ${label}`} onClick={() => onChange(step(value, 1))}>
            <span className="stepper-arrow stepper-arrow-up" />
          </button>
          <button type="button" aria-label={`Decrease ${label}`} onClick={() => onChange(step(value, -1))}>
            <span className="stepper-arrow stepper-arrow-down" />
          </button>
        </span>
      </div>
    </div>
  );
}

function SurveyChoices({
  id,
  text,
  options,
  value,
  onChange,
}: {
  id: string;
  text: string;
  options: readonly string[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <fieldset className="field" id={id}>
      <legend className="eyebrow">{text}</legend>
      <div className="choice-row">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            className="control choice"
            aria-pressed={value === option}
            onClick={() => onChange(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

function LoadingSheet({ onFinished }: { onFinished: () => void }) {
  const [raised, setRaised] = useState(false);
  const [filling, setFilling] = useState(false);
  const onFinishedRef = useRef(onFinished);
  onFinishedRef.current = onFinished;

  useEffect(() => {
    const raise = requestAnimationFrame(() => setRaised(true));
    const fill = window.setTimeout(() => setFilling(true), 650);
    const lower = window.setTimeout(() => setRaised(false), 2900);
    const done = window.setTimeout(() => onFinishedRef.current(), 3600);
    return () => {
      cancelAnimationFrame(raise);
      window.clearTimeout(fill);
      window.clearTimeout(lower);
      window.clearTimeout(done);
    };
  }, []);

  return (
    <div className={raised ? "loading-sheet raised" : "loading-sheet"} role="status" aria-live="polite">
      <p className="loading-label">Loading</p>
      <div className="loading-track">
        <div className={filling ? "loading-fill run" : "loading-fill"} />
      </div>
    </div>
  );
}

export function SurveyFields() {
  const [values, setValues] = useState<Record<string, string>>({});
  const [stage, setStage] = useState<"survey" | "loading" | "score" | "board">("survey");

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStage("loading");
  }

  if (stage === "score") return <RankingScreen onNext={() => setStage("board")} />;
  if (stage === "board") return <Leaderboard />;

  return (
    <main className="survey-screen">
      <form className={stage === "loading" ? "dossier survey-leave" : "dossier"} onSubmit={onSubmit}>
      {choices.map((question) => (
        <SurveyChoices
          key={question.id}
          id={question.id}
          text={question.text}
          options={question.options}
          value={values[question.id] ?? ""}
          onChange={(value) => setValues((current) => ({ ...current, [question.id]: value }))}
        />
      ))}
      {questions.map((question) => (
        <SurveyStepper
          key={question.id}
          id={question.id}
          label={question.label}
          value={values[question.id] ?? ""}
          onChange={(value) => setValues((current) => ({ ...current, [question.id]: value }))}
        />
      ))}
      <div className="actions">
        <button className="action" type="submit">
          Next
          <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
        </button>
      </div>
    </form>
      {stage === "loading" ? <LoadingSheet onFinished={() => setStage("score")} /> : null}
    </main>
  );
}
