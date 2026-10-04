import assert from "node:assert/strict";
import { test } from "node:test";
import { httpApi, type Estimate } from "../src/api.ts";
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
  assert.match(await chat.reply("c", "maybe"), /didn't catch that/);
  assert.match(await chat.reply("c", "2"), /can't refine the estimate yet/);
  assert.deepEqual(seen[1], ["/answer", { session_id: "s1", question_id: "windows", answer: "double-pane" }]);
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
  assert.match(afterUnit, /single-pane or double-pane/);
  assert.doesNotMatch(afterUnit, /\(was/); // same size → same range → no "was"
  const update = await chat.reply("judge", "double");
  assert.match(update, /Heating \+ cooling a year: \$980–\$1,740.*\(was \$760–\$1,960\)/);
  assert.doesNotMatch(update, /Winter|🏠/); // answers get a short update, not the whole card
  assert.match(await chat.reply("judge", "top"), /\$1,120–\$1,600/);
  const last = await chat.reply("judge", "yes");
  assert.match(last, /Grade B 🔒/);
  assert.match(last, /double pane club/);
  assert.match(last, /Grade locked in/);
});

test("chats are independent", async () => {
  const chat = new Conversations(mockApi());
  await chat.reply("a", "912 Mary St, Ann Arbor, MI");
  assert.match(await chat.reply("b", "850"), /Hidden Rent/); // b has no pending question → welcome
});
