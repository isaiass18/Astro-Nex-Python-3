# Sincronización de local, VNC y GitHub

## Regla principal

`origin/main` es la única fuente de verdad para el código, las pruebas, la
documentación y los instaladores que se publiquen. Un cambio no está
terminado hasta que los tres entornos estén en el mismo commit y sus árboles
Git estén limpios:

1. repositorio local;
2. `origin/main` en GitHub;
3. `/home/ubuntu/astronex-github-vnc-test` en VNC.

No se deben editar archivos de código directamente en VNC. VNC sirve para
probar una revisión que ya fue publicada en Git; no es una segunda fuente de
cambios.

## Estado de partida — 28 de julio de 2026

La divergencia encontrada fue de historial, no de contenido: VNC conservaba
un `HEAD` antiguo y acumulaba reparaciones locales que ya coincidían con el
árbol local. Esta normalización fija los tres entornos en el commit actual de
`origin/main`, con la corrección del Punto de Edad y el crédito de migración.

Los entornos virtuales, binarios compilados, capturas, claves, notas privadas
y scripts de reparación de un solo uso no forman parte del repositorio y no
se publican. Si hace falta conservarlos, se archivan fuera de la carpeta del
proyecto.

## Flujo obligatorio de publicación

1. Trabajar sólo en el clon local.
2. Ejecutar las pruebas relacionadas y revisar visualmente el cambio.
3. Revisar el alcance:

   ```bash
   git status --short
   git diff --check
   ```

4. Añadir explícitamente sólo los archivos del cambio, confirmar el commit y
   publicar:

   ```bash
   git add ruta/archivo
   git commit -m "Describe el resultado"
   git push origin main
   ```

5. Confirmar que el clon local queda limpio y que coincide con GitHub:

   ```bash
   git fetch origin main
   git status -sb
   git rev-parse HEAD
   git rev-parse origin/main
   ```

Los dos últimos identificadores deben ser iguales.

## Despliegue controlado en VNC

Antes de sincronizar, detener Astro-Nex. Desde el servidor VNC se actualiza
la copia de trabajo al commit publicado, sin editar archivos sueltos:

```bash
cd /home/ubuntu/astronex-github-vnc-test
git fetch origin main
git reset --hard origin/main
git clean -fd
DISPLAY=:1 nohup .venv/bin/python nex.py > /tmp/astronex.log 2>&1 &
```

`git clean -fd` elimina únicamente archivos no versionados de la carpeta de
trabajo. Antes de usarlo, archivar fuera del repositorio cualquier archivo
que deba conservarse. Nunca borra archivos ya versionados.

Después del despliegue, verificar:

```bash
git status --short
git rev-parse HEAD
git rev-parse origin/main
tail -50 /tmp/astronex.log
```

No debe haber salida en `git status --short` y ambos commits deben coincidir.

## Instaladores

Los instaladores se construyen únicamente desde un árbol local limpio que ya
coincide con `origin/main`. Después de comprobarlos, sus artefactos se añaden
explícitamente en un commit propio. No se construyen desde VNC ni desde una
carpeta con cambios sin confirmar.
