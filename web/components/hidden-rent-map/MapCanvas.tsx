"use client";

import { useEffect, useRef, useState } from "react";
import type { ExpressionSpecification, FilterSpecification, IControl, LngLatBoundsLike, Map as MLMap, Marker, Popup } from "maplibre-gl";
import type { FeatureCollection, Geometry, Position } from "geojson";
import "maplibre-gl/dist/maplibre-gl.css";
import { GRADE_COLORS } from "./grade-colors";
import styles from "./hidden-rent-map.module.css";
import type { CityBuildingProps, Focus, MapWidgetData } from "./types";

const STYLE_URL = "https://tiles.openfreemap.org/styles/positron";
// Satellite/aerial basemap for the "Satellite" view; our grade layers draw on top of it.
const SATELLITE_TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const SATELLITE_ATTRIBUTION = 'Imagery <a href="https://www.esri.com">Esri</a>, Maxar, Earthstar Geographics, USDA, USGS';
const FT_TO_M = 0.3048;
const BLUE = "#173bfa";
const INK = "#11121a";
const HOVER = "#ffb000";

const OTHER = "#bdbab0";

interface Props {
  data: MapWidgetData;
  focus: Focus;
  homeColor: string;
  /** Building id to highlight (from outside the map, or the map's own hover). */
  highlightId: number | null;
  /** Glide the camera to the highlighted building (when the highlight comes from outside the map, e.g. a peer bar). */
  followHighlight?: boolean;
  onHoverBuilding: (id: number | null) => void;
  reducedMotion: boolean;
}

function positions(g: Geometry): Position[] {
  if (g.type === "Polygon") return g.coordinates.flat();
  if (g.type === "MultiPolygon") return g.coordinates.flat(2);
  return [];
}

function boundsOf(ps: Position[]): LngLatBoundsLike {
  const xs = ps.map((p) => p[0]);
  const ys = ps.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

function centroid(g: Geometry): [number, number] {
  const ps = positions(g);
  return [ps.reduce((s, p) => s + p[0], 0) / ps.length, ps.reduce((s, p) => s + p[1], 0) / ps.length];
}

const hovered: ExpressionSpecification = ["boolean", ["feature-state", "hover"], false];
const gradeColor: ExpressionSpecification = ["match", ["get", "grade"], "A", GRADE_COLORS.A, "B", GRADE_COLORS.B, "C", GRADE_COLORS.C, "D", GRADE_COLORS.D, "F", GRADE_COLORS.F, OTHER];

/** A MapLibre control: a row of buttons where one is selected (first by default) and `pick` runs on change. */
function buttonGroup<T extends string>(options: readonly (readonly [T, string])[], pick: (value: T) => void): IControl {
  const group = document.createElement("div");
  group.className = "maplibregl-ctrl maplibregl-ctrl-group";
  group.style.display = "flex";
  options.forEach(([value, label], i) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    Object.assign(button.style, { width: "auto", padding: "0 10px", fontWeight: i === 0 ? "700" : "400" });
    button.setAttribute("aria-pressed", String(i === 0));
    button.onclick = () => {
      pick(value);
      for (const b of group.querySelectorAll("button")) {
        b.setAttribute("aria-pressed", String(b === button));
        b.style.fontWeight = b === button ? "700" : "400";
      }
    };
    group.appendChild(button);
  });
  return { onAdd: () => group, onRemove: () => group.remove() };
}

