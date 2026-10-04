import assert from "node:assert/strict";
import { test } from "node:test";
import { mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadEnvFiles } from "../src/env.ts";
import { Accounts, accountHandle } from "../src/accounts.ts";
import { httpApi, type Api, type ApiResult, type Reminder } from "../src/api.ts";
import { Conversations, LOGIN } from "../src/conversation.ts";
import { mockApi } from "../src/mockApi.ts";
import { billResultText, projectionText, suggestionsText } from "../src/phase2Replies.ts";
import { parseTypedBill, estimateText } from "../src/replies.ts";
import { ReceiptStore, ReminderPoller } from "../src/reminders.ts";

const sender = { handle: "+12025550164" };
const ok = <T>(data: T): ApiResult<T> => ({ ok: true, data });
const must = <T>(r: ApiResult<T>): T => { assert.equal(r.ok, true); return (r as { ok: true; data: T }).data; };
async function home(api = mockApi()) {
  const chat = new Conversations(api);
  const reply = (text: string) => chat.reply("test", text, sender);
  await reply("1514 Morton Ave, Ann Arbor, MI"); await reply("850"); await reply("gas"); await reply("single"); await reply("top");
  const account = must(await api.authPhone({ phone: sender.handle }));
  return { api, chat, reply, userId: account.user_id, propertyId: account.current_property_id! };
}

test("agent-key header covers every API endpoint so texters do not share the public IP budget", async () => {
  const seen: { path: string; method: string; key: string | null }[] = [];
  const fetcher = (async (url: string, init: RequestInit) => { seen.push({ path: new URL(url).pathname, method: init.method!, key: new Headers(init.headers).get("X-Agent-Key") }); return new Response(JSON.stringify({})); }) as typeof fetch;
  const api = httpApi("http://api", fetcher, () => {}, "test-secret");
  await api.authPhone({ phone: sender.handle }); await api.confirmLogin({ phone: sender.handle, code: "123456" }); await api.me("u"); await api.patchMe("u", { pending_checkin: null }); await api.property({ user_id: "u", session_id: "s" }); await api.checkin("u"); await api.suggestions("p"); await api.commitments("p"); await api.commit({ user_id: "u", property_id: "p", catalog_id: "window_upgrade" }); await api.updateCommitment("c", "completed"); await api.projection({ property_id: "p", commitment_ids: ["c"] }); await api.remindersDue(); await api.reminderSent("r"); await api.reminderInbound("u"); await api.reminderControl("u", "stop"); await api.reminderDemo("u"); await api.calendarConnect("u"); await api.calendarReminder({ user_id: "u", commitment_id: "c", cadence: "once" }); await api.calibrate({ session_id: "s", property_id: "p", therms: 120, start: "2026-09-01", end: "2026-09-30" });
  await api.estimate({ address: "1514 Morton Ave" });
  await api.answer({ session_id: "s", question_id: "heating_fuel", answer: "gas" });
  await api.session("s"); await api.fixes("s");
  await api.calibrate({ session_id: "s", therms: 120, start: "2026-09-01", end: "2026-09-30" });
  assert.ok(seen.every((x) => x.key === "test-secret")); assert.ok(seen.some((x) => x.method === "PATCH"));
  assert.equal(seen.length, 24);
});

test("an unconfigured agent key is omitted rather than sent as an empty header", async () => {
  const fetcher = (async (_url: string, init: RequestInit) => {
    assert.equal(new Headers(init.headers).has("X-Agent-Key"), false);
    return new Response(JSON.stringify({}));
  }) as typeof fetch;
  await httpApi("http://api", fetcher, () => {}).estimate({ address: "1514 Morton Ave" });
});

test("account cache normalizes phone, preserves numeric email, shares first request, retries new ref", async () => {
  const api = mockApi(); let calls = 0; const auth = api.authPhone; api.authPhone = async (req) => { calls++; return auth(req); };
  const accounts = new Accounts(api);
  const [a, b] = await Promise.all([accounts.resolve({ handle: "202-555-0164" }), accounts.resolve(sender)]);
  assert.equal(must(a).user_id, must(b).user_id); assert.equal(calls, 1);
  assert.equal(accountHandle("renter1234567890@EXAMPLE.com"), "renter1234567890@example.com");
  await accounts.resolve(sender, "web1"); await accounts.resolve(sender, "web1"); assert.equal(calls, 2);
});

