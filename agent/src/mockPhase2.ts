import type { Api, ApiResult, Account, Calibration, CalibrateRequest, Commitment, Estimate, HabitStreak, Me, Reminder, ReminderState, ReplyingTo, Suggestion } from "./api.ts";
import { accountHandle } from "./accounts.ts";
const ok = <T>(data: T): ApiResult<T> => ({ ok: true, data });
const fail = (code: string, message: string): ApiResult<never> => ({ ok: false, code, message });
const band = (p50: number) => ({ p10: p50 * .8, p50, p90: p50 * 1.2 });
// Local days in the API's default timezone (app/habits.py), as YYYY-MM-DD.
const localDay = (at = new Date()) => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Detroit" }).format(at);
const dayBefore = (day: string) => new Date(Date.parse(`${day}T12:00:00Z`) - 86_400_000).toISOString().slice(0, 10);

/** Deterministic demo data. The conversation labels every response; no real transport is involved. */
export class MockPhase2 {
  private next = 1;
  private phones = new Map<string, Account>();
  private users = new Map<string, Me>();
  private accepted = new Map<string, Commitment>();
  private controls = new Map<string, ReminderState>();
  private bills = new Map<string, Calibration>();
  private reminders = new Map<string, Reminder>();
  private sent = new Set<string>();
  private habitDays = new Map<string, Set<string>>();
  private habitBest = new Map<string, number>();
  private shown = new Map<string, ReplyingTo>();
  constructor(private estimate: Api["estimate"], private session: Api["session"]) {}
  private owner(propertyId: string) { return [...this.users.values()].find((m) => m.properties.some((p) => p.id === propertyId)); }
  private reminder(user_id: string, kind: Reminder["kind"] = "checkin"): ApiResult<Reminder> {
    const me = this.users.get(user_id); if (!me?.current_property_id) return fail("no_reminder", "Save a home first.");
    if (this.controls.get(user_id)?.stopped || this.controls.get(user_id)?.paused || me.reminder_prefs.paused || me.reminder_prefs.cadence === "off") return fail("no_reminder", "Reminders are stopped or paused.");
    const task = kind === "task" ? [...this.accepted.values()].find((c) => c.property_id === me.current_property_id && c.status === "accepted") : undefined;
    if (kind === "task" && !task) return fail("no_reminder", "No reminder is available. Accept a commitment with a target date first.");
    const id = `demo-reminder-${user_id}-${this.next++}`;
    const h = this.streak(user_id);
    const text_hint = task ? `Demo data: your target for ${task.title}. ${h.current ? `Habit streak ${h.current} days; reply done to keep it.` : "Reply done once you've done it today to start a habit streak."}` : `Demo data: still at ${me.current_estimate?.building.address}?`;
    const r: Reminder = { reminder_id: id, user_id, handle: [...this.phones].find(([, a]) => a.user_id === user_id)![0], kind: task ? "task" : "checkin", text_hint, property_id: me.current_property_id, ...(task ? { commitment_id: task.id } : {}), demo: true };
    this.reminders.set(id, r); this.shown.set(user_id, { reminder_id: id, kind: r.kind, local_date: localDay(), ...(task ? { commitment_id: task.id } : {}) });
    return ok(r);
  }
  /** app/habits.py's rule: consecutive local days ending today, or yesterday while today is pending. */
  private streak(user_id: string): HabitStreak {
    const days = this.habitDays.get(user_id) ?? new Set<string>(); const today = localDay();
    let day = days.has(today) ? today : dayBefore(today), current = 0;
    while (days.has(day)) { current++; day = dayBefore(day); }
    const best = Math.max(current, this.habitBest.get(user_id) ?? 0); this.habitBest.set(user_id, best);
    return { current, best, checked_in_today: days.has(today), last_checkin_date: [...days].sort().at(-1) ?? null, badges: [3, 7].filter((n) => best >= n).map((n) => `habit-${n}`) };
  }
  async bill(req: CalibrateRequest, data: Calibration): Promise<Calibration> {
    if (!req.property_id) return data;
    const key = `${req.property_id}:${"start" in req ? req.start + req.end : req.bill_image_base64}`;
    const old = this.bills.get(key); if (old) return old;
    const result: Calibration = { ...data, meaningful: false, noise_floor: 100, bill_id: `demo-bill-${this.next++}`, verified: false,
      snapshot: { source: "bill_regrade", grade: "A", provisional: true, label: "early signal from one bill: inside normal month-to-month variation, so your grade doesn't change" },
      bill_signal: { grade: "A", score: 90, annual_usd: 1000, label: "early signal" },
      ...("amount_usd" in req ? { extracted: { estimated_from_amount: true, note: "Demo gas usage estimated from your bill amount." } } : {}) };
    this.bills.set(key, result); return result;
  }
  readonly methods: Pick<Api, "authPhone" | "confirmLogin" | "me" | "patchMe" | "property" | "checkin" | "suggestions" | "commitments" | "commit" | "updateCommitment" | "projection" | "remindersDue" | "reminderSent" | "reminderInbound" | "reminderControl" | "reminderDemo" | "calendarConnect" | "calendarReminder" | "habitCheckin" | "habits" | "fastForward"> = {
    authPhone: async (req) => {
      const phone = accountHandle(req.phone); let a = this.phones.get(phone); const created = !a;
      if (!a) {
        a = { user_id: `demo-user-${this.next++}`, created: true, current_property_id: null }; this.phones.set(phone, a);
        this.users.set(a.user_id, { user_id: a.user_id, current_property_id: null, properties: [], current_estimate: null, current_grade: null, pending_checkin: null, calendar_connected: false, timezone: "America/Detroit", reminder_prefs: { channel: "imessage", cadence: "monthly", hour_local: 10, paused: false } });
      }
      if (req.session_id && !this.users.get(a.user_id)!.current_property_id) await this.methods.property({ user_id: a.user_id, session_id: req.session_id });
      return ok({ ...a, created, current_property_id: this.users.get(a.user_id)!.current_property_id });
    },
    confirmLogin: async ({ code, phone }) => /^\d{6}$/.test(code) ? this.methods.authPhone({ phone }) : fail("bad_code", "That login code wasn't found."),
    me: async (id) => { const me = this.users.get(id); if (!me) return fail("not_found", "Account not found."); if (me.current_estimate?.session_id) { const s = await this.session(me.current_estimate.session_id); if (s.ok) me.current_estimate = s.data; } return ok(structuredClone(me)); },
    patchMe: async (id, req) => { const m = this.users.get(id); if (!m) return fail("not_found", "Account not found."); if ("pending_checkin" in req) m.pending_checkin = null; if (req.reminder_prefs) Object.assign(m.reminder_prefs, req.reminder_prefs); return this.methods.me(id); },
    property: async (req) => {
      const m = this.users.get(req.user_id); if (!m) return fail("not_found", "Account not found.");
      const e = "session_id" in req ? await this.session(req.session_id) : await this.estimate(req);
      if (!e.ok) return e;
      const existing = m.properties.find((p) => p.session_id === e.data.session_id);
      const id = existing?.id ?? `demo-property-${this.next++}`;
      m.properties.forEach((p) => p.active = p.id === id);
      if (!existing) m.properties.push({ id, user_id: req.user_id, address: e.data.building.address!, session_id: e.data.session_id!, active: true });
      m.current_property_id = id; m.current_estimate = e.data; m.pending_checkin = null;
      m.current_grade = { source: "initial_estimate", grade: e.data.grade!, score: e.data.score!, bill_annual: e.data.bill.annual };
      return ok({ property_id: id, estimate: e.data, active: true });
    },
    checkin: async (id) => { const m = this.users.get(id); if (!m?.current_property_id) return fail("no_property", "Save a home first."); m.pending_checkin = { property_id: m.current_property_id, address: m.current_estimate!.building.address!, created_at: new Date().toISOString(), message_hint: "still_at_address" }; return ok(m.pending_checkin); },
    suggestions: async () => ok({ commitments: [
      { catalog_id: "window_upgrade", title: "Upgrade single-pane windows", who_acts: "landlord", pending_model: false, grh_points: 4, projected: { usd_saved_yr: 125, co2_kg_saved_yr: 699, score_delta: 11, new_grade: "B", label: "projected_if_completed" } },
      { catalog_id: "air_sealing", title: "Air sealing", who_acts: "landlord", pending_model: true, grh_points: null, projected: null },
      { catalog_id: "thermostat_setback", title: "Thermostat setback", who_acts: "renter", pending_model: true, grh_points: null, projected: null, note: "Never set below 64°F (WHO minimum for healthy adults); keep vulnerable people warmer." },
    ] satisfies Suggestion[] }),
    commitments: async (id) => ok({ commitments: [...this.accepted.values()].filter((c) => c.property_id === id) }),
    commit: async (req) => { const existing = [...this.accepted.values()].find((c) => c.property_id === req.property_id && c.catalog_id === req.catalog_id && c.status === "accepted"); if (existing) return ok(existing); const c: Commitment = { ...req, id: `demo-commitment-${this.next++}`, title: req.catalog_id.replace(/_/g, " "), status: "accepted", evidence: "projected" }; this.accepted.set(c.id, c); return ok(c); },
    updateCommitment: async (id, status) => { const c = this.accepted.get(id); if (!c) return fail("not_found", "Commitment not found."); if (c.status !== "accepted") return fail("bad_transition", "That commitment is no longer accepted."); c.status = status; c.evidence = status === "completed" ? "reported" : "projected"; return ok(c); },
    projection: async (req) => { const m = this.owner(req.property_id); if (!m) return fail("not_found", "Property not found."); const modeled = req.commitment_ids.filter((id) => (this.accepted.get(id)?.catalog_id ?? id) === "window_upgrade"); return ok({ label: "projected_if_completed", current: { grade: m.current_estimate!.grade!, score: m.current_estimate!.score!, bill_annual: m.current_estimate!.bill.annual, co2_kg_yr: band(2100) }, projected: { grade: "B", score: 70, bill_annual: band(1235), co2_kg_yr: band(1401), label: "projected_if_completed" }, delta: { usd_saved_yr: 125, co2_kg_saved_yr: 699, score: 11, label: "projected_if_completed" }, modeled, not_modeled: req.commitment_ids.filter((id) => !modeled.includes(id)) }); },
    remindersDue: async () => ok([...this.reminders.values()].filter((r) => !this.sent.has(r.reminder_id) && !this.controls.get(r.user_id)?.stopped && !this.controls.get(r.user_id)?.paused)),
    reminderSent: async (id) => { const r = this.reminders.get(id); if (!r) return fail("not_found", "Reminder not found."); const s = this.controls.get(r.user_id) ?? { stopped: false, paused: false, unanswered: 0 }; if (!this.sent.has(id)) s.unanswered = (s.unanswered ?? 0) + 1; if (s.unanswered! >= 2) s.paused = true; this.sent.add(id); this.controls.set(r.user_id, s); return ok(s); },
    reminderInbound: async (id) => { const s = this.controls.get(id) ?? { stopped: false, paused: false }; s.unanswered = 0; this.controls.set(id, s); const replying_to = this.shown.get(id) ?? null; this.shown.delete(id); return ok({ ...s, replying_to }); },
    reminderControl: async (id, action) => { const s = this.controls.get(id) ?? { stopped: false, paused: false }; s.stopped = action === "stop" ? true : action === "resume" ? false : s.stopped; s.paused = action !== "resume"; this.controls.set(id, s); return ok(s); },
    reminderDemo: async (id, kind) => this.reminder(id, kind),
    habitCheckin: async (id, req) => {
      const me = this.users.get(id); if (!me) return fail("not_found", "Account not found.");
      const habits = [...this.accepted.values()].filter((c) => c.property_id === me.current_property_id && c.status !== "dismissed");
      if (!habits.length) return fail("no_habits", "Pick a daily habit first: text 'options'");
      const today = localDay(), day = req.date ?? today;
      if (day !== today && day !== dayBefore(today)) return fail("bad_date", "You can check in for today, or for yesterday right after midnight.");
      if (req.commitment_id && !habits.some((c) => c.id === req.commitment_id)) return fail("unknown_commitment", "That isn't one of your daily habits. Text 'options' to see them.");
      const days = this.habitDays.get(id) ?? new Set<string>(); days.add(day); this.habitDays.set(id, days);
      return ok(this.streak(id));
    },
    habits: async (id) => this.users.has(id) ? ok(this.streak(id)) : fail("not_found", "Account not found."),
    // Demo data: only window_upgrade is "modeled" (the mock projection's $125 / 699 kg a year), spread flat.
    fastForward: async ({ property_id, days }) => {
      const m = this.owner(property_id); if (!m) return fail("property_not_found", "Property not found.");
      if (days < 1 || days > 365) return fail("bad_days", "Fast-forward 1 to 365 days.");
      const mine = [...this.accepted.values()].filter((c) => c.property_id === property_id && c.status !== "dismissed");
      const modeled = mine.some((c) => c.catalog_id === "window_upgrade"), share = modeled ? days / 365 : 0;
      const real = this.streak(m.user_id).current;
      return ok({ label: "simulated_projected_if_kept", label_text: "Simulated · projected if you keep your commitments",
        totals: { days, end_date: new Date(Date.now() + days * 86_400_000).toISOString().slice(0, 10), usd_saved: Math.round(125 * share * 100) / 100, kg_co2_saved: Math.round(699 * share * 100) / 100 },
        commitments: mine.map((c) => ({ catalog_id: c.catalog_id, title: c.title, modeled: c.catalog_id === "window_upgrade" })),
        not_modeled: mine.filter((c) => c.catalog_id !== "window_upgrade").map((c) => c.catalog_id), real_habit_streak: real, simulated_habit_streak: real + days });
    },
    calendarConnect: async (id) => { const m = this.users.get(id); if (!m) return fail("not_found", "Account not found."); m.calendar_connected = true; return ok({ auth_url: "https://example.com/calendar-demo", mock: true, message: "Demo data: Calendar connection simulated." }); },
    calendarReminder: async (req) => { if (!this.users.get(req.user_id)?.calendar_connected) return fail("calendar_not_connected", "Connect Calendar first."); const c = this.accepted.get(req.commitment_id); if (!c || c.status !== "accepted") return fail("commitment_not_accepted", "An accepted commitment is required."); c.calendar_event_id = `demo-event-${c.id}`; return ok({ reminder_id: `demo-calendar-${c.id}`, event_id: c.calendar_event_id, html_link: null, mock: true }); },
  };
}
