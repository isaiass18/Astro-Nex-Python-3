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

## 25 de julio de 2026 — cabecera de fecha de la carta

### Incidencia observada

En NexP3, la fecha/hora de la carta actual se situaba centrada en algunas
presentaciones. En Astro-Nex 1.2/NexP2 la misma cabecera queda alineada al
borde derecho del área visible de la carta.

### Corrección

La fecha/hora y el símbolo planetario que la acompaña se anclan ahora al
ancho real de la ventana. Antes heredaban el ancho del lienzo de la carta;
en GTK3/Pango la cabecera se compone en coordenadas de ventana y quedaba
desplazada sobre el centro al existir el panel izquierdo.

La regla se aplica igualmente a las cabeceras de fecha de PE y del grado
regente, que comparten el mismo borde superior derecho.

### Verificación

Se añadió `test_chart_header_uses_the_visible_canvas_right_edge` a las
pruebas gráficas GTK3. Confirma que, aunque una vista calcule el dibujo con
un ancho reducido, la cabecera conserva como referencia el ancho visible de
la carta.

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
| Ventana auxiliar, aspectos, ciclos y diagramas | Corregido en los casos reportados. | Validar funcionalmente con cartas variadas. |
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

## 24 de julio de 2026 — carga de campos enmascarados y cierre de ventanas

### Corrección

- Las fechas y coordenadas cargadas desde datos guardados ya no se reinyectan
  como pulsaciones de teclado GTK3. El control enmascarado bloquea sólo su
  controlador interactivo durante una asignación programática completa, con
  lo que se eliminan las advertencias internas de conversión de texto.
- El explorador comprueba que el modelo y sus páginas siguen existiendo al
  recibir señales de selección o de pérdida de foco durante el cierre, y
  desconecta su controlador de selección antes de que GTK destruya el árbol.
- El cierre de la ventana principal sólo solicita salir de GTK si hay un bucle
  gráfico activo; esto permite cerrar ventanas durante las pruebas sin el
  aviso espurio de `gtk_main_quit`.
- El diálogo Acerca de cierra correctamente su archivo de licencia después de
  leerlo.

### Verificación

Se añadieron pruebas para cargar una fecha y una coordenada en campos
enmascarados. La batería gráfica se ejecutó en Ubuntu 24 bajo Xvfb y completó
correctamente sus pruebas. Las advertencias de conversión de texto de fecha y
coordenadas ya no aparecen.

## 24 de julio de 2026 — proporciones de las casillas de datos

La tarjeta de datos personales vuelve a usar el ancho de 320 píxeles y la
casilla de almacenamiento de 125 píxeles de la presentación histórica. GTK3
ampliaba la tarjeta para seguir el tamaño natural de la barra de herramientas,
alterando las proporciones de las dos filas de datos. Inicialmente se
conservaron los iconos de NexP3 alineados a la izquierda como diferenciador
visual. Tras establecer una portada y número de versión propios para
Astro-Nex 2.0 beta, la tarjeta vuelve a centrarse como en NexP2; las etiquetas
de sus datos permanecen alineadas a la izquierda.

La fila de carpeta, ojo, reloj y lápiz utiliza ahora dos anchos fijos que
suman la medida histórica de la tarjeta: 125 píxeles para la carpeta y 195
píxeles para el grupo de acciones. Esto conserva la separación de NexP2 sin
permitir que GTK3 expanda o desplace el panel completo.
Los bordes de GTK3 pueden hacer que el contenedor exterior mida 324 píxeles;
la fila útil conserva los 320 píxeles históricos.

## 24 de julio de 2026 — mnemónicos del mezclador

Los botones del mezclador conservaban los guiones bajos del código GTK2 como
texto visible (`_Crear tabla`, por ejemplo). En GTK3 se declara explícitamente
que el texto usa mnemónicos para que el guion bajo no se muestre y el atajo de
teclado continúe disponible.

## 25 de julio de 2026 — controles emergentes, rueda y selección por texto

### Incidencias revisadas

Las notas y capturas de la revisión funcional señalaron comportamientos
inconsistentes en el primer uso del calendario, la rueda del ratón sobre la
ventana auxiliar, Diagramas y PE puente, y la selección de una persona o
localidad al empezar a escribir su nombre.

### Correcciones

- Los botones con estado de la barra vertical (calendario, punto de edad,
  aspectos, ciclos, diagramas y PE puente) se sincronizan ahora con la señal
  GTK3 `toggled`. Así el estado visual y el panel asociado cambian juntos,
  incluso en la primera activación o cuando un diálogo se cierra por sí mismo.
- El puente PE limpia su referencia antes de desactivarse. Se evita de esta
  forma un segundo cierre de la misma ventana provocado por la señal de la
  barra.
- Los lienzos principal, auxiliar, diagramas, selector de casas,
  planetograma y PE puente solicitan explícitamente eventos de rueda. La capa
  de compatibilidad incluye tanto rueda convencional como desplazamiento
  suave de trackpad, que GTK3 separa en dos máscaras.
- La búsqueda por escritura de listas usa el carácter compuesto de GTK3 y no
  una conversión ASCII. Por tanto, vuelve a admitir nombres como `Élodie`,
  acentos y distribuciones de teclado no inglesas al seleccionar registros o
  localidades.

### Verificación en macOS

Se añadieron pruebas gráficas para la primera activación del calendario, la
recepción y el cambio de contenido por rueda en los lienzos emergentes y la
búsqueda con un carácter Unicode. La batería GTK3 local completó 15 pruebas
correctas y la batería general completó 28 pruebas correctas (15 de ellas se
omiten fuera de modo gráfico). Después se construyó un DMG temporal Apple
Silicon y se inició `Astro-Nex.app` desde el DMG; la aplicación permaneció en
ejecución correctamente antes de cerrarse de forma controlada.

El DMG de esta comprobación es local y temporal: estas correcciones todavía
no se han publicado en GitHub ni incorporado a los instaladores públicos.

## 25 de julio de 2026 — biografías y selección de registros

### Incidencias revisadas

