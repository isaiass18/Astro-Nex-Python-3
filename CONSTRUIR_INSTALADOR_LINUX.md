# Construir Instalador para Linux (Paquete .deb y .AppImage)

Esta guía explica cómo construir los instaladores para Linux utilizando una arquitectura híbrida **Windows-AWS**.

Dado que construir entornos de Linux desde Windows o Mac puede ser problemático por la falta de librerías nativas, este proceso automatizado se conecta a una instancia remota de Linux en AWS, delega el trabajo pesado (compilación) en la nube y descarga automáticamente el instalador terminado en tu escritorio.

## 1. La Estrategia Dual

Astro-Nex soporta dos formatos de instalación para Linux:

1. **El paquete `.deb` Nativo (Para Ubuntu/Debian/Mint)**: 
   Es la opción recomendada para estas distribuciones. El instalador pesa solo ~5MB ya que aprovecha las dependencias del sistema (Python, GTK, temas gráficos) y se integra nativamente. A cambio, los ejecutables `.so` (como el cálculo de efemérides) deben coincidir con la versión de Python del sistema. Por ello, el script permite elegir para qué versión de Ubuntu construirlo.
   
2. **El `.AppImage` Autocontenido (Para Fedora, Arch, o portabilidad)**:
   Si el usuario no tiene Ubuntu o prefieres enviar un instalador universal, esta opción empaqueta todo: Python 3.8, librerías GTK, `_pysw.so`, fuentes y recursos en un solo archivo de ~60-100MB. Este AppImage se construye basado en Ubuntu 20.04 garantizando compatibilidad con cualquier distribución igual o más reciente.

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
4. Aparecerá un menú interactivo. Ingresa el número de tu elección y presiona Enter.

**¿Qué hacen estos scripts automatizados?**
- Leen tu llave `astronext.pem`.
- Se conectan en silencio por SSH a tu instancia de AWS.
- Ejecutan Docker en la nube, usando el archivo de configuración correspondiente.
- Descargan el paquete `.deb` o `.AppImage` terminado directo a tu carpeta local.

El archivo resultante tendrá la nueva nomenclatura estándar:
- `Astro-Nex-v2.0-beta-Ubuntu22.04-amd64.deb`
- `Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`
- `Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`
- Limpian los restos en el servidor.

## 4. Estructura y Mantenimiento

- `Dockerfile.deb`: Define cómo se empaqueta el archivo `.deb`. Acepta un argumento `UBUNTU_VER` para garantizar que la compilación de C (`_pysw.so`) coincida con la versión de Python de ese Ubuntu (ej. 22.04 o 24.04).
- `Dockerfile.appimage`: Usa `ubuntu:20.04` y descarga `linuxdeploy` y `linuxdeploy-plugin-gtk` para empaquetar una versión autocontenida de Python y GTK sin depender del sistema del usuario.
- `AppRun`: Es el punto de entrada personalizado del `AppImage` que inyecta manualmente las rutas correctas (GTK, Python, Typelibs) para que Astro-Nex inicie de forma transparente.
- `construir_linux.bat` / `.sh`: Es el puente que conecta tu entorno local con AWS. Si la IP del servidor AWS cambia, actualiza la variable `AWS_IP` dentro de estos archivos.
