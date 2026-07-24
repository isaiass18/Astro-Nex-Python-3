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

## Pendiente de validación funcional detallada

Los siguientes puntos necesitan pasos reproducibles, resultado esperado y
resultado observado para terminar su revisión. No se han marcado como
corregidos sólo por abrir los diálogos.

| Área | Estado | Información necesaria |
|---|---|---|
| Clic izquierdo sobre la carta | Pendiente | Carta utilizada, punto pulsado y efecto esperado. |
| Icono de ojo | Corregido para la apertura del menú; selección de cada opción pendiente de validación. | Captura o pasos si alguna persona reciente no se carga. |
| F1 / ayuda | Pendiente de aclaración | Qué opción falta, es errónea o no está documentada. |
| Calendario, ventana auxiliar, aspectos, ciclos, diagramas y puente | Pendiente | Icono concreto, pasos, resultado esperado y resultado actual. |
| Planetograma | Menú contextual cubierto por esta corrección; apertura, dibujo e interacción pendientes de validar. | Carta y pasos que producen el fallo. |
| noVNC | Entorno de demostración | El 24 de julio la aplicación se cerró por un fallo de segmentación en GTK3 del host. No se atribuyó a una acción concreta sin una traza reproducible. |

## Cómo informar una incidencia

Para cada caso, anotar:

1. Plataforma y versión (Windows o Linux).
2. Carta o datos utilizados, sin incluir información privada si no es
   necesaria.
3. Pasos exactos.
4. Resultado esperado en Astro-Nex 1.2/Python 2.
5. Resultado observado en Python 3.
6. Captura de pantalla o vídeo corto, si es posible.

