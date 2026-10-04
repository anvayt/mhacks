// Photon management API (https://spectrum.photon.codes/openapi/json).
// Free/Pro shared lines only text numbers registered as project users,
// so judges get allowlisted here before they text the agent.

const API = "https://spectrum.photon.codes";

/** The text a new user's Messages app opens with. Text only: links in a first message trip Apple's junk filter. */
export const OPENER = "Hi Hidden Rent! What's my apartment's hidden rent?";

export interface PhotonCreds {
  projectId: string;
  projectSecret: string;
}

export interface SharedUser {
  id: string;
  phoneNumber: string;
}

/** Normalize a typed phone number to E.164, assuming US (+1) for 10-digit input. Returns null if it can't. */
export function normalizePhone(input: string): string | null {
  const trimmed = input.trim();
  const digits = trimmed.replace(/\D/g, "");
  if (trimmed.startsWith("+")) return /^[1-9]\d{6,14}$/.test(digits) ? `+${digits}` : null;
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
  return null;
}

export class PhotonError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

/** POST /projects/{id}/users with type "shared". Idempotent per phone number on Photon's side. */
export async function createSharedUser(
  creds: PhotonCreds,
  phoneNumber: string,
  firstName?: string,
  fetchImpl: typeof fetch = fetch,
): Promise<SharedUser> {
  const auth = Buffer.from(`${creds.projectId}:${creds.projectSecret}`).toString("base64");
  const res = await fetchImpl(`${API}/projects/${creds.projectId}/users/`, {
    method: "POST",
    headers: { Authorization: `Basic ${auth}`, "Content-Type": "application/json" },
    body: JSON.stringify({ type: "shared", phoneNumber, ...(firstName ? { firstName } : {}) }),
  });
  const body = (await res.json().catch(() => null)) as { succeed?: boolean; data?: SharedUser } | null;
  if (!res.ok || !body?.succeed || !body.data) {
    throw new PhotonError(`Photon create user failed (${res.status}): ${JSON.stringify(body)}`, res.status);
  }
  return { id: body.data.id, phoneNumber: body.data.phoneNumber };
}

/** Public Photon endpoint that 302s into Messages (SMS deep link) with the opener pre-filled. */
export function redirectUrl(userId: string, msg = OPENER): string {
  return `${API}/users/${encodeURIComponent(userId)}/redirect?msg=${encodeURIComponent(msg)}`;
}
