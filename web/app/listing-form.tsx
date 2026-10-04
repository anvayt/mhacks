"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"; // /api (PLAN.md §10)
const ONBOARD = process.env.NEXT_PUBLIC_ONBOARD_URL ?? "http://localhost:8787"; // P4's iMessage onboarding page

export function ListingForm({
  onPicked,
  submitLabel = "Find my hidden rent",
  backHref,
}: {
  onPicked?: (listing: string) => void;
  submitLabel?: string;
  backHref?: string;
}) {
  const [listing, setListing] = useState("");
  const [result, setResult] = useState<string | null>(null);

  // ponytail: integration wiring only; the real report card (grade, range bar, questions) is P3's to build.
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (onPicked) {
      onPicked(listing);
      return;
    }
    setResult("Looking it up…");
    const input = /https?:\/\//i.test(listing) ? { url: listing } : { address: listing };
    try {
      const res = await fetch(`${API}/estimate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      const e = await res.json();
      setResult(
        res.ok
          ? `${e.building.address}: heating + cooling about $${Math.round(e.bill.annual.p50).toLocaleString("en-US")} a year (typical weather, predicted)`
          : e.detail?.message ?? "Something went wrong. Try again.",
      );
    } catch {
      setResult("The Hidden Rent API isn't reachable right now.");
    }
  }

  return (
    <form className="dossier" onSubmit={onSubmit}>
      <div className="field">
        <label className="eyebrow" htmlFor="listing">
          Listing link or address
        </label>
        <div className="control">
          <img src="/hero/map-pin.svg" alt="" width={20} height={20} />
          <input
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
      <div className="actions">
        <div className="action-row">
          {backHref ? (
            <Link className="back-action" href={backHref}>
              <span className="back-arrow" aria-hidden="true" />
              Back
            </Link>
          ) : null}
          <button className="action" type="submit">
            {submitLabel}
            <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
          </button>
        </div>
        <a className="imessage" href={ONBOARD}>
          Or start by iMessage ↗
        </a>
      </div>
      <p className="fine-print" aria-live="polite">
        {result ?? "Use a listing URL or address. No account needed to explore this design."}
      </p>
    </form>
  );
}