En Punto Edad, el doble clic sobre una biografía seguía una ruta distinta pero
el clic simple no movía el regulador de fecha. Además, el cuadro que aparece
al escribir en una tabla podía mostrarse sin seleccionar el registro
coincidente.

### Correcciones

- El regulador de las biografías se conecta directamente a pulsación,
  liberación y movimiento del puntero. La antigua conexión genérica `event`
  era una ruta de GTK2 que GTK3 no despacha de forma fiable en una superficie
  con manejadores específicos.
- Al cambiar el texto de búsqueda se localiza, selecciona y desplaza al primer
  registro cuyo nombre comienza por el texto escrito. Esto se aplica a las
  tablas de cartas y a las listas de localidades.

### Verificación

La prueba gráfica de búsqueda ahora comprueba no sólo que el cuadro acepte
`É`, sino también que quede seleccionado el registro `Élodie`. La prueba
GTK3 local sigue finalizando correctamente con 15 pruebas correctas.

## 25 de julio de 2026 — cierre de ventanas flotantes en noVNC

### Incidencia observada

La revisión de la sesión Ubuntu/noVNC mostró una ventana flotante superpuesta
a la carta que parecía quedar bloqueada: Escape no siempre la cerraba y PE
puente se creaba sin borde ni botón de cierre visible.

### Corrección

- La ventana auxiliar queda declarada como transitoria de la ventana principal,
  con lo que recibe foco y conserva el control de cierre de la plataforma.
- El puente PE deja de ocultar la decoración de ventana. En noVNC el usuario
  puede cerrarlo también desde la `X`, sin depender de un acelerador de
  teclado.
- Los dos controladores de Escape destruyen la ventana y devuelven el evento
  como atendido. El cierre de una auxiliar comprueba además que siga en la
  lista antes de eliminarla, evitando un error durante cierres repetidos.

### Verificación

Se añadió una prueba GTK3 que abre ambas ventanas, verifica que la auxiliar es
transitoria, ejecuta Escape y comprueba que la auxiliar desaparece; también
verifica que el puente PE conserva decoración y se cierra mediante Escape.

## 25 de julio de 2026 — presentación de aspectos y acciones auxiliares

### Correcciones

- El selector de aspectos usa una distribución vertical explícita, espaciado
  regular y botones de 42×30 píxeles. Con ello su forma ya no depende de la
  política variable del tema GTK3.
- Las acciones `Congelar` y `Permutar` muestran una descripción al situar el
  puntero sobre ellas: la primera mantiene las cartas de la ventana auxiliar;
  la segunda intercambia allí la carta principal y la carta de clic.
- La presentación de `Momento actual` mantiene la fecha/hora a la derecha y
  reserva el margen final para el planeta anual. Las tarjetas de entrada
  continúan con la proporción fijada de 320 píxeles, 125 para carpeta y 195
  para ojo/reloj/lápiz.

### Verificación

La prueba gráfica comprueba que los once botones del selector conservan el
mismo tamaño y que su distribución no depende del tema. La batería GTK3 local
completa 17 pruebas correctas.

## 25 de julio de 2026 — fuente de símbolos en macOS

### Incidencia observada

El DMG de macOS incluía `Astro-Nex.ttf`, pero al abrir la aplicación Pango la
sustituía por Helvetica. Como consecuencia, los glifos astrológicos se
mostraban como letras (`d`, `f`, `g`, etc.).

### Corrección

El punto de entrada de macOS registra `Astro-Nex.ttf` con CoreText en el
ámbito exclusivo del proceso antes de cargar GTK/Pango. Así la fuente está
disponible para Astro-Nex desde el primer dibujo sin copiar archivos a
`~/Library/Fonts`, solicitar contraseña ni modificar la instalación de fuentes
del usuario.

### Verificación

Una prueba macOS inicia un proceso limpio, registra la fuente y solicita
`Astro-Nex 12` a Pango; verifica que la familia resultante es `Astro-Nex` y no
una fuente de sustitución.

## 25 de julio de 2026 — apertura y tamaño del calendario

### Incidencia observada

El primer icono de la barra vertical no siempre hacía visible el calendario
al primer clic. Cuando finalmente aparecía, el calendario nativo de GTK3
ocupaba un panel notablemente mayor que el de Astro-Nex 1.2/NexP2.

### Corrección

- El icono usa `GtkToggleToolButton` con su señal nativa GTK3 `toggled`.
  La conversión anterior conservaba la acción PyGTK `clicked`, que no se
  dispara al pulsar ese control en GTK3/macOS. F4/Ctrl+C cambian el mismo
  estado activo, por lo que siguen exactamente la ruta de un clic físico.
- Al activar el botón de calendario, el panel se muestra explícitamente y se
  oculta al desactivarlo, dentro de la misma ventana principal.
- El calendario se aloja en `Gtk.Overlay`, encima del área de carta. Es el
  reemplazo GTK3 de la superposición que NexP2 hacía con `Gtk.Layout`: no abre
  una ventana independiente y conserva la apariencia integrada del programa.
  Se elimina así el fallo de macOS donde el `Gtk.Layout` mantenía el panel
  activo pero no lo componía en pantalla.
- Se fijó la huella visual histórica del panel a **230 × 150 píxeles**. El
  calendario interno ocupa 228 × 107 y la fila de controles 230 × 32, evitando
  que el tamaño natural mayor de GTK3 cambie el formato de NexP2.
- El `SpinButton` del tema GTK3 de macOS imponía por sí solo 118 píxeles de
  ancho. Se sustituyó en esta fila por un campo compacto de 1–10 que conserva
  el valor que utilizan las flechas de avance/retroceso de fecha.

### Verificación

`test_calendar_toolbar_toggle_opens_on_first_use` comprueba la activación
nativa `toggled`, la primera apertura, la visibilidad real del panel, su posición
`(0, 0)`, el tamaño compacto y el cierre posterior. La batería local completó
32 pruebas
correctamente. Se reconstruyó y arrancó el único DMG de prueba desde
`Mac Instalador/Astro-Nex-2.0-beta-macos-arm64.dmg`; no se hizo publicación
en GitHub.

