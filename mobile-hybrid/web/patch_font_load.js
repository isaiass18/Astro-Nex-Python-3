const fs = require('fs');
const file = '/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/web/src/components/chart/ChartCanvas.tsx';
let code = fs.readFileSync(file, 'utf8');

code = code.replace(
  'const canvasRef = useRef<HTMLCanvasElement>(null);',
  'const canvasRef = useRef<HTMLCanvasElement>(null);\n  const [fontsLoaded, setFontsLoaded] = React.useState(false);\n\n  useEffect(() => {\n    document.fonts.ready.then(() => setFontsLoaded(true));\n  }, []);'
);

code = code.replace(
  '  useEffect(() => {\n    const canvas = canvasRef.current;\n    if (!canvas || !chartData) return;',
  '  useEffect(() => {\n    const canvas = canvasRef.current;\n    if (!canvas || !chartData || !fontsLoaded) return;'
);

code = code.replace(
  '  }, [width, height, chartData]);',
  '  }, [width, height, chartData, fontsLoaded]);'
);

fs.writeFileSync(file, code);
