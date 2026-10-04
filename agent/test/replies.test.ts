import assert from "node:assert/strict";
import { test } from "node:test";
import { CONTRACT_ERROR, httpApi, type Estimate } from "../src/api.ts";
import { Conversations, DEMO_LABEL } from "../src/conversation.ts";
import { mockApi } from "../src/mockApi.ts";
import { UNIT_SIZE_QUESTION, WELCOME, estimateText, matchOption } from "../src/replies.ts";

const band = (p50: number) => ({ p10: null, p50, p90: null });
// Shape of the real /estimate today (integration notes): p50 only, no session or questions yet.
const RESSTOCK_BASIS = "ResStock applied to held-out real Ann Arbor buildings ≥10k ft²; small buildings have no local meter data, so expect at least this error";
const estimate = (over: Partial<Estimate> = {}, building: Partial<Estimate["building"]> = {}): Estimate => ({
  session_id: null,
  building: {
    address: "912 MARY ST, ANN ARBOR, MI, 48104",
    type: "Multi-Family with 2 - 4 Units",
    sqft: 1100.4,
    sqft_estimated: false,
    year_built: 1939,
    year_built_source: "given by caller (listing)",
    ...building,
  },
  bill: { annual: band(1234.4), seasonal: { winter: band(800), spring: band(200), summer: band(134), fall: band(100) } },
  heating_cooling: { building: { heating_fuel: "gas" }, accuracy: { seasonal_gas_median_abs_error: { all: 0.299 }, basis: RESSTOCK_BASIS } },
  ...over,
});

/** Fake /api: answers each call with the next body; records [path, body]. */
function fakeApi(responses: [number, unknown][], seen: [string, any][] = []) {
  const fetchFn = (async (url: string, init: RequestInit) => {
    seen.push([new URL(url).pathname, JSON.parse(init.body as string)]);
    const [status, body] = responses.shift() ?? [500, {}];
    return new Response(JSON.stringify(body), { status });
  }) as typeof fetch;
  return new Conversations(httpApi("http://api", fetchFn));
}

test("an address goes to POST /estimate and the reply only repeats API numbers", async () => {
  const seen: [string, any][] = [];
  const text = await fakeApi([[200, estimate()]], seen).reply("c", "912 Mary St, Ann Arbor, MI");
  assert.deepEqual(seen, [["/estimate", { address: "912 Mary St, Ann Arbor, MI" }]]);
  assert.match(text, /912 MARY ST/);
  assert.match(text, /1,100 sq ft, built 1939/);
  assert.match(text, /Heating \+ cooling a year: \$1,234/);
  assert.match(text, /Winter \$800 · Spring \$200 · Summer \$134 · Fall \$100/);
  assert.doesNotMatch(text, /coming soon|Grade/);
});

test("wording: ResStock-path error says 'at least', gas error is dropped for electric heat, census year is a neighborhood median", () => {
  assert.match(estimateText(estimate()), /gas meters: at least 30%/);
  const metered = estimate({ heating_cooling: { building: { heating_fuel: "gas" }, accuracy: { seasonal_gas_median_abs_error: { all: 0.12 }, basis: "this building's own meters, predicting a held-out year" } } });
  assert.match(estimateText(metered), /gas meters: 12%/);
  const electric = estimate({ heating_cooling: { building: { heating_fuel: "electric" }, accuracy: { seasonal_gas_median_abs_error: { all: 0.3 }, basis: RESSTOCK_BASIS } } });
  assert.doesNotMatch(estimateText(electric), /error/);
  const median = estimate({}, { year_built: 1965, year_built_source: "ACS 2023 5-year B25035 median year structure built, block group 15000US261614001001" });
  assert.match(estimateText(median), /built around 1965 \(neighborhood median\)/);
});