## 25 de julio de 2026 — estabilidad de atajos y reloj en macOS

### Incidencia observada

Al hacer doble clic sobre el reloj de la carta del momento, macOS mostró el
aviso de cierre inesperado. El informe del sistema identificó un `SIGSEGV` en
`gtk_accel_groups_activate`, es decir, en el despacho de atajos de GTK3 y no
en el cálculo ni en el dibujo de la carta.

### Corrección

La capa de compatibilidad conserva ahora explícitamente cada callback y su
conexión mientras exista su `Gtk.AccelGroup`. Es el ciclo de vida que PyGTK
aportaba implícitamente y que PyGObject no garantiza para métodos enlazados.
Las ventanas que crean sus propios atajos también conservan el grupo completo.
Con ello GTK3 no puede intentar llamar una referencia Python liberada al
recibir un atajo después de una interacción con el reloj, calendario o ayuda.

### Verificación

Se añadieron pruebas para dos clics consecutivos sobre el reloj y para la
retención de todos los callbacks globales. La comprobación del calendario
sigue verificando que el botón físico lo abre en el primer clic y lo cierra en
el segundo.

## 26 de julio de 2026 — visibilidad del calendario, alineación de slots y cierre de ventanas

### Incidencias observadas

- En el modo Radix, el panel del calendario (`ChangeDatePanel`) quedaba oculto o desplazado fuera del área visible, aunque GTK lo instanciaba correctamente. Esto no ocurría en "Análisis de polaridades".
- Los botones de acciones en las tarjetas de datos (carpeta, ojo, reloj, lápiz) no mantenían una alineación uniforme cuando el icono del ojo (para ver personas recientes) se ocultaba o mostraba.
- En entornos sin decorador de ventanas (como instancias noVNC), los diálogos y ventanas auxiliares no ofrecían un mecanismo rápido para cerrarse mediante teclado, lo que causaba bloqueos de flujo.

### Corrección

- **Visibilidad del Calendario**: El renderizado en modo Radix modificaba la matriz de transformación del lienzo (Cairo) para centrar la carta (`cr.translate`), pero luego llamaba a `cr.identity_matrix()` destruyendo la traslación inicial proporcionada por GTK3. Se envolvió el dibujo con `cr.save()` y `cr.restore()` en `dispatch()` de `layoutsurface.py` para aislar el dibujo de la carta y garantizar que GTK3 retenga su sistema de coordenadas local para componer los widgets hijos superpuestos (como el calendario). También se agregaron las llamadas explícitas a `self.panel.show()` y `hide()` para interoperabilidad con los parches previos de macOS.
- **Alineación de slots**: Se introdujeron espaciadores elásticos (`gtk.Label` con propiedad de expansión) a los lados del icono del ojo en `astronex/gui/mainnb.py`. Esto fuerza al icono de la carpeta a permanecer anclado a la izquierda, al ojo a centrarse en el espacio libre, y asegura que el reloj y el lápiz estén siempre alineados a la derecha, independientemente de los estados de visibilidad.
- **Cierre con Escape**: Inicialmente se intentó inyectar globalmente el evento `key-press-event` en todas las clases base, pero esto provocó bloqueos (pantalla negra en VNC) debido a que se ejecutaba antes de que GTK terminara de construir las ventanas. Se revirtió ese cambio y se agregó el controlador manualmente y de forma segura al final de la inicialización (después de `gtk.Dialog.__init__`) en las cinco ventanas de diálogo más utilizadas: Entradas (`EntryDlg`), Configuración (`ConfigDlg`), Selector de aspectos (`PlanSelector`), Localidades (`LocSelector`, `CustomLocDlg`) y Ciclos (`CycleSelector`).

### Verificación

- La aparición del panel de calendario fue verificada gráficamente en servidor X/VNC al pulsar F5/Ctrl+C en la vista principal Radix, confirmando su superposición correcta en la esquina superior izquierda.
- La alineación de la barra de botones en los slots fue validada visualmente mediante captura de pantalla, mostrando el espaciado correcto incluso en los slots (inferiores) donde el icono de ojo está desactivado.
- Se deshizo el parche global que colgaba la aplicación y el cierre con teclado (Escape) fue probado con éxito en los diálogos principales sin interrumpir el arranque del programa.

## 26 de julio de 2026 (Fase 2) — comportamiento del Punto de la Edad y sincronización de versión en VNC

### Incidencias observadas

- **Punto de la Edad (Ctrl+A)**: El usuario reportó que el botón y el atajo funcionaban de forma intermitente (a veces sí, a veces no).
- **Versión e Imagen Desactualizadas en el Servidor**: La ventana "Acerca de" mostraba la versión "1.2" y el antiguo splash en la instancia VNC, a pesar de que el código fuente ya había sido actualizado a "2.0-beta" en un commit previo.

### Corrección / Explicación

- **Punto de la Edad (Ctrl+A)**: Se investigó el código fuente en `layoutsurface.py` y se descubrió que no se trata de un error. El software desactiva intencionalmente el botón si la carta activa es "Momento actual" (`curr.curr_chart == curr.now`), dado que para el momento actual la edad es cero y no se puede calcular un Punto de la Edad histórico. El botón funciona perfectamente tan pronto como se carga una carta natal con fecha de nacimiento al panel activo (por ejemplo, al cambiar al modo Parejas o cargar una persona guardada). Se le explicó este comportamiento diseñado por el creador original al usuario.
- **Sincronización VNC (Astro-Nex 2.0-beta)**: El código en el repositorio local ya contaba con la marca "2.0-beta" en `nex.py` y la nueva imagen `splash.png`. La incidencia se debía a que los despliegues recientes mediante `rsync` al servidor VNC solo incluían los archivos modificados en la carpeta `astronex/gui/`. Se solucionó desplegando los archivos estáticos faltantes (`nex.py` y `astronex/resources/splash.png`) a la instancia VNC y reiniciando el proceso.

