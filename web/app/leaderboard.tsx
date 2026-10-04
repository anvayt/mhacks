"use client";

import { useState, type CSSProperties } from "react";
import { ListingForm } from "./listing-form";
import { SignInButton } from "./sign-in-button";
import { commitments } from "./mocks/commitments";
import { backgroundColorAt, mockPeers } from "./mocks/leaderboard";

const highest = Math.max(...mockPeers.map((peer) => peer.annualUsd));
const startIndex = mockPeers.findIndex((peer) => peer.you);

function gradientStops(position: number): CSSProperties {
  const blueEnd = Math.round((75 - position * 60) * 100) / 100;
  const redStart = Math.min(100, blueEnd + 25);
  return { "--blue-end": `${blueEnd}%`, "--red-start": `${redStart}%` };
}

export function Leaderboard() {
  const [chosen, setChosen] = useState<string[]>([]);
  const [monthly, setMonthly] = useState<"ask" | "address" | "bill">("ask");
  const [bill, setBill] = useState("");
  const youIndex = Math.max(0, startIndex - chosen.length);
  const rows = mockPeers.map((peer, index) => ({
    ...peer,
    label: index === youIndex ? "You" : `Peer ${index + 1}`,
    you: index === youIndex,
  }));

  function toggle(id: string) {
    setChosen((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  function stepBill(delta: number) {
    const parsed = Number.parseInt(bill, 10);
    const base = Number.isNaN(parsed) ? 0 : parsed;
    setBill(String(base + delta));
  }

  return (
    <main className="hero ranking board-screen" style={gradientStops(youIndex / (mockPeers.length - 1))}>
      <div className="hero-decor" aria-hidden="true">
        <img className="halo" src="/hero/halo.svg" alt="" />
        <img className="orbit" src="/hero/orbit.svg" alt="" />
        <img className="texture" src="/hero/texture.svg" alt="" />
      </div>
      <div className="ranking-inner">
        <p className="ranking-notice">Mock leaderboard · same-type peers · not a live city rank</p>
        <section className="board">
          <h1 className="board-title">Same-type peers</h1>
          <p className="board-note">
            Bars run from the documented P10 ($1,052) to P90 ($2,254) annual bill for this size. Left and blue
            match the low-cost side of the page. Right and red match the high-cost side. Your illustrated place
            sits at the midpoint.
          </p>
          <ol className="board-chart">
            {rows.map((peer, index) => (
              <li key={peer.id} className={peer.you ? "board-col you" : "board-col"}>
                <span className="board-value">${peer.annualUsd.toLocaleString("en-US")}</span>
                <span className="board-track">
                  <span
                    className="board-bar"
                    style={{
                      height: `${(peer.annualUsd / highest) * 100}%`,
                      background: backgroundColorAt(index / (rows.length - 1)),
                    }}
                  />
                </span>
                <span className="board-label">{peer.label}</span>
              </li>
            ))}
          </ol>
          <div className="field">
            <p className="eyebrow">Commitments</p>
            <p className="board-note">
              Hardcoded for now. Each one moves you one step toward the lower bill. The model has not scored these
              yet.
            </p>
            <div className="choice-row">
              {commitments.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className="control choice"
                  aria-pressed={chosen.includes(item.id)}
                  onClick={() => toggle(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <p className="eyebrow">Change address?</p>
            <div className="choice-row">
              <button type="button" className="control choice" aria-pressed={monthly === "address"} onClick={() => setMonthly("address")}>
                Yes
              </button>
              <button type="button" className="control choice" aria-pressed={monthly === "bill"} onClick={() => setMonthly("bill")}>
                No
              </button>
            </div>
          </div>
          {monthly === "address" ? <ListingForm /> : null}
          {monthly === "bill" ? (
            <div className="field">
              <label className="eyebrow" htmlFor="electricity-bill">
                This month&apos;s electricity bill
              </label>
              <div className="control">
                <input
                  id="electricity-bill"
                  inputMode="numeric"
                  autoComplete="off"
                  value={bill}
                  onChange={(event) => {
                    const next = event.target.value;
                    if (next === "" || /^-?\d+$/.test(next)) setBill(next);
                  }}
                />
                <span className="stepper-arrows">
                  <button type="button" aria-label="Increase this month's electricity bill" onClick={() => stepBill(1)}>
                    <span className="stepper-arrow stepper-arrow-up" />
                  </button>
                  <button type="button" aria-label="Decrease this month's electricity bill" onClick={() => stepBill(-1)}>
                    <span className="stepper-arrow stepper-arrow-down" />
                  </button>
                </span>
              </div>
            </div>
          ) : null}
          <SignInButton />
        </section>
      </div>
    </main>
  );
}
