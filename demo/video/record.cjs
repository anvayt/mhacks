#!/usr/bin/env node
// Six real API beats, recorded sequentially. No API route mocks or fixture replay.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const args = new Set(process.argv.slice(2));
if (args.has('--help')) {
  console.log('make demo-video [VIDEO_ARGS="--dry-run|--record"]\nBASE_URL=http://localhost:3000 API=http://localhost:8000\nVIEWPORTS=desktop,mobile PAUSE_MS=3500 TIMEOUT_MS=120000 HEADED=1\nVIDEO_LOCAL_AUTH=1 USE_MOCKS=1 AGENT_API_KEY=… (local isolated mock-auth API only)');
  process.exit(0);
}
for (const arg of args) assert(['--dry-run', '--record'].includes(arg), `Unknown argument: ${arg}`);
assert(!(args.has('--dry-run') && args.has('--record')), 'Choose dry-run OR record.');
const record = args.has('--record'); // Final capture is always an explicit action after dev merges.
const BASE = new URL(process.env.BASE_URL || 'http://localhost:3000').origin;
const API = new URL(process.env.API || process.env.API_BASE_URL || 'http://localhost:8000').origin;
const timeout = Number(process.env.TIMEOUT_MS || 120000);
const pause = Number(process.env.PAUSE_MS || (record ? 3500 : 500));
assert(Number.isFinite(timeout) && timeout > 0 && Number.isFinite(pause) && pause >= 0, 'Invalid timing configuration.');
const sizes = { desktop: { width: 1280, height: 720 }, mobile: { width: 390, height: 844 } };
const viewports = (process.env.VIEWPORTS || 'desktop,mobile').split(',');
viewports.forEach(v => assert(sizes[v], `Unknown viewport: ${v}`));
const id = new Date().toISOString().replace(/[:.]/g, '-');
const out = path.join(__dirname, 'out', `${record ? 'record' : 'dry-run'}-${id}`);
const report = { started_at: new Date().toISOString(), mode: record ? 'record' : 'dry-run', base_url: BASE, api: API, runs: [] };
const MORTON = '1514 Morton Ave, Ann Arbor, MI';
const ARROW = '2322 Arrowwood Trl, Ann Arbor, MI';
const YARD = '615 S Main St, Ann Arbor, MI';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
class Blocked extends Error {}

