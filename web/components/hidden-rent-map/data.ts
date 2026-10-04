import type { MapWidgetData } from "./types";
import { API, ApiError } from "@/app/lib/api";
import demo from "@/mocks/map/912-mary-st.json";

// Mock fixtures are opt-in; a failed API call never falls back to invented data.
export const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "1";
export const demoMapData = demo as unknown as MapWidgetData;

export async function getMapWidgetData(sessionId: string, init?: RequestInit): Promise<MapWidgetData> {
  if (USE_MOCKS) return demoMapData;
  let res: Response;
  try { res = await fetch(`${API}/map/${encodeURIComponent(sessionId)}`, init); }
  catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new ApiError(0, "unreachable", "The Hidden Rent API isn't reachable right now.");
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, body?.detail?.code ?? "error", body?.detail?.message ?? "The map could not be loaded. Try again.");
  // The current API still advertises P3's static path; /city is the scored live layer.
  return { ...body, buildings_url: `${API}/city` } as MapWidgetData;
}
