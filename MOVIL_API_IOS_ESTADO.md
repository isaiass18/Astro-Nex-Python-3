# Estado provisional — API móvil e iOS

**Fecha:** 28 de julio de 2026  
**Estado Git:** trabajo local pendiente. **No añadir, confirmar ni publicar en
GitHub hasta recibir una instrucción explícita.**

## Objetivo

Crear una app móvil de Astro-Nex que conserve las cartas originales sin
reescribir su geometría, símbolos, cálculos ni aspectos. La app iOS pide los
renders al servidor y el servidor usa el motor Python/Cairo/Pango de
Astro-Nex para generar los PNG.

## Separación respecto a Astro-Nex y VNC

No se modificó ningún archivo bajo `astronex/`, `nex.py` ni el checkout que
se muestra por noVNC. La API es un proceso y una carpeta independientes; su
única relación con el checkout es importarlo como dependencia de lectura para
usar el motor original.

| Componente | Ubicación | Función |
| --- | --- | --- |
| Astro-Nex/noVNC | `/home/ubuntu/astronex-github-vnc-test` | Aplicación GTK original, visible en el puerto 6080. |
| API móvil | `/home/ubuntu/astronex-mobile-api` | Adaptador Flask independiente. |
| Estado de la API | `/home/ubuntu/astronex-mobile-api/runtime/.astronex` | Configuración y base de datos propias de la API. |
| App iOS local | `mobile/ios` | Proyecto SwiftUI/Xcode. |

La API serializa los renders con un candado: el renderer histórico mantiene
estado global y así una solicitud no puede mezclarse con otra. También carga
`astronex/resources/Astro-Nex.ttf` como fuente privada mediante Fontconfig,
para que los símbolos astrológicos aparezcan correctamente sin instalar nada
en el sistema ni afectar VNC.

### Protección obligatoria de VNC y de la API

Estas reglas aplican a cualquier sesión o chat futuro:

- **No escribir, sincronizar, reemplazar, actualizar ni reiniciar** nada bajo
  `/home/ubuntu/astronex-github-vnc-test`. Esa ruta pertenece exclusivamente a
  Astro-Nex de escritorio/noVNC.
- **No desplegar la API dentro del checkout VNC.** Los archivos de API se
  sincronizan únicamente hacia `/home/ubuntu/astronex-mobile-api/`.
- La variable `ASTRONEX_CHECKOUT` de la API señala el checkout VNC sólo para
  importar el motor y recursos en modo lectura. No convertirlo en destino de
  `rsync`, `scp`, instalación de dependencias ni generación de archivos.
- El reinicio permitido para cambios móviles es únicamente el proceso Flask de
  `/home/ubuntu/astronex-mobile-api`; no los procesos `nex.py`, Xvfb, x11vnc ni
  websockify/noVNC.
- Si alguna tarea requiere cambiar el checkout VNC, su configuración o el
  servicio noVNC, detenerse y pedir autorización explícita antes de hacerlo.

## API desplegada

- Salud: `GET http://3.19.232.60:8088/health`
- Render: `POST http://3.19.232.60:8088/v1/charts/render`
- Datos técnicos: `POST http://3.19.232.60:8088/v1/charts/details`
- Países: `GET http://3.19.232.60:8088/v1/locations/countries?q=...`
- Ciudades: `GET http://3.19.232.60:8088/v1/locations/search?q=...&country=CO`
- Autenticación: cabecera `X-API-Key`.
- Puerto temporal: `8088`.
- Proceso: `/home/ubuntu/astronex-mobile-api/.venv/bin/python /home/ubuntu/astronex-mobile-api/app.py`.
- Registro: `/home/ubuntu/astronex-mobile-api/api.log`.
- PID: `/home/ubuntu/astronex-mobile-api/api.pid`.

La clave reside únicamente en `/home/ubuntu/astronex-mobile-api/.env` y en el
archivo local ignorado `mobile/ios/AstroNexMobile/Secrets.xcconfig`. No debe
copiarse a documentación, Git, capturas ni mensajes.

### Operaciones de carta habilitadas

