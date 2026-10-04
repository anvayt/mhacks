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
