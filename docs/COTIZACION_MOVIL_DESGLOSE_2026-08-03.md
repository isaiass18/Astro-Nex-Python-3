# Cotizacion Desglosada Astro-Nex Movil

Fecha: 2026-08-03

Este documento esta pensado para explicar con claridad:

- que existe hoy en la app movil
- que no existe todavia en la app
- que incluye la propuesta inicial de 2.000 EUR
- cuanto costaria cada modulo adicional del escritorio si se implementa en local dentro de la app

## Estado actual real de la app movil

Aunque en `mobile-hybrid` existen pruebas, calculos parciales y bases tecnicas para otras cartas, a nivel de app mostrable y vendible hoy solo deben considerarse visibles estas dos funciones:

- Carta Radix
- Tránsitos

Las demas cartas y funciones del escritorio no deben presentarse como si ya estuvieran entregadas en la app movil.

## Punto clave para la cotizacion

La app movil no es una copia automatica del escritorio.

Astro-Nex escritorio esta hecho en Python y GTK, mientras que la app movil usa otra arquitectura y otra capa grafica. Por eso cada carta, biografia, progresion, comparacion o diagrama debe portarse de forma individual.

Cada modulo adicional implica:

- adaptar o rehacer la logica necesaria para movil
- reproducir su representacion visual
- integrarlo a una interfaz tactil
- validarlo contra los resultados del escritorio

## Que incluye la propuesta inicial de 2.000 EUR

La propuesta base de 2.000 EUR debe entenderse como una primera fase cerrada, no como la totalidad de Astro-Nex en movil.

### Fase 1 por 2.000 EUR

Incluye:

- Carta Radix terminada, rediseñada y validada
- Tránsitos como modulo funcional dentro de la app
- 2 modulos adicionales a elegir de una lista acordada
- calculo local en el dispositivo para esos modulos
- creacion, edicion, eliminacion y almacenamiento local de personas
- busqueda de ciudades
- ubicacion por GPS
- mapa
- adaptacion de interfaz para tablet y celular
- una ronda conjunta de ajustes de diseño y usabilidad

### Lo que no incluye esta fase

- todas las cartas del escritorio
- todas las biografias
- todos los clics o comparaciones
- todos los diagramas especiales
- soporte indefinido
- cambios grandes posteriores sin nueva cotizacion

## Como recomiendo explicarlo comercialmente

La fase de 2.000 EUR entrega:

- 2 modulos base ya definidos:
  - Radix
  - Tránsitos
- 2 modulos adicionales elegidos por el cliente

En otras palabras:

- total de modulos funcionales de esta primera fase: 4
- de esos 4, dos ya estan definidos:
  - Radix
  - Tránsitos
- y quedan 2 cupos para elegir modulos adicionales

## Modulos del escritorio que aun no estan entregados en la app

Tomando como referencia el escritorio `astronex`, estos son los modulos y familias funcionales que aun no deben considerarse parte de la app entregada.

## Lista de modulos adicionales y precio individual

Los precios de abajo son valores unitarios para agregarlos despues de la fase inicial, o para usarlos como referencia si el cliente quiere sustituir uno de los 2 modulos opcionales de la fase 1 por otro de mayor o menor complejidad.

### A. Cartas simples adicionales

Estas son las mas razonables para escoger dentro de los 2 modulos adicionales de la fase inicial.

| Modulo | Precio EUR | Incluye |
|---|---:|---|
| Carta de Casas | 200 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta Nodal de Casas | 200 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta del Alma / Causal | 240 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta Dharma | 240 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta Nodal | 240 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta Local | 240 | Calculo local, visualizacion movil, integracion tactil, validacion con escritorio |
| Carta del Perfil | 260 | Port visual y funcional completo como modulo independiente |
| Carta de Integracion | 260 | Port visual y funcional completo como modulo independiente |
| Clic Individual | 280 | Calculo y visualizacion tactil especifica del modulo |
| Radix-Alma | 280 | Carta compuesta y validacion respecto al escritorio |
| Radix-Dharma | 280 | Carta compuesta y validacion respecto al escritorio |
| Planetograma | 420 | Port visual especial, interaccion y validacion propia |

### B. Fichas tecnicas y progresiones

Estas no son simplemente "otra carta". Son modulos de lectura tecnica o cronologica.

| Modulo | Precio EUR | Incluye |
|---|---:|---|
| Datos Radix | 140 | Ficha tecnica movil equivalente al escritorio |
| Datos Casas | 140 | Ficha tecnica movil equivalente al escritorio |
| Datos Nodales | 140 | Ficha tecnica movil equivalente al escritorio |
| Progresion de la edad Radix | 220 | Calculo, cronologia, interfaz movil y validacion |
| Progresion de la edad Nodal | 220 | Calculo, cronologia, interfaz movil y validacion |
| Progresion de la edad Local | 220 | Calculo, cronologia, interfaz movil y validacion |
| Progresion de la edad Alma | 220 | Calculo, cronologia, interfaz movil y validacion |
| Progresion secundaria | 360 | Tecnica temporal completa, integracion y validacion |
| Revolucion solar | 360 | Tecnica temporal completa, integracion y validacion |
| Radix con transitos | 340 | Vista compuesta y controles temporales dedicados |

### C. Biografias

Cada biografia debe considerarse un modulo independiente.

| Modulo | Precio EUR | Incluye |
|---|---:|---|
| Biografia Radix | 280 | Logica, visualizacion movil y validacion |
| Biografia Nodal | 280 | Logica, visualizacion movil y validacion |
| Biografia Alma | 280 | Logica, visualizacion movil y validacion |
| Biografia Dharma | 300 | Logica, visualizacion movil y validacion |

