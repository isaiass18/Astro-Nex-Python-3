export interface BirthData {
  birth: string; // ISO-8601 local date time, e.g. "1990-06-15T14:30:00"
  timezone: string; // IANA timezone, e.g. "America/Bogota"
  latitude: number;
  longitude: number;
  firstName?: string;
  lastName?: string;
  city?: string;
  region?: string;
  country?: string;
}

export interface ChartCalculationOptions {
  operation?: string; // e.g. "draw_nat"
}

export interface PlanetPosition {
  index: number;
  name: string;
  longitude: number;
  sign: string;
  degree: number;
}

export interface Aspect {
  p1: number;
  p2: number;
  name: string;
  angle: number;
  orb: number;
  goodwill: boolean;
}

export interface ChartDetailsResult {
  planets: PlanetPosition[];
  aspects: Aspect[];
}

export interface AstroNexEngine {
  /**
   * Initializes the engine, allocating WASM and Ephemeris resources.
   */
  initialize(): Promise<void>;

  /**
   * Calculates chart details equivalent to the Python API /v1/charts/details endpoint.
   */
  calculateChartDetails(
    birthData: BirthData,
    options?: ChartCalculationOptions
  ): Promise<ChartDetailsResult>;
}
