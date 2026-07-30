"""HTTP API independiente para renderizar cartas de Astro-Nex.

El servicio no modifica el checkout de Astro-Nex: sólo importa su motor de
cálculo y el renderer Cairo/Pango que ya usa la aplicación GTK.  Como ese
renderer mantiene estado global histórico, las operaciones se serializan con
un candado para garantizar que una carta nunca se mezcle con otra.
"""

from __future__ import annotations

import io
import os
import sys
import threading
import ctypes
import ctypes.util
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request
from pytz import UnknownTimeZoneError, timezone


CHECKOUT = Path(os.environ.get("ASTRONEX_CHECKOUT", Path(__file__).resolve().parents[2]))
RUNTIME_HOME = Path(os.environ.get("ASTRONEX_API_HOME", Path(__file__).resolve().parent / ".runtime"))
RENDER_LOCK = threading.Lock()
MAX_DIMENSION = 2048
MIN_DIMENSION = 320

# Astro-Nex busca pysw.py y _pysw en la raíz de su checkout.  Esta API vive
# fuera de ese árbol cuando se instala en VNC, por eso se declara explícito.
if str(CHECKOUT) not in sys.path:
    sys.path.insert(0, str(CHECKOUT))

# check_home_dir usa expanduser('~'). Al redefinir HOME antes de inicializarlo,
# la base de datos/configuración de la API queda aislada de la sesión VNC.
os.environ["HOME"] = str(RUNTIME_HOME)


def _register_symbol_font() -> None:
    """Hace visible Astro-Nex.ttf sólo al proceso de la API en Linux.

    La UI GTK suele tener esa fuente instalada en el sistema. El proceso
    aislado no debe depender de ello ni instalarla globalmente: Fontconfig
    permite añadir un archivo como fuente privada antes de cargar GTK/Cairo.
    """
    if not sys.platform.startswith("linux"):
        return
    font_path = CHECKOUT / "astronex" / "resources" / "Astro-Nex.ttf"
    library_name = ctypes.util.find_library("fontconfig")
    if not font_path.is_file() or not library_name:
        return
    try:
        fontconfig = ctypes.CDLL(library_name)
        fontconfig.FcInit.restype = ctypes.c_int
        fontconfig.FcConfigGetCurrent.restype = ctypes.c_void_p
        fontconfig.FcConfigAppFontAddFile.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
        fontconfig.FcConfigAppFontAddFile.restype = ctypes.c_int
        fontconfig.FcConfigBuildFonts.argtypes = (ctypes.c_void_p,)
        fontconfig.FcConfigBuildFonts.restype = ctypes.c_int
        if fontconfig.FcInit():
            config = fontconfig.FcConfigGetCurrent()
            if config and fontconfig.FcConfigAppFontAddFile(config, str(font_path).encode("utf-8")):
                fontconfig.FcConfigBuildFonts(config)
    except OSError:
        # El renderer informará su error normal si el entorno carece de Cairo.
        pass


_register_symbol_font()

from astronex import nex  # noqa: E402


app = Flask(__name__)
_engine: tuple[Any, Any] | None = None


def _engine_state() -> tuple[Any, Any]:
    """Inicializa una sola vez el mismo motor que emplea Astro-Nex GTK."""
    global _engine
    if _engine is not None:
        return _engine

    RUNTIME_HOME.mkdir(parents=True, exist_ok=True)
    nex.check_home_dir(CHECKOUT)
    application = nex.application(CHECKOUT)
    options = nex.read_config(nex.home_dir)
    options.home_dir = nex.home_dir
    nex.langs[options.lang].install()
    nex.countries.install(options.lang)
    # Varias pantallas históricas resuelven _() cuando se importan. Este orden
    # es el mismo de nex.setup_app(): instalar idioma antes de importar GUI y
    # Manager, aunque la API no cree ninguna ventana GTK.
    from astronex.boss import Manager
    from astronex.state import Current
    state = Current(application)
    nex.init_config(nex.home_dir, options, state)
    manager = Manager(application, options, state)
    _engine = manager, state
    return _engine


def _number(payload: dict[str, Any], field: str, low: float, high: float) -> float:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
        raise ValueError(f"{field} debe ser un número entre {low} y {high}")
    return float(value)