test("login intent is exactly six digits; success and original API error text", async () => {
  for (const text of ["login 123456", "LOGIN\t123456"]) assert.ok(LOGIN.test(text));
  for (const text of ["login 12345", "login 1234567", "please login 123456", "login 123456 now"]) assert.ok(!LOGIN.test(text));
  const api = mockApi(); const chat = new Conversations(api);
  assert.match(await chat.reply("c", "LOGIN 123456", sender), /You're signed in on the web ✅/);
  api.confirmLogin = async () => ({ ok: false, code: "bad_code", message: "This exact code is gone." });
  assert.match(await chat.reply("c", "login 000000", sender), /This exact code is gone\.$/);
});

test("lock auto-adopts answers; options → mixed accept → honest projection → reported done", async () => {
  const { api, reply, propertyId } = await home(); assert.ok(propertyId);
  const options = await reply("what can I do"); assert.match(options, /1\) Upgrade single-pane windows.*\$125\/yr less.*699 kg.*4 GRH/);
  assert.match(options, /2\) Air sealing.*Tip only/); assert.doesNotMatch(options.split("\n").find((x) => x.startsWith("2)"))!, /\$|\d+ GRH|\d+ kg/);
  assert.match(options, /Never set below 64°F/);
  const accepted = await reply("do 1 and 3 by 2026-11-01"); assert.match(accepted, /Projected if completed: grade B/); assert.doesNotMatch(accepted, /your new grade/i); assert.match(accepted, /Never set below 64°F/);
  const commitments = must(await api.commitments(propertyId)).commitments; assert.equal(commitments.length, 2);
  assert.match(await reply("done 1"), /Reported complete.*current grade is unchanged/);
  assert.equal(must(await api.commitments(propertyId)).commitments.find((c) => c.catalog_id === "window_upgrade")!.evidence, "reported");
});

test("restart rehydrates current home and pending checkin; done requires a displayed list", async () => {
  const { api, userId } = await home(); await api.checkin(userId);
  const restarted = new Conversations(api);
  assert.match(await restarted.reply("new-space", "hi", sender), /Welcome back, still at 1514 Morton/);
  assert.match(await restarted.reply("new-space", "yes", sender), /120 therms.*120 ccf.*\$85/);
  assert.match(await restarted.reply("new-space", "done 1", sender), /Say "options" first/);
});

test("monthly therms, ccf and dollars use last full month; malformed numbers/dates are rejected", () => {
  const today = new Date(2026, 9, 4);
  assert.deepEqual(parseTypedBill("120 therms", today), { therms: 120, start: "2026-09-01", end: "2026-09-30" });
  assert.deepEqual(parseTypedBill("120 ccf", today), { therms: 120, gas_unit: "ccf", start: "2026-09-01", end: "2026-09-30" });
  assert.deepEqual(parseTypedBill("$85", today), { amount_usd: 85, start: "2026-09-01", end: "2026-09-30" });
  assert.equal((parseTypedBill("1,200 therms", today) as any).therms, 1200);
  for (const text of ["12,00 therms", "-2 therms", "$-5", "120 therms 2026-02-30 to 2026-03-04"]) assert.ok("error" in parseTypedBill(text, today)!);
});

test("bill result stays provisional, dedupes, includes property and clears pending checkin", async () => {
  const { api, reply, userId, propertyId } = await home(); await reply("checkin"); await reply("yes");
  const seen: any[] = []; const calibrate = api.calibrate; api.calibrate = async (req) => { seen.push(req); return calibrate(req); };
  const text = await reply("120 therms"); assert.equal(seen[0].property_id, propertyId);
  assert.match(text, /This bill suggests grade A, but one bill.*your grade stays/); assert.match(text, /not a verified reduction/); assert.doesNotMatch(text, /your new grade/i);
  assert.equal(must(await api.me(userId)).pending_checkin, null);
  assert.match(await reply("$85 2026-08-01 to 2026-08-31"), /estimated from your bill amount/);
});

test("stop/pause survive inbound replies and restart; resume restores reminder state", async () => {
  const { api, reply, userId } = await home();
  assert.match(await reply("stop"), /stopped.*still answer/); await reply("options"); assert.equal(must(await api.reminderInbound(userId)).stopped, true);
  assert.match(await reply("remind-now"), /stopped or paused/);
  const restarted = new Conversations(api); await restarted.reply("r", "resume", sender); assert.equal(must(await api.reminderInbound(userId)).stopped, false);
  await restarted.reply("r", "pause", sender); assert.equal(must(await api.reminderInbound(userId)).paused, true);
  assert.match(await restarted.reply("r", "remind-now", sender), /stopped or paused/);
});