- `draw_nat`, `draw_house`, `draw_nod`
- `draw_soul`, `draw_dharma`, `draw_ur_nodal`
- `draw_local`, `draw_prof`, `draw_int`, `draw_single`
- `draw_radsoul`, `draw_raddharma`
- `dat_nat`, `dat_house`, `dat_nod`
- `draw_transits`, `rad_and_transit`
- `draw_moment`: carta de Momento actual para la fecha, hora y localidad
  enviadas por la app. Internamente usa `state.now` y el render `draw_nat`,
  igual que la carta activa de Momento actual en el escritorio.

El endpoint `/v1/charts/details` devuelve, sin interpretaciones, posiciones
de los 11 planetas/puntos y aspectos con su orbe. Los valores se calculan por
Astro-Nex; no existe una segunda calculadora en la API.

## Momento actual y tránsitos

La pantalla iOS **Momento actual** usa una localidad propia, configurable en
esa misma pantalla mediante el buscador de país y ciudad de Astro-Nex. La
fecha y hora se pueden elegir manualmente, volver a ahora o avanzar por
minutos, horas, días, meses y años.

Los botones `+` y `−` son controles continuos nativos: realizan un paso al
tocar y repiten mientras se mantiene el dedo. Durante la carga se conserva la
carta anterior, que se funde hacia la nueva cuando llega; el indicador aparece
en el botón **Actualizar momento**, no sobre la imagen.

La corrección relevante del backend fue sustituir el uso de `state.set_now()`
(que reemplazaba la fecha enviada por la hora real del servidor) por
`state.refresh_nowchart()` después de crear la fecha solicitada. Se verificó
que fechas distintas devuelven PNG distintos.

## Estado de la app iOS

La pantalla principal se titula **Cartas Astro-Nex** y contiene:

1. Datos de nacimiento y buscador de país/ciudad respaldado por la base de
   datos de Astro-Nex.
2. Selector horizontal de las doce cartas disponibles: Radix, Casas, Nodal de
   Casas, Causal, Dharma, Nodal, Local, Perfil, Integración, Clic individual,
   Radix-Causal y Radix-Dharma.
3. Vista a pantalla completa con zoom para cartas, fichas y Momento actual.
4. Opción de guardar una persona al generar; menú Personas con carga, edición
   y eliminación local.
5. Menú Datos con las fichas Radix, Casas y Nodal, más posiciones y aspectos
   técnicos calculados por el endpoint de detalles.
6. Menú Momento actual con ubicación independiente, fecha/hora, avance y
   transición de la carta.
7. Botón para ocultar el teclado.

Al abrir se muestra durante un instante el splash original de Astro-Nex. El
icono de la app usa el recurso original `astronex/resources/iconex-48.png`.

## Archivos locales relevantes

```text
mobile/
├── api/
│   ├── app.py                 # API Flask y adaptador del motor original
│   ├── requirements.txt
│   ├── start-vnc-api.sh       # Inicio exclusivo de la API
│   └── README.md
└── ios/
    ├── AstroNexMobile.xcodeproj
    ├── AstroNexMobile/
    │   ├── AstroNexMobileApp.swift
    │   ├── ContentView.swift
    │   ├── Info.plist
    │   ├── Secrets.xcconfig.example
    │   └── Secrets.xcconfig   # Ignorado por Git; contiene valores de prueba
    └── README.md
```

`.gitignore` incluye `mobile/ios/AstroNexMobile/Secrets.xcconfig`.

## Compilación e instalación iPhone

- Xcode 26.6: `/Applications/Xcode.app`.
- Dispositivo de prueba: `iPhone de isaias` (iPhone 17 Pro Max).
- Identificador de la app: `com.astronex.app`.
- La compilación Debug se firma con el equipo personal ya configurado en
  Xcode y se instala desde consola con `xcrun devicectl`.

No guardar credenciales de Apple en el repositorio.

## Pendiente antes de producción

- Dominio, HTTPS, proxy inverso y cierre del puerto directo 8088.
- Autenticación por usuario o tokens temporales; la clave fija actual es sólo
  para la prueba.
- Límites de solicitudes y registro estructurado.
- Servicio persistente `systemd` para la API, independiente de noVNC.
- Android reutilizando la misma API.
- Funciones futuras: exportar/compartir, resaltar aspectos en la rueda,
  revolución solar/lunar, progresiones y sinastría.

## Regla de publicación

Hasta una orden explícita del propietario:

- no ejecutar `git add`;
- no crear commits;
- no ejecutar `git push`;
- no copiar `Secrets.xcconfig` ni `.env` a ningún lugar público.
