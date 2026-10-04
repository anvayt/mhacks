import { Suspense } from "react";
import MapPage from "./map-page";
export default function Page() { return <Suspense fallback={<p>Loading your map…</p>}><MapPage /></Suspense>; }
