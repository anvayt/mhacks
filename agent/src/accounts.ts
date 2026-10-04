import type { Account, Api, ApiResult } from "./api.ts";
import { normalizePhone } from "./photon.ts";

export interface Sender { handle: string; photonUserId?: string }
export const accountHandle = (handle: string) => handle.includes("@") ? handle.trim().toLowerCase() : normalizePhone(handle) ?? handle.trim();

/** Concurrent first messages share one request. A fresh web ref must still reach /auth/phone. */
export class Accounts {
  private cache = new Map<string, Promise<ApiResult<Account>>>();
  private refs = new Map<string, string>();
  constructor(private api: Api) {}
  resolve(sender: Sender, sessionId?: string): Promise<ApiResult<Account>> {
    const phone = accountHandle(sender.handle);
    const cached = this.cache.get(phone);
    if (cached && (!sessionId || this.refs.get(phone) === sessionId)) return cached;
    const request = this.api.authPhone({ phone, ...(sender.photonUserId ? { photon_user_id: sender.photonUserId } : {}), ...(sessionId ? { session_id: sessionId } : {}) });
    this.cache.set(phone, request);
    if (sessionId) this.refs.set(phone, sessionId);
    void request.then((r) => { if (!r.ok && this.cache.get(phone) === request) { this.cache.delete(phone); this.refs.delete(phone); } });
    return request;
  }
}
