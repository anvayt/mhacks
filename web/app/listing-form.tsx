"use client";

import Link from "next/link";
import { FormEvent, useRef, useState } from "react";
import { errorText, estimate, listingInput, needsUnitSize, type Estimate } from "./flow-api";
import { apiFetch } from "./lib/api";
import { LoadingSheet } from "./survey-fields";

const ONBOARD = process.env.NEXT_PUBLIC_ONBOARD_URL ?? "http://localhost:8787"; // P4's iMessage onboarding page

export function ListingForm({
  onPicked,
  submitLabel = "Find my hidden rent",
  backHref,
}: {
  /** Called once /estimate has answered (and the unit size was asked); `estimate` is that body, already the session. */
  onPicked?: (listing: string, estimate: Estimate) => void;
  submitLabel?: string;
  backHref?: string;
}) {
  const [listing, setListing] = useState("");
  const [result, setResult] = useState<string | null>(null);
  // With onPicked: the flow's own /estimate, the unit-size ask, then onPicked once the response is in.
  const [unit, setUnit] = useState<Estimate | null>(null);
  const [sqft, setSqft] = useState("");
  const [waiting, setWaiting] = useState<"no" | "busy" | "done">("no");
  const outcome = useRef<{ next: "pick" | "unit" | "stay"; estimate?: Estimate }>({ next: "stay" });
  const listingField = useRef<HTMLInputElement>(null);

  async function lookUp(unitSqft?: number) {
    setWaiting("busy");
    setResult(null);
    try {
      const e = await estimate(listing, unitSqft);
      outcome.current = { next: unitSqft === undefined && needsUnitSize(e) ? "unit" : "pick", estimate: e };
    } catch (err) {
      outcome.current = { next: "stay" };
      setResult(errorText(err));
    }
    setWaiting("done");
  }

  function afterSheet() {
    setWaiting("no");
    const { next, estimate: e } = outcome.current;
    if (next === "pick" && e) onPicked?.(listing, e);
    else if (next === "unit") setUnit(e ?? null);
    else listingField.current?.select();
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (onPicked) {
      if (!unit) return lookUp();
      const n = Number(sqft.replace(/[,\s]/g, ""));
      if (!sqft.trim()) return onPicked(listing, unit); // optional: keep the first estimate
      if (!Number.isFinite(n) || n < 100 || n > 10000) {
        setResult("Unit size should be the unit's floor area in square feet (100 to 10,000).");
        return;
      }
      return lookUp(n);
    }
    // The about page's inline check: a quick answer, not the flow's session.
    setResult("Looking it up…");
    try {
      const e = await apiFetch<Estimate>("/estimate", { body: listingInput(listing) });
      const p50 = e.bill.annual.p50;
      setResult(
        `${e.building.address}${p50 != null ? `: heating + cooling about $${Math.round(p50).toLocaleString("en-US")} a year (typical weather, predicted)` : ""}`,
      );
    } catch (err) {
      setResult(errorText(err));
    }
  }

  const b = unit?.building;
  return (
    <form className="dossier" onSubmit={onSubmit}>
      {unit ? (
        <div className="field">
          <label className="eyebrow" htmlFor="unit-sqft">
            How big is the unit in sq ft? (it&apos;s on the listing)
          </label>
          <div className="control">
            <input
              id="unit-sqft"
              name="unit-sqft"
              type="text"
              inputMode="numeric"
              autoComplete="off"
              placeholder="e.g. 750"
              value={sqft}
              onChange={(event) => setSqft(event.target.value)}
              autoFocus
            />
          </div>
        </div>
      ) : (
        <div className="field">
          <label className="eyebrow" htmlFor="listing">
            Listing link or address
          </label>
          <div className="control">
            <img src="/hero/map-pin.svg" alt="" width={20} height={20} />
            <input
              ref={listingField}
              id="listing"
              name="listing"
              type="text"
              inputMode="text"
              autoComplete="street-address"
              placeholder="Paste a Zillow, Apartments.com or Redfin link"
              value={listing}
              onChange={(event) => setListing(event.target.value)}
              required
            />
          </div>
        </div>
      )}
      <div className="actions">
        <div className="action-row">
          {unit ? (
            <button className="back-action" type="button" onClick={() => onPicked?.(listing, unit)}>
              Skip
            </button>
          ) : backHref ? (
            <Link className="back-action" href={backHref}>
              <span className="back-arrow" aria-hidden="true" />
              Back
            </Link>
          ) : null}
          <button className="action" type="submit" disabled={waiting !== "no"}>
            {submitLabel}
            <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
          </button>
        </div>
        {unit ? null : (
          <a className="imessage" href={ONBOARD}>
            Or start by iMessage ↗
          </a>
        )}
      </div>
      <p className="fine-print" aria-live="polite">
        {result ??
          (b
            ? `${b.address ?? "Found it"} · ${b.type ?? "home"}.${b.sqft != null ? ` City records give about ${Math.round(b.sqft).toLocaleString("en-US")} sq ft per unit (building floor area ÷ units, which runs high).` : ""} Optional: skip to keep the estimate.`
            : "Use a listing URL or address. No account needed.")}
      </p>
      {waiting !== "no" ? <LoadingSheet ready={waiting === "done"} onFinished={afterSheet} /> : null}
    </form>
  );
}
