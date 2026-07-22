# Astro-Nex para Python 3

## Ejecutar Astro-Nex

### Linux (Ubuntu/Debian)

Si ya descargaste o clonaste este repositorio, abre una Terminal dentro de su
carpeta y ejecuta:

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

### Windows 8 y Windows 10 (64 bits)

1. Descarga el repositorio como ZIP desde **Code → Download ZIP** y
   descomprímelo.
2. Entra en `windows Instalador\Astro-Nex`.
3. Ejecuta `Astro-Nex.exe` con doble clic.

No hay que instalar Python, GTK ni dependencias adicionales: esta distribución
portable incluye el runtime necesario. **No muevas sólo el EXE**; debe quedar
junto a la carpeta `_internal`.

Windows puede mostrar una advertencia porque el ejecutable todavía no está
firmado. Ejecuta únicamente una copia descargada de este repositorio oficial.

## Más información

- [Guía completa de la migración e instalación](MIGRACION_PYTHON3.md)
- [Detalles del paquete portable de Windows](windows%20Instalador/README.md)
- [Instrucciones técnicas de instalación](INSTALL)

Astro-Nex fue migrado de Python 2/PyGTK a Python 3/GTK3. Linux y Windows usan
la misma fuente; los binarios nativos se construyen específicamente para cada
plataforma.
