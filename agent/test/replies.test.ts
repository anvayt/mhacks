import assert from "node:assert/strict";
import { test } from "node:test";
import { replyFor } from "../src/replies.ts";

const band = (p50: number) => ({ p10: null, p50, p90: null });
const ESTIMATE = {
  building: { address: "912 MARY ST, ANN ARBOR, MI, 48104", type: "Multi-Family with 2 - 4 Units", sqft: 1100.4, sqft_estimated: true, year_built: 1939 },
  bill: { annual: band(1234.4), seasonal: { winter: band(800), spring: band(200), summer: band(134), fall: band(100) } },
  heating_cooling: { accuracy: { seasonal_gas_median_abs_error: { all: 0.299 } } },
};
const fakeFetch = (status: number, body: unknown, seen: unknown[] = []) =>
  (async (url: string, init: RequestInit) => {
    seen.push([url, JSON.parse(init.body as string)]);
    return new Response(JSON.stringify(body), { status });
  }) as typeof fetch;

test("an address is sent to POST /estimate and the reply only repeats API numbers", async () => {
  const seen: unknown[] = [];
  const text = await replyFor("912 Mary St, Ann Arbor, MI", fakeFetch(200, ESTIMATE, seen));
  const [[url, body]] = seen as [string, unknown][];
  assert.match(url, /\/estimate$/);
  assert.deepEqual(body, { address: "912 Mary St, Ann Arbor, MI" });
  assert.match(text, /912 MARY ST/);
  assert.match(text, /1,100 sq ft \(estimated\), built 1939/);
  assert.match(text, /\$1,234/);
  assert.match(text, /Winter \$800 · Spring \$200 · Summer \$134 · Fall \$100/);
  assert.match(text, /30%/);
});

test("a link is sent as url; the API's 422 message is passed on", async () => {
  const seen: unknown[] = [];
  const body = { detail: { code: "needs_address", message: "What's the address?", hint: "715 Arbor St, Ann Arbor, MI" } };
  const text = await replyFor("https://www.zumper.com/apartment-buildings/p1/715-arbor-st", fakeFetch(422, body, seen));
  assert.equal((seen[0] as any)[1].url, "https://www.zumper.com/apartment-buildings/p1/715-arbor-st");
  assert.equal(text, "What's the address? (Is it 715 Arbor St, Ann Arbor, MI?)");
});
