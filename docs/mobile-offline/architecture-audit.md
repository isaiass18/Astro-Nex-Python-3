# Auditoría de Arquitectura de la Aplicación Móvil Actual

## Tecnología Actual
- **Motor Backend (API):** Flask (Python 3), exponiendo el motor `astronex` (que históricamente era de escritorio). Utiliza SQLite para la base de datos `worldnames`.
- **Cálculo Base:** Extensiones C (ej. `_pysw.*`) que hacen de puente hacia Swiss Ephemeris (`pysw.py`), además de mucha lógica matemática en Python dentro de `astronex/chart.py` y similares.
- **Renderizado Gráfico:** Actualmente se realiza vía Cairo y Pango en el servidor. La API móvil tiene un endpoint `/v1/charts/render` que devuelve directamente una imagen PNG generada en servidor.
- **Aplicación iOS:** Escrita nativamente en Swift en `mobile/ios/AstroNexMobile`. Consume endpoints REST para buscar localidades, obtener detalles astronómicos y renderizar imágenes.

## Flujo Completo Actual
1. **Entrada:** La app móvil envía un JSON con `birth` (ISO-8601), `timezone`, latitud y longitud.
2. **Cálculo (Servidor):**
   - Se instancian clases de GTK/State sin montar ventanas (`astronex.state.Current`).
   - Se establece la localidad.
   - `astronex.chart.Chart.calc()` se invoca usando `astronex.nexdate.NeXDate` para conversiones de tiempo y Día Juliano.
   - `_pysw` / Swiss Ephemeris efectúa los cálculos precisos.
3. **Respuesta:**
   - Para detalles: JSON con planetas, casas y aspectos con sus orbes.
   - Para renderizado: Una imagen PNG generada mediante Cairo.

## Dependencias de GTK
- Las importaciones de `astronex.boss` y `astronex.state` exigen tener emuladores de GTK o stubs si no hay display activo, pero en VNC se inicia con soporte gráfico de X11.

## Archivos Críticos
- Efemérides: Archivos del sistema y `astronex/resources`.
- Base de datos: `db/nex.db` y sqlite `worldnames`.
