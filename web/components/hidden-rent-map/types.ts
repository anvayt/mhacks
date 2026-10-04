import type { FeatureCollection, MultiPolygon, Polygon } from "geojson";

export type Season = "winter" | "spring" | "summer" | "fall";

export type Chapter = "building" | "block" | "answers";

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
  p10: number;
  p50: number;
  p90: number;
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
  building: {
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
  /** Nearby footprints, each with `height_ft`, for 3D context. */
  neighbors: FeatureCollection<Polygon | MultiPolygon, { height_ft: number }>;
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
