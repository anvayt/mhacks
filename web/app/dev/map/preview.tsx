"use client";

import { useState } from "react";
import { HiddenRentMap, MapStory, demoMapData, type Focus } from "@/components/hidden-rent-map";

export function MapPreview({ initialFocus, initialStep }: { initialFocus: Focus; initialStep: number }) {
  const [focus, setFocus] = useState<Focus>(initialFocus);
  const [step, setStep] = useState(initialStep);
  return (
    <>
      <HiddenRentMap
        data={demoMapData}
        step={step}
        focus={focus}
        onFocusChange={setFocus}
        className="map-preview-widget"
      />
      <MapStory data={demoMapData} step={step} onStepChange={setStep} onFocus={setFocus} />
    </>
  );
}
