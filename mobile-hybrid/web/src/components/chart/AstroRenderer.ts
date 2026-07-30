/**
 * Canvas/TypeScript port of the Radix drawing logic used by the original
 * PyCairo renderer (coredraw.py, roundedcharts.py and aspects.py).
 *
 * Coordinate rule:
 *   screenAngle = (180 + ascendant) - zodiacDegree
 *
 * All public data stays in real zodiac longitude (0..360). Rotation is applied
 * only by AstroRenderer.polar(), so callers never have to pre-rotate values.
 */

export type RGB = readonly [number, number, number];
export type RGBA = readonly [number, number, number, number];

export interface Point {
  x: number;
  y: number;
}

export type CanvasPathCommand =
  | { op: "M"; x: number; y: number }
  | { op: "L"; x: number; y: number }
  | { op: "C"; cp1x: number; cp1y: number; cp2x: number; cp2y: number; x: number; y: number }
  | { op: "Q"; cpx: number; cpy: number; x: number; y: number }
  | { op: "Z" };

export interface PathGlyph {
  kind: "path";
  /** Commands in the glyph's own coordinate system. */
  commands: readonly CanvasPathCommand[];
  /** Original bounds, used to center and scale the path. */
  bounds: { x: number; y: number; width: number; height: number };
}

export interface SvgPathGlyph {
  kind: "svg-path";
  /** SVG path-data accepted by new Path2D(pathData). */
  path: string;
  viewBox: { x: number; y: number; width: number; height: number };
}

export interface TextGlyph {
  kind: "text";
  text: string;
  fontFamily?: string;
  fontWeight?: string | number;
}

export type Glyph = PathGlyph | SvgPathGlyph | TextGlyph;

export interface PlanetDatum {
  id: string;
  longitude: number;
  sourceLongitude?: number;
  color: RGB;
  glyph: Glyph;
  /** Index used by the original aspect-orb table. Defaults to planet order. */
  classIndex?: number;
}

export interface ZodiacDatum {
  id: string;
  longitude: number;
  color: RGB;
  glyph: Glyph;
}

export interface AspectDatum {
  /** Planet index or resolved longitude, depending on the consuming method. */
  p1: number;
  p2: number;
  /** 0..11 aspect sector in the original twelve-aspect system. */
  a?: number;
  /** Orb ratio relative to body 1. */
  f1: number;
  /** Orb ratio relative to body 2. */
  f2: number;
  /** Optional override for aspect colors */
  color?: RGB;
  /** True if this is a goodwill (wider orb) aspect */
  gw?: boolean;
}

export interface RadixData {
  /** Ecliptic longitude of the ascendant. Usually houses[0]. */
  ascendant: number;
  /** Twelve unequal house cusps, in zodiac longitude. */
  houses: readonly number[];
  planets: readonly PlanetDatum[];
  /** Optional zodiac glyphs. Longitudes should normally be 15, 45, ... 345. */
  zodiac?: readonly ZodiacDatum[];
  /** Optional already-resolved aspects. If omitted, AspectEngine may calculate them. */
  aspects?: readonly AspectDatum[];
  /** Whether p1/p2 in `aspects` are planet indexes or zodiac degrees. Defaults to indices. */
  aspectCoordinates?: "indices" | "degrees";
  /** Optional chart date, used only by year labels/custom extensions. */
  date?: string;
}

export interface AspectEngineConfig {
  /** 5 planet classes x 5 aspect classes, injected in the original application. */
  orbs: readonly (readonly number[])[];
  /** Planet class per planet index. Original: [0,0,1,1,2,1,2,3,3,3,4]. */
  planetClasses?: readonly number[];
  /** Aspect sector -> orb class. Original: [4,0,1,2,3,1,4,1,3,2,1,0]. */
  aspectClasses?: readonly number[];
  /** Color for each of the twelve aspect sectors. */
  colors: readonly RGB[];
}

export interface RendererPalette {
  background: string;
  foreground: RGB;
  ruler: RGB;
  cross: RGB;
  houseZoneBase: RGB;
  houseZones: readonly RGB[];
  cuspColors: readonly RGB[];
  goldenLow: RGB;
  goldenInverse: RGB;
}

export interface RendererOptions {
  pixelRatio?: number;
  fontFamily?: string;
  baselineLineWidth?: number;
  palette?: Partial<RendererPalette>;
  showHouseZones?: boolean;
  showRulers?: boolean;
  showSignBoundaries?: boolean;
  showCusps?: boolean;
  showGoldenPoints?: boolean;
  showPlanetLines?: boolean;
  showAspects?: boolean;
  showInnerCircles?: boolean;
  showHouseTrimming?: boolean;
  aspectMode?: "auto" | "fusus" | "unilateral";
  aspectEngine?: AspectEngine;
}

interface PlanetPlot {
  sourceIndex: number;
  /** Longitude adjusted so polar() reproduces the old +corr screen rotation. */
  longitude: number;
  sourceLongitude: number;
  radialFactor: number;
  correction: number;
}

const TAU = Math.PI * 2;
const RAD = Math.PI / 180;
const PHI = 1 / ((1 + Math.sqrt(5)) / 2);

