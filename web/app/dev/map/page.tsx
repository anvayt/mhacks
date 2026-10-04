import type { Focus } from "@/components/hidden-rent-map";
import { MapPreview } from "./preview";

export const metadata = { title: "Map widget preview (demo fixture) · Hidden Rent" };

const FOCI: Focus[] = ["city", "block", "building"];

export default async function MapPreviewPage({
  searchParams,
}: {
  searchParams: Promise<{ focus?: string; step?: string }>;
}) {
  const q = await searchParams;
  const focus = FOCI.find((f) => f === q.focus) ?? "city";
  const step = Number(q.step ?? 0) || 0;
  return (
    <main style={{ minHeight: "100vh", padding: 24, background: "#f4f2eb" }}>
      <style>{`.map-preview-widget { height: min(680px, calc(100vh - 48px)); }`}</style>
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <p style={{ margin: "0 0 12px", fontFamily: "var(--font-mono)", fontSize: 12, textTransform: "uppercase" }}>
          Demo fixture · recorded sample data, not a live estimate
        </p>
        <MapPreview key={`${focus}-${step}`} initialFocus={focus} initialStep={step} />
      </div>
    </main>
  );
}
