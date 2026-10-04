// The iMessage interview (PLAN.md §4 steps 3–5): link/address → estimate → questions one at a time → answers →
// narrower range, until the API says the grade is locked. One state per chat (Spectrum space), in memory.
import type { Api, ApiResult, Estimate, EstimateRequest, Question, Me, Suggestion, Commitment, Calibration, ReplyingTo } from "./api.ts";
import { Accounts, accountHandle, type Sender } from "./accounts.ts";
import { billResultText, fastForwardText, projectionText, suggestionsText } from "./phase2Replies.ts";
import { refInText } from "./handoff.ts";
import { billImageBase64 } from "./photo.ts";
import {
  ADDRESS,
  NEED_LISTING_FOR_BILL,
  calibrationText,
  fixesText,
  parseTypedBill,
  type Inbound,
  LINK,
  UNIT_SIZE_QUESTION,
  WELCOME,
  estimateText,
  matchOption,
  optionValue,
  questionText,
  updateText,
} from "./replies.ts";

export const LOGIN = /^login\s+(\d{6})$/i;
// Daily habit check-ins (api/app/habits.py). "done <n>" (commitment n completed) is a different intent.
export const HABIT_REPLY = /^(done|did it|did it today|✅️?|yes)[.!]*$/iu; // only when answering a task reminder
export const HABIT_TODAY = /^done today[.!]*$/i; // any time

type Pending = { kind: "checkin" } | { kind: "bill" } | { kind: "move" } | { kind: "address" } | { kind: "unit_sqft" } | { kind: "question"; question: Question };

interface ChatState {
  userId?: string;
  propertyId?: string;
  propertySession?: string;
  me?: Me;
  greeted?: boolean;
  suggestions?: Suggestion[];
  accepted?: Commitment[];
  savedSession?: string;
  replyingTo?: ReplyingTo; // the proactive reminder this text answers, from POST /reminders/inbound
  request: EstimateRequest | null;
  sessionId: string | null;
  last: Estimate | null;
  answered: Set<string>;
  pending: Pending | null;
}

const fresh = (): ChatState => ({ request: null, sessionId: null, last: null, answered: new Set(), pending: null });

export const DEMO_LABEL = "[demo data, not a real estimate]";

// Same words /api treats as skip (app/estimate.py SKIP), plus "skip …".
const SKIP = /^(skip\b.*|not sure|unsure|idk|dont know|don't know|i don't know)$/i;

export class Conversations {
  private chats = new Map<string, ChatState>();

  private accounts: Accounts;
  private calendarCreated = new Set<string>();
  private queues = new Map<string, Promise<unknown>>();
  constructor(private api: Api) { this.accounts = new Accounts(api); }

  /** The messages to send back for one inbound message in chat `chatId` (usually one; a bill photo can give three). */
  async respond(chatId: string, input: Inbound, sender?: Sender): Promise<string[]> {
    const key = sender ? accountHandle(sender.handle) : chatId;
    const previous = this.queues.get(key) ?? Promise.resolve();
    const run = previous.catch(() => {}).then(() => this.process(key, input, sender));
    this.queues.set(key, run);
    try { return await run; } finally { if (this.queues.get(key) === run) this.queues.delete(key); }
  }

  private async process(key: string, input: Inbound, sender?: Sender): Promise<string[]> {
    const s = this.state(key);
    const text = input.kind === "text" ? input.text.trim() : "";
    if (sender) {
      const auth = await this.accounts.resolve(sender, refInText(text) ?? undefined);
      if (!auth.ok) return [auth.message];
      s.userId = auth.data.user_id;
      const inbound = await this.api.reminderInbound(s.userId);
      // Losing an acknowledgement must not block a requested stop or a normal reply.
      if (!inbound.ok) console.warn(`[reminders] inbound acknowledgement failed (${inbound.code})`);
      s.replyingTo = (inbound.ok && inbound.data.replying_to) || undefined;
      if (LOGIN.test(text)) {
        const r = await this.api.confirmLogin({ code: text.match(LOGIN)![1], phone: accountHandle(sender.handle) });
        return this.label([r.ok ? "You're signed in on the web ✅" : r.message]);
      }
      const me = await this.api.me(s.userId);
      if (!me.ok) return this.label([me.message]);
      const first = !s.greeted;
      s.me = me.data;
      if (!s.sessionId || (s.propertyId && me.data.current_property_id !== s.propertyId)) this.hydrate(s, me.data);
      if (me.data.pending_checkin && s.pending?.kind !== "bill" && s.pending?.kind !== "move") s.pending = { kind: "checkin" };
      s.greeted = true;
      if (first && !auth.data.created && s.propertyId && /^(hi|hello|hey|hi hidden rent[!.]?|welcome)\b/i.test(text) && !refInText(text)) {
        s.pending = { kind: "checkin" };
        return this.label([`Welcome back, still at ${this.address(s)}? Reply yes for a bill check, or moved.`]);
      }
    }
    const out = input.kind === "photo" ? await this.bill(s, input) : [await this.handle(s, text)];
    if (s.userId && s.last?.locked && s.sessionId && s.savedSession !== s.sessionId) {
      const saved = await this.save(s);
      out.push(saved);
    }
    return this.label(out);
  }

