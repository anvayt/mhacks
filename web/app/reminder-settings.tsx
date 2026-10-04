"use client";

// Text-reminder opt-in and controls (NEW_CHANGES §9.6 / D4). Uses the API's existing account routes:
// GET/PATCH /me/{user_id} (reminder_prefs, timezone) and POST /reminders/{user_id}/pause|resume|stop.
// Nothing here texts anyone: it only saves the renter's choice; the agent sends within these rules.
import { useEffect, useState } from "react";
import { ApiError, apiFetch, load } from "./lib/api";
import styles from "./board/board.module.css";

type Cadence = "daily" | "weekly" | "monthly" | "off";
type Channel = "imessage" | "calendar" | "none";
export type ReminderPrefs = { channel: Channel; cadence: Cadence; hour_local: number; paused: boolean };
type Me = { reminder_prefs: ReminderPrefs; timezone?: string | null; habit_streak?: { current: number; best: number } };

const HOURS = Array.from({ length: 14 }, (_, i) => i + 8); // 8 AM–9 PM: the API never texts at night
const hourLabel = (h: number) => `${h % 12 === 0 ? 12 : h % 12} ${h < 12 ? "AM" : "PM"}`;
const CADENCES: { value: Exclude<Cadence, "off">; label: string; note: string }[] = [
  { value: "monthly", label: "Monthly", note: "A check-in: still at this address? Send this month's bill." },
  { value: "weekly", label: "Weekly", note: "A nudge on the commitments you picked." },
  { value: "daily", label: "Daily", note: "Your habit reminder. Reply \"done\" to keep your streak." },
];
const RULES = "At most one text a day, only between 8 AM and 9 PM. Reply STOP anytime.";

const browserZone = () => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || undefined;
  } catch {
    return undefined;
  }
};
const message = (err: unknown) => (err instanceof ApiError ? err.message : "Something went wrong. Try again.");

async function saveMe(userId: string, prefs: Partial<ReminderPrefs>): Promise<Me> {
  const timezone = browserZone();
  return apiFetch<Me>(`/me/${encodeURIComponent(userId)}`, {
    method: "PATCH",
    body: { reminder_prefs: prefs, ...(timezone ? { timezone } : {}) },
  });
}

