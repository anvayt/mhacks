// Web integration smoke test (P3-INT review). Run via scripts/web-smoke.sh; see the header there.
// Mode "api": the exact API calls the web should make, per demo address. Mode "web": drives the real pages in Chrome
// (Playwright) and checks every number shown against the API's own answer. Mode "all": both.
import { readFileSync } from "node:fs";

const MODE = process.argv[2] ?? "all";
const API = process.env.API ?? "http://localhost:8033";
const WEB = process.env.WEB ?? "http://localhost:3004";
const ROOT = new URL("..", import.meta.url).pathname;
const ADDRS = readFileSync(`${ROOT}demo/addresses.txt`, "utf8").split("\n").map((s) => s.trim()).filter(Boolean);
const COMPARE = ["624 Church St, Ann Arbor, MI", "1022 S Forest Ave, Ann Arbor, MI"];
const ZUMPER = "https://www.zumper.com/apartments-for-rent/ann-arbor-mi";
const NOT_HOME = "500 S State St, Ann Arbor, MI";
const MAP_ADDRS = ["912 Mary St, Ann Arbor, MI", "615 S Main St, Ann Arbor, MI"];
// Survey answers to pick when the API offers them (label text, exactly as the API sends it).
const PICK = { heating_fuel: "Gas", window_panes: "Single-pane", floor_level: "Middle floor", cooling_code: "Central AC" };
const HEAT_INCLUDED_ADDR = "1022 S Forest Ave"; // decision 4: this address answers "Heat is included in my rent"

const results = []; // {scope, check, status: PASS|FAIL|WARN, detail}
const rec = (scope, check, status, detail = "") => {
  results.push({ scope, check, status, detail });
  console.log(`${status.padEnd(4)} ${scope} :: ${check}${detail ? ` (${detail})` : ""}`);
};
const ok = (scope, check, cond, detail, soft = false) => rec(scope, check, cond ? "PASS" : soft ? "WARN" : "FAIL", detail);

// Mirror api/app/public_guard.py. Node oracle calls and every browser context
// share localhost's visitor budget. Pace between flows, never bypass the guard
// or retry a 429; one real browser walkthrough must fit the normal limit.
const REQUEST_LIMIT = 30;
const WINDOW_MS = 60_000;
const WINDOW_MARGIN_MS = 250;
const protectedRequests = [];
function protectedRequest(method, url) {
  const path = new URL(url, API).pathname.replace(/\/$/, "");
  return method === "POST" && ["/estimate", "/answer", "/compare", "/calibrate", "/projection", "/properties", "/auth/web/start"].includes(path)
    || method === "GET" && ["/map", "/forecast", "/fixes", "/debug/features", "/commitments/suggested", "/leaderboard/position"].some(p => path === p || path.startsWith(`${p}/`));
}
function pruneRequests() {
  const cutoff = Date.now() - WINDOW_MS - WINDOW_MARGIN_MS;
  while (protectedRequests.length && protectedRequests[0] <= cutoff) protectedRequests.shift();
}
function recordRequest() {
  pruneRequests();
  protectedRequests.push(Date.now());
}
async function paceWait(ms, label) {
  console.log(`PACE ${label}: waiting ${(ms / 1000).toFixed(1)}s for the public request budget`);
  const until = Date.now() + ms;
  while (Date.now() < until) await new Promise(resolve => setTimeout(resolve, Math.min(30_000, until - Date.now())));
}
async function reserveRequests(count, label) {
  pruneRequests();
  while (protectedRequests.length + count > REQUEST_LIMIT) {
    // Wait for exactly enough older requests to expire, with a small transport
    // margin. The browser is never given a key or a slower request interceptor.
    const oldestNeeded = protectedRequests[protectedRequests.length + count - REQUEST_LIMIT - 1];
    await paceWait(Math.max(1, oldestNeeded + WINDOW_MS + WINDOW_MARGIN_MS - Date.now()), label);
    pruneRequests();
  }
}