def _dimension(payload: dict[str, Any], field: str, default: int) -> int:
    value = payload.get(field, default)
    if isinstance(value, bool) or not isinstance(value, int) or not MIN_DIMENSION <= value <= MAX_DIMENSION:
        raise ValueError(f"{field} debe ser un entero entre {MIN_DIMENSION} y {MAX_DIMENSION}")
    return value


def _chart_from_payload(payload: dict[str, Any], state: Any) -> Any:
    from astronex.chart import Chart
    from astronex.nexdate import NeXDate

    if not isinstance(payload, dict):
        raise ValueError("el cuerpo debe ser un objeto JSON")
    birth = payload.get("birth")
    if not isinstance(birth, str):
        raise ValueError("birth debe ser una fecha ISO-8601 local, por ejemplo 1990-06-15T14:30:00")
    try:
        local_birth = datetime.fromisoformat(birth)
    except ValueError as exc:
        raise ValueError("birth no tiene un formato ISO-8601 válido") from exc
    if local_birth.tzinfo is not None:
        raise ValueError("birth debe ser una hora local sin desplazamiento; indique timezone por separado")

    zone_name = payload.get("timezone")
    if not isinstance(zone_name, str):
        raise ValueError("timezone es obligatorio, por ejemplo America/Bogota")
    try:
        zone = timezone(zone_name)
    except UnknownTimeZoneError as exc:
        raise ValueError("timezone no es una zona IANA válida") from exc

    lat, lon = _set_current_location(payload, state, zone_name)
    state.calcdt = NeXDate(state, local_birth, zone)

    result = Chart("api")
    result.first = str(payload.get("firstName", ""))[:80]
    result.last = str(payload.get("lastName", ""))[:80]
    # La etiqueta de exportación histórica asume ciudad y país no vacíos.
    # Para clientes que aún no hayan integrado el buscador de localidades,
    # conservamos la carta y usamos marcadores visuales seguros.
    result.city = str(payload.get("city") or "—")[:120]
    result.region = str(payload.get("region", ""))[:80]
    result.country = str(payload.get("country") or "—")[:80]
    result.latitud = lat
    result.longitud = lon
    result.zone = zone_name
    result.date = state.calcdt.dateforstore()
    result.planets, result.houses = result.calc(state.calcdt.dateforcalc(), state.loc, state.epheflag)
    return result


def _set_current_location(payload: dict[str, Any], state: Any, zone_name: str | None = None) -> tuple[float, float]:
    """Actualiza sólo la localidad activa del motor, igual que el selector GTK."""
    lat = _number(payload, "latitude", -90, 90)
    lon = _number(payload, "longitude", -180, 180)
    resolved_zone = zone_name or payload.get("timezone")
    if not isinstance(resolved_zone, str):
        raise ValueError("timezone es obligatorio, por ejemplo America/Bogota")
    try:
        timezone(resolved_zone)
    except UnknownTimeZoneError as exc:
        raise ValueError("timezone no es una zona IANA válida") from exc
    state.loc.latdec = lat
    state.loc.longdec = lon
    state.loc.zone = resolved_zone
    state.loc.city = str(payload.get("city") or "—")[:120]
    state.loc.region = str(payload.get("region", ""))[:80]
    state.loc.country = str(payload.get("country") or "—")[:80]
    return lat, lon


def _set_transit_moment(payload: dict[str, Any], state: Any) -> None:
    """Calcula el momento de tránsito con el mismo reloj de Astro-Nex."""
    from astronex.nexdate import NeXDate

    raw_moment = payload.get("transit")
    if not isinstance(raw_moment, str):
        raise ValueError("transit debe ser una fecha ISO-8601 local")
    try:
        moment = datetime.fromisoformat(raw_moment)
    except ValueError as exc:
        raise ValueError("transit no tiene un formato ISO-8601 válido") from exc
    if moment.tzinfo is not None:
        raise ValueError("transit debe ser una hora local sin desplazamiento")
    try:
        zone = timezone(state.loc.zone)
    except UnknownTimeZoneError as exc:
        raise ValueError("timezone no es una zona IANA válida") from exc
    state.date = NeXDate(state, moment, zone)
    # set_now() sustituye state.date por datetime.now(), anulando el momento
    # elegido por el móvil. refresh_nowchart() conserva esa fecha y sólo
    # recalcula las posiciones del chart de tránsito.
    state.refresh_nowchart()


