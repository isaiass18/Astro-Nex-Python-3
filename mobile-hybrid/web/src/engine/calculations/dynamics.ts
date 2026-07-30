export const POINTS = [12, 12, 8, 8, 8, 8, 12, 6, 6, 6, 4];

export function resolveDyn(dinary: number[]) {
  const elem = { fire: 0, earth: 0, air: 0, water: 0 };
  const cross = { card: 0, fix: 0, mut: 0 };

  for (let i = 0; i < 12; i++) {
    if (i % 4 === 3) elem.water += dinary[i];
    else if (i % 4 === 0) elem.fire += dinary[i];
    else if (i % 4 === 1) elem.earth += dinary[i];
    else if (i % 4 === 2) elem.air += dinary[i];

    if (i % 3 === 2) cross.mut += dinary[i];
    else if (i % 3 === 0) cross.card += dinary[i];
    else if (i % 3 === 1) cross.fix += dinary[i];
  }
  return { elem, cross };
}

export function signDyn(planets: number[], houses: number[]) {
  let sum1 = 0;
  const signs = new Array(12).fill(0);
  const hou = new Array(12).fill(0);
  
  [0, 3, 6, 9].forEach(h => {
    hou[h] = Math.floor(houses[h] / 30);
  });

  for (let i = 0; i < planets.length; i++) {
    const p = planets[i];
    const sign = Math.floor(p / 30);
    const deg = p - sign * 30;
    let point = POINTS[i] || 0;
    
    if (deg < 2 || deg >= 27) point -= 3;
    else if (deg >= 7 && deg <= 18) point += 3;
    
    signs[sign] += point;
    if (sign === hou[0]) sum1 += 1;

    if (deg >= 29 && deg < 30) {
      signs[(sign + 1) % 12] += Math.floor(point / 2);
    } else if (deg >= 0 && deg < 1) {
      signs[(sign + 11) % 12] += Math.floor(point / 2);
    }
  }

  if (sum1 === 1) {
    signs[hou[0]] += 5;
  } else {
    signs[hou[0]] += 3 * sum1;
  }
  
  return resolveDyn(signs);
}

export function houseDyn(planets: number[], houses: number[], sizes: number[]) {
  const magick = [0.206, 0.412, 0.6847, 0.745, 0.8727, 0.966];
  const houseD = new Array(12).fill(0);
  
  // simple plan_in_house
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

  for (let i = 0; i < 11; i++) {
    const point = POINTS[i];
    const hou = plinh[i];
    const houplus = (hou + 1) % 12;
    let plus = (hou % 3 === 0) ? 5 : 3;
    
    let p = planets[i] - houses[hou];
    if (p < 0) p += 360;
    
    const zone = new Array(6).fill(0);
    for (let j = 0; j < 6; j++) {
      zone[j] = sizes[hou] * magick[j];
    }
    
    if (p < zone[0]) {
      houseD[hou] += (point + plus);
    } else if (p < zone[1]) {
      houseD[hou] += point;
    } else if (p < zone[2]) {
      houseD[hou] += (point - 3);
    } else if (p < zone[3]) {
      houseD[hou] += (point - 3);
      houseD[houplus] += (point - 3);
    } else if (p < zone[4]) {
      houseD[hou] += point;
      houseD[houplus] += point;
    } else if (p < zone[5]) {
      plus = (houplus % 3 === 0) ? 5 : 3;
      houseD[hou] += (point + plus);
      houseD[houplus] += (point + plus);
    } else {
      plus = (houplus % 3 === 0) ? 5 : 3;
      houseD[houplus] += (point + plus);
    }
  }
  
  return resolveDyn(houseD);
}

export function calculateDynamics(planets: number[], houses: number[], sizes: number[]) {
  const sd = signDyn(planets, houses);
  const hd = houseDyn(planets, houses, sizes);

  return {
    signs: sd,
    houses: hd,
  };
}
