# -*- coding: utf-8 -*-
import math
import re
from datetime import datetime, timedelta, date, time
from pytz import timezone
import pysw
from .utils import parsestrtime


def _angular_difference(target, value):
    """Shortest signed angular distance from ``value`` to ``target``."""
    return (target - value + 180.0) % 360.0 - 180.0


def solar_return_julday(target_longitude, year, month, day, epheflag=4):
    """Find the UTC Julian day of the annual return of the natal Sun.

    The former implementation compared raw longitudes in a succession of
    loops.  That fails near Aries (0°/360°) and can select the previous year.
    Newton iteration with wrapped angular differences converges on the return
    nearest the birthday regardless of the sign boundary.
    """
    julday = pysw.julday(year, month, day, 0.0)
    for _ in range(12):
        _, longitude, message = pysw.calc(julday, 0, epheflag)
        if message:
            raise RuntimeError(message)
        difference = _angular_difference(target_longitude, longitude)
        if abs(difference) < 1e-8:
            return julday

        _, next_longitude, message = pysw.calc(julday + 0.05, 0, epheflag)
        if message:
            raise RuntimeError(message)
        speed = _angular_difference(next_longitude, longitude) / 0.05
        if speed <= 0:
            raise RuntimeError("invalid solar speed while calculating solar return")
        julday += difference / speed
    return julday


def solar_rev(boss):
    date, time = parsestrtime(boss.state.curr_chart.date)
    d, m, _ = [int(i) for i in date.split("/")]
    nowyear = boss.state.date.dt.year
    sun = boss.state.curr_chart.planets[0]
    julday = solar_return_julday(sun, nowyear, m, d, boss.state.epheflag)

    sol = pysw.revjul(julday)
    zone = boss.state.curr_chart.zone
    dt = boss.state.date.getnewdt(sol)
    boss.da.panel.set_date_only(dt)

def sec_prog(boss):
    chart = boss.state.curr_chart
    if not chart.date:
        chart = boss.state.now

    date = strdate_to_date(chart.date)
    nowyear = boss.state.date.dt.year
    birthyear = date.year
    yearsfrombirth = nowyear - birthyear
    progdate = date + timedelta(yearsfrombirth)

    if not boss.da.sec_alltimes:
        dt = combine_date(progdate)
        boss.state.calcdt.setdt(dt)
        boss.state.setprogchart(chart)
        birthday = synthbirthday(date,nowyear)
        boss.da.panel.set_date_only(birthday)
    else:
        nowdate = boss.state.date.dt
        prev_birthday = synthbirthday(date,nowyear)
        next_birthday = synthbirthday(date,nowyear+1)
        delta = nowdate - prev_birthday
        if delta.days < 0:
            next_birthday = prev_birthday
            prev_birthday = synthbirthday(date,nowyear-1)
            delta = nowdate - prev_birthday
            yearsfrombirth -= 1
        yeardelta = next_birthday - prev_birthday
        wholedelta = delta.days*86400+delta.seconds
        wholeyeardelta = yeardelta.days*86400+yeardelta.seconds
        frac = wholedelta/float(wholeyeardelta)
        oneday_ahead = date + timedelta(yearsfrombirth+1)
        daydelta = (oneday_ahead - progdate)
        daydelta = timedelta(daydelta.days*frac,daydelta.seconds*frac)
        inbetween_progdate = progdate + daydelta
        dt = combine_date(inbetween_progdate)
        boss.state.calcdt.setdt(dt)
        boss.state.setprogchart(chart)

#curr.setloc(city,code)
#curr.calcdt.setdt(datetime.datetime.combine(self.date,self.time))
#curr.setchart()

def strdate_to_date(strdate):
    # Progressions use the stored local date/time, not the trailing offset.
    # Older Python 3 builds wrote decimal offsets such as ``+5.5:30.0``.
    match = re.match(r"^(\d{1,4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::\d{2})?", strdate)
    if not match:
        raise ValueError("Invalid Astro-Nex chart date: %r" % strdate)
    y, mo, d, h, m = [int(value) for value in match.groups()]
    return datetime(y, mo, d, h, m, 0, tzinfo=timezone('UTC'))

def combine_date(dt):
    newdate = date(dt.year,dt.month,dt.day)
    newtime = time(dt.hour,dt.minute,dt.second)
    return datetime.combine(newdate,newtime)

def synthbirthday(date,nowyear):
    h = date.hour
    m = date.minute
    s = date.second
    y = nowyear
    mo = date.month
    d = date.day
    return datetime(y,mo,d,h,m,s,tzinfo=timezone('UTC'))