const DEFAULT_PALETTE: RendererPalette = {
  background: "#ffffff",
  foreground: [0, 0, 0],
  ruler: [0, 0, 0],
  cross: [0.9, 0, 0.9],
  houseZoneBase: [0.4, 0.4, 0.9],
  houseZones: [
    [0.87, 0.21, 0.21],
    [0.97, 0.94, 0.51],
    [0.72, 0.72, 0.9],
    [0.34, 0.77, 0.41],
    [0.96, 0.8, 0.32],
    [0.83, 0.5, 0.51],
    [0.87, 0.21, 0.21],
  ],
  cuspColors: [
    [0.8, 0, 0],
    [0, 0, 0.6],
    [0, 0.5, 0],
  ],
  goldenLow: [0.95, 0.65, 0.05],
  goldenInverse: [0.55, 0.35, 0.75],
};

const CUSP_NAMES = ["AC", "2", "3", "IC", "5", "6", "DC", "8", "9", "MC", "11", "12"] as const;

export function normalizeDegree(value: number): number {
  return ((value % 360) + 360) % 360;
}

export function forwardDifference(low: number, high: number): number {
  return normalizeDegree(high - low);
}

export function rgb(color: RGB): string {
  const channel = (value: number): number => Math.round(Math.max(0, Math.min(1, value)) * 255);
  return `rgb(${channel(color[0])} ${channel(color[1])} ${channel(color[2])})`;
}

export function rgba(color: RGB | RGBA, alpha?: number): string {
  const a = alpha ?? (color.length === 4 ? color[3] : 1);
  const channel = (value: number): number => Math.round(Math.max(0, Math.min(1, value)) * 255);
  return `rgba(${channel(color[0])}, ${channel(color[1])}, ${channel(color[2])}, ${Math.max(0, Math.min(1, a))})`;
}

/**
 * Equivalent of coredraw.rebuild_paths(), using Canvas camelCase methods.
 */
export function replayPath(ctx: CanvasRenderingContext2D, commands: readonly CanvasPathCommand[]): void {
  for (const command of commands) {
    switch (command.op) {
      case "M":
        ctx.moveTo(command.x, command.y);
        break;
      case "L":
        ctx.lineTo(command.x, command.y);
        break;
      case "C":
        ctx.bezierCurveTo(command.cp1x, command.cp1y, command.cp2x, command.cp2y, command.x, command.y);
        break;
      case "Q":
        ctx.quadraticCurveTo(command.cpx, command.cpy, command.x, command.y);
        break;
      case "Z":
        ctx.closePath();
        break;
      default: {
        const exhaustive: never = command as never;
        throw new Error(`Unsupported path command: ${String(exhaustive)}`);
      }
    }
  }
}

/** Port of roundedcharts.Basic_Chart logic required by a Radix chart. */
export class RadixLayout {
  static readonly R_INNER = 0.48;
  static readonly R_RULED_INNER = 0.65;
  static readonly R_RULED_OUTER = 0.78;
  static readonly R_RULED_MID = 0.84;
  static readonly R_LINE_INSET = 0.2;
  static readonly R_PLANET = RadixLayout.R_INNER + (RadixLayout.R_RULED_INNER - RadixLayout.R_INNER) / 2;
  static readonly PLAN_FACTORS = [0.93, 1.07] as const;

  readonly data: RadixData;

  constructor(data: RadixData) {
    this.data = data;
    if (data.houses.length !== 12) {
      throw new Error(`A Radix chart requires exactly 12 house cusps; received ${data.houses.length}.`);
    }
  }

  get ascendant(): number {
    return normalizeDegree(this.data.ascendant);
  }

  get sizes(): number[] {
    return this.data.houses.map((house, index) =>
      forwardDifference(house, this.data.houses[(index + 1) % this.data.houses.length]),
    );
  }

  get offset(): number {
    return this.ascendant % 30;
  }

  get ascendantSign(): number {
    return Math.floor(this.ascendant / 30);
  }

  get signCusps(): number[] {
    return Array.from({ length: 12 }, (_, index) => index * 30);
  }

  get goldenPoints(): Array<{ house: number; low: number; inverse: number }> {
    return this.data.houses.map((house, index) => ({
      house,
      low: this.sizes[index] * PHI,
      inverse: this.sizes[index] * (1 - PHI),
    }));
  }

  sortPlanets(): Array<{ degree: number; index: number }> {
    return this.data.planets
      .map((planet, index) => ({ degree: normalizeDegree(planet.longitude), index }))
      .sort((a, b) => a.degree - b.degree);
  }

  /** Equivalent of Basic_Chart.joinsort(). */
  joinSort(cell: readonly { degree: number; index: number }[]): Array<{ degree: number; index: number }> {
    const witness = [...cell].sort((a, b) => a.degree - b.degree);
    if (witness.length < 2) return witness;

    let split = 0;
    for (let index = 0; index < witness.length; index += 1) {
      const gap = forwardDifference(witness[index].degree, witness[(index + 1) % witness.length].degree);
      if (gap > 6.5) {
        split = index + 1;
        break;
      }
    }
    return witness.slice(split).concat(witness.slice(0, split));
  }

