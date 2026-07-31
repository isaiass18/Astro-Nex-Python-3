# Astro-Nex para Python 3

## Probar Astro-Nex ahora, desde el navegador

**[Abrir Astro-Nex online](http://3.19.232.60:6080/vnc.html?autoconnect=1&resize=scale)**

Esta demostración abre la versión Linux en el navegador; no requiere
instalación. Es un servicio público de prueba.

## Ejecutar Astro-Nex

### Linux (Ubuntu/Debian)

⚠️ **Requisito de Sistema:** Astro-Nex requiere **Python 3.8 o superior**. Esto significa que es compatible con cualquier distribución Linux moderna (ej. Ubuntu 20.04 en adelante). Si usas un sistema antiguo (como Ubuntu 18.04 que usa Python 3.6), la aplicación te informará que tu versión de Python es muy antigua y no arrancará.

La forma principal y más sencilla de instalar Astro-Nex en sistemas basados en Debian y Ubuntu es utilizando el instalador precompilado `.deb`.

1. **[Descarga el instalador Linux desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest)** (`Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`).
2. Dale **doble clic** al archivo para instalarlo visualmente desde tu Centro de Software.
   *(Alternativamente, puedes instalarlo desde la terminal ejecutando `sudo apt install ./Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb` en la carpeta de descargas).*

#### Método Alternativo (Script de instalación local)

**NOTA IMPORTANTE:** El script local hace exactamente el mismo proceso y tiene el mismo requisito de **Python 3.8 o superior**. Solo utiliza este script si el archivo `.deb` te da problemas de dependencias en tu distribución particular.

Si prefieres instalar Astro-Nex compilando el código fuente localmente, abre una Terminal dentro de la carpeta del proyecto y ejecuta:

```bash
./scripts/install_linux.sh
```

El instalador instala los requisitos de GTK3, crea el entorno Python, compila
el motor astronómico, instala la tipografía y crea un acceso en el menú de
aplicaciones.

Si aún no tienes el código, puedes descargar e instalar todo directamente
desde GitHub con:

```bash
curl -fsSL https://raw.githubusercontent.com/isaiass18/Astro-Nex-Python-3/main/scripts/install_from_github.sh | bash
```

Para que el instalador ejecute también las pruebas:

```bash
./scripts/install_linux.sh --test
```

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