def _authorized() -> bool:
    expected = os.environ.get("ASTRONEX_API_KEY")
    return not expected or request.headers.get("X-API-Key") == expected


def _normalized_search(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", value.lower())
        if unicodedata.category(char) != "Mn"
    )


def _location_payload(loc: Any) -> dict[str, Any]:
    return {
        "id": "|".join((loc.country_code, loc.region_code, loc.city)),
        "city": loc.city,
        "region": loc.region,
        "country": loc.country,
        "timezone": loc.zone,
        "latitude": loc.latdec,
        "longitude": loc.longdec,
    }


def _normalized_sql_column(column: str) -> str:
    """Normalización SQL mínima para buscar sin exigir acentos."""
    return (
        "replace(replace(replace(replace(replace(replace(replace(lower("
        f"{column}" "),'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ü','u'),'ñ','n')"
    )


def _search_countries(query: str, limit: int) -> list[dict[str, str]]:
    from astronex import database

    normalized_query = _normalized_search(query).strip()
    if len(normalized_query) < 2:
        raise ValueError("q debe contener al menos dos caracteres")
    rows = database.local_conn.cursor().execute(
        f"SELECT code, name FROM worldnames WHERE {_normalized_sql_column('name')} LIKE ? "
        "ORDER BY name LIMIT ?",
        (f"%{normalized_query}%", limit),
    )
    return [{"id": code, "code": code, "name": name} for code, name in rows]


def _search_locations(query: str, country_code: str, limit: int) -> list[dict[str, Any]]:
    """Busca localidades directamente en la base de datos de Astro-Nex."""
    from astronex import database
    from astronex.state import Locality

    normalized_query = _normalized_search(query).strip()
    if len(normalized_query) < 2:
        raise ValueError("q debe contener al menos dos caracteres")

    cursor = database.local_conn.cursor()
    country = cursor.execute("SELECT code FROM worldnames WHERE code = ?", (country_code,)).fetchone()
    if country is None:
        raise ValueError("country debe ser un país seleccionado de Astro-Nex")
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    try:
        # El nombre de tabla se obtuvo de worldnames, nunca de la entrada de
        # texto libre. La ciudad queda siempre parametrizada.
        rows = list(cursor.execute(
            f'SELECT Ciudad, AC FROM "{country_code}" '
            f"WHERE {_normalized_sql_column('Ciudad')} LIKE ? LIMIT ?",
            (f"%{normalized_query}%", limit),
        ))
    except Exception:
        return results
    for city, region_code in rows:
        try:
            loc = Locality()
            database.fetch_worldcity(country_code, city, region_code, loc)
            item = _location_payload(loc)
        except Exception:
            continue
        if item["id"] not in seen:
            seen.add(item["id"])
            results.append(item)
    return results


@app.get("/health")
def health() -> Response:
    return jsonify(service="astronex-mobile-api", status="ok", renderer="Astro-Nex Cairo/Pango")


@app.get("/v1/locations/search")
def search_locations() -> Response:
    if not _authorized():
        return jsonify(error="unauthorized"), 401
    try:
        query = request.args.get("q", "")
        country_code = request.args.get("country", "")
        limit = min(max(int(request.args.get("limit", "12")), 1), 30)
        with RENDER_LOCK:
            _engine_state()
            locations = _search_locations(query, country_code, limit)
    except ValueError as exc:
        return jsonify(error="invalid_request", message=str(exc)), 400
    return jsonify(results=locations)


@app.get("/v1/locations/countries")
def search_countries() -> Response:
    if not _authorized():
        return jsonify(error="unauthorized"), 401
    try:
        query = request.args.get("q", "")
        limit = min(max(int(request.args.get("limit", "12")), 1), 30)
        with RENDER_LOCK:
            _engine_state()
            countries = _search_countries(query, limit)
    except ValueError as exc:
        return jsonify(error="invalid_request", message=str(exc)), 400
    return jsonify(results=countries)


