import { Suspense } from "react";
import SharePage from "./share-page";
export default function Page() { return <Suspense fallback={<p>Loading your share card…</p>}><SharePage /></Suspense>; }
