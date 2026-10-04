import { Suspense } from "react";
import WatchPage from "./watch-page";
export default function Page() { return <Suspense fallback={<p>Loading your report…</p>}><WatchPage /></Suspense>; }