test("moved archives old home, ref and unit-size replacements never bill the old property", async () => {
  const { api, reply, userId, propertyId } = await home();
  await reply("moved"); await reply("912 Mary St, Ann Arbor, MI");
  const me = must(await api.me(userId)); assert.notEqual(me.current_property_id, propertyId); assert.equal(me.properties.find((p) => p.id === propertyId)!.active, false);
  let sent: any; const cal = api.calibrate; api.calibrate = async (req) => { sent = req; return cal(req); };
  await reply("700"); assert.match(await reply("120 therms"), /Say "save"/); assert.equal(sent, undefined);
  await reply("Hi (ref another-web-session)"); assert.match(await reply("120 therms"), /Say "save"/); assert.equal(sent, undefined);
});

test("Calendar connects separately, only accepted dated commitments, repeat avoids duplicate; failure leaves commitment", async () => {
  const { api, reply, propertyId } = await home(); await reply("options"); await reply("do 1 by 2026-11-01");
  assert.match(await reply("add to calendar"), /mock Calendar.*\nConnect Calendar:/);
  let calls = 0; const create = api.calendarReminder; api.calendarReminder = async (req) => { calls++; return create(req); };
  assert.match(await reply("calendar connected"), /Mock Calendar reminder/); await reply("calendar connected"); assert.equal(calls, 1);
  assert.equal(must(await api.commitments(propertyId)).commitments[0].status, "accepted");
});

test("heat included quotes renter cooling only and the building-grade explanation", async () => {
  const api = mockApi(); const e = must(await api.estimate({ address: "test" }));
  e.bill.building_annual = e.bill.annual; e.bill.annual = { p10: 10, p50: 20, p90: 30 }; e.bill.note = "Heat is paid by your landlord; the grade still rates the building.";
  assert.match(estimateText(e), /Your cooling bill a year.*\$20/); assert.match(estimateText(e), /grade still rates the building/);
});

const reminder: Reminder = { reminder_id: "r1", user_id: "u1", handle: sender.handle, kind: "task", text_hint: "Close the storm windows.", property_id: "p1" };
const receipt = () => new ReceiptStore(join(mkdtempSync(join(tmpdir(), "a16-reminders-")), "receipts.json"));
test("one serialized poll; delivered receipt retries ack across restart, never text; failed ack blocks new IDs", async () => {
  const api = mockApi(); let ackOK = false; let due = [reminder]; let sends = 0;
  api.remindersDue = async () => ok(due);
  api.reminderSent = async () => ackOK ? ok({ stopped: false, paused: false }) : ({ ok: false, code: "offline", message: "offline" });
  const store = receipt(); const send = async () => { sends++; };
  const poller = new ReminderPoller(api, send, store, () => {});
  await Promise.all([poller.poll(), poller.poll()]); assert.equal(sends, 1); assert.equal(store.ids.r1, "delivered");
  due = [reminder, { ...reminder, reminder_id: "r2" }];
  const restarted = new ReminderPoller(api, send, store, () => {}); await restarted.poll(); assert.equal(sends, 1);
  ackOK = true; await restarted.poll(); assert.equal(sends, 2); assert.equal(store.ids.r1, "acknowledged");
});

test("failed send stays queued; uncertain crash receipt blocks resend; receipt file has no PII and mode600", async () => {
  const api = mockApi(); api.remindersDue = async () => ok([reminder]); api.reminderSent = async () => ok({ stopped: false, paused: false });
  const dir = mkdtempSync(join(tmpdir(), "a16-r-")); const path = join(dir, "r.json"); const store = new ReceiptStore(path);
  const bad = new ReminderPoller(api, async () => { throw new Error("transport"); }, store, () => {}); await bad.poll(); assert.equal(store.ids.r1, undefined);
  store.set("r1", "sending"); let sent = 0; await new ReminderPoller(api, async () => { sent++; }, new ReceiptStore(path), () => {}).poll(); assert.equal(sent, 0);
  assert.equal(statSync(path).mode & 0o777, 0o600); assert.doesNotMatch(readFileSync(path, "utf8"), /1202555|Close the storm|p1/);
});

