# Comparación de Cartas Astrológicas: Astro-Nex vs App Móvil

Este documento registra las diferencias visuales y de cálculo entre la carta original de Python/C (`python_chart.png`) y la nueva implementación de la App (`app_chart.png`). Se actualiza conforme se van aplicando las correcciones.

---

## 1. Diferencia Matemática (Ascendente/Rotación) — [x] Solucionado (era visual)

El motor matemático WASM calcula correctamente el Ascendente. La percepción de error era causada por artefactos visuales ya corregidos.

---

## 2. Colores del Zodiaco — [x] Solucionado

- **Astro-Nex**: Fuego=Rojo, Tierra=Verde, Aire=Amarillo, Agua=Azul.
- **Antes**: Tierra=Amarillo, Aire=Lila, Agua=Verde.
- **Corrección aplicada** en `glyphs.ts`.

---

## 3. Colores de los Planetas — [x] Solucionado

- **Astro-Nex**: Sol=Naranja, Luna=Naranja, Saturno=Naranja; Mercurio/Venus/Marte/Júpiter=Azul; Urano/Neptuno=Púrpura; Plutón=Verde.
- **Antes**: Sol=Rojo, Luna=Rojo.
- **Corrección aplicada** en `glyphs.ts`.

---

## 4. Marca de agua / Texto inferior — [x] Solucionado

- Texto "Golden TestPr..." eliminado del componente `CenterData.tsx`.

---

## 5. Flecha roja central — [x] Solucionado

- El polígono de flecha del Ascendente fue eliminado de `HouseCusps.tsx`. El centro ahora está limpio.

---

## 6. Labels de casas (AC, DC, MC, IC, números) — [x] Solucionado

- Los labels ahora usan `font-family: sans-serif` en lugar de `Astro-Nex` (que los deformaba mostrando caracteres incorrectos).
- Los números 2, 3, 5, 6, 8, 9, 11, 12 son visibles en los colores correctos.

---

## 7. Líneas de Aspectos — [x] Solucionado

- **Astro-Nex**: Líneas rectas con jerarquía visual (sólidas, discontinuas, punteadas).
- **Antes**: Formas llenas curvas "fusus" sin distinción.
- **Corrección aplicada**: Ahora son `<line>` con `stroke-dasharray` por tipo.
  - Cuadratura/Oposición → Rojo sólido.
  - Trígono/Sextil → Azul discontinuo (`4,4`).
  - Quincuncio/Semisextil → Verde punteado (`1,3`).

---

## 8. Tamaño de los Glifos Planetarios — [x] Solucionado

- **Astro-Nex**: Los símbolos de los planetas son **notablemente más pequeños y delgados**, proporcionales al ancho de la banda interior donde se colocan. Se puede distinguir con claridad cada símbolo sin que "invada" el espacio de los signos zodiacales.
- **App actual**: Los glifos planetarios eran demasiado grandes.
  - **Corrección**: Se redujo `fontSize` de los planetas para coincidir con la proporción visual del motor Astro-Nex.

---

## 9. Tamaño de los Glifos del Zodiaco — [x] Solucionado

- **Astro-Nex**: Los símbolos de los signos son **grandes y expresivos** pero bien contenidos dentro del anillo zodiacal, sin rebasar los bordes.
- **App actual**: Los glifos del zodiaco eran ligeramente oversized, rozando con los glifos planetarios del anillo interior.
  - **Corrección**: Se redujo `fontSize` de los signos zodiacales.

---

## 10. Números de grados en el anillo zodiacal exterior — [x] Solucionado

- **Astro-Nex**: Muestra pequeños números grises (10, 20) dentro del anillo zodiacal exterior indicando las subdivisiones por grados de cada signo, con orientación rotacional (siguiendo el radio).
- **App actual**: Estos números de grado no existían.
  - **Corrección**: Añadidos labels de grado a 10 y 20 en gris y rotados correctamente dentro del borde exterior de la rueda.

---

## 11. Escala del anillo zodiacal (banda más estrecha) — [x] Solucionado

- **Astro-Nex**: La banda zodiacal (`R_RULED_OUTER - R_RULED_INNER`) es **más estrecha** en proporción total, dejando más espacio para los planetas en la zona interior.
- **App actual**: La banda zodiacal era más ancha, apretando el espacio para los planetas.
  - **Corrección**: Ajustados los radios `R_RULED_OUTER` y `R_RULED_INNER` a las proporciones originales.

---

## 12. Líneas de Aspectos — Grosor y Estilo fino — [x] Solucionado

- **Astro-Nex**: Las líneas de aspecto se ven **más finas y precisas**; con una jerarquía de grosor donde los aspectos mayores/tensos tienen más peso y los menores son muy sutiles.
- **App actual**: Todas las líneas tenían el mismo `stroke-width` de `0.6`.
  - **Corrección**: Implementada jerarquía de grosor donde conjunción > sextil/trígono > cuadratura/oposición > quincuncio/semisextil. También se engrosó la línea de ejes AC/MC con rojo puro como en el original.

---

## Resumen de Estado

| # | Diferencia | Estado |
|---|---|---|
| 1 | Ascendente / Rotación | ✅ Solucionado |
| 2 | Colores del Zodiaco | ✅ Solucionado |
| 3 | Colores de Planetas | ✅ Solucionado |
| 4 | Marca de agua | ✅ Solucionado |
| 5 | Flecha roja central | ✅ Solucionado |
| 6 | Labels AC/DC/MC/IC/números | ✅ Solucionado |
| 7 | Líneas de Aspectos (tipo y jerarquía) | ✅ Solucionado |
| 8 | Tamaño glifos planetarios | ✅ Solucionado |
| 9 | Tamaño glifos zodiacales | ✅ Solucionado |
| 10 | Números de grado (10, 20) orientados radialmente | ✅ Solucionado |
| 11 | Proporción banda zodiacal | ✅ Solucionado |
| 12 | Grosor de aspectos por jerarquía | ✅ Solucionado |