async function request(endpoint, body, headers = {}) {
  let response;
  try {
    response = await fetch(`${API}${endpoint}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(timeout),
    });
  } catch (e) { throw new Blocked(`${endpoint}: API unreachable (${e.name})`); }
  const json = await response.json().catch(() => ({}));
  if (!response.ok) throw new Blocked(`${endpoint}: HTTP ${response.status} ${json.detail?.code || ''}: ${json.detail?.message || 'request failed'}`);
  return json;
}

async function caption(page, title, detail = '') {
  await page.evaluate(({ title, detail, dry }) => {
    let box = document.getElementById('demo-video-caption');
    if (!box) {
      box = document.createElement('aside'); box.id = 'demo-video-caption';
      box.setAttribute('aria-label', 'Demo video caption');
      Object.assign(box.style, { position: 'fixed', zIndex: '2147483647', left: '12px', right: '12px', bottom: '12px',
        padding: '12px 16px', background: 'rgba(12,23,43,.94)', color: 'white', borderRadius: '12px',
        font: '600 16px/1.4 system-ui,sans-serif', pointerEvents: 'none', boxShadow: '0 4px 20px #0004' });
      document.body.appendChild(box);
    }
    box.replaceChildren();
    const heading = document.createElement('div'); heading.textContent = `${dry ? 'REHEARSAL · ' : ''}${title}`;
    const note = document.createElement('div'); note.textContent = detail; note.style.cssText = 'font-size:12px;font-weight:400;margin-top:3px';
    box.append(heading, note);
  }, { title, detail, dry: !record });
}

async function runViewport(browser, name) {
  const dir = path.join(out, name); await fs.mkdir(dir, { recursive: true });
  const context = await browser.newContext({ viewport: sizes[name], deviceScaleFactor: 1, locale: 'en-US',
    timezoneId: 'America/Detroit', ...(record ? { recordVideo: { dir, size: sizes[name] } } : {}) });
  const page = await context.newPage(); page.setDefaultTimeout(timeout); page.setDefaultNavigationTimeout(timeout);
  const run = { viewport: name, size: sizes[name], beats: [], evidence: [], browser_errors: [] }; report.runs.push(run);
  page.on('pageerror', e => run.browser_errors.push(e.message));
  // Never log headers, auth codes, tokens, request bodies or browser storage.
  let shot = 0, morton = null, arrow = null;
  async function capture(slug, title, detail, focus) {
    if (focus) {
      await focus.scrollIntoViewIfNeeded();
      await focus.evaluate(el => el.scrollIntoView({ block: 'center', inline: 'nearest' }));
    }
    await caption(page, title, detail); await delay(pause);
    const file = `${String(++shot).padStart(2, '0')}-${slug}.png`;
    await page.screenshot({ path: path.join(dir, file) });
    run.evidence.push(file);
  }
  async function action(endpoint, act) {
    const pending = page.waitForResponse(r => new URL(r.url()).pathname === endpoint && r.request().method() === 'POST');
    const [response] = await Promise.all([pending, act()]);
    assert.equal(new URL(response.url()).origin, API, `Web is using a different API: ${new URL(response.url()).origin}; restart web with NEXT_PUBLIC_API_BASE_URL=${API}.`);
    const json = await response.json();
    if (!response.ok()) throw new Blocked(`${endpoint}: HTTP ${response.status()} ${json.detail?.code || ''}: ${json.detail?.message || 'request failed'}`);
    return json;
  }
  async function beat(number, title, fn) {
    const started = Date.now();
    try {
      const numbers = await fn();
      run.beats.push({ beat: number, title, status: 'pass', seconds: (Date.now() - started) / 1000, ...numbers });
    } catch (error) {
      const status = error instanceof Blocked ? 'blocked' : 'fail';
      run.beats.push({ beat: number, title, status, seconds: (Date.now() - started) / 1000, error: error.message });
      await capture(`beat-${number}-${status}`, `${number}. ${title} — ${status.toUpperCase()}`, error.message).catch(() => {});
    }
    const result = run.beats.at(-1);
    console.log(`${name.padEnd(8)} ${number} ${result.status.toUpperCase().padEnd(7)} ${title}${result.error ? `: ${result.error.split('\n')[0]}` : ''}`);
    await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  }
  async function lookup(address, title) {
    await page.goto(`${BASE}/address`);
    await page.getByLabel('Listing link or address', { exact: true }).fill(address);
    await capture('address', title, 'Real Ann Arbor address · predicted heating + cooling only');
    const result = await action('/estimate', () => page.getByRole('button', { name: 'Next', exact: true }).click());
    // City-estimated unit sizes are retained; no made-up rental size is introduced.
    await Promise.race([
      page.getByRole('button', { name: 'Skip', exact: true }).waitFor({ state: 'visible' }),
      page.waitForURL('**/survey'),
    ]);
    if (await page.getByRole('button', { name: 'Skip', exact: true }).isVisible()) {
      await capture('public-record-area', title, 'Using the estimated public-record unit size; renter size was not supplied.');
      await page.getByRole('button', { name: 'Skip', exact: true }).click();
    }
    await page.waitForURL('**/survey');
    return result;
  }
  async function answer(name, title) {
    const button = page.getByRole('button', { name, exact: true });
    const result = await action('/answer', () => button.click());
    await page.getByRole('button', { name: 'Next', exact: true }).waitFor({ state: 'visible' });
    await page.waitForFunction(() => ![...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Next' && b.disabled));
    await capture('answer', title, 'Illustrative renter answer; equipment has not been independently verified.', button);
    return result;
  }
  async function grade(title) {
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await page.getByRole('link', { name: 'Skip for now', exact: true }).click();
    await page.waitForURL('**/grade');
    await page.getByText('Predicted score', { exact: true }).waitFor();
    await capture('grade', title, 'Predicted grade and annual range from the API, not a measured tenant bill.', page.getByText('Predicted score', { exact: true }));
  }
  async function restore(session) {
    await page.goto(`${BASE}/address`);
    await page.evaluate(session => {
      ['hr_user_id', 'hr_token', 'hr_property_id'].forEach(k => localStorage.removeItem(k));
      localStorage.setItem('hr_session_id', session);
    }, session);
  }
  async function board() {
    await page.goto(`${BASE}/board`);
    await page.getByRole('heading', { name: 'Same-type peers', exact: true }).waitFor();
    await page.getByRole('list', { name: 'Anonymized nearby ranks, annual cost at your unit size' }).waitFor();
  }

  try {
    await beat(1, 'Where do you live?', async () => {
      await lookup(MORTON, '1. Where do you live?');
      await answer('Gas', '1. Your home, your answers');
      morton = await answer('Single-pane', '1. Your home, your answers');
      await grade('1. Your predicted hidden rent');
      await page.getByRole('button', { name: 'Next', exact: true }).click();
      await page.waitForURL('**/board'); await board();
      const position = await request(`/leaderboard/position?session_id=${encodeURIComponent(morton.session_id)}`);
      await capture('rank', '1. Your place among same-type homes', 'Real city ranks. Bars scale peer costs to this estimated unit size.', page.getByRole('heading', { name: 'Same-type peers' }));
      return { address: MORTON, grade: morton.grade, grade_span: morton.grade_span, annual: morton.bill.annual, rank: position.current };
    });
    await beat(2, 'Listing battle', async () => {
      await page.goto(`${BASE}/compare`);
      await page.getByRole('region', { name: 'Listing A', exact: true }).getByLabel('Address or listing link').fill('624 Church St, Ann Arbor, MI');
      await page.getByRole('region', { name: 'Listing B', exact: true }).getByLabel('Address or listing link').fill('1022 S Forest Ave, Ann Arbor, MI');
      if (name === 'mobile') {
        for (const side of ['A', 'B']) await capture(`battle-input-${side.toLowerCase()}`, `2. Listing ${side}`, 'Public-record estimated size; not an independently verified rental listing.', page.getByRole('region', { name: `Listing ${side}`, exact: true }).getByLabel('Address or listing link'));
      } else await capture('battle-inputs', '2. Listing battle', 'Same building type; public-record size estimates, not verified rental listings.', page.getByRole('region', { name: 'Listing A', exact: true }).getByLabel('Address or listing link'));
      const result = await action('/compare', () => page.getByRole('button', { name: /Reveal the hidden difference/ }).click());
      const reveal = page.getByRole('heading', { name: /costs \$[\d,]+\/yr more to live in\./ });
      await reveal.waitFor();
      await page.getByText('★ Lower predicted bill', { exact: true }).waitFor();
      for (const side of ['A', 'B']) await capture(`battle-result-${side.toLowerCase()}`, `2. Listing ${side}: the predicted annual bill`, 'Predicted heating + cooling, with uncertainty. Winner compares total cost.', page.getByRole('region', { name: `Listing ${side}`, exact: true }).getByText(/estimated range$/));
      await capture('battle-results', '2. The hidden difference', 'Predicted heating + cooling only. Returned ranges and uncertainty stay visible.', reveal);
      return { winner: result.winner, diff_usd_yr: result.diff_usd_yr, confident: result.confident, annual_a: result.a.bill.annual, annual_b: result.b.bill.annual };
    });
    await beat(3, 'Lock in your grade', async () => {
      const before = await lookup(ARROW, '3. Lock in your grade');
      await capture('grade-before', '3. One useful question', 'Answer-driven grade uncertainty is separate from annual bill uncertainty.');
      arrow = await answer('Central AC', '3. Central AC — an illustrative renter answer');
      assert.equal(arrow.grade, 'B', 'Arrowwood no longer grades B; recheck the demo pick.');
      assert.equal(arrow.locked, true, 'Arrowwood did not lock after Central AC.');
      assert.equal(arrow.grade_span.length, 1, 'Arrowwood still spans multiple grades.');
      await grade('3. Grade locked: B 🔒');
      return { address: ARROW, before: before.grade_span, after: arrow.grade_span, annual: arrow.bill.annual };
    });
    await beat(4, 'Commitments', async () => {
      if (!morton) throw new Blocked('Needs the real Morton session from beat 1.');
      await restore(morton.session_id); await board();
      const chart = page.getByRole('list', { name: 'Anonymized nearby ranks, annual cost at your unit size' });
      const before = await chart.innerText();
      const background = await page.getByRole('main').getAttribute('style');
      const button = page.getByRole('button', { name: /window/i }).filter({ hasText: 'Projected if completed' });
      await button.waitFor();
      if (!await button.isEnabled()) throw new Blocked('Window upgrade is a pending-model tip; it cannot be projected.');
      await capture('commitments-options', '4. Choose a modeled improvement', 'Tips have no invented savings. This is a what-if, not completed work.', button);
      const projection = await action('/projection', () => button.click());
      assert.equal(projection.projected.label, 'projected_if_completed');
      await page.getByLabel(/^Projected if completed: score/).waitFor();
      assert.equal(await chart.innerText(), before, 'Current You/peer bars changed under a projection.');
      const afterBackground = await page.getByRole('main').getAttribute('style');
      assert.notEqual(afterBackground, background, 'Projected percentile did not move the background; check current model results.');
      await capture('ghost-marker', '4. Projected if completed', 'The ghost moves; the solid “You” bar and current grade do not.', chart);
      return { current_unchanged: true, projected: projection.projected, delta: projection.delta };
    });
    await beat(5, 'Monthly bill', async () => {
      if (!morton) throw new Blocked('Needs the real Morton session from beat 1.');
      // This setup runs in Node; the private agent key never reaches browser storage or screenshots.
      if (process.env.VIDEO_LOCAL_AUTH !== '1' || process.env.USE_MOCKS !== '1' || !process.env.AGENT_API_KEY)
        throw new Blocked('Early bill_signal requires a saved property: enable VIDEO_LOCAL_AUTH=1, USE_MOCKS=1 and AGENT_API_KEY against the isolated mock-auth API.');
      assert(['localhost', '127.0.0.1', '[::1]'].includes(new URL(API).hostname), 'Mock-auth setup is limited to a local isolated API.');
      const phone = name === 'desktop' ? '+12025550181' : '+12025550182'; // Reserved fictional 555-01xx numbers.
      const start = await request('/auth/web/start', { phone });
      assert(start.redirect_url.startsWith('sms:'), 'API auth is not in mock mode; stopped before confirming.');
      await request('/auth/web/confirm', { code: start.code, phone }, { 'X-Agent-Key': process.env.AGENT_API_KEY });
      const login = await request(`/auth/web/${encodeURIComponent(start.login_id)}`);
      assert(login.token && login.user_id, 'Mock-auth login did not return a bearer token.');
      const saved = await request('/properties', { user_id: login.user_id, session_id: morton.session_id }, { Authorization: `Bearer ${login.token}` });
      await restore(morton.session_id);
      await page.evaluate(({ user, property, token }) => {
        localStorage.setItem('hr_user_id', user); localStorage.setItem('hr_property_id', property); localStorage.setItem('hr_token', token);
      }, { user: login.user_id, property: saved.property_id, token: login.token });
      await board();
      const beforeBill = await request(`/leaderboard/position/${encodeURIComponent(saved.property_id)}`, undefined, { Authorization: `Bearer ${login.token}` });
      await page.getByRole('button', { name: 'No', exact: true }).click();
      const form = page.getByRole('region', { name: 'Monthly bill check', exact: true });
      await form.getByLabel('Gas usage (therms)', { exact: false }).fill('120');
      await form.getByLabel('Billing start', { exact: true }).fill('2026-02-01');
      await form.getByLabel('Billing end', { exact: true }).fill('2026-02-28');
      await capture('bill-input', '5. Check a monthly bill', 'Hypothetical example: 120 therms, February 2026. No actual tenant bill.', form.getByRole('button', { name: 'Check my bill' }));
      const result = await action('/calibrate', () => form.getByRole('button', { name: 'Check my bill', exact: true }).click());
      assert(Number.isFinite(result.pct_vs_expected_for_weather), 'Calibration has no weather comparison.');
      assert(result.bill_signal && result.snapshot?.provisional === true, 'API did not return the expected provisional bill signal; recheck this demo month.');
      const afterBill = await request(`/leaderboard/position/${encodeURIComponent(saved.property_id)}`, undefined, { Authorization: `Bearer ${login.token}` });
      assert.deepEqual(afterBill.current, beforeBill.current, 'Current grade/rank changed after the provisional bill signal.');
      assert.equal(result.verified, false, 'This scripted bill must not be presented as verified savings.');
      await form.getByText(/normal for this weather/).waitFor();
      await form.getByText(/Early signal, not verified savings/).waitFor();
      await capture('bill-result', '5. An early signal, not verified savings', 'One hypothetical bill; uncertainty remains and the current grade stays unchanged.', form.getByText(/normal for this weather/));
      return { therms: 120, start: '2026-02-01', end: '2026-02-28', pct_vs_expected_for_weather: result.pct_vs_expected_for_weather,
        noise_floor: result.noise_floor, verified: result.verified, current_unchanged: true, bill_signal: result.bill_signal, snapshot: result.snapshot };
    });
    await beat(6, 'City map', async () => {
      const yard = await request('/estimate', { address: YARD });
      assert(yard.score >= 98 && yard.grade === 'A', 'The Yard no longer meets the top-2% demo pick; recheck it.');
      await page.goto(`${BASE}/map?session=${encodeURIComponent(yard.session_id)}`);
      const map = page.getByRole('img', { name: /Map of Ann Arbor showing/ });
      await map.waitFor();
      await page.getByLabel('City predicted grades', { exact: true }).waitFor();
      await page.waitForFunction(() => Number(document.querySelector('[role="img"][data-city-count]')?.getAttribute('data-city-count')) > 30000);
      const cityCount = Number(await map.getAttribute('data-city-count'));
      assert.equal(Number(await map.getAttribute('data-building-id')), 50892, 'Wrong footprint highlighted for The Yard.');
      await page.getByRole('button', { name: 'Building', exact: true }).click();
      await capture('map-building', '6. Your home in the city', 'The Yard · top 2% by predicted cost per square foot; allocated public-meter model.', map);
      await page.getByRole('button', { name: 'Ann Arbor', exact: true }).click();
      await delay(record ? 3000 : 500);
      await capture('map-city', '6. From one home to Ann Arbor', 'Citywide predicted grades. Unscored buildings remain gray; no invented look-alikes.', map);
      return { address: YARD, score: yard.score, grade: yard.grade, building_id: 50892, city_footprints: cityCount };
    });
  } finally {
    const video = page.video(); await context.close();
    if (record && video) {
      const raw = await video.path();
      const complete = run.beats.length === 6 && run.beats.every(b => b.status === 'pass');
      const output = path.join(out, `${complete ? 'backup' : 'INCOMPLETE'}-${name}.webm`);
      await fs.rename(raw, output); run.video = path.basename(output);
      const ffmpeg = spawnSync('ffmpeg', ['-y', '-i', output, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output.replace(/\.webm$/, '.mp4')], { stdio: 'ignore' });
      if (ffmpeg.status === 0) run.mp4 = path.basename(output.replace(/\.webm$/, '.mp4'));
      else run.conversion = ffmpeg.error?.code === 'ENOENT' ? 'ffmpeg not installed; WebM retained' : 'ffmpeg conversion failed; WebM retained';
    }
  }
}

(async () => {
  await fs.mkdir(out, { recursive: true });
  console.log(`${record ? 'RECORDING' : 'DRY RUN (screenshots only)'} ${BASE} → ${API}`);
  const browser = await chromium.launch({ headless: process.env.HEADED !== '1', args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  try { for (const viewport of viewports) await runViewport(browser, viewport); }
  finally { await browser.close(); report.finished_at = new Date().toISOString(); await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2)); }
  console.log(`Evidence: ${out}`);
  if (report.runs.some(r => r.beats.length !== 6 || r.beats.some(b => b.status !== 'pass'))) process.exitCode = 1;
})().catch(error => { console.error(error.message); process.exitCode = 1; });
