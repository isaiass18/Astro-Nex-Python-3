# Astro-Nex para Python 3

## Probar Astro-Nex ahora, desde el navegador

**[Abrir Astro-Nex online](http://3.19.232.60:6080/vnc.html?autoconnect=1&resize=scale)**

Esta demostración abre la versión Linux en el navegador; no requiere
instalación. Es un servicio público de prueba.

## Ejecutar Astro-Nex

### Linux

Los instaladores AppImage y `.deb` incluyen su propio Python y bibliotecas
nativas, por lo que no requieren instalar Python ni `libffi` en el sistema. El
requisito de Python 3.8 o superior aplica solamente a la instalación desde el
código fuente.

Tienes tres opciones para ejecutar Astro-Nex en Linux, dependiendo de tus preferencias:

**Opción 1: Paquete `.deb` (integración Debian del AppImage)** - *Recomendado para Ubuntu, Mint, Debian, Pop!_OS*
1. **[Descarga el paquete Ubuntu 24.04 desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest/download/Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb)** (`Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`).
2. Dale doble clic para instalarlo desde tu Centro de Software, o ejecuta en la terminal:
   `sudo apt install ./Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`

> 💡 **Solución de problemas (GDebi/Centro de Software):** Si al darle doble clic al instalador el botón de "Instalar" no hace nada o se cierra silenciosamente (un fallo común de permisos gráficos en ciertos entornos Linux), puedes instalarlo de forma 100% segura e infalible desde la terminal. Abre una terminal en la carpeta donde descargaste el archivo y ejecuta:
> `sudo apt install ./Astro-Nex*.deb`

**Opción 2: Paquete Universal (AppImage)** - *Para cualquier otra distribución*
1. **[Descarga el instalador Linux desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest/download/Astro-Nex-v2.0-beta-Linux-x86_64.AppImage)** (`Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`).
2. Haz clic derecho en el archivo, ve a "Propiedades" > "Permisos" y marca la casilla **"Permitir ejecutar el archivo como un programa"**.
3. Dale **doble clic** para abrirlo (no requiere instalación).
> ⚠️ **Nota de Seguridad:** Linux por defecto bloquea la ejecución de archivos descargados de internet. Es obligatorio realizar el paso 2 (dar permisos de ejecución) o el sistema te arrojará un error diciendo que "no se puede abrir" o "no hay aplicación instalada para este archivo".

**Opción 3: Compilación Local (Script bash)**
Si prefieres instalar compilando el código fuente localmente desde la terminal:
```bash
./scripts/install_linux.sh
```
*(Si no tienes el código clonado, puedes descargar e instalar usando: `curl -fsSL https://raw.githubusercontent.com/isaiass18/Astro-Nex-Python-3/main/scripts/install_from_github.sh | bash`)*

### Windows 8, 10 y 11 (64 bits)

1. **[Descarga el instalador Windows desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/download/v2.0b0/Astro-Nex-v2.0-beta-Windows-x64.exe)** (`Astro-Nex-v2.0-beta-Windows-x64.exe`).
2. Sigue el asistente de instalación y ejecuta Astro-Nex desde el acceso creado.

> ⚠️ **Aviso de Seguridad (SmartScreen):** Como esta versión beta aún no cuenta con un certificado digital comercial, al abrir el instalador Windows mostrará una pantalla azul diciendo *"Windows protegió su PC"*. Para continuar la instalación de forma segura:
> 1. Haz clic en el texto que dice **"Más información"**.
> 2. Aparecerá un nuevo botón en la parte inferior; haz clic en **"Ejecutar de todas formas"**.

### macOS (Apple Silicon: M1, M2, M3 y M4)

1. **[Descarga el instalador macOS desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/download/v2.0b0/Astro-Nex-v2.0-beta-macOS-arm64.dmg)** (`Astro-Nex-v2.0-beta-macOS-arm64.dmg`).
2. Ábrelo con doble clic.
3. Copia `Astro-Nex.app` a la carpeta **Aplicaciones** y ábrelo desde allí.

> ⚠️ **Aviso de Seguridad (Gatekeeper):** Como la aplicación está firmada de forma "ad-hoc" (sin certificado comercial de Apple), macOS bloqueará la aplicación la primera vez que intentes abrirla, diciendo que *"no se puede verificar el desarrollador"* o que está *"dañada"*. Para solucionarlo:
> 1. Ve a **Configuración del Sistema** (o Preferencias del Sistema) > **Privacidad y Seguridad**.
> 2. Baja hasta el final de la pantalla.
> 3. Verás un mensaje indicando que se bloqueó el uso de Astro-Nex. Haz clic en el botón **"Abrir de todos modos"** o **"Permitir"**.
> 4. Te pedirá tu contraseña de Mac; ingrésala y la aplicación se abrirá sin problemas de ahí en adelante.

## Más información

- [Guía completa de la migración e instalación](guias/MIGRACION_PYTHON3.md)
- [Detalles del instalador Windows](Windows%20Instalador/README.md)
- [Cómo construir el instalador macOS](guias/CONSTRUIR_INSTALADOR_MACOS.md)
- [Instrucciones técnicas de instalación](INSTALL)

Astro-Nex fue migrado de Python 2/PyGTK a Python 3/GTK3. Linux, Windows y
macOS usan la misma fuente; los binarios nativos se construyen específicamente
para cada plataforma.
