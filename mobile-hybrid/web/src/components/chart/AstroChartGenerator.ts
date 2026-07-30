export interface ChartGeneratorOptions {
  width?: number;
  height?: number;
  isTransit?: boolean;
}

export function generateChartSvg(data: any, options: ChartGeneratorOptions = {}): string {
  const { isTransit = false } = options;
  const SIZE = 1000;
  const CX = SIZE / 2;
  const CY = SIZE / 2;
  const RADIUS = SIZE / 2 - 40;

  const OFFSET = data.houses ? data.houses[0] : 0;

  // Astro-Nex Python: HouseChart.get_offset() siempre devuelve 0 (la carta
  // de Casas no rota con el ascendente: la cuspide AC se fija arriba/abajo
  // segun convencion y todas las casas quedan iguales a 30 grados). Todos
  // los datos de planetas ya llegan transformados a "espacio de casas"
  // (house_plan_long) desde chartTypes.ts/engine.worker.ts, por lo que aqui
  // solo necesitamos anular el offset del ascendente para este modo.
  const isHouseChart = data.chartType === 'draw_house';
  const BASE_OFFSET = isHouseChart ? 0 : OFFSET;

  const PLANET_COLORS = ['#ff8000', '#ff8000', '#0000ff', '#0000ff', '#0000ff', '#0000ff', '#ff8000', '#9900cc', '#9900cc', '#009900', '#9900cc'];
  const PLANET_GLYPHS = ['d', 'f', 'h', 'j', 'k', 'l', 'g', 'z', 'x', 'c', 'v'];

  const ASP_COLOR: Record<string, string> = {
    red: '#ee0000',
    blue: '#0000f7',
    green: '#00cc00',
    orange: '#ff8000'
  };

  const CUSP_NAMES = ['AC', '2', '3', 'IC', '5', '6', 'DC', '8', '9', 'MC', '11', '12'];
  const CUSP_COLORS = ['#b30033', '#1a1a99', '#00991a', '#b30033', '#1a1a99', '#00991a', '#b30033', '#1a1a99', '#00991a', '#b30033', '#1a1a99', '#00991a'];

  function normDeg(d: number) { let n = d % 360; if (n < 0) n += 360; return n; }

  function polar(r: number, deg: number, offset = BASE_OFFSET) {
    const visual = normDeg(180 - deg + offset);
    const rad = visual * Math.PI / 180;
    return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
  }

  let svgParts: string[] = [];

  svgParts.push(`<rect x="0" y="0" width="${SIZE}" height="${SIZE}" fill="#ffffff"/>`);

  // --- Rings
  const outerR = isTransit ? RADIUS * 0.99 : RADIUS * 0.84; // R_RULED_MID (Outer boundary for ticks)
  const midR = isTransit ? RADIUS * 0.93 : RADIUS * 0.78; // R_RULED_OUTER (Separates signs from degree marks)
  const innerR = isTransit ? RADIUS * 0.80 : RADIUS * 0.65; // R_RULED_INNER (Inner boundary for zodiac)
  const planetRingOuter = RADIUS * 0.48; // R_INNER
  const aspR = RADIUS * 0.435; // R_ASP

  let natalPlanetR = isTransit ? (RADIUS * 0.48 + (RADIUS * 0.80 - RADIUS * 0.48) / 4) : (RADIUS * 0.48 + (RADIUS * 0.65 - RADIUS * 0.48) / 2);
  let transitPlanetR = isTransit ? (RADIUS * 0.48 + 3 * (RADIUS * 0.80 - RADIUS * 0.48) / 4) : 0;

  svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${outerR}" fill="none" stroke="#999" stroke-width="0.5"/>`);
  svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${midR}" fill="none" stroke="#999" stroke-width="0.5"/>`);
  svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${planetRingOuter}" fill="none" stroke="#999" stroke-width="0.5"/>`);
  svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${innerR}" fill="none" stroke="#999" stroke-width="0.5" stroke-dasharray="2,3"/>`);

  // En la carta de Casas los limites de signo no caen cada 30 grados exactos:
  // se deforman segun house_sign_long (houseSignCusps), calculado en el
  // worker, para que el anillo zodiacal se comprima/estire dentro de las
  // casas reales desiguales, igual que en Astro-Nex Python.
  const signBoundaryDegs: number[] = isHouseChart && data.houseSignCusps
    ? data.houseSignCusps
    : (() => {
      const ascSign = Math.floor(OFFSET / 30);
      const firstBoundary = ascSign * 30;
      return Array.from({ length: 12 }, (_, h) => firstBoundary + h * 30);
    })();

  for (let h = 0; h < 12; h++) {
    const boundaryDeg = signBoundaryDegs[h];
    const p1 = polar(outerR, boundaryDeg);
    const p2 = polar(innerR, boundaryDeg); // Boundaries go from 0.84 down to 0.65
    svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="#000" stroke-width="0.5"/>`);
  }

  for (let i = 0; i < 360; i++) {
    const inInsets: Record<number, number> = { 0: -RADIUS * 0.018, 5: -RADIUS * 0.012 };
    const inInset = inInsets[i % 10] ?? -RADIUS * 0.004;
    const pI1 = polar(outerR, i);
    const pI2 = polar(outerR + inInset, i);
    svgParts.push(`<line x1="${pI1.x}" y1="${pI1.y}" x2="${pI2.x}" y2="${pI2.y}" stroke="#000" stroke-width="0.5"/>`);
  }

  // Astro-Nex Python: HouseChart hereda de EqualHousesChart, cuyas
  // get_cusps_offsets()/get_sizes() fijan casas iguales de 30 grados en
  // lugar de las cuspides reales desiguales. Se usa tanto para las lineas
  // de anios (Age Point) como para las cuspides visibles mas abajo.
  const houseCuspDegs: number[] = isHouseChart
    ? Array.from({ length: 12 }, (_, i) => i * 30)
    : data.houses;

  if (data.houses) {
    const yearLabelRadius = outerR + RADIUS * 0.045;
    let currentYear = data.birthYear || 1888;

    for (let h = 0; h < 12; h++) {
      currentYear += 1;
      const off = houseCuspDegs[h];
      const nextOff = houseCuspDegs[(h + 1) % 12];
      let size = off - nextOff;
      if (size < 0) size += 360;

      const ysize = size / 6;

      for (let j = 1; j <= 5; j++) {
        const angle = normDeg(off - ysize * j);
        const tickLen = (j === 5) ? 8 : 4;
        const p1 = polar(outerR, angle);
        const p2 = polar(outerR + tickLen, angle);
        svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="#666" stroke-width="0.5"/>`);

        if (j === 4) {
          const yrText = String(currentYear).slice(-2);
          const pT = polar(yearLabelRadius, angle);

          const visualAngle = normDeg(180 - angle + BASE_OFFSET);
          let textRot = visualAngle - 90;
          if (textRot < -90) textRot += 180;
          if (textRot > 90) textRot -= 180;

          svgParts.push(`<text x="${pT.x}" y="${pT.y}" fill="#666" font-size="${RADIUS * 0.024}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${-textRot} ${pT.x} ${pT.y})">${yrText}</text>`);
        }
        currentYear += 1;
      }
      currentYear -= 1;
    }
  }

  const ZODIAC_GLYPHS_LIST = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's'];
  const ZODIAC_COLORS_LIST = [ASP_COLOR.red, ASP_COLOR.green, '#FFD700', ASP_COLOR.blue];
  const glyphFontSize = RADIUS * 0.12;
  const signR = innerR + (midR - innerR) / 2; // Between 0.65 and 0.78
  const degreeLabelR = midR + (outerR - midR) / 2; // Between 0.78 and 0.84

  for (let i = 0; i < 12; i++) {
    const startDeg = signBoundaryDegs[i];
    let nextDeg = signBoundaryDegs[(i + 1) % 12];
    if (nextDeg < startDeg) nextDeg += 360;
    // Punto medio del segmento (deformado en la carta de Casas, de 30 grados
    // exactos en el resto de las cartas).
    const mid = normDeg((startDeg + nextDeg) / 2);
    const zodiacIdx = i;

    const p = polar(signR, mid);
    const visualAngle = normDeg(180 - mid + BASE_OFFSET);

    let textRot = visualAngle + 90;
    svgParts.push(`<text x="${p.x}" y="${p.y}" fill="${ZODIAC_COLORS_LIST[zodiacIdx % 4]}" font-size="${glyphFontSize}" text-anchor="middle" dominant-baseline="central" font-family="Astro-Nex" font-weight="normal" transform="rotate(${textRot} ${p.x} ${p.y})">${ZODIAC_GLYPHS_LIST[zodiacIdx]}</text>`);

    // Draw 10 and 20 degree marks (proportionally placed within the warped segment)
    [10, 20].forEach(fraction => {
      const deg = normDeg(startDeg + (nextDeg - startDeg) * (fraction / 30));
      const pDeg = polar(degreeLabelR, deg);
      const vAngle = normDeg(180 - deg + BASE_OFFSET);
      let tRot = vAngle + 90;
      svgParts.push(`<text x="${pDeg.x}" y="${pDeg.y}" fill="#666" font-size="${RADIUS * 0.035}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${tRot} ${pDeg.x} ${pDeg.y})">${fraction}</text>`);
    });
  }

  if (data.houses) {
    const lineEnd = outerR + RADIUS * 0.08;
    const textRad = lineEnd * 1.01;

    for (let i = 0; i < 12; i++) {
      const hDeg = houseCuspDegs[i];
      const isCardinal = (i % 3 === 0);
      const p1 = polar(outerR, hDeg);
      const p2 = polar(lineEnd, hDeg);
      const sw = isCardinal ? 0.6 : 0.5;
      svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${CUSP_COLORS[i]}" stroke-width="${sw}"/>`);

      const label = CUSP_NAMES[i];
      let hTextRad = textRad;
      let tColor = CUSP_COLORS[i];

      const visualAngle = normDeg(180 - hDeg + BASE_OFFSET);
      let textRot = visualAngle - 90;
      if (textRot < -90) textRot += 180;
      if (textRot > 90) textRot -= 180;

      if (isCardinal) {
        textRot = 0;
        hTextRad += RADIUS * 0.035;
      }

      const hP = polar(hTextRad, hDeg);
      svgParts.push(`<text x="${hP.x}" y="${hP.y}" fill="${tColor}" font-size="${RADIUS * 0.035}" font-weight="bold" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${-textRot} ${hP.x} ${hP.y})">${label}</text>`);
    }
  }

  const drawAspects = (aspects: any[], pList1: any[], pList2: any[], opacity: string) => {
    const REAL_ASP_R = RADIUS * 0.435;
    for (const asp of aspects) {
      const p1d = pList1.find((p: any) => (p.index ?? p.ix) === asp.p1);
      const p2d = pList2.find((p: any) => (p.index ?? p.ix) === asp.p2);
      if (!p1d || !p2d) continue;

      const p1 = polar(REAL_ASP_R, p1d.longitude);
      const p2 = polar(REAL_ASP_R, p2d.longitude);

      let color = '#ccc';

      const ASPECT_NAMES: Record<number, string> = {
        0: 'conj', 1: 'semi', 2: 'sext', 3: 'cuad', 4: 'trig', 5: 'quinc',
        6: 'opos', 7: 'quinc', 8: 'trig', 9: 'cuad', 10: 'sext', 11: 'semi'
      };
      const name = asp.name || ASPECT_NAMES[asp.a];

      if (['cuad', 'opos'].includes(name)) { color = ASP_COLOR.red; }
      else if (['trig', 'sext'].includes(name)) { color = ASP_COLOR.blue; }
      else if (['quinc', 'semi'].includes(name)) { color = ASP_COLOR.green; }
      if (name === 'conj') continue;

      let dis = Math.abs(p1d.longitude - p2d.longitude);
      if (dis > 180) dis = 360 - dis;

      const exactAngles: Record<string, number> = { 'conj': 0, 'semi': 30, 'sext': 60, 'cuad': 90, 'trig': 120, 'quinc': 150, 'opos': 180 };
      const exact = exactAngles[name] || 0;
      const trueOrb = Math.abs(dis - exact);

      const PLANET_CLASS: Record<number, number> = {
        0: 0, 1: 0,
        2: 1, 3: 1, 5: 1,
        4: 2, 6: 2,
        7: 3, 8: 3, 9: 3,
        10: 4
      };
      const ASP_CLASS: Record<string, number> = { 'semi': 0, 'sext': 1, 'quinc': 1, 'cuad': 2, 'trig': 3, 'conj': 4, 'opos': 4 };
      const ORB_TABLE = [
        [3.0, 5.0, 6.0, 8.0, 9.0],
        [2.0, 4.0, 5.0, 6.0, 7.0],
        [1.5, 3.0, 4.0, 5.0, 6.0],
        [1.0, 2.0, 3.0, 4.0, 5.0],
        [1.0, 2.0, 2.0, 3.0, 4.0]
      ];

      const pc1 = PLANET_CLASS[asp.p1] ?? 3;
      const pc2 = PLANET_CLASS[asp.p2] ?? 3;
      const acl = ASP_CLASS[name] ?? 0;

      const orb1 = ORB_TABLE[pc1][acl];
      const orb2 = ORB_TABLE[pc2][acl];

      let f1 = asp.f1 !== undefined ? asp.f1 : (trueOrb / orb1);
      let f2 = asp.f2 !== undefined ? asp.f2 : (trueOrb / orb2);
      let isUnilateral = f1 > 1.0 || f2 > 1.0;

      const x1 = p1.x; const y1 = p1.y;
      const x2 = p2.x; const y2 = p2.y;

      const p1_outer = polar(planetRingOuter, p1d.longitude);
      const p2_outer = polar(planetRingOuter, p2d.longitude);
      svgParts.push(`<line x1="${x1}" y1="${y1}" x2="${p1_outer.x}" y2="${p1_outer.y}" stroke="${color}" stroke-width="0.5" opacity="${opacity}"/>`);
      svgParts.push(`<line x1="${x2}" y1="${y2}" x2="${p2_outer.x}" y2="${p2_outer.y}" stroke="${color}" stroke-width="0.5" opacity="${opacity}"/>`);

      if (isUnilateral) {
        let fX1 = x1, fY1 = y1, fX2 = x2, fY2 = y2;
        if (f1 < f2) {
          fX1 = x2; fY1 = y2; fX2 = x1; fY2 = y1;
        }
        const xx = (fX1 + fX2) / 2;
        const yy = (fY1 + fY2) / 2;
        const strokeW = 0.55;

        svgParts.push(`<line x1="${fX1}" y1="${fY1}" x2="${xx}" y2="${yy}" stroke="${color}" stroke-width="${strokeW}" stroke-dasharray="4,3,12,4,18,5,24,6,30,6,36,6,48,6,60,6" class="aspect-line unilateral-dashed" opacity="${opacity}"/>`);
        svgParts.push(`<line x1="${xx}" y1="${yy}" x2="${fX2}" y2="${fY2}" stroke="${color}" stroke-width="${strokeW}" class="aspect-line unilateral-solid" opacity="${opacity}"/>`);
      } else {
        const xx = (x1 + x2) / 2;
        const yy = (y1 + y2) / 2;
        const angle = Math.atan2(y2 - y1, x2 - x1);

        const aspRadius = RADIUS * 0.435;
        const scl = aspRadius * 0.00065;
        const f = 3 * ((5 - 5 * f1) + (5 - 5 * f2)) * scl;
        const pDx = Math.cos(angle + Math.PI / 2) * f;
        const pDy = Math.sin(angle + Math.PI / 2) * f;

        const pathData = `M ${x1} ${y1} C ${xx + pDx} ${yy + pDy}, ${xx + pDx} ${yy + pDy}, ${x2} ${y2} C ${xx - pDx} ${yy - pDy}, ${xx - pDx} ${yy - pDy}, ${x1} ${y1} Z`;
        svgParts.push(`<path d="${pathData}" fill="${color}" stroke="${color}" stroke-width="0.55" class="aspect-line fusus" opacity="${opacity}"/>`);
      }
    }
  };

  if (data.aspects && data.planets) {
    drawAspects(data.aspects, data.planets, data.planets, isTransit ? "0.5" : "1.0");
  }
  if (isTransit && data.interAspects && data.planets && data.transitPlanets) {
    drawAspects(data.interAspects, data.planets, data.transitPlanets, "1.0");
  }

  const drawPlanets = (planets: any[], targetR: number, isOuterRing: boolean) => {
    const correctShift = (corr: number) => corr;
    const sortedPlanets = [...planets].sort((a, b) => a.longitude - b.longitude);
    const cells: any[][] = [];
    if (sortedPlanets.length > 0) {
      let currentCell = [sortedPlanets[0]];
      for (let i = 1; i < sortedPlanets.length; i++) {
        const prev = sortedPlanets[i - 1];
        const curr = sortedPlanets[i];
        if (normDeg(curr.longitude - prev.longitude) <= 6.5) {
          currentCell.push(curr);
        } else {
          cells.push(currentCell);
          currentCell = [curr];
        }
      }
      if (cells.length > 0) {
        const first = cells[0][0];
        const last = currentCell[currentCell.length - 1];
        if (normDeg(first.longitude - last.longitude) <= 6.5) {
          cells[0] = [...currentCell, ...cells[0]];
        } else {
          cells.push(currentCell);
        }
      } else {
        cells.push(currentCell);
      }
    }

    const displayData = new Map();
    cells.forEach(cell => {
      const numPlans = cell.length;
      let fac = [0.93, 1.07];

      cell.forEach((p, pos) => {
        let radFac = 1.0;
        let corr = 0.0;
        if (numPlans >= 2) {
          radFac = fac[0];
          fac = [fac[1], fac[0]];
        }
        if (numPlans >= 3) {
          const faraway = pos - Math.floor(numPlans / 2);
          let diff = 0;
          if (faraway < 0) {
            diff = normDeg(cell[pos + 1].longitude - p.longitude);
          } else if (faraway > 0) {
            diff = normDeg(p.longitude - cell[pos - 1].longitude);
            if (diff >= 353.5) {
              diff = -(diff - 353.5);
              radFac = fac[0];
            }
          }
          corr = correctShift(-faraway * (6.5 - diff) / 2.5);
        }
        const index = p.index ?? p.ix;
        displayData.set(index, {
          displayDegree: normDeg(p.longitude + corr),
          radFac: radFac
        });
      });
    });

    planets.forEach((p: any) => {
      const index = p.index ?? p.ix;
      const dData = displayData.get(index) || { displayDegree: p.longitude, radFac: 1.0 };
      const actualR = targetR * dData.radFac;

      const pTrueInner = polar(aspR, p.longitude);
      const pTrueOuter = polar(planetRingOuter, p.longitude);
      const pGlyph = polar(actualR, dData.displayDegree);
      const color = PLANET_COLORS[index] || '#000';

      if (!isOuterRing) {
        svgParts.push(`<line x1="${pTrueInner.x}" y1="${pTrueInner.y}" x2="${pTrueOuter.x}" y2="${pTrueOuter.y}" stroke="${color}" stroke-width="${0.85}"/>`);
      } else {
        svgParts.push(`<line x1="${pTrueInner.x}" y1="${pTrueInner.y}" x2="${pTrueOuter.x}" y2="${pTrueOuter.y}" stroke="${color}" stroke-width="${0.85}" opacity="0.3"/>`);
      }

      const glyph = PLANET_GLYPHS[index] || '?';
      svgParts.push(`<text x="${pGlyph.x}" y="${pGlyph.y}" fill="${color}" font-family="Astro-Nex" font-size="${RADIUS * 0.065}" text-anchor="middle" dominant-baseline="central">${glyph}</text>`);
    });
  };

  if (data.planets) {
    drawPlanets(data.planets, natalPlanetR, false);
  }
  if (isTransit && data.transitPlanets) {
    drawPlanets(data.transitPlanets, transitPlanetR, true);
  }

  svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${RADIUS * 0.065}" fill="none" stroke="#ccc" stroke-width="0.5"/>`);

  return svgParts.join('\n');
}