  /** Equivalent of Basic_Chart.marshall_planets(). */
  marshallPlanets(): Array<Array<{ degree: number; index: number }>> {
    const planets = this.sortPlanets();
    if (planets.length === 0) return [];

    const closeToNext = planets.map((planet, index) => {
      const next = planets[(index + 1) % planets.length];
      return forwardDifference(planet.degree, next.degree) <= 6.5;
    });

    if (closeToNext.some(Boolean)) {
      let guard = 0;
      while ((!closeToNext[0] || closeToNext[closeToNext.length - 1]) && guard < closeToNext.length * 2) {
        closeToNext.push(closeToNext.shift() as boolean);
        planets.push(planets.shift() as { degree: number; index: number });
        guard += 1;
      }
    }

    const groups: Array<Array<{ degree: number; index: number }>> = [];
    let current: Array<{ degree: number; index: number }> = [];
    planets.forEach((planet, index) => {
      current.push(planet);
      if (!closeToNext[index]) {
        groups.push(current);
        current = [];
      }
    });
    if (current.length > 0) groups.push(current);
    return groups;
  }

  /**
   * Equivalent of inject_plan_degrees(). The old renderer added correction to
   * the already transformed screen angle. Because this port keeps zodiac
   * longitudes untransformed, the correction is subtracted from longitude.
   */
  injectPlanetDegrees(): PlanetPlot[] {
    const output = new Array<PlanetPlot>(this.data.planets.length);

    for (const group of this.marshallPlanets()) {
      const count = group.length;
      const factors = [...RadixLayout.PLAN_FACTORS];
      const witness = this.joinSort(group);

      witness.forEach((planet, position) => {
        let radialFactor = count < 2 ? 1 : factors[0];
        if (count >= 2) factors.reverse();

        let correction = 0;
        if (count >= 3) {
          const faraway = position - Math.floor(count / 2);
          let difference = 0;
          if (faraway < 0) {
            difference = forwardDifference(planet.degree, witness[position + 1].degree);
          } else if (faraway > 0) {
            difference = forwardDifference(witness[position - 1].degree, planet.degree);
            if (difference >= 353.5) {
              difference = -(difference - 353.5);
              radialFactor = factors[0];
            }
          }
          correction = (-faraway * (6.5 - difference)) / 2.5;
        }

        output[planet.index] = {
          sourceIndex: planet.index,
          sourceLongitude: planet.degree,
          longitude: normalizeDegree(planet.degree - correction),
          radialFactor,
          correction,
        };
      });
    }

    return output;
  }
}

/** Port of aspects.py::FususAspect. */
export class FususAspect {
  draw(
    ctx: CanvasRenderingContext2D,
    radius: number,
    aspects: readonly AspectDatum[],
    polar: (radius: number, degree: number) => Point,
  ): void {
    ctx.save();
    const scale = radius * 0.00065;

    for (const aspect of aspects) {
      const f = 3 * ((5 - 5 * aspect.f1) + (5 - 5 * aspect.f2)) * scale;
      const p1 = polar(radius, aspect.p1);
      const p2 = polar(radius, aspect.p2);
      const midpoint = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };

      // Same thickened-center polygon intent as the original atan-based code,
      // but using a stable perpendicular vector for vertical lines as well.
      const vx = p2.x - p1.x;
      const vy = p2.y - p1.y;
      const length = Math.hypot(vx, vy) || 1;
      const dx = (-vy / length) * f;
      const dy = (vx / length) * f;

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.bezierCurveTo(midpoint.x + dx, midpoint.y + dy, midpoint.x + dx, midpoint.y + dy, p2.x, p2.y);
      ctx.bezierCurveTo(midpoint.x - dx, midpoint.y - dy, midpoint.x - dx, midpoint.y - dy, p1.x, p1.y);
      ctx.closePath();
      ctx.fillStyle = rgb(aspect.color || [0,0,0]);
      ctx.strokeStyle = rgb(aspect.color || [0,0,0]);
      ctx.fill(); // Canvas keeps the current path: equivalent to Cairo fill_preserve().
      ctx.lineWidth = 0.425;
      ctx.stroke();
    }
    ctx.restore();
  }
}


/** Port of aspects.py::ConjunctioAspect. */
export class ConjunctioAspect {
  draw(
    ctx: CanvasRenderingContext2D,
    radius: number,
    aspects: readonly AspectDatum[],
    zodiacToScreenAngle: (degree: number) => number,
    screenPolar: (radius: number, screenDegree: number) => Point,
    filter = false,
    extend?: number,
  ): void {
    const ex = extend ?? 1.105;
    const divisionFactor = extend ? 20 : 10;

    ctx.save();
    for (const aspect of aspects) {
      const p1Degree = normalizeDegree(zodiacToScreenAngle(aspect.p1));
      const p2Degree = normalizeDegree(zodiacToScreenAngle(aspect.p2));
      const f1 = aspect.f1 > 1 ? ex * 0.99 : 1 + aspect.f1 / divisionFactor;
      const f2 = aspect.f2 > 1 ? ex * 0.99 : 1 + aspect.f2 / divisionFactor;

      const p1Scaled = screenPolar(radius * f1, p1Degree);
      const p2Scaled = screenPolar(radius * f2, p2Degree);
      const center = screenPolar(0, 0); // Get origin (centerX, centerY)

      let distance = Math.abs(p1Degree - p2Degree);
      distance = Math.min(distance, 360 - distance);
      let deltaAngle = distance === 0 || filter
        ? 3
        : (((distance / aspect.f1 + distance / aspect.f2) / 2) - distance) / 2;
      deltaAngle = Math.abs(deltaAngle);

      let a1 = normalizeDegree(Math.min(p1Degree, p2Degree) - deltaAngle);
      let a2 = normalizeDegree(Math.max(p1Degree, p2Degree) + deltaAngle);
      if (Math.min(p1Degree, p2Degree) !== p1Degree) [a1, a2] = [a2, a1];

      const outer1 = screenPolar(radius * ex, a1);
      
      ctx.beginPath();
      ctx.fillStyle = rgb([1, 0.3, 0]);
      ctx.moveTo(p1Scaled.x, p1Scaled.y);
      ctx.lineTo(outer1.x, outer1.y);
      const positiveArc = (a1 < a2 && a2 - a1 < 180) || a1 - a2 > 180;
      ctx.arc(center.x, center.y, radius * ex, a1 * RAD, a2 * RAD, !positiveArc);
      ctx.lineTo(p2Scaled.x, p2Scaled.y);
      ctx.closePath();
      ctx.fill();

      ctx.beginPath();
      ctx.fillStyle = rgb(aspect.color || [0,0,0]);
      ctx.moveTo(p1Scaled.x, p1Scaled.y);
      const p1Ex = screenPolar(radius * ex, p1Degree);
      const p2Ex = screenPolar(radius * ex, p2Degree);
      ctx.lineTo(p1Ex.x, p1Ex.y);
      ctx.lineTo(p2Ex.x, p2Ex.y);
      ctx.lineTo(p2Scaled.x, p2Scaled.y);
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }
}

/** Port of aspects.py::UnilateralAspect. */
export class UnilateralAspect {
  private readonly baseline: number;
  constructor(baseline: number) {
    this.baseline = baseline;
  }

