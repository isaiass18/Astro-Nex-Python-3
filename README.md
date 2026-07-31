# Astro-Nex para Python 3

## Probar Astro-Nex ahora, desde el navegador

**[Abrir Astro-Nex online](http://3.19.232.60:6080/vnc.html?autoconnect=1&resize=scale)**

Esta demostración abre la versión Linux en el navegador; no requiere
instalación. Es un servicio público de prueba.

## Ejecutar Astro-Nex

### Linux

⚠️ **Requisito de Sistema:** Astro-Nex requiere **Python 3.8 o superior**. Esto significa que es compatible con cualquier distribución Linux moderna (ej. Ubuntu 20.04 en adelante). Si usas un sistema antiguo (como Ubuntu 18.04 que usa Python 3.6), la aplicación te informará que tu versión de Python es muy antigua y no arrancará.

Tienes tres opciones para ejecutar Astro-Nex en Linux, dependiendo de tus preferencias:

**Opción 1: Paquete Universal (AppImage)** - *Recomendado para cualquier distribución*
1. **[Descarga el instalador Linux desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest)** (`Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`).
2. Haz clic derecho en el archivo, ve a "Propiedades" > "Permisos" y marca la casilla **"Permitir ejecutar el archivo como un programa"**.
3. Dale **doble clic** para abrirlo (no requiere instalación).

**Opción 2: Paquete Nativo (.deb)** - *Para Debian, Ubuntu, Mint, Pop!_OS*
1. Descarga el paquete `Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb` desde GitHub Releases.
2. Dale doble clic para instalarlo desde tu Centro de Software, o ejecuta en la terminal:
   `sudo apt install ./Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`

**Opción 3: Compilación Local (Script bash)**
Si prefieres instalar compilando el código fuente localmente desde la terminal:
```bash
./scripts/install_linux.sh
```
*(Si no tienes el código clonado, puedes descargar e instalar usando: `curl -fsSL https://raw.githubusercontent.com/isaiass18/Astro-Nex-Python-3/main/scripts/install_from_github.sh | bash`)*

### Windows 8, 10 y 11 (64 bits)

1. **[Descarga el instalador Windows desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest)** (`Astro-Nex-v2.0-beta-Windows-x64.exe`).
2. Sigue el asistente de instalación y ejecuta Astro-Nex desde el acceso
   creado por el instalador.

No hay que instalar Python, GTK ni dependencias adicionales.



Windows puede mostrar una advertencia porque el ejecutable todavía no está
firmado. Ejecuta únicamente una copia descargada de este repositorio oficial.

### macOS (Apple Silicon: M1, M2, M3 y M4)

1. **[Descarga el instalador macOS desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest)** (`Astro-Nex-v2.0-beta-macOS-arm64.dmg`).
2. Ábrelo con doble clic.
3. Copia `Astro-Nex.app` a la carpeta **Aplicaciones** y ábrelo desde allí.

Este instalador es para Macs con procesador Apple Silicon y macOS 26 o
posterior. Incluye Python, GTK3, el motor astronómico y la tipografía de
Astro-Nex; no hace falta instalar dependencias adicionales. La aplicación se
firma de forma ad-hoc, por lo que macOS puede solicitar una confirmación la
primera vez que se abre.

## Más información

- [Guía completa de la migración e instalación](guias/MIGRACION_PYTHON3.md)
- [Detalles del instalador Windows](Windows%20Instalador/README.md)
- [Cómo construir el instalador macOS](guias/CONSTRUIR_INSTALADOR_MACOS.md)
- [Instrucciones técnicas de instalación](INSTALL)

Astro-Nex fue migrado de Python 2/PyGTK a Python 3/GTK3. Linux, Windows y
macOS usan la misma fuente; los binarios nativos se construyen específicamente
para cada plataforma.
