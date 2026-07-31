# Astro-Nex - Instalador de Linux (.deb)

Este directorio contiene el instalador oficial de Astro-Nex empaquetado para distribuciones Linux basadas en Debian y Ubuntu.

## 🛠️ Cómo instalar en Linux

Si vas a instalar Astro-Nex en un equipo con Ubuntu, Linux Mint, Debian u otra distribución derivada, estas son las instrucciones que debes seguir:

### Opción A: Instalación Gráfica (Fácil)
1. Descarga el archivo `astronex_2.0_amd64.deb`.
2. Dale **doble clic** al archivo.
3. Se abrirá el Centro de Software (o el Instalador de Paquetes GDebi).
4. Haz clic en **Instalar** y pon tu contraseña de administrador.
5. ¡Listo! Busca Astro-Nex en el menú de aplicaciones de tu sistema.

### Opción B: Instalación por Terminal (Avanzada)
Abre la terminal en la carpeta donde descargaste el archivo y ejecuta:

```bash
sudo apt install ./astronex_2.0_amd64.deb
```
*(Usar `apt` en lugar de `dpkg` asegura que cualquier pequeña dependencia faltante del sistema operativo, como librerías base, se instale automáticamente).*

### ⚠️ Requisitos de Sistema (Importante)
Astro-Nex requiere **Python 3.8 o superior**. Esto significa que es compatible con cualquier distribución Linux moderna (ej. Ubuntu 20.04 en adelante). 

**¿Por qué?** El código fuente de Astro-Nex ha sido actualizado para utilizar herramientas de programación modernas de Python (como el manejo avanzado de rutas de archivos). Si intentas instalar esto en una versión de Linux muy antigua (como Ubuntu 18.04 que trae Python 3.6), el instalador funcionará, pero al abrir el programa recibirás un mensaje indicando que tu versión de Python es demasiado antigua.
