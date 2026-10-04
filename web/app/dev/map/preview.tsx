"use client";

import { useState } from "react";
import { HiddenRentMap, MapStory, demoMapData, type Focus } from "@/components/hidden-rent-map";

const data = demoMapData;

export function MapPreview({ initialFocus, initialStep }: { initialFocus: Focus; initialStep: number }) {
  const [focus, setFocus] = useState<Focus>(initialFocus);
  const [step, setStep] = useState(initialStep);
  const [hoverId, setHoverId] = useState<number | null>(null);
  const [listHover, setListHover] = useState<number | null>(null);

  return (
    <>
      <HiddenRentMap
        data={data}
        step={step}
        focus={focus}
        onFocusChange={setFocus}
        highlightId={listHover}
        onHoverBuilding={setHoverId}
        className="map-preview-widget"
      />

      <section style={{ margin: "20px 0 0", fontSize: 13, color: "#11121a" }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 12, fontFamily: "var(--font-mono)", textTransform: "uppercase" }}>
          Similar homes (highlight test)
        </h3>
        <p style={{ margin: "0 0 8px", color: "#656570", fontSize: 12 }}>{data.similar.rule}</p>
        <ul style={{ display: "flex", flexWrap: "wrap", gap: 6, margin: 0, padding: 0, listStyle: "none" }}>
          {[{ id: data.building.id, address: `${data.address.split(",")[0]} (selected)` }, ...data.similar.items].map(
            (s) => {
              const on = listHover === s.id || hoverId === s.id;
              return (
                <li
                  key={s.id}
                  tabIndex={0}
                  onMouseEnter={() => setListHover(s.id)}
                  onMouseLeave={() => setListHover(null)}
                  onFocus={() => setListHover(s.id)}
                  onBlur={() => setListHover(null)}
                  style={{
                    padding: "5px 9px",
                    border: "1px solid #11121a",
                    background: on ? "#ffb000" : "#fff",
                    cursor: "default",
                  }}
                >
                  {s.address}
                </li>
              );
            },
          )}
        </ul>
      </section>

      <MapStory data={data} step={step} onStepChange={setStep} onFocus={setFocus} />
    </>
  );
}