### D. Clics y comparaciones entre cartas

Estos modulos suelen requerir dos cartas y una logica visual mas compleja.

| Modulo | Precio EUR | Incluye |
|---|---:|---|
| Casas-Casas | 300 | Doble carta, comparacion y visualizacion movil |
| Nodal-Nodal | 300 | Doble carta, comparacion y visualizacion movil |
| Casas-Nodal | 320 | Doble carta, comparacion y visualizacion movil |
| Nodal-Casas | 320 | Doble carta, comparacion y visualizacion movil |
| Alma-Alma | 320 | Doble carta, comparacion y visualizacion movil |
| Radix-Radix | 300 | Doble carta, comparacion y visualizacion movil |
| Radix-Alma | 340 | Doble carta, comparacion y visualizacion movil |
| Alma-Nodal | 340 | Doble carta, comparacion y visualizacion movil |
| Clic subjetivo | 280 | Port funcional del modulo con UI tactil |
| Puente | 380 | Modulo compuesto, mas complejo que un clic simple |

### E. Diagramas y modulos especiales

Estos son de los mas costosos por su complejidad visual o relacional.

| Modulo | Precio EUR | Incluye |
|---|---:|---|
| Comparacion pareja I | 360 | Logica relacional, vista movil y validacion |
| Comparacion pareja II | 360 | Logica relacional, vista movil y validacion |
| Estrella de ascenso | 320 | Port visual y funcional completo |
| Estrella maravillosa | 340 | Port visual y funcional completo |
| Analisis de polaridades | 320 | Port visual y funcional completo |
| Uniones corona | 340 | Port visual y funcional completo |
| Panal de la pareja | 520 | Modulo visual especial de alta complejidad |
| Comparacion PE | 320 | Port visual y funcional completo |
| Contra horoscopos | 320 | Port visual y funcional completo |
| Cuadrantes dinamicos | 220 | Port visual y funcional completo |
| Clic Cuadrantes dinamicos | 300 | Port visual y funcional completo |
| Estrellas dinamicas | 280 | Port visual y funcional completo |

## Funciones transversales cotizables aparte

Estas no son cartas, pero tienen valor propio y conviene nombrarlas por separado.

| Funcion | Precio EUR | Incluye |
|---|---:|---|
| Importacion AAF compatible con Astro-Nex escritorio | 340 | Lectura, parseo, integracion y pruebas de intercambio |
| Exportacion AAF compatible con Astro-Nex escritorio | 260 | Generacion de archivo compatible y validacion |
| Gestion completa de personas guardadas | 220 | Crear, editar, eliminar, persistencia y mejoras de flujo |
| Mejora de almacenamiento local | 260 | Persistencia mas robusta que el estado actual |
| Ajuste extra de interfaz para tablet y movil | 300 | Refinamiento de layouts, densidad y usabilidad |
| QA final por hito | 340 | Revision funcional, pruebas cruzadas y estabilizacion |

## Como usar esta tabla dentro de la propuesta de 2.000 EUR

La manera mas clara de presentarlo seria asi:

### Paquete inicial de 2.000 EUR

Incluye:

- Radix
- Tránsitos
- 2 modulos adicionales a elegir

### Recomendacion de eleccion para esos 2 modulos

Si quieres mantener el alcance controlado dentro del presupuesto inicial, lo mas razonable es que esos 2 modulos adicionales salgan de este grupo:

- Carta de Casas
- Carta Nodal de Casas
- Carta del Alma / Causal
- Carta Dharma
- Carta Nodal
- Carta Local

Eso te permite defender que la fase 1 sigue siendo coherente tecnicamente y no se dispara en complejidad.

### Si el cliente quiere un modulo mas complejo en vez de uno simple

Puedes usar esta regla:

- si elige un modulo de 200 EUR, entra comodamente dentro del equilibrio de la fase 1
- si elige un modulo de 240 EUR, sigue siendo viable pero ajusta mas el margen
- si elige un modulo de 280 EUR o mas, conviene cotizarlo como adicional fuera del paquete inicial o cambiar el alcance

## Propuesta comercial resumida para decirlo de forma clara

Puedes plantearlo asi:

"La primera fase por 2.000 EUR no incluye todo Astro-Nex en movil. Incluye la base funcional de la app, con Radix y Tránsitos, mas dos modulos adicionales a elegir previamente. Cada carta, biografia, progresion, comparacion o diagrama adicional del escritorio se considera un modulo independiente y se cotiza por separado segun su complejidad."

## Recomendacion concreta

Si te piden una cotizacion mas completa, yo recomendaria entregar dos niveles:

### Nivel 1

Una propuesta principal muy simple:

- 2.000 EUR
- incluye Radix + Tránsitos + 2 modulos adicionales

### Nivel 2

Un anexo con tabla de modulos adicionales:

- cartas simples: 200 a 240 EUR
- cartas compuestas o especiales: 260 a 420 EUR
- biografias: 280 a 300 EUR
- clics y comparaciones: 280 a 380 EUR
- tecnicas temporales especiales: 340 a 360 EUR
- funciones AAF y mejoras transversales: 220 a 340 EUR

## Conclusion

La app hoy no debe presentarse como si ya incluyera todas las cartas visibles en el codigo experimental. Comercialmente, lo correcto es decir que la app muestra hoy Radix y Tránsitos, y que la fase inicial de 2.000 EUR entrega esos dos modulos mas dos modulos adicionales acordados previamente.

Todo lo demas debe tratarse como modulo adicional independiente con precio propio.
