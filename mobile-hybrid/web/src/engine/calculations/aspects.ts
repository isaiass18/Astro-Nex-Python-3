import type { AspectResult, EngineSettings } from './types';

export const planclass = [0, 0, 1, 1, 2, 1, 2, 3, 3, 3, 4];
export const aspclass = [4, 0, 1, 2, 3, 1, 4, 1, 3, 2, 1, 0];

/**
 * Calculates aspects between planets using Astro-Nex orb logic.
 * Equivalent to `Chart.aspects()` in python.
 * 
 * @param planets Array of 11 planetary longitudes (Sun to Node)
 * @param settings Engine settings containing the orbs matrices
 * @returns List of calculated aspects
 */
export function calculateAspects(planets: number[], settings: EngineSettings): AspectResult[] {
  const chart_orbs: AspectResult[] = [];
  const orbs = settings.orbs;

  for (let i = 0; i < planets.length; i++) {
    for (let j = i + 1; j < planets.length; j++) {
      const pci = planclass[i];
      let pcj = planclass[j];
      if (j === 10) {
        pcj = planclass[i];
      }

      const dis = Math.abs(planets[i] - planets[j]);
      let nsig = Math.floor(dis / 30);
      let orb = dis - nsig * 30;

      if (orb > 20.0) {
        nsig += 1;
        orb = 30.0 - orb;
      }

      const a = nsig % 12;
      const acl = aspclass[a];

      if (orb <= 9.0) {
        const orb1 = orbs[pci][acl];
        const orb2 = orbs[pcj][acl];

        if (orb <= orb1 || orb <= orb2) {
          const f1 = orb / orb1;
          const f2 = orb / orb2;
          chart_orbs.push({ p1: i, p2: j, a, f1, f2, gw: false });
        } else if (orb <= orb1 * 1.1 || orb <= orb2 * 1.1) {
          chart_orbs.push({ p1: i, p2: j, a, f1: 0, f2: 0, gw: true });
        }
      }
    }
  }

  return chart_orbs;
}

export function calculateDrawAspects(
  planets: number[], 
  settings: EngineSettings,
  clickPlanets?: number[]
): AspectResult[] {
  const aspects: AspectResult[] = [];
  const isCross = !!clickPlanets;
  const orbs = isCross ? (settings.peorbs || settings.orbs) : settings.orbs;
  const pairpl = clickPlanets || planets;
  const lencl = pairpl.length;

  for (let i = 0; i < planets.length; i++) {
    const startJ = isCross ? 0 : i + 1;
    for (let j = startJ; j < lencl; j++) {
      const dis = Math.abs(planets[i] - pairpl[j]);
      let nsig = Math.floor(dis / 30);
      let orb = dis % 30;

      if (orb > 20.0) {
        nsig += 1;
        orb = 30.0 - orb;
      }

      const a = nsig % 12;
      const pc1 = planclass[i];
      let pc2 = planclass[j];
      
      if (isCross || (!isCross && j !== 10)) {
        pc2 = planclass[j];
      } else {
        pc2 = planclass[i];
      }

      const acl = aspclass[a];
      const orb1 = orbs[pc1][acl];
      const orb2 = orbs[pc2][acl];

      if (orb <= orb1 * 1.1 || orb <= orb2 * 1.1) {
        aspects.push({
          p1: i, // Radix (inner)
          p2: j, // Transit/Click (outer)
          a,
          f1: orb / orb1,
          f2: orb / orb2
        });
      }
    }
  }

  return aspects;
}
