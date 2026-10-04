"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { HiddenRentMap, getMapWidgetData, type Focus, type MapWidgetData } from "@/components/hidden-rent-map";

/** The city map under the grade, so the result shows where the home sits without another click. */
export function GradeMap({ session }: { session: string }) {
  const [data, setData] = useState<MapWidgetData | null>(null);
  const [focus, setFocus] = useState<Focus>("building");
  useEffect(() => {
    const abort = new AbortController();
    getMapWidgetData(session, { signal: abort.signal }).then(setData).catch(() => {}); // ponytail: no map on failure; the grade stands alone
    return () => abort.abort();
  }, [session]);
  if (!data) return null;
  return (
    <section className="score-reveal score-reveal-late" aria-label="This home on the Ann Arbor map" style={{ marginTop: 24, alignSelf: "stretch", width: "100%" }}>
      <HiddenRentMap data={data} step={data.steps.length - 1} focus={focus} onFocusChange={setFocus} />
      <p className="ranking-source">
        Every Ann Arbor building, colored by its predicted grade. Switch to Satellite or hide neighbors in the corner.{" "}
        <Link href={`/map?session=${encodeURIComponent(session)}`}>Open the full city map ↗</Link>
      </p>
    </section>
  );
}