### Verificación

- Se verificó en el código de GTK3 que el estado del botón (`toggled`) se reseteaba correctamente por la regla matemática impuesta en `layoutsurface.show_pe`.
- Se lanzó un comando `rsync` directo contra el servidor remoto y se validó en los logs que la transferencia concluyó correctamente, restaurando la marca visual de la beta 2.0 en VNC.

## 26 de julio de 2026 (Fase 3) — Interacción de la ventana auxiliar (Ventana flotante)

### Incidencias observadas

- **Fallo al interactuar con Ventanas Flotantes Auxiliares**: El usuario indicó que al hacer clic derecho sobre la ventana emergente general, el menú aparecía pero no realizaba ninguna acción, y la rueda del ratón no lograba cambiar la carta. Además, este mismo fallo de interacción de la rueda del ratón ocurría en la ventana flotante "PE puente" (la cual tiene un carrusel de dos imágenes).
- **Pantalla Negra al Arrancar (VNC)**: Tras un despliegue parcial, la aplicación dejó de arrancar en el servidor VNC (quedó en pantalla negra), lanzando un error crítico en el inicio.

### Corrección

- **Fallo en Ventanas Flotantes (Scroll y Menú)**: Se determinó que la selección de opciones del menú y el scroll de la rueda del ratón en las ventanas auxiliares (incluida la ventana de *PE puente*) capturaban los eventos correctamente, pero fallaban en silencio al intentar actualizar el gráfico. Esto se debía al uso del método de repintado antiguo `self.window.invalidate_rect` (removido en GTK3). Se reemplazaron todas las rutinas de `redraw` en `sdasurface.py` y `bridgewin.py` por la API moderna `self.queue_draw()`. Además, se agregó el permiso explícito `SCROLL_MASK` a la inicialización de *PE puente* para permitir que GTK3 detecte la rueda del ratón en ese panel.
- **Cuelgue de Inicio (VNC)**: El error de arranque en VNC ocurrió porque `sdasurface.py` fue actualizado para pedir acceso explícito a la rueda del ratón (`SCROLL_MASK`), pero ese parche de compatibilidad solo existía en el archivo `gtk_compat.py` local, el cual no había sido subido. Se solucionó sincronizando el árbol completo de la carpeta de código fuente `astronex/` al servidor, garantizando paridad total con la versión reparada local.

### Verificación

- Se constató en los procesos del servidor que la aplicación vuelve a iniciar correctamente sin errores en la importación de constantes.
- Las funciones de redibujado de las ventanas auxiliares y del *PE puente* ya no invocan métodos obsoletos, permitiendo que el visor responda fluidamente a los cambios de opción desde el menú contextual o al girar la rueda del ratón para navegar los carruseles.

## 26 de julio de 2026 (Fase 4) — Corrección de Búsqueda Interactiva y Clic en Biografías

### Incidencias observadas

- **Caja de búsqueda de personas reescribía las letras**: El usuario reportó que al escribir en el panel de personas (ej: "isaias"), la caja de búsqueda se reiniciaba. Si escribía una segunda letra, se borraba la primera (ej. la "i" se borraba al escribir la "s"), o en ocasiones ignoraba los teclazos por completo (quedándose seleccionada solo la primera letra).
- **Clic simple no funcionaba en la línea de tiempo biográfica**: El usuario observó en un manual que "el clic en la biografía no funciona", pero argumentó que debería funcionar para explorar los tránsitos de años venideros partiendo de "Momento actual".

### Corrección / Explicación

- **Búsqueda Interactiva de la lista (SearchView)**: La lista de la interfaz cuenta con un componente `SearchView` completamente personalizado que dibuja una caja de texto flotante abajo a la derecha. Al migrar a GTK3, esa ventana flotante sin decoración muchas veces no obtenía el foco automático del gestor de ventanas (Wayland/X11), o, si lo obtenía, GTK seleccionaba de forma predeterminada el texto inicial, causando que la siguiente tecla lo sobrescribiera.
  - *Solución*: En `searchview.py`, se utilizó `idle_add` para obligar a la ventana a presentarse (`present()`), capturar el foco incondicionalmente (`grab_focus()`), deseleccionar el texto y mover el cursor al final de la palabra ingresada (`select_region(-1,-1)` y `set_position(-1)`). Adicionalmente, se implementó un mecanismo robusto de propagación de eventos (`on_keypress`) para que, en caso de que el sistema operativo niegue el foco de todas formas, el componente reciba manualmente y encole las letras escritas por el usuario.
- **Limitación intencional en Biografías (Momento Actual)**: Investigando el código fuente original (`biograph.py`), se descubrió que el autor bloqueó *a propósito* el clic izquierdo si la carta base era `curr.now` ("Momento actual"), seguramente derivado de una regla reutilizada del "Punto de Edad" (donde la edad para el momento actual es nula).
  - *Solución*: Se le explicó al usuario que esta limitación era intencional en la versión antigua, pero se le dio la razón técnica. Se retiró la comprobación `curr.curr_chart == curr.now` de `pe_rulercb`, logrando que al hacer clic simple en la biografía se interpole el cursor del píxel sobre el eje X y se ajuste dinámicamente el panel del tiempo a la fecha del tránsito. Esto mejora la funcionalidad original del software.

### Verificación

- Se validó que al escribir de forma seguida en la lista, la caja de texto recibe todos los caracteres preservando las letras anteriores.
- Al cargar el "Momento actual" y abrir un panel de biografía de tránsitos, ahora el clic simple es reconocido, actualizando la fecha y repintando la regla (`ruler`) adecuadamente.

## 26 de julio de 2026 (Fase 5) — Errores Visuales por División en Python 3

### Incidencias observadas

- **Descuadre en Configuración de Colores**: Los botones para personalizar los colores de elementos (Fuego, Tierra, Primera Persona, etc.) estaban desfasados hacia la derecha y no respetaban la cuadrícula en GTK3. Además, todo el panel quedaba arrinconado a la izquierda dejando mucho espacio vacío a la derecha.
- **Inclinación en Listas (PE radix)**: En las vistas de listas de progresión del Punto de Edad, las columnas de texto comenzaban rectas pero iban desviándose ("cayéndose") gradualmente hacia la derecha línea tras línea.

