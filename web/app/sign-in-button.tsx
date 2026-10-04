"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useRef, useState } from "react";
import { adoptSession, errorText, loginStatus, startLogin, verifyLogin, type WebLogin } from "./flow-api";
import { ApiError, load, save } from "./lib/api";
import { REMINDER_CHOICES, REMINDER_RULES, saveReminderChoice, type Cadence } from "./reminder-settings";

/** Shown on the phone and code steps; the opt-in step after verification has its own heading. */
function SignUpHeader() {
  return (
    <>
      <p className="eyebrow">Sign in or sign up</p>
      <h1 className="board-title">Save your home and progress</h1>
      <ul className="board-note" style={{ margin: 0, paddingLeft: 20, lineHeight: 1.8 }}>
        <li>Keep your grade and answers when you come back</li>
        <li>Save commitments and track the carbon and money you cut</li>
        <li>Optional monthly check-ins by text: you choose on the next step</li>
      </ul>
    </>
  );
}

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

/** Phone number = login, Duo-style: we text a 6-digit code, the renter types it here (fallback: they text us). */
export function PhoneSignIn() {
  const router = useRouter();
  const next = safeNext(useSearchParams().get("next"), "/board");
  const [phone, setPhone] = useState("");
  const [login, setLogin] = useState<WebLogin | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [cadence, setCadence] = useState<Cadence>("off"); // chosen on the phone step; nothing preselected
  const [typed, setTyped] = useState("");
  const [sent, setSent] = useState(false);
  const finishing = useRef(false);

  // Just verified: this session becomes the new account's home. A failed save never blocks the grade.
  async function finish() {
    if (finishing.current) return; // the typed code and the fallback poll can both see the same sign-in
    finishing.current = true;
    setMessage("Signed in. Saving this home to your account…");
    try {
      await adoptSession();
      setMessage(null);
    } catch (err) {
      setMessage(`This home wasn't saved to your account: ${errorText(err)} Your grade still works.`);
    }
    const uid = load("user");
    if (uid && cadence !== "off") {
      try {
        await saveReminderChoice(uid, cadence);
      } catch (err) {
        setMessage(`Signed in, but your reminder choice wasn't saved: ${errorText(err)} Change it on your board.`);
        finishing.current = false;
        setLogin(null);
        return;
      }
    }
    router.push(next);
  }

  async function verify(code: string) {
    if (!login || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      const s = await verifyLogin(login.login_id, code);
      if (s.token && s.user_id) {
        save("token", s.token);
        save("user", s.user_id);
      }
      await finish();
    } catch (err) {
      setMessage(errorText(err));
      setTyped("");
    } finally {
      setBusy(false);
    }
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
        if (s.status === "pending") return void setSent(!!s.sent);
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
      setTyped("");
      setSent(false);
      setLogin(await startLogin(phone));
    } catch (err) {
      setMessage(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  const skip = (
    <Link className="back-action" href={next}>
      Skip for now
    </Link>
  );

  if (login) {
    const last4 = login.assigned_number_masked?.replace(/\D/g, "").slice(-4);
    return (
      <>
        <p className="eyebrow">Step 2 of 2 · Check your Messages</p>
        <h1 className="board-title" style={{ textTransform: "none" }}>Enter the 6-digit code we texted you</h1>
        <p className="board-note">
          {login.delivery === "dev"
            ? `Dev mode: no texting service is set up, so here's your code: ${login.dev_sent_code}.`
            : `We sent it by iMessage to ${login.phone_masked}${last4 ? ` from Hidden Rent's number ending in ${last4}` : ""}. It may show as an unknown sender.`}{" "}
          {login.delivery !== "dev" && (sent ? "Sent ✓" : "Sending…")}
        </p>
        <form className="field" onSubmit={(e) => { e.preventDefault(); void verify(typed); }}>
          <label className="eyebrow" htmlFor="code">Code</label>
          <div className="control">
            <input id="code" name="code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9 ]*" maxLength={7}
              placeholder="123456" value={typed} autoFocus
              onChange={(e) => { const v = e.target.value.replace(/[^0-9 ]/g, ""); setTyped(v); if (v.replace(/\D/g, "").length === 6) void verify(v); }} />
          </div>
          <div className="action-row" style={{ flexWrap: "wrap" }}>
            <button type="button" className="back-action" onClick={() => { setLogin(null); setMessage(null); }}>Use a different number</button>
            <button type="button" className="back-action" disabled={busy} onClick={() => void onSubmit({ preventDefault() {} } as FormEvent<HTMLFormElement>)}>Send a new code</button>
            <button className="action" type="submit" disabled={busy || typed.replace(/\D/g, "").length !== 6}>
              Verify
              <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
            </button>
          </div>
        </form>
        <p className="fine-print" aria-live="polite">{message ?? "The code works for 10 minutes."}</p>
        <details className="fine-print">
          <summary>No text after a minute? Text us instead</summary>
          From {phone}, send <strong>{login.text_body}</strong> to Hidden Rent. On your iPhone,{" "}
          <a href={login.redirect_url}>open Messages with it typed in</a>. This page signs you in by itself once it arrives.
        </details>
        {skip}
      </>
    );
  }

  return (
    <>
    <SignUpHeader />
    <form className="field" onSubmit={onSubmit}>
      <p className="board-note">
        Step 1 of 2: enter your phone number. We&apos;ll text you a 6-digit code by iMessage; type it on the next screen.
        No password, no app.
      </p>
      <label className="eyebrow" htmlFor="phone">
        Your phone number (this is your account)
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
      <fieldset className="field" style={{ border: 0, padding: 0, margin: 0 }}>
        <legend className="eyebrow">Reminder texts (optional)</legend>
        {[{ value: "off" as Cadence, label: "No reminders", note: "We only text your sign-in code." }, ...REMINDER_CHOICES].map((c) => (
          <label key={c.value} className="board-note" style={{ display: "flex", gap: 8 }}>
            <input type="radio" name="cadence" value={c.value} checked={cadence === c.value} onChange={() => setCadence(c.value)} />
            <span><strong>{c.label}</strong>: {c.note}</span>
          </label>
        ))}
        <p className="fine-print">{REMINDER_RULES} Change it anytime on your board.</p>
      </fieldset>
      <div className="action-row" style={{ flexWrap: "wrap" }}>
        {skip}
        <button className="action" type="submit" disabled={busy}>
          Text me a code
          <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
        </button>
      </div>
      <p className="fine-print" aria-live="polite">
        {message ??
          "New here? Entering the code creates your account; returning works the same way. Skip and your grade still works."}
      </p>
    </form>
    </>
  );
}
