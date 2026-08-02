# Construir Instalador para Linux (Paquete .deb y .AppImage)

Esta guía explica cómo construir los instaladores para Linux utilizando una arquitectura híbrida **Windows-AWS**.

Dado que construir entornos de Linux desde Windows o Mac puede ser problemático por la falta de librerías nativas, este proceso automatizado se conecta a una instancia remota de Linux en AWS, delega el trabajo pesado (compilación) en la nube y descarga automáticamente el instalador terminado en tu escritorio.

## 1. La Estrategia Dual

Astro-Nex soporta dos formatos de instalación para Linux y ambos comparten el
mismo AppImage autocontenido. Esto reduce las dependencias externas, aunque se
valida el arranque antes de publicar cada compilación.

1. **El paquete `.deb` (Envoltorio de AppImage)**:
   Es la opción recomendada para usuarios de Ubuntu, Mint o Debian. Integra el
   lanzador y el icono en el sistema. Internamente instala el mismo AppImage en
   `/opt/astro-nex/`; no es un paquete Python nativo ni descarga librerías.
   
2. **El `.AppImage` Autocontenido (Paquete Universal)**:
   Si el usuario usa Fedora, Arch, o simplemente prefiere una versión portátil
   que no requiera instalación ni permisos de administrador (`sudo`), esta
   opción empaqueta Python 3.8, GTK, `libffi.so.7` y las bibliotecas nativas que
   cargan sus extensiones. Así no depende de que el sistema tenga `libffi.so.7`
   o `libffi.so.8`.

## 2. Requisitos Previos

No necesitas instalar Docker en tu entorno local. Sólo requieres:
1. Tener la llave de seguridad SSH `astronext.pem` en la carpeta raíz del proyecto.
2. Contar con conexión a internet.
3. Para Windows: no se requieren programas adicionales.
4. Para Mac/Linux: tener instalada la terminal (`bash` o `zsh`) y el comando `ssh`.

## 3. Cómo construir los Instaladores

### En Windows:
1. Abre el Explorador de Archivos de Windows.
2. Navega a la carpeta: `Astro-Nex-1.2.3\Linux Instalador`
3. Dale doble clic al archivo `construir_linux.bat`.
4. Aparecerá un menú interactivo preguntando qué paquete deseas construir. Elige la opción deseada y presiona Enter.

### En Mac / Linux:
1. Abre la Terminal.
2. Navega a la carpeta: `cd ruta/a/Astro-Nex-1.2.3/Linux\ Instalador`
3. Ejecuta el script: `./construir_linux.sh`
4. Aparecerá un menú interactivo:
   - Opción 1: Construir AppImage autocontenido y el `.deb` que lo integra.
   - Opción 2: Construir solo el `.AppImage`.

**¿Qué hacen estos scripts automatizados?**
- Leen tu llave `astronext.pem`.
- Se conectan por SSH con `ServerAliveInterval=60` a `ubuntu@3.16.216.254`.
- Limpian el entorno temporal, clonan el código desde GitHub y copian la
  carpeta local `Linux Instalador` para usar los Dockerfiles de la revisión
  local.
- Construyen las imágenes Docker `astronex-builder` y `astronex-deb-builder`.
- Descargan el paquete terminado directo a tu carpeta local.
- Limpian los restos en el servidor.

El archivo resultante tendrá la nueva nomenclatura estándar:
- `Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`
- `Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`

## 4. Arquitectura y Mantenimiento

- `Dockerfile.appimage`: Usa `ubuntu:20.04` y descarga `linuxdeploy` y
  `linuxdeploy-plugin-gtk`. Además ejecuta `bundle_runtime_libs.sh`, que copia
  recursivamente las bibliotecas no glibc requeridas por Python/GTK, incluye
  `libffi.so.7`, ajusta el RPATH y falla si `ldd` detecta alguna dependencia
  sin resolver. Genera la imagen base `astronex-builder`.
- `Dockerfile.deb`: Es un Dockerfile muy ligero que simplemente toma el `.AppImage` resultante de `astronex-builder` y lo empaqueta dentro de la estructura estándar de Debian (`/DEBIAN/control`, `/opt/astro-nex/`, `/usr/share/applications/`) usando `dpkg-deb`.
- `AppRun`: Es el punto de entrada personalizado del `AppImage` que inyecta las
  rutas de GTK, Python, Pixbuf y las bibliotecas internas. Adicionalmente
  reescribe dinámicamente el `loaders.cache` para solucionar fallos con iconos
  SVG/PNG.
- `construir_linux.bat` / `.sh`: Es el puente que conecta tu entorno local con AWS. Si la IP del servidor AWS cambia, actualiza la variable `AWS_IP` dentro de estos archivos.
