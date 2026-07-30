export type OrbsMatrix = number[][]; // 5x5 matrix of orbs

export interface EngineSettings {
  orbs: OrbsMatrix;
  peorbs: OrbsMatrix;
  transits?: number[];
}

export interface PlanetData {
  degree: number; // Ecliptic longitude (0-360)
  ix: number;     // Planet index (0=Sun, 1=Moon... 10=Node)
}

export interface AspectResult {
  p1: number;
  p2: number;
  a: number;      // aspect index (0=conj, 1=semi, 2=sext...)
  f1: number;     // strength/orb fraction 1
  f2: number;     // strength/orb fraction 2
  gw?: boolean;   // goodwill flag for out-of-orb but within 1.1x bounds
}

export interface Elements {
  fire: number;
  earth: number;
  air: number;
  water: number;
}

export interface Crosses {
  card: number;
  fix: number;
  mut: number;
}

export interface DynamicsResult {
  elem: Elements;
  cross: Crosses;
}

export interface DynamicsSummary {
  signdyn: DynamicsResult;
  housedyn: DynamicsResult;
}

export interface AgeProgressionEvent {
  day: string;
  mon: string;
  year: number;
  lab: string;
  cl: string;
  scusp?: number; // internal sorting key, not always present in final UI but useful
}
