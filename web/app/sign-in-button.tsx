"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { adoptSession, errorText, loginStatus, startLogin, type WebLogin } from "./flow-api";
import { ApiError, load, save } from "./lib/api";
import { ReminderOptIn } from "./reminder-settings";
import { qrMatrix } from "./share/qr";
import styles from "./signin/signin.module.css";

/** The Photon redirect as a QR: scanned with an iPhone camera it opens Messages to Hidden Rent with the code typed in. */
function MessagesQr({ url }: { url: string }) {
  const { size, cells } = qrMatrix(url);
  return (
    <svg className={styles.qr} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="QR code that opens Messages to Hidden Rent">
      <rect width={size} height={size} fill="#fff" />
      <path d={cells.map(([x, y]) => `M${x} ${y}h1v1h-1z`).join("")} fill="#11121a" />
    </svg>
  );
}

/** Shown on the phone and code steps; the opt-in step after verification has its own heading. */
function SignUpHeader({ compact = false }: { compact?: boolean }) {
  return (
    <>
      <p className="eyebrow">Sign in or sign up</p>
      <h1 className="board-title">Save your home and progress</h1>
      {!compact && <ul className="board-note" style={{ margin: 0, paddingLeft: 20, lineHeight: 1.8 }}>
        <li>Keep your grade and answers when you come back</li>
        <li>Save commitments and track your habit streak</li>
        <li>Optional monthly check-ins by text: you choose on the next step</li>
      </ul>}
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

/** Phone number = login: text "login <code>" to Hidden Rent, the agent confirms it, this page polls for the token. */
export function PhoneSignIn() {
  const router = useRouter();
  const next = safeNext(useSearchParams().get("next"), "/board");
  const [phone, setPhone] = useState("");
  const [login, setLogin] = useState<WebLogin | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [askReminders, setAskReminders] = useState(false);
  const [copied, setCopied] = useState(false); // verified: one explicit opt-in question, then continue

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
    const last4 = login.assigned_number_masked?.replace(/\D/g, "").slice(-4);
    const copyCode = () => navigator.clipboard?.writeText(login.text_body).then(() => setCopied(true), () => undefined);
    return (
      <>
        <SignUpHeader compact />
        <p className="eyebrow">Last step: text this code to Hidden Rent</p>
        <div className={styles.code}>
          <p className={styles.codeText}>{login.text_body}</p>
          <button type="button" className={`control choice ${styles.copy}`} onClick={copyCode}>
            {copied ? "Copied ✓" : "Copy"}
          </button>
        </div>
        <ol className={styles.steps}>
          <li className={styles.step}>
            <p className={styles.stepTitle}>On your iPhone · {phone}</p>
            <p className={styles.stepNote}>Opens Messages to Hidden Rent with your code already typed in. Just tap Send.</p>
            <div className="action-row" style={{ flexWrap: "wrap" }}>
              <a className="action" href={login.redirect_url} style={{ textDecoration: "none" }}>
                Open Messages
                <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
              </a>
            </div>
          </li>
          <li className={`${styles.step} ${styles.computerOnly}`}>
            <p className={styles.stepTitle}>On a computer? Scan with your iPhone camera</p>
            <div className={styles.qrRow}>
              <MessagesQr url={login.redirect_url} />
              <p className={styles.stepNote}>
                Point your iPhone camera at the code and tap the banner. Messages opens to Hidden Rent with your code typed in;
                tap Send.
              </p>
            </div>
          </li>
          <li className={styles.step}>
            <p className={styles.stepTitle}>Or type it yourself</p>
            <p className={styles.stepNote}>
              From {phone}, text <b className={styles.em}>{login.text_body}</b> to Hidden Rent&apos;s iMessage number
              {last4 ? <> ending in <b className={styles.em}>{last4}</b></> : null}. It&apos;s our texting service&apos;s number, so it may look
              unfamiliar. It has to come from the same phone number you entered.
            </p>
          </li>
        </ol>
        <p className="fine-print" aria-live="polite">
          {message ?? "Waiting for your text… This page moves on by itself once it arrives. The code works for 10 minutes."}
        </p>
        <div className="action-row" style={{ flexWrap: "wrap" }}>
          {skip}
          <button type="button" className="back-action" onClick={() => { setLogin(null); setMessage(null); setCopied(false); }}>
            Use a different number
          </button>
        </div>
      </>
    );
  }

  return (
    <>
    <SignUpHeader />
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
    </>
  );
}
