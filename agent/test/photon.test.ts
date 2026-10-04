import assert from "node:assert/strict";
import { test } from "node:test";
import { OPENER, PhotonError, createSharedUser, normalizePhone, redirectUrl } from "../src/photon.ts";
import { NOT_LIVE, WELCOME, replyFor } from "../src/replies.ts";

test("normalizePhone handles common US inputs and E.164", () => {
  assert.equal(normalizePhone("(734) 555-0123"), "+17345550123");
  assert.equal(normalizePhone("734.555.0123"), "+17345550123");
  assert.equal(normalizePhone("1 734 555 0123"), "+17345550123");
  assert.equal(normalizePhone("+44 20 7946 0958"), "+442079460958");
  assert.equal(normalizePhone("555-0123"), null);
  assert.equal(normalizePhone("+0123456789"), null);
  assert.equal(normalizePhone(""), null);
});

test("createSharedUser sends Basic auth and a shared-user body", async () => {
  let seen: { url: string; init: RequestInit } | undefined;
  const fakeFetch = (async (url: string, init: RequestInit) => {
    seen = { url, init };
    return new Response(JSON.stringify({ succeed: true, data: { id: "u1", phoneNumber: "+17345550123" } }));
  }) as typeof fetch;
  const user = await createSharedUser({ projectId: "p", projectSecret: "s" }, "+17345550123", "Ada", fakeFetch);
  assert.deepEqual(user, { id: "u1", phoneNumber: "+17345550123" });
  assert.equal(seen!.url, "https://spectrum.photon.codes/projects/p/users/");
  assert.equal((seen!.init.headers as Record<string, string>).Authorization, `Basic ${Buffer.from("p:s").toString("base64")}`);
  assert.deepEqual(JSON.parse(seen!.init.body as string), { type: "shared", phoneNumber: "+17345550123", firstName: "Ada" });
});

test("createSharedUser throws PhotonError on a failed response", async () => {
  const fakeFetch = (async () => new Response(JSON.stringify({ succeed: false }), { status: 403 })) as typeof fetch;
  await assert.rejects(createSharedUser({ projectId: "p", projectSecret: "s" }, "+17345550123", undefined, fakeFetch), PhotonError);
});

test("redirectUrl pre-fills the text-only opener", () => {
  const url = new URL(redirectUrl("abc"));
  assert.equal(url.pathname, "/users/abc/redirect");
  assert.equal(url.searchParams.get("msg"), OPENER);
  assert.doesNotMatch(OPENER, /https?:/);
});

test("replyFor: listings and addresses get NOT_LIVE, anything else the welcome, and no numbers are invented", () => {
  assert.equal(replyFor("https://www.zillow.com/homedetails/123-Main-St-Ann-Arbor-MI-48104/1_zpid/"), NOT_LIVE);
  assert.equal(replyFor("1100 S University Ave, Ann Arbor"), NOT_LIVE);
  assert.equal(replyFor("hi"), WELCOME);
  assert.doesNotMatch(WELCOME + NOT_LIVE, /\$\d/);
});
