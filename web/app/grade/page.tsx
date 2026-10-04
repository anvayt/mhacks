"use client";

import { useRouter } from "next/navigation";
import { RankingScreen } from "../ranking-screen";

export default function GradePage() {
  const router = useRouter();

  return <RankingScreen onNext={() => router.push("/board")} />;
}
