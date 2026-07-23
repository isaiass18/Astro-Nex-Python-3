# Astro-Nex para Python 3

## Probar Astro-Nex ahora, desde el navegador

**[Abrir Astro-Nex online](http://3.19.232.60:6080/vnc.html?autoconnect=1&resize=scale)**

Esta demostración abre la versión Linux en el navegador; no requiere
instalación. Es un servicio público de prueba.

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
2. Abre `Windows Instalador\Astro-Nex-Setup.exe`.
3. Sigue el asistente de instalación y ejecuta Astro-Nex desde el acceso
   creado por el instalador.

No hay que instalar Python, GTK ni dependencias adicionales. Como alternativa
portable, se puede abrir `Windows Instalador\Astro-Nex\Astro-Nex.exe`, pero
no se debe mover ese EXE sin su carpeta `_internal`.

Windows puede mostrar una advertencia porque el ejecutable todavía no está
firmado. Ejecuta únicamente una copia descargada de este repositorio oficial.

## Más información

- [Guía completa de la migración e instalación](MIGRACION_PYTHON3.md)
- [Detalles del instalador Windows](Windows%20Instalador/README.md)
- [Instrucciones técnicas de instalación](INSTALL)

Astro-Nex fue migrado de Python 2/PyGTK a Python 3/GTK3. Linux y Windows usan
la misma fuente; los binarios nativos se construyen específicamente para cada
plataforma.
