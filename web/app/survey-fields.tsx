"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";
import { answer, currentEstimate, gradeStatus, usdRange, type Estimate, type Option, type Question } from "./flow-api";
import { ApiError } from "./lib/api";

// P3's option for renters whose heat is in the rent (team decision 4); the API serves it from wave 6.
const HEAT_INCLUDED: Option = { value: "included", label: "Heat is included in my rent" };

function withIncluded(q: Question): Question {
  if (q.id !== "heating_fuel" || q.options.some((o) => o.value === HEAT_INCLUDED.value)) return q;
  return { ...q, options: [...q.options, HEAT_INCLUDED] };
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
  options: readonly Option[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <fieldset className="field" id={id}>
      <legend className="eyebrow">{text}</legend>
      <div className="choice-row">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className="control choice"
            aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

/** P3's loading sheet. With `ready`, it stays up until ready is true (a first lookup can take a minute). */
export function LoadingSheet({ onFinished, ready = true }: { onFinished: () => void; ready?: boolean }) {
  const [raised, setRaised] = useState(false);
  const [filling, setFilling] = useState(false);
  const [minDone, setMinDone] = useState(false);
  const onFinishedRef = useRef(onFinished);
  onFinishedRef.current = onFinished;

  useEffect(() => {
    const raise = requestAnimationFrame(() => setRaised(true));
    const fill = window.setTimeout(() => setFilling(true), 900);
    const min = window.setTimeout(() => setMinDone(true), 4600);
    return () => {
      cancelAnimationFrame(raise);
      window.clearTimeout(fill);
      window.clearTimeout(min);
    };
  }, []);

  useEffect(() => {
    if (!minDone || !ready) return;
    setRaised(false);
    const done = window.setTimeout(() => onFinishedRef.current(), 900);
    return () => window.clearTimeout(done);
  }, [minDone, ready]);

  return (
    <div className={raised ? "loading-sheet raised" : "loading-sheet"} role="status" aria-live="polite">
      <p className="loading-label">{minDone && !ready ? "Looking up city records · first lookups take up to a minute" : "Loading"}</p>
      <div className="loading-track">
        <div className={filling ? "loading-fill run" : "loading-fill"} />
      </div>
    </div>
  );
}

export function SurveyFields({ onNext, leaving = false }: { onNext: () => void; leaving?: boolean }) {
  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [shown, setShown] = useState<Question[]>([]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [exit, setExit] = useState(false);

  // Answered questions stay where they are (pressed); questions the API stops asking go; new ones join at the end.
  function take(e: Estimate) {
    setEstimate(e);
    setShown((current) => {
      const live = new Set([...Object.keys(e.answers ?? {}), ...e.questions.map((q) => q.id)]);
      const added = e.questions.filter((q) => !current.some((c) => c.id === q.id)).map(withIncluded);
      return [...current.filter((q) => live.has(q.id)), ...added];
    });
  }

  useEffect(() => {
    currentEstimate()
      .then((e) => {
        take(e);
        setValues(e.answers ?? {});
      })
      .catch((err: ApiError) => setMessage(err.message));
  }, []);

  async function pick(questionId: string, value: string) {
    const previous = values[questionId];
    if (pending || previous === value) return;
    setValues((current) => ({ ...current, [questionId]: value }));
    setPending(true);
    setMessage(null);
    try {
      take(await answer(questionId, value));
    } catch (err) {
      setValues((current) => ({ ...current, [questionId]: previous ?? "" }));
      setMessage((err as ApiError).message);
    } finally {
      setPending(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setExit(true);
    window.setTimeout(onNext, 900);
  }

  const range = estimate ? usdRange(estimate.bill.annual) : null;
  const status = pending
    ? "Updating your estimate…"
    : message ??
      (estimate
        ? `Predicted grade ${gradeStatus(estimate)}${range ? ` · heating + cooling ${range} a year` : ""}`
        : "Loading your questions…");

  return (
    <main className="survey-screen dim-screen">
      <form className={leaving || exit ? "dossier survey-leave" : "dossier"} onSubmit={onSubmit}>
        {shown.map((question) => (
          <SurveyChoices
            key={question.id}
            id={question.id}
            text={question.text}
            options={question.options}
            value={values[question.id] ?? ""}
            onChange={(value) => pick(question.id, value)}
          />
        ))}
        {estimate && shown.length === 0 ? (
          <p className="eyebrow">No questions for this home: no answer would change its estimate.</p>
        ) : null}
        <div className="actions">
          <div className="action-row">
            <Link className="back-action" href="/address">
              <span className="back-arrow" aria-hidden="true" />
              Back
            </Link>
            <button className="action" type="submit" disabled={!estimate || pending}>
              Next
              <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
            </button>
          </div>
        </div>
        <p className="fine-print" aria-live="polite">
          {status}
        </p>
      </form>
    </main>
  );
}
