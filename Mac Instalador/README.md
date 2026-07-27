# Astro-Nex 2.0 beta para macOS

Este directorio contiene el instalador:

```text
Astro-Nex-2.0-beta-macos-arm64.dmg
```

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

## Primera apertura

El paquete está firmado localmente, pero todavía no está notarizado por Apple.
macOS puede mostrar una advertencia la primera vez que se abra. En ese caso,
hacer clic con el botón derecho sobre `Astro-Nex.app`, elegir **Abrir** y
confirmar la apertura.

La guía para reconstruir este instalador está en
[`CONSTRUIR_INSTALADOR_MACOS.md`](../CONSTRUIR_INSTALADOR_MACOS.md).
