"use client";

import { useState } from "react";
import { Leaderboard } from "./leaderboard";
import { ListingForm } from "./listing-form";
import { RankingScreen } from "./ranking-screen";
import { LoadingSheet, SurveyFields } from "./survey-fields";

type Stage = "start" | "toAddress" | "address" | "survey" | "toGrade" | "grade" | "board";

export function GameFlow() {
  const [stage, setStage] = useState<Stage>("start");

  if (stage === "start") {
    return (
      <main className="start-screen">
        <button className="start-photo" type="button" onClick={() => setStage("toAddress")}>
          <img src="/hero/house.png" alt="" />
          <span className="start-photo-label">Start</span>
        </button>
      </main>
    );
  }

  if (stage === "toAddress") {
    return <LoadingSheet onFinished={() => setStage("address")} />;
  }

  if (stage === "address") {
    return (
      <main className="survey-screen">
        <ListingForm onPicked={() => setStage("survey")} submitLabel="Next" />
      </main>
    );
  }

  if (stage === "survey" || stage === "toGrade") {
    return (
      <>
        <SurveyFields leaving={stage === "toGrade"} onNext={() => setStage("toGrade")} />
        {stage === "toGrade" ? <LoadingSheet onFinished={() => setStage("grade")} /> : null}
      </>
    );
  }

  if (stage === "grade") return <RankingScreen onNext={() => setStage("board")} />;
  return <Leaderboard />;
}