  private label(messages: string[]): string[] { return this.api.mock ? messages.map((m, i) => i === 0 ? `${DEMO_LABEL}\n${m}` : m) : messages; }

  /** Text-only convenience; production supplies the sender handle. */
  async reply(chatId: string, text: string, sender?: Sender): Promise<string> {
    return (await this.respond(chatId, { kind: "text", text }, sender)).join("\n\n");
  }

  private hydrate(s: ChatState, me: Me) {
    s.propertyId = me.current_property_id ?? undefined;
    const property = me.properties.find((p) => p.id === me.current_property_id);
    if (property && me.current_estimate) {
      s.sessionId = property.session_id; s.propertySession = property.session_id; s.savedSession = property.session_id;
      s.last = me.current_estimate; s.request = { address: property.address };
      s.answered = new Set(Object.keys(s.last.answers ?? {}));
      s.pending = null;
      this.withNextQuestion(s, "");
    }
    if (me.pending_checkin) s.pending = { kind: "checkin" };
  }

  private address(s: ChatState) { return s.me?.properties.find((p) => p.id === s.propertyId)?.address ?? s.last?.building.address ?? "your current home"; }

  private state(chatId: string): ChatState {
    let s = this.chats.get(chatId);
    if (!s) this.chats.set(chatId, (s = fresh()));
    return s;
  }

  private async handle(s: ChatState, text: string): Promise<string> {
    if (s.userId) {
      const phase2 = await this.phase2(s, text);
      if (phase2 !== null) return phase2;
    }
    const ref = refInText(text);
    if (ref) return this.resume(s, ref);
    const typed = parseTypedBill(text);
    if (typed) return (await this.typedBill(s, typed)).join("\n\n");
    const link = text.match(LINK)?.[0];
    if (link) return this.estimate(s, { url: link });
    if (ADDRESS.test(text)) return this.estimate(s, { address: text });

    const p = s.pending;
    // A clear command works at any point, even mid-interview.
    if (s.sessionId && /^(fix|fixes|landlord|email)\b/i.test(text)) {
      const out = await this.fixes(s);
      // still mid-interview: remind them of the open question
      if (p?.kind === "question") out.push(`Back to your question:\n${questionText(p.question)}`);
      return out.join("\n\n");
    }
    if (p?.kind === "move") return this.estimate(s, { address: text });
    if (p?.kind === "bill") return 'Send a bill photo, "120 therms", "120 ccf", or "$85". Without dates I use the last full month.';
    if (p?.kind === "address") return this.estimate(s, { address: text });
    if (p?.kind === "unit_sqft") return this.unitSize(s, text);
    if (p?.kind === "question") return this.answer(s, p.question, text);
    return WELCOME;
  }

  /** New listing or address: start over in this chat. */
  private async estimate(s: ChatState, request: EstimateRequest, previous?: Estimate): Promise<string> {
    const moved = s.userId && s.propertyId && !previous;
    const property = moved ? await this.api.property({ user_id: s.userId!, ...request }) : null;
    const r = property ? (property.ok ? { ok: true as const, data: property.data.estimate } : property) : await this.api.estimate(request);
    if (property?.ok) { s.propertySession = property.data.estimate.session_id ?? undefined; s.propertyId = property.data.property_id; s.savedSession = property.data.estimate.session_id ?? undefined; s.suggestions = undefined; s.accepted = undefined; }
    if (!r.ok) return this.failure(s, r);
    if (s.propertySession && s.propertySession !== r.data.session_id) { s.propertyId = undefined; s.propertySession = undefined; s.savedSession = undefined; s.suggestions = undefined; }
    Object.assign(s, { request, sessionId: r.data.session_id, last: r.data, answered: new Set(), pending: null });
    const body = `${moved ? "Saved your new home; the old home and its history are archived. This starts a separate baseline.\n" : ""}${estimateText(r.data, previous)}`;
    // Team decision (P2-04): an estimated unit size is the first question; /estimate takes unit_sqft.
    if (r.data.building.sqft_estimated && request.unit_sqft == null) {
      s.pending = { kind: "unit_sqft" };
      return `${body}\n\n${UNIT_SIZE_QUESTION}`;
    }
    return this.withNextQuestion(s, body);
  }

