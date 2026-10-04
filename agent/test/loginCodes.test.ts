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
  const { api, acked } = fakeApi([{ login_id: "a", handle: "+17345550100", text: "Your Hidden Rent code is 123456." }]);
  const sent: [string, string][] = [];
  const sender = new LoginCodeSender(api, async (h, t) => { sent.push([h, t]); }, () => {});
  await sender.poll();
  await sender.poll();
  assert.deepEqual(sent, [["+17345550100", "Your Hidden Rent code is 123456."]]);
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
