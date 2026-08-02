# Astro-Nex 2.0 beta para Linux

Este directorio es el entorno de compilación para los instaladores:

```text
Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb
Astro-Nex-v2.0-beta-Linux-x86_64.AppImage
```


## 🛠️ Cómo instalar en Linux

Si vas a instalar Astro-Nex en un equipo con Ubuntu, Linux Mint, Debian u otra distribución derivada, estas son las instrucciones que debes seguir:

### Opción A: Instalación Gráfica (Fácil)
1. **[Descarga el paquete Ubuntu 24.04 desde GitHub](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest/download/Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb)** (`Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb`).
2. Dale **doble clic** al archivo.
3. Se abrirá el Centro de Software (o el Instalador de Paquetes GDebi).
4. Haz clic en **Instalar** y pon tu contraseña de administrador.
5. ¡Listo! Busca Astro-Nex en el menú de aplicaciones de tu sistema.

> 💡 **Solución de problemas:** Si al presionar "Instalar" la ventana no hace nada o se cancela silenciosamente (un fallo común de permisos en algunas versiones de Linux), abre una terminal en esa misma carpeta y ejecuta: `sudo apt install ./Astro-Nex*.deb`

### Opción B: Paquete Universal (AppImage)
Si prefieres no instalar nada en el sistema o usas una distribución diferente (como Fedora, Arch, etc.):
1. **[Descarga el AppImage (Paquete Universal) desde GitHub](https://github.com/isaiass18/Astro-Nex-Python-3/releases/latest/download/Astro-Nex-v2.0-beta-Linux-x86_64.AppImage)** (`Astro-Nex-v2.0-beta-Linux-x86_64.AppImage`).
2. Haz clic derecho, ve a **Propiedades** > **Permisos** y marca **"Permitir ejecutar el archivo como un programa"**.
3. Dale doble clic para ejecutar.

> ⚠️ **Aviso de Seguridad:** Linux por defecto bloquea la ejecución de archivos descargados de internet. Es obligatorio realizar el paso 2 (dar permisos de ejecución) o el sistema te arrojará un error diciendo que *"no se puede abrir"* o *"no hay aplicación instalada para este archivo"*.

### Opción C: Instalación por Terminal (Avanzada)
Abre la terminal en la carpeta donde descargaste el instalador `.deb` y ejecuta:

```bash
sudo apt install ./Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb
```
*(Usar `apt` en lugar de `dpkg` asegura que cualquier pequeña dependencia faltante del sistema operativo, como librerías base, se instale automáticamente).*

### Requisitos de Sistema
El AppImage contiene Python 3.8, GTK y sus dependencias nativas, incluida
`libffi.so.7`; el `.deb` instala ese mismo AppImage en `/opt/astro-nex/`.
Por ello ninguno requiere Python ni `libffi` preinstalados. Se necesita una
distribución Linux de 64 bits, permisos de ejecución y un entorno gráfico GTK.

El requisito de Python 3.8 o superior aplica sólo si se instala directamente
desde el código fuente con `scripts/install_linux.sh`.
