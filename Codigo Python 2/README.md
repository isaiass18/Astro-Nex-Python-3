# Astro-Nex - codigo historico Python 2

Este directorio conserva una referencia historica de Astro-Nex antes de su
migracion a Python 3 y GTK 3. Se publica para consulta, comparacion tecnica y
preservacion del instalador anterior; no es una version mantenida ni adecuada
para instalaciones nuevas.

## Contenido

- [`Codigo fuente Linux`](Codigo%20fuente%20Linux/): fuente original Python 2
  orientada a Linux, incluidos recursos, extensiones C, scripts de instalacion,
  caches y binarios compilados de la copia original.
- [`Instalador Windows/Astro-Nex-1.2.3p.exe`](Instalador%20Windows/Astro-Nex-1.2.3p.exe):
  instalador ejecutable historico para Windows.
- [Descarga directa — Instalador Windows v1 (Python 2, x86)](https://github.com/isaiass18/Astro-Nex-Python-3/releases/download/v2.0b0/Astro-Nex-v1-Python2-Windows-x86.exe):
  copia descargable sin clonar el repositorio.

La fuente requiere un entorno heredado de Python 2, PyGTK, PyGObject, PyCairo,
ConfigObj, pytz y la extension astronomica `pysw`. Las versiones actuales de
macOS, Windows y Linux no deben depender de este codigo ni de esos requisitos.

## Version actual

Astro-Nex actual usa Python 3 y GTK 3. Para descargar instaladores mantenidos:

- [macOS Apple Silicon](../Mac%20Instalador/README.md)
- [Linux AppImage y DEB](../Linux%20Instalador/README.md)
- [Windows](../Windows%20Instalador/README.md)
- [GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases)

La migracion tecnica desde Python 2 se documenta en
[`guias/MIGRACION_PYTHON3.md`](../guias/MIGRACION_PYTHON3.md).