@app.post("/v1/charts/details")
def chart_details() -> Response:
    """Devuelve datos técnicos calculados por Astro-Nex, sin interpretarlos."""
    if not _authorized():
        return jsonify(error="unauthorized"), 401
    payload = request.get_json(silent=True)
    try:
        with RENDER_LOCK:
            _, state = _engine_state()
            chart = _chart_from_payload(payload, state)
            from astronex.chart import aspnames, planames, zodnames

            planets = []
            for index, longitude in enumerate(chart.planets):
                normalized = float(longitude) % 360.0
                planets.append({
                    "index": index,
                    "name": planames[index],
                    "longitude": normalized,
                    "sign": zodnames[int(normalized // 30)],
                    "degree": normalized % 30.0,
                })

            aspects = []
            for aspect in chart.aspects():
                p1 = int(aspect["p1"])
                p2 = int(aspect["p2"])
                distance = abs(float(chart.planets[p1]) - float(chart.planets[p2])) % 360.0
                distance = min(distance, 360.0 - distance)
                exact_angle = int(aspect["a"]) * 30.0
                aspects.append({
                    "p1": p1,
                    "p2": p2,
                    "name": aspnames[int(aspect["a"])],
                    "angle": exact_angle,
                    "orb": abs(distance - exact_angle),
                    "goodwill": bool(aspect["gw"]),
                })
    except ValueError as exc:
        return jsonify(error="invalid_request", message=str(exc)), 400
    except Exception:
        app.logger.exception("No se pudieron preparar los datos técnicos")
        return jsonify(error="details_failed"), 500
    return jsonify(planets=planets, aspects=aspects)


@app.post("/v1/charts/render")
def render_chart() -> Response:
    if not _authorized():
        return jsonify(error="unauthorized"), 401
    payload = request.get_json(silent=True)
    try:
        with RENDER_LOCK:
            manager, state = _engine_state()
            width = _dimension(payload, "width", 1024)
            height = _dimension(payload, "height", 1024)
            operation = payload.get("operation", "draw_nat")
            if operation not in {
                "draw_nat", "draw_house", "draw_nod", "draw_soul", "draw_dharma", "draw_ur_nodal",
                "draw_local", "draw_prof", "draw_int", "draw_single", "draw_radsoul", "draw_raddharma",
                "dat_nat", "dat_house", "dat_nod", "draw_transits", "rad_and_transit", "draw_moment",
            }:
                raise ValueError("operation no está habilitada")

            if operation == "draw_moment":
                # Equivale a seleccionar "Momento actual" en Astro-Nex: la
                # carta activa es state.now, calculada para fecha y localidad
                # elegidas, sin intervenir una persona natal.
                _set_current_location(payload, state)
                _set_transit_moment(payload, state)
                chart = state.now
                render_operation = "draw_nat"
            else:
                chart = _chart_from_payload(payload, state)
                render_operation = operation
                if operation in {"draw_transits", "rad_and_transit"}:
                    _set_transit_moment(payload, state)

            # Estas son las mismas variables de estado que la exportación PNG
            # de escritorio establece antes de llamar a dispatch_pres().
            state.curr_chart = chart
            state.curr_click = state.click
            state.curr_op = render_operation
            state.opmode = "simple"
            from astronex.drawing.dispatcher import DrawMixin
            from astronex.surfaces import pngsurface

            pngsurface.opts = manager.opts
            pngsurface.minim = min(width, height)

            import cairo
            import pangocairo

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            context = pangocairo.CairoContext(cairo.Context(surface))
            context.set_source_rgb(1, 1, 1)
            context.paint()
            context.set_line_join(cairo.LINE_JOIN_ROUND)
            context.set_line_width(float(manager.opts.base))
            drawer = DrawMixin(manager.opts, pngsurface.DrawPng())
            drawer.dispatch_pres(context, width, height)
            if manager.opts.labels == "true":
                pngsurface.draw_label(context, width, height)
            output = io.BytesIO()
            surface.write_to_png(output)
    except ValueError as exc:
        return jsonify(error="invalid_request", message=str(exc)), 400
    except Exception:
        app.logger.exception("No se pudo renderizar la carta")
        return jsonify(error="render_failed"), 500

    return Response(output.getvalue(), mimetype="image/png", headers={"Cache-Control": "no-store"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8088"))
    # Astro-Nex mantiene conexiones SQLite y estado de renderer ligados al
    # hilo de creación. La API se serializa con RENDER_LOCK, por eso un único
    # hilo también evita que Flask use la conexión desde otro hilo.
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=port, threaded=False)
