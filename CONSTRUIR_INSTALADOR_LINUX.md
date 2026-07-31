# Construir Instalador para Linux (Paquete .deb)

Esta guía explica cómo construir el instalador nativo `.deb` para Linux utilizando una arquitectura híbrida **Windows-AWS**.

Dado que Windows puede carecer de virtualización (Hyper-V) para correr Docker localmente, este proceso automatizado se conecta a una instancia remota de Linux en AWS, delega el trabajo pesado (compilación) en la nube y descarga automáticamente el instalador terminado en tu escritorio.

## 1. Adiós a PyInstaller, Hola Empaquetado Nativo

En el pasado, Astro-Nex intentó usar PyInstaller para Linux, pero fallaba constantemente por incompatibilidades con las librerías gráficas de GTK y Cairo. 

La solución definitiva e implementada actualmente es **Empaquetado Nativo**. El archivo `.deb` ya no es un ejecutable gigante de 100MB, sino un paquete ligero de 5MB que:
1. Copia el código fuente de Python directamente a `/usr/share/astronex`.
2. Declara las dependencias nativas en el sistema (ej. `python3-gi`, `python3-ipython`).
3. Usa la versión de Python del sistema operativo del usuario.

## 2. El "Sweet Spot" de Compatibilidad (Python 3.8+)

Aunque usemos tu servidor de AWS (que corre Ubuntu), la compilación de la librería en C (`_pysw.so`) ocurre **dentro de un contenedor Docker ligero de Python 3.9**.
- **El truco de compatibilidad:** Para garantizar que el instalador funcione en cualquier versión de Python 3.8+, el `Dockerfile` renombra automáticamente la librería compilada de `_pysw.cpython-39-x86_64-linux-gnu.so` a un genérico `_pysw.so`. De esta forma, cualquier versión moderna de Python puede cargar el motor astrológico.
- **Requisito mínimo:** Astro-Nex requiere **Python 3.8 o superior**. Si un usuario de Ubuntu 18.04 (Python 3.6) lo instala, el programa le mostrará educadamente un mensaje en la terminal indicando que su sistema es demasiado viejo, evitando así un fallo misterioso.

## 3. Requisitos Previos (En tu Windows)

No necesitas instalar Docker en Windows. Sólo requieres:
1. Tener la llave de seguridad SSH `astronext.pem` en la carpeta raíz del proyecto.
2. Contar con conexión a internet.

## 4. Cómo construir el Instalador (1 clic)

1. Abre el Explorador de Archivos de Windows.
2. Navega a la carpeta: `H:\Astro-Nex-1.2.3\Linux Instalador`
3. Dale doble clic al archivo `construir_deb.bat`.

**¿Qué hace este botón mágico?**
- Lee tu llave `astronext.pem`.
- Se conecta en silencio por SSH a tu instancia de AWS.
- Ejecuta Docker en la nube y compila el paquete `.deb` ligero usando el `Dockerfile` nativo.
- Usa el protocolo `scp` para enviarte el archivo `astronex_2.0_amd64.deb` terminado directo a tu carpeta de Windows.
- Limpia los restos en el servidor para no ocupar espacio.

## 5. Estructura y Mantenimiento

- `Dockerfile`: Reside en tu proyecto y contiene las instrucciones para el contenedor. Define las dependencias (`python3-gi`, `python3-ipython`, etc.), compila el código en C, renombra la librería para que sea universal, y arma la estructura `.deb`.
- `construir_deb.bat`: Es el puente que conecta tu entorno local de Windows con AWS. Si la IP del servidor cambia, actualiza la variable `AWS_IP` dentro de este archivo.
