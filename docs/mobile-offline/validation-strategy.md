# Estrategia de Validación y Tolerancias

La clave del éxito es lograr **Paridad Matemática** con el motor original en Python/C.

## Golden Fixtures
- Se usará un script para volcar resultados completos de la API a archivos JSON (`mobile/tests/golden/`).

## Tolerancias Numéricas
- **Grados de Longitud Planetaria:** ± 0.0005° (aprox 2 segundos de arco, límite aceptable para redondos entre coma flotante JS vs C).
- **Día Juliano:** Precisión de milisegundos.

## Pruebas
1. Pruebas unitarias que ejecutan WASM local y comparan sus resultados con los golden fixtures.
2. Si falla (fuera de tolerancia), la compilación debe fallar.
