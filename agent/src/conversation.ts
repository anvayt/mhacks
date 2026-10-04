// The iMessage interview (PLAN.md §4 steps 3–5): link/address → estimate → questions one at a time → answers →
// narrower range, until the API says the grade is locked. One state per chat (Spectrum space), in memory.
import type { Api, ApiResult, Estimate, EstimateRequest, Question } from "./api.ts";
import {
  ADDRESS,
  LINK,
  UNIT_SIZE_QUESTION,
  WELCOME,
  estimateText,
  matchOption,
  optionValue,
  questionText,
  updateText,
} from "./replies.ts";

type Pending = { kind: "address" } | { kind: "unit_sqft" } | { kind: "question"; question: Question };

interface ChatState {
  request: EstimateRequest | null;
  sessionId: string | null;
  last: Estimate | null;
  answered: Set<string>;
  pending: Pending | null;
}

const fresh = (): ChatState => ({ request: null, sessionId: null, last: null, answered: new Set(), pending: null });

export const DEMO_LABEL = "[demo data, not a real estimate]";

export class Conversations {
  private chats = new Map<string, ChatState>();

  constructor(private api: Api) {}

  /** The reply to one inbound text in chat `chatId`. */
  async reply(chatId: string, text: string): Promise<string> {
    const out = await this.handle(this.state(chatId), text.trim());
    return this.api.mock ? `${DEMO_LABEL}\n${out}` : out;
  }

  private state(chatId: string): ChatState {
    let s = this.chats.get(chatId);
    if (!s) this.chats.set(chatId, (s = fresh()));
    return s;
  }

  private async handle(s: ChatState, text: string): Promise<string> {
    const link = text.match(LINK)?.[0];
    if (link) return this.estimate(s, { url: link });
    if (ADDRESS.test(text)) return this.estimate(s, { address: text });

    const p = s.pending;
    if (p?.kind === "address") return this.estimate(s, { address: text });
    if (p?.kind === "unit_sqft") return this.unitSize(s, text);
    if (p?.kind === "question") return this.answer(s, p.question, text);
    return WELCOME;
  }

  /** New listing or address: start over in this chat. */
  private async estimate(s: ChatState, request: EstimateRequest, previous?: Estimate): Promise<string> {
    const r = await this.api.estimate(request);
    if (!r.ok) return this.failure(s, r);
    Object.assign(s, { request, sessionId: r.data.session_id, last: r.data, answered: new Set(), pending: null });
    const body = estimateText(r.data, previous);
    // Team decision (P2-04): an estimated unit size is the first question; /estimate takes unit_sqft.
    if (r.data.building.sqft_estimated && request.unit_sqft == null) {
      s.pending = { kind: "unit_sqft" };
      return `${body}\n\n${UNIT_SIZE_QUESTION}`;
    }
    return this.withNextQuestion(s, body);
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
    const option = matchOption(q, text);
    if (!option) return `Sorry, I didn't catch that.\n${questionText(q)}`;
    if (!s.sessionId) return WELCOME;
    const r = await this.api.answer({ session_id: s.sessionId, question_id: q.id, answer: optionValue(option) });
    if (!r.ok) {
      s.pending = null;
      return r.code === "not_served"
        ? "Thanks! Answers can't refine the estimate yet; that part is still being built."
        : r.message;
    }
    s.answered.add(q.id);
    const previous = s.last ?? undefined;
    s.last = r.data;
    s.pending = null;
    return this.withNextQuestion(s, updateText(r.data, previous));
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
    if (e?.locked) return `${body}\n\nGrade locked in. Send another listing to compare.`;
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
