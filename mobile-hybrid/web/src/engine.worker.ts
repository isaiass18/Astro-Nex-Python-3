import SwissEPH from 'sweph-wasm';
import { calculateAspects, calculateDrawAspects } from './engine/calculations/aspects';
import { transformPlanets, calculateHouseSizes, calculateHouseSignLong } from './engine/calculations/chartTypes';
import { calculateDynamics } from './engine/calculations/dynamics';

const PLANET_NAMES = [
  "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
  "uranus", "neptune", "pluto", "node"
];

const SIGNS = [
  "aries", "tauro", "geminis", "cancer", "leo", "virgo",
  "libra", "scorpio", "sagitario", "capricornio", "acuario", "piscis"
];

const DEFAULT_SETTINGS = {
  orbs: [
    [3.0, 5.0, 6.0, 8.0, 9.0],
    [2.0, 4.0, 5.0, 6.0, 7.0],
    [1.5, 3.0, 4.0, 5.0, 6.0],
    [1.0, 2.0, 3.0, 4.0, 5.0],
    [1.0, 2.0, 2.0, 3.0, 4.0]
  ],
  peorbs: [
    [1.5, 1.5, 1.5, 1.5, 1.5],
    [1.5, 1.5, 1.5, 1.5, 1.5],
    [1.5, 1.5, 1.5, 1.5, 1.5],
    [1.5, 1.5, 1.5, 1.5, 1.5],
    [1.5, 1.5, 1.5, 1.5, 1.5]
  ]
};

function localTimeToUtc(year: number, month: number, day: number, hour: number, timezone?: string) {
  if (!timezone) return { year, month, day, hour };
  const wholeHour = Math.floor(hour);
  const minute = Math.round((hour - wholeHour) * 60);
  const localAsUtc = Date.UTC(year, month - 1, day, wholeHour, minute);
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
  });
  const parts = formatter.formatToParts(new Date(localAsUtc));
  const read = (type: string) => Number(parts.find((part) => part.type === type)?.value);
  const observedAsUtc = Date.UTC(read('year'), read('month') - 1, read('day'), read('hour'), read('minute'));
  const corrected = new Date(localAsUtc - (observedAsUtc - localAsUtc));
  return {
    year: corrected.getUTCFullYear(),
    month: corrected.getUTCMonth() + 1,
    day: corrected.getUTCDate(),
    hour: corrected.getUTCHours() + corrected.getUTCMinutes() / 60
  };
}

self.onmessage = async (e: MessageEvent) => {
  if (e.data.type === 'CALCULATE') {
    try {
      const swe = await SwissEPH.init();

      const { year, month, day, hour, lat, lon, timezone, tYear, tMonth, tDay, tHour, chartType } = e.data;
      const utcBirth = localTimeToUtc(year, month, day, hour, timezone);
      const jd = swe.swe_julday(utcBirth.year, utcBirth.month, utcBirth.day, utcBirth.hour, swe.SE_GREG_CAL);

      let planets = [];
      const planetLongitudes = [];

      for (let i = 0; i < 11; i++) {
        const pos = swe.swe_calc_ut(jd, i, swe.SEFLG_SWIEPH);
        const lonPos = pos[0];
        const signIdx = Math.floor(lonPos / 30);


        planetLongitudes.push(lonPos);
        planets.push({
          index: i,
          name: PLANET_NAMES[i],
          longitude: lonPos,
          sign: SIGNS[signIdx],
          degree: lonPos
        });
      }

      // Astro-Nex y los golden fixtures emplean Koch, no Placidus.
      const houseData = swe.swe_houses(jd, lat, lon, "K");
      let houses = (houseData as any).cusps || (houseData as any).house || (houseData as any).houses || (houseData as any).data?.houses;

      if (!houses && houseData && typeof (houseData as any).length === 'number' && (houseData as any).length >= 12) {
        houses = houseData;
      }

      if (!houses || typeof houses.length !== 'number' || houses.length === 0) {
        throw new Error("No se pudo calcular el sistema de casas. houseData devuelto es inválido.");
      }

      houses = Array.from(houses);
      if (houses.length === 13) {
        houses = houses.slice(1);
      }
      if (houses.length < 12) {
        throw new Error(`El sistema de casas devolvió datos incompletos: ${houses.length} elementos.`);
      }

      // Ensure numerical types
      houses = houses.map((h: any) => Number(h) || 0);

      // Transform planets for specific chart types
      if (chartType && chartType !== 'draw_nat') {
        planets = transformPlanets(chartType, planets, houses);
      }

      // For the "House" chart, Astro-Nex also warps the zodiac ring itself
      // (house_sign_long): sign boundaries are remapped into the equalized
      // 30deg/house space instead of following the real unequal houses.
      const houseSignCusps = chartType === 'draw_house'
        ? calculateHouseSignLong(houses)
        : undefined;

      // Calculate dynamics on original radix planets
      const houseSizes = calculateHouseSizes(houses);
      const dynamics = calculateDynamics(planetLongitudes, houses, houseSizes);

      const aspects = calculateAspects(planets.map(p => p.longitude), DEFAULT_SETTINGS);

      let transitPlanets = undefined;
      let interAspects = undefined;

      if (tYear !== undefined && tMonth !== undefined) {
        transitPlanets = [];
        const utcTransit = localTimeToUtc(tYear, tMonth, tDay, tHour, timezone);
        const tJd = swe.swe_julday(utcTransit.year, utcTransit.month, utcTransit.day, utcTransit.hour, swe.SE_GREG_CAL);
        for (let i = 0; i < 11; i++) {
          const pos = swe.swe_calc_ut(tJd, i, swe.SEFLG_SWIEPH);
          const lonPos = pos[0];
          const signIdx = Math.floor(lonPos / 30);

          transitPlanets.push({
            index: i,
            name: PLANET_NAMES[i],
            longitude: lonPos,
            sign: SIGNS[signIdx],
            degree: lonPos
          });
        }

        interAspects = calculateDrawAspects(
          planets.map(p => p.longitude),
          DEFAULT_SETTINGS,
          transitPlanets.map(p => p.longitude)
        );
      }

      self.postMessage({
        type: 'SUCCESS',
        chartData: {
          birthYear: year,
          planets,
          aspects,
          interAspects,
          houses,
          transitPlanets,
          dynamics,
          chartType,
          houseSignCusps
        }
      });

    } catch (err: any) {
      self.postMessage({ type: 'ERROR', message: err.message });
    }
  }
};
