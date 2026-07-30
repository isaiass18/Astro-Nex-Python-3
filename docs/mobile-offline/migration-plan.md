# Plan de Migración a Motor Híbrido Offline

## Paso 1: Prueba Vertical y Validación de WASM (Actual)
- Implementar un Web Worker con un puerto de Swiss Ephemeris en WASM.
- Verificar contra la API si los cálculos de planetas y casas concuerdan a 0.001 grados.

## Paso 2: Portar Lógica de `chart.py` y `nexdate.py` a TypeScript
- Crear la capa Typescript que coordine las fechas y orqueste el acceso a WASM, reproduciendo la lógica exacta de Astro-Nex en `src/engine/calculations/`.

## Paso 3: Portar `database.py` a SQLite en Capacitor
- Migrar las bases de datos SQLite (`worldnames` y demás) al almacenamiento local de Capacitor usando el plugin oficial de SQLite.

## Paso 4: Motor de Renderizado Offline
- Sustituir Cairo/Pango por una renderización SVG/Canvas usando React.

## Paso 5: Reemplazo en iOS/Android
- Construir la app Capacitor.
- Eliminar la necesidad del servidor `mobile/api`.
