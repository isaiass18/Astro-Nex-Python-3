const fs = require('fs');
const opentype = require('opentype.js');
const buffer = fs.readFileSync('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/web/public/fonts/Astro-Nex.ttf');
const font = opentype.parse(buffer.buffer);

const letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*()_+-=[]{}|;:',./<>?";
console.log("Glyphs found:");
for (let i = 0; i < letters.length; i++) {
  const char = letters[i];
  const glyph = font.charToGlyph(char);
  if (glyph.name && glyph.name !== '.notdef') {
    console.log(char + " -> " + glyph.name);
  }
}
