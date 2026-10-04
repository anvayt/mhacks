"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { adoptSession, errorText, loginStatus, startLogin, type WebLogin } from "./flow-api";
import { ApiError, load, save } from "./lib/api";
import { ReminderOptIn } from "./reminder-settings";

/** Only same-site paths, so ?next= can't send anyone elsewhere. */
const safeNext = (next: string | null, fallback: string) => (next && /^\/(?!\/)/.test(next) ? next : fallback);

export function SignInButton({ className = "ghost-action", next = "/board" }: { className?: string; next?: string }) {
  const router = useRouter();
  return (
    <button className={className} type="button" onClick={() => router.push(`/signin?next=${encodeURIComponent(next)}`)}>
      Sign in to save your scores
    </button>
  );
}

/** Phone number = login: text "login <code>" to Hidden Rent, the agent confirms it, this page polls for the token. */
export function PhoneSignIn() {
  const router = useRouter();
  const next = safeNext(useSearchParams().get("next"), "/board");
  const [phone, setPhone] = useState("");
  const [login, setLogin] = useState<WebLogin | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [askReminders, setAskReminders] = useState(false); // verified: one explicit opt-in question, then continue

  // Just verified: this session becomes the new account's home. A failed save never blocks the grade.
  async function finish() {
    setMessage("Signed in. Saving this home to your account…");
    try {
      await adoptSession();
      setMessage(null);
    } catch (err) {
      setMessage(`This home wasn't saved to your account: ${errorText(err)} Your grade still works.`);
    }
    setLogin(null);
    setAskReminders(true);
  }

  // Already signed in: go on without touching the saved home (the grade screen offers "Save this as my home").
  useEffect(() => {
    if (load("token") && load("user")) router.replace(next);
  }, [router, next]);

  useEffect(() => {
    if (!login) return;
    const poll = window.setInterval(async () => {
      try {
        const s = await loginStatus(login.login_id);
        if (s.status === "pending") return;
        window.clearInterval(poll);
        if (s.status === "verified") {
          if (s.token && s.user_id) {
            save("token", s.token);
            save("user", s.user_id);
          }
          if (load("token")) return void finish();
          setLogin(null); // the token is handed out once; another tab took it
          setMessage("That sign-in was already used. Start again for a new code.");
        } else {
          setLogin(null);
          setMessage("That login code expired. Start again for a new one.");
        }
      } catch (err) {
        if ((err as ApiError).status === 404) {
          window.clearInterval(poll);
          setLogin(null);
        }
        setMessage(errorText(err));
      }
    }, 2000);
    return () => window.clearInterval(poll);
  }, [login]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage(null);
    try {
      setLogin(await startLogin(phone));
    } catch (err) {
      setMessage(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  if (askReminders) {
    return (
      <>
        {message && <p className="fine-print" role="status">{message}</p>}
        <ReminderOptIn onDone={() => router.push(next)} />
      </>
    );
  }

  const skip = (
    <Link className="back-action" href={next}>
      Skip for now
    </Link>
  );

  if (login) {
    return (
      <>
        <p className="eyebrow">Text this to Hidden Rent</p>
        <p className="board-title" style={{ textTransform: "none" }}>{login.text_body}</p>
        <p className="board-note">
          Send it from {phone}
          {login.assigned_number_masked ? ` to ${login.assigned_number_masked}` : ""}. On your phone, the button opens
          Messages with it typed in.
        </p>
        <div className="action-row" style={{ flexWrap: "wrap" }}>
          {skip}
          <a className="action" href={login.redirect_url} style={{ textDecoration: "none" }}>
            Open Messages
            <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
          </a>
        </div>
        <p className="fine-print" aria-live="polite">
          {message ?? "Waiting for your text… The code works for 10 minutes."}
        </p>
      </>
    );
  }

  return (
    <form className="field" onSubmit={onSubmit}>
      <label className="eyebrow" htmlFor="phone">
        Your phone number is your account
      </label>
      <div className="control">
        <input
          id="phone"
          name="phone"
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          placeholder="(734) 555-0142"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          required
        />
      </div>
      <div className="action-row" style={{ flexWrap: "wrap" }}>
        {skip}
        <button className="action" type="submit" disabled={busy}>
          Text me a code
          <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
        </button>
      </div>
      <p className="fine-print" aria-live="polite">
        {message ??
          "No password. New here? Texting the code creates your account; returning works the same way. We only text you if you say yes on the next step. Skip and your grade still works."}
      </p>
    </form>
  );
}