test("an estimated unit size is asked first; the answer re-runs /estimate with unit_sqft and quotes both API numbers", async () => {
  const seen: [string, any][] = [];
  const first = estimate({}, { sqft_estimated: true });
  const second = estimate({ bill: { annual: band(820) } }, { sqft: 700, sqft_estimated: false });
  const chat = fakeApi([[200, first], [200, second]], seen);
  const a = await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.ok(a.endsWith(UNIT_SIZE_QUESTION));
  const b = await chat.reply("c", "about 700 sq ft");
  assert.deepEqual(seen[1], ["/estimate", { address: "912 Mary St, Ann Arbor, MI", unit_sqft: 700 }]);
  assert.match(b, /700 sq ft, built 1939/);
  assert.match(b, /\$820 \(was \$1,234\)/);
  assert.equal(await chat.reply("c", "thanks"), WELCOME);
});

test("'skip' keeps the estimated size and makes no API call", async () => {
  const seen: [string, any][] = [];
  const chat = fakeApi([[200, estimate({}, { sqft_estimated: true })]], seen);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.match(await chat.reply("c", "skip"), /keeping the estimated size/);
  assert.equal(seen.length, 1);
});

test("needs_address: the API's hint is passed on and the next text is used as the address", async () => {
  const seen: [string, any][] = [];
  const needs = { detail: { code: "needs_address", message: "What's the address?", hint: "715 Arbor St, Ann Arbor, MI" } };
  const chat = fakeApi([[422, needs], [200, estimate()]], seen);
  assert.equal(await chat.reply("c", "https://www.zumper.com/apartment-buildings/p1/715-arbor-st"), "What's the address? (Is it 715 Arbor St, Ann Arbor, MI?)");
  assert.deepEqual(seen[0], ["/estimate", { url: "https://www.zumper.com/apartment-buildings/p1/715-arbor-st" }]);
  await chat.reply("c", "715 Arbor");
  assert.deepEqual(seen[1], ["/estimate", { address: "715 Arbor" }]);
});

test("other API errors (not_a_home, 503) are passed on as the API words them", async () => {
  const notHome = { detail: { code: "not_a_home", message: "That doesn't look like a home. Send a residential address or listing." } };
  assert.equal(await fakeApi([[422, notHome]]).reply("c", "301 E Huron St, Ann Arbor"), notHome.detail.message);
});

test("with a session and questions: answer goes to POST /answer; a 404 (not served yet) is said honestly", async () => {
  const seen: [string, any][] = [];
  const q = { id: "windows", text: "Single or double pane?", options: ["single-pane", "double-pane"] };
  const chat = fakeApi([[200, estimate({ session_id: "s1", questions: [q] })], [404, { detail: "Not Found" }]], seen);
  const a = await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.match(a, /Single or double pane\?\n1\) single-pane {2}2\) double-pane/);
  assert.match(await chat.reply("c", "7"), /didn't catch that/); // out-of-range number: re-asked locally, no API call
  assert.equal(seen.length, 1);
  assert.match(await chat.reply("c", "2"), /can't refine the estimate yet/);
  assert.deepEqual(seen[1], ["/answer", { session_id: "s1", question_id: "windows", answer: "double-pane" }]);
});

// P2's real shapes (api/app/estimate.py): {value,label} options with values that aren't 1..n, 422 bad_answer.
const FLOOR = { id: "floor_level", text: "Is the unit on the ground floor, a middle floor or the top floor?",
  options: [{ value: "0", label: "Ground floor" }, { value: "1", label: "Middle floor" }, { value: "2", label: "Top floor" }] };

test("real API: our option number maps to the option's VALUE (2 → middle = '1'), never sent raw", async () => {
  const seen: [string, any][] = [];
  const chat = fakeApi([[200, estimate({ session_id: "s1", questions: [FLOOR] })], [200, estimate({ session_id: "s1", questions: [] })]], seen);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  await chat.reply("c", "2");
  assert.deepEqual(seen[1], ["/answer", { session_id: "s1", question_id: "floor_level", answer: "1" }]);
});