export function MapCanvas({ data, focus, homeColor, highlightId, followHighlight = false, onHoverBuilding, reducedMotion }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MLMap | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const markers = useRef<{ pin?: Marker; height?: Marker; block?: Marker }>({});
  const onHoverRef = useRef(onHoverBuilding);
  onHoverRef.current = onHoverBuilding;
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState<string | null>(null);
  const [cityCount, setCityCount] = useState<number | null>(null);
  const cityRef = useRef<FeatureCollection<Geometry, CityBuildingProps> | null>(null);

  useEffect(() => {
    let cancelled = false;
    let map: MLMap | null = null;
    (async () => {
      let city: FeatureCollection<Geometry, CityBuildingProps>;
      try {
        const response = await fetch(data.buildings_url);
        if (!response.ok) throw new Error();
        city = await response.json();
        if (!Array.isArray(city.features)) throw new Error();
      } catch {
        if (!cancelled) setFailed("The city footprint layer is unavailable. Reload to try again; your estimate is still shown below.");
        return;
      }
      const maplibregl = (await import("maplibre-gl")).default;
      if (cancelled || !container.current) return;
      setCityCount(city.features.length);
      cityRef.current = city;
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
        setFailed("The map needs WebGL, which this browser has turned off.");
        return;
      }
      mapRef.current = map;
      popupRef.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false, className: styles.popup });
      map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");

      map.on("load", () => {
        if (!map) return;
        for (const layer of map.getStyle().layers ?? []) {
          if ("source-layer" in layer && layer["source-layer"] === "building") {
            map.setLayoutProperty(layer.id, "visibility", "none");
          }
        }
        const sel = data.building.id;
        const simIds = data.similar.items.map((s) => s.id);

        // Added first so it sits above the street basemap but under every Hidden Rent layer.
        map.addSource("satellite", { type: "raster", tiles: [SATELLITE_TILES], tileSize: 256, maxzoom: 19, attribution: SATELLITE_ATTRIBUTION });
        map.addLayer({ id: "satellite", type: "raster", source: "satellite", layout: { visibility: "none" } });
        map.addControl(buttonGroup([["map", "Map"], ["satellite", "Satellite"]], (view) =>
          map?.setLayoutProperty("satellite", "visibility", view === "satellite" ? "visible" : "none")), "top-right");

        map.addSource("block-group", {
          type: "geojson",
          data: { type: "Feature", geometry: data.block_group.geometry, properties: {} },
        });
        map.addLayer({
          id: "block-group-fill",
          type: "fill",
          source: "block-group",
          paint: { "fill-color": BLUE, "fill-opacity": 0.1 },
        });
        map.addLayer({
          id: "block-group-line",
          type: "line",
          source: "block-group",
          paint: { "line-color": BLUE, "line-width": 2, "line-dasharray": [2, 1.5], "line-opacity": 0.8 },
        });

        map.addSource("city", { type: "geojson", data: city, promoteId: "id" });
        map.addLayer({
          id: "city-3d",
          type: "fill-extrusion",
          source: "city",
          filter: ["!=", ["get", "id"], sel],
          paint: {
            "fill-extrusion-color": ["case", hovered, HOVER, gradeColor],
            "fill-extrusion-height": ["*", ["get", "h"], FT_TO_M],
            "fill-extrusion-opacity": 0.92,
          },
        });
        // Neighbors: every building (graded + gray unscored), only graded ones, or just this home.
        const others: FilterSpecification = ["!=", ["get", "id"], sel];
        map.addControl(buttonGroup([["all", "All homes"], ["graded", "Graded only"], ["mine", "Just mine"]], (show) => {
          map?.setLayoutProperty("city-3d", "visibility", show === "mine" ? "none" : "visible");
          map?.setFilter("city-3d", show === "graded" ? ["all", others, ["in", ["get", "grade"], ["literal", ["A", "B", "C", "D", "F"]]]] : others);
        }), "top-right");

        map.addSource("home", {
          type: "geojson",
          data: { type: "Feature", geometry: data.building.footprint, properties: { id: sel, h: data.building.height_ft ?? 0, grade: city.features.find((f) => f.properties.id === sel)?.properties.grade ?? "" } },
        });
        map.addLayer({
          id: "home-3d",
          type: "fill-extrusion",
          source: "home",
          paint: {
            "fill-extrusion-color": gradeColor,
            "fill-extrusion-color-transition": { duration: 700 },
            "fill-extrusion-height": ["*", ["get", "h"], FT_TO_M],
            "fill-extrusion-opacity": 1,
          },
        });

        map.addLayer({ id: "home-outline", type: "line", source: "home", paint: { "line-color": BLUE, "line-width": 4 } });

        map.addSource("similar-links", {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: data.similar.items.map((s) => ({
              type: "Feature",
              id: s.id,
              geometry: { type: "LineString", coordinates: [data.center, s.center] },
              properties: {},
            })),
          },
        });
        map.addLayer({
          id: "similar-links",
          type: "line",
          source: "similar-links",
          paint: {
            "line-color": ["case", hovered, HOVER, INK],
            "line-width": ["case", hovered, 2.5, 1],
            "line-dasharray": [3, 2],
            "line-opacity": ["case", hovered, 1, 0.45],
          },
        });
        map.addSource("similar-dots", {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: data.similar.items.map((s) => ({
              type: "Feature",
              id: s.id,
              geometry: { type: "Point", coordinates: s.center },
              properties: { id: s.id, a: s.address },
            })),
          },
        });
        map.addLayer({
          id: "similar-dots",
          type: "circle",
          source: "similar-dots",
          paint: {
            "circle-color": ["case", hovered, HOVER, INK],
            "circle-radius": ["case", hovered, 8, 5],
            "circle-stroke-color": "#fff",
            "circle-stroke-width": 2,
            "circle-opacity": ["interpolate", ["linear"], ["zoom"], 15, 1, 16.5, 0],
            "circle-stroke-opacity": ["interpolate", ["linear"], ["zoom"], 15, 1, 16.5, 0],
          },
        });
        for (const id of simIds) map.setFeatureState({ source: "city", id }, { similar: true });

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

        const hoverLayers = ["similar-dots", "city-3d"];
        let last: number | null = null;
        const report = (id: number | null) => {
          if (id === last) return;
          last = id;
          onHoverRef.current(id);
        };
        map.on("mousemove", (e) => {
          if (!map) return;
          const f = map.queryRenderedFeatures(e.point, { layers: hoverLayers })[0];
          const id = f ? Number((f.properties as CityBuildingProps).id) : null;
          map.getCanvas().style.cursor = id != null ? "pointer" : "";
          report(id);
        });
        map.on("mouseout", () => report(null));
        setReady(true);
      });
    })();
    return () => {
      cancelled = true;
      markers.current = {};
      popupRef.current?.remove();
      map?.remove();
      mapRef.current = null;
      setReady(false);
    };
    // homeColor and highlightId are applied by their own effects; depending on them here would rebuild the map.
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
    } else if (focus === "similar") {
      const pts = [data.center, ...data.similar.items.map((s) => s.center)];
      map.fitBounds(boundsOf(pts), { padding: 70, pitch: 45, bearing: -15, duration });
    } else if (focus === "block") {
      map.fitBounds(boundsOf(positions(data.block_group.geometry)), { padding: 48, pitch: 35, bearing: -10, duration });
    } else {
      map.easeTo({ center: data.center, zoom: 17.4, pitch: 60, bearing: -28, duration });
    }
  }, [focus, ready, data, reducedMotion]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    const pin = markers.current.pin?.getElement();
    if (pin) pin.style.background = homeColor;
  }, [homeColor, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || highlightId == null) return;
    const isSimilar = data.similar.items.find((s) => s.id === highlightId);
    const sources = ["city", ...(isSimilar ? ["similar-dots", "similar-links"] : [])];
    for (const source of sources) map.setFeatureState({ source, id: highlightId }, { hover: true });
    const feature = isSimilar
      ? { center: isSimilar.center, address: isSimilar.address }
      : (() => {
          // Off-screen buildings aren't in the rendered tiles, so fall back to the loaded city layer.
          const f = map.querySourceFeatures("city", { filter: ["==", ["get", "id"], highlightId] })[0]
            ?? cityRef.current?.features.find((c) => c.properties.id === highlightId);
          const p = f?.properties as CityBuildingProps | undefined;
          return f ? { center: centroid(f.geometry), address: p?.a ?? "" } : null;
        })();
    if (feature && followHighlight) map.easeTo({ center: feature.center, zoom: Math.max(map.getZoom(), 16), duration: 600 });
    if (feature?.address) popupRef.current?.setLngLat(feature.center).setText(feature.address).addTo(map);
    return () => {
      for (const source of sources) map.setFeatureState({ source, id: highlightId }, { hover: false });
      popupRef.current?.remove();
    };
  }, [highlightId, followHighlight, ready, data]);

  if (failed) {
    return <div role="alert" className={styles.mapFallback}>{failed}</div>;
  }
  return <div ref={container} data-building-id={data.building.id} data-city-count={cityCount ?? undefined} className={styles.map} role="img" aria-label={`Map of Ann Arbor showing ${data.address}`} />;
}
