# Correcciones recientes

Este archivo resume las correcciones funcionales más recientes de la versión
Python 3/GTK3. Para el detalle técnico completo, causa raíz y verificación,
véase también [REVISION_REPARACIONES.md](REVISION_REPARACIONES.md).

## 30 de julio de 2026 — overlays de calendario y diagrama en Pareja II

### Incidencia observada

En `Análisis de pareja II` el calendario (`Ctrl+A`) y el diagrama de barras
(`Ctrl+D`) dejaron de respetar la esquina visible superior. Aunque ya no se
abrían por defecto, al desplegarlos aparecían desplazados hacia la zona baja o
derecha de la carta. El problema también podía congelar la interfaz durante
unos segundos al alternar su visibilidad.

### Corrección

Se replicó el comportamiento funcional esperado del Astro-Nex original y se
reorganizó el montaje de estos paneles en GTK3:

- el selector de fecha y el diagrama dejaron de depender del `GtkLayout`
  scrolleable de la carta;
- ambos se montan ahora como overlays reales sobre el `ScrolledWindow`, para
  que su posición visible no herede el desplazamiento interno de `compo_two`;
- la sincronización con la barra de herramientas se mantiene al cambiar de
  carta para evitar estados “pegados” al entrar o salir de `Pareja II`;
- se conservó el ajuste previo de altura del navegador de cartas en macOS y la
  exclusión en Git de la copia local `Astro-Nex-1.2.3-inicial python2/`.

### Verificación

Se validó con pruebas GTK3 centradas en este flujo:

```bash
ASTRONEX_GUI_SMOKE=1 ./.venv-macos-build/bin/python -m unittest \
  tests.test_gui_smoke.GtkSmokeTest.test_chart_canvas_uses_scrolled_window_directly \
  tests.test_gui_smoke.GtkSmokeTest.test_extended_pair_chart_anchors_overlays_to_the_visible_area \
  tests.test_gui_smoke.GtkSmokeTest.test_toolbar_state_hides_stale_overlays
```

También se reconstruyó y probó visualmente el instalador macOS:

- `Mac Instalador/Astro-Nex-2.0-beta-20260730-131509-macos-arm64.dmg`
