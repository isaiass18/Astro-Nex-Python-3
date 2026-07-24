# Revisión y reparaciones posteriores a la migración

Este documento registra correcciones realizadas después de la revisión
funcional de la versión Python 3/GTK3. Su objetivo es dejar una relación
verificable entre una incidencia observada, la causa técnica, el cambio y la
prueba aplicada.

## 24 de julio de 2026 — menús contextuales de GTK3

### Incidencia observada

Durante la revisión de Joan Solé se indicó que diversas opciones al hacer
clic derecho sobre la carta y al usar el icono de ojo no funcionaban. La
sesión Linux de prueba registró el siguiente error reproducible:

```text
TypeError: Menu.popup() missing 1 required positional argument: 'activate_time'
```

La aplicación conservaba la firma de PyGTK/GTK2 de cinco argumentos para
`Menu.popup`. GTK3 añade un argumento `data` antes del botón y la hora de
activación.

### Corrección

Se añadió un adaptador central en `astronex/gtk_compat.py`. Conserva la firma
usada por el código histórico y llama a GTK3 insertando `None` como datos de
usuario del callback.

Esto cubre las llamadas existentes en:

- carta y áreas de dibujo;
- icono de ojo y casillas de entrada;
- listas del mezclador y explorador;
- parejas;
- ventanas auxiliares;
- planetograma.

### Verificación

Se añadió `test_legacy_context_menus_open_under_gtk3` a
`tests/test_gui_smoke.py`. Se ejecuta junto con las pruebas gráficas GTK3:

```bash
ASTRONEX_GUI_SMOKE=1 xvfb-run -a python -m unittest tests.test_gui_smoke
```

La prueba crea un menú y utiliza exactamente la llamada histórica de cinco
argumentos. El resultado esperado es que el menú se abra sin el `TypeError`.

## 24 de julio de 2026 — ayuda mediante F1

### Incidencia observada

Al pulsar F1 se abría una ventana vacía y la sesión gráfica terminaba cerrando
Astro-Nex. El registro mostró este error reproducible:

```text
AttributeError: 'cairo.Context' object has no attribute 'create_layout'
```

La ventana de ayuda debe mostrar una referencia visual de atajos de teclado y
acciones de ratón. El código conservaba los métodos que PyGTK añadía a Cairo,
pero PyGObject/GTK3 los expone a través de `PangoCairo`.

### Corrección

`astronex/gui/quickhelp.py` adapta el contexto de dibujo con
`pangocairo.CairoContext` antes de crear el diseño de texto. Así recupera las
operaciones `create_layout` y `show_layout` requeridas para pintar la ayuda.

Además, F1 se consume tras abrir la ayuda y los grupos de aceleradores se
mantienen como atributos de sus ventanas. El cierre observado ocurría dentro
de `gtk_accel_groups_activate` después de procesar F1; conservar esas
referencias evita que GTK3 despache aceleradores hacia callbacks liberados.

### Verificación

Se añadió `test_f1_help_window_renders_under_gtk3` a las pruebas gráficas. La
prueba crea la ventana de ayuda y ejecuta su dibujo sobre una superficie Cairo;
debe finalizar sin excepción y con la imagen de fondo disponible. También
fuerza un recorrido por `gtk_accel_groups_activate` después de una recolección
de memoria, que es el punto donde se produjo el cierre nativo de GTK3.

## Pendiente de validación funcional detallada

Los siguientes puntos necesitan pasos reproducibles, resultado esperado y
resultado observado para terminar su revisión. No se han marcado como
corregidos sólo por abrir los diálogos.

| Área | Estado | Información necesaria |
|---|---|---|
| Clic izquierdo sobre la carta | Pendiente | Carta utilizada, punto pulsado y efecto esperado. |
| Icono de ojo | Corregido para la apertura del menú; selección de cada opción pendiente de validación. | Captura o pasos si alguna persona reciente no se carga. |
| F1 / ayuda | Corregido el dibujo de la ventana. | Validar visualmente el contenido de los atajos en Windows y Linux. |
| Calendario / selector de casas | Corregido el acceso GTK2 a `parent.parent`. | Validar navegación completa por fechas y casas en Windows y Linux. |
| PE puente | Corregido el dibujo de sus etiquetas. | Validar su apertura, cambio de modo y cierre. |
| Dharma | Corregido el tamaño de la superficie de dibujo. | Validar el dibujo con cartas variadas. |
| Ventana auxiliar, aspectos, ciclos y diagramas | Pendiente | Icono concreto, pasos, resultado esperado y resultado actual. |
| Planetograma | Menú contextual cubierto por esta corrección; apertura, dibujo e interacción pendientes de validar. | Carta y pasos que producen el fallo. |
| noVNC | Entorno de demostración | Las correcciones de F1 y aceleradores se desplegaron en la instancia. Si Astro-Nex se cierra por otra operación, noVNC permanecerá disponible pero mostrará una pantalla vacía hasta relanzar la aplicación. |

