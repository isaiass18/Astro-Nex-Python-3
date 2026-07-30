const fs = require('fs');

const src = fs.readFileSync('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/scripts/generate_chart_svg.mjs', 'utf8');

let out = `export interface ChartGeneratorOptions {
  width?: number;
  height?: number;
  isTransit?: boolean;
}

export function generateChartSvg(data: any, options: ChartGeneratorOptions = {}): string {
  const { isTransit = false } = options;
  const SIZE = 1000;
  const CX = SIZE / 2;
  const CY = SIZE / 2;
  const RADIUS = SIZE / 2 - 40; // Use exactly what generate_chart_svg.mjs uses!

  const OFFSET = data.houses ? data.houses[0] : 0;

  const R_RULED_MID   = 0.84;
  const R_RULED_OUTER = 0.78;
  const R_RULED_INNER = 0.65;
  const R_INNER = 0.48;
  const R_PL = 0.565;

  const ZODIAC_COLORS = ['#de3535','#57c468','#f7ef82','#b7b7e5'];
  const PLANET_COLORS = ['#ff8000','#ff8000','#0000ff','#0000ff','#0000ff','#0000ff','#ff8000','#9900cc','#9900cc','#009900','#9900cc'];
  const ZODIAC_GLYPHS = ['q','w','e','r','t','y','u','i','o','p','a','s'];
  const PLANET_GLYPHS = ['d','f','h','j','k','l','g','z','x','c','v'];
  const ASP_COLOR = {
    red: '#ee0000',
    blue: '#0000f7',
    green: '#00cc00',
    orange: '#ff8000'
  };
  const CUSP_NAMES  = ['AC','2','3','IC','5','6','DC','8','9','MC','11','12'];
  const CUSP_COLORS = ['#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a','#b30033','#1a1a99','#00991a'];

  function normDeg(d: number) { let n = d % 360; if(n<0) n+=360; return n; }

  function polar(r: number, deg: number, offset=OFFSET) {
    const visual = normDeg(180 - deg + offset);
    const rad = visual * Math.PI / 180;
    return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
  }

  function angDist(a: number, b: number) { let d = Math.abs(a-b)%360; return d>180 ? 360-d : d; }

  let svgParts: string[] = [];

  const outerR = isTransit ? RADIUS * 0.95 : RADIUS * 0.80;
  const midR   = isTransit ? RADIUS * 0.73 : RADIUS * 0.65;
  const innerR = RADIUS * 0.48;
  const aspR   = RADIUS * 0.435;
`;

const lines = src.split('\n');

// Find start of SVG drawing logic
const startIndex = lines.findIndex(l => l.includes('svgParts.push(`<circle cx="${CX}" cy="${CY}" r="${outerR}"'));
// Find end
const endIndex = lines.findIndex(l => l.includes('const svg = `<?xml version="1.0"'));

let logicLines = lines.slice(startIndex, endIndex);

out += logicLines.join('\n') + '\n';
out += '  return svgParts.join("\\n");\n}\n';

fs.writeFileSync('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/web/src/components/chart/AstroChartGenerator.ts', out);