### Corrección / Explicación

- **Incompatibilidad de División (Python 2 vs 3)**: Ambos errores gráficos compartían la misma causa de fondo: la transición de Python 2 a Python 3. En Python 2, el operador `/` entre dos enteros realizaba una **división entera** estricta (ej. `3 / 2 = 1`). En Python 3, la división simple arroja un **número flotante decimal** (ej. `3 / 2 = 1.5`).
- **Reparación en `config_dlg.py`**: El algoritmo que acomodaba los botones en la tabla calculaba la columna usando la fórmula `(i / ix) * 2`. En Python 3, esto introducía un componente decimal que GTK3 interpretaba redondeando hacia posiciones cada vez más lejanas. Se corrigió cambiando la fórmula para forzar la división entera (`//`). Adicionalmente, se forzó el centrado manual de las tablas (`table.set_halign(3)`), dado que el contenedor `VBox` de GTK3 ya no estira nativamente las tablas a lo ancho como lo hacía GTK2.
- **Reparación en `progsheet.py`**: El cálculo del eje X donde el texto se escribía en la pantalla del visor utilizaba una fórmula análoga: `x = hm + int(ho*(i / 48))`. Al arrojar decimales, el factor `int()` lo iba convirtiendo progresivamente en 1 o 2 píxeles adicionales a la derecha por renglón, causando la inclinación. Se corrigió reemplazando el operador por una división entera (`i // 48`).

### Verificación

- Las tablas de configuración de colores ahora muestran una cuadrícula intacta y se hallan centradas estéticamente en la pantalla.
- Las tablas textuales generadas por `progsheet.py` (ej. PE radix) ahora presentan columnas rectas y perfectamente alineadas de forma vertical.

## 26 de julio de 2026 (Fase 6) — Problema de Reaparición del Cuadro de Entradas

### Incidencias observadas

- **Ventana de Entradas (Ctrl+E) dejaba de funcionar tras cerrarse**: El usuario reportó que el botón superior y el atajo `Ctrl+E` para abrir el formulario de introducción de datos operaba correctamente la primera vez. Sin embargo, tras cerrar dicha ventana, volvía a oprimir el botón y ya no sucedía nada, quedando inutilizado de forma permanente durante la sesión.

### Corrección / Explicación

- **Pérdida de Referencias al Destruir**: Al cerrar la ventana (a través de la tecla Escape, la 'X' de la barra de título o los botones Aceptar/Cancelar), la rutina llamaba a `dialog.destroy()`, aniquilando el widget de la memoria de GTK3. Sin embargo, en varios casos (como al usar la tecla Escape), no se borraba la referencia de la variable `self.entry` del módulo principal. Al presionar el botón de nuevo, el sistema verificaba si `self.entry` existía; como no era `None` (aún apuntaba al objeto destruido), creía que la ventana seguía viva e ignoraba la orden de instanciar una nueva.
- **Implementación de Ocultación (`hide`)**: En lugar de destruir la ventana y lidiar con la complejidad de limpiar las variables en todos los flujos de cierre, se reescribió `entry_dlg.py` para utilizar `dialog.hide()`. Para el botón de la 'X', se vinculó el evento GTK `delete-event` a `hide_on_delete`.
- **Reutilización del Widget**: En `winnex.py`, se actualizó el disparador del botón para que, además de crear el cuadro si no existe, ejecute incondicionalmente `self.entry.present()`.

### Verificación

- La ventana se puede abrir y cerrar infinitas veces sin perderse en el vacío de GTK.
- Como efecto secundario altamente positivo, el estado previo queda en memoria. Si el usuario ingresa parcialmente el nombre de un sujeto y cierra la ventana por accidente, sus datos se preservan intactos para cuando vuelva a pulsar `Ctrl+E`.

## 26 de julio de 2026 (Fase 7) — Gráficas Faltantes en el Planetograma

### Incidencias observadas

- **Lado derecho del Planetograma en blanco**: El botón del planetograma (toolbar) dibujaba correctamente el gráfico principal a la izquierda, pero las gráficas suplementarias de la derecha (Carta del Alma, de las Casas, reglas lineales) no aparecían en pantalla.

### Corrección / Explicación

- **Error silencioso de PangoCairo**: Al inspeccionar los registros (`/tmp/astronex.log`) se detectó una falla al tratar de renderizar las gráficas secundarias: `AttributeError: 'cairo.Context' object has no attribute 'create_layout'`. En PyGObject (GTK3), el contexto crudo de cairo no posee el método `create_layout` (usado para dibujar textos con pango); necesita envolverse mediante una capa de compatibilidad. Aunque los desarrolladores del proyecto crearon un wrapper custom (`pangocairo_compat.CairoContext`), olvidaron aplicarlo en el manejador del evento `"draw"` de esta ventana (`DrawPlagram.dispatch`).
- **Aplicación del Wrapper**: Se inyectó la línea `cr = pangocairo.CairoContext(cr)` al inicio de `dispatch` en `astronex/gui/plagram_dlg.py`, dotando al lienzo de la habilidad para dibujar los textos requeridos sin colapsar y permitiendo que la ejecución del renderizado prosiguiese hasta el final.
- **Fallo en Opciones de Repintado (Menú Contextual)**: Las opciones del menú contextual como "Ver puntos de sombra" o "Ver lineas personales" parecían no hacer nada al desmarcarse. Se identificaron dos factores:
  1. **Redraw inoperante**: Se utilizaba `self.window.invalidate_rect`, método obsoleto que lanzaba `AttributeError` en GTK3. Al estar bajo un bloque `try/except pass`, fallaba silenciosamente y nunca ordenaba a GTK repintar. Se reemplazó por el estándar de GTK3: `self.queue_draw()`.
  2. **Lectura de Etiquetas del Menú**: En PyGTK se obtenía el texto con `menuitem.child.get_text()`, pero en GTK3 la propiedad `child` no es legible. Se reemplazó por la forma moderna y segura de extraer la etiqueta de un widget hijo en un MenuItem: `menuitem.get_child().get_text()`.

