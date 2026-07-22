# Estado de la migración a Python 3

## Verificado

Todo el árbol Python compila con Python 3.9:

```sh
python3 -m compileall -q astronex nex.py setup.py setup_win.py
```

También se han comprobado las utilidades matemáticas y de rutas usadas por el
programa. El lanzador responde a `python3 nex.py --help`.

## Bloqueadores de ejecución

La interfaz fue escrita para **PyGTK 2**, una biblioteca exclusiva de Python 2:

```text
ModuleNotFoundError: No module named 'gtk'
```

Para ejecutar Astro-Nex en Python 3 es necesario migrar los módulos de la GUI
a PyGObject/GTK 3 (o reevaluarlos para GTK 4). GTK 3 es la ruta recomendada,
porque conserva más de las APIs de PyGTK que utiliza la aplicación. Esta parte
incluye las importaciones `gtk`, `gobject`, `pango` y `pangocairo`, además de
las constantes, señales, diálogos e impresión de la GUI.

El fichero `_pysw.so` incluido tampoco se puede reutilizar: es un binario
compilado para otra plataforma y ABI de Python. Debe generarse una extensión
`pysw` para cada combinación de sistema operativo, arquitectura y versión de
Python. El código fuente de Swiss Ephemeris está en `ext/ext32/src`, pero se
necesita conservar o reconstruir el código de enlace Python/C que expone las
funciones `planets`, `houses`, `calc_ut_with_speed` y `setpath`.

## Orden recomendado

1. Preparar un entorno reproducible de Linux con Python 3.9+ y las
   dependencias de desarrollo de GTK 3, PyGObject, Pycairo, Pango, pytz,
   ConfigObj y Pillow.
2. Migrar primero una ventana mínima y el arranque de configuración a GTK 3;
   comprobar que abre sin cargar todos los diálogos.
3. Compilar y probar `pysw` para Python 3 con valores de referencia conocidos
   de Swiss Ephemeris.
4. Migrar por grupos los diálogos, superficies Cairo/Pango, impresión y
   exportaciones, añadiendo pruebas de cálculo y capturas de referencia.
5. Crear el paquete Windows después de estabilizar el núcleo en Linux, con una
   compilación separada de `pysw` para Windows.

No se debe distribuir todavía como una versión funcional de Python 3: la
compatibilidad sintáctica está resuelta, pero las dos dependencias críticas de
ejecución siguen pendientes.
