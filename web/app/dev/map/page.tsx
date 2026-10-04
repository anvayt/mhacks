import type { Focus } from "@/components/hidden-rent-map";
import { MapPreview } from "./preview";

export const metadata = { title: "Map widget preview · Hidden Rent" };

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
        <MapPreview key={`${focus}-${step}`} initialFocus={focus} initialStep={step} />
      </div>
    </main>
  );
}