### Verificación

- Al abrir la ventana del Planetograma, ahora se observa la composición completa de gráficas (Soul, House y reglas) distribuidas por el lienzo como originalmente se ideó.
- Las opciones del clic derecho (activar/desactivar gráficas superpuestas) redibujan y conmutan sus respectivas capas de manera instantánea.

## 26 de julio de 2026 (Fase 8) — Botones de Lápiz (Editar) Inoperantes

### Incidencias observadas

- **Botones de edición sin respuesta**: Los botones de lápiz (Editar) en las listas de cartas (ej. "Joan Solé" o "Momento actual") dejaron de invocar la ventana `EntryDlg` ("Entradas") si esta había sido previamente cerrada.

### Corrección / Explicación

- **Efecto secundario de la ocultación (Fase 6)**: Anteriormente, al cerrar la ventana `EntryDlg` esta era destruida. Los botones de lápiz (`on_entry_clicked` en `mainnb.py`) validaban `if not mainwin.entry` para crearla y mostrarla. Al cambiar la lógica a "ocultar" (`hide`), la ventana permanece en memoria, haciendo que el bloque condicional saltase el intento de invocar la rutina de repintado.
- Para remediar esto, se forzó el comando `mainwin.entry.present()` en `mainnb.py` tras inyectar los datos de la carta (`modify_entries`). De esta forma, si la ventana existe pero está oculta/minimizada, el sistema la trae automáticamente al frente del usuario.

## 26 de julio de 2026 (Fase 9) — Ajustes Específicos para Entorno VNC

### Incidencias observadas

- **Resolución y Botón de Reinicio**: El entorno VNC se renderizaba a una resolución cuadrada (`1440x1000`) provocando bordes grises (letterboxing) en pantallas anchas. Además, se solicitó una forma de reiniciar el aplicativo directamente desde el visor VNC en caso de bloqueos, pero el servidor VNC (Xvfb) carece de entorno de escritorio o gestor de ventanas real (Window Manager).

### Corrección / Explicación

- **Ajuste de Resolución Xvfb**: Se modificó el comando de arranque del servidor Xvfb a la resolución estándar 16:9 de `1920x1080` (Full HD), aprovechando al máximo el ancho de los navegadores web que consumen noVNC.
- **Botón de Reinicio (Exclusivo VNC)**: Se creó un script secundario (`restarter.py`) que genera una pequeña ventana GTK3 sin bordes anclada permanentemente en la esquina inferior derecha. Al hacer clic, este botón fuerza la muerte del proceso `nex.py` (`pkill`) y lo relanza automáticamente.
- **Auto-Superposición Activa**: Puesto que Xvfb no cuenta con un Window Manager para hacer respetar reglas de apilado como "Mantener Siempre Arriba" (`set_keep_above`), la ventana de la aplicación `nex.py` solía aplastar al botón. Esto se solucionó introduciendo un temporizador (`GLib.timeout_add(500, self.present)`) que obliga al botón a saltar al frente del "Z-index" cada medio segundo de forma perpetua.
- **Gestión de Foco de Teclado (Openbox)**: Al abrir diálogos flotantes (como el Planetograma) en un entorno VNC sin gestor de ventanas, el sistema no reasignaba el foco del teclado al nuevo widget. Esto causaba que atajos como *Escape* fueran ignorados por completo en todas las ventanas. Se solucionó instalando e inyectando un gestor de ventanas ligero (`openbox-session`) en el servidor Xvfb, permitiendo que las ventanas hereden decoraciones básicas y capturen el foco de entrada automáticamente al abrirse, restaurando así el funcionamiento universal del cierre mediante *Escape*.

> [!NOTE]
> Estos ajustes (botón flotante, resolución forzada y Openbox) son aditamentos *exclusivos* para el entorno de pruebas virtual en AWS (VNC). No afectan ni son parte del código fuente nativo de AstroNex descargado por los usuarios.

## 26 de julio de 2026 (Fase 10) — Rueda del Ratón (Eventos Scroll en GTK3)

### Incidencias observadas

- **Planetograma sin zoom:** Al abrir la ventana emergente del Planetograma, girar la rueda del ratón no producía ningún aumento o disminución de la imagen.
- **Casillas de trabajo estáticas:** En los slots principales (casilla 1 y 2), la rueda del ratón debía hacer un carrusel cambiando entre las últimas personas cargadas, pero el evento era ignorado por completo.

### Corrección / Explicación

La migración a GTK3 endureció las reglas sobre qué contenedores pueden recibir eventos de hardware.
- **En el Planetograma (`plagram_dlg.py`):** El lienzo `DrawPlagram` conectaba el evento `scroll-event`, pero carecía de la máscara de hardware necesaria. Se añadió explícitamente la bandera `gtk.gdk.SCROLL_MASK` en la inicialización de eventos para autorizar la lectura de la rueda.
- **En las Casillas de Trabajo (`mainnb.py`):** La clase `Slot` heredaba de `GtkVBox`, la cual es un contenedor sin ventana propia (`no-window widget`) en GTK3. Se corrigió delegando la conexión del evento `scroll-event` directamente al contenedor interno `EventBox` (`self.eb`) que sí posee superficie interactiva, además de añadirle explícitamente la máscara de desplazamiento. Ambos componentes volvieron a ser interactivos de inmediato.

## 26 de julio de 2026 (Fase 11) — Correcciones de Renderizado y Arranque

### Incidencias observadas

- **Rueda selectora de casas invisible:** Al entrar a la sección de Biografías, el selector inferior izquierdo (una rueda de colores dividida en 12 segmentos) no se dibujaba. En su lugar, solo aparecía un recuadro beige con un punto azul.
- **Icono del ojo duplicado:** Al iniciar la aplicación, sorpresivamente ambas casillas de trabajo mostraban el icono del ojo (visibilidad de cartas secundarias), cuando por diseño la casilla principal debía ocultarlo.

