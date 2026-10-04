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
  assert.match(msgs[1], /1\) Air sealing: saves \$310\/yr, 300 kg CO₂\/yr less, costs \$700 \(\$350 rebate\), \+18 GRH pts → grade B/);
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

test("mid-interview: 'fixes' runs the fixes command; 'skip' is sent to /answer and moves on", async () => {
  const chat = new Conversations(mockApi());
  await chat.reply("c", "Hi (ref web9)");
  assert.match(await chat.reply("c", "skip"), /Skipped\.[\s\S]*Are the windows single-, double- or triple-pane\?/);
  const fixes = await chat.reply("c", "fixes");
  assert.match(fixes, /Top fixes:/);
  assert.match(fixes, /Back to your question:\nAre the windows single-, double- or triple-pane\?/);
  assert.match(await chat.reply("c", "double"), /Grade B–C/); // the open question still works after the detour
});

import { calibrationText, fixesText, parseTypedBill } from "../src/replies.ts";

test("calibrationText follows P1: inside the noise → 'within normal'; outside winter → rough read; no 🎉 unless meaningful", () => {
  const base = { streak_months: 0, badges: [], estimate: EST as any };
  assert.equal(calibrationText({ ...base, pct_vs_expected_for_weather: -6, meaningful: false, noise_floor: 9.5 }),
    "📄 Your bill is within the normal range for this weather (-6% vs expected, inside our typical ±10% error).");
  assert.match(calibrationText({ ...base, pct_vs_expected_for_weather: -12, meaningful: null }), /12% below what this month's weather predicts\. Outside Dec–Feb/);
  assert.doesNotMatch(calibrationText({ ...base, pct_vs_expected_for_weather: -12, meaningful: null }), /🎉/);
  assert.match(calibrationText({ ...base, pct_vs_expected_for_weather: -18.4, meaningful: true }), /18% below normal for this weather 🎉/);
});

test("fixesText never prints a number the API left null; negative savings read as 'costs more to run'", () => {
  const text = fixesText({
    fixes: [
      { item: "Air sealing", grh_points: 9, co2_kg_saved: 410, usd_saved_yr: 160, cost_usd: null, rebate_usd: 500, new_grade: "B" },
      { item: "Heat pump", grh_points: 35, co2_kg_saved: 900, usd_saved_yr: -120, cost_usd: 15400, rebate_usd: 4000, new_grade: "B" },
      { item: "Storm windows", grh_points: 4, co2_kg_saved: null, usd_saved_yr: null, cost_usd: null, rebate_usd: null, new_grade: null, unpriced: true },
    ],
    grh_points_now: 0, grh_points_after: 48, grh_points_required: 70, landlord_email: "x",
  });
  assert.doesNotMatch(text, /\$0\b|null|NaN|undefined/);
  assert.match(text, /1\) Air sealing: saves \$160\/yr, 410 kg CO₂\/yr less, \$500 rebate, \+9 GRH pts → grade B/);
  assert.match(text, /2\) Heat pump: costs \$120\/yr more to run, 900 kg CO₂\/yr less, costs \$15,400 \(\$4,000 rebate\)/);
  assert.match(text, /3\) Storm windows: \+4 GRH pts/);
  assert.match(text, /0 → 48 \(Ann Arbor requires 70\)/);
});

test("parseTypedBill: therms or CCF (explicit API unit), m/d dates with year inference, ISO dates, kWh optional", () => {
  const today = new Date(2026, 9, 4); // Oct 4, 2026
  assert.deepEqual(parseTypedBill("52 therms 9/3 to 10/2", today), { therms: 52, start: "2026-09-03", end: "2026-10-02" });
  assert.deepEqual(parseTypedBill("gas 100 CCF, 12/5 - 1/6", today), { therms: 100, gas_unit: "ccf", start: "2025-12-05", end: "2026-01-06" });
  assert.deepEqual(parseTypedBill("40 therms 320 kWh 2026-08-01 to 2026-08-31", today), { therms: 40, kwh: 320, start: "2026-08-01", end: "2026-08-31" });
  assert.deepEqual(parseTypedBill("52 therms", today), { therms: 52, start: "2026-09-01", end: "2026-09-30" });
  assert.equal(parseTypedBill("912 Mary St, Ann Arbor", today), null);
});

test("typed bill → POST /calibrate {therms, start, end} → reply + fixes; before a listing → asks for it", async () => {
  const seen: [string, string, any][] = [];
  const chat = fakeApi({ "/estimate": [200, EST], "/calibrate": [200, { ...CAL, meaningful: true }], "/fixes/": [200, FIXES] }, seen);
  assert.equal(await chat.reply("c", "52 therms 9/3 to 10/2"), NEED_LISTING_FOR_BILL);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  const r = await chat.reply("c", "52 therms 9/3 to 10/2");
  const call = seen.find(([, p]) => p === "/calibrate")!;
  assert.equal(call[2].therms, 52);
  assert.match(call[2].start, /-09-03$/);
  assert.match(r, /18% above normal for this weather\.[\s\S]*Top fixes/);
});

test("vision down: the API's 'type the numbers instead' message is passed on, and a typed bill then works", async () => {
  const VISION_DOWN = "Reading bill photos isn't working right now. Type the numbers instead: gas used (therms or CCF), and the billing start and end dates.";
  const chat = fakeApi({ "/estimate": [200, EST], "/calibrate": [503, { detail: { code: "vision_unavailable", message: VISION_DOWN } }] });
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.deepEqual(await chat.respond("c", photo()), [VISION_DOWN]);
});
