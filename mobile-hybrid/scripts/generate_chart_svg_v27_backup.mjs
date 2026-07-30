#!/usr/bin/env node
/**
 * Genera un SVG de carta astrologica con los estilos correctos de Astro-Nex
 * usando el golden fixture y lo escribe en comparisons/app_chart_new.svg
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const goldenPath = join(__dirname, '../tests/golden/natal_output.json');
const data = JSON.parse(readFileSync(goldenPath, 'utf8'));

// ============================================================
// Constantes replicando Astro-Nex (Python/Cairo)
// ============================================================
const SIZE = 1000;
const CX = SIZE / 2;
const CY = SIZE / 2;
const RADIUS = SIZE / 2 - 40;

// Ascendente como offset (house[0])
const OFFSET = data.houses[0];

// Radios normalizados (igual que en React)
// Fix #11 & #15: Tres anillos zodiacales (Astro-Nex)
const R_RULED_MID   = 0.84;
const R_RULED_OUTER = 0.78;
const R_RULED_INNER = 0.65;
const R_INNER = 0.48;
const R_PL = 0.565; // Restore to original since band is back to normal

// Colores del zodiaco: Fuego, Tierra, Aire, Agua (CORRECTO Astro-Nex)
const ZODIAC_COLORS = ['#de3535','#57c468','#f7ef82','#b7b7e5'];
const PLANET_COLORS = ['#ff8000','#ff8000','#0000ff','#0000ff','#0000ff','#0000ff','#ff8000','#9900cc','#9900cc','#009900','#9900cc'];

// Glyphs Astro-Nex font (mapped chars)
const ZODIAC_GLYPHS = ['q','w','e','r','t','y','u','i','o','p','a','s'];
const PLANET_GLYPHS = ['d','f','h','j','k','l','g','z','x','c','v'];

// Aspect colors
const ASP_COLOR = {
  red: '#ee0000',
  blue: '#0000f7',
  green: '#00cc00',
  orange: '#ff8000'
};

// House cusp labels & colors
const CUSP_NAMES  = ['AC','2','3','IC','5','6','DC','8','9','MC','11','12'];
const CUSP_COLORS = ['#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a'];

// ============================================================
// Helpers
// ============================================================
function normDeg(d) { let n = d % 360; if(n<0) n+=360; return n; }

function polar(r, deg, offset=OFFSET) {
  const visual = normDeg(180 - deg + offset);
  const rad = visual * Math.PI / 180;
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}

function angDist(a, b) { let d = Math.abs(a-b)%360; return d>180 ? 360-d : d; }

// ============================================================
// Build SVG pieces
// ============================================================
let svgParts = [];

// Background
svgParts.push(`<rect x="0" y="0" width="${SIZE}" height="${SIZE}" fill="#ffffff"/>`);

// --- Zodiac wheel rings
const outerR = RADIUS * 0.80; // R_YEARS (Zodiac outer boundary / year ring)
const midR   = RADIUS * 0.65; // R_RULEDINNER (Zodiac inner boundary, dashed)
const innerR = RADIUS * 0.48; // R_INNER (Planet inner boundary / Aspects outer boundary)
const aspR   = RADIUS * 0.435; // R_ASP

// Draw the 0.48 and 0.80 solid circles
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${outerR}" fill="none" stroke="#999" stroke-width="0.5"/>`);
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${innerR}" fill="none" stroke="#999" stroke-width="0.5"/>`);

// Draw the 0.65 dashed circle (zodiac inner boundary / ruler)
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${midR}" fill="none" stroke="#999" stroke-width="0.5" stroke-dasharray="2,3"/>`);

// --- Sign boundaries anchored to ascendant sign (Astro-Nex logic)
// get_offset = houses[0] % 30 (degrees inside the ascendant's sign)
// sign boundary starts at: 30*h - offset  (absolute ecliptic degree of each sign boundary)
const SIGN_OFFSET = OFFSET % 30;  // e.g. 213.43 % 30 = 3.43
const ASC_SIGN    = Math.floor(OFFSET / 30);  // 213/30 = 7 → Scorpio
// The first sign boundary in the wheel is the start of the ascendant's sign
const FIRST_BOUNDARY = ASC_SIGN * 30;  // e.g. 7*30 = 210°
for(let h=0; h<12; h++) {
  const boundaryDeg = FIRST_BOUNDARY + h * 30;  // ecliptic degree of each boundary
  const p1 = polar(outerR, boundaryDeg); // Sign boundaries go from outerR (0.80)
  const p2 = polar(midR, boundaryDeg); // ONLY to midR (0.65), they do NOT enter the planet ring!
  svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="#000" stroke-width="0.5"/>`);
}

// --- Ruler ticks (On the outerR 0.80 ring pointing inwards!)
for(let i=0; i<360; i++) {
  const inInsets = { 0: -RADIUS*0.018, 5: -RADIUS*0.012 };
  const inInset = inInsets[i%10] ?? -RADIUS*0.004;
  const pI1 = polar(outerR, i); // ticks on outerR (0.80)
  const pI2 = polar(outerR + inInset, i); // point inwards!
  svgParts.push(`<line x1="${pI1.x}" y1="${pI1.y}" x2="${pI2.x}" y2="${pI2.y}" stroke="#000" stroke-width="0.5"/>`);
}

// --- Outer Year Lines & Ticks (Huber Age Point logic: 6 years per house)
const yearLabelRadius = outerR + RADIUS * 0.045;
let startYear = 1888; 
let currentYear = startYear;

for (let h = 0; h < 12; h++) {
  currentYear += 1;
  const off = data.houses[h];
  const nextOff = data.houses[(h+1)%12];
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
      
      const visualAngle = normDeg(180 - angle + OFFSET);
      let textRot = visualAngle - 90;
      if (textRot < -90) textRot += 180;
      if (textRot > 90) textRot -= 180;
      
      svgParts.push(`<text x="${pT.x}" y="${pT.y}" fill="#666" font-size="${RADIUS*0.024}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${-textRot} ${pT.x} ${pT.y})">${yrText}</text>`);
    }
    currentYear += 1;
  }
  currentYear -= 1;
}

// --- Zodiac Signs
const ZODIAC_GLYPHS_LIST = ['q','w','e','r','t','y','u','i','o','p','a','s'];
const ZODIAC_COLORS_LIST = [ASP_COLOR.red, ASP_COLOR.green, ASP_COLOR.blue, '#FFD700'];
const glyphFontSize = RADIUS * 0.14; 
const signR = RADIUS * 0.725; // Centered between 0.65 and 0.80

for(let i=0; i<12; i++) {
  const startDeg = i * 30;
  const mid = startDeg + 15;
  const zodiacIdx = i;



  const p = polar(signR, mid);
  const visualAngle = normDeg(180 - mid + OFFSET);
  
  let textRot = visualAngle + 90;
  svgParts.push(`<text x="${p.x}" y="${p.y}" fill="${ZODIAC_COLORS_LIST[zodiacIdx%4]}" font-size="${glyphFontSize}" text-anchor="middle" dominant-baseline="central" font-family="Astro-Nex" font-weight="normal" transform="rotate(${textRot} ${p.x} ${p.y})">${ZODIAC_GLYPHS_LIST[zodiacIdx]}</text>`);
}

// --- House cusps
const lineEnd = outerR + RADIUS * 0.08; // House lines extend OUTWARDS past the year ring!
const textRad = lineEnd * 1.01; // Numbers are placed just outside the line ends

for(let i=0; i<12; i++) {
  const hDeg = data.houses[i];
  
  // All house lines only go inwards to outerR (0.80)! They do NOT go into the chart.
  const isCardinal = (i % 3 === 0);
  const p1 = polar(outerR, hDeg);
  const p2 = polar(lineEnd, hDeg);
  const sw = isCardinal ? 0.6 : 0.5;
  svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${CUSP_COLORS[i]}" stroke-width="${sw}"/>`);
  
  // House labels (AC, 2, 3, IC, etc.)
  const label = CUSP_NAMES[i];
  let hTextRad = textRad;
  let tColor = CUSP_COLORS[i];
  
  // Astro-Nex text orientation
  const visualAngle = normDeg(180 - hDeg + OFFSET);
  let textRot = visualAngle - 90;
  if (textRot < -90) textRot += 180;
  if (textRot > 90) textRot -= 180;
  
  if (isCardinal) {
    // Cardinal texts are always horizontal in Astro-Nex
    textRot = 0;
    
    // Draw the red semi-circle at the end of the tick (lineEnd)
    const arcRad = RADIUS * 0.025;
    const hRot = visualAngle + 180;
    svgParts.push(`<path d="M 0,${-arcRad} A ${arcRad},${arcRad} 0 0,1 0,${arcRad} Z" fill="#cc0000" transform="translate(${p2.x}, ${p2.y}) rotate(${hRot})"/>`);
    
    // Push the text further out so it doesn't overlap the semi-circle
    hTextRad += arcRad * 1.5;
  }
  
  const hP = polar(hTextRad, hDeg);
  svgParts.push(`<text x="${hP.x}" y="${hP.y}" fill="${tColor}" font-size="${RADIUS*0.035}" font-weight="bold" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${-textRot} ${hP.x} ${hP.y})">${label}</text>`);
}

// --- Aspect lines (FususAspect - Fix: Curvas de Bézier rellenas como en Astro-Nex)
const REAL_ASP_R = RADIUS * 0.435;
for(const asp of data.aspects) {
  const p1d = data.planets.find(p => p.index === asp.p1);
  const p2d = data.planets.find(p => p.index === asp.p2);
  if(!p1d || !p2d) continue;

  const p1 = polar(REAL_ASP_R, p1d.longitude);
  const p2 = polar(REAL_ASP_R, p2d.longitude);

  let color = '#ccc';
  const name = asp.name;
  if(['cuad','opos'].includes(name))        { color = ASP_COLOR.red; }
  else if(['trig','sext'].includes(name))   { color = ASP_COLOR.blue; }
  else if(['quinc','semi'].includes(name))  { color = ASP_COLOR.green; }
  if(name === 'conj') continue; // Conjunctions are not drawn across the center
  
  // Calculate true orb from planetary positions
  let dis = Math.abs(p1d.longitude - p2d.longitude);
  if (dis > 180) dis = 360 - dis;
  
  const exactAngles = { 'conj': 0, 'semi': 30, 'sext': 60, 'cuad': 90, 'trig': 120, 'quinc': 150, 'opos': 180 };
  const exact = exactAngles[name] || 0;
  const trueOrb = Math.abs(dis - exact);

  // Huber exact orb tables based on planet class and aspect class
  const PLANET_CLASS = {
    0: 0, 1: 0,       // Sun, Moon
    2: 1, 3: 1, 5: 1, // Mercury, Venus, Mars
    4: 2, 6: 2,       // Jupiter, Saturn
    7: 3, 8: 3, 9: 3, // Uranus, Neptune, Pluto
    10: 4             // Node
  };
  const ASP_CLASS = { 'semi': 0, 'sext': 1, 'quinc': 1, 'cuad': 2, 'trig': 3, 'conj': 4, 'opos': 4 };
  const ORB_TABLE = [
    [3.0, 5.0, 6.0, 8.0, 9.0], // Sun/Moon
    [2.0, 4.0, 5.0, 6.0, 7.0], // Merc/Ven/Mars
    [1.5, 3.0, 4.0, 5.0, 6.0], // Jup/Sat
    [1.0, 2.0, 3.0, 4.0, 5.0], // Ura/Nep/Plu
    [1.0, 2.0, 2.0, 3.0, 4.0]  // Node
  ];

  const pc1 = PLANET_CLASS[asp.p1] ?? 3;
  const pc2 = PLANET_CLASS[asp.p2] ?? 3;
  const acl = ASP_CLASS[name] ?? 0;
  
  const orb1 = ORB_TABLE[pc1][acl];
  const orb2 = ORB_TABLE[pc2][acl];

  // Calculate Huber f1 and f2 for exactness
  let f1 = trueOrb / orb1;
  let f2 = trueOrb / orb2;
  let isUnilateral = f1 > 1.0 || f2 > 1.0;

  const x1 = p1.x; const y1 = p1.y;
  const x2 = p2.x; const y2 = p2.y;

  // Thin line connecting the planet (aspR=0.48) to the fusus start (REAL_ASP_R=0.435)
  const p1_outer = polar(aspR, p1d.longitude);
  const p2_outer = polar(aspR, p2d.longitude);
  svgParts.push(`<line x1="${x1}" y1="${y1}" x2="${p1_outer.x}" y2="${p1_outer.y}" stroke="${color}" stroke-width="0.5"/>`);
  svgParts.push(`<line x1="${x2}" y1="${y2}" x2="${p2_outer.x}" y2="${p2_outer.y}" stroke="${color}" stroke-width="0.5"/>`);

  if (isUnilateral) {
    // UnilateralAspect (Half dashed, half solid based on weakness)
    let fX1 = x1, fY1 = y1, fX2 = x2, fY2 = y2;
    if (f1 < f2) {
      fX1 = x2; fY1 = y2; fX2 = x1; fY2 = y1;
    }
    const xx = (fX1 + fX2) / 2;
    const yy = (fY1 + fY2) / 2;
    const strokeW = 0.55; 
    
    // Half 1: Dashed (weak planet to midpoint)
    svgParts.push(`<line x1="${fX1}" y1="${fY1}" x2="${xx}" y2="${yy}" stroke="${color}" stroke-width="${strokeW}" stroke-dasharray="4,3,12,4,18,5,24,6,30,6,36,6,48,6,60,6" class="aspect-line unilateral-dashed"/>`);
    // Half 2: Solid (midpoint to strong planet)
    svgParts.push(`<line x1="${xx}" y1="${yy}" x2="${fX2}" y2="${fY2}" stroke="${color}" stroke-width="${strokeW}" class="aspect-line unilateral-solid"/>`);
  } else {
    // FususAspect (Solid, dynamic spindle)
    const xx = (x1 + x2) / 2;
    const yy = (y1 + y2) / 2;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    // Astro-Nex Fusus Aspect logic (dynamic width based on exactness)
    const aspRadius = RADIUS * 0.435;
    const scl = aspRadius * 0.00065;
    const f = 3 * ((5 - 5 * f1) + (5 - 5 * f2)) * scl; 
    const pDx = Math.cos(angle + Math.PI/2) * f;
    const pDy = Math.sin(angle + Math.PI/2) * f;
    
    const pathData = `M ${x1} ${y1} C ${xx+pDx} ${yy+pDy}, ${xx+pDx} ${yy+pDy}, ${x2} ${y2} C ${xx-pDx} ${yy-pDy}, ${xx-pDx} ${yy-pDy}, ${x1} ${y1} Z`;
    svgParts.push(`<path d="${pathData}" fill="${color}" stroke="${color}" stroke-width="0.55" class="aspect-line fusus"/>`);
  }
}

// --- Planets (with spread algorithm)
// Replicates Astro-Nex correct_shift
const correctShift = (corr) => corr;

// 1. Sort planets
const sortedPlanets = [...data.planets].sort((a, b) => a.longitude - b.longitude);

// 2. Identify overlapping clusters (Marshalling)
const cells = [];
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

// 3. Inject Plan Degrees
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
    displayData.set(p.index, {
      displayDegree: normDeg(p.longitude + corr),
      radFac: radFac
    });
  });
});

data.planets.forEach((p) => {
  const dData = displayData.get(p.index) || { displayDegree: p.longitude, radFac: 1.0 };
  const actualR = RADIUS * R_PL * dData.radFac;
  
  const pTrueInner = polar(REAL_ASP_R, p.longitude); // Connect from aspect node (0.435)
  const pTrueOuter = polar(innerR, p.longitude);     // Connect to inner circle (0.48)
  const pGlyph = polar(actualR, dData.displayDegree);
  const color = PLANET_COLORS[p.index] || '#000';
  
  // Tick
  svgParts.push(`<line x1="${pTrueInner.x}" y1="${pTrueInner.y}" x2="${pTrueOuter.x}" y2="${pTrueOuter.y}" stroke="${color}" stroke-width="${0.85}"/>`);
  
  const glyph = PLANET_GLYPHS[p.index] || '?';
  // Astro-Nex original: planets are smaller (0.065 instead of 0.09)
  svgParts.push(`<text x="${pGlyph.x}" y="${pGlyph.y}" fill="${color}" font-family="Astro-Nex" font-size="${RADIUS * 0.065}" text-anchor="middle" dominant-baseline="central">${glyph}</text>`);
});

// Small center circle (clean, no text, no arrow)
// Astro-Nex original R_VERYINNER is 0.065 and it's empty
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${RADIUS*0.065}" fill="none" stroke="#ccc" stroke-width="0.5"/>`);

// ============================================================
// Compose SVG
// ============================================================
const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}">
  <style>text { user-select: none; }</style>
  ${svgParts.join('\n  ')}
</svg>`;

const outSvg = join(__dirname, '../comparisons/app_chart.svg');
writeFileSync(outSvg, svg, 'utf8');
console.log('SVG generado en:', outSvg);
