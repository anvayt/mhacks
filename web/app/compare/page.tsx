import { Suspense } from "react";
import ComparePage from "./compare-page";
export default function Page() { return <Suspense fallback={<p>Loading listing battle…</p>}><ComparePage /></Suspense>; }
