"use client";

import { SignInButton } from "./sign-in-button";
import { backgroundColorAt, mockPeers } from "./mocks/leaderboard";

const highest = Math.max(...mockPeers.map((peer) => peer.annualUsd));

export function Leaderboard() {
  return (
    <main className="hero ranking">
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
            {mockPeers.map((peer, index) => (
              <li key={peer.id} className={peer.you ? "board-col you" : "board-col"}>
                <span className="board-value">${peer.annualUsd.toLocaleString("en-US")}</span>
                <span className="board-track">
                  <span
                    className="board-bar"
                    style={{
                      height: `${(peer.annualUsd / highest) * 100}%`,
                      background: backgroundColorAt(index / (mockPeers.length - 1)),
                    }}
                  />
                </span>
                <span className="board-label">{peer.label}</span>
              </li>
            ))}
          </ol>
          <SignInButton />
        </section>
      </div>
    </main>
  );
}
