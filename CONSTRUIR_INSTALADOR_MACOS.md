# Construir el instalador de macOS

Esta guía genera un DMG autocontenido para **macOS Apple Silicon** (M1, M2,
M3 o M4). El usuario final no necesita instalar Python, GTK ni Homebrew.

El resultado es:

```text
Mac Instalador/Astro-Nex-2.0-beta-macos-arm64.dmg
```

## Alcance

- Arquitectura: `arm64` / Apple Silicon.
- Versión de Astro-Nex: 2.0 beta.
- Compatibilidad del DMG actual: macOS 26.0 o posterior.
- El paquete contiene la aplicación `Astro-Nex.app`, Python, GTK3, el motor
  astronómico compilado y todos los recursos.
- Para Intel se debe crear una compilación separada desde un Mac Intel o un
  entorno de compilación Intel. No distribuir un DMG ARM64 como si fuera
  compatible con Intel.
- Para macOS 11–15 se necesita una compilación separada con Python, GTK y el
  SDK de una versión compatible; este paquete no debe anunciarse como apto
  para esas versiones.

## Requisitos del Mac de compilación

1. macOS en un Mac Apple Silicon.
2. Herramientas de línea de comandos de Xcode:

   ```bash
   xcode-select --install
   ```

3. Homebrew y las bibliotecas de GTK:

   ```bash
   brew install python gtk+3 pygobject3 harfbuzz graphite2 glib pkg-config
   ```

4. Una copia actualizada del repositorio:

   ```bash
   git clone https://github.com/isaiass18/Astro-Nex-Python-3.git
   cd Astro-Nex-Python-3
   ```

## Compilación automática

El script crea un entorno de compilación local, compila `_pysw`, genera la
aplicación con PyInstaller, incluye GTK3 y crea el DMG.

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

No sobrescribe un DMG existente. Para generar el archivo en otra carpeta,
pasar una ruta como argumento:

```bash
./scripts/build_macos.sh "$HOME/Desktop/Astro-Nex-macOS"
```

El script trata explícitamente una incompatibilidad entre HarfBuzz incluido
por Pillow y GTK de Homebrew. Este paso es necesario para que el `.app` abra
sin depender del Homebrew instalado en el Mac del usuario final.

## Verificación antes de distribuir

1. Abrir el DMG generado.
2. Copiar `Astro-Nex.app` a `Aplicaciones`.
3. Abrir la aplicación y comprobar que aparece la ventana principal y la
   portada 2.0 beta.
4. Probar F1, la entrada de datos, clic derecho en la carta, exportación y el
   calendario.
5. Comprobar la firma local:

   ```bash
   codesign --verify --deep --strict \
     "/Applications/Astro-Nex.app"
   ```

La compilación se firma de forma ad-hoc. Para evitar advertencias de Gatekeeper
al distribuir fuera de GitHub, se necesita una cuenta de Apple Developer para
firmar con un certificado de distribución y notarizar el DMG. No publicar una
versión como “notarizada” si no se ha realizado ese proceso.

## Publicar desde macOS en GitHub

Primero comprobar qué ha cambiado. No incluir entornos virtuales, directorios
temporales ni archivos personales:

```bash
git status -sb
git fetch origin main
git rebase origin/main
```

Revisar las modificaciones y añadir únicamente los archivos que se quieren
publicar. Para publicar la documentación, el script y un DMG ya probado:

```bash
git add \
  CONSTRUIR_INSTALADOR_MACOS.md \
  scripts/build_macos.sh \
  macos_entry.py \
  "Mac Instalador/Astro-Nex-2.0-beta-macos-arm64.dmg"
git commit -m "Add macOS Apple Silicon installer"
git push origin main
```

Si otra persona ha publicado cambios mientras se construía el DMG, ejecutar
antes de `push`:

```bash
git fetch origin main
git rebase origin/main
```

Resolver cualquier conflicto, volver a verificar el DMG y sólo entonces hacer
el `push`. Tras publicarlo, comprobar que GitHub muestra el archivo y su
tamaño completo.
