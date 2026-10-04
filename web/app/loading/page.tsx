"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LoadingSheet } from "../survey-fields";

const NEXT_SCREENS = new Set(["/address", "/survey", "/grade", "/board"]);

function LoadingStep() {
  const router = useRouter();
  const params = useSearchParams();
  const requested = params.get("next") ?? "/address";
  const next = NEXT_SCREENS.has(requested) ? requested : "/address";

  return (
    <main className="dim-screen">
      <LoadingSheet onFinished={() => router.push(next)} />
    </main>
  );
}

export default function LoadingPage() {
  return (
    <Suspense fallback={null}>
      <LoadingStep />
    </Suspense>
  );
}