test("real API: unclear text goes to /answer; a 422 bad_answer keeps the question open", async () => {
  const seen: [string, any][] = [];
  const bad = { detail: { code: "bad_answer", message: "Sorry, I didn't catch that. Is the unit on the ground floor, a middle floor or the top floor? Reply Ground floor, Middle floor or Top floor, or say skip." } };
  const chat = fakeApi([
    [200, estimate({ session_id: "s1", questions: [FLOOR] })],
    [422, bad],
    [200, estimate({ session_id: "s1", questions: [], grade: "B", grade_span: ["B"], locked: true })],
  ], seen);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  assert.equal(await chat.reply("c", "the attic"), bad.detail.message);
  assert.deepEqual(seen[1], ["/answer", { session_id: "s1", question_id: "floor_level", answer: "the attic" }]);
  const locked = await chat.reply("c", "Top");      // still the same question → answered
  assert.deepEqual(seen[2], ["/answer", { session_id: "s1", question_id: "floor_level", answer: "2" }]);
  assert.match(locked, /Grade B 🔒/);
});

test("real API: 'skip' is sent as 'skip' so the API can lock the grade", async () => {
  const seen: [string, any][] = [];
  const chat = fakeApi([[200, estimate({ session_id: "s1", questions: [FLOOR] })], [200, estimate({ session_id: "s1", questions: [], locked: true, grade: "C", grade_span: ["C"] })]], seen);
  await chat.reply("c", "912 Mary St, Ann Arbor, MI");
  const r = await chat.reply("c", "not sure");
  assert.deepEqual(seen[1], ["/answer", { session_id: "s1", question_id: "floor_level", answer: "skip" }]);
  assert.match(r, /^Skipped\.\nGrade C 🔒/);
});

test("matchOption: numbers, exact, unique partial; ambiguous or junk is null", () => {
  const q = { id: "floor", text: "Floor?", options: ["top", "middle", "ground"] };
  assert.equal(matchOption(q, "3"), "ground");
  assert.equal(matchOption(q, "Top"), "top");
  assert.equal(matchOption(q, "middle floor"), "middle");
  assert.equal(matchOption(q, "7"), null);
  assert.equal(matchOption(q, "x"), null);
});

