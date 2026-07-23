# Migración de Astro-Nex de Python 2 a Python 3

## Demostración online

La versión Linux puede probarse desde un navegador, sin instalar nada:

**[Abrir Astro-Nex online](http://3.19.232.60:6080/vnc.html?autoconnect=1&resize=scale)**

Es un servicio público de demostración.

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

### Plataformas comprobadas

| Plataforma | Estado de comprobación |
| --- | --- |
| Ubuntu 24.04 x86_64 | Compilación de `_pysw`, 17 pruebas automáticas, prueba GTK3 de diálogos, instalación desde rueda y ejecución de la interfaz. |
| Windows x86_64 (MSYS2 UCRT64) | Esta misma fuente fue compilada y probada funcionalmente en Windows. La aplicación y su interfaz funcionan correctamente en ese entorno. |

Linux y Windows deben trabajar siempre sobre la misma revisión de los archivos
fuente. Sólo los artefactos compilados (`_pysw`, ruedas, `build/` y `dist/`)
son distintos por plataforma y se generan localmente.

## Instalación en Linux

Esta guía reemplaza el procedimiento del PDF de Python 2. No instales
`python2`, `pip2` ni `python-gtk2`: esta edición usa Python 3 y GTK3.

### Instalación sencilla (recomendada para Ubuntu/Debian)

Hay dos instaladores, según dónde se encuentre el código.

#### Opción A: ya tienes una copia local o descargaste el ZIP

Abre una Terminal dentro de la carpeta `Astro-Nex-Python-3` y ejecuta:

```bash
./scripts/install_linux.sh
```

El script pide la contraseña de `sudo` una sola vez para instalar los paquetes
de Ubuntu/Debian. Después crea el entorno Python, instala las dependencias,
compila el motor astronómico, instala la tipografía y crea un lanzador llamado
**Astro-Nex** en el menú de aplicaciones.

Para instalar y ejecutar las pruebas al final:

```bash
./scripts/install_linux.sh --test
```

Opciones útiles: `--no-system-deps`, `--no-font` y `--no-launcher`. Consulta
`./scripts/install_linux.sh --help` para el detalle.

#### Opción B: descargar o actualizar directamente desde GitHub

Descarga el instalador y ejecútalo con:

```bash
curl -fsSL https://raw.githubusercontent.com/isaiass18/Astro-Nex-Python-3/main/scripts/install_from_github.sh | bash
```

El instalador descarga el repositorio en
`~/Aplicaciones/Astro-Nex-Python-3` (o actualiza esa copia si ya existe) y
ejecuta la instalación completa. Para que además ejecute las pruebas:

```bash
curl -fsSL https://raw.githubusercontent.com/isaiass18/Astro-Nex-Python-3/main/scripts/install_from_github.sh | bash -s -- --test
```

También puede descargarse el archivo
[`scripts/install_from_github.sh`](scripts/install_from_github.sh), revisarlo y
ejecutarlo localmente. Usa `--directory /otra/ruta` para cambiar la carpeta de
instalación.

### Instalación manual

### 1. Preparar el sistema

En Ubuntu/Debian se necesitan Python 3.9 o posterior, GTK3, PyGObject,
Pycairo, `pkg-config`, compilador C y las cabeceras de desarrollo de Python y
GTK. Abre una Terminal e instala los requisitos:

```bash
sudo apt update
sudo apt install build-essential python3-venv python3-dev pkg-config \
  libgtk-3-dev gir1.2-gtk-3.0 python3-gi python3-gi-cairo python3-cairo
```

### 2. Descargar el programa

Elige una carpeta de trabajo, por ejemplo `~/Aplicaciones`, y descarga el
repositorio público:

```bash
mkdir -p ~/Aplicaciones
cd ~/Aplicaciones
git clone https://github.com/isaiass18/Astro-Nex-Python-3.git
cd Astro-Nex-Python-3
```

Si se ha descargado un archivo ZIP desde GitHub, descomprímelo y entra en la
carpeta `Astro-Nex-Python-3` antes de continuar.

### 3. Crear el entorno Python e instalar dependencias

Desde la carpeta del proyecto ejecuta:

```bash
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install pytz configobj Pillow ipython
```

El parámetro `--system-site-packages` es importante: permite que el entorno
virtual utilice PyGObject y Pycairo instalados por Ubuntu.

### 4. Compilar la extensión astronómica

La primera vez, compila `_pysw`, la extensión nativa de Swiss Ephemeris:

```bash
python setup.py build_ext --inplace
```

### 5. Instalar la tipografía astrológica

Abre el archivo `astronex/resources/Astro-Nex.ttf` con el visor de fuentes del
sistema y selecciona **Instalar**. Este paso es recomendable para que los
símbolos astrológicos se muestren correctamente.

### 6. Ejecutar Astro-Nex

En la misma Terminal, con el entorno activado, inicia el programa:

```bash
python nex.py
```

En ejecuciones posteriores:

```bash
cd ~/Aplicaciones/Astro-Nex-Python-3
. .venv/bin/activate
python nex.py
```

### 7. Comprobación opcional

Antes de usarlo con datos personales, puedes ejecutar la suite automática:

```bash
python -m unittest discover -s tests -q
```

### 8. Crear un lanzador opcional

En la mayoría de escritorios Linux puedes crear un archivo
`~/.local/share/applications/astronex.desktop` con este contenido, ajustando
la ruta si instalaste el proyecto en otra carpeta:

```ini
[Desktop Entry]
Type=Application
Name=Astro-Nex
Exec=/home/TU_USUARIO/Aplicaciones/Astro-Nex-Python-3/.venv/bin/python /home/TU_USUARIO/Aplicaciones/Astro-Nex-Python-3/nex.py
Icon=/home/TU_USUARIO/Aplicaciones/Astro-Nex-Python-3/astronex/resources/iconex-48.png
Terminal=false
Categories=Education;Science;
```

Sustituye `TU_USUARIO` por tu nombre de usuario de Linux. Tras guardar, busca
**Astro-Nex** en el menú de aplicaciones. Si el escritorio no muestra el icono
inmediatamente, cierra sesión y vuelve a entrar.

## Instalación en Windows

### Ejecutar el paquete portable (recomendado)

El repositorio incluye una distribución Windows ya preparada en
[`Windows Instalador`](Windows%20Instalador). Para instalarla:

1. Descarga el repositorio completo como ZIP y descomprímelo.
2. Ejecuta `Windows Instalador/Astro-Nex-Setup.exe`.
3. Sigue el asistente y abre Astro-Nex desde el acceso que crea.

No instales Python ni GTK de forma separada para este paquete: ya incluye sus
dependencias. También incluye una variante portable en
`Windows Instalador/Astro-Nex/Astro-Nex.exe`; conserva ese EXE junto con la
carpeta `_internal`. Esta distribución es para Windows de 64 bits.

### Compilar desde el código fuente

La ruta reproducible usada para Windows es **MSYS2 UCRT64 x86_64**. Instala
[MSYS2](https://www.msys2.org/), abre la consola **MSYS2 UCRT64** (no MSYS ni
MINGW64) y ejecuta:

```bash
pacman -Syu
pacman -S --needed \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-python-pip \
  mingw-w64-ucrt-x86_64-python-setuptools \
  mingw-w64-ucrt-x86_64-python-wheel \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-cairo \
  mingw-w64-ucrt-x86_64-python-pillow \
  mingw-w64-ucrt-x86_64-python-pytz \
  mingw-w64-ucrt-x86_64-python-ipython \
  mingw-w64-ucrt-x86_64-gtk3 \
  mingw-w64-ucrt-x86_64-gcc
```

En una copia nueva del repositorio, desde la misma consola UCRT64:

```bash
cd /h/Astro-Nex-Python-3
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install configobj
python -m pip install .
astronex
```

Para ejecutar desde las fuentes tras compilar la extensión:

```bash
python setup.py build_ext --inplace
python nex.py
```

Para crear una rueda de Windows reproducible:

```bash
python -m pip wheel --no-deps --wheel-dir dist .
```

No mezcles el Python/GTK de UCRT64 con CPython oficial, ni copies binarios
`.so`, `.pyd`, `build/` o `dist/` desde otra plataforma.

Los detalles completos y la solución de problemas habituales están en
[`INSTALL`](INSTALL).

## Pendiente de validación funcional exhaustiva

- Crear y editar cartas, localidades, parejas y preferencias desde la GUI.
- Comparar resultados con cartas históricas, zonas horarias antiguas,
  latitudes altas y nombres con caracteres no ASCII.
- Probar impresión y exportación desde los cuadros de diálogo, no sólo desde
  llamadas internas.
- Verificar visualmente todas las operaciones y tipos de carta frente a la
  versión Python 2 de referencia.
