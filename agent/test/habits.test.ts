// Daily habit streak intents (conversation.ts → POST /habits/{user_id}/checkin, GET /habits/{user_id}).
import assert from "node:assert/strict";
import { test } from "node:test";
import { CONTRACT_ERROR, httpApi, type ApiResult } from "../src/api.ts";
import { Conversations } from "../src/conversation.ts";
import { mockApi } from "../src/mockApi.ts";

const sender = { handle: "+12025550164" };
const must = <T>(r: ApiResult<T>): T => { assert.equal(r.ok, true); return (r as { ok: true; data: T }).data; };

/** A saved home with commitment 1 accepted; every habit check-in request is recorded. */
async function pledged() {
  const api = mockApi(); const chat = new Conversations(api);
  const reply = async (text: string) => (await chat.reply("test", text, sender)).replace(/^\[demo data, not a real estimate\]\n/, "");
  for (const text of ["1514 Morton Ave, Ann Arbor, MI", "850", "gas", "single", "top", "options", "do 1"]) await reply(text);
  const checkins: unknown[] = []; const real = api.habitCheckin;
  api.habitCheckin = async (id, req) => { checkins.push(req); return real(id, req); };
  const account = must(await api.authPhone({ phone: sender.handle }));
  return { api, reply, checkins, userId: account.user_id, propertyId: account.current_property_id! };
}

test("bare done answering a task reminder → Day 1 from the API; streak; done 1 still completes commitment 1", async () => {
  const { api, reply, checkins, propertyId } = await pledged();
  assert.match(await reply("remind-now task"), /\[demo reminder\]\n.*start a habit streak/);
  assert.equal(await reply("done"), "Day 1 🔥, best 1. See you tomorrow.");
  const [req] = checkins as { date: string; commitment_id: string; source: string }[];
  assert.equal(req.source, "imessage"); assert.match(req.date, /^\d{4}-\d{2}-\d{2}$/); assert.ok(req.commitment_id);
  assert.equal(await reply("streak"), "🔥 Habit streak: 1 day, best 1. Today already counts.");
  assert.match(await reply("done 1"), /Reported complete: window upgrade/);
  assert.equal(must(await api.commitments(propertyId)).commitments[0].status, "completed");
  assert.equal(checkins.length, 1); // "done 1" never checks in a habit
});

for (const text of ["did it", "did it today", "✅", "yes", "Done!"]) {
  test(`"${text}" answering a task reminder checks in`, async () => {
    const { reply, checkins } = await pledged(); await reply("remind-now task");
    assert.equal(await reply(text), "Day 1 🔥, best 1. See you tomorrow.");
    assert.equal(checkins.length, 1);
    assert.equal("date" in (checkins[0] as object), !/today/.test(text)); // "today" means today, not the reminder's day
  });
}

test("without a task reminder: done today checks in any time; bare done/yes never do", async () => {
  const { reply, checkins } = await pledged();
  assert.match(await reply("done"), /Say "done today".*"done 1"/);
  await reply("remind-now"); // a check-in reminder ("Still at …?"), not a task
  assert.doesNotMatch(await reply("yes"), /Day \d/);
  assert.equal(checkins.length, 0);
  assert.equal(await reply("done today"), "Day 1 🔥, best 1. See you tomorrow.");
  assert.equal(await reply("done today"), "Day 1 🔥, best 1. See you tomorrow."); // idempotent per day
  await reply("remind-now task"); await reply("hello?"); // the reminder was answered by another text
  assert.match(await reply("done"), /Say "done today"/);
});

test("no accepted habit: the API's no_habits message, word for word", async () => {
  const api = mockApi(); const chat = new Conversations(api);
  for (const text of ["1514 Morton Ave, Ann Arbor, MI", "850", "gas", "single", "top"]) await chat.reply("t", text, sender);
  assert.match(await chat.reply("t", "done today", sender), /Pick a daily habit first: text 'options'$/);
});

test("habit numbers only from a well-formed API body; API errors pass through", async () => {
  const bodies = [{ current: 2, best: 5, checked_in_today: true, last_checkin_date: "2026-10-04" }, { current: "2", best: 5 },
    { detail: { code: "no_habits", message: "Pick a daily habit first: text 'options'" } }];
  const fetcher = (async () => { const body = bodies.shift()!; return new Response(JSON.stringify(body), { status: "detail" in body ? 422 : 200 }); }) as typeof fetch;
  const api = httpApi("http://api", fetcher, () => {});
  assert.equal(must(await api.habitCheckin("u", { source: "imessage" })).current, 2);
  assert.deepEqual(await api.habits("u"), { ok: false, code: "contract_mismatch", message: CONTRACT_ERROR });
  assert.deepEqual(await api.habitCheckin("u", { source: "imessage" }), { ok: false, code: "no_habits", message: "Pick a daily habit first: text 'options'", hint: undefined });
});
