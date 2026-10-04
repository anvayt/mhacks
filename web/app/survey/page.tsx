import type { Metadata } from "next";
import { SurveyFields } from "../survey-fields";

export const metadata: Metadata = {
  title: "Hidden Rent survey",
  description: "Answer the numeric questions that narrow a rental's energy estimate.",
};

export default function SurveyPage() {
  return <SurveyFields />;
}
