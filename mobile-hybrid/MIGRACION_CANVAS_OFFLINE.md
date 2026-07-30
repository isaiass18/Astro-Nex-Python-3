# Propuesta de Refactorización Visual Offline: De SVG a HTML5 Canvas

**Fecha:** 29 de julio de 2026
**Alcance:** Proyecto `mobile-hybrid`
**Objetivo:** Lograr paridad visual píxel a píxel con el motor original de Astro-Nex (Cairo) de forma 100% offline, eliminando la complejidad actual de generar archivos SVG.

---

## 1. El Problema Actual: La Fricción del SVG

Actualmente, el proyecto híbrido está utilizando el script `scripts/generate_chart_svg.mjs` para intentar replicar los dibujos que Astro-Nex genera nativamente con **Python y Cairo** (`astronex/drawing/`). 

Este enfoque está causando un "súper lío" de mantenimiento y diferencias visuales ("no quedan iguales") por una razón arquitectónica profunda: **incompatibilidad de modelos mentales**.

*   **Cairo (Original):** Es un motor **imperativo**. Funciona como un pincel. Se le dan órdenes directas: *"Muévete a X, haz un arco, rellena, cambia de color, traza una línea"*.
*   **SVG (Actual híbrido):** Es un motor **declarativo**. Funciona estructurando nodos en un árbol DOM (`<circle>`, `<path>`, `<g>`). 

Traducir la matemática de un pincel (Cairo) a etiquetas (SVG) requiere rediseñar toda la lógica geométrica desde cero, lo cual es propenso a errores y hace casi imposible alcanzar la paridad perfecta sin un esfuerzo monumental.

## 2. La Solución Definitiva: HTML5 `<canvas>`

Para resolver esto sin necesidad de compilar C para iOS y manteniendo la app 100% offline, la solución es abandonar el SVG y adoptar el **API de Canvas de HTML5 / Javascript**.

### ¿Por qué Canvas?
El API de Canvas 2D fue diseñado con una filosofía idéntica a la de Cairo (de hecho, comparten raíces conceptuales e incluso librerías subyacentes en algunos navegadores). Ambos son **imperativos**.

Esto significa que **el código Python de Astro-Nex se puede traducir casi línea por línea a Javascript**, conservando la misma matemática, los mismos ángulos y las mismas transformaciones de matrices.

#### Ejemplo de Traducción Directa (1 a 1)

Tomando la función `d_inner_circles` de `astronex/drawing/coredraw.py`:

**Código Original (Python / Cairo):**
```python
def d_inner_circles(self, cr, radius):
    cr.save()
    cr.set_source_rgb(1, 1, 1)
    cr.arc(0, 0, radius * R_VERYINNER, 0, 360 * RAD)
    cr.fill_preserve()
    
    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.35 * cr.get_line_width())
    cr.stroke()
    cr.restore()
```

**Código Nuevo (Javascript / Canvas):**
```javascript
function d_inner_circles(ctx, radius) {
    ctx.save();
    ctx.fillStyle = "rgb(255, 255, 255)";
    ctx.beginPath();
    ctx.arc(0, 0, radius * R_VERYINNER, 0, 360 * RAD);
    ctx.fill();
    
    ctx.strokeStyle = "rgb(0, 0, 0)";
    ctx.lineWidth = 0.35 * ctx.lineWidth;
    ctx.stroke();
    ctx.restore();
}
```

Como se observa, la lógica geométrica no requiere ser rediseñada, solo "transcrita" a su equivalente en JS.

---

## 3. Plan de Migración Recomendado

Para implementar este cambio en `mobile-hybrid`, se sugiere el siguiente flujo de trabajo:

### Fase 1: Preparación
1. **Mantener el motor de cálculo:** Continuar usando `@swisseph/browser` (WASM) como fuente de verdad para los grados planetarios.
2. **Depreciar el generador SVG:** Congelar el desarrollo en `generate_chart_svg.mjs`.

### Fase 2: El Nuevo Motor de Renderizado
1. **Crear el lienzo:** En la interfaz de React, reemplazar el contenedor del SVG por un componente nativo `<canvas id="astro-chart" width={1000} height={1000} />`.
2. **Crear el adaptador (`CanvasRenderer.ts`):** Crear una clase en TypeScript que reciba el contexto del canvas (`ctx = canvas.getContext('2d')`).
3. **Portar Constantes:** Copiar las constantes de `coredraw.py` a JS (ej. `PHI`, `RAD`, radios como `R_INNER`, etc.).

### Fase 3: Traducción Secuencial
Comenzar a traducir las funciones de `astronex/drawing/` en orden de las capas de la carta (de atrás hacia adelante):
1. `d_inner_circles` y `d_ruline` (Esqueleto base).
2. `draw_cusps` y `draw_signs` (Cúspides y Signos).
3. `draw_planets` y `make_plines` (Planetas y líneas de aspectos).

### Fase 4: Símbolos y Fuentes
Para los glifos planetarios y astrológicos:
* En lugar de dibujar paths complejos a mano, importar la fuente original (`Astro-Nex.ttf` mencionada en la documentación) usando CSS `@font-face`.
* En Canvas, usar `ctx.font = "24px 'Astro-Nex'"` y dibujar los glifos directamente como texto usando `ctx.fillText(simbolo, x, y)`. Esto garantiza que los símbolos sean idénticos a los del escritorio sin esfuerzo de trazado.

---

## Conclusión

Migrar de SVG a Canvas elimina la barrera de la traducción visual. Al hablar el mismo "idioma geométrico" que Cairo, el equipo podrá reutilizar el 90% de la lógica matemática de Python en Javascript, logrando cartas astrológicas idénticas a las originales de forma eficiente, mantenible y completamente offline en iOS y Android.
