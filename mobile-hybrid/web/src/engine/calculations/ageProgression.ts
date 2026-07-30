import type { AgeProgressionEvent, PlanetData } from './types';
import { calculateHouseSizes } from './chartTypes';

export const planames = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'node'];
export const zodnames = ['aries', 'tauro', 'geminis', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagitario', 'capricornio', 'acuario', 'piscis'];
export const aspnames = ['conj', 'semi', 'sext', 'cuad', 'trig', 'quinc', 'opos', 'quinc', 'trig', 'cuad', 'sext', 'semi'];

const PHI = 1 / ((1 + Math.sqrt(5)) / 2);

interface TimeLapsus {
  begin: Date;
  lapsusDays: number;
}

function isLeapYear(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
}

function createDate(year: number, month: number, day: number, hour: number, minutes: number): Date {
  // Mimic Python's leap year handling (fallback to day-1)
  if (month === 2 && day === 29 && !isLeapYear(year)) {
    return new Date(Date.UTC(year, month - 1, 28, hour, minutes, 0));
  }
  return new Date(Date.UTC(year, month - 1, day, hour, minutes, 0));
}

export function houseTimeLapsus(birthDateISO: string, h: number, playagain = 0): TimeLapsus {
  // Parse birthDateISO "1990-06-15T14:30:00"
  const [datePart, timePart] = birthDateISO.split('T');
  const [yearStr, monthStr, dayStr] = datePart.split('-');
  const [hourStr, minStr] = timePart.split(':');

  let year = parseInt(yearStr, 10);
  const month = parseInt(monthStr, 10);
  const day = parseInt(dayStr, 10);
  const hour = parseInt(hourStr, 10);
  const minutes = parseInt(minStr, 10);

  if (playagain) {
    year += playagain * 72;
  }

  const bbegin = createDate(year + h * 6, month, day, hour, minutes);
  const eend = createDate(year + (h + 1) * 6, month, day, hour, minutes);

  // Difference in milliseconds to days
  const lapsusDays = (eend.getTime() - bbegin.getTime()) / (1000 * 60 * 60 * 24);

  return { begin: bbegin, lapsusDays };
}

function plMidpoints(plans: PlanetData[], houses: number[]) {
  const allMidpoints = [];
  for (let i = 0; i < plans.length; i++) {
    const nextIx = (i + 1) % 11;
    let midpoint = plans[nextIx].degree - plans[i].degree;
    if (midpoint < 0) midpoint += 360;
    midpoint = plans[i].degree + midpoint / 2;
    if (midpoint > 360) midpoint -= 360;

    const name = `${planames[plans[i].ix]}/${planames[plans[nextIx].ix]}`;
    
    for (let j = 0; j < 12; j++) {
      const h1 = houses[j];
      let h2 = houses[(j + 1) % 12];
      let mp = midpoint;
      if (h1 > h2) {
        if (mp < h1 && mp < h2) mp += 360;
        h2 += 360;
      }
      if (mp > h1 && mp < h2) {
        const sign = Math.floor(midpoint / 30);
        const degree = midpoint - 30 * sign;
        allMidpoints.push({ degree, sign, house: j, name });
        break;
      }
    }
  }
  return allMidpoints;
}

export function calculateAgeProgression(
  birthDateISO: string,
  planets: PlanetData[],
  houses: number[]
): AgeProgressionEvent[] {
  const degs = houses.map(h => {
    const sign = Math.floor(h / 30);
    return h - sign * 30;
  });
  
  const sizes = calculateHouseSizes(houses);
  const mids = plMidpoints(planets, houses);
  const ageProg: AgeProgressionEvent[] = [];

  for (let i = 0; i < 12; i++) {
    const events: any[] = [];
    const timeObj = houseTimeLapsus(birthDateISO, i);
    
    const d = timeObj.begin;
    ageProg.push({
      day: String(d.getUTCDate()).padStart(2, '0'),
      mon: String(d.getUTCMonth() + 1).padStart(2, '0'),
      year: d.getUTCFullYear(),
      lab: `Cc ${i + 1}`,
      cl: 'txt_cp'
    });

    const house = houses[i];
    let s = 0;
    let scusp = 30.0 - degs[i];
    const sign = Math.floor(house / 30);

    while (scusp < sizes[i]) {
      events.push({ scusp, sname: zodnames[(sign + 1 + s) % 12], cl: 'sign' });
      s += 1;
      scusp += s * 30; 
    }

    for (const m of mids) {
      const dif = Math.abs(sign - m.sign);
      let lg = m.degree + 30 * dif - degs[i];
      if (lg < 0) lg += 30;
      if (m.house === i) {
        events.push({ scusp: lg, sname: m.name, cl: 'mid' });
      }
    }

    for (const p of planets) {
      let pl_lg = p.degree; // Wait, in python p is the dictionary, but degree is the longitude!
      const pl_sign = Math.floor(pl_lg / 30);
      pl_lg = pl_lg - 30 * pl_sign;
      let lg = pl_lg - degs[i];
      if (lg < 0) lg += 30;
      
      let c = 0;
      while (lg + 30 * c < sizes[i]) {
        const aspsign = Math.floor((house + lg + 30 * c) / 30) % 12;
        const realasp = Math.abs(pl_sign - aspsign);
        const label = `${aspnames[realasp]}/${planames[p.ix]}`;
        events.push({ scusp: lg + 30 * c, sname: label, cl: 'asp' });
        c += 1;
      }
    }

    const pr = sizes[i] * PHI;
    const pi = sizes[i] - pr;
    events.push({ scusp: pr, sname: `Pr ${i + 1}`, cl: 'pr' });
    events.push({ scusp: pi, sname: `Pi ${i + 1}`, cl: 'pi' });

    events.sort((a, b) => a.scusp - b.scusp);

    for (const e of events) {
      const fac = e.scusp / sizes[i];
      const days = timeObj.lapsusDays * fac;
      
      // Compute the new date by adding milliseconds
      const dat = new Date(timeObj.begin.getTime() + days * 24 * 60 * 60 * 1000);
      
      ageProg.push({
        day: String(dat.getUTCDate()).padStart(2, '0'),
        mon: String(dat.getUTCMonth() + 1).padStart(2, '0'),
        year: dat.getUTCFullYear(),
        lab: e.sname,
        cl: e.cl
      });
    }
  }

  return ageProg;
}
