import assert from "node:assert/strict";
import { once } from "node:events";
import type { AddressInfo } from "node:net";
import { test } from "node:test";
import type { ContentBuilder } from "spectrum-ts";
import type { Api } from "../src/api.ts";
import { INTRO, Intros, shareCard } from "../src/intro.ts";

const fakeApi = (address?: string): Pick<Api, "session"> => ({
  session: async (id) => (id === "gone1" ? { ok: false, code: "not_found", message: "no" } : ({ ok: true, data: { session_id: id, building: { address } } } as never)),
});

test("texts the intro, then the card, once per phone per 10 minutes, with no links", async () => {
  const sent: string[] = [];
  let now = 0;
  const intros = new Intros(async (h, t) => { sent.push(`${h} ${t}`); }, fakeApi(), async (h, line) => { sent.push(`${h} card ${line}`); }, () => now);
  assert.equal(await intros.intro("+17345550100", null, "+15550001111"), "sent");
  assert.equal(await intros.intro("+17345550100", null, "+15550001111"), "throttled");
  now = 9 * 60_000;
  assert.equal(await intros.intro("+17345550100", null), "throttled");
  now = 10 * 60_000;
  assert.equal(await intros.intro("+17345550100", null, "+15550001111"), "sent");
  const pair = [`+17345550100 ${INTRO}`, "+17345550100 card +15550001111"];
  assert.deepEqual(sent, [...pair, ...pair]);
  assert.doesNotMatch(INTRO, /https?:|www\./);
});

test("a failed text still counts toward the throttle; a failed card never fails the intro", async () => {
  let tries = 0;
  const down = new Intros(async () => { tries++; throw new Error("spectrum down"); }, fakeApi(), undefined, () => 0);
  await assert.rejects(down.intro("+17345550101", null));
  assert.equal(await down.intro("+17345550101", null), "throttled");
  assert.equal(tries, 1);
  const noCard = new Intros(async () => {}, fakeApi(), async () => { throw new Error("no card"); }, () => 0);
  assert.equal(await noCard.intro("+17345550101", null, "+15550001111"), "sent");
});

test("Continue in iMessage: the intro names the report and the next reply resumes it once", async () => {
  const sent: string[] = [];
  const intros = new Intros(async (_h, t) => { sent.push(t); }, fakeApi("123 Main St, Ann Arbor"), undefined, () => 0);
  await intros.intro("+17345550102", "web123");
  assert.match(sent[0], /your report for 123 Main St, Ann Arbor/);
  assert.match(sent[0], /Reply anything to pick up where you left off\.$/);
  assert.equal(intros.take("(734) 555-0102"), "web123"); // Spectrum handle format differs; same account handle
  assert.equal(intros.take("+17345550102"), null);
  await intros.intro("+17345550103", "gone1"); // session lookup failed: still texts, without an address
  assert.match(sent[1], /I have your report from the website/);
});

test("contact card carries the user's own line; falls back to the line's native iMessage card", async () => {
  const built: Record<string, unknown>[] = [];
  const space = (failContact = false) => ({
    send: async (c: ContentBuilder) => {
      const content = (await c.build()) as unknown as Record<string, unknown>;
      if (failContact && content.type === "contact") throw new Error("contact rejected");
      built.push(content);
    },
  });
  assert.equal(await shareCard(space(), "+15550001111"), "contact");
  const card = built[0] as { name: { formatted: string }; phones: { value: string }[]; photo: { mimeType: string }; urls?: unknown };
  assert.equal(card.name.formatted, "Hidden Rent");
  assert.deepEqual(card.phones.map((p) => p.value), ["+15550001111"]);
  assert.equal(card.photo.mimeType, "image/png");
  assert.equal(card.urls, undefined); // no links on first contact
  assert.equal(await shareCard(space(true), "+15550001111"), "native");
  assert.equal(await shareCard(space(), null), "native");
  assert.deepEqual(built.slice(1).map((c) => c.type), ["contactCard", "contactCard"]);
});

test("POST /intro listens on 127.0.0.1 only and rejects bad input without crashing", async () => {
  const sent: string[] = [];
  const cards: unknown[] = [];
  const intros = new Intros(async (h) => { sent.push(h); }, fakeApi(), async (_h, line) => { cards.push(line); }, () => 0);
  const server = intros.serve(0);
  await once(server, "listening");
  const { address, port } = server.address() as AddressInfo;
  assert.equal(address, "127.0.0.1");
  try {
    const post = (body: string) => fetch(`http://127.0.0.1:${port}/intro`, { method: "POST", body });
    assert.equal((await post("not json")).status, 400);
    assert.equal((await post(JSON.stringify({ phone: "12" }))).status, 400);
    const ok = await post(JSON.stringify({ phone: "(734) 555-0104", session: "bad id!", line: "+1 555 000 1111" }));
    assert.deepEqual(await ok.json(), { status: "sent" });
    assert.deepEqual(sent, ["+17345550104"]);
    assert.deepEqual(cards, ["+15550001111"]);
  } finally {
    server.close();
  }
});
