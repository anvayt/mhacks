"use client";

import { useEffect, useState } from "react";

export function RankingScreen({ onNext }: { onNext: () => void }) {
  const [nextReady, setNextReady] = useState(false);

  useEffect(() => {
    const enable = window.setTimeout(() => setNextReady(true), 5400);
    return () => window.clearTimeout(enable);
  }, []);

  return (
    <main className="hero ranking">
      <div className="hero-decor" aria-hidden="true">
        <img className="halo" src="/hero/halo.svg" alt="" />
        <img className="orbit" src="/hero/orbit.svg" alt="" />
        <img className="texture" src="/hero/texture.svg" alt="" />
      </div>
      <div className="ranking-inner">
        <header className="ranking-toolbar">
          <p>Rental dossier / Ann Arbor, Michigan / No listing supplied</p>
          <div className="ranking-actions">
            <button className="ghost-action" type="button">
              Compare listing
              <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
            </button>
            <button className="ghost-action" type="button">
              Share preview
              <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
            </button>
          </div>
        </header>
        <p className="ranking-notice">Illustrative ranking state · not a measured property</p>
        <section className="ranking-body">
          <div className="ranking-copy score-reveal">
            <h1>Middle 50%</h1>
            <p className="ranking-subhead">Right in the middle of the spectrum.</p>
            <p className="ranking-detail">
              Red and blue in balance. A midpoint example within the same building-type peer group.
            </p>
            <p className="ranking-source">Ann Arbor same-type peers · illustrative score, not a live city rank</p>
          </div>
          <aside className="ranking-card score-reveal score-reveal-late">
            <p className="eyebrow">Predicted score / illustration</p>
            <div className="ranking-score">
              <p className="ranking-number">50</p>
              <p className="ranking-grade">C</p>
            </div>
            <div className="ranking-score-labels">
              <p>Out of 100</p>
              <p>Example grade</p>
            </div>
            <div className="ranking-rule" />
            <p className="ranking-awaiting">
              Actual predicted score / grade:
              <br />
              — · awaiting estimate
            </p>
          </aside>
        </section>
        <button className="ghost-action ranking-next" type="button" disabled={!nextReady} onClick={onNext}>
          Next
          <img src="/hero/arrow-up-right-ink.svg" alt="" width={16} height={16} />
        </button>
      </div>
    </main>
  );
}
