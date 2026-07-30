/**
 * Mappings for the Astro-Nex custom font glyphs.
 */

// Zodiac signs mapping (ASCII mapped to Astro-Nex.ttf)
export const ZODIAC_GLYPHS = [
  'q', // Aries
  'w', // Taurus
  'e', // Gemini
  'r', // Cancer
  't', // Leo
  'y', // Virgo
  'u', // Libra
  'i', // Scorpio
  'o', // Sagittarius
  'p', // Capricorn
  'a', // Aquarius
  's'  // Pisces
];

// Planet mapping corresponding to the standard engine planet index.
// 0: Sun, 1: Moon, 2: Mercury, 3: Venus, 4: Mars, 5: Jupiter, 6: Saturn, 
// 7: Uranus, 8: Neptune, 9: Pluto, 10: Node
export const PLANET_GLYPHS = [
  'd', // Sun
  'f', // Moon
  'h', // Mercury
  'j', // Venus
  'k', // Mars
  'l', // Jupiter
  'g', // Saturn
  'z', // Uranus
  'x', // Neptune
  'c', // Pluto
  'v'  // Node
];

// Aspect mapping
export const ASPECT_GLYPHS = [
  '1', // Conjunction
  '2', // Semi-sextile
  '3', // Sextile
  '4', // Square
  '5', // Trine
  '6', // Quincunx
  '7', // Opposition
  '6', // Quincunx
  '5', // Trine
  '4', // Square
  '3', // Sextile
  '2'  // Semi-sextile
];

// Element colors based on Astro-Nex defaults
export const ZODIAC_COLORS = [
  '#de3535', // Fire
  '#57c468', // Earth
  '#f7ef82', // Air
  '#b7b7e5'  // Water
];

// The pattern of elements in the zodiac (Fire, Earth, Air, Water)
export const getZodiacColor = (index: number) => ZODIAC_COLORS[index % 4];

// Standard planet colors
// Standard planet colors
export const PLANET_COLORS = [
  '#ff8000', // 0: Sun (pers)
  '#ff8000', // 1: Moon (pers)
  '#0000ff', // 2: Mercury (tool)
  '#0000ff', // 3: Venus (tool)
  '#0000ff', // 4: Mars (tool)
  '#0000ff', // 5: Jupiter (tool)
  '#ff8000', // 6: Saturn (pers)
  '#9900cc', // 7: Uranus (trans)
  '#9900cc', // 8: Neptune (trans)
  '#009900', // 9: Pluto (trans)
  '#9900cc'  // 10: Node (node)
];

export const getPlanetColor = (index: number) => PLANET_COLORS[index] || '#0000ff';

// Colors for aspect lines based on goodwill or angle, adjusted for dark theme
export const ASPECT_COLORS = {
  red: '#ee0000',   // Squares, oppositions
  blue: '#0000f7',  // Sextiles, trines
  green: '#00cc00', // Quincunx, semi-sextile
  orange: '#ff8000' // Conjunction
};