async function api(path, body) {
  const method = body === undefined ? "GET" : "POST";
  if (protectedRequest(method, path)) {
    await reserveRequests(1, `oracle ${method} ${path.split("?")[0]}`);
    recordRequest();
  }
  const res = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (res.status === 429) rec("rate limit", `${method} ${path.split("?")[0]}`, "FAIL", "429; the harness does not retry or bypass it");
  return { status: res.status, data: await res.json().catch(() => null) };
}
const money = (n) => `$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;
const num = (n) => `(${Math.round(n)}|${Math.round(n).toLocaleString("en-US")})`; // 1014 or 1,014
const span = (s) => (s.length === 1 ? s[0] : `${s[0]}\\s*(–|-|—|to)\\s*${s[s.length - 1]}`);
// locked may mean no remaining answer can narrow a multi-grade range.
const displayedGrades = (estimate) => estimate.grade_span?.length > 1 ? estimate.grade_span : [estimate.grade];
const short = (a) => a.split(",")[0];

// ---------- API mode: what the web should call ----------
async function apiFlow(addr) {
  const sc = `api ${short(addr)}`;
  let r = await api("/estimate", { address: addr });
  ok(sc, "POST /estimate 200", r.status === 200, r.data?.detail?.code);
  if (r.status !== 200) return;
  const sid = r.data.session_id;
  for (const q of r.data.questions) {
    const want = addr.startsWith(HEAT_INCLUDED_ADDR) && q.id === "heating_fuel" ? "Heat is included in my rent" : PICK[q.id];
    const opt = q.options.find((o) => o.label === want) ?? q.options[0];
    r = await api("/answer", { session_id: sid, question_id: q.id, answer: opt.value });
    ok(sc, `POST /answer ${q.id}=${opt.value}`, r.status === 200, r.data?.detail?.code);
  }
  const s = (await api(`/session/${sid}`)).data;
  ok(sc, "GET /session", !!s?.grade, `grade ${s?.grade} span ${s?.grade_span?.join("-")} locked ${s?.locked} hidden ${s?.hidden_rent_usd_mo}/mo`);
  if (s?.answers?.heating_fuel === "included") ok(sc, "heat included -> bill.note", !!s.bill?.note, s.bill?.note);
  const sug = await api(`/commitments/suggested?session_id=${sid}`);
  const modeled = (sug.data?.commitments ?? []).filter((c) => !c.pending_model);
  ok(sc, "GET /commitments/suggested?session_id", sug.status === 200, `${modeled.length} modeled: ${modeled.map((c) => c.catalog_id).join(",") || "none"}`);
  const pos = await api(`/leaderboard/position?session_id=${sid}`);
  ok(sc, "GET /leaderboard/position?session_id", pos.status === 200 && pos.data.projected === null, `rank ${pos.data?.current?.rank}/${pos.data?.current?.of}`);
  if (modeled.length) {
    const id = modeled[0].catalog_id;
    const pr = await api("/projection", { session_id: sid, commitment_ids: [id] });
    ok(sc, `POST /projection {session_id,[${id}]}`, pr.status === 200 && pr.data.label === "projected_if_completed", `score ${pr.data?.current?.score} -> ${pr.data?.projected?.score}`);
    const gp = await api(`/leaderboard/position?session_id=${sid}&catalog_ids=${id}`);
    ok(sc, "ghost marker (position&catalog_ids)", gp.data?.projected?.label === "projected_if_completed", `rank ${gp.data?.current?.rank} -> ${gp.data?.projected?.rank}`);
  }
  const cal = await api("/calibrate", { session_id: sid, therms: 60, gas_unit: "therms", start: "2026-09-01", end: "2026-09-30" });
  ok(sc, "POST /calibrate therms", cal.status === 200, `${cal.data?.pct_vs_expected_for_weather}% vs normal for weather`);
  const amt = await api("/calibrate", { session_id: sid, amount_usd: 80, start: "2026-09-01", end: "2026-09-30" });
  ok(sc, "POST /calibrate amount_usd", amt.status === 200 && !!amt.data?.extracted?.estimated_from_amount, amt.data?.detail?.code ?? `${amt.data?.pct_vs_expected_for_weather}%`);
  const map = await api(`/map/${sid}`);
  ok(sc, "GET /map/{session}", map.status === 200, `${map.data?.steps?.length} steps, lookalikes ${map.data?.lookalikes?.pool_size}`);
}

async function apiOnce() {
  const sc = "api errors";
  const c = await api("/compare", { listings: COMPARE.map((address) => ({ address })) });
  ok("api compare", "POST /compare Church vs Forest", c.status === 200, `winner ${c.data?.winner} diff ${c.data?.diff_usd_yr}/yr confident ${c.data?.confident}`);
  let r = await api("/estimate", { url: ZUMPER });
  ok(sc, "Zumper link -> 422 needs_address + hint", r.data?.detail?.code === "needs_address" && !!r.data.detail.hint, r.data?.detail?.hint);
  r = await api("/estimate", { address: NOT_HOME });
  ok(sc, "500 S State St -> 422 not_a_home", r.data?.detail?.code === "not_a_home");
  r = await api("/compare", { listings: [{ address: COMPARE[0] }, { url: ZUMPER }] });
  // ponytail: compare.py spreads the inner detail after code, so code is the inner one (needs_address), not estimate_failed.
  ok(sc, "compare with bad side -> 422 + listing b", r.status === 422 && r.data?.detail?.listing === "b", `code ${r.data?.detail?.code}`);
  ok(sc, "compare error code is estimate_failed (contract)", r.data?.detail?.code === "estimate_failed", `got ${r.data?.detail?.code}`, true);
  r = await api("/session/nope-not-a-session");
  ok(sc, "unknown session -> 404 not_found", r.status === 404 && r.data?.detail?.code === "not_found");
}

// ---------- web mode: the real pages ----------
let pw, browser;
const BAD_COPY = /illustrat|awaiting estimate|example grade|mock leaderboard|hardcoded for now|\$1,052|\$2,254|not a live city rank/i;

async function audit(page, sc, where) {
  const a = await page.evaluate(() => {
    const named = (el) => (el.getAttribute("aria-label") || el.getAttribute("aria-labelledby") || el.textContent.trim() || el.querySelector("img[alt]:not([alt=''])")) ? 1 : 0;
    const btn = [...document.querySelectorAll("button,[role=button]")].filter((b) => !named(b)).length;
    const divClick = [...document.querySelectorAll("div[onclick],span[onclick]")].length;
    const inputs = [...document.querySelectorAll("input:not([type=hidden]),textarea,select")].filter(
      (i) => !(i.labels?.length || i.getAttribute("aria-label") || i.getAttribute("aria-labelledby")),
    ).length;
    return {
      btn, divClick, inputs,
      live: document.querySelectorAll("[aria-live],[role=status],[role=alert]").length,
      overflow: document.documentElement.scrollWidth - window.innerWidth,
    };
  });
  ok(sc, `${where}: buttons named, inputs labelled`, a.btn + a.inputs + a.divClick === 0, `unnamed buttons ${a.btn}, unlabelled inputs ${a.inputs}, div onclick ${a.divClick}`);
  ok(sc, `${where}: aria-live/status present`, a.live > 0, "", true);
  ok(sc, `${where}: no horizontal scroll at this width`, a.overflow <= 1, `overflow ${a.overflow}px`);
}

async function newPage(sc, { width = 375, height = 812 } = {}) {
  // A full anonymous flow uses about 12 browser + 5 oracle requests. Leave room
  // for extra questions/effect fetches, without pacing its actual interactions.
  await reserveRequests(22, sc);
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(15000);
  const calls = [];
  let browserProtected = 0;
  let peakSharedBudget = 0;
  page.on("request", (q) => {
    if (!q.url().startsWith(API)) return;
    const h = q.headers();
    if ("x-agent-key" in h) rec(sc, "X-Agent-Key sent from the browser", "FAIL", q.url());
    if (protectedRequest(q.method(), q.url())) {
      recordRequest();
      browserProtected++;
      peakSharedBudget = Math.max(peakSharedBudget, protectedRequests.length);
    }
    calls.push(`${q.method()} ${q.url().slice(API.length).split("?")[0].replace(/\/[A-Za-z0-9_-]{8,}$/, "/:id")}${h.authorization ? " [bearer]" : ""}`);
  });
  page.on("response", (r) => {
    if (r.url().startsWith(API) && r.status() === 429) rec(sc, "browser received 429", "FAIL", new URL(r.url()).pathname);
  });
  page.on("close", () => ok(sc, "normal public request budget", peakSharedBudget <= REQUEST_LIMIT,
    `${browserProtected} protected browser calls; peak ${peakSharedBudget}/${REQUEST_LIMIT} including oracle calls`));
  page.on("pageerror", (e) => rec(sc, "page error", "FAIL", e.message.slice(0, 160)));
  page.on("console", (m) => m.type() === "error" && !/favicon|Failed to load resource/.test(m.text()) && rec(sc, "console error", "WARN", m.text().slice(0, 160)));
  return { ctx, page, calls };
}
const text = (page) => page.locator("body").innerText();
const button = (page, re) => page.getByRole("button", { name: re }).or(page.getByRole("link", { name: re })).first();
async function waitText(page, re, timeout = 20000) {
  try {
    await page.waitForFunction((src) => new RegExp(src, "i").test(document.body.innerText), re.source, { timeout });
    return true;
  } catch {
    return false;
  }
}
const stored = (page, key) => page.evaluate((k) => localStorage.getItem(k), key);

// Seeds a session the way W1 should have (estimate + answers via the API) so W2 can be checked on its own branch.
async function seed(page, addr) {
  const e = (await api("/estimate", { address: addr })).data;
  for (const q of e.questions) {
    const want = addr.startsWith(HEAT_INCLUDED_ADDR) && q.id === "heating_fuel" ? "Heat is included in my rent" : PICK[q.id];
    await api("/answer", { session_id: e.session_id, question_id: q.id, answer: (q.options.find((o) => o.label === want) ?? q.options[0]).value });
  }
  await page.evaluate((id) => localStorage.setItem("hr_session_id", id), e.session_id);
  return e.session_id;
}

async function webFlow(addr) {
  const w1 = `W1 ${short(addr)}`;
  const w2 = `W2 ${short(addr)}`;
  const { ctx, page, calls } = await newPage(`web ${short(addr)}`);
  let sid = null;
  // ---- W1: address -> survey -> sign-in (skip) -> grade
  try {
    await page.goto(`${WEB}/address`);
    await audit(page, w1, "/address");
    await page.getByLabel(/listing link or address/i).fill(addr);
    await button(page, /^next/i).click();
    // W1 may ask for the unit size first (multi-unit, sqft_estimated); skip keeps the first estimate.
    const unitAsk = page.getByLabel(/how big is the unit|unit size/i).first();
    await Promise.race([page.waitForURL(/\/survey/, { timeout: 40000 }), unitAsk.waitFor({ timeout: 40000 })]);
    if (await unitAsk.isVisible().catch(() => false)) {
      rec(w1, "unit-size ask shown (not in P3 design)", "WARN", "skipped");
      await audit(page, w1, "unit-size ask");
      await page.getByRole("button", { name: /^skip$/i }).first().click();
      await page.waitForURL(/\/survey/, { timeout: 20000 });
    }
    sid = await stored(page, "hr_session_id");
    ok(w1, "session saved as hr_session_id", !!sid, sid ?? "missing");
    if (!sid) throw new Error("no session saved; W1 not wired here");
    const first = (await api(`/session/${sid}`)).data;
    await page.waitForTimeout(800);
    await audit(page, w1, "/survey");
    ok(w1, "old hardcoded survey stepper gone", !/this month's gas bill/i.test(await text(page)));
    for (const q of first.questions) {
      const want = addr.startsWith(HEAT_INCLUDED_ADDR) && q.id === "heating_fuel" ? "Heat is included in my rent" : PICK[q.id] ?? q.options[0].label;
      const b = page.getByRole("button", { name: want, exact: true }).first();
      const shown = await b.isVisible().catch(() => false);
      ok(w1, `survey shows API question ${q.id} option "${want}"`, shown);
      if (shown) await Promise.all([page.waitForResponse((r) => r.url().includes("/answer"), { timeout: 15000 }).catch(() => null), b.click()]);
    }
    await button(page, /^next/i).click();
    // Sign-in is offered right before the grade with "Skip for now" (decision 2).
    const skip = page.getByRole("button", { name: /skip for now/i }).or(page.getByRole("link", { name: /skip for now/i })).first();
    const sawSkip = await skip.waitFor({ timeout: 15000 }).then(() => true, () => false);
    ok(w1, 'sign-in step with "Skip for now" before the grade', sawSkip);
    if (sawSkip) {
      await audit(page, w1, "sign-in step");
      await skip.click();
    }
    await page.waitForURL(/\/grade/, { timeout: 30000 });
    const s = (await api(`/session/${sid}`)).data;
    ok(w1, "answers reached POST /answer", first.questions.every((q) => q.id in (s.answers ?? {})), JSON.stringify(s.answers));
    const grades = displayedGrades(s);
    const gradeRe = new RegExp(`\\b${span(grades)}\\b`);
    ok(w1, `grade shown (${grades.join("–")})`, await waitText(page, gradeRe, 15000));
    const t = await text(page);
    if (s.percentile_city != null) {
      const pct = Math.round(s.percentile_city * 100);
      const heading = s.percentile_city >= .75 ? `Top ${Math.max(1, 100 - pct)}%`
        : s.percentile_city < .25 ? `Bottom ${Math.max(1, pct)}%` : "Middle 50%";
      ok(w1, "city percentile heading matches API", (await page.getByRole("heading", { level: 1 }).innerText()).trim() === heading,
        `${heading} from percentile ${s.percentile_city}`);
    }
    ok(w1, `score ${s.score} shown`, new RegExp(`\\b${s.score}\\b`).test(t), "", true);
    ok(w1, '"predicted" label', /predicted/i.test(t));
    ok(w1, `hidden rent ${s.hidden_rent_usd_mo}/mo shown`, t.includes(money(s.hidden_rent_usd_mo)), "", true);
    ok(w1, "no illustrative/mock copy on grade", !BAD_COPY.test(t), t.match(BAD_COPY)?.[0]);
    if (s.bill?.note) ok(w1, "bill.note shown (heat included)", t.includes(s.bill.note.slice(0, 25)));
    ok(w1, "address shown", t.toUpperCase().includes(s.building.address.split(",")[0].toUpperCase()), "", true);
    const hrefs = await page.$$eval("a[href]", (as) => as.map((a) => a.getAttribute("href")));
    ok(w1, "Compare link -> /compare?a=", hrefs.some((h) => /^\/compare\?a=/.test(h)), hrefs.filter((h) => /compare/.test(h)).join(" "));
    ok(w1, "Share link -> /share?session=<id>", hrefs.some((h) => h.includes(`/share?session=${sid}`)), hrefs.filter((h) => /share/.test(h)).join(" "));
    await audit(page, w1, "/grade");
    const next = button(page, /^next/i);
    await page.waitForFunction(() => [...document.querySelectorAll("button")].some((b) => /^next/i.test(b.textContent.trim()) && !b.disabled), null, { timeout: 10000 }).catch(() => {});
    await next.click();
    await page.waitForURL(/\/board/, { timeout: 30000 });
  } catch (e) {
    rec(w1, "flow stopped", "FAIL", e.message.split("\n")[0].slice(0, 200));
  }
  // ---- W2: board (rank, commitments -> ghost, monthly bill)
  try {
    if (!sid) {
      await page.goto(`${WEB}/`);
      sid = await seed(page, addr);
      rec(w2, "session seeded via API (W1 flow not available on this build)", "WARN", sid);
    }
    if (!/\/board/.test(page.url())) await page.goto(`${WEB}/board`);
    const pos = (await api(`/leaderboard/position?session_id=${sid}`)).data;
    ok(w2, `board rank ${pos.current.rank} of ${pos.current.of} shown`, await waitText(page, new RegExp(num(pos.current.rank)), 15000));
    let bt = await text(page);
    ok(w2, "no mock/hardcoded copy on board", !BAD_COPY.test(bt), bt.match(BAD_COPY)?.[0]);
    ok(w2, '"predicted" label', /predicted/i.test(bt));
    const sug = (await api(`/commitments/suggested?session_id=${sid}`)).data.commitments;
    const modeled = sug.filter((c) => !c.pending_model);
    if (sug.length) await waitText(page, new RegExp(sug[0].title.slice(0, 20).replace(/[()]/g, ".")), 15000);
    bt = await text(page);
    for (const c of sug.slice(0, 3)) ok(w2, `commitment "${c.title.slice(0, 30)}" listed`, bt.includes(c.title.slice(0, 20)), "", true);
    if (modeled.length) {
      const c = modeled[0];
      const gp = (await api(`/leaderboard/position?session_id=${sid}&catalog_ids=${c.catalog_id}`)).data;
      const pr = (await api("/projection", { session_id: sid, commitment_ids: [c.catalog_id] })).data;
      await page.getByRole("button", { name: new RegExp(c.title.slice(0, 20).replace(/[()]/g, "."), "i") }).first().click().catch(() => rec(w2, "toggle modeled commitment", "FAIL", "button not found"));
      ok(w2, `"projected if completed" after toggling ${c.catalog_id}`, await waitText(page, /projected if completed/i, 20000));
      ok(w2, `projected score ${pr.projected.score} shown`, await waitText(page, new RegExp(`score ${pr.projected.score}\\b`), 5000), "", true);
      ok(w2, `ghost at projected rank ${gp.projected.rank}`, await waitText(page, new RegExp(num(gp.projected.rank)), 3000), "", true);
    } else rec(w2, "toggle modeled commitment", "WARN", "no modeled commitment for this home (all pending_model)");
    await audit(page, w2, "/board");
    // Monthly bill (decision 3): typed therms.
    const no = page.getByRole("button", { name: /^no$/i }).first();
    if (await no.isVisible().catch(() => false)) await no.click();
    const gas = page.getByLabel(/gas used/i).first();
    if (await gas.isVisible({ timeout: 3000 }).catch(() => false)) {
      const cal = (await api("/calibrate", { session_id: sid, therms: 60, gas_unit: "therms", ...lastMonth() })).data;
      await gas.fill("60");
      await Promise.all([page.waitForResponse((r) => r.url().includes("/calibrate"), { timeout: 30000 }).catch(() => null), gas.press("Enter")]);
      ok(w2, "bill result: % vs normal for this weather", await waitText(page, /normal for (this|the) weather/i, 20000));
      bt = await text(page);
      const pct = Math.abs(cal.pct_vs_expected_for_weather);
      ok(w2, `bill % (${pct}) matches the API`, bt.includes(pct.toLocaleString("en-US", { maximumFractionDigits: 1 })) || bt.includes(String(Math.round(pct))), "", true);
      ok(w2, "early signal not called verified", !/\bverified (savings|reduction)\b/i.test(bt.replace(/not verified/gi, "")) || cal.verified, "", true);
      await audit(page, w2, "/board after bill");
    } else rec(w2, 'monthly bill "Gas used this month" input', "FAIL", "not found (label /gas used/)");
  } catch (e) {
    rec(w2, "flow stopped", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    ok(`web ${short(addr)}`, "API calls made by the pages", true, [...new Set(calls)].join(" | "));
    await ctx.close();
  }
}

function lastMonth() {
  const now = new Date();
  const f = (d) => d.toISOString().slice(0, 10);
  return { start: f(new Date(Date.UTC(now.getFullYear(), now.getMonth() - 1, 1))), end: f(new Date(Date.UTC(now.getFullYear(), now.getMonth(), 0))) };
}

async function webOnce() {
  // Compare (?a= is the grade screen's session id, as W1 links it), share, map
  let sc = "W3 compare";
  let { ctx, page, calls } = await newPage(sc, { width: 1280, height: 900 });
  try {
    const cmp = (await api("/compare", { listings: COMPARE.map((address) => ({ address })) })).data;
    const a = (await api("/estimate", { address: COMPARE[0] })).data;
    await page.goto(`${WEB}/compare?a=${encodeURIComponent(a.session_id)}`);
    const inputs = page.getByRole("textbox", { name: /address|listing/i });
    await page.waitForFunction(() => {
      const i = document.querySelector("input");
      return i && i.value && !i.disabled;
    }, null, { timeout: 15000 }).catch(() => {});
    ok(sc, "two listing inputs", (await inputs.count()) >= 2, `${await inputs.count()} inputs`);
    const pre = await inputs.nth(0).inputValue();
    ok(sc, "?a=<session> prefills listing A with its address", /624 CHURCH/i.test(pre), pre);
    if (!pre) await inputs.nth(0).fill(COMPARE[0]);
    await inputs.nth(1).fill(COMPARE[1]);
    await page.locator("button[type=submit]").first().click();
    const got = await waitText(page, new RegExp(money(cmp.diff_usd_yr).replace("$", "\\$")), 30000);
    ok(sc, `diff ${money(cmp.diff_usd_yr)}/yr (API, addresses only) shown`, got, got ? "" : (await text(page)).match(/costs \$[\d,]+\/yr more|\$[\d,]+\/yr more/)?.[0]);
    const t = await text(page);
    ok(sc, "winner named", /more to live in|lower predicted bill|winner/i.test(t));
    ok(sc, cmp.confident ? "confident: ranges don't overlap" : "not confident: too close to call", cmp.confident ? !/too close to call/i.test(t) : /too close to call|overlap/i.test(t));
    ok(sc, "no illustrative copy", !BAD_COPY.test(t), t.match(BAD_COPY)?.[0]);
    ok(sc, '"predicted" label', /predicted/i.test(t));
    await audit(page, sc, "/compare desktop");
    await page.setViewportSize({ width: 375, height: 812 });
    await audit(page, sc, "/compare 375px");
    ok(sc, "calls", calls.some((c) => c.startsWith("POST /compare")), [...new Set(calls)].join(" | "));
    // compare error: listing B without an address -> that side's message + hint
    await page.goto(`${WEB}/compare`);
    await inputs.nth(0).fill(COMPARE[0]);
    await inputs.nth(1).fill(ZUMPER);
    await page.locator("button[type=submit]").first().click();
    ok(sc, "listing B error shows the needs_address message", await waitText(page, /doesn't show the street address|what's the address/i, 20000));
    await page.route(`${API}/**`, (r) => r.abort());
    await page.locator("button[type=submit]").first().click();
    ok(sc, "API down -> unreachable message", await waitText(page, /isn't reachable/i, 15000));
    await page.unroute(`${API}/**`);
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }

  const est = (await api("/estimate", { address: ADDRS[0] })).data;
  sc = "W3 share";
  ({ ctx, page, calls } = await newPage(sc));
  try {
    await page.goto(`${WEB}/share?session=${est.session_id}`);
    const grades = displayedGrades(est);
    ok(sc, `grade ${grades.join("–")} shown`, await waitText(page, new RegExp(`\\b${span(grades)}\\b`), 15000));
    const t = await text(page);
    ok(sc, '"predicted" label', /predicted/i.test(t));
    ok(sc, `hidden rent ${money(est.hidden_rent_usd_mo)} shown`, t.includes(money(est.hidden_rent_usd_mo)), "", true);
    ok(sc, "no illustrative copy", !BAD_COPY.test(t), t.match(BAD_COPY)?.[0]);
    await audit(page, sc, "/share");
    await page.goto(`${WEB}/share?session=nope-not-a-session`);
    ok(sc, "expired session message", await waitText(page, /expired|send the listing again|not found/i, 10000));
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }

  for (const addr of MAP_ADDRS) {
    sc = `W3 map ${short(addr)}`;
    ({ ctx, page, calls } = await newPage(sc, { width: 1280, height: 900 }));
    try {
      const m = (await api("/estimate", { address: addr })).data;
      const map = (await api(`/map/${m.session_id}`)).data;
      await page.goto(`${WEB}/map?session=${m.session_id}`);
      ok(sc, "map canvas renders", await page.locator("canvas").first().waitFor({ timeout: 30000 }).then(() => true, () => false));
      await page.waitForFunction(() => document.querySelector("[data-city-count]") || document.querySelector("[role=alert]"), null, { timeout: 30000 }).catch(() => {});
      const city = await page.locator("[data-city-count]").first().getAttribute("data-city-count").catch(() => null);
      ok(sc, "city layer loaded", !!city, `${city} footprints`, true);
      ok(sc, "GET /map/{session} called (not the fixture)", calls.some((c) => c.startsWith("GET /map/")), [...new Set(calls)].join(" | "));
      const t = await text(page);
      ok(sc, `address ${map.address.split(",")[0]} shown`, t.toUpperCase().includes(map.address.split(",")[0].toUpperCase()));
      ok(sc, "no mock label / NaN / undefined", !/MOCK PREVIEW|\bNaN\b|undefined/.test(t), t.match(/MOCK PREVIEW|\bNaN\b|undefined/)?.[0]);
      // ponytail: Next's route announcer is an empty role=alert, so only count alerts with text.
      const alerts = (await page.locator("[role=alert]").allInnerTexts()).filter((s) => s.trim());
      ok(sc, "no map error shown", !alerts.length, alerts.join(" "));
      await audit(page, sc, "/map desktop");
      await page.setViewportSize({ width: 375, height: 812 });
      await audit(page, sc, "/map 375px");
    } catch (e) {
      rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
    } finally {
      await ctx.close();
    }
  }

  // Error paths on /address
  sc = "W1 errors";
  ({ ctx, page } = await newPage(sc));
  const tryAddr = async (value, re, label) => {
    await page.goto(`${WEB}/address`);
    await page.getByLabel(/listing link or address/i).fill(value);
    await button(page, /^next/i).click();
    ok(sc, label, await waitText(page, re, 20000));
    ok(sc, `${label}: stays on /address`, /\/address/.test(page.url()), page.url());
  };
  try {
    await tryAddr(ZUMPER, /doesn't show the street address/i, "Zumper link -> needs_address message");
    ok(sc, "needs_address hint (Ann Arbor, MI) shown", /Ann Arbor, MI/.test(await page.locator("[aria-live]").allInnerTexts().then((a) => a.join(" "))), "", true);
    await tryAddr(NOT_HOME, /doesn't look like a home/i, "500 S State St -> not_a_home message");
    await page.route(`${API}/**`, (r) => r.abort());
    await tryAddr(ADDRS[0], /isn't reachable/i, "API down -> unreachable message");
    await page.unroute(`${API}/**`);
    // board and grade without any session: should point back to /address, not crash
    await page.evaluate(() => localStorage.clear());
    for (const path of ["/grade", "/board", "/survey"]) {
      await page.goto(`${WEB}${path}`);
      await page.waitForTimeout(1500);
      const t = await text(page);
      ok(sc, `${path} with no session: no crash, no fake numbers`, !/\bNaN\b|undefined/.test(t) && !BAD_COPY.test(t), t.slice(0, 80).replace(/\s+/g, " "), true);
    }
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }
}

// Optional (SMOKE_SIGNIN=1 + AGENT_API_KEY in env): phone sign-in with a fictional number on a USE_MOCKS=1 API.
// Plays the agent's part (POST /auth/web/confirm) itself; checks the token lands in hr_token and polling stops.
async function webSignin() {
  const sc = "W1 signin";
  const phone = "+17345550142";
  const { ctx, page, calls } = await newPage(sc);
  try {
    await page.goto(`${WEB}/address`);
    await page.getByLabel(/listing link or address/i).fill(ADDRS[4]);
    await button(page, /^next/i).click();
    await page.waitForURL(/\/survey/, { timeout: 40000 });
    await button(page, /^next/i).click();
    await page.getByLabel(/phone/i).first().fill(phone);
    await page.getByRole("button", { name: /text|send|sign in|log ?in|continue/i }).first().click();
    ok(sc, 'shows "Text login 123456"', await waitText(page, /login \d{6}/i, 15000));
    const code = (await text(page)).match(/login (\d{6})/i)?.[1];
    const res = await fetch(`${API}/auth/web/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Agent-Key": process.env.AGENT_API_KEY },
      body: JSON.stringify({ code, phone }),
    });
    ok(sc, "agent confirm (test harness)", res.ok, String(res.status));
    await page.waitForFunction(() => !!localStorage.getItem("hr_token"), null, { timeout: 20000 }).catch(() => {});
    ok(sc, "token saved in hr_token", !!(await stored(page, "hr_token")));
    ok(sc, "user saved in hr_user_id", !!(await stored(page, "hr_user_id")));
    await page.waitForFunction(() => !!localStorage.getItem("hr_property_id"), null, { timeout: 15000 }).catch(() => {});
    ok(sc, "property adopted (hr_property_id)", !!(await stored(page, "hr_property_id")), calls.filter((c) => c.includes("properties")).join(" "));
    const before = calls.filter((c) => c.includes("/auth/web/")).length;
    await page.waitForTimeout(5000);
    ok(sc, "polling stopped after verified", calls.filter((c) => c.includes("/auth/web/")).length === before, `${before} polls`);
    ok(sc, "token never in URL", !/token=/.test(page.url()));
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }
}

// A preceding phase2-check may have used this IP. Begin with a clean window;
// later waits are based on observed requests and are split into <=30s sleeps.
await paceWait(WINDOW_MS + WINDOW_MARGIN_MS, "start (clear earlier local test traffic)");
if (MODE === "api" || MODE === "all") {
  for (const a of ADDRS) await apiFlow(a);
  await apiOnce();
}
if (MODE === "web" || MODE === "all") {
  pw = await import(process.env.PW ?? "playwright");
  browser = await pw.chromium.launch({ channel: process.env.PW_CHANNEL ?? "chrome", headless: process.env.HEADED !== "1" });
  for (const a of ADDRS) await webFlow(a);
  await webOnce();
  if (process.env.SMOKE_SIGNIN === "1" && process.env.AGENT_API_KEY) await webSignin();
  await browser.close();
}
const count = (st) => results.filter((r) => r.status === st).length;
console.log(`\n${count("PASS")} pass, ${count("WARN")} warn, ${count("FAIL")} fail  (API ${API}, web ${WEB})`);
process.exit(count("FAIL") ? 1 : 0);
