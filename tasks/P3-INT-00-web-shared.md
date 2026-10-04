# Web integration: wiring P3's finished design to the real API (shared rules)

P3's screens are finished (dev `be97437`) but run on illustrative data. Three agents wire them to P2's API **without changing the design**. P3 reviews the result.
Read this file, then PLAN.md §5/§10, NEW_CHANGES.md §6 and §9.2 (projection wording), `notes/contract-changes.md` (every endpoint and field) and `api/README.md` on `origin/dev`.

| Slice | Owner | Branch | Files you own | Web dev port |
|---|---|---|---|---|
| W1 flow: address → survey → phone sign-in → grade | Claude | `p3/int-flow` | `listing-form.tsx`, `survey-fields.tsx`, `survey-gate.tsx`, `survey/`, `address/`, `ranking-screen.tsx`, `grade/`, `game-flow.tsx`, `sign-in-button.tsx`, `signin/`, `auth/callback/`, `loading/` | 3001 |
| W2 leaderboard: rank + ghost marker, commitments, change address, monthly bill | Astra | `p3/int-board` | `leaderboard.tsx`, `board/`, `mocks/` (delete what you replace) | 3002 |
| W3 map, listing battle, share card | Astra | `p3/int-map-compare` | `components/hidden-rent-map/` (merge `origin/p3/map-widget`), new `compare/` and `share/` routes and their components | 3003 |

## Team decisions (Oct 4, ~3:10 AM)
1. **Keep P3's design.** Reuse its components, class names and copy. Only replace mock or illustrative data with API data. Remove an "illustrative / mock" label only where real data now fills that spot. New styles go in a CSS module next to your component; don't edit `globals.css` (three branches would conflict).
2. **Phone number = login** (`POST /auth/web/start` → show "Text `login 123456` to Hidden Rent" + open `redirect_url` → poll `GET /auth/web/{login_id}` → keep the bearer token). This replaces the generic OAuth button. **Signing in is offered right before the grade (the sketch), with a "Skip for now" link.** Photon's free tier allowlists only ~10 numbers, so the demo must never depend on a judge signing in. Without a token, everything works on the session: `?session_id=` variants of suggested, projection and position.
3. **Monthly bill box: both.** "Gas used this month (therms or ccf, on your DTE bill)" is the exact path. A "$ amount" toggle is labelled "estimated from your bill amount" (`amount_usd`). There's also an optional bill photo (`bill_image_base64`, JPEG). Electricity kWh is optional and only stored, never compared.
4. **"Heat is included in my rent"** is an answer option for `heating_fuel` (`value: "included"`). The grade still rates the building; the renter's heating $ shows 0 and hidden rent counts cooling only. Show the API's `bill.note`.
5. **Honesty (PLAN.md §0, §5):** every number comes from an API response. Projected figures say "projected if completed" (the `label` field). Show ranges when the grade isn't locked ("B–C"). Label scores "predicted". Placeholder commitments (`pending_model: true`) are tips with no numbers. Leaderboard entries flagged `demo: true` say "demo data".

## API features that land on `dev` with merge wave 6 (P2), for the web
- `POST /answer` heating_fuel option `included`, plus `bill.note`.
- `POST /calibrate` accepts `amount_usd` (+ start/end) when therms aren't given, and `gas_unit: "ccf" | "therms"`.
- `POST /properties {user_id, session_id}` adopts the session you already answered (no re-estimate).
- Anonymous, by session: `GET /commitments/suggested?session_id=`, `POST /projection {session_id, commitment_ids: [catalog ids]}` (what-if only, not stored), `GET /leaderboard/position?session_id=` (current only, no ghost marker unless a projection is passed).
Until wave 6 lands, code against these shapes and test against the property-based versions or recorded responses.

## Rules
- Branch off `origin/dev`; push your branch. Never merge into `dev` or push to `main`. Never edit `/api`, `/model` or `/agent`; ask the lead for API changes.
- Run the API from your worktree: `cd api && uv sync && MODEL_BASE_URL=http://localhost:8001 WEB_ORIGINS=http://localhost:<your web port> SESSIONS_DB=/tmp/<you>-s.sqlite APP_DB=/tmp/<you>-a.sqlite uv run uvicorn app.main:app --port <8030|8031|8032>`. P1's model on :8001: never start, stop or rebuild it. Run the web with `NEXT_PUBLIC_API_BASE_URL=http://localhost:<api port> npm run dev -- -p <web port>`. Never use :3000 or :8000.
- `cd web && npm run build` must pass (type-check + build). Check the demo addresses in `demo/addresses.txt` in a real browser (Playwright or the browser tool), including loading and error states (`needs_address` shows its hint; `not_a_home`; API down).
- Accessibility basics: buttons stay buttons, labels stay on inputs, there's an `aria-live` for results, and it works at 375 px wide.
- Final report: branch + head commit, each screen → endpoint, screenshots or a description per demo address, anything still mocked, and anything you need from the API.

## Shared file `web/app/lib/api.ts`
Create it with exactly this text if it's missing (identical on every branch, so the merge is clean). Put your own typed calls next to your components, not in this file.

```ts
// Shared /api client for the web (P3 integration). Identical on every integration branch: don't edit; add typed calls next to your components.
export const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly hint?: string,
  ) {
    super(message);
  }
}

const KEYS = { session: "hr_session_id", property: "hr_property_id", user: "hr_user_id", token: "hr_token" } as const;
export type StoredKey = keyof typeof KEYS;

export function load(key: StoredKey): string | null {
  try {
    return localStorage.getItem(KEYS[key]);
  } catch {
    return null;
  }
}

export function save(key: StoredKey, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(KEYS[key]);
    else localStorage.setItem(KEYS[key], value);
  } catch {
    // private mode / blocked storage: the flow still works for this page view
  }
}

export async function apiFetch<T>(path: string, init: { method?: string; body?: unknown } = {}): Promise<T> {
  const token = load("token");
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, {
      method: init.method ?? (init.body === undefined ? "GET" : "POST"),
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: init.body === undefined ? undefined : JSON.stringify(init.body),
    });
  } catch {
    throw new ApiError(0, "unreachable", "The Hidden Rent API isn't reachable right now.");
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const d = data?.detail ?? {};
    throw new ApiError(res.status, d.code ?? "error", d.message ?? "Something went wrong. Try again.", d.hint);
  }
  return data as T;
}
```

Stored state: `session` = the current `/estimate` session_id, `property`/`user`/`token` after sign-in. Navigation between W1's grade screen and W2's board relies only on these keys.
