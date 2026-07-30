# Análisis Forense Exhaustivo: Astro-Nex (Python) vs App Móvil (React)

Este documento detalla todas las discrepancias geométricas, algorítmicas y visuales encontradas al analizar el código fuente original de Astro-Nex (`astronex/drawing/`) en comparación con la implementación inicial de la App en React.

## 1. Algoritmo de Aspectos: El "Fusus"

El mayor descubrimiento visual es que Astro-Nex **no usa líneas simples ni guiones** para dibujar los aspectos astrológicos (conjunción, cuadratura, trígono, etc.). 

### Implementación Original (Python)
En el archivo `aspects.py`, la clase `FususAspect` es la encargada de dibujar los aspectos:
```python
def draw(self, cr, r, aspects):
    scl = r * 0.00065
    for asp in aspects:
        f = 3*((5-5*asp.f1)+(5-5*asp.f2)) * scl
        x1 = r * math.cos(asp.p1 * RAD)
        y1 = r * math.sin(asp.p1 * RAD)
        x2 = r * math.cos(asp.p2 * RAD)
        y2 = r * math.sin(asp.p2 * RAD)
        xx = (x2 + x1)/2; yy = (y2 + y1)/2
        cr.set_source_rgb(*asp.col)
        angle = math.atan((y2-y1)/(x2-x1)) / RAD 
        dx = math.cos((90+angle)*RAD)* f
        dy = math.sin((90+angle)*RAD)* f
        
        # Dibujo de curvas Bézier para crear el huso (spindle)
        cr.move_to(x1,y1)
        cr.curve_to((xx+dx),(yy+dy),(xx+dx),(yy+dy),x2,y2)
        cr.curve_to((xx-dx),(yy-dy),(xx-dx),(yy-dy),x1,y1)
        cr.fill_preserve()
        cr.set_line_width(0.425)
        cr.stroke()
```
- **Forma Geométrica**: Dibuja un polígono curvo ("huso" o "spindle") usando dos curvas Bézier Cúbicas. El polígono se rellena con el color del aspecto.
- **Dinámica**: Es grueso en el centro (controlado por `dx`, `dy` y `f`) y afilado en los extremos (donde toca los planetas).
- **Grosor Condicional**: El grosor `f` depende de la "fuerza" u "orbe" del aspecto (`asp.f1`, `asp.f2`). Si es muy exacto, el huso es más "gordo".
- **Visualización**: Al ser formas rellenas con puntas finas, en resoluciones bajas o pantallas antiguas pueden aparentar ser líneas intermitentes o punteadas. El usuario describió correctamente que van "de gruesa a delgada".

### Problema en la App
La App usaba etiquetas SVG `<line>` simples. Posteriormente, en un intento de imitar los estilos, se les aplicó la propiedad `stroke-dasharray` para simular distintos grosores o estilos. Esto rompía completamente con la estética orgánica y dinámica original.

---

## 2. Arquitectura de los Anillos Zodiacales

El anillo donde residen los signos zodiacales no es una franja simple.

### Implementación Original (`coredraw.py` y `roundedcharts.py`)
Existen **tres** constantes de radio que definen la estructura geométrica:
```python
R_RULEDINNER = 0.65 
R_RULEDOUTER = 0.78
R_RULEDMID   = 0.84
```
Esto genera 3 círculos concéntricos y dos "carriles":
1. **Carril Principal (0.65 - 0.78)**: Contiene exclusivamente los glifos de los signos zodiacales.
2. **Carril Exterior (0.78 - 0.84)**: Una vía secundaria muy estrecha que aloja las subdivisiones de los decanatos/grados (los números "10" y "20").
3. **Muescas (Ticks)**: Tienen orientaciones algorítmicas:
   - El anillo interno (`0.65`) proyecta sus líneas hacia **afuera**.
   - Los anillos medio y exterior (`0.78` y `0.84`) proyectan sus marcas hacia **adentro**.

### Problema en la App
La App asumía dos anillos, mezclando los glifos y los grados en un mismo espacio, lo que generaba saturación visual y rompía las proporciones del `canvas` central.

---

## 3. Líneas de Cúspides y Ejes Cardinales (Casas)

Las líneas que dividen el círculo interior (las casas astrológicas) tienen una jerarquía estricta.

### Implementación Original
- **Ascendente (AC)**: Posee una flecha o marcador en forma de triángulo proyectado hacia el exterior de la rueda.
- **Colores de Cúspides**: Siguen un ciclo fijo y no son aleatorios ni monocromáticos:
  ```python
  cusp_cols = cycle(((0.8,0,0), (0,0,0.6), (0,0.5,0)))  # Rojo, Azul, Verde
  ```
- **Grosores (Widths)**: Las casas angulares/cardinales (AC, MC, IC, DC) tienen un peso de línea mucho mayor que las casas sucedentes o cadentes.

### Problema en la App
- Ejes AC-DC dibujados muy finos o del color incorrecto.
- Falta del cabezal de flecha en el Ascendente, crucial para la rápida lectura de la carta.

---

## Conclusión y Próximos Pasos

La discrepancia central radica en que la versión Python usa **geometría analítica dinámica** (curvas de Bézier calculadas en tiempo de ejecución, grosores basados en fuerza gravitacional/aspecto) mientras que la App inicial optó por SVG estáticos y primitivos. 

El paso correctivo es trasladar la matemática del `FususAspect` y la estructura tricéntrica al motor SVG de React.
