"use client";

import { useRouter } from "next/navigation";
import { SurveyFields } from "./survey-fields";

// Sign-in is offered right before the grade, always with "Skip for now" (team decision 2).
const TO_GRADE = `/signin?next=${encodeURIComponent("/loading?next=/grade")}`;

export function SurveyGate() {
  const router = useRouter();

  return <SurveyFields onNext={() => router.push(TO_GRADE)} />;
}