  draw(
    ctx: CanvasRenderingContext2D,
    radius: number,
    aspects: readonly AspectDatum[],
    polar: (radius: number, degree: number) => Point,
  ): void {
    ctx.save();
    ctx.lineWidth = 0.6 * this.baseline;

    for (const aspect of aspects) {
      let p1 = polar(radius, aspect.p1);
      let p2 = polar(radius, aspect.p2);
      if (aspect.f1 < aspect.f2) [p1, p2] = [p2, p1];

      const midpoint = { x: (p2.x + p1.x) / 2, y: (p2.y + p1.y) / 2 };
      ctx.strokeStyle = rgb(aspect.color || [0,0,0]);

      ctx.setLineDash([4, 3, 12, 4, 18, 5, 24, 6, 30, 6, 36, 6, 48, 6, 60, 6]);
      ctx.lineDashOffset = 0;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(midpoint.x, midpoint.y);
      ctx.stroke();

      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(midpoint.x, midpoint.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }
    ctx.restore();
  }
}

export class GoodwillAspect {
  private readonly baseline: number;
  constructor(baseline: number) {
    this.baseline = baseline;
  }

  draw(
    ctx: CanvasRenderingContext2D,
    radius: number,
    aspects: readonly AspectDatum[],
    polar: (radius: number, degree: number) => Point,
  ): void {
    ctx.save();
    ctx.setLineDash([12, 6]);
    ctx.lineDashOffset = 2;
    ctx.lineWidth = 0.7 * this.baseline;
    for (const aspect of aspects) {
      const p1 = polar(radius, aspect.p1);
      const p2 = polar(radius, aspect.p2);
      ctx.strokeStyle = rgb(aspect.color || [0,0,0]);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }
    ctx.restore();
  }
}

export class AgePointAspect {
  draw(
    ctx: CanvasRenderingContext2D,
    radius: number,
    aspects: readonly (AspectDatum & { f: number })[],
    agePointDegree: number,
    polar: (radius: number, degree: number) => Point,
  ): void {
    ctx.save();
    ctx.setLineDash([3, 3]);
    ctx.lineDashOffset = 2;
    for (const aspect of aspects) {
      const p1 = polar(radius, aspect.p1);
      const p2 = polar(radius, agePointDegree);
      ctx.lineWidth = Math.max(0.3, 1.2 - aspect.f);
      ctx.strokeStyle = rgb(aspect.color || [0,0,0]);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }
    ctx.restore();
  }
}

/**
 * Port of SimpleAspectManager.twelve_aspects(). It returns raw planet indices;
 * resolveAspects() converts them to zodiac longitudes for the Canvas drawers.
 */
export class AspectEngine {
  readonly planetClasses: readonly number[];
  readonly aspectClasses: readonly number[];

  readonly config: AspectEngineConfig;

  constructor(config: AspectEngineConfig) {
    this.config = config;
    this.planetClasses = config.planetClasses ?? [0, 0, 1, 1, 2, 1, 2, 3, 3, 3, 4];
    this.aspectClasses = config.aspectClasses ?? [4, 0, 1, 2, 3, 1, 4, 1, 3, 2, 1, 0];
  }

  twelveAspects(planets: readonly PlanetDatum[]): AspectDatum[] {
    const result: AspectDatum[] = [];

    for (let i = 0; i < planets.length; i += 1) {
      for (let j = i + 1; j < planets.length; j += 1) {
        const distance = Math.abs(normalizeDegree(planets[i].longitude) - normalizeDegree(planets[j].longitude));
        let sector = Math.floor(distance / 30);
        let orb = distance % 30;
        if (orb > 20) {
          sector += 1;
          orb = 30 - orb;
        }
        sector %= 12;

        const class1 = planets[i].classIndex ?? this.planetClasses[i] ?? 0;
        const class2 = planets[j].classIndex ?? (j !== 10 ? this.planetClasses[j] : class1) ?? 0;
        const aspectClass = this.aspectClasses[sector];
        const orb1 = this.config.orbs[class1]?.[aspectClass];
        const orb2 = this.config.orbs[class2]?.[aspectClass];
        if (!(orb1 > 0) || !(orb2 > 0)) continue;

        if (orb <= orb1 * 1.1 || orb <= orb2 * 1.1) {
          result.push({
            p1: i,
            p2: j,
            a: sector,
            f1: orb / orb1,
            f2: orb / orb2,
            color: this.config.colors[sector] ?? [0, 0, 0],
          });
        }
      }
    }
    return result;
  }