### Corrección / Explicación

- **División Flotante de Python 3 (`sdasurface.py`):** En el método que dibuja la rueda de 12 segmentos de la clase `HouseSelector`, se dividía el grado actual entre 30 (`ang / 30`) para escoger un color de la lista de paletas. En Python 2 esto generaba un número entero, pero en Python 3 genera un flotante (ej. `1.0`), provocando una falla interna invisible por intentar indexar una lista con decimales (`TypeError`). Se reemplazó por la división entera estricta (`ang // 30`), restaurando el dibujo de la rueda.
- **Ruta de Inicialización Rota (`mainnb.py`):** Al mover el control de los clics en la Fase 10 (del contenedor invisible `Slot` al visible `EventBox`), la rutina de inicialización automática `slot_activate(slot)` que simulaba un clic maestro al arrancar se quedó huérfana. Como nunca se disparaba ese clic falso en el arranque, la aplicación nunca ocultaba el ojo de la casilla principal. Se corrigió redireccionando la llamada de inicialización hacia el nuevo escuchador (`slot.eb.emit("button_press_event", event)`), regresando el estado visual a la normalidad.

## 26 de julio de 2026 (Fase 12) — Foco de Teclado Robado por el Botón de Reinicio en VNC

### Incidencias observadas

- **Flechas ↑↓ no navegaban las listas:** En la instancia VNC, al hacer clic en un elemento de la lista de personas o de cartas, las teclas de flecha arriba/abajo no desplazaban la selección.
- **Búsqueda por escritura inoperativa en VNC:** Al pulsar una letra en las listas (personas, cartas, ciudades), la caja de búsqueda flotante aparecía pero no aceptaba ningún carácter. El texto nunca se actualizaba. En macOS local la misma función funcionaba perfectamente, descartando un error de código puro.

### Causa Raíz

El responsable fue el script `restarter.py` que se ejecuta permanentemente en la instancia VNC como botón flotante de reinicio. Este script contenía el siguiente timer:

```python
GLib.timeout_add(500, self.keep_on_top)

def keep_on_top(self):
    self.present()  # ← ejecutado cada 500 ms
    return True
```

En X11 (el protocolo de pantalla que utiliza Xvfb/VNC), la llamada `present()` no solo eleva la ventana al frente — también **transfiere el foco del teclado** a esa ventana. Al dispararse cada 500 milisegundos, el botón de reinicio robaba el foco antes de que el usuario pudiera escribir o navegar con las flechas, lo que hacía que todos los pulsaciones de tecla se perdieran.

### Corrección

**`restarter.py` (en el servidor VNC):** Se eliminó por completo el timer `keep_on_top` con `present()`. Para mantener la ventana visible por encima de las demás sin robar el foco se utilizan dos banderas GTK que actúan puramente a nivel visual:

```python
self.set_keep_above(True)    # mantiene la ventana siempre encima
self.set_focus_on_map(False) # impide que el WM le dé foco al mostrarse
```

**`searchview.py` (mejora complementaria para X11):** Aunque el problema principal era el `restarter.py`, se añadió también `gtk.gdk.keyboard_grab()` al abrir la caja de búsqueda flotante (y `keyboard_ungrab()` al cerrarla). Esto garantiza que, en entornos X11 donde el gestor de ventanas no transfiere el foco automáticamente a ventanas sin decoración, la caja de búsqueda siempre reciba las pulsaciones del teclado.

**`searchview.py` (foco al hacer clic):** Se añadió `self.grab_focus()` al inicio del manejador `on_buttonpress` para que cada clic en un elemento de la lista asegure el foco de teclado en el `TreeView`, permitiendo la navegación inmediata con flechas.

**`entry_dlg.py`:** Se corrigió la conexión `delete-event` que usaba `self.hide_on_delete` (firma de GTK2 de 1 argumento) por una lambda compatible con GTK3 de 2 argumentos.

### Verificación

- Se confirmó en macOS local que la búsqueda y las flechas funcionaban correctamente antes de aplicar el fix de VNC, descartando error en el código de la aplicación.
- Se desplegó el `restarter.py` corregido en la instancia VNC y se verificó que el proceso antiguo con el timer quedó eliminado.
- La instancia VNC reinició limpiamente y las listas de personas, cartas y ciudades volvieron a responder a teclas y flechas normalmente.

## 27 de julio de 2026 — trackpad de macOS en controles personalizados

### Incidencia observada

Las correcciones de rueda funcionaban en noVNC y con ratones convencionales,
pero algunas superficies propias no respondían al trackpad de macOS. GTK3
emite `SMOOTH` con deltas fraccionarios para el trackpad, mientras que el
código heredado sólo trataba las direcciones discretas `SCROLL_UP` y
`SCROLL_DOWN`.

### Corrección

La capa GTK3 normaliza ambos formatos en `gtk.gdk.scroll_delta`. Los
controladores del planetograma, casillas de recientes, carta principal,
auxiliares, diagramas, selector de casas, PE puente y selectores de fecha
usan ahora ese valor. Las casillas acumulan los deltas suaves hasta completar
un cambio de carta; el zoom del planetograma conserva la intensidad gradual
del gesto.

### Verificación

Se añadió una prueba que compara un evento de rueda y un evento suave de
trackpad. Ambas rutas se convierten a la misma dirección de desplazamiento.

## 27 de julio de 2026 — sensibilidad y límite de zoom del trackpad

### Incidencia observada

En macOS, un desplazamiento corto en el trackpad podía ampliar el
planetograma de forma extrema. Quartz entrega distancias de desplazamiento de
alta resolución, no los pasos discretos de una rueda. Al tratarlas como pasos
completos, el zoom se multiplicaba demasiado rápido y Cairo quedaba ocupado
redibujando una carta gigantesca; macOS podía marcar la aplicación como no
respondiente.

### Corrección

