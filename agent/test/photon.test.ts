import assert from "node:assert/strict";
import { test } from "node:test";
import {
  OPENER,
  PhotonError,
  createSharedUser,
  listSharedUsers,
  normalizePhone,
  redirectUrl,
  removeSharedUserByPhone,
} from "../src/photon.ts";
import { UNREACHABLE, httpApi } from "../src/api.ts";
import { Conversations } from "../src/conversation.ts";
import { WELCOME, inboundText } from "../src/replies.ts";

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
    return new Response(
      JSON.stringify({ succeed: true, data: { id: "u1", phoneNumber: "+17345550123", assignedPhoneNumber: "+15550001111", firstName: "Ada", meta: null } }),
    );
  }) as typeof fetch;
  const user = await createSharedUser({ projectId: "p", projectSecret: "s" }, "+17345550123", "Ada", fakeFetch);
  assert.deepEqual(user, { id: "u1", phoneNumber: "+17345550123", assignedPhoneNumber: "+15550001111", firstName: "Ada" });
  assert.equal(seen!.url, "https://spectrum.photon.codes/projects/p/users/");
  assert.equal((seen!.init.headers as Record<string, string>).Authorization, `Basic ${Buffer.from("p:s").toString("base64")}`);
  assert.deepEqual(JSON.parse(seen!.init.body as string), { type: "shared", phoneNumber: "+17345550123", firstName: "Ada" });
});

test("createSharedUser throws PhotonError with Photon's message (real 401 shape)", async () => {
  // Body captured from spectrum.photon.codes with fake credentials.
  const body = { succeed: false, data: null, code: "401", message: "Invalid credentials" };
  const fakeFetch = (async () => new Response(JSON.stringify(body), { status: 401 })) as typeof fetch;
  await assert.rejects(
    createSharedUser({ projectId: "p", projectSecret: "s" }, "+17345550123", undefined, fakeFetch),
    (err: unknown) => err instanceof PhotonError && err.status === 401 && /Invalid credentials/.test(err.message),
  );
});

test("listSharedUsers asks for shared users and returns them", async () => {
  let url = "";
  const fakeFetch = (async (u: string) => {
    url = u;
    const users = [{ id: "u1", phoneNumber: "+17345550123", assignedPhoneNumber: "+15550001111", firstName: null }];
    return new Response(JSON.stringify({ succeed: true, data: { users, total: 1 } }));
  }) as typeof fetch;
  const { users, total } = await listSharedUsers({ projectId: "p", projectSecret: "s" }, fakeFetch);
  assert.equal(url, "https://spectrum.photon.codes/projects/p/users/?type=shared&limit=500");
  assert.equal(total, 1);
  assert.equal(users[0].assignedPhoneNumber, "+15550001111");
});

test("redirectUrl pre-fills the text-only opener", () => {
  const url = new URL(redirectUrl("abc"));
  assert.equal(url.pathname, "/users/abc/redirect");
  assert.equal(url.searchParams.get("msg"), OPENER);
  assert.doesNotMatch(OPENER, /https?:/);
});

// API unreachable: links and addresses get UNREACHABLE (replies.test.ts covers the API answering).
const down = (async () => {
  throw new TypeError("fetch failed");
}) as typeof fetch;
const reply = (text: string) => new Conversations(httpApi("http://api", down)).reply("chat", text);

test("while the API is down, listings and addresses get UNREACHABLE, anything else the welcome, and no numbers are invented", async () => {
  assert.equal(await reply("https://www.zillow.com/homedetails/123-Main-St-Ann-Arbor-MI-48104/1_zpid/"), UNREACHABLE);
  assert.equal(await reply("1100 S University Ave, Ann Arbor"), UNREACHABLE);
  assert.equal(await reply("hi"), WELCOME);
  assert.doesNotMatch(WELCOME + UNREACHABLE, /\$\d/);
});

test("inboundText answers text and pasted links, ignores reactions and typing", async () => {
  assert.equal(inboundText({ type: "text", text: "hi" }), "hi");
  const url = "https://www.redfin.com/MI/Ann-Arbor/1-Main-St-48104/home/1";
  assert.equal(inboundText({ type: "richlink", url }), url);
  assert.equal(await reply(inboundText({ type: "richlink", url })!), UNREACHABLE);
  assert.equal(inboundText({ type: "reaction" }), null);
  assert.equal(inboundText({ type: "typing" }), null);
});

// Fake Photon: GET lists two users, DELETE records which ids were removed.
function fakePhoton(deleted: string[]) {
  const users = [
    { id: "u1", phoneNumber: "+17345550123", assignedPhoneNumber: "+15550001111", firstName: "Ada" },
    { id: "u2", phoneNumber: "+17345559999", assignedPhoneNumber: "+15550001111", firstName: null },
  ];
  return (async (url: string, init: RequestInit) => {
    if (init.method === "DELETE") {
      const id = url.match(/\/users\/([^/]+)\/$/)![1];
      deleted.push(id);
      return new Response(JSON.stringify({ succeed: true, data: { userId: id } }));
    }
    return new Response(JSON.stringify({ succeed: true, data: { users, total: users.length } }));
  }) as typeof fetch;
}

test("removeSharedUserByPhone deletes only the matching user", async () => {
  const deleted: string[] = [];
  const removed = await removeSharedUserByPhone({ projectId: "p", projectSecret: "s" }, "+17345550123", fakePhoton(deleted));
  assert.deepEqual(deleted, ["u1"]);
  assert.equal(removed[0].phoneNumber, "+17345550123");
});

test("removeSharedUserByPhone returns [] and deletes nothing for an unknown phone", async () => {
  const deleted: string[] = [];
  const removed = await removeSharedUserByPhone({ projectId: "p", projectSecret: "s" }, "+12025550100", fakePhoton(deleted));
  assert.deepEqual(removed, []);
  assert.deepEqual(deleted, []);
});
