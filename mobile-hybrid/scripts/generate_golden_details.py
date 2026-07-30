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

with open(base_dir / "mobile-hybrid" / "fixtures" / "natal_input.json", "r", encoding="utf-8") as f:
    fixture_input = json.load(f)

from astronex import nex
nex.check_home_dir(base_dir)
application = nex.application(base_dir)
options = nex.read_config(nex.home_dir)
options.home_dir = nex.home_dir
nex.langs[options.lang].install()
nex.countries.install(options.lang)

from astronex.boss import Manager
from astronex.state import Current
from astronex.chart import Chart, aspnames, planames, zodnames
from astronex.nexdate import NeXDate

state = Current(application)
nex.init_config(nex.home_dir, options, state)
manager = Manager(application, options, state)

local_birth = datetime.fromisoformat(fixture_input["birth"])
zone = timezone(fixture_input["timezone"])
state.loc.latdec = fixture_input["latitude"]
state.loc.longdec = fixture_input["longitude"]
state.loc.zone = fixture_input["timezone"]
state.calcdt = NeXDate(state, local_birth, zone)

chart = Chart("api")
chart.latitud = fixture_input["latitude"]
chart.longitud = fixture_input["longitude"]
chart.zone = fixture_input["timezone"]
chart.date = state.calcdt.dateforstore()
chart.planets, chart.houses = chart.calc(state.calcdt.dateforcalc(), state.loc, state.epheflag)

golden_dir = base_dir / "mobile-hybrid" / "tests" / "golden"
os.makedirs(golden_dir, exist_ok=True)

# 1. Orbs Config
orbs_config = {
    "orbs": state.orbs,
    "peorbs": state.peorbs
}
with open(golden_dir / "config_orbs.json", "w", encoding="utf-8") as f:
    json.dump(orbs_config, f, indent=2)

# 2. Aspects (using chart.aspects('radix') and calc_aspects)
aspects_radix = chart.aspects('radix')
# calc_aspects returns objects
calc_aspects_raw = chart.calc_aspects(chart.planets)
calc_aspects = []
for a in calc_aspects_raw:
    calc_aspects.append({
        "p1": a.p1,
        "p2": a.p2,
        "a": a.a,
        "f1": a.f1,
        "f2": a.f2
    })
with open(golden_dir / "aspects_output.json", "w", encoding="utf-8") as f:
    json.dump({"aspects_radix": aspects_radix, "calc_aspects": calc_aspects}, f, indent=2)

# 3. Dynamics
signdyn = chart.signdyn()
housedyn = chart.housedyn()
with open(golden_dir / "dynamics_output.json", "w", encoding="utf-8") as f:
    json.dump({"signdyn": signdyn, "housedyn": housedyn}, f, indent=2)

# 4. Age Progression (Punto de la Edad)
plan = [{'degree': p, 'ix': i} for i, p in enumerate(chart.planets)]
plan.sort(key=lambda x: x['degree'])
agep = chart.calc_agep(plan)
with open(golden_dir / "agep_output.json", "w", encoding="utf-8") as f:
    json.dump(agep, f, indent=2)

print("Nuevos Golden Fixtures (details) generados exitosamente.")
