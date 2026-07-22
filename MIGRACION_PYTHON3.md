# Migración de Astro-Nex de Python 2 a Python 3

Este repositorio conserva Astro-Nex 1.2.3 y documenta su port a Python 3 con
GTK 3. El objetivo del trabajo es mantener el comportamiento funcional del
programa original, con prioridad para Linux y una base de código compartida
para Windows.

## Alcance

La migración incluye:

- conversión del código Python 2 a sintaxis y semántica Python 3;
- sustitución de PyGTK/GTK 2 por PyGObject/GTK 3;
- compilación de la extensión Swiss Ephemeris mediante `setuptools`;
- correcciones de rutas SQLite y empaquetado multiplataforma;
- revisión de cálculos, cartas, retornos solares, mezclador y exportación;
- validación automática y apertura de los diálogos GTK3 principales.

No se considera terminada por el mero hecho de que la aplicación abra: cada
función debe contrastarse contra el comportamiento conocido de la versión
Python 2, con cartas reales de diferentes épocas, zonas horarias, latitudes y
alfabetos.

## Cambios técnicos principales

### Compatibilidad Python 3

- Se actualizaron importaciones, excepciones, iteradores, texto Unicode,
  serialización `pickle` y operaciones de división/ordenación.
- Las importaciones y exportaciones AAF trabajan con texto UTF-8.
- Las rutas de datos y SQLite se resuelven como rutas Python 3, creando los
  directorios necesarios antes de abrir la base de datos.

### GTK3 y PyGObject

`astronex/gtk_compat.py` proporciona una capa explícita y acotada para las API
de PyGTK que ya no existen en GTK3. Entre otros aspectos cubre cajas, tablas,
cuadros de diálogo, combos editables, aceleradores de teclado, calendario y
propiedades antiguas de widgets.

Se corrigieron incompatibilidades concretas detectadas en ejecución:

- aceleradores que GTK3 exige como enums `Gdk.ModifierType` y
  `Gtk.AccelFlags`;
- opciones del calendario como `Gtk.CalendarDisplayOptions`;
- `ComboBoxEntry.pack_start` con el argumento heredado opcional;
- diálogo de localidades: se evita el atributo reservado `widget` de GObject
  y se corrige la entrada de longitud;
- señales de dibujado, adaptación Cairo/Pango y selectores de tablas.

### Motor astronómico y empaquetado

- La extensión `_pysw` se construye desde el código fuente SWIG incluido.
- `setup.py`, `pyproject.toml` y `MANIFEST.in` permiten construir una rueda
  para la plataforma de destino sin reutilizar binarios antiguos.
- Los binarios compilados y cachés no se versionan: deben generarse en Linux o
  Windows durante la instalación.

## Verificación realizada

La suite en `tests/` cubre, entre otros, rutas de base de datos, coordenadas,
fechas UTC, carta actual, retorno solar, datos de mezclador, AAF y extensión
Swiss Ephemeris. `tests/test_gui_smoke.py` abre de forma controlada los
diálogos GTK3 principales.

En Ubuntu 24.04 se comprobó:

```bash
python -m compileall -q astronex tests
python -m unittest discover -s tests -q
ASTRONEX_GUI_SMOKE=1 python -m unittest tests.test_gui_smoke -q
```

También se validó la compilación de la extensión nativa y la instalación desde
una rueda generada localmente.

## Instalación en Linux

Consulta [`INSTALL`](INSTALL). Como referencia, en Ubuntu se necesitan Python
3, GTK3/PyGObject, Cairo, compilador C y los paquetes de desarrollo de GTK.
Después se crea un entorno virtual, se instalan las dependencias y se ejecuta:

```bash
python setup.py build_ext --inplace
python nex.py
```

## Windows

La fuente debe mantenerse idéntica a Linux. La extensión `_pysw` se compila
para Windows en el propio Windows; no se deben copiar ficheros `.so`, `.pyd`,
`build/` ni `dist/` de otra plataforma. La validación funcional en Windows
debe cubrir los mismos diálogos, cartas, impresión y exportaciones.

## Pendiente de validación funcional exhaustiva

- Crear y editar cartas, localidades, parejas y preferencias desde la GUI.
- Comparar resultados con cartas históricas, zonas horarias antiguas,
  latitudes altas y nombres con caracteres no ASCII.
- Probar impresión y exportación desde los cuadros de diálogo, no sólo desde
  llamadas internas.
- Verificar visualmente todas las operaciones y tipos de carta frente a la
  versión Python 2 de referencia.

## Seguridad del repositorio

El repositorio no debe incluir llaves privadas, archivos `.pem`, tokens,
variables de entorno, IPs de servidores ni bases de datos locales de usuarios.
La configuración de exclusión está en [`.gitignore`](.gitignore).
