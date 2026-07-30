# API móvil independiente

Esta carpeta es un adaptador: no modifica `astronex/`. En VNC se instala en
`/home/ubuntu/astronex-mobile-api` y recibe el checkout existente sólo como
dependencia de lectura. Renderiza PNG con `DrawMixin`, Cairo y Pango, que son
exactamente las mismas clases de Astro-Nex escritorio.

## Endpoints

`POST /v1/charts/render` devuelve `image/png`.

```json
{
  "firstName": "Ana",
  "lastName": "García",
  "birth": "1990-06-15T14:30:00",
  "timezone": "America/Bogota",
  "latitude": 4.711,
  "longitude": -74.0721,
  "city": "Bogotá",
  "country": "Colombia",
  "operation": "draw_nat",
  "width": 1024,
  "height": 1024
}
```

Incluya `X-API-Key` en todas las rutas bajo `/v1/`. Además del render, están
disponibles:

- `POST /v1/charts/details`, con posiciones y aspectos técnicos calculados
  por Astro-Nex;
- `GET /v1/locations/countries?q=...` y
  `GET /v1/locations/search?q=...&country=CO`, para el buscador de
  localidades;
- `GET /health`, sin autenticación, para comprobar el proceso.

Las operaciones admitidas por el render son `draw_nat`, `draw_house`,
`draw_nod`, `draw_soul`, `draw_dharma`, `draw_ur_nodal`, `draw_local`,
`draw_prof`, `draw_int`, `draw_single`, `draw_radsoul`, `draw_raddharma`,
`dat_nat`, `dat_house`, `dat_nod`, `draw_transits`, `rad_and_transit` y
`draw_moment`.

## Nota de producción

El primer despliegue escucha en el puerto 8088 para pruebas. Antes de enviar
la app a App Store o Play Store debe publicarse detrás de HTTPS con un dominio
y certificado; iOS no acepta HTTP plano como configuración de producción.
La API se despliega fuera del checkout de noVNC y lo usa sólo en modo lectura.
