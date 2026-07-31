# Construir Instalador para Linux (Paquete .deb)

Esta guía explica cómo construir el instalador nativo `.deb` para Linux utilizando una arquitectura híbrida **Windows-AWS**.

Dado que Windows puede carecer de virtualización (Hyper-V) para correr Docker localmente, este proceso automatizado se conecta a una instancia remota de Linux en AWS, delega el trabajo pesado (compilación) en la nube y descarga automáticamente el instalador terminado en tu escritorio.

## 1. El "Sweet Spot" de Compatibilidad (Ubuntu 18.04)

Aunque usemos tu servidor de AWS (que corre Ubuntu 26), la compilación real ocurre **dentro de un contenedor Docker de Ubuntu 18.04** alojado en ese servidor.
- **¿Por qué Ubuntu 18.04?:** Para garantizar que el instalador funcione en la mayor cantidad de versiones de Linux posibles (desde 2018 hasta 2026+). Si compilaras directo en el Ubuntu 26 de tu servidor, el instalador exigiría librerías modernas (`glibc`) y fallaría en sistemas viejos.

## 2. Requisitos Previos (En tu Windows)

No necesitas instalar Docker en Windows. Sólo requieres:
1. Tener la llave de seguridad SSH `astronext.pem` en la carpeta raíz del proyecto.
2. Contar con conexión a internet.

## 3. Cómo construir el Instalador (1 clic)

1. Abre el Explorador de Archivos de Windows.
2. Navega a la carpeta: `H:\Astro-Nex-1.2.3\Linux Instalador`
3. Dale doble clic al archivo `construir_deb.bat`.

**¿Qué hace este botón mágico?**
- Lee tu llave `astronext.pem`.
- Se conecta en silencio por SSH a tu instancia de pruebas (`3.138.192.48`).
- Ejecuta Docker en la nube, clona el código más fresco, y empaqueta el sistema en Ubuntu 18.04.
- Usa el protocolo `scp` para enviarte el archivo `astronex_2.0_amd64.deb` terminado directo a tu carpeta de Windows.
- Limpia los restos en el servidor para no ocupar espacio.

## 4. Estructura y Mantenimiento

- `Dockerfile`: Reside en tu proyecto y contiene las instrucciones para el contenedor (Python 3.9, GTK3, PyInstaller y creación del DEBIAN/control).
- `construir_deb.bat`: Es el puente que conecta tu entorno local de Windows con AWS. Si la IP del servidor cambia, actualiza la variable `AWS_IP` dentro de este archivo.
