const fs = require('fs');
const path = require('path');

const svgContent = fs.readFileSync(path.join(__dirname, '../comparisons/app_chart.svg'), 'utf-8');
const fontPath = path.join(__dirname, '../web/public/fonts/Astro-Nex.ttf');
const fontBase64 = fs.readFileSync(fontPath).toString('base64');

const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    @font-face {
      font-family: 'Astro-Nex';
      src: url(data:font/truetype;base64,${fontBase64}) format('truetype');
    }
    body { margin: 0; background: white; }
    svg { display: block; }
  </style>
</head>
<body>
  ${svgContent}
</body>
</html>`;

const outPath = path.join(__dirname, '../comparisons/render.html');
fs.writeFileSync(outPath, htmlContent, 'utf8');
console.log('HTML generado en:', outPath);
