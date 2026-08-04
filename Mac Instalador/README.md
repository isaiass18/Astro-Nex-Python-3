# Astro-Nex 2.0 beta para macOS

Este directorio es el entorno de compilación para el instalador:

```text
Astro-Nex-v2.0-beta-macOS-arm64.dmg
```

👉 **[Descargar instalador para macOS desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/download/v2.0b0/Astro-Nex-v2.0-beta-macOS-arm64.dmg)**

## Compatibilidad

Esta compilación funciona únicamente en:

- Macs con procesador Apple Silicon: M1, M2, M3, M4 o posterior.
- macOS 26.0 o posterior.

No es compatible con Macs Intel ni con macOS 11, 12, 13, 14 o 15. Esos
equipos requieren una compilación específica.

## Instalación

1. Descargar el archivo `.dmg`.
2. Abrirlo con doble clic.
3. Arrastrar `Astro-Nex.app` a la carpeta `Aplicaciones`.
4. Abrir Astro-Nex desde `Aplicaciones`.

La aplicación ya incluye Python, GTK3, el motor astronómico y la fuente de
símbolos `Astro-Nex.ttf`. La fuente se registra sólo mientras Astro-Nex está
abierto: no es necesario instalar Python, GTK, Homebrew ni la fuente en macOS.

## Migrar datos de una instalación anterior

Astro-Nex 2 guarda sus datos en `~/.astronex-v2/`. Si ya usabas Astro-Nex,
puedes copiar tus datos anteriores a esa carpeta:

1. Cierra Astro-Nex si está abierto.
2. Abre **Finder** y selecciona **Ir > Ir a la carpeta...** (`Mayusculas + Cmd + G`).
3. Escribe `~/.astronex/` y pulsa **Ir**. Esta es la carpeta de Astro-Nex 1.
4. Copia `charts.db`, `customloc.db` y `cfg.ini`.
5. En Finder, vuelve a usar **Ir > Ir a la carpeta...** y escribe
   `~/.astronex-v2/`.
6. Pega los archivos. Si macOS pregunta si deseas reemplazarlos, conserva una
   copia de los existentes antes de confirmar.

La carpeta `~/.astronex-v2/` se crea al abrir Astro-Nex 2 por primera vez. Si
no existe todavía, abre y cierra la aplicación una vez y repite los pasos 5 y
6.

Ahí se encuentran los archivos principales:

- `charts.db`: las personas y cartas creadas.
- `customloc.db`: las ubicaciones personalizadas.
- `cfg.ini`: la configuración, colores y preferencias.

Si usabas Astro-Nex 1, su carpeta anterior se llama `~/.astronex/`, sin el
sufijo `-v2`.

## Primera apertura

El paquete está firmado de forma "ad-hoc" pero todavía no cuenta con un certificado comercial de desarrollador de Apple. Por este motivo, macOS puede bloquear la aplicación la primera vez que intentes abrirla, mostrando un mensaje que dice *"no se puede verificar el desarrollador"* o que está *"dañada"*. 

Para solucionarlo y permitir que macOS conozca el origen del programa, sigue estos pasos:

1. Ve a **Configuración del Sistema** (o Preferencias del Sistema) > **Privacidad y Seguridad**.
2. Baja hasta el final de la pantalla.
3. Verás un mensaje indicando que se bloqueó el uso de Astro-Nex. Haz clic en el botón **"Abrir de todos modos"** o **"Permitir"**.
4. Te pedirá tu contraseña de Mac; ingrésala y la aplicación se abrirá sin problemas de ahí en adelante.

La guía para reconstruir este instalador está en
[`CONSTRUIR_INSTALADOR_MACOS.md`](../guias/CONSTRUIR_INSTALADOR_MACOS.md).
