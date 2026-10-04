"use client";

import { useEffect, useRef, useState } from "react";
import type { LngLatBoundsLike, Map as MLMap, Marker } from "maplibre-gl";
import type { Geometry, Position } from "geojson";
import "maplibre-gl/dist/maplibre-gl.css";
import styles from "./hidden-rent-map.module.css";
import type { Focus, MapWidgetData } from "./types";

const STYLE_URL = "https://tiles.openfreemap.org/styles/positron";
const FT_TO_M = 0.3048;
const BLUE = "#173bfa";

interface Props {
  data: MapWidgetData;
  focus: Focus;
  homeColor: string;
  reducedMotion: boolean;
}

function positions(g: Geometry): Position[] {
  if (g.type === "Polygon") return g.coordinates.flat();
  if (g.type === "MultiPolygon") return g.coordinates.flat(2);
  return [];
}

function bounds(g: Geometry): LngLatBoundsLike {
  const ps = positions(g);
  const xs = ps.map((p) => p[0]);
  const ys = ps.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

function centroid(g: Geometry): [number, number] {
  const ps = positions(g);
  return [ps.reduce((s, p) => s + p[0], 0) / ps.length, ps.reduce((s, p) => s + p[1], 0) / ps.length];
}

export function MapCanvas({ data, focus, homeColor, reducedMotion }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MLMap | null>(null);
  const markers = useRef<{ pin?: Marker; height?: Marker; block?: Marker }>({});
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let map: MLMap | null = null;
    (async () => {
      const maplibregl = (await import("maplibre-gl")).default;
      if (cancelled || !container.current) return;
      try {
        map = new maplibregl.Map({
          container: container.current,
          style: STYLE_URL,
          bounds: data.city_bounds,
          fitBoundsOptions: { padding: 24 },
          cooperativeGestures: true,
          attributionControl: { compact: true },
        });
      } catch {
        setFailed(true);
        return;
      }
      mapRef.current = map;
      map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
      map.on("load", () => {
        if (!map) return;
        for (const layer of map.getStyle().layers ?? []) {
          if ("source-layer" in layer && layer["source-layer"] === "building") {
            map.setLayoutProperty(layer.id, "visibility", "none");
          }
        }
        map.addSource("block-group", {
          type: "geojson",
          data: { type: "Feature", geometry: data.block_group.geometry, properties: {} },
        });
        map.addLayer({
          id: "block-group-fill",
          type: "fill",
          source: "block-group",
          paint: { "fill-color": BLUE, "fill-opacity": 0.12 },
        });
        map.addLayer({
          id: "block-group-line",
          type: "line",
          source: "block-group",
          paint: { "line-color": BLUE, "line-width": 2, "line-dasharray": [2, 1.5], "line-opacity": 0.9 },
        });
        map.addSource("neighbors", { type: "geojson", data: data.neighbors });
        map.addLayer({
          id: "neighbors-3d",
          type: "fill-extrusion",
          source: "neighbors",
          minzoom: 14,
          paint: {
            "fill-extrusion-color": "#d8d5cb",
            "fill-extrusion-height": ["*", ["get", "height_ft"], FT_TO_M],
            "fill-extrusion-opacity": 0.9,
          },
        });
        map.addSource("home", {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: data.building.footprint,
            properties: { height_ft: data.building.height_ft ?? 0 },
          },
        });
        map.addLayer({
          id: "home-3d",
          type: "fill-extrusion",
          source: "home",
          minzoom: 14,
          paint: {
            "fill-extrusion-color": homeColor,
            "fill-extrusion-color-transition": { duration: 700 },
            "fill-extrusion-height": ["*", ["get", "height_ft"], FT_TO_M],
            "fill-extrusion-opacity": 0.95,
          },
        });

        const pin = document.createElement("div");
        pin.className = styles.pin;
        pin.style.background = homeColor;
        markers.current.pin = new maplibregl.Marker({ element: pin }).setLngLat(data.center).addTo(map);

        if (data.building.height_ft != null) {
          const el = document.createElement("div");
          el.className = styles.mapTag;
          el.textContent = `${data.building.height_ft.toFixed(1)} ft`;
          markers.current.height = new maplibregl.Marker({ element: el, anchor: "bottom", offset: [0, -12] })
            .setLngLat(centroid(data.building.footprint))
            .addTo(map);
        }
        if (data.block_group.median_year_built != null) {
          const el = document.createElement("div");
          el.className = `${styles.mapTag} ${styles.mapTagBlue}`;
          el.textContent = `built ~${data.block_group.median_year_built}`;
          markers.current.block = new maplibregl.Marker({ element: el, anchor: "center" })
            .setLngLat(centroid(data.block_group.geometry))
            .addTo(map);
        }
        setReady(true);
      });
    })();
    return () => {
      cancelled = true;
      markers.current = {};
      map?.remove();
      mapRef.current = null;
      setReady(false);
    };
    // homeColor is applied by its own effect; depending on it here would rebuild the map on every answer.
  }, [data]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const duration = reducedMotion ? 0 : 1800;
    markers.current.pin?.getElement().classList.toggle(styles.hidden, focus === "building");
    markers.current.height?.getElement().classList.toggle(styles.hidden, focus !== "building");
    markers.current.block?.getElement().classList.toggle(styles.hidden, focus !== "block");
    if (focus === "city") {
      map.fitBounds(data.city_bounds, { padding: 24, pitch: 0, bearing: 0, duration });
    } else if (focus === "block") {
      map.fitBounds(bounds(data.block_group.geometry), { padding: 48, pitch: 35, bearing: -10, duration });
    } else {
      map.easeTo({ center: data.center, zoom: 17.4, pitch: 60, bearing: -28, duration });
    }
  }, [focus, ready, data, reducedMotion]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    map.setPaintProperty("home-3d", "fill-extrusion-color", homeColor);
    const pin = markers.current.pin?.getElement();
    if (pin) pin.style.background = homeColor;
  }, [homeColor, ready]);

  if (failed) {
    return <div className={styles.mapFallback}>The map needs WebGL, which this browser has turned off.</div>;
  }
  return <div ref={container} className={styles.map} role="img" aria-label={`Map of Ann Arbor showing ${data.address}`} />;
}
