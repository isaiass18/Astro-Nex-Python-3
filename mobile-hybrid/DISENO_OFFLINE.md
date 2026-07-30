# Diseño de la app móvil offline

**Referencia visual:** captura de la app móvil entregada el 29 de julio de
2026. El alcance de estos cambios es exclusivamente `mobile-hybrid/web`: no
usa la API remota ni altera el motor Swiss Ephemeris WASM, SQLite local o los
datos de la aplicación offline.

## Objetivo

La pantalla offline debe tener la misma apariencia iOS oscura de la app móvil
de referencia: títulos grandes, tarjetas agrupadas oscuras, esquinas muy
redondeadas, campos de fecha/hora en cápsulas, botón de ancho completo y
selector de cartas horizontal.

## Cambios aplicados

- Se sustituyó la capa visual genérica de Konsta por componentes locales con
  clases `offline-*`; el flujo de cálculo, búsqueda local y guardado de
  perfiles no cambia.
- Se ajustaron el fondo negro, la tipografía del sistema de iOS, los márgenes
  y la jerarquía de texto para que coincidan con la referencia.
- Los bloques “Datos de nacimiento” y “Lugar de nacimiento” ahora se muestran
  como tarjetas `#1c1c1e` con radio amplio y divisores internos.
- Fecha y hora se renderizan como cápsulas oscuras, y el interruptor y el
  botón principal toman las proporciones de la referencia.
- El menú circular, las pestañas de tipos de carta y las pantallas secundarias
  comparten el mismo lenguaje visual para no romper la consistencia después de
  calcular una carta.
- Se ajustó la escala móvil a puntos nativos de iPhone después de la primera
  instalación: títulos de 35 pt, secciones de 20 pt, filas de 17 pt y
  controles de 44–54 pt. Esto evita el efecto de interfaz ampliada.
- El menú circular se alineó más abajo dentro del encabezado para que no quede
  pegado al área de estado del iPhone.
- La pantalla Momento actual/Tránsitos usa ahora una tarjeta agrupada, selector
  de intervalo compacto y botones secundarios para los saltos; el único botón
  principal es “Actualizar momento”.
- Los botones `− Salto` y `+ Salto` ejecutan un paso inmediato y repiten cada
  150 ms después de 350 ms mientras se mantienen oprimidos; no seleccionan
  texto durante el gesto.

## Archivos modificados

- `web/src/components/ui/iOS.tsx`: primitivas de interfaz offline.
- `web/src/ios.css`: sistema visual y adaptación para pantallas estrechas.
- `web/src/main.tsx`: carga de los estilos de interfaz.

## Paridad del render de cartas

El renderer de la app debe tomar como fuente de verdad
`scripts/generate_chart_svg.mjs`, no el script alternativo `*_shifted` ni
versiones anteriores de los componentes React. Se alinearon el sistema Koch,
los anillos, las divisiones zodiacales ancladas al ascendente, las cúspides y
el tamaño de glifos planetarios. La paridad numérica de fecha/zona horaria se
valida de manera independiente con los golden fixtures. La entrada Golden Test
usa ahora el mismo nacimiento local (`1990-06-15 12:30`, America/Bogota) y la
app lo convierte a UTC antes del cálculo WASM.

## Verificación visual pendiente

Probar en un iPhone o simulador después de `npm run build` y comparar la
pantalla inicial a 393 × 852 pt con la captura de referencia. Los criterios
son: composición, tamaños de título/sección, radios de tarjetas, separadores,
campos y botón. El contenido debe seguir funcionando sin red.
