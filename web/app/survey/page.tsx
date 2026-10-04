import type { Metadata } from "next";
import { SurveyGate } from "../survey-gate";

export const metadata: Metadata = {
  title: "Hidden Rent survey",
  description: "Answer the questions that narrow a rental's energy estimate.",
};

export default function SurveyPage() {
  return <SurveyGate />;
}
