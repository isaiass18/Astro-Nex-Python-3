# Astro-Nex para Windows

Esta carpeta contiene la distribución portable para Windows de 64 bits. Está
preparada para ejecutarse en **Windows 8 y Windows 10**.

## Inicio rápido

1. Mantén toda la carpeta `Astro-Nex` junta al copiarla o descomprimirla.
2. Abre `Astro-Nex`.
3. Ejecuta `Astro-Nex.exe` con doble clic.

No requiere una instalación previa de Python, GTK3 ni bibliotecas
adicionales. La carpeta `_internal` contiene el runtime Python, GTK3,
efemérides y los demás componentes requeridos por el ejecutable.

## Importante

- No copies ni muevas `Astro-Nex.exe` sin la carpeta `_internal`.
- Esta distribución se ha preparado para Windows 8/10 x86_64.
- Es posible que Windows muestre una advertencia de reputación porque el
  ejecutable no está firmado. Comprueba que lo descargaste de este repositorio
  antes de ejecutarlo.

Para compilar o modificar el programa desde el código fuente, consulta
[`../MIGRACION_PYTHON3.md`](../MIGRACION_PYTHON3.md).
