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
// Survey answers to pick when the API offers them (label text, exactly as the API sends it).
const PICK = { heating_fuel: "Gas", window_panes: "Single-pane", floor_level: "Middle floor", cooling_code: "Central AC" };
const HEAT_INCLUDED_ADDR = "1022 S Forest Ave"; // decision 4: this address answers "Heat is included in my rent"

const results = []; // {scope, check, status: PASS|FAIL|WARN, detail}
const rec = (scope, check, status, detail = "") => {
  results.push({ scope, check, status, detail });
  console.log(`${status.padEnd(4)} ${scope} :: ${check}${detail ? ` (${detail})` : ""}`);
};
const ok = (scope, check, cond, detail, soft = false) => rec(scope, check, cond ? "PASS" : soft ? "WARN" : "FAIL", detail);

async function api(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return { status: res.status, data: await res.json().catch(() => null) };
}
const money = (n) => `$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;
const num = (n) => `(${Math.round(n)}|${Math.round(n).toLocaleString("en-US")})`; // 1014 or 1,014
const span = (s) => (s.length === 1 ? s[0] : `${s[0]}\\s*(–|-|—|to)\\s*${s[s.length - 1]}`);
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
const BAD_COPY = /illustrat|awaiting estimate|example grade|middle 50%|mock leaderboard|hardcoded for now|\$1,052|\$2,254|not a live city rank/i;

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
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(15000);
  const calls = [];
  page.on("request", (q) => {
    if (!q.url().startsWith(API)) return;
    const h = q.headers();
    if (h["x-agent-key"]) rec(sc, "X-Agent-Key sent from the browser", "FAIL", q.url());
    calls.push(`${q.method()} ${q.url().slice(API.length).split("?")[0].replace(/\/[A-Za-z0-9_-]{8,}$/, "/:id")}${h.authorization ? " [bearer]" : ""}`);
  });
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

async function webFlow(addr) {
  const sc = `web ${short(addr)}`;
  const { ctx, page, calls } = await newPage(sc);
  try {
    await page.goto(`${WEB}/address`);
    await audit(page, sc, "/address");
    await page.getByLabel(/listing link or address/i).fill(addr);
    await button(page, /^next/i).click();
    await page.waitForURL(/\/survey|\/loading/, { timeout: 30000 });
    const sid = await stored(page, "hr_session_id");
    ok(sc, "session saved as hr_session_id", !!sid, sid ?? "missing");
    if (!sid) return;
    await page.waitForURL(/\/survey/, { timeout: 15000 });
    const first = (await api(`/session/${sid}`)).data;
    await page.waitForTimeout(800);
    await audit(page, sc, "/survey");
    const surveyText = await text(page);
    ok(sc, "old hardcoded survey stepper gone", !/this month's gas bill/i.test(surveyText), "", true);
    for (const q of first.questions) {
      const want = addr.startsWith(HEAT_INCLUDED_ADDR) && q.id === "heating_fuel" ? "Heat is included in my rent" : PICK[q.id] ?? q.options[0].label;
      const b = page.getByRole("button", { name: want, exact: true }).first();
      const shown = await b.isVisible().catch(() => false);
      ok(sc, `survey shows API question ${q.id} option "${want}"`, shown);
      if (shown) await b.click();
    }
    await button(page, /^next/i).click();
    // Sign-in is offered right before the grade with "Skip for now" (decision 2).
    const skip = page.getByRole("button", { name: /skip for now/i }).or(page.getByRole("link", { name: /skip for now/i })).first();
    const sawSkip = await skip.waitFor({ timeout: 15000 }).then(() => true, () => false);
    ok(sc, 'sign-in step with "Skip for now" before the grade', sawSkip);
    if (sawSkip) {
      await audit(page, sc, "sign-in step");
      await skip.click();
    }
    await page.waitForURL(/\/grade/, { timeout: 30000 });
    const s = (await api(`/session/${sid}`)).data;
    ok(sc, "answers reached POST /answer", first.questions.every((q) => q.id in (s.answers ?? {})), JSON.stringify(s.answers));
    const gradeRe = new RegExp(`\\b${span(s.locked ? [s.grade] : s.grade_span)}\\b`);
    ok(sc, `grade shown (${s.locked ? s.grade : s.grade_span.join("–")})`, await waitText(page, gradeRe, 15000));
    const t = await text(page);
    ok(sc, `score ${s.score} shown`, new RegExp(`\\b${s.score}\\b`).test(t), "", true);
    ok(sc, '"predicted" label', /predicted/i.test(t));
    ok(sc, `hidden rent ${s.hidden_rent_usd_mo}/mo shown`, t.includes(money(s.hidden_rent_usd_mo)), "", true);
    ok(sc, "no illustrative/mock copy on grade", !BAD_COPY.test(t), t.match(BAD_COPY)?.[0]);
    if (s.bill?.note) ok(sc, "bill.note shown (heat included)", t.includes(s.bill.note.slice(0, 25)));
    ok(sc, "address shown", t.toUpperCase().includes(s.building.address.split(",")[0].toUpperCase()), "", true);
    const hrefs = await page.$$eval("a[href]", (as) => as.map((a) => a.getAttribute("href")));
    ok(sc, "Compare link -> /compare?a=", hrefs.some((h) => /^\/compare\?a=/.test(h)), hrefs.filter((h) => /compare/.test(h)).join(" "));
    ok(sc, "Share link -> /share?session=<id>", hrefs.some((h) => h.includes(`/share?session=${sid}`)), hrefs.filter((h) => /share/.test(h)).join(" "));
    await audit(page, sc, "/grade");

    // Board
    const next = button(page, /^next/i);
    await next.waitFor({ timeout: 10000 });
    await page.waitForFunction(() => [...document.querySelectorAll("button")].some((b) => /^next/i.test(b.textContent.trim()) && !b.disabled), null, { timeout: 10000 }).catch(() => {});
    await next.click();
    await page.waitForURL(/\/board/, { timeout: 30000 });
    const pos = (await api(`/leaderboard/position?session_id=${sid}`)).data;
    ok(sc, `board rank ${pos.current.rank} of ${pos.current.of} shown`, await waitText(page, new RegExp(num(pos.current.rank)), 15000));
    let bt = await text(page);
    ok(sc, "no mock/hardcoded copy on board", !BAD_COPY.test(bt), bt.match(BAD_COPY)?.[0]);
    const sug = (await api(`/commitments/suggested?session_id=${sid}`)).data.commitments;
    const modeled = sug.filter((c) => !c.pending_model);
    for (const c of sug.slice(0, 3)) ok(sc, `commitment "${c.title.slice(0, 30)}" listed`, bt.includes(c.title.slice(0, 20)), "", true);
    if (modeled.length) {
      const c = modeled[0];
      const gp = (await api(`/leaderboard/position?session_id=${sid}&catalog_ids=${c.catalog_id}`)).data;
      await page.getByRole("button", { name: new RegExp(c.title.slice(0, 20).replace(/[()]/g, "."), "i") }).first().click().catch(() => rec(sc, "toggle modeled commitment", "FAIL", "button not found"));
      ok(sc, '"projected if completed" after toggle', await waitText(page, /projected if completed/i, 15000));
      ok(sc, `ghost marker at projected rank ${gp.projected.rank}`, await waitText(page, new RegExp(num(gp.projected.rank)), 5000), "", true);
    } else rec(sc, "toggle modeled commitment", "WARN", "no modeled commitment for this home");
    await audit(page, sc, "/board");
    // Monthly bill (decision 3): typed therms.
    const no = page.getByRole("button", { name: /^no$/i }).first();
    if (await no.isVisible().catch(() => false)) await no.click();
    const gas = page.getByLabel(/gas used/i).first();
    if (await gas.isVisible({ timeout: 3000 }).catch(() => false)) {
      await gas.fill("60");
      const send = page.getByRole("button", { name: /check|send|compare|submit|save|add/i }).last();
      await (await send.isVisible() ? send.click() : gas.press("Enter"));
      ok(sc, "bill result: % vs normal for this weather", await waitText(page, /normal for (this|the) weather/i, 20000));
      bt = await text(page);
      ok(sc, "bill wording never says verified for an early signal", !/\bverified\b/i.test(bt) || /early signal/i.test(bt), "", true);
    } else rec(sc, 'monthly bill "Gas used this month" input', "FAIL", "not found (label /gas used/)");
    ok(sc, "board calls", true, [...new Set(calls)].join(" | "));
  } catch (e) {
    rec(sc, "flow aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
    ok(sc, "calls so far", true, [...new Set(calls)].join(" | "));
  } finally {
    await ctx.close();
  }
}

async function webOnce() {
  // Compare, share, map
  let sc = "web compare";
  let { ctx, page, calls } = await newPage(sc, { width: 1280, height: 900 });
  try {
    const cmp = (await api("/compare", { listings: COMPARE.map((address) => ({ address })) })).data;
    await page.goto(`${WEB}/compare?a=${encodeURIComponent(COMPARE[0])}`);
    const inputs = page.locator("input[type=text],input:not([type]),input[type=url],input[type=search]");
    ok(sc, "two listing inputs", (await inputs.count()) >= 2, `${await inputs.count()} inputs`);
    if ((await inputs.nth(0).inputValue()) === "") await inputs.nth(0).fill(COMPARE[0]);
    else ok(sc, "?a= prefills listing A", true, await inputs.nth(0).inputValue());
    await inputs.nth(1).fill(COMPARE[1]);
    await page.getByRole("button", { name: /compare|battle|go|fight|next/i }).first().click();
    ok(sc, `diff ${money(cmp.diff_usd_yr)}/yr shown`, await waitText(page, new RegExp(money(cmp.diff_usd_yr).replace("$", "\\$")), 30000));
    const t = await text(page);
    ok(sc, "no illustrative copy", !BAD_COPY.test(t), t.match(BAD_COPY)?.[0]);
    ok(sc, '"predicted" label', /predicted/i.test(t));
    await audit(page, sc, "/compare desktop");
    await page.setViewportSize({ width: 375, height: 812 });
    await audit(page, sc, "/compare 375px");
    ok(sc, "calls", calls.includes("POST /compare"), [...new Set(calls)].join(" | "));
    // compare error: one side without an address
    await page.goto(`${WEB}/compare`);
    await inputs.nth(0).fill(COMPARE[0]);
    await inputs.nth(1).fill(ZUMPER);
    await page.getByRole("button", { name: /compare|battle|go|fight|next/i }).first().click();
    ok(sc, "estimate_failed on B shows the needs_address message", await waitText(page, /doesn't show the street address|what's the address/i, 20000));
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }

  const est = (await api("/estimate", { address: ADDRS[0] })).data;
  sc = "web share";
  ({ ctx, page, calls } = await newPage(sc));
  try {
    await page.goto(`${WEB}/share?session=${est.session_id}`);
    ok(sc, `grade ${est.locked ? est.grade : est.grade_span.join("–")} shown`, await waitText(page, new RegExp(`\\b${span(est.locked ? [est.grade] : est.grade_span)}\\b`), 15000));
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

  sc = "web map";
  ({ ctx, page, calls } = await newPage(sc, { width: 1280, height: 900 }));
  try {
    await page.goto(`${WEB}/`);
    await page.evaluate((id) => localStorage.setItem("hr_session_id", id), est.session_id);
    await page.goto(`${WEB}/map?session=${est.session_id}`);
    ok(sc, "map canvas renders", await page.locator("canvas").first().waitFor({ timeout: 20000 }).then(() => true, () => false));
    await page.waitForTimeout(2000);
    ok(sc, "GET /map/{session} called (not the 912 Mary St fixture)", calls.some((c) => c.startsWith("GET /map/")), [...new Set(calls)].join(" | "));
    const t = await text(page);
    ok(sc, "fixture address not shown", !/912 Mary/i.test(t), "", true);
    ok(sc, "no NaN/undefined on page", !/\bNaN\b|undefined/.test(t), t.match(/\bNaN\b|undefined/)?.[0]);
    await audit(page, sc, "/map desktop");
    await page.setViewportSize({ width: 375, height: 812 });
    await audit(page, sc, "/map 375px");
  } catch (e) {
    rec(sc, "aborted", "FAIL", e.message.split("\n")[0].slice(0, 200));
  } finally {
    await ctx.close();
  }

  // Error paths on /address
  sc = "web errors";
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
  const sc = "web signin";
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
