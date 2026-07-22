# Estado de la migración a Python 3

## Estado actual

Astro-Nex se ha portado a Python 3 y GTK3/PyGObject. El árbol de código se
compila, la extensión Swiss Ephemeris se construye desde su fuente y la
aplicación se ha ejecutado y probado en Ubuntu 24.04. La misma fuente es la
referencia para la compilación de Windows.

## Verificado

- Compilación de los módulos Python 3.
- Construcción de `_pysw` para la plataforma de destino.
- Rutas de datos y SQLite.
- Pruebas de coordenadas, fechas UTC, carta actual, retorno solar, mezclador,
  importación/exportación AAF y extensión astronómica.
- Apertura automática de los diálogos GTK3 principales, incluidos preferencias
  y localidades.
- Instalación desde una rueda generada localmente en Ubuntu 24.04.

Los comandos de referencia son:

```sh
python -m compileall -q astronex tests
python -m unittest discover -s tests -q
ASTRONEX_GUI_SMOKE=1 python -m unittest tests.test_gui_smoke -q
```

## Validación pendiente

La validación funcional continúa: deben contrastarse todas las operaciones,
impresión, exportación y flujos de edición con la versión Python 2, usando
cartas reales variadas (zonas horarias históricas, latitudes altas y texto no
ASCII). El detalle de alcance y cambios está en
[`MIGRACION_PYTHON3.md`](MIGRACION_PYTHON3.md).

## Plataformas

Linux es la plataforma de referencia actual. Windows debe compilar su propia
extensión nativa y no reutilizar binarios de Linux o macOS.