  /** After move-in: bill photo → POST /calibrate → weather comparison + streak → GET /fixes → fixes + landlord email. */
  private async bill(s: ChatState, photo: Extract<Inbound, { kind: "photo" }>): Promise<string[]> {
    if (!s.sessionId) return [NEED_LISTING_FOR_BILL];
    if (s.userId && !s.propertyId) return ['This report is not saved to your current home. Say "save", then send the bill again.'];
    let bill_image_base64: string;
    try {
      bill_image_base64 = await billImageBase64(await photo.read(), photo.mimeType, photo.name);
    } catch {
      return ["I couldn't download that photo. Try sending it again."];
    }
    const c = await this.api.calibrate({ session_id: s.sessionId, ...(s.propertyId ? { property_id: s.propertyId } : {}), bill_image_base64 });
    if (!c.ok) return [c.code === "not_served" ? "Thanks! Bill checks aren't live yet; that part is still being built." : c.message];
    return this.afterBill(s, c.data);
  }

  private async fixes(s: ChatState): Promise<string[]> {
    if (!s.sessionId) return [NEED_LISTING_FOR_BILL];
    const f = await this.api.fixes(s.sessionId);
    if (!f.ok) return f.code === "not_served" ? [] : [f.message];
    return f.data.landlord_email ? [fixesText(f.data), f.data.landlord_email] : [fixesText(f.data)];
  }

  /** First text from the website handoff: "… (ref <session id>)". Continue that API session. */
  private async resume(s: ChatState, sessionId: string): Promise<string> {
    const r = await this.api.session(sessionId);
    if (!r.ok) {
      return r.code === "unreachable"
        ? r.message
        : "I couldn't find your report from the website. Send the listing link or address and I'll start fresh.";
    }
    if (s.propertySession && s.propertySession !== (r.data.session_id ?? sessionId)) { s.propertyId = undefined; s.propertySession = undefined; s.savedSession = undefined; s.suggestions = undefined; }
    const address = r.data.building.address;
    Object.assign(s, {
      request: address ? { address } : null,
      sessionId: r.data.session_id ?? sessionId,
      last: r.data,
      answered: new Set(),
      pending: null,
    });
    return this.withNextQuestion(s, `Picking up your report from the website.\n${estimateText(r.data)}`);
  }

  private async unitSize(s: ChatState, text: string): Promise<string> {
    if (/^(skip|no|idk|not sure|don'?t know)\b/i.test(text)) {
      s.pending = null;
      return this.withNextQuestion(s, "OK, keeping the estimated size.");
    }
    const n = Number(text.replace(/,/g, "").match(/\d+(\.\d+)?/)?.[0]);
    if (!s.request || !Number.isFinite(n) || n <= 0) return "Send the unit size in square feet, like 750, or say skip.";
    const { unit_sqft: _drop, ...base } = s.request;
    return this.estimate(s, { ...base, unit_sqft: n }, s.last ?? undefined);
  }

  private async answer(s: ChatState, q: Question, text: string): Promise<string> {
    if (!s.sessionId) return WELCOME;
    const skip = SKIP.test(text);
    const option = skip ? null : matchOption(q, text);
    // A typed number is OUR option number; option values aren't always 1..n (floor_level is 0/1/2), so never send it raw.
    if (!skip && !option && /^\d+[).]?$/.test(text)) return `Sorry, I didn't catch that.\n${questionText(q)}`;
    // Unclear text goes to the API, whose parser knows more words ("central air", "first floor").
    const answer = skip ? "skip" : option ? optionValue(option) : text;
    const r = await this.api.answer({ session_id: s.sessionId, question_id: q.id, answer });
    if (!r.ok) {
      if (r.code === "bad_answer") return r.message; // keep the question open; the API's text lists the options
      if (r.code === "not_served") {
        s.pending = null;
        if (skip) {
          s.answered.add(q.id); // no /answer yet: skip locally so the interview can go on
          return this.withNextQuestion(s, "Skipped.");
        }
        return "Thanks! Answers can't refine the estimate yet; that part is still being built.";
      }
      s.pending = null;
      return r.message;
    }
    s.answered.add(q.id);
    const previous = s.last ?? undefined;
    s.last = r.data;
    s.pending = null;
    const update = updateText(r.data, previous);
    return this.withNextQuestion(s, skip ? `Skipped.${update ? `\n${update}` : ""}` : update);
  }