/** Right after sign-up: one explicit question. Nothing is preselected; "No thanks" turns texts off. */
export function ReminderOptIn({ onDone }: { onDone: () => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const userId = load("user");

  async function choose(cadence: Cadence) {
    if (!userId) return onDone();
    setBusy(true);
    setError(null);
    try {
      await saveMe(userId, { cadence, channel: cadence === "off" ? "none" : "imessage", paused: false });
      onDone();
    } catch (err) {
      setError(`${message(err)} You can change this later on your board.`);
      setBusy(false);
    }
  }

  return (
    <div className="field">
      <p className="eyebrow">You&apos;re signed in</p>
      <p className="board-title" style={{ textTransform: "none" }}>Want a monthly check-in by text?</p>
      <p className="board-note">
        Once a month Hidden Rent asks if you still live here and checks your bill against the weather, so you can see
        whether your energy use actually dropped. {RULES}
      </p>
      <div className="action-row" style={{ flexWrap: "wrap" }}>
        <button type="button" className="back-action" onClick={() => choose("off")} disabled={busy}>
          No thanks
        </button>
        <button type="button" className="action" onClick={() => choose("monthly")} disabled={busy}>
          Yes, text me monthly
          <img src="/hero/arrow-up-right.svg" alt="" width={16} height={16} />
        </button>
      </div>
      <p className="fine-print" aria-live="polite">
        {error ?? (busy ? "Saving your choice…" : "You can switch to weekly or daily, pick a time, or stop anytime on your board.")}
      </p>
      {error && (
        <button type="button" className="back-action" onClick={onDone}>
          Continue
        </button>
      )}
    </div>
  );
}

/** Board section: on/off, frequency, hour, channel, and pause / resume / stop. Signed-in users only. */
export function ReminderSettings() {
  const userId = load("user");
  const [prefs, setPrefs] = useState<ReminderPrefs | null>(null);
  const [draft, setDraft] = useState<ReminderPrefs | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!userId || !load("token")) return;
    apiFetch<Me>(`/me/${encodeURIComponent(userId)}`)
      .then((me) => {
        setPrefs(me.reminder_prefs);
        setDraft(me.reminder_prefs);
      })
      .catch((err) => setError(message(err)));
  }, [userId]);

  if (!userId || !load("token")) return null;

  const on = !!draft && draft.cadence !== "off" && draft.channel !== "none";
  const dirty = !!draft && !!prefs && JSON.stringify(draft) !== JSON.stringify(prefs);
  const set = (patch: Partial<ReminderPrefs>) => draft && setDraft({ ...draft, ...patch });

  async function save() {
    if (!draft || !userId) return;
    setBusy(true);
    setError(null);
    try {
      const me = await saveMe(userId, draft);
      setPrefs(me.reminder_prefs);
      setDraft(me.reminder_prefs);
      setStatus(me.reminder_prefs.cadence === "off" ? "Text reminders are off." : "Saved. We'll text within these settings.");
    } catch (err) {
      setError(message(err));
    } finally {
      setBusy(false);
    }
  }

  async function control(action: "pause" | "resume" | "stop") {
    if (!userId) return;
    setBusy(true);
    setError(null);
    try {
      const res = await apiFetch<{ paused: boolean; reminder_prefs: ReminderPrefs }>(
        `/reminders/${encodeURIComponent(userId)}/${action}`,
        { method: "POST", body: {} },
      );
      setPrefs(res.reminder_prefs);
      setDraft(res.reminder_prefs);
      setStatus(
        action === "resume" ? "Reminders resumed." : action === "pause" ? "Reminders paused. Resume anytime." : "All reminder texts stopped.",
      );
    } catch (err) {
      setError(message(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.section} aria-labelledby="reminders-heading">
      <h2 className="eyebrow" id="reminders-heading">Text reminders</h2>
      {!draft && !error && <p role="status" className="board-note">Loading your reminder settings…</p>}
      {draft && (
        <>
          <p className="board-note">
            {prefs?.paused
              ? "Paused: we won't text you until you resume."
              : prefs && prefs.cadence !== "off" && prefs.channel !== "none"
                ? `On: ${prefs.cadence} ${prefs.channel === "calendar" ? "calendar reminders" : "texts"} around ${hourLabel(prefs.hour_local)}.`
                : "Off: we won't text you reminders."}
          </p>
          <div className="choice-row" role="group" aria-label="Text me reminders">
            <button type="button" className="control choice" aria-pressed={on} disabled={busy}
              onClick={() => set({ cadence: draft.cadence === "off" ? "monthly" : draft.cadence, channel: draft.channel === "none" ? "imessage" : draft.channel })}>
              On
            </button>
            <button type="button" className="control choice" aria-pressed={!on} disabled={busy} onClick={() => set({ cadence: "off", channel: "none" })}>
              Off
            </button>
          </div>
          {on && (
            <>
              <div className={styles.choices} role="group" aria-label="How often">
                {CADENCES.map((c) => (
                  <button key={c.value} type="button" className={`control choice ${styles.choice}`} aria-pressed={draft.cadence === c.value}
                    disabled={busy} onClick={() => set({ cadence: c.value })}>
                    <span>{c.label}</span>
                    <small>{c.note}</small>
                  </button>
                ))}
              </div>
              <div className={styles.grid}>
                <label className={styles.input}>
                  Around
                  <select value={draft.hour_local} disabled={busy} onChange={(e) => set({ hour_local: Number(e.target.value) })}>
                    {HOURS.map((h) => <option key={h} value={h}>{hourLabel(h)}</option>)}
                  </select>
                </label>
                <label className={styles.input}>
                  By
                  <select value={draft.channel} disabled={busy} onChange={(e) => set({ channel: e.target.value as Channel })}>
                    <option value="imessage">iMessage</option>
                    <option value="calendar">Calendar event</option>
                  </select>
                </label>
              </div>
              {draft.channel === "calendar" && (
                <p className="board-note">Calendar reminders need a connected calendar; connect it under Commitments.</p>
              )}
            </>
          )}
          <div className={styles.actions}>
            <button type="button" className="action" onClick={save} disabled={busy || !dirty}>
              {busy ? "Saving…" : "Save reminder settings"}
            </button>
            {prefs && prefs.cadence !== "off" && (prefs.paused
              ? <button type="button" className="control choice" onClick={() => control("resume")} disabled={busy}>Resume</button>
              : <button type="button" className="control choice" onClick={() => control("pause")} disabled={busy}>Pause</button>)}
            {prefs && prefs.cadence !== "off" && (
              <button type="button" className="control choice" onClick={() => control("stop")} disabled={busy}>Stop all texts</button>
            )}
          </div>
        </>
      )}
      <p className="fine-print">{RULES} Your number is never shown on any leaderboard.</p>
      {status && <p role="status" className={styles.status}>{status}</p>}
      {error && <p role="alert" className={`${styles.status} ${styles.error}`}>{error}</p>}
    </section>
  );
}
