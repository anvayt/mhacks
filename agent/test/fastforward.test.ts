// "fast forward <days>" / "ff <days>" → POST /simulate/fast-forward, worded as a simulation (never usage).
import assert from "node:assert/strict";
import { test } from "node:test";
import { CONTRACT_ERROR, httpApi, type ApiResult } from "../src/api.ts";
import { Conversations } from "../src/conversation.ts";
import { mockApi } from "../src/mockApi.ts";

const sender = { handle: "+12025550164" };
const must = <T>(r: ApiResult<T>): T => { assert.equal(r.ok, true); return (r as { ok: true; data: T }).data; };

async function saved(accept?: string) {
  const api = mockApi(); const chat = new Conversations(api);
  const reply = async (text: string) => (await chat.reply("ff", text, sender)).replace(/^\[demo data, not a real estimate\]\n/, "");
  for (const text of ["1514 Morton Ave, Ann Arbor, MI", "850", "gas", "single", "top", "options"]) await reply(text);
  if (accept) await reply(accept);
  return { api, reply, userId: must(await api.authPhone({ phone: sender.handle })).user_id };
}

test("ff 30 → one simulated reply with API numbers; the real streak is quoted and never changes", async () => {
  const { api, reply, userId } = await saved("do 1 and 2");
  await reply("done today");
  assert.equal(await reply("ff 30"), "Simulation, not real usage: if you keep your commitment to window upgrade, in 30 days you'd save about $10 and 57 kg CO₂ (projected). Your real streak stays 1.");
  assert.match(await reply("fast forward 365 days"), /in 365 days you'd save about \$125 and 699 kg CO₂ \(projected\)/);
  assert.match(await reply("Fast-forward 1"), /in 1 day you'd save about \$0\.34 and 1\.9 kg/);
  assert.equal(must(await api.habits(userId)).current, 1); // nothing simulated is stored
});

test("only tips accepted → pick a modeled commitment; bad day counts and no home get a usage hint", async () => {
  const { reply } = await saved("do 2");
  assert.match(await reply("ff 30"), /^Nothing to fast-forward yet: none of your commitments has modeled savings/);
  for (const text of ["ff 0", "ff 366"]) assert.equal(await reply(text), 'Fast-forward 1 to 365 days, like "ff 30".');
  const fresh = new Conversations(mockApi());
  assert.match(await fresh.reply("x", "ff 30", { handle: "+12025550111" }), /Save your home and accept a commitment first/);
});

test("fast-forward numbers only from a body labelled as a simulation", async () => {
  const good = { label: "simulated_projected_if_kept", label_text: "Simulated", totals: { days: 7, end_date: "2026-10-11", usd_saved: 1.5, kg_co2_saved: 4 }, commitments: [], not_modeled: [], real_habit_streak: 0, simulated_habit_streak: 7 };
  const bodies: unknown[] = [good, { ...good, label: "projected_if_completed" }, { ...good, totals: { days: 7 } }];
  const api = httpApi("http://api", (async () => new Response(JSON.stringify(bodies.shift()))) as typeof fetch, () => {});
  assert.equal(must(await api.fastForward({ property_id: "p", days: 7 })).totals.usd_saved, 1.5);
  for (let i = 0; i < 2; i++) assert.deepEqual(await api.fastForward({ property_id: "p", days: 7 }), { ok: false, code: "contract_mismatch", message: CONTRACT_ERROR });
});
