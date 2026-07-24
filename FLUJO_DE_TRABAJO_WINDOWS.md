# Flujo único de trabajo en Windows

## Carpeta de trabajo

La única copia de código que se debe usar en este equipo es este repositorio:

```text
H:\Astro-Nex-1.2.3
```

No crear clonaciones auxiliares para compilar. Antes de cualquier revisión o
reconstrucción, abrir una terminal en esta carpeta y actualizarla desde GitHub:

```powershell
git fetch origin main
git pull --ff-only origin main
git rev-parse --short HEAD
git status --short
```

El último comando debe quedar sin salida. Si existen cambios locales no
publicados, no se deben mezclar con una reconstrucción: primero hay que
revisarlos y decidir si se publican o se descartan de forma consciente.

## Regla para el instalador

Siempre se construyen la portable y `Astro-Nex-Setup.exe` a partir del código
actual de esta única carpeta, ya sincronizada con `origin/main`. No se debe
usar una portable antigua de Descargas, otra unidad, ni una carpeta de salida
de una compilación anterior.

Las instrucciones técnicas completas para la compilación están en
`CONSTRUIR_INSTALADOR_WINDOWS.md`. Esa guía exige conservar
`astronex/resources/ac.pk` con finales de línea LF y generar un instalador
Inno Setup que instale también la fuente `Astro-Nex.ttf`.

## Publicación

Después de validar los ejecutables, comprobar el alcance antes de publicar:

```powershell
git status --short
git diff --stat
```

En una reconstrucción normal sólo se publican los archivos generados dentro de
`Windows Instalador` y, si procede, la documentación. Nunca se modifican ni se
revierten archivos fuente que llegaron desde GitHub sin un error reproducible.
