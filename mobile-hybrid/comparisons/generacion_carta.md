# ¿Cómo se genera la Carta Astral (Gráfica SVG) en la App?

Este documento explica paso a paso el flujo de datos y renderizado que sigue la aplicación web (React) para generar la imagen de la carta natal (Carta Radix), y cómo reproducir ambas imágenes (App y Python) para compararlas.

---

## DATOS EXACTOS DE PRUEBA PARA COMPARACIÓN

> ⚠️ **IMPORTANTE:** Usar **exactamente** estos datos en ambas generaciones para que la comparación sea válida.

| Campo         | Valor                    |
|---------------|--------------------------|
| Nombre        | Golden Test              |
| Fecha         | 15 de Junio de 1990      |
| Hora local    | 12:30:00                 |
| Hora UTC      | 17:30:00                 |
| Zona horaria  | America/Bogota (UTC-5)   |
| Ciudad        | Bogotá, Colombia         |
| Latitud       | 4.6097                   |
| Longitud      | -74.0817                 |

---

## GENERACIÓN DE LA IMAGEN DE LA APP (SVG → PNG)

### Paso 1: Calcular los datos astrológicos (Python)
```bash
cd /Users/user/Documents/Astro-Nex-1.2.3
.venv-macos-build/bin/python3 mobile-hybrid/scripts/generate_golden.py
```
Esto genera: `mobile-hybrid/tests/golden/natal_output.json`  
(contiene `planets`, `houses`, `aspects` con los datos exactos de los datos de prueba)

### Paso 2: Generar el SVG de la App (Golden Test Script)
```bash
node mobile-hybrid/scripts/generate_chart_svg.mjs
```
Esto genera: `mobile-hybrid/comparisons/app_chart.svg`  
El script lee `natal_output.json` y dibuja la carta en SVG. **IMPORTANTE:** Este script (`generate_chart_svg.mjs`) es la *referencia canónica y pura* aprobada para la lógica visual de Astro-Nex. Su contenido se copia 1:1 al archivo TypeScript que usa la app en producción (`AstroChartGenerator.ts`) para garantizar que la app móvil renderice exactamente los mismos píxeles sin importar el entorno.

### Paso 3: Generar el HTML con la fuente incrustada
```bash
node mobile-hybrid/scripts/generate_html.js
```
Esto genera: `mobile-hybrid/comparisons/render.html`  
Este paso es **crítico**: incrusta la fuente `Astro-Nex.ttf` en base64 dentro del HTML para que Chrome la cargue correctamente.

### Paso 4: Renderizar a PNG usando Chrome Headless
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --screenshot=mobile-hybrid/comparisons/app_20260729_v1.png \
  --window-size=1000,1000 \
  file:///Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/comparisons/render.html
```
Esto genera: `mobile-hybrid/comparisons/app_20260729_v1.png`

> 💡 **TIP PARA EL CACHÉ:** Si estás compartiendo estas imágenes en el chat de Antigravity (u otros chats), **siempre genera las nuevas imágenes con un nombre distinto** (ej. agregando `_v2`, `_fixed`, etc.). El chat tiene un caché muy agresivo y si sobrescribes el mismo archivo, la interfaz de usuario seguirá mostrando la versión antigua.

> ❌ **NO usar `qlmanage`** para convertir el SVG — no carga las fuentes y genera imágenes con letras de texto en lugar de los símbolos del zodíaco.

---

## GENERACIÓN DE LA IMAGEN DE PYTHON (Astro-Nex Original)

> ⚠️ **LIMITACIÓN:** El programa Astro-Nex original usa PyGTK (interfaz gráfica de escritorio) que **requiere una pantalla real** para poder dibujar. No se puede ejecutar en modo headless/servidor. Solo el motor matemático puede ejecutarse sin pantalla.

### Opción A: Desde el programa de escritorio (recomendado)
1. Abrir el programa **Astro-Nex** en tu Mac.
2. Crear una carta nueva con los datos exactos de prueba (tabla arriba).
3. Tomar captura de pantalla y guardar como `mobile-hybrid/comparisons/original_YYYYMMDD.png`.

### Opción B: Verificar los valores numéricos (sin imagen)
```bash
cd /Users/user/Documents/Astro-Nex-1.2.3
.venv-macos-build/bin/python3 mobile-hybrid/scripts/generate_golden.py
cat mobile-hybrid/tests/golden/natal_output.json
```
Los valores clave para verificar alineación:
- `houses[0]` = Ascendente (AC) — debe quedar a la izquierda de la carta
- `houses[3]` = IC (Imum Coeli) — debe quedar abajo  
- `houses[6]` = Descendente (DC) — debe quedar a la derecha
- `houses[9]` = MC (Medium Coeli) — debe quedar arriba

**Valores calculados por el motor Python con los datos de prueba:**
```
houses[0]  = 182.27°  → AC en Libra
houses[3]  = 271.97°  → IC en Capricornio
houses[6]  = 2.27°    → DC en Aries
houses[9]  = 91.97°   → MC en Cáncer
```

---

## FLUJO INTERNO DE LA APP (para referencia)

### 1. Entrada de Datos (App.tsx)
La aplicación almacena la fecha, hora, latitud y longitud en el estado de React. Cuando el usuario hace clic en "Calcular", estos parámetros se agrupan y se envían a un Web Worker (`engine.worker.ts`) para no bloquear la interfaz gráfica.

### 2. Cálculo Astrológico (engine.worker.ts)
El Web Worker carga la librería **Swiss Ephemeris** compilada en WebAssembly (`swisseph`). 
- Calcula el día juliano a partir de la fecha UTC.
- Pide a `swisseph` las posiciones de los planetas (`pysw.planets`).
- Pide a `swisseph` las cúspides de las casas (`pysw.houses`), por defecto usando el sistema de casas de Koch.
- Calcula los aspectos entre planetas.
- Devuelve un gran objeto JSON (`chartData`) de vuelta a `App.tsx`.

### 3. Renderizado Geométrico Monolítico (AstroChartGenerator.ts)
A diferencia de las primeras versiones basadas en múltiples componentes de React, **la renderización de la carta entera se centralizó en un único motor monolítico** ubicado en:
`mobile-hybrid/web/src/components/chart/AstroChartGenerator.ts`

Este archivo es una exportación 1:1 de `generate_chart_svg.mjs` pero adaptado a TypeScript.
El Web Worker (`engine.worker.ts`) le entrega la data y este archivo devuelve directamente el string `<svg>...</svg>`.
Esto garantiza que la lógica (como los radios `R_RULEDINNER`, cálculos polinomiales de FususAspects, la progresión Huber `currentYear`, y `aspR`) no sufra ninguna alteración por el motor de renderizado de React.

### 4. Dibujo en Pantalla (ChartSvg.tsx)
Finalmente, `App.tsx` invoca el generador e inyecta el String SVG estático dentro de un div usando `dangerouslySetInnerHTML`:
```tsx
<div dangerouslySetInnerHTML={{ __html: svgContent }} />
```