test("mock interview (USE_MOCK_API): link → grade span + question → answers narrow the range → grade locks", async () => {
  const chat = new Conversations(mockApi());
  const first = await chat.reply("judge", "https://www.zillow.com/homedetails/1-Main-St-Ann-Arbor-MI-48104/1_zpid/");
  assert.ok(first.startsWith(DEMO_LABEL));
  assert.match(first, /Grade B–D: answer a few questions/);
  assert.ok(first.endsWith(UNIT_SIZE_QUESTION));
  const afterUnit = await chat.reply("judge", "850");
  assert.match(afterUnit, /Is the heat gas or electric, or included in your rent\?/);
  assert.doesNotMatch(afterUnit, /\(was/); // same size → same range → no "was"
  const update = await chat.reply("judge", "gas");
  assert.match(update, /Heating \+ cooling a year: \$980–\$1,740.*\(was \$760–\$1,960\)/);
  assert.match(update, /single-, double- or triple-pane/);
  assert.doesNotMatch(update, /Winter|🏠/); // answers get a short update, not the whole card
  assert.match(await chat.reply("judge", "double"), /\$1,120–\$1,600/);
  assert.match(await chat.reply("judge", "attic"), /didn't catch that[\s\S]*Ground floor, Middle floor or Top floor/); // bad_answer keeps the question
  const last = await chat.reply("judge", "3"); // our option 3 = Top floor (value "2")
  assert.match(last, /Grade B 🔒/);
  assert.match(last, /double pane club/);
  assert.match(last, /Grade locked in/);
});

test("chats are independent", async () => {
  const chat = new Conversations(mockApi());
  await chat.reply("a", "912 Mary St, Ann Arbor, MI");
  assert.match(await chat.reply("b", "850"), /Hidden Rent/); // b has no pending question → welcome
});

test("contract mismatch: a 200 without bill.annual.p50 is logged and answered honestly, without numbers", async () => {
  const logs: string[] = [];
  const fetchFn = (async () => new Response(JSON.stringify({ session_id: null, building: {}, bill: {} }))) as unknown as typeof fetch;
  const chat = new Conversations(httpApi("http://api", fetchFn, (m) => logs.push(m)));
  assert.equal(await chat.reply("c", "912 Mary St, Ann Arbor, MI"), CONTRACT_ERROR);
  assert.match(logs.join("\n"), /\[contract\] POST \/estimate: bill\.annual\.p50 missing/);
});

test("contract warnings (bad question shape) are logged but the reply still goes out", async () => {
  const logs: string[] = [];
  const body = estimate({ session_id: "s1", questions: [{ id: "q", text: "?" } as any] });
  const fetchFn = (async () => new Response(JSON.stringify(body))) as unknown as typeof fetch;
  const text = await new Conversations(httpApi("http://api", fetchFn, (m) => logs.push(m))).reply("c", "912 Mary St, Ann Arbor, MI");
  assert.match(text, /\$1,234/);
  assert.match(logs[0], /questions\[0\] needs \{id, text, options\[\]\}/);
});

test("website handoff: '(ref <id>)' in the first text loads GET /session/{id} and continues with its questions", async () => {
  const seen: [string, any][] = [];
  const fetchFn = (async (url: string, init: RequestInit) => {
    seen.push([init.method!, new URL(url).pathname]);
    const q = { id: "windows", text: "Single or double pane?", options: ["single-pane", "double-pane"] };
    return new Response(JSON.stringify(estimate({ session_id: "web123", questions: [q] })));
  }) as typeof fetch;
  const text = await new Conversations(httpApi("http://api", fetchFn)).reply("c", "Hi Hidden Rent! What's my apartment's hidden rent? (ref web123)");
  assert.deepEqual(seen, [["GET", "/session/web123"]]);
  assert.match(text, /^Picking up your report from the website\./);
  assert.match(text, /\$1,234/);
  assert.match(text, /Single or double pane\?/);
});

test("website handoff: unknown or unserved session → friendly restart, no numbers", async () => {
  const fetchFn = (async () => new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 })) as unknown as typeof fetch;
  const text = await new Conversations(httpApi("http://api", fetchFn)).reply("c", "Hi! (ref nope99)");
  assert.match(text, /couldn't find your report/);
  assert.doesNotMatch(text, /\$\d/);
});

test("two phones at once: interleaved, concurrent messages never mix sessions, questions or addresses", async () => {
  const chat = new Conversations(mockApi());
  const [a1, b1] = await Promise.all([chat.reply("phoneA", "912 Mary St, Ann Arbor, MI"), chat.reply("phoneB", "715 Arbor St, Ann Arbor, MI")]);
  assert.match(a1, /912 Mary St/);
  assert.match(b1, /715 Arbor St/);
  const [a2, b2] = await Promise.all([chat.reply("phoneA", "850"), chat.reply("phoneB", "skip")]);
  assert.match(a2, /850 sq ft, built/); // A re-estimated with its size
  assert.match(b2, /keeping the estimated size/); // B skipped; A's answer didn't land here
  const [a3, b3] = await Promise.all([chat.reply("phoneA", "electric"), chat.reply("phoneB", "gas")]);
  assert.match(a3, /single-, double- or triple-pane/);
  assert.match(b3, /single-, double- or triple-pane/);
  const fixesA = await chat.reply("phoneA", "fixes");
  assert.match(fixesA, /912 Mary St/); // A's landlord email names A's address
  assert.doesNotMatch(fixesA, /715 Arbor/);
});
