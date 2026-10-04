import assert from "node:assert/strict";
import { test } from "node:test";
import type { Api, LoginText } from "../src/api.ts";
import { LoginCodeSender } from "../src/loginCodes.ts";

function fakeApi(queue: LoginText[]) {
  const acked: string[] = [];
  const api = {
    loginOutbox: async () => ({ ok: true as const, data: queue.filter((q) => !acked.includes(q.login_id)) }),
    loginSent: async (login_id: string) => { acked.push(login_id); return { ok: true as const, data: { login_id, sent: true } }; },
  } as unknown as Api;
  return { api, acked };
}

test("texts each queued sign-in code once, then acks it", async () => {
  const { api, acked } = fakeApi([{ login_id: "a", handle: "+17345550100", text: "Hidden Rent here 👋 This is your Hidden Rent number, save it. Your sign-in code is 123456." }]);
  const sent: [string, string][] = [];
  const sender = new LoginCodeSender(api, async (h, t) => { sent.push([h, t]); }, () => {});
  await sender.poll();
  await sender.poll();
  assert.deepEqual(sent, [["+17345550100", "Hidden Rent here 👋 This is your Hidden Rent number, save it. Your sign-in code is 123456."]]);
  assert.deepEqual(acked, ["a"]);
});

test("a failed send isn't acked, so the next poll retries it", async () => {
  const { api, acked } = fakeApi([{ login_id: "b", handle: "+17345550101", text: "code" }]);
  let fail = true;
  const logs: string[] = [];
  const sender = new LoginCodeSender(api, async () => { if (fail) throw new Error("down"); }, (m) => logs.push(m));
  await sender.poll();
  assert.deepEqual(acked, []);
  fail = false;
  await sender.poll();
  assert.deepEqual(acked, ["b"]);
  assert.ok(logs.some((m) => m.includes("retry")));
});

test("a sent but unacked code retries only the ack; a failing handle stops after 3 tries", async () => {
  const queue: LoginText[] = [{ login_id: "c", handle: "+17345550102", text: "code" }, { login_id: "d", handle: "+17345550103", text: "code" }];
  let ackOk = false;
  const acked: string[] = [];
  const api = {
    loginOutbox: async () => ({ ok: true as const, data: queue.filter((q) => !acked.includes(q.login_id)) }),
    loginSent: async (login_id: string) => ackOk ? (acked.push(login_id), { ok: true as const, data: { login_id, sent: true } }) : { ok: false as const, code: "unreachable", message: "down" },
  } as unknown as Api;
  const sends: string[] = [];
  const sender = new LoginCodeSender(api, async (h) => { sends.push(h); if (h.endsWith("03")) throw new Error("not allowed"); }, () => {});
  for (let i = 0; i < 5; i++) await sender.poll();
  assert.equal(sends.filter((h) => h.endsWith("02")).length, 1); // texted once despite 4 failed acks
  assert.equal(sends.filter((h) => h.endsWith("03")).length, 3); // capped
  ackOk = true;
  await sender.poll();
  assert.deepEqual(acked, ["c"]);
  assert.equal(sends.length, 4);
});

test("an API that's down never crashes the poller", async () => {
  const api = { loginOutbox: async () => { throw new Error("boom"); } } as unknown as Api;
  const logs: string[] = [];
  const sender = new LoginCodeSender(api, async () => { throw new Error("must not send"); }, (m) => logs.push(m));
  const stop = sender.start(5);
  await new Promise((r) => setTimeout(r, 30));
  stop();
  assert.ok(logs.some((m) => m.includes("poll failed")));
});
