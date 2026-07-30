// Helper: Calculate house sizes from 12 houses array
export function calculateHouseSizes(houses: number[]): number[] {
  const sizes = new Array(12).fill(0);
  for (let i = 0; i < 6; i++) {
    let s = houses[i + 1] - houses[i];
    if (s < 0) s += 360;
    sizes[i] = s;
    sizes[i + 6] = s; // Opposite houses are equal in most quadrant systems
  }
  return sizes;
}

// 1. Causal / Soul Chart
export function calculateSoulChart(planets: number[], houses: number[]): number[] {
  const sizes = calculateHouseSizes(houses);
  const splan = [];
  for (const p of planets) {
    const s = Math.floor(p / 30);
    const dh = (p - s * 30) * sizes[s] / 30.0;
    let pos = houses[s] + dh;
    if (pos > 360) pos -= 360;
    splan.push(pos);
  }
  return splan;
}

// 2. Nodal Chart
export function calculateUrNodChart(planets: number[], houses: number[]): number[] {
  const sizes = calculateHouseSizes(houses);
  const plans = [...planets];
  plans[10] = houses[0]; // Ascendant is swapped with Node in original python logic
  const nod = planets[10]; // Node
  const n = nod % 30.0;

  const uplan = [];
  for (const p of plans) {
    // Math.floor can go negative, Python's int() towards zero, so handle negative mod safely:
    let diff = ((p - nod) / 30.0) % 12;
    if (diff < 0) diff += 12;
    const h = 11 - Math.floor(diff);

    let dist = (n - (p % 30.0)) % 30.0;
    if (dist < 0) dist += 30.0;

    let res = (houses[h] + dist * sizes[h] / 30.0) % 360;
    uplan.push(res);
  }
  return uplan;
}

// Helper: for each zodiac sign boundary (0,30,...330), find which house it falls in.
// Port of Python's `sign_in_house()`.
export function calculateSignInHouse(houses: number[]): number[] {
  const signinh: number[] = [];
  for (let i = 0; i < 12; i++) {
    let sign = 30 * i;
    for (let j = 0; j < houses.length; j++) {
      let h1 = houses[j];
      let h2 = houses[(j + 1) % 12];
      if (h1 > h2) {
        if (sign < h1 && sign < h2) sign += 360;
        h2 += 360;
      }
      if (sign > h1 && sign < h2) {
        signinh.push(j);
        break;
      }
    }
  }
  return signinh;
}

// Where each zodiac sign boundary falls in the equalized (30deg/house) house-space.
// Port of Python's `house_sign_long()`. Used to draw the warped zodiac ring in the House chart.
export function calculateHouseSignLong(houses: number[]): number[] {
  const signinh = calculateSignInHouse(houses);
  const sizes = calculateHouseSizes(houses);
  const factor = sizes.map(s => 30 / s);
  const hssg: number[] = [];
  for (let i = 0; i < 12; i++) {
    const h = signinh[i];
    let dist = (i * 30 - houses[h]) % 360;
    if (dist < 0) dist += 360;
    hssg.push(h * 30 + dist * factor[h]);
  }
  return hssg;
}

// 3. Houses / Dharma Chart
export function calculateHouseChart(planets: number[], houses: number[]): number[] {
  const sizes = calculateHouseSizes(houses);

  // Find which house each planet is in
  const plinh = new Array(11).fill(0);
  for (let i = 0; i < planets.length; i++) {
    let plan = planets[i];
    for (let j = 0; j < 12; j++) {
      let h1 = houses[j];
      let h2 = houses[(j + 1) % 12];
      if (h1 > h2) {
        if (plan < h1 && plan < h2) plan += 360;
        h2 += 360;
      }
      if (plan >= h1 && plan < h2) {
        plinh[i] = j;
        break;
      }
    }
  }

  const factor = sizes.map(s => 30.0 / s);
  const hspl = new Array(11).fill(0);
  for (let i = 0; i < planets.length; i++) {
    const h = plinh[i];
    let dist = planets[i] - houses[h];
    if (dist < 0) dist += 360;
    hspl[i] = (h * 30 + dist * factor[h]) % 360;
  }

  return hspl;
}

export function transformPlanets(
  type: string,
  radixPlanets: any[],
  houses: number[]
): any[] {
  const pLongitudes = radixPlanets.map(p => p.longitude);
  let transformed: number[] = pLongitudes;

  switch (type) {
    case 'draw_soul':
    case 'draw_radsoul':
      transformed = calculateSoulChart(pLongitudes, houses);
      break;
    case 'draw_ur_nodal':
    case 'draw_nod':
      transformed = calculateUrNodChart(pLongitudes, houses);
      break;
    case 'draw_dharma':
    case 'draw_raddharma':
    case 'draw_house':
      transformed = calculateHouseChart(pLongitudes, houses);
      break;
    default:
      transformed = pLongitudes;
  }

  return radixPlanets.map((p, i) => {
    const lon = transformed[i];
    return {
      ...p,
      longitude: lon,
      sign: 'transformed',
      degree: lon
    };
  });
}