  resolveAspects(planets: readonly PlanetDatum[], aspects = this.twelveAspects(planets)): AspectDatum[] {
    return aspects.map((aspect) => ({
      ...aspect,
      p1: planets[aspect.p1]?.longitude ?? aspect.p1,
      p2: planets[aspect.p2]?.longitude ?? aspect.p2,
      color: aspect.color ?? this.config.colors[aspect.a ?? 0] ?? [0, 0, 0],
    }));
  }
}

export class AstroRenderer {
  readonly ctx: CanvasRenderingContext2D;
  private data: RadixData | null = null;
  private layout: RadixLayout | null = null;
  private centerX = 0;
  private centerY = 0;
  private radius = 0;
  private readonly options: Required<Omit<RendererOptions, "palette" | "aspectEngine">> & {
    palette: RendererPalette;
    aspectEngine?: AspectEngine;
  };
  private readonly fusus = new FususAspect();
  private readonly conjunctio = new ConjunctioAspect();
  private unilateral: UnilateralAspect;

  readonly canvas: HTMLCanvasElement;

  constructor(canvas: HTMLCanvasElement, options: RendererOptions = {}) {
    this.canvas = canvas;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("CanvasRenderingContext2D is unavailable.");
    this.ctx = ctx;

    const pixelRatio = options.pixelRatio ?? (typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1);
    const baselineLineWidth = options.baselineLineWidth ?? 1;
    this.options = {
      pixelRatio,
      fontFamily: options.fontFamily ?? "Arial, sans-serif",
      baselineLineWidth,
      palette: { ...DEFAULT_PALETTE, ...options.palette },
      showHouseZones: options.showHouseZones ?? true,
      showRulers: options.showRulers ?? true,
      showSignBoundaries: options.showSignBoundaries ?? true,
      showCusps: options.showCusps ?? true,
      showGoldenPoints: options.showGoldenPoints ?? true,
      showPlanetLines: options.showPlanetLines ?? true,
      showAspects: options.showAspects ?? true,
      showInnerCircles: options.showInnerCircles ?? true,
      showHouseTrimming: options.showHouseTrimming ?? false,
      aspectMode: options.aspectMode ?? "auto",
      aspectEngine: options.aspectEngine,
    };
    this.unilateral = new UnilateralAspect(baselineLineWidth);
  }

  /**
   * Required astrological projection. Canvas Y grows down, therefore:
   *   theta = ((180 + ascendant) - degree) * PI / 180
   */
  public polar(radius: number, degree: number): Point {
    if (!this.data) throw new Error("polar() requires active chart data; call render() first.");
    const angle = ((180 + this.data.ascendant) - degree) * RAD;
    return { x: this.centerX + radius * Math.cos(angle), y: this.centerY + radius * Math.sin(angle) };
  }

  private screenAngle(degree: number): number {
    if (!this.data) throw new Error("screenAngle() requires active chart data.");
    return normalizeDegree((180 + this.data.ascendant) - degree);
  }

  private screenPolar(radius: number, screenDegree: number): Point {
    const angle = screenDegree * RAD;
    return { x: this.centerX + radius * Math.cos(angle), y: this.centerY + radius * Math.sin(angle) };
  }

  render(data: RadixData): void {
    this.data = this.validateData(data);
    this.layout = new RadixLayout(this.data);
    this.prepareCanvas();

    const ctx = this.ctx;
    ctx.save();
    // ctx.translate(this.centerX, this.centerY); // Removed because polar now adds centerX/Y directly
    ctx.lineWidth = this.options.baselineLineWidth;
    ctx.lineCap = "butt";
    ctx.lineJoin = "round";

    if (this.options.showHouseZones) this.drawHouseZones();
    if (this.options.showHouseTrimming) this.drawHouseTrimming();
    if (this.options.showRulers) this.drawAllRulers();
    if (this.options.showSignBoundaries) this.drawSignBoundaries();
    if (this.options.showCusps) this.drawCusps();
    if (this.options.showGoldenPoints) this.drawGoldenPoints();
    this.drawSigns();
    if (this.options.showPlanetLines) this.drawPlanetLines();
    if (this.options.showAspects) this.drawAspects();
    this.drawPlanets();
    if (this.options.showInnerCircles) this.drawInnerCircles();

    ctx.restore();
  }

  private validateData(data: RadixData): RadixData {
    if (data.houses.length !== 12) throw new Error("houses must contain exactly 12 cusp longitudes.");
    if (data.planets.length === 0) throw new Error("At least one planet is required.");
    return {
      ...data,
      ascendant: normalizeDegree(data.ascendant),
      houses: data.houses.map(normalizeDegree),
      planets: data.planets.map((planet) => ({ ...planet, longitude: normalizeDegree(planet.longitude) })),
      zodiac: data.zodiac?.map((sign) => ({ ...sign, longitude: normalizeDegree(sign.longitude) })),
    };
  }

