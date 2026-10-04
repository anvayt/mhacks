import type { MapWidgetData } from "./types";
import demo from "@/mocks/map/912-mary-st.json";

/**
 * The single switch between mock data and the backend. Mocks are on unless NEXT_PUBLIC_USE_MOCKS=0.
 * The backend endpoint is a proposal (notes/contract-changes.md); it must return `MapWidgetData`.
 */
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== "0";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const demoMapData = demo as unknown as MapWidgetData;

export async function getMapWidgetData(sessionId: string, init?: RequestInit): Promise<MapWidgetData> {
  if (USE_MOCKS) return demoMapData;
  const res = await fetch(`${API_BASE_URL}/map/${encodeURIComponent(sessionId)}`, init);
  if (!res.ok) throw new Error(`map data request failed: ${res.status}`);
  return (await res.json()) as MapWidgetData;
}