test("Calendar failure never undoes an accepted commitment; bill-regraded current blocks stale projection", async () => {
  const { api, reply, userId, propertyId } = await home(); await reply("options"); await reply("do 1 by 2026-11-01");
  api.calendarConnect = async () => ({ ok: false, code: "calendar_unavailable", message: "Google isn't reachable." });
  assert.match(await reply("add to calendar"), /Google isn't reachable.*commitments are still saved/);
  assert.equal(must(await api.commitments(propertyId)).commitments[0].status, "accepted");
  const me = api.me; api.me = async (id) => { const r = await me(id); if (r.ok && r.data.current_grade) r.data.current_grade.source = "bill_regrade"; return r; };
  let projections = 0; api.projection = async () => { projections++; throw new Error("must not project stale baseline"); };
  const result = await reply("do 1"); assert.match(result, /updated baseline isn't available/); assert.equal(projections, 0);
});

test("photo uses the saved property and vision errors pass through; substantive bill snapshot uses current wording", async () => {
  const { api, chat, propertyId } = await home(); let req: any;
  api.calibrate = async (r) => { req = r; return { ok: false, code: "vision_unavailable", message: "Reading bill photos isn't working. Type the numbers instead." }; };
  const result = await chat.respond("photo", { kind: "photo", mimeType: "image/jpeg", read: async () => Buffer.from("fixture") }, sender);
  assert.equal(req.property_id, propertyId); assert.equal(req.bill_image_base64, Buffer.from("fixture").toString("base64"));
  assert.match(result[0], /Type the numbers instead/);
  const e = must(await api.estimate({ address: "test" }));
  assert.match(billResultText({ estimate: e, pct_vs_expected_for_weather: -120, meaningful: true, streak_months: 1, badges: [], verified: true, snapshot: { grade: "B", source: "bill_regrade", provisional: false, label: "from your bill, adjusted for weather" } }), /Current grade B — from your bill, adjusted for weather/);
});

test("uncertain receipt blocks a different day's reminder until manual recovery", async () => {
  const api = mockApi(); const store = receipt(); store.set("old-id", "sending"); let calls = 0;
  api.remindersDue = async () => { calls++; return ok([{ ...reminder, reminder_id: "new-id" }]); };
  await new ReminderPoller(api, async () => { throw new Error("must not send"); }, store, () => {}).poll(); assert.equal(calls, 0);
});

test("mock reminder inbound resets unanswered but preserves auto-pause after two unacknowledged replies", async () => {
  const { api, userId } = await home(); const r = must(await api.reminderDemo(userId));
  assert.equal(must(await api.reminderSent(r.reminder_id)).unanswered, 1);
  assert.equal(must(await api.reminderSent(r.reminder_id)).unanswered, 1); // same ID is idempotent
  await api.reminderControl(userId, "pause"); const state = must(await api.reminderInbound(userId)); assert.equal(state.unanswered, 0); assert.equal(state.paused, true);
});


test("empty agent file placeholders fall through to root values; environment and nonempty overrides win", () => {
  const dir = mkdtempSync(join(tmpdir(), "a16-env-")); const agent = join(dir, "agent.env"), root = join(dir, "root.env");
  writeFileSync(agent, 'AGENT_API_KEY=\nPHOTON_PROJECT_ID=\nPUBLIC_URL="https://agent.example"\nEMPTY=\n');
  writeFileSync(root, 'AGENT_API_KEY="test-root-key"\nPHOTON_PROJECT_ID=test-project\nPUBLIC_URL=https://root.example\nEMPTY=root-default\n');
  const values: NodeJS.ProcessEnv = { PHOTON_PROJECT_ID: "process-project", EMPTY: "" }; loadEnvFiles([agent, root], values);
  assert.deepEqual(values, { PHOTON_PROJECT_ID: "process-project", EMPTY: "", AGENT_API_KEY: "test-root-key", PUBLIC_URL: "https://agent.example" });
});

test("mock included answer preserves building band/CO2 and quotes cooling only; single panes do not earn double-pane badge", async () => {
  const api = mockApi(); const first = must(await api.estimate({ address: "1514 Morton Ave" }));
  const included = must(await api.answer({ session_id: first.session_id!, question_id: "heating_fuel", answer: "included" }));
  assert.ok(included.bill.building_annual); assert.ok(included.bill.annual.p50! < included.bill.building_annual.p50!); assert.deepEqual(included.co2_t, first.co2_t);
  const single = must(await api.answer({ session_id: first.session_id!, question_id: "window_panes", answer: "1" }));
  assert.ok(!single.badges!.includes("double-pane-club")); assert.match(estimateText(single), /cooling only/);
});


test("manual direct delivery obeys global receipts and retries a matching delivered acknowledgement without texting", async () => {
  const api = mockApi(); let sends = 0, acknowledgements = 0;
  api.reminderSent = async () => { acknowledgements++; return ok({ stopped: false, paused: false }); };
  const store = receipt(); store.set("old-id", "sending");
  const poller = new ReminderPoller(api, async () => { sends++; }, store, () => {});
  await poller.deliver(reminder); assert.equal(sends, 0);
  store.set("old-id", "delivered"); await poller.deliver(reminder); assert.equal(sends, 0);
  await poller.deliver({ ...reminder, reminder_id: "old-id" }); assert.equal(acknowledgements, 1); assert.equal(sends, 0);
  await poller.deliver(reminder); assert.equal(sends, 1);
});
