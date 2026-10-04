import assert from "node:assert/strict";
import { test } from "node:test";
import { httpApi } from "../src/api.ts";
import { Conversations, DEMO_LABEL } from "../src/conversation.ts";
import { mockApi } from "../src/mockApi.ts";
import { billImageBase64 } from "../src/photo.ts";
import { NEED_LISTING_FOR_BILL, inbound, type Inbound } from "../src/replies.ts";

const photo = (bytes = Buffer.from("fake-jpeg"), mimeType = "image/jpeg"): Inbound => ({ kind: "photo", mimeType, read: async () => bytes });
const band = (p50: number) => ({ p10: null, p50, p90: null });
const EST = { session_id: "s1", building: { address: "912 MARY ST" }, bill: { annual: band(1200) }, questions: [] };
const CAL = { pct_vs_expected_for_weather: 18, streak_months: 0, badges: [], estimate: EST };
const FIXES = {
  fixes: [{ item: "Air sealing", grh_points: 18, co2_kg_saved: 300, usd_saved_yr: 310, cost_usd: 700, rebate_usd: 350, new_grade: "B" }],
  grh_points_now: 45,
  grh_points_after: 72,
  landlord_email: "Subject: Air sealing\n\nHi, ...",
};

/** Fake /api that routes by path and records [method, path, body]. */
function fakeApi(routes: Record<string, [number, unknown]>, seen: [string, string, any][] = []) {
  const fetchFn = (async (url: string, init: RequestInit) => {
    const path = new URL(url).pathname;
    seen.push([init.method!, path, init.body ? JSON.parse(init.body as string) : undefined]);
    const key = Object.keys(routes).find((k) => path.startsWith(k));
    const [status, body] = key ? routes[key] : [404, { detail: "Not Found" }];
    return new Response(JSON.stringify(body), { status });
  }) as typeof fetch;
  return new Conversations(httpApi("http://api", fetchFn, () => {}));
}

test("a bill photo before any listing asks for the listing first (no API call)", async () => {
  const seen: [string, string, any][] = [];
  assert.deepEqual(await fakeApi({}, seen).respond("c", photo()), [NEED_LISTING_FOR_BILL]);
  assert.equal(seen.length, 0);
});

test("bill photo → POST /calibrate (base64) → GET /fixes → three messages, numbers only from the API", async () => {
  const seen: [string, string, any][] = [];
  const chat = fakeApi({ "/estimate": [200, EST], "/calibrate": [200, CAL], "/fixes/": [200, FIXES] }, seen);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  const msgs = await chat.respond("c", photo());
  assert.deepEqual(seen[1], ["POST", "/calibrate", { session_id: "s1", bill_image_base64: Buffer.from("fake-jpeg").toString("base64") }]);
  assert.deepEqual(seen[2].slice(0, 2), ["GET", "/fixes/s1"]);
  assert.equal(msgs.length, 3);
  assert.equal(msgs[0], "📄 Your bill is 18% above normal for this weather.");
  assert.match(msgs[1], /1\) Air sealing: saves \$310\/yr, costs \$700 \(\$350 rebate\) → grade B, \+18 GRH pts/);
  assert.match(msgs[1], /Green Rental Housing points: 45 → 72 \(Ann Arbor requires 70\)/);
  assert.equal(msgs[2], FIXES.landlord_email);
});

test("'fixes' text gets the fixes + email without a new photo", async () => {
  const chat = fakeApi({ "/estimate": [200, EST], "/fixes/": [200, FIXES] });
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.match(await chat.reply("c", "fixes"), /Top fixes:[\s\S]*Subject: Air sealing/);
});

test("/calibrate not served yet → honest text; contract break → logged, no numbers", async () => {
  const chat = fakeApi({ "/estimate": [200, EST] });
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.deepEqual(await chat.respond("c", photo()), ["Thanks! Bill checks aren't live yet; that part is still being built."]);

  const logs: string[] = [];
  const fetchFn = (async (url: string) =>
    new Response(JSON.stringify(new URL(url).pathname === "/estimate" ? EST : { streak_months: 2 }))) as unknown as typeof fetch;
  const broken = new Conversations(httpApi("http://api", fetchFn, (m) => logs.push(m)));
  await broken.reply("c", "912 Mary St, Ann Arbor, MI");
  const [msg] = await broken.respond("c", photo());
  assert.doesNotMatch(msg, /\d+%/);
  assert.match(logs.join("\n"), /\[contract\] POST \/calibrate: pct_vs_expected_for_weather missing/);
});

test("mock after-move-in (USE_MOCK_API): below normal, streak grows, demo label on the first message only", async () => {
  const chat = new Conversations(mockApi());
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  const first = await chat.respond("c", photo());
  assert.equal(first[0], `${DEMO_LABEL}\n📄 Your bill is 12% below normal for this weather 🎉\n🔥 1-month streak below normal\n🏅 weather beater`);
  assert.match(first[1], /^🔧 Top fixes:/);
  assert.match(first[2], /^Subject: Energy fixes/);
  assert.match((await chat.respond("c", photo()))[0], /2-month streak/);
});

test("inbound(): images become photos, other attachments and reactions are ignored", async () => {
  const p = inbound({ type: "attachment", mimeType: "image/heic", name: "IMG_1.HEIC", read: async () => new Uint8Array([1, 2]) });
  assert.equal(p?.kind, "photo");
  assert.deepEqual(await (p as any).read(), Buffer.from([1, 2]));
  assert.equal(inbound({ type: "attachment", mimeType: "application/pdf", read: async () => new Uint8Array() }), null);
  assert.equal(inbound({ type: "reaction" }), null);
  assert.deepEqual(inbound({ type: "text", text: "hi" }), { kind: "text", text: "hi" });
});

test("billImageBase64: JPEG passes through; a broken HEIC falls back to the original bytes instead of failing", async () => {
  assert.equal(await billImageBase64(Buffer.from("jpg"), "image/jpeg"), Buffer.from("jpg").toString("base64"));
  const warn = console.warn;
  console.warn = () => {};
  try {
    assert.equal(await billImageBase64(Buffer.from("not-really-heic"), "image/heic"), Buffer.from("not-really-heic").toString("base64"));
  } finally {
    console.warn = warn;
  }
});

test("mid-interview: 'fixes' runs the fixes command, 'skip' moves to the next question without calling /answer", async () => {
  const chat = new Conversations(mockApi());
  await chat.reply("c", "Hi (ref web9)");
  assert.match(await chat.reply("c", "skip"), /Skipped\.\n\nIs the unit on the top, middle or ground floor\?/);
  const fixes = await chat.reply("c", "fixes");
  assert.match(fixes, /Top fixes:/);
  assert.match(fixes, /Back to your question:\nIs the unit on the top, middle or ground floor\?/);
  assert.match(await chat.reply("c", "top"), /Grade B–C/); // the open question still works after the detour
});
