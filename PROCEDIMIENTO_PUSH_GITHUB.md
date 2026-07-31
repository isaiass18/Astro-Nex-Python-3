# Publicar cambios en GitHub

Este documento describe el procedimiento para subir cambios de Astro-Nex al
repositorio público:

<https://github.com/isaiass18/Astro-Nex-Python-3>

## Antes de publicar

1. Revisar los archivos modificados:

   ```bash
   git status --short
   git diff --check
   ```

2. Ejecutar las pruebas relacionadas con el cambio. Para la interfaz GTK3 en
   macOS:

   ```bash
   ASTRONEX_GUI_SMOKE=1 ./.venv-macos-build/bin/python -m unittest discover -s tests
   ```

3. Si el cambio afecta el instalador de macOS, reconstruir el único DMG de
   prueba/publicación:

   ```bash
   ./scripts/build_macos.sh
   ```

4. Verificar manualmente la función modificada antes de publicar. No se debe
   subir una corrección que sólo pase una prueba automática si su interfaz no
   funciona visualmente.

## Preparar el commit

Se agregan **únicamente** los archivos que pertenecen al cambio. No usar
`git add .` ni `git add -A` en este proyecto, porque puede haber capturas,
archivos temporales, instaladores de prueba o cambios aún no aprobados.

Ejemplo:

```bash
git add astronex/gui/mainnb.py \
        astronex/surfaces/layoutsurface.py \
        tests/test_gui_smoke.py \
        REVISION_REPARACIONES.md
```

Comprobar lo que entrará en el commit:

```bash
git diff --cached --check
git diff --cached --stat
git diff --cached
```

## Crear y subir el commit

El repositorio remoto configurado se llama `origin` y apunta a:

```text
https://github.com/isaiass18/Astro-Nex-Python-3.git
```

Crear un mensaje breve que describa el resultado, no sólo el archivo tocado:

```bash
git commit -m "Corrige calendario GTK3 en macOS"
git push origin main
```

Después, comprobar que no quedan cambios preparados por error y que la rama
local está sincronizada:

```bash
git status
git log -1 --oneline
```

## Si se actualiza el instalador (Publicación en GitHub Releases)

**IMPORTANTE:** Para mantener el repositorio ligero y rápido de clonar, **NUNCA debes incluir los archivos binarios compilados** (`.exe`, `.dmg`, `.deb`, `.AppImage`) ni las carpetas pesadas (como `Windows Instalador/Astro-Nex/`) dentro de un `commit` de Git. Todos estos archivos ya están ignorados por el `.gitignore`.

Cuando una modificación de código debe estar disponible para usuarios finales como un instalador:

1. Realiza tus pruebas locales normalmente y asegúrate de que todo funcione.
2. Construye el instalador final que necesites (ej. `Astro-Nex-v2.0-beta-Windows-x64.exe`, `.dmg`, `.AppImage`, o `.deb`).
3. Haz `git commit` y `git push` **únicamente del código fuente**, asegurándote de incluir cualquier cambio en los scripts de compilación (`installer.iss`, `Dockerfile`, `.sh`, `.bat`).
4. Ve a la página de tu repositorio en GitHub y navega a la sección **"Releases"**.
5. Crea un nuevo "Release" (por ejemplo: `v2.0.1`), pega las notas de la versión, y **arrastra los instaladores finales compilados** a la caja de archivos adjuntos (Assets).
6. Haz clic en "Publish release". 

De esta manera, los usuarios podrán descargar la versión más reciente del instalador directamente desde GitHub sin inflar el historial de código.

## Regla de seguridad

No incluir en GitHub llaves `.pem`, contraseñas, tokens, direcciones IP de
instancias, bases de datos privadas de usuarios, archivos de configuración
local ni capturas que contengan información sensible.

Antes de cada `git add`, revisar la ruta exacta de cada archivo.