  private prepareCanvas(): void {
    const ratio = this.options.pixelRatio;
    const cssWidth = this.canvas.clientWidth || Number(this.canvas.getAttribute("width")) || 800;
    const cssHeight = this.canvas.clientHeight || Number(this.canvas.getAttribute("height")) || cssWidth;
    const targetWidth = Math.max(1, Math.round(cssWidth * ratio));
    const targetHeight = Math.max(1, Math.round(cssHeight * ratio));
    if (this.canvas.width !== targetWidth) this.canvas.width = targetWidth;
    if (this.canvas.height !== targetHeight) this.canvas.height = targetHeight;

    this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.ctx.clearRect(0, 0, cssWidth, cssHeight);
    this.ctx.fillStyle = this.options.palette.background;
    this.ctx.fillRect(0, 0, cssWidth, cssHeight);
    this.centerX = cssWidth / 2;
    this.centerY = cssHeight / 2;
    this.radius = Math.min(cssWidth, cssHeight) * 0.47;
  }

  private radialLine(outerRadius: number, innerRadius: number, degree: number): void {
    const outer = this.polar(outerRadius, degree);
    const inner = this.polar(innerRadius, degree);
    this.ctx.beginPath();
    this.ctx.moveTo(inner.x, inner.y);
    this.ctx.lineTo(outer.x, outer.y);
    this.ctx.stroke();
  }

  /** Trace an arc by zodiac longitude, avoiding Canvas/Cairo direction ambiguity. */
  private longitudeArc(radius: number, startDegree: number, sweepDegree: number, move = true): void {
    const steps = Math.max(2, Math.ceil(Math.abs(sweepDegree) / 2));
    for (let index = 0; index <= steps; index += 1) {
      const point = this.polar(radius, startDegree + (sweepDegree * index) / steps);
      if (index === 0 && move) this.ctx.moveTo(point.x, point.y);
      else this.ctx.lineTo(point.x, point.y);
    }
  }

  private drawPlanetLines(): void {
    // Disabled as per user request to remove lines from inner planets
  }

  private drawCircle(radius: number): void {
    const ctx = this.ctx;
    ctx.beginPath();
    ctx.arc(this.centerX, this.centerY, radius, 0, Math.PI * 2);
    ctx.stroke();
  }

  private drawInnerCircles(): void {
    const ctx = this.ctx;
    ctx.save();
    ctx.strokeStyle = rgb(this.options.palette.foreground);
    
    // Central small circle
    ctx.fillStyle = "#ffffff";
    ctx.lineWidth = this.radius * 0.001;
    this.drawCircle(this.radius * 0.065);
    ctx.fill();
    ctx.stroke();

    ctx.lineWidth = this.radius * 0.0015;
    this.drawCircle(this.radius * RadixLayout.R_INNER);
    ctx.lineWidth = this.radius * 0.004;
    this.drawCircle(this.radius * RadixLayout.R_RULED_INNER);
    ctx.lineWidth = this.radius * 0.0015;
    this.drawCircle(this.radius * RadixLayout.R_RULED_MID);
    ctx.restore();
  }