  /** A typed bill (when the photo reader is down, the API asks for one): POST /calibrate with therms + dates. */
  private async typedBill(s: ChatState, typed: NonNullable<ReturnType<typeof parseTypedBill>>): Promise<string[]> {
    if ("error" in typed) return [typed.error];
    if (!s.sessionId) return [NEED_LISTING_FOR_BILL];
    if (s.userId && !s.propertyId) return ['This report is not saved to your current home. Say "save", then send the bill again.'];
    const c = await this.api.calibrate({ session_id: s.sessionId, ...(s.propertyId ? { property_id: s.propertyId } : {}), ...typed });
    if (!c.ok) return [c.code === "not_served" ? "Thanks! Bill checks aren't live yet; that part is still being built." : c.message];
    return this.afterBill(s, c.data);
  }

  private async afterBill(s: ChatState, c: Calibration): Promise<string[]> {
    const current = s.me?.current_grade?.grade ?? s.last?.grade;
    if (c.estimate) s.last = c.estimate;
    s.pending = null;
    const clear = s.userId ? await this.api.patchMe(s.userId, { pending_checkin: null }) : null;
    if (clear?.ok) s.me = clear.data;
    const text = s.userId ? billResultText(c, current) : calibrationText(c);
    return [text, ...(clear && !clear.ok ? [clear.message] : []), ...(await this.fixes(s))];
  }

  private async save(s: ChatState): Promise<string> {
    if (!s.userId || !s.sessionId) return "Send a listing or address first, then say save.";
    if (s.savedSession === s.sessionId) return 'Your home is saved. Say "options" for commitments.';
    const r = await this.api.property({ user_id: s.userId, session_id: s.sessionId });
    if (!r.ok) return r.message;
    s.propertyId = r.data.property_id; s.propertySession = s.sessionId; s.savedSession = s.sessionId;
    const me = await this.api.me(s.userId); if (me.ok) s.me = me.data;
    return 'Your home and answers are saved. Say "options" for commitments.';
  }