Los deltas suaves se escalan y se limitan antes de llegar a los controles
históricos. El planetograma aplica un factor mucho menor para trackpad que
para una rueda convencional y su zoom queda acotado entre el tamaño normal y
4×. Un gesto breve cambia el tamaño gradualmente y no puede sacar el dibujo a
una escala que bloquee la interfaz.

### Verificación

La prueba gráfica simula un delta suave muy grande: se limita a un cambio
pequeño, diez eventos conservan un zoom inferior a 1.2× y una secuencia larga
nunca supera el límite de 4×.

## 27 de julio de 2026 — alineación uniforme de tarjetas de datos

### Incidencia observada

Las dos tarjetas de datos podían quedar centradas en posiciones diferentes.
GTK3 calculaba el ancho natural de cada tarjeta a partir de sus propios textos;
una fecha o localidad más larga ensanchaba una fila y desplazaba la otra.

### Corrección

Se descartó igualar artificialmente el ancho natural de las tarjetas: en
GTK3/macOS esa restricción encogía el panel completo y lo centraba dentro de
la ventana. El panel conserva su distribución histórica; la alineación de los
controles de acción se resuelve dentro de cada tabla, sin cambiar el tamaño
global de la interfaz.

### Verificación

La prueba gráfica verifica directamente el borde derecho del grupo de
acciones en cada tarjeta.

## 27 de julio de 2026 — botones de acción alineados en ambas tarjetas

### Incidencia observada

Aunque las tarjetas ya tenían la misma anchura, los botones de reloj y edición
de la segunda fila quedaban desplazados a la izquierda cuando su localidad era
más corta. GTK3 repartía el ancho de sus columnas de forma independiente en
cada tabla y el grupo de acciones no ocupaba el espacio sobrante.

### Corrección

El grupo que contiene el ojo, reloj y lápiz se expande hasta el borde derecho
de la tabla. Sus dos espaciadores internos conservan el ojo centrado y anclan
reloj y lápiz al mismo borde derecho en las dos filas, sin depender del texto
de localidad.

### Verificación

La prueba gráfica comprueba que el borde final del grupo de acciones coincide
con el borde derecho de la tabla principal y secundaria.

## 27 de julio de 2026 — icono de Astro-Nex en el instalador macOS

### Corrección

El compilador macOS convierte `astronex/resources/nex.ico`, el logo del
instalador de Windows, en un archivo `.icns` Retina y lo entrega a PyInstaller.
La aplicación dentro del DMG muestra así el icono de Astro-Nex en Finder,
Aplicaciones y el Dock.

### Verificación

Se generó el `.icns` con `iconutil` y macOS lo reconoce como un icono válido.

## 27 de julio de 2026 — posición estable del panel principal en macOS

### Incidencia observada

En una ventana amplia de macOS, el contenedor horizontal heredado podía
centrar el bloque completo de controles y carta. El panel aparecía separado
del borde izquierdo y el `ScrolledWindow` centraba también la carta, dejando
un gran vacío entre ambas zonas.

### Corrección

Se contrastó el comportamiento con la instancia VNC funcional y se restauró
su distribución original basada en `HBox`, sin una cuadrícula adicional ni
forzar la expansión de la fila de acciones. Así se conservan las proporciones
históricas de la interfaz.

### Verificación

La prueba gráfica de tarjetas sigue pasando y el código de distribución local
coincide con el de la instancia VNC funcional.

## 27 de julio de 2026 — cambio prematuro del ciclo del Punto de Edad

### Incidencia observada

Al llegar al 1 de enero del año que completa un ciclo de 72 años, Punto de
Edad cambiaba la biografía a la casa 1 y al ciclo siguiente, aunque el
aniversario natal todavía no hubiera ocurrido. La guía del PE quedaba fuera de
la biografía que correspondía a la casa 12.

Se reprodujo con los dos casos informados:

- Núria Alberich, nacida el 12/11/1954: el error aparecía el 01/01/2026 y el
  cambio correcto corresponde al 12/11/2026.
- Joan Solé, nacido el 30/12/1957: el error aparecía el 01/01/2029 y el cambio
  correcto corresponde al 30/12/2029.

### Corrección

`Chart.get_cycles` ya no deduce el ciclo solamente del año del calendario.
Calcula el posible ciclo de 72 años y verifica su fecha de inicio real —el
aniversario natal con su hora—. Si la fecha consultada es anterior, conserva
el ciclo previo.

### Verificación

Se añadieron `tests/test_age_cycles.py` y tres casos de regresión. En la
instancia VNC pasaron los dos límites de Núria y Joan, además de la ruta de
fecha con zona horaria usada por el selector. El 1 de enero permanece en casa
12 y ciclo 1; el cambio a casa 1 y ciclo 2 ocurre en el aniversario exacto.
Astro-Nex fue reiniciado en VNC con esta corrección para la validación manual.

Durante la validación manual se detectó que el selector de fecha de VNC entrega
una fecha con zona horaria, mientras que el cálculo histórico de lapsos usa
fechas locales sin zona. Se normalizan ambos valores a la misma hora civil
local antes de compararlos, evitando la excepción de dibujo. La prueba cubre
también esta ruta con fecha consciente de zona horaria.

## 28 de julio de 2026 — proporciones de calendario y selector de aspectos

### Incidencia observada

En GTK3, el calendario integrado y el selector de aspectos ocupaban más espacio
que sus equivalentes de Astro-Nex 1.2. El calendario ampliaba el área de carta
y los botones del selector hacían la ventana sensiblemente más alta.

### Corrección

El calendario aplica métricas compactas sólo a sus propios controles y limita
su anchura real a 230 píxeles; el panel conserva 230 × 160 píxeles, dejando
margen para que no se recorte el borde inferior. El selector de aspectos
recupera la distribución
`SPREAD` y limita sus botones a la altura histórica, sin afectar otros diálogos
ni las preferencias globales del tema GTK.

### Verificación

En macOS Apple Silicon, el calendario se asigna a 230 × 160 y el selector queda
en 360 píxeles de alto, con once botones de 27 píxeles. Se comprobará también
en VNC antes de reconstruir el DMG de distribución.