## 24 de julio de 2026 — calendario, PE puente y Dharma

### Incidencias observadas

La sesión de prueba registró tres errores reproducibles al usar estas áreas:

- el calendario intentaba acceder a `HouseSelector.parent.parent`, una ruta
  de widgets propia de GTK2;
- PE puente trataba de crear texto Pango directamente sobre un contexto Cairo
  nativo;
- la operación Dharma pasaba tamaños decimales a `create_similar`, que
  pycairo sólo acepta como enteros.

### Corrección

- El selector de casas usa ahora el gestor ya disponible (`boss.da`) para
  actualizar la biografía y volver a la carta actual.
- PE puente adapta su contexto mediante `PangoCairo`, igual que las demás
  superficies de dibujo migradas.
- Dharma convierte las dimensiones de la superficie temporal a enteros antes
  de crearla.

### Verificación

Se añadieron pruebas gráficas para:

- ejecutar el selector de casas desde una fecha sin depender de la jerarquía
  de widgets de GTK2;
- dibujar las etiquetas de PE puente en una superficie Cairo mediante el
  adaptador PangoCairo.

La batería gráfica GTK3 se ejecutó en Ubuntu 24 bajo Xvfb con ocho pruebas
correctas. La misma revisión se desplegó en la instancia noVNC.

## Distribución de las reparaciones

Las correcciones se realizan primero en el código fuente común y se publican
en la rama principal de GitHub. La instalación Linux y la instancia noVNC usan
directamente ese código. La distribución Windows requiere reconstruir
`Astro-Nex-Setup.exe` y la carpeta portable desde el último commit para incluir
cualquier reparación posterior a la última compilación.

## 24 de julio de 2026 — auditoría preventiva GTK2/GTK3

Además de los casos descubiertos durante pruebas manuales, se realizó una
revisión estática de las APIs heredadas de PyGTK. Se corrigieron los siguientes
riesgos antes de que fueran reportados por un usuario:

- Tres manejadores de arrastre comparaban una constante de movimiento en vez
  de comparar `event.type`; afectaban a la carta principal, biografías y
  planetograma.
- La búsqueda rápida de listas (`Ctrl+F`) usaba `parent.parent`; ahora obtiene
  la ventana superior mediante la API GTK3.
- La activación de la opción Copiar/Cortar del explorador usa el padre GTK3
  del elemento de menú.
- El cuadro emergente de posiciones planetarias y la miniatura del explorador
  adaptan ahora su contexto de dibujo con PangoCairo.

La auditoría distingue estos errores verificables de APIs simplemente
obsoletas que siguen siendo compatibles en GTK3; estas últimas se conservan
hasta poder migrarlas sin alterar la funcionalidad.

## 24 de julio de 2026 — tránsitos y selector de fecha

### Corrección

- La capa temporal usada al dibujar tránsitos convierte sus dimensiones a
  enteros antes de llamar a Cairo, igual que las demás superficies auxiliares.
- El selector emergente de fecha reemplaza las comprobaciones GTK2 `flags()`
  por `get_realized`, `get_mapped` y `has_focus` de GTK3.
- El mismo recorrido de prueba detectó y sustituyó `Window.group` por
  `get_group()` y `hide_all()` por `hide()`, ambos eliminados en GTK3.
- El cálculo de posición del selector interpreta ahora el valor de éxito que
  GTK3 añade a `Gdk.Window.get_origin()`.
- El tamaño solicitado del calendario se obtiene mediante los campos del
  objeto `Requisition` que GTK3 devuelve.

### Verificación

Se añadió una prueba gráfica que realiza el ciclo de apertura y cierre del
selector de fecha sobre una ventana GTK3 realizada. Las capturas de
puntero/teclado heredadas siguen en observación: continúan siendo compatibles
en GTK3, pero requieren una revisión funcional específica antes de migrarlas
a la API moderna de asientos de entrada.
