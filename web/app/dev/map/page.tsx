import { HiddenRentMap, demoMapData, type Chapter } from "@/components/hidden-rent-map";

export const metadata = { title: "Map widget preview · Hidden Rent" };

const CHAPTERS: Chapter[] = ["building", "block", "answers"];

export default async function MapPreviewPage({
  searchParams,
}: {
  searchParams: Promise<{ chapter?: string; step?: string }>;
}) {
  const q = await searchParams;
  const chapter = CHAPTERS.find((c) => c === q.chapter) ?? "building";
  const step = Number(q.step ?? 0) || 0;
  return (
    <main style={{ minHeight: "100vh", padding: 24, background: "#f4f2eb" }}>
      <div style={{ maxWidth: 1240, margin: "0 auto", height: "min(820px, calc(100vh - 48px))", display: "grid" }}>
        <HiddenRentMap key={`${chapter}-${step}`} data={demoMapData} defaultChapter={chapter} defaultStep={step} />
      </div>
    </main>
  );
}
