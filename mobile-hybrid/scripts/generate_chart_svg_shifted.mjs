#!/usr/bin/env node
/**
 * Genera un SVG de carta astrologica con los estilos correctos de Astro-Nex
 * usando el golden fixture y lo escribe en comparisons/app_chart_new.svg
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const goldenPath = join(__dirname, '../tests/golden/natal_output_shifted.json');
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
const midR   = RADIUS * R_RULED_MID;
const outerR = RADIUS * R_RULED_OUTER;
const innerR = RADIUS * R_RULED_INNER;
const aspR   = RADIUS * R_INNER;
const plR    = RADIUS * R_PL;

svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${midR}" fill="none" stroke="#000" stroke-width="0.5"/>`);
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${outerR}" fill="none" stroke="#000" stroke-width="0.5"/>`);
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${innerR}" fill="none" stroke="#000" stroke-width="0.5"/>`);
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${aspR}"   fill="none" stroke="#000" stroke-width="0.5"/>`);

// --- Sign boundaries (every 30 deg, from innerR to midR)
for(let i=0; i<360; i+=30) {
  const p1 = polar(midR, i);
  const p2 = polar(innerR, i);
  svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="#000" stroke-width="0.5"/>`);
}

// --- Ruler ticks
for(let i=0; i<360; i++) {
  // Mid ring ticks (inwards)
  const midInsets = { 0: RADIUS*0.014, 5: RADIUS*0.010 };
  const midInset = midInsets[i%10] ?? RADIUS*0.004;
  const pM1 = polar(midR, i);
  const pM2 = polar(midR - midInset, i);
  svgParts.push(`<line x1="${pM1.x}" y1="${pM1.y}" x2="${pM2.x}" y2="${pM2.y}" stroke="#000" stroke-width="0.5"/>`);

  // Outer ring ticks (inwards)
  const outInsets = { 0: RADIUS*0.016, 5: RADIUS*0.010 };
  const outInset = outInsets[i%10] ?? RADIUS*0.004;
  const pO1 = polar(outerR, i);
  const pO2 = polar(outerR - outInset, i);
  svgParts.push(`<line x1="${pO1.x}" y1="${pO1.y}" x2="${pO2.x}" y2="${pO2.y}" stroke="#000" stroke-width="0.5"/>`);

  // Inner ring ticks (outwards -> negative inset means it adds to radius)
  const inInsets = { 0: -RADIUS*0.018, 5: -RADIUS*0.012 };
  const inInset = inInsets[i%10] ?? -RADIUS*0.004;
  const pI1 = polar(innerR, i);
  const pI2 = polar(innerR - inInset, i);
  svgParts.push(`<line x1="${pI1.x}" y1="${pI1.y}" x2="${pI2.x}" y2="${pI2.y}" stroke="#000" stroke-width="0.5"/>`);
}

// --- Zodiac glyphs (Fix #9: tamaño, Fix #13: rotación, Fix #15: banda de glifos correcta)
const signR = RADIUS * ((R_RULED_INNER + R_RULED_OUTER) / 2);
const glyphFontSize = RADIUS * 0.105; // Slightly smaller to fit perfectly
for(let i=0; i<12; i++) {
  const mid = i*30 + 15;
  const p = polar(signR, mid);
  const visualAngle = normDeg(180 - mid + OFFSET);
  let textRot = visualAngle - 90;
  if (textRot < -90) textRot += 180;
  if (textRot > 90) textRot -= 180;
  svgParts.push(`<text x="${p.x}" y="${p.y}" fill="${ZODIAC_COLORS[i%4]}" font-size="${glyphFontSize}" text-anchor="middle" dominant-baseline="central" font-family="Astro-Nex" font-weight="normal" transform="rotate(${-textRot} ${p.x} ${p.y})">${ZODIAC_GLYPHS[i]}</text>`);
}

// --- Degree numbers INSIDE outer ring (Fix #15: banda de grados correcta)
const degLabelR = RADIUS * ((R_RULED_OUTER + R_RULED_MID) / 2);
for(let i=0; i<360; i+=10) {
  const degInSign = i % 30;
  if(degInSign === 0) continue; // skip sign boundaries
  const p = polar(degLabelR, i);
  const visualAngle = normDeg(180 - i + OFFSET);
  let textRot = visualAngle - 90;
  if (textRot < -90) textRot += 180;
  if (textRot > 90) textRot -= 180;
  svgParts.push(`<text x="${p.x}" y="${p.y}" fill="#999" font-size="${RADIUS*0.035}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" transform="rotate(${-textRot} ${p.x} ${p.y})">${degInSign}</text>`);
}

// --- House cusps + AC/MC axis lines
const fcusp = midR * 1.08;

// Flecha del Ascendente (Fix: Replicando el marcador del original)
const arrowSize = RADIUS * 0.02;
const acVisAng = normDeg(180 - data.houses[0] + OFFSET);
const acP = polar(fcusp * 1.02, data.houses[0]);
svgParts.push(`<polygon points="0,0 ${-arrowSize},${-arrowSize/1.5} ${-arrowSize},${arrowSize/1.5}" fill="#cc0000" transform="translate(${acP.x}, ${acP.y}) rotate(${-acVisAng})"/>`);

const mcP = polar(fcusp * 1.02, data.houses[9]);
const icP = polar(fcusp * 1.02, data.houses[3]);
svgParts.push(`<line x1="${mcP.x}" y1="${mcP.y}" x2="${icP.x}" y2="${icP.y}" stroke="#cc0000" stroke-width="0.8"/>`);

for(let i=0; i<12; i++) {
  const hDeg = data.houses[i];
  const p1 = polar(midR, hDeg);
  const p2 = polar(fcusp, hDeg);
  const sw = (i%3===0) ? 0.6 : 0.5;
  svgParts.push(`<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${CUSP_COLORS[i]}" stroke-width="${sw}"/>`);

  let textRad = fcusp * 1.01;
  const pt = polar(textRad, hDeg);
  svgParts.push(`<text x="${pt.x}" y="${pt.y}" fill="${CUSP_COLORS[i]}" font-size="${RADIUS*0.048}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-weight="${i===0?'bold':'normal'}">${CUSP_NAMES[i]}</text>`);
}

// --- Aspect lines (FususAspect - Fix: Curvas de Bézier rellenas como en Astro-Nex)
for(const asp of data.aspects) {
  const p1d = data.planets.find(p => p.index === asp.p1);
  const p2d = data.planets.find(p => p.index === asp.p2);
  if(!p1d || !p2d) continue;

  const p1 = polar(aspR, p1d.longitude);
  const p2 = polar(aspR, p2d.longitude);

  let color = '#ccc';
  const name = asp.name;
  if(['cuad','opos'].includes(name))        { color = ASP_COLOR.red; }
  else if(['trig','sext'].includes(name))   { color = ASP_COLOR.blue; }
  else if(['quinc','semi'].includes(name))  { color = ASP_COLOR.green; }
  if(name === 'conj') continue; // Conjunctions are not drawn across the center
  
  // Simulate f1 and f2 based on the raw "orb" in the json
  // If orb is > 5, we simulate an out-of-orb (Unilateral) aspect
  let f1 = asp.orb > 5.0 ? 1.2 : asp.orb / 5.0;
  let f2 = asp.orb > 5.0 ? 1.2 : asp.orb / 5.0;
  let isUnilateral = f1 > 1.0 || f2 > 1.0;

  const x1 = p1.x; const y1 = p1.y;
  const x2 = p2.x; const y2 = p2.y;

  if (isUnilateral) {
    // UnilateralAspect (Dashed lines)
    svgParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${0.6 * 0.85}" stroke-dasharray="4 3 12 4 18 5 24 6 30 6 36 6 48 6 60 6" class="aspect-line unilateral"/>`);
  } else {
    // FususAspect (Solid, dynamic spindle)
    const xx = (x1 + x2) / 2;
    const yy = (y1 + y2) / 2;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    // Astro-Nex exact dynamic thickness formula
    const scl = RADIUS * 0.00065;
    const f = 3 * ((5 - 5 * f1) + (5 - 5 * f2)) * scl; 
    const pDx = Math.cos(angle + Math.PI/2) * f;
    const pDy = Math.sin(angle + Math.PI/2) * f;
    
    const pathData = `M ${x1} ${y1} C ${xx+pDx} ${yy+pDy}, ${xx+pDx} ${yy+pDy}, ${x2} ${y2} C ${xx-pDx} ${yy-pDy}, ${xx-pDx} ${yy-pDy}, ${x1} ${y1} Z`;
    svgParts.push(`<path d="${pathData}" fill="${color}" stroke="${color}" stroke-width="0.425" class="aspect-line fusus"/>`);
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
  
  const tickInner = RADIUS * innerR;
  const tickOuter = tickInner * 1.03;

  const pGlyph = polar(actualR, dData.displayDegree);
  const pTrueInner = polar(tickInner, p.longitude);
  const pTrueOuter = polar(tickOuter, p.longitude);
  const color = PLANET_COLORS[p.index] || '#000';
  
  // Tick
  svgParts.push(`<line x1="${pTrueInner.x}" y1="${pTrueInner.y}" x2="${pTrueOuter.x}" y2="${pTrueOuter.y}" stroke="${color}" stroke-width="${0.85 * 0.5}"/>`);
  
  const glyph = PLANET_GLYPHS[p.index] || '?';
  svgParts.push(`<text x="${pGlyph.x}" y="${pGlyph.y}" fill="${color}" font-family="Astro-Nex" font-size="${RADIUS * 0.09}" text-anchor="middle" dominant-baseline="central">${glyph}</text>`);
});

// Small center circle (clean, no text, no arrow)
svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${RADIUS*0.12}" fill="#fff" stroke="#ccc" stroke-width="0.5"/>`);

// ============================================================
// Compose SVG
// ============================================================
const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}">
  ${svgParts.join('\n  ')}
</svg>`;

const outSvg = join(__dirname, '../comparisons/app_chart.svg');
writeFileSync(outSvg, svg, 'utf8');
console.log('SVG generado en:', outSvg);
