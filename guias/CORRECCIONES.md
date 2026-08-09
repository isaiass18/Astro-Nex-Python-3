# Correcciones recientes

Este archivo resume las correcciones funcionales más recientes de la versión
Python 3/GTK3. Para el detalle técnico completo, causa raíz y verificación,
véase también [REVISION_REPARACIONES.md](REVISION_REPARACIONES.md).

## 8 de agosto de 2026 — diagnósticos macOS: configuración, búsqueda y tablas

Se corrigieron tres fallos identificados en los diagnósticos remotos de macOS:

- `ConfigObj` abre y guarda `cfg.ini` explícitamente como UTF-8, por lo que
  localidades y países con acentos no producen `UnicodeEncodeError`.
- El buscador cancela su temporizador de forma segura y no intenta eliminar dos
  veces el mismo `Source ID` de GLib.
- Las operaciones de cartas validan el nombre de tabla antes de crear SQL.
  `Buscar` y `None` ya no pueden convertirse en consultas SQLite; al guardar
  desde la búsqueda se usa la tabla configurada válida, y Copiar/Cortar toma la
  tabla de origen de cada resultado global.

La advertencia interna GTK `g_value_get_int` no se modificó: los registros no
aportan una traza que permita atribuirla a una llamada concreta con seguridad.

### Verificación

- Compilación sintáctica de los cinco módulos modificados y `git diff --check`.
- Prueba UTF-8 de lectura y escritura con `España` y `Las Rozas de Madrid`.
- Prueba SQLite que confirma que `Buscar` y `None` se rechazan sin
  `OperationalError`.
- DMG Apple Silicon reconstruido y verificado con `hdiutil verify`.

DMG: `Astro-Nex-v2.0-beta-macOS-arm64.dmg`
(SHA-256 `94eb0a4a467ba43cd9f98007b2b8fed567c3e771dbb8a597a58e6e8e74d2bb20`).

## 8 de agosto de 2026 — nueva entrada limpia tras guardar en macOS

Al crear y guardar una persona, `Data entry` quedaba oculto en vez de
cerrarse. Al pulsar de nuevo `Ctrl+E`, Astro-Nex reutilizaba la misma instancia
GTK y mostraba el nombre, fecha y localidad de la entrada anterior. El fallo
no era exclusivo de macOS: correspondía al flujo GTK3 compartido.

Ahora Guardar, Cancelar, Escape y el cierre nativo destruyen el diálogo y
liberan su referencia en la ventana principal. Cada `Ctrl+E` crea así una
entrada nueva y restablece explícitamente nombre y apellidos. `Ctrl+Shift+E`
conserva su comportamiento intencional: carga la carta actual para editarla.

### Verificación

- Compilación de `astronex/gui/entry_dlg.py` con el entorno macOS.
- `git diff --check` sin errores.
- DMG Apple Silicon reconstruido, con firma ad-hoc verificada y `hdiutil verify`
  correcto.
- Recursos, base local y traducciones comparados byte a byte entre la fuente y
  el DMG; no faltan archivos.

DMG publicado: `Astro-Nex-v2.0-beta-macOS-arm64.dmg`
(SHA-256 `78488fcd6cf0b8efbeba7ba11117b27b195f5dc808c790e93e644e2c645ea7e3`).

## 4 de agosto de 2026 — arranque macOS con Python 3.14 y Expat

El DMG para Apple Silicon podía cerrarse al arrancar al cargar `pyexpat`: la
extensión de Python 3.14 buscaba el símbolo
`_XML_SetAllocTrackerActivationThreshold` en la Expat del sistema, que no lo
incluye en las versiones de macOS afectadas. El error del visor IPython
histórico además se convertía en un `TypeError` porque conservaba un `raise`
de Python 2.

El empaquetador macOS incluye ahora `libexpat.1.dylib` dentro de
`Astro-Nex.app/Contents/Frameworks` y reescribe la dependencia de `pyexpat`
para cargar esa copia interna. También valida el enlace antes de firmar. La
consola IPython y sus dependencias permanecen incluidas en el DMG, sin retirar
ninguna función existente.

### Verificación

- `codesign --verify --deep --strict` sobre `Astro-Nex.app`.
- `hdiutil verify` sobre el DMG generado.
- `otool -L` confirma que `pyexpat` usa
  `@loader_path/../../libexpat.1.dylib`.
- La Expat incluida exporta `_XML_SetAllocTrackerActivationThreshold`.

## 3 de agosto de 2026 - arranque macOS con base de ciudades

PyInstaller guarda los datos de `--add-data` de un bundle macOS en
`Astro-Nex.app/Contents/Resources`, pero `sys._MEIPASS` apunta a
`Contents/Frameworks`. El lanzador usaba esa segunda ruta directamente;
SQLite no encontraba `astronex/db/local.db`, creaba una base vacia y el inicio
fallaba con `sqlite3.OperationalError: no such table: SP`.

El lanzador ahora selecciona `Contents/Resources` cuando contiene la base de
ciudades empaquetada y mantiene `_MEIPASS` como alternativa. No modifica las
bases de cartas del usuario.

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

## 30 de julio de 2026 — calendario compacto y tono Beta más oscuro

### Incidencia observada

Tras la migración a GTK3, el calendario integrado seguía viéndose más grande
que en Astro-Nex 1.2 y el primer control inferior ya no conservaba el aspecto
de campo numérico con mini flechas verticales del original. Además, la
variante Beta del icono seguía demasiado cerca del tono de la edición 1.2 y
se distinguía poco en Finder, Dock, ventana, splash y accesos.

### Corrección

Se ajustó el panel compacto del calendario para acercarlo visualmente a la
referencia Python 2:

- el calendario reduce su anchura preferida y la fila inferior recupera
  proporciones más próximas al diseño histórico;
- el control numérico vuelve a presentarse como campo pequeño con flechas
  verticales apiladas, en lugar del `SpinButton` estándar de GTK3;
- el selector de unidad separa mejor su flecha interna del botón derecho.

En paralelo, se oscurecieron de forma uniforme los recursos gráficos de la
identidad Beta, sin añadir texto ni cambiar el dibujo:

- `astronex/resources/iconex-beta-22.png`
- `astronex/resources/iconex-beta-48.png`
- `astronex/resources/nex-beta.ico`
- `astronex/resources/splash.png`

### Verificación

Se validó con pruebas GTK3 centradas en la carta y sus overlays:

```bash
ASTRONEX_GUI_SMOKE=1 ./.venv-macos-build/bin/python -m unittest \
  tests.test_gui_smoke.GtkSmokeTest.test_chart_canvas_uses_scrolled_window_directly \
  tests.test_gui_smoke.GtkSmokeTest.test_extended_pair_chart_anchors_overlays_to_the_visible_area \
  tests.test_gui_smoke.GtkSmokeTest.test_toolbar_state_hides_stale_overlays
```

También se reconstruyó el instalador macOS listo para revisión visual:

- `Mac Instalador/Astro-Nex-2.0-beta-20260730-141028-macos-arm64.dmg`
