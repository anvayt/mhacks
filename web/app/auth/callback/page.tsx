"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

const STATE_KEY = "hiddenrent_oauth_state";

function CallbackStatus() {
  const params = useSearchParams();
  const [message, setMessage] = useState("Checking the sign-in return…");

  useEffect(() => {
    const returned = params.get("state");
    const expected = sessionStorage.getItem(STATE_KEY);
    const error = params.get("error");
    const code = params.get("code");
    if (!returned || returned !== expected) {
      setMessage("Sign-in was interrupted. Start again from the scores screen.");
      return;
    }
    sessionStorage.removeItem(STATE_KEY);
    if (error === "provider_unconfigured") {
      setMessage("The sign-in screen is ready. Add the OAuth authorize URL and client id to connect a provider.");
      return;
    }
    if (error) {
      setMessage("The provider declined sign-in. Your scores are still on this device.");
      return;
    }
    if (code) {
      setMessage("The provider sent a sign-in code. Scores can be saved once the server exchanges that code.");
      return;
    }
    setMessage("Sign-in returned without a code. Your scores are still on this device.");
  }, [params]);

  return <p className="board-note">{message}</p>;
}

export default function AuthCallbackPage() {
  return (
    <main className="survey-screen">
      <section className="dossier sign-in-card">
        <p className="eyebrow">Account</p>
        <h1 className="board-title">Sign in to save your scores</h1>
        <Suspense fallback={<p className="board-note">Checking the sign-in return…</p>}>
          <CallbackStatus />
        </Suspense>
      </section>
    </main>
  );
}
