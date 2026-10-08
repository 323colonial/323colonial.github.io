#!/usr/bin/env python3
"""Approximate clear-sky horizontal illuminance by solar elevation, and times that give a chosen elevation.
Table values are standard order-of-magnitude figures for twilight (sunset ~400 lx, end of civil ~3 lx, end of nautical ~0.01 lx, moonless night ~0.001 lx)."""
import datetime as dt, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot
TABLE = [(-18, -3.0), (-15, -2.8), (-12, -2.1), (-9, -0.9), (-6, 0.5), (-3, 1.9), (0, 2.7), (2, 3.2), (5, 3.7), (10, 4.1), (20, 4.5), (35, 4.8), (60, 5.0)]   # (elevation deg, log10 lux)
def loglux(el):
    if el <= TABLE[0][0]: return TABLE[0][1]
    for (a, x), (b, y) in zip(TABLE, TABLE[1:]):
        if el <= b: return x + (y - x) * (el - a) / (b - a)
    return TABLE[-1][1]
def elev_for(L):
    for (a, x), (b, y) in zip(TABLE, TABLE[1:]):
        if x <= L <= y: return a + (b - a) * (L - x) / (y - x)
def elevation(m, d, h, mi):
    keep = pilot.STEPS[0]; pilot.STEPS[0] = (0, '', '', (m, d, h, mi), ''); az, el = pilot.sun(0); pilot.STEPS[0] = keep; return az, el
def exact_el(m, d, h, mi):                      # unrounded elevation
    t = dt.datetime(2026, m, d, h, mi, tzinfo=pilot.TZ).astimezone(dt.timezone.utc)
    n = (t - dt.datetime(2000, 1, 1, 12, tzinfo=dt.timezone.utc)).total_seconds() / 86400
    L = math.radians((280.46 + 0.9856474 * n) % 360); g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.02) * math.sin(2 * g); eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam)); dec = math.asin(math.sin(eps) * math.sin(lam))
    ha = math.radians(((18.697374558 + 24.06570982441908 * n) % 24 * 15 + pilot.LON) % 360) - ra; lat = math.radians(pilot.LAT)
    return math.degrees(math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha)))
def time_for(m, d, target, evening):
    best = None
    for minute in (range(12 * 60, 24 * 60) if evening else range(0, 12 * 60)):
        e = exact_el(m, d, minute // 60, minute % 60)
        if best is None or abs(e - target) < abs(best[1] - target): best = (minute, e)
    return f'{best[0] // 60:02d}:{best[0] % 60:02d}', round(best[1], 1)
if __name__ == '__main__':
    print('current schedule')
    for s in pilot.STEPS:
        e = exact_el(*s[3]); print(f'  {s[0]:2d} {s[2]:15s} {s[3][0]:02d}-{s[3][1]:02d} {s[3][2]:02d}:{s[3][3]:02d}  sun {e:6.1f} deg  log10 lux {loglux(e):5.1f}')
    a, b = loglux(exact_el(10, 28, 17, 45)), -3.0; c = loglux(exact_el(4, 15, 7, 45))
    print('even steps in log illuminance: fall golden hour -> night -> spring golden morning')
    for k, (m, d), evening, L in ((4, (11, 18), True, a + (b - a) / 3), (5, (12, 10), True, a + 2 * (b - a) / 3), (7, (2, 20), False, b + (c - b) / 3), (8, (3, 20), False, b + 2 * (c - b) / 3)):
        el = elev_for(L); print(f'  step {k}: log10 lux {L:5.2f} -> sun {el:5.1f} deg -> {m:02d}-{d:02d} at', time_for(m, d, el, evening))
    print('  step 6 night: sun below -18 deg from', time_for(1, 15, -18, True))