  private async phase2(s: ChatState, text: string): Promise<string | null> {
    const uid = s.userId!;
    const control = text.match(/^(stop|pause|resume|start)$/i)?.[1].toLowerCase();
    if (control) {
      const action = control === "start" ? "resume" : control as "stop" | "pause" | "resume";
      const r = await this.api.reminderControl(uid, action);
      return r.ok ? action === "resume" ? "Reminders resumed with your saved preferences. You can say pause or stop any time." : `Proactive reminders ${action === "stop" ? "stopped" : "paused"}. I'll still answer when you text me.` : r.message;
    }
    const task = s.replyingTo?.kind === "task" ? s.replyingTo : undefined;
    if ((task && HABIT_REPLY.test(text)) || HABIT_TODAY.test(text)) {
      // A reply to a task reminder counts for the reminder's own day (a late reply after midnight is yesterday's).
      const day = task && !/today/i.test(text) ? { date: task.local_date } : {};
      const r = await this.api.habitCheckin(uid, { source: "imessage", ...day, ...(task?.commitment_id ? { commitment_id: task.commitment_id } : {}) });
      s.replyingTo = undefined;
      return r.ok ? `Day ${r.data.current} 🔥, best ${r.data.best}. See you tomorrow.` : r.message;
    }
    if (/^(done|did it|✅️?)$/iu.test(text)) return 'Say "done today" to log today\'s habit, or "done 1" to mark commitment 1 complete.';
    if (/^(my )?streak\??$/i.test(text)) {
      const r = await this.api.habits(uid); if (!r.ok) return r.message;
      const next = r.data.checked_in_today ? "Today already counts." : 'Reply "done today" once you\'ve kept your daily habit.';
      return `🔥 Habit streak: ${r.data.current} day${r.data.current === 1 ? "" : "s"}, best ${r.data.best}. ${next}`;
    }
    const ff = text.match(/^(?:fast[- ]?forward|ff)\s+(\d+)(?:\s*days?)?$/i);
    if (ff) {
      const days = Number(ff[1]);
      if (days < 1 || days > 365) return 'Fast-forward 1 to 365 days, like "ff 30".';
      if (!s.propertyId) return 'Save your home and accept a commitment first, then say "fast forward 30".';
      const r = await this.api.fastForward({ property_id: s.propertyId, days }); // a simulation: stores nothing
      return r.ok ? fastForwardText(r.data) : r.message;
    }
    if (/^(moved|i moved|no[, ]+i moved)$/i.test(text)) { s.pending = { kind: "move" }; return "What's your new address or listing link? Your old home's history stays separate."; }
    if (/^save$/i.test(text)) return this.save(s);
    if (/^(checkin|check-in)$/i.test(text)) {
      const r = await this.api.checkin(uid); if (!r.ok) return r.message;
      s.pending = { kind: "checkin" }; return `Still at ${r.data.address}? Reply yes or moved.`;
    }
    if (/^(yes|yep|yeah)$/i.test(text) && s.pending?.kind === "checkin") {
      s.pending = { kind: "bill" };
      return 'Send this month’s bill photo, or type "120 therms", "120 ccf", or "$85" (estimated from your bill amount). Without dates I use the last full month; you can add start/end dates.';
    }
    const remind = text.match(/^remind[- ]now(?:\s+(task|checkin|weather))?$/i);
    if (remind) { const r = await this.api.reminderDemo(uid, remind[1]?.toLowerCase() as ReplyingTo["kind"] | undefined); return r.ok ? `${r.data.demo ? "[demo reminder]\n" : ""}${r.data.text_hint}` : r.message; }
    const pref = text.match(/^reminders? (daily|weekly|monthly)(?: at (\d{1,2}))?$/i);
    if (pref) {
      const r = await this.api.patchMe(uid, { reminder_prefs: { channel: "imessage", cadence: pref[1].toLowerCase(), ...(pref[2] ? { hour_local: Number(pref[2]) } : {}) } });
      return r.ok ? `Reminder preference saved: ${r.data.reminder_prefs.cadence} at ${r.data.reminder_prefs.hour_local}:00 ${r.data.timezone}. At most one per day; two unanswered messages pause them. Say resume if previously stopped.` : r.message;
    }
    if (/^(options|commitments|what can i do|show my options)\??$/i.test(text)) {
      if (!s.propertyId) { const saved = await this.save(s); if (!s.propertyId) return saved; }
      const r = await this.api.suggestions(s.propertyId!); if (!r.ok) return r.message;
      s.suggestions = r.data.commitments;
      return suggestionsText(s.suggestions);
    }
    const choose = text.match(/^do\s+(.+)$/i);
    if (choose) {
      if (!s.propertyId || !s.suggestions?.length) return 'Say "options" first so the numbers match your current home.';
      const date = choose[1].match(/\bby\s+(\d{4}-\d{2}-\d{2})$/i)?.[1];
      const choices = choose[1].replace(/\bby\s+\d{4}-\d{2}-\d{2}$/i, "").trim();
      if (!/^\d+(?:\s*(?:,|and)\s*\d+)*$/i.test(choices)) return 'Use option numbers, like "do 1 and 3 by 2026-11-01".';
      const ids = [...new Set(choices.match(/\d+/g)!.map(Number))];
      if (ids.some((n) => n < 1 || n > s.suggestions!.length)) return 'That option number is not on the list. Say "options" to see it again.';
      const saved: Commitment[] = []; const failures: string[] = [];
      for (const n of ids) {
        const r = await this.api.commit({ user_id: uid, property_id: s.propertyId, catalog_id: s.suggestions[n - 1].catalog_id, ...(date ? { target_date: date } : {}) });
        if (r.ok) saved.push(r.data); else failures.push(r.message);
      }
      if (!saved.length) return failures.join("\n");
      const existing = await this.api.commitments(s.propertyId); if (existing.ok) s.accepted = existing.data.commitments;
      const lines = [saved.map((c) => `Accepted: ${c.title}${c.target_date ? ` (target ${c.target_date})` : ""}.`).join("\n"), ...failures];
      if (s.me?.current_grade?.source === "bill_regrade") lines.push("Your current grade comes from a bill. A projection from that updated baseline isn't available yet; the commitments are saved.");
      else {
        const modeled = saved.filter((c) => !s.suggestions!.find((x) => x.catalog_id === c.catalog_id)?.pending_model);
        if (!modeled.length) lines.push("Saved as tips; no modeled savings or projected grade is available for these.");
        else { const p = await this.api.projection({ property_id: s.propertyId, commitment_ids: modeled.map((c) => c.id) }); lines.push(p.ok ? projectionText(p.data) : `Commitments saved. ${p.message}`); }
      }
      for (const c of saved) { const note = s.suggestions.find((x) => x.catalog_id === c.catalog_id)?.note; if (note) lines.push(note); }
      lines.push('When finished, say "done 1" using the option number. Optional: "reminders weekly" or "add to calendar" (Calendar needs a target date).');
      return lines.join("\n");
    }
    const done = text.match(/^(done|dismiss)\s+(\d+)$/i);
    if (done) {
      if (!s.propertyId) return "Save a home first.";
      const list = await this.api.commitments(s.propertyId); if (!list.ok) return list.message;
      if (!s.suggestions?.length) return 'Say "options" first so I can match that number to the right commitment.';
      const chosen = s.suggestions[Number(done[2]) - 1];
      const c = chosen && list.data.commitments.find((x) => x.catalog_id === chosen.catalog_id && x.status === "accepted");
      if (!c) return "I couldn't find that accepted commitment. Say options, then use its number.";
      const r = await this.api.updateCommitment(c.id, done[1].toLowerCase() === "done" ? "completed" : "dismissed");
      return r.ok ? r.data.status === "completed" ? `Reported complete: ${r.data.title}. Your current grade is unchanged; bills can verify a reduction later.` : `Dismissed: ${r.data.title}.` : r.message;
    }
    if (/^(add to calendar|calendar|calendar connected)$/i.test(text)) {
      if (!s.propertyId) return "Save your home and accept a commitment with a target date first.";
      const me = await this.api.me(uid); if (!me.ok) return me.message;
      if (!me.data.calendar_connected) { const r = await this.api.calendarConnect(uid); return r.ok ? `${r.data.mock ? "[mock Calendar — no Google event]\n" : ""}Connect Calendar: ${r.data.auth_url}\nAfter connecting, reply "calendar connected". Your commitments are already saved.` : `${r.message} Your commitments are still saved.`; }
      const list = await this.api.commitments(s.propertyId); if (!list.ok) return list.message;
      const eligible = list.data.commitments.filter((c) => c.status === "accepted" && c.target_date && !c.calendar_event_id && !this.calendarCreated.has(c.id));
      if (!eligible.length) return 'No accepted commitments with a target date need a Calendar event. Use "do 1 by YYYY-MM-DD".';
      const messages: string[] = [];
      for (const c of eligible) { const r = await this.api.calendarReminder({ user_id: uid, commitment_id: c.id, start: c.target_date!, cadence: "once" }); if (r.ok) this.calendarCreated.add(c.id); messages.push(r.ok ? `${r.data.mock ? "Mock Calendar reminder" : "Calendar reminder"}: ${c.title}${r.data.html_link ? ` ${r.data.html_link}` : ""}` : `${r.message} Your commitment is still saved.`); }
      return messages.join("\n");
    }
    return null;
  }

  /** Append the API's next unanswered question, unless the grade is locked or the API sent none. */
  private withNextQuestion(s: ChatState, body: string): string {
    const e = s.last;
    const usable = (x: Question) => x && typeof x.id === "string" && typeof x.text === "string" && Array.isArray(x.options);
    const questions = Array.isArray(e?.questions) ? e.questions : [];
    const q = e && !e.locked && s.sessionId ? questions.find((x) => usable(x) && !s.answered.has(x.id)) : undefined;
    if (q) {
      s.pending = { kind: "question", question: q };
      return `${body}\n\n${questionText(q)}`;
    }
    if (e?.locked) return `${body}\n\nGrade locked in. Send another listing to compare, or after move-in text me a photo of your bill.`;
    return body;
  }

  private failure(s: ChatState, r: Extract<ApiResult, { ok: false }>): string {
    if (r.code === "needs_address") {
      s.pending = { kind: "address" };
      return r.hint ? `${r.message} (Is it ${r.hint}?)` : r.message;
    }
    return r.message;
  }
}