  private drawAllRulers(): void {
    const rules = new Map<number, readonly [number, number, number]>([
      [RadixLayout.R_RULED_MID, [-0.016, -0.01, -0.004]], // Negative goes outward
      [RadixLayout.R_RULED_INNER, [-0.022, -0.015, -0.006]],
    ]);
    this.drawRuler(RadixLayout.R_RULED_MID, rules.get(RadixLayout.R_RULED_MID) as readonly [number, number, number]);
    this.drawRuler(RadixLayout.R_RULED_INNER, rules.get(RadixLayout.R_RULED_INNER) as readonly [number, number, number]);

    // Draw Huber Age Points at cusps
    if (this.data?.houses && this.data.houses.length >= 12) {
      const ctx = this.ctx;
      ctx.save();
      ctx.fillStyle = "#888888";
      ctx.font = `${this.radius * 0.035}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const textRadius = this.radius * (RadixLayout.R_RULED_MID + 0.045); // Keep Huber numbers close to the ticks


      
      const huberAges = ["00", "06", "12", "18", "24", "30", "36", "42", "48", "54", "60", "66"];
      for (let i = 0; i < 12; i++) {
        const cuspDegree = this.data.houses[i];
        const pos = this.polar(textRadius, cuspDegree);
        // Align text upright relative to the circle
        const screenAngle = ((180 + this.data.ascendant) - cuspDegree) * RAD;
        ctx.save();
        ctx.translate(pos.x, pos.y);
        ctx.rotate(screenAngle + Math.PI / 2);
        ctx.fillText(huberAges[i], 0, 0);
        ctx.restore();
      }
      ctx.restore();
    }
  }

  private drawRuler(ruleFactor: number, insetFactors: readonly [number, number, number]): void {
    const ctx = this.ctx;
    const [tenInset, fiveInset, defaultInset] = insetFactors.map((factor) => this.radius * factor) as [number, number, number];
    const rulerRadius = this.radius * ruleFactor;

    ctx.save();
    ctx.strokeStyle = "#444444"; // More distinct, darker grey for the ticks
    for (let degree = 0; degree < 360; degree += 1) {
      const isMajor = degree % 10 === 0;
      const isMedium = degree % 5 === 0 && !isMajor;
      const inset = isMajor ? tenInset : isMedium ? fiveInset : defaultInset;
      
      ctx.lineWidth = isMajor ? (this.radius * 0.003) : isMedium ? (this.radius * 0.002) : (this.radius * 0.001);
      this.radialLine(rulerRadius, rulerRadius - inset, degree);
    }
    ctx.restore();
  }

  private drawSignBoundaries(): void {
    const ctx = this.ctx;
    const base = this.radius * RadixLayout.R_RULED_INNER;
    const inset = base * RadixLayout.R_LINE_INSET;
    ctx.save();
    ctx.strokeStyle = rgb(this.options.palette.foreground);
    ctx.lineWidth *= 0.5;
    for (let degree = 0; degree < 360; degree += 30) {
      this.radialLine(base + inset, base, degree);
    }
    ctx.restore();
  }

  private drawCusps(): void {
    if (!this.layout) return;
    const ctx = this.ctx;
    const cuspRadius = this.radius * RadixLayout.R_RULED_MID;
    const outerRadius = cuspRadius * 1.10;
    const widths = [0.6, 0.5, 0.5] as const;
    const fontSize = Math.max(10, 16 * cuspRadius * 0.00246);

    ctx.save();
    ctx.font = `${fontSize}px sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    this.data?.houses.forEach((house, index) => {
      ctx.lineWidth = widths[index % widths.length] * this.options.baselineLineWidth;
      ctx.strokeStyle = rgb(this.options.palette.cuspColors[index % this.options.palette.cuspColors.length]);
      ctx.fillStyle = ctx.strokeStyle;
      this.radialLine(outerRadius, cuspRadius, house);
      const labelPoint = this.polar(outerRadius * 1.12, house); // Push Cusp names/numbers MUCH further out
      ctx.fillText(CUSP_NAMES[index], labelPoint.x, labelPoint.y);
    });
    ctx.restore();
  }

  private drawGoldenPoints(): void {
    if (!this.layout) return;
    const ctx = this.ctx;
    const lowRadius = this.radius * 0.8 * 0.965;
    const inverseRadius = this.radius * 0.8 * 0.993;
    const dotRadius = Math.max(1.5, 1.5 * this.radius * 0.0024);

    ctx.save();
    for (const point of this.layout.goldenPoints) {
      const low = this.polar(lowRadius, point.house + point.low);
      ctx.fillStyle = rgb(this.options.palette.goldenLow);
      ctx.beginPath();
      ctx.arc(low.x, low.y, dotRadius, 0, TAU);
      ctx.fill();

      const inverse = this.polar(inverseRadius, point.house + point.inverse);
      ctx.fillStyle = rgb(this.options.palette.goldenInverse);
      ctx.beginPath();
      ctx.arc(inverse.x, inverse.y, dotRadius, 0, TAU);
      ctx.fill();
    }
    ctx.restore();
  }

  private drawHouseZones(): void {
    if (!this.layout || !this.data) return;
    const ctx = this.ctx;
    const percentages = [0.21, 0.41, 0.68, 0.75, 0.87, 0.97, 1.0] as const;
    const ringRadius = this.radius * RadixLayout.R_RULED_MID * 1.006;
    const scaledLineWidth = this.options.baselineLineWidth * ringRadius * 0.00246;

    ctx.save();
    ctx.strokeStyle = rgb(this.options.palette.houseZoneBase);
    ctx.lineWidth = 6.5 * scaledLineWidth;
    this.drawCircle(ringRadius);
    ctx.stroke();

    ctx.lineWidth = 5 * scaledLineWidth;
    ctx.lineCap = "butt";
    this.data.houses.forEach((house, houseIndex) => {
      let previous = 0;
      const houseSize = this.layout?.sizes[houseIndex] ?? 30;
      percentages.forEach((percentage, zoneIndex) => {
        const current = houseSize * percentage;
        ctx.strokeStyle = rgb(this.options.palette.houseZones[zoneIndex % this.options.palette.houseZones.length]);
        ctx.beginPath();
        this.longitudeArc(ringRadius, house + previous, current - previous, true);
        ctx.stroke();
        previous = current;
      });
    });
    ctx.restore();
  }

  /** Port of d_house_trimming() using Canvas gradients and bezierCurveTo(). */
  private drawHouseTrimming(): void {
    if (!this.layout || !this.data) return;
    const ctx = this.ctx;
    const low = this.radius * 0.79;
    const cusp = this.radius * 0.89;
    const size = 30;
    const talk = size * PHI;
    const inverse = size - talk;

    ctx.save();
    ctx.lineWidth = 1.1 * this.options.baselineLineWidth;
    for (let index = 0; index < 12; index += 1) {
      const cuspDegree = index * 30;
      const begin = this.polar(low, cuspDegree - inverse);
      const center = this.polar(cusp, cuspDegree);
      const end = this.polar(low, cuspDegree + talk);

      const cp1 = this.polar(low, cuspDegree - inverse * 0.45);
      const cp2 = this.polar(0.95 * cusp, cuspDegree - inverse * 0.15);
      const cp3 = this.polar(0.95 * cusp, cuspDegree + inverse * 0.45);
      const cp4 = this.polar(low, cuspDegree + talk * 0.7);

      const gradient = ctx.createLinearGradient(begin.x, begin.y, end.x, end.y);
      if (index % 3 === 0) {
        gradient.addColorStop(0, rgb([0, 0.6, 0]));
        gradient.addColorStop(0.3, rgb([0.7, 0, 0]));
      } else if (index % 3 === 1) {
        gradient.addColorStop(0, rgb([0.7, 0, 0]));
        gradient.addColorStop(0.3, rgb([0, 0, 0.6]));
      } else {
        gradient.addColorStop(0, rgb([0, 0, 0.6]));
        gradient.addColorStop(0.3, rgb([0, 0.6, 0]));
      }

      ctx.strokeStyle = gradient;
      ctx.beginPath();
      ctx.moveTo(begin.x, begin.y);
      ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, center.x, center.y);
      ctx.bezierCurveTo(cp3.x, cp3.y, cp4.x, cp4.y, end.x, end.y);
      ctx.stroke();
    }
    ctx.restore();
  }

