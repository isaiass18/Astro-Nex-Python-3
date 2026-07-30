# Evaluación de Alternativas para Motor Offline

## A. TypeScript + Swiss Ephemeris (WASM) [Recomendada]
- **Compatibilidad con Capacitor (iOS/Android):** Excelente, se carga como archivo estático.
- **Funcionamiento Offline:** Total.
- **Tamaño:** ~1 MB para WASM + unos pocos MB de efemérides básicas.
- **Rendimiento:** Casi nativo.
- **Mantenibilidad:** Alta, aprovechando el ecosistema JS/TS con tipos.

## B. Python vía Pyodide (WASM)
- **Compatibilidad con Capacitor:** Posible, pero pesada.
- **Funcionamiento Offline:** Total, pero requiere un runtime Python en el navegador (~20-30MB de carga inicial).
- **Rendimiento:** Más lento (Python interpretado sobre WASM).
- **Riesgos Técnicos:** Integrar extensiones C (`_pysw`) sobre Pyodide es extremadamente complejo; probablemente habría que recompilar todo el `astronex` para emscripten.

## C. Biblioteca JavaScript Nativa (sin WASM)
- **Riesgo:** Swiss Ephemeris es el estándar de oro en astrología. Cualquier port 100% JS puro puede introducir diferencias de redondeo o errores astronómicos que fallarán las tolerancias de la API original.

### Conclusión
Se seleccionará **TypeScript + WASM (Swiss Ephemeris)** porque ofrece la mejor relación de rendimiento, exactitud y ligereza.
