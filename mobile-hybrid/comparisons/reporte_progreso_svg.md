# Reporte de Avance: Migración y Perfeccionamiento del Generador SVG (Astro-Nex)

Este documento detalla el progreso técnico logrado para alcanzar la **paridad visual absoluta (1:1)** entre la gráfica original de Astro-Nex (Python/Desktop) y la nueva implementación móvil híbrida (React/Capacitor).

## 1. Arquitectura de Renderizado

La generación de la carta astral en la aplicación móvil fluye a través de tres componentes principales:

1. **Estado y UI (`App.tsx` / `ChartSvg.tsx`)**: Gestionan la interacción del usuario y renderizan directamente el string SVG proporcionado por el generador. No se aplica CSS que sobrescriba el SVG (para preservar los colores y trazos originales).
2. **Motor de Cálculo (`engine.worker.ts`)**: Ejecuta `sweph-wasm` en un Web Worker para obtener longitudes planetarias, casas y aspectos en segundo plano, evitando bloquear la interfaz.
3. **Generador Monolítico (`AstroChartGenerator.ts`)**: Recibe los datos astronómicos crudos y los transforma en un string SVG puro. Es el "corazón" del renderizado visual y reemplaza a la antigua librería Python.

## 2. Archivos Modificados y Su Propósito

### `web/src/components/chart/AstroChartGenerator.ts`
El componente principal de dibujo. Se le aplicaron las siguientes correcciones críticas para coincidir con el *"Golden Test"* documentado:

- **Restauración de los 3 Anillos Zodiacales**: Se modificaron las proporciones de los radios (`innerR`, `midR`, `outerR`) pasando de 2 a 3 anillos (`0.65`, `0.78` y `0.84`). Esto permite que los glifos zodiacales tengan su propio carril interior, dejando el carril exterior libre para los marcadores de grados.
- **Marcadores de 10° y 20°**: Se reimplementó la iteración que dibuja los textos "10" y "20" radialmente en cada signo (en el anillo `0.78` - `0.84`), un detalle vital de Astro-Nex original que se había perdido.
- **Corrección de Colores Elementales (`ZODIAC_COLORS_LIST`)**: Se corrigió el mapeo de colores. El orden correcto restaurado es Fuego (Rojo), Tierra (Verde), Aire (Amarillo - `#FFD700`) y Agua (Azul).
- **Corrección de Aspectos ("Fusus" vs "Unilateral")**: Se solucionó un bug crítico donde todas las líneas de aspecto se dibujaban grises, rectas y delgadas. 
  - *Causa*: `engine.worker.ts` enviaba la ID del aspecto (`a = 0 a 11`) pero no el nombre (ej. `'trig'`). Al ser el nombre `undefined`, el motor no aplicaba el color correcto, y usaba la matriz de orbes de "Semisextil" para todo. Esto causaba que la división de orbes (`f1 = trueOrb / orb1`) resultara mayor a `1.0`, disparando el modo *Unilateral* (línea recta) en lugar del *Fusus* (curva Bézier).
  - *Solución*: Se implementó un mapeo de ID a Nombre (`ASPECT_NAMES`) dentro del generador, restaurando los colores (Rojo, Azul, Verde) y las curvas Bézier (husos) dinámicas según la fuerza del orbe. También restauró la capacidad de ocultar las conjunciones.

### `scripts/generate_chart_svg.mjs`
Es el script Node.js utilizado para pruebas locales rápidas (*Golden Script*). Se mantiene 100% sincronizado con `AstroChartGenerator.ts`. Todas las correcciones geométricas (anillos, marcas de 10/20 grados y colores) se replicaron aquí para garantizar que la generación mediante consola (`node generate_chart_svg.mjs`) sea idéntica a la de la App.

## 3. Despliegue en Dispositivo Físico (iOS)

Dado que la aplicación es híbrida usando Capacitor, el flujo de instalación directa en el iPhone (sin necesidad de abrir la interfaz de Xcode) se logró mediante los siguientes pasos:

1. **Construcción Web**: `npm run build` en la carpeta `web` compila el bundle de React + Vite.
2. **Sincronización**: `npx cap copy ios` traslada los archivos estáticos (`dist/`) al directorio del proyecto nativo (`ios/App/App/public`).
3. **Compilación Nativa**: Usando `xcodebuild -workspace App.xcworkspace -scheme App -destination ... build`, se genera el empaquetado `.app` de iOS.
4. **Instalación (`devicectl`)**: Usando la herramienta de línea de comandos de Apple `xcrun devicectl device install app --device <UUID>`, se inyecta la aplicación directamente en el iPhone físico conectado, permitiendo pruebas instantáneas sin emulador.

## 4. Estado Actual y Próximos Pasos

- **Radical y Tránsitos**: Ambos modos renderizan exactamente igual al software de escritorio original, incluyendo el anillo exterior adicional para los planetas en tránsito y los aspectos cruzados (interaspectos).
- **Paridad Visual**: Verificada y aceptada. Las proporciones, curvas Bézier, estilos de trazo, glifos de la fuente *Astro-Nex* y colores son idénticos al test de referencia de 1990.
