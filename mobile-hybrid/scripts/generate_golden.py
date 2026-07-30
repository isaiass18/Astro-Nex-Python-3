import json
import os
import sys
from pathlib import Path
from datetime import datetime
from pytz import UnknownTimeZoneError, timezone

base_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(base_dir))

# Redirect HOME to avoid sandbox permission errors
runtime_home = base_dir / "mobile-hybrid" / ".runtime"
runtime_home.mkdir(parents=True, exist_ok=True)
os.environ["HOME"] = str(runtime_home)

fixture_input = {
    "birth": "1990-06-15T12:30:00",
    "timezone": "America/Bogota",
    "latitude": 4.6097,
    "longitude": -74.0817,
    "firstName": "Golden",
    "lastName": "Test",
    "city": "Bogotá",
    "country": "CO"
}

fixtures_dir = base_dir / "mobile-hybrid" / "fixtures"
golden_dir = base_dir / "mobile-hybrid" / "tests" / "golden"

os.makedirs(fixtures_dir, exist_ok=True)
os.makedirs(golden_dir, exist_ok=True)

with open(fixtures_dir / "natal_input.json", "w", encoding="utf-8") as f:
    json.dump(fixture_input, f, indent=2, ensure_ascii=False)

from astronex import nex

nex.check_home_dir(base_dir)
application = nex.application(base_dir)
options = nex.read_config(nex.home_dir)
options.home_dir = nex.home_dir
nex.langs[options.lang].install()
nex.countries.install(options.lang)

# Import AFTER installing langs so _() is defined in builtins
from astronex.boss import Manager
from astronex.state import Current
from astronex.chart import Chart, aspnames, planames, zodnames
from astronex.nexdate import NeXDate

state = Current(application)
nex.init_config(nex.home_dir, options, state)
manager = Manager(application, options, state)

local_birth = datetime.fromisoformat(fixture_input["birth"])
zone = timezone(fixture_input["timezone"])
lat = fixture_input["latitude"]
lon = fixture_input["longitude"]
state.loc.latdec = lat
state.loc.longdec = lon
state.loc.zone = fixture_input["timezone"]
state.loc.city = fixture_input["city"]
state.loc.country = fixture_input["country"]

state.calcdt = NeXDate(state, local_birth, zone)

chart = Chart("api")
chart.first = fixture_input["firstName"]
chart.last = fixture_input["lastName"]
chart.city = fixture_input["city"]
chart.country = fixture_input["country"]
chart.latitud = lat
chart.longitud = lon
chart.zone = fixture_input["timezone"]
chart.date = state.calcdt.dateforstore()
chart.planets, chart.houses = chart.calc(state.calcdt.dateforcalc(), state.loc, state.epheflag)

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

data = {"planets": planets, "aspects": aspects, "houses": chart.houses, "birthYear": local_birth.year}

with open(golden_dir / "natal_output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Golden fixture generated successfully.")
