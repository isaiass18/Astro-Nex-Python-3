import React, { useEffect, useRef } from 'react';
import { AstroRenderer, type RadixData, type PlanetDatum, type ZodiacDatum, type AspectDatum, type RGB } from './AstroRenderer';

interface ChartCanvasProps {
  width?: number;
  height?: number;
  chartData: any;
}

const ZODIAC_GLYPHS = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's'];
const PLANET_GLYPHS = ['d', 'f', 'h', 'j', 'k', 'l', 'g', 'z', 'x', 'c', 'v'];

// Hex to RGB [0..1]
function hexToRgb(hex: string): RGB {
  let r = 0, g = 0, b = 0;
  if (hex.length === 4) {
    r = parseInt(hex[1] + hex[1], 16) / 255;
    g = parseInt(hex[2] + hex[2], 16) / 255;
    b = parseInt(hex[3] + hex[3], 16) / 255;
  } else if (hex.length === 7) {
    r = parseInt(hex.substring(1, 3), 16) / 255;
    g = parseInt(hex.substring(3, 5), 16) / 255;
    b = parseInt(hex.substring(5, 7), 16) / 255;
  }
  return [r, g, b];
}

// Map old colors to RGB
const PLANET_COLORS_RGB: RGB[] = [
  hexToRgb('#ff8000'), hexToRgb('#ff8000'), hexToRgb('#0000ff'), hexToRgb('#0000ff'), 
  hexToRgb('#0000ff'), hexToRgb('#0000ff'), hexToRgb('#ff8000'), hexToRgb('#9900cc'), 
  hexToRgb('#9900cc'), hexToRgb('#009900'), hexToRgb('#9900cc')
];

const ZODIAC_COLORS_RGB: RGB[] = [
  hexToRgb('#ED333B'), // Fire
  hexToRgb('#00BB00'), // Earth
  hexToRgb('#FFB600'), // Air
  hexToRgb('#0000FF')  // Water
];

export const ChartCanvas: React.FC<ChartCanvasProps> = ({
  width = 1000,
  height = 1000,
  chartData
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [fontsLoaded, setFontsLoaded] = React.useState(false);

  useEffect(() => {
    document.fonts.ready.then(() => setFontsLoaded(true));
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !chartData || !fontsLoaded) return;

    // Convert chartData to RadixData for AstroRenderer
    const ascendant = chartData.houses[0];
    const houses = chartData.houses;

    const planets: PlanetDatum[] = chartData.planets?.map((p: any, i: number) => {
      const idx = p.index !== undefined ? p.index : p.ix;
      return {
        id: `planet-${i}`,
        longitude: p.longitude,
        color: PLANET_COLORS_RGB[idx] || [0, 0, 0],
        glyph: { kind: "text", text: PLANET_GLYPHS[idx] || '?', fontFamily: 'Astro-Nex' },
        classIndex: idx,
        sourceLongitude: p.degree || p.longitude // Assuming p.degree might be different or same
      };
    }) || [];

    const zodiac: ZodiacDatum[] = Array.from({ length: 12 }, (_, i) => ({
      id: `sign-${i}`,
      longitude: i * 30 + 15,
      color: ZODIAC_COLORS_RGB[i % 4],
      glyph: { kind: "text", text: ZODIAC_GLYPHS[i], fontFamily: 'Astro-Nex' }
    }));

    const aspectColors: Record<string, RGB> = {
      'cuad': [1, 0, 0], 'opos': [1, 0, 0],
      'trig': [0, 0, 1], 'sext': [0, 0.8, 0], // Trine is Blue, Sextile is Green
      'quinc': [0, 0.8, 0], 'semi': [0, 0.8, 0] // Minor aspects usually Green
    };
    const ASPECT_NAMES: Record<number, string> = {
      0: 'conj', 1: 'semi', 2: 'sext', 3: 'cuad', 4: 'trig', 5: 'quinc',
      6: 'opos', 7: 'quinc', 8: 'trig', 9: 'cuad', 10: 'sext', 11: 'semi'
    };

    let aspects: AspectDatum[] | undefined;
    if (chartData.aspects) {
      aspects = chartData.aspects.map((asp: any) => {
        const name = asp.name || ASPECT_NAMES[asp.a];
        return {
          p1: asp.p1, // assuming index
          p2: asp.p2, // assuming index
          a: asp.a,
          f1: asp.f1 || 0, // Fallback if no orb data is present
          f2: asp.f2 || 0,
          gw: asp.gw,
          color: aspectColors[name] || [0.5, 0.5, 0.5]
        };
      });
    }

    const radixData: RadixData = {
      ascendant,
      houses,
      planets,
      zodiac,
      aspects,
      aspectCoordinates: 'indices'
    };

    const renderer = new AstroRenderer(canvas, {
      fontFamily: 'Astro-Nex',
      showHouseZones: false, // Let's disable some extras to match previous look exactly
      showHouseTrimming: false,
      showGoldenPoints: false
    });

    renderer.render(radixData);

  }, [width, height, chartData, fontsLoaded]);

  return (
    <canvas ref={canvasRef} width={width} height={height}
      style={{ display: 'block', margin: '0 auto', backgroundColor: '#fff', borderRadius: '50%', width: '100%', height: '100%' }}
    />
  );
};
