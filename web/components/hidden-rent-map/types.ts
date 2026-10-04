import type { MultiPolygon, Polygon } from "geojson";

/** Properties of each feature in `buildings_url`. */
export interface CityBuildingProps {
  id: number;
  /** LiDAR above-ground height, ft (0 if unknown). */
  h: number;
  /** 1 if the city marks the footprint Residential. */
  r: 0 | 1;
  /** Most common mailing address inside the footprint, if any. */
  a?: string;
  score?: number;
  grade?: string;
  excess_usd_per_sqft?: number;
  type?: string;
}

export interface SimilarBuilding {
  id: number;
  address: string;
  /** [lon, lat] */
  center: [number, number];
  height_ft: number | null;
  stories: number | null;
  footprint_sqft: number;
}

export type Season = "winter" | "spring" | "summer" | "fall";

/** What the map camera frames: all of Ann Arbor, the selected + similar buildings, the census block group, or the building. */
export type Focus = "city" | "similar" | "block" | "building";

export interface StepEstimate {
  /** Model's typical-year heating + cooling cost for the unit, $/yr. */
  annual_usd: number;
  seasons: Record<Season, number>;
  heating_fuel: "gas" | "electric";
  /** Median absolute error on held-out real Ann Arbor buildings (0.299 = ±30%). */
  typical_error: number;
  method: string;
}

export interface LookalikeCloud {
  /** Simulated homes still matching the unit after this step's answers. */
  count: number;
  /** Sorted sample of those homes' heating + cooling $/yr, priced at this address. */
  usd_yr: number[];
  p10: number | null;
  p50: number | null;
  p90: number | null;
}

export interface SurveyStep {
  /** "public_record" for the starting point, else the question id. */
  id: string;
  question: string | null;
  answer_label: string | null;
  estimate: StepEstimate;
  lookalikes: LookalikeCloud;
}

export interface MapWidgetData {
  address: string;
  /** [lon, lat] */
  center: [number, number];
  /** [west, south, east, north] of every Ann Arbor footprint. */
  city_bounds: [number, number, number, number];
  building: {
    /** City footprint OBJECTID; the same `id` as in the citywide layer. */
    id: number;
    footprint: Polygon | MultiPolygon;
    height_ft: number | null;
    height_source: string;
    stories: number | null;
    stories_source: string;
    footprint_sqft: number;
    floor_area_sqft: number;
    floor_area_source: string;
    unit_sqft: number;
    unit_sqft_source: string;
    building_type: string;
    building_type_source: string;
  };
  /** Every Ann Arbor footprint (`CityBuildingProps`), loaded by the map at runtime; too large to inline. */
  buildings_url: string;
  /** Buildings to show relative to the selected one (a ranking later; a labelled test sample for now). */
  similar: { rule: string; items: SimilarBuilding[] };
  block_group: {
    geoid: string;
    geometry: Polygon | MultiPolygon;
    median_year_built: number | null;
    median_year_built_source: string;
    gas_heat_share: number | null;
    electric_heat_share: number | null;
    heating_fuel_source: string;
  };
  lookalikes: { pool_size: number; rule: string };
  /** steps[0] is public record only; each later step adds one survey answer. */
  steps: SurveyStep[];
  accuracy_basis: string;
  sources: { label: string; url: string }[];
}