  private drawSigns(): void {
    if (!this.layout || !this.data?.zodiac) return;
    const signRadius = this.radius * (RadixLayout.R_RULED_INNER + RadixLayout.R_RULED_MID) / 2;
    const glyphSize = this.radius * 0.12;

    for (const sign of this.data.zodiac) {
      const position = this.polar(signRadius, sign.longitude);
      const screenAngle = ((180 + this.data.ascendant) - sign.longitude) * RAD;
      this.drawGlyph(sign.glyph, position, glyphSize, sign.color, screenAngle + Math.PI / 2);
    }
  }



  private drawPlanets(): void {
    if (!this.layout || !this.data) return;
    const plots = this.layout.injectPlanetDegrees();
    const basePlanetRadius = this.radius * RadixLayout.R_PLANET;
    const glyphSize = this.radius * 0.058;

    plots.forEach((plot, index) => {
      const planet = this.data?.planets[index];
      if (!planet) return;
      const position = this.polar(basePlanetRadius * plot.radialFactor, plot.longitude);
      this.drawGlyph(planet.glyph, position, glyphSize, planet.color, 0);
    });
  }

  private drawAspects(): void {
    if (!this.data) return;
    let aspects: AspectDatum[];
    if (this.data.aspects) {
      const coordinates = this.data.aspectCoordinates ?? "indices";
      aspects = this.data.aspects.map((aspect) => ({
        ...aspect,
        p1:
          coordinates === "indices"
            ? this.data?.planets[aspect.p1]?.longitude ?? aspect.p1
            : normalizeDegree(aspect.p1),
        p2:
          coordinates === "indices"
            ? this.data?.planets[aspect.p2]?.longitude ?? aspect.p2
            : normalizeDegree(aspect.p2),
      }));
    } else if (this.options.aspectEngine) {
      aspects = this.options.aspectEngine.resolveAspects(this.data.planets);
    } else {
      return;
    }

    const radius = this.radius * 0.435;
    const goodwill = aspects.filter((aspect) => aspect.gw === true || (aspect.f1 > 1 && aspect.f2 > 1));
    const afterGoodwill = aspects.filter((aspect) => !(aspect.gw === true || (aspect.f1 > 1 && aspect.f2 > 1)));
    const conjunctions = afterGoodwill.filter((aspect) => aspect.a === 0);
    const afterConjunctions = afterGoodwill.filter((aspect) => aspect.a !== 0);
    const unilateral = afterConjunctions.filter((aspect) => aspect.f1 > 1 || aspect.f2 > 1);
    const normal = afterConjunctions.filter((aspect) => aspect.f1 <= 1 && aspect.f2 <= 1);

    if (goodwill.length > 0) {
      new GoodwillAspect(this.options.baselineLineWidth).draw(this.ctx, radius, goodwill, this.polar.bind(this));
    }
    if (conjunctions.length > 0) {
      this.conjunctio.draw(
        this.ctx,
        radius,
        conjunctions,
        this.screenAngle.bind(this),
        this.screenPolar.bind(this),
      );
    }

    if (this.options.aspectMode === "fusus") {
      this.fusus.draw(this.ctx, radius, [...unilateral, ...normal], this.polar.bind(this));
    } else if (this.options.aspectMode === "unilateral") {
      this.unilateral.draw(this.ctx, radius, [...unilateral, ...normal], this.polar.bind(this));
    } else {
      if (unilateral.length > 0) {
        this.unilateral.draw(this.ctx, radius, unilateral, this.polar.bind(this));
      }
      if (normal.length > 0) {
        this.fusus.draw(this.ctx, radius, normal, this.polar.bind(this));
      }
    }
  }

  private drawGlyph(glyph: Glyph, point: Point, targetSize: number, color: RGB, rotation: number): void {
    const ctx = this.ctx;
    ctx.save();
    ctx.translate(point.x, point.y);
    ctx.rotate(rotation);
    ctx.fillStyle = rgb(color);
    ctx.strokeStyle = rgb(color);

    if (glyph.kind === "text") {
      ctx.font = `${glyph.fontWeight ?? "normal"} ${targetSize}px ${glyph.fontFamily ?? this.options.fontFamily}`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(glyph.text, 0, 0);
      ctx.restore();
      return;
    }

    const bounds = glyph.kind === "path" ? glyph.bounds : glyph.viewBox;
    const scale = targetSize / Math.max(bounds.width, bounds.height, 1);
    ctx.scale(scale, scale);
    ctx.translate(-(bounds.x + bounds.width / 2), -(bounds.y + bounds.height / 2));
    ctx.beginPath();

    if (glyph.kind === "path") {
      replayPath(ctx, glyph.commands);
      ctx.fill();
    } else {
      const path = new Path2D(glyph.path);
      ctx.fill(path);
    }
    ctx.restore();
  }
}
