"use client";

import { useRouter } from "next/navigation";
import { SurveyFields } from "./survey-fields";

export function SurveyGate() {
  const router = useRouter();

  return <SurveyFields onNext={() => router.push("/loading?next=/grade")} />;
}
