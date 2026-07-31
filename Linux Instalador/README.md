# Astro-Nex 2.0 beta para Linux

Este directorio es el entorno de compilación para los instaladores:

```text
Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb
Astro-Nex-v2.0-beta-Linux-x86_64.AppImage
```

👉 **[Descargar instaladores para Linux desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest)**

## 🛠️ Cómo instalar en Linux

Si vas a instalar Astro-Nex en un equipo con Ubuntu, Linux Mint, Debian u otra distribución derivada, estas son las instrucciones que debes seguir:

### Opción A: Instalación Gráfica (Fácil)
1. Descarga el archivo `Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb` desde GitHub.
2. Dale **doble clic** al archivo.
3. Se abrirá el Centro de Software (o el Instalador de Paquetes GDebi).
4. Haz clic en **Instalar** y pon tu contraseña de administrador.
5. ¡Listo! Busca Astro-Nex en el menú de aplicaciones de tu sistema.

### Opción B: Instalación por Terminal (Avanzada)
Abre la terminal en la carpeta donde descargaste el archivo y ejecuta:

```bash
sudo apt install ./Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb
```
*(Usar `apt` en lugar de `dpkg` asegura que cualquier pequeña dependencia faltante del sistema operativo, como librerías base, se instale automáticamente).*

### Opción C: Paquete Universal (AppImage)
Si prefieres no instalar nada en el sistema o usas una distribución diferente (como Fedora, Arch, etc.):
1. Descarga el archivo `Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`.
2. Haz clic derecho, ve a **Propiedades** > **Permisos** y marca **"Permitir ejecutar el archivo como un programa"**.
3. Dale doble clic para ejecutar.

> ⚠️ **Aviso de Seguridad:** Linux por defecto bloquea la ejecución de archivos descargados de internet. Es obligatorio realizar el paso 2 (dar permisos de ejecución) o el sistema te arrojará un error diciendo que *"no se puede abrir"* o *"no hay aplicación instalada para este archivo"*.

### ⚠️ Requisitos de Sistema (Importante)
Astro-Nex requiere **Python 3.8 o superior**. Esto significa que es compatible con cualquier distribución Linux moderna (ej. Ubuntu 20.04 en adelante). 

**¿Por qué?** El código fuente de Astro-Nex ha sido actualizado para utilizar herramientas de programación modernas de Python (como el manejo avanzado de rutas de archivos). Si intentas instalar esto en una versión de Linux muy antigua (como Ubuntu 18.04 que trae Python 3.6), el instalador funcionará, pero al abrir el programa recibirás un mensaje indicando que tu versión de Python es demasiado antigua.
