"use client";

import { FormEvent, useState } from "react";

export function ListingForm() {
  const [listing, setListing] = useState("");

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
        <button className="action" type="submit">
          Find my hidden rent
          <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
        </button>
        <a className="imessage" href="sms:">
          Or start by iMessage ↗
        </a>
      </div>
      <p className="fine-print">Use a listing URL or address. No account needed to explore this design.</p>
    </form>
  );
}
