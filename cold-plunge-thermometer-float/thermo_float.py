#!/usr/bin/env python3
"""Cold plunge thermometer float: a hollow ring float that holds a stick or tube thermometer upright in the water.

The float is a sealed hollow ring (an air chamber with a 45 degree roof, so it prints without supports inside).
A slotted collar grips the thermometer; a small eye takes a cord to tie it to the edge of the tub.
The script computes whether it floats and how deep, from the mesh it writes.
Run:  python3 thermo_float.py            (writes stl/ and 3mf/ for the diameters in FILES, prints the buoyancy check)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, printcheck  # noqa: E402
from dvx_cad import poly as _poly  # noqa: E402

# ---------------- parameters (mm, g) ----------------
THERMO_D = 25.0       # diameter of the thermometer where the float holds it
FILES = [16.0, 25.0, 35.0]   # diameters written by default
FLOAT_D = 110.0       # float diameter
FLOAT_H = 40.0        # float height
CELLS = 3             # number of ring-shaped air chambers
WALL = 2.0            # every wall of the air chamber (print with 5 perimeters of 0.4 mm = solid)
COLLAR_H = 16.0       # height of the slotted collar above the float
FINGERS = 6           # slots in the collar
FINGER_T = 1.6        # collar wall (thin on purpose, so the fingers flex)
GRIP = 0.5            # the collar narrows by this much (diameter) toward the top, to grip
EYE_D = 5.0           # hole for a cord in the eye at the edge (0 = no eye)
# buoyancy check
PETG = 1.27           # g/cm3, solid PETG (the walls print solid; any infill air would only help)
WATER = 1.00          # g/cm3, fresh water (cold water is a little denser, which only helps)
THERMO_G = 60.0       # g, a heavy thermometer for the check (most stick and pool thermometers weigh less)
# ------------------------------------------------------
SEG = 128


def poly(points):
    cs = _poly(points)
    return cs if cs.area() > 0 else _poly(points[::-1])


def parts(d=THERMO_D):
    """Returns (float with its chamber, envelope = the same with the chamber filled)."""
    R = FLOAT_D / 2
    rb = d / 2 + 0.3                                   # bore radius
    rh = rb + WALL                                     # hub outer radius = inner wall of the chamber
    c = 4.0                                            # 45 degree chamfer at the bottom outside edge
    top_r = 6.0
    pts = [(rb, 0), (R - c, 0), (R, c)]
    for i in range(9):                                 # rounded top outside edge
        a = math.radians(90 * i / 8)
        pts.append((R - top_r + top_r * math.cos(a), FLOAT_H - top_r + top_r * math.sin(a)))
    pts += [(rb, FLOAT_H)]
    env = poly(pts).revolve(SEG)
    # air chambers: CELLS rings side by side, walls WALL thick. Each has a 45 degree gable roof, so nothing
    # inside needs support; several narrow rings waste less plastic under the roofs than one wide one.
    inset = poly(pts).offset(-WALL)
    r1, r2 = rh, R - WALL
    w = (r2 - r1 - (CELLS - 1) * WALL) / CELLS
    cells = None
    for k in range(CELLS):
        a = r1 + k * (w + WALL)
        zr = FLOAT_H - WALL - w / 2 - 0.3
        assert zr > WALL + 3, "float too flat for its chambers: raise FLOAT_H or CELLS"
        cell = poly([(a, WALL), (a + w, WALL), (a + w, zr), (a + w / 2, zr + w / 2), (a, zr)]) ^ inset
        cells = cell if cells is None else cells + cell
    chamber = cells.revolve(SEG)
    body = env - chamber
    # slotted collar on top
    rc_out = rb + FINGER_T
    collar = Manifold.cylinder(COLLAR_H + 0.01, rc_out, rc_out, SEG).translate((0, 0, FLOAT_H - 0.01))
    grip = poly([(0, -1), (rb, -1), (rb, FLOAT_H), (rb - GRIP / 2, FLOAT_H + COLLAR_H - 2),
                 (rb + 0.6, FLOAT_H + COLLAR_H + 0.01), (0, FLOAT_H + COLLAR_H + 1)]).revolve(SEG)
    lip = poly([(rc_out - 0.01, FLOAT_H + COLLAR_H - 4.8), (rc_out + 1.2, FLOAT_H + COLLAR_H - 3.3),
                (rc_out + 1.2, FLOAT_H + COLLAR_H), (rc_out - 0.01, FLOAT_H + COLLAR_H)]).revolve(SEG)   # holds a rubber band
    collar = collar + lip
    for k in range(FINGERS):
        slot = Manifold.cube((rc_out + 3, 1.6, COLLAR_H - 3)).translate((0, -0.8, FLOAT_H + 3))
        collar -= slot.rotate((0, 0, 360 * k / FINGERS + 30))
    body = body + collar - grip                       # the bore runs through, and narrows in the collar to grip
    env -= grip
    if EYE_D > 0:
        eye = (Manifold.cylinder(5, EYE_D / 2 + 3.5, EYE_D / 2 + 3.5, 48).translate((R + EYE_D / 2 + 1, 0, 0))
               + Manifold.cube((10, EYE_D + 7, 5)).translate((R - 8, -(EYE_D + 7) / 2, 0)))
        eye -= Manifold.cylinder(7, EYE_D / 2, EYE_D / 2, 48).translate((R + EYE_D / 2 + 1, 0, -1))
        eye -= env
        body += eye
        env += eye
    return body, env


def buoyancy(body, env, thermo_g=THERMO_G):
    """Mass, lift and waterline, from the mesh volumes."""
    plastic = body.volume() / 1000                     # cm3 of PETG (the chamber is not counted)
    mass = plastic * PETG
    full = env.volume() / 1000                         # cm3 the float displaces when pushed fully under
    load = mass + thermo_g
    lo, hi = 0.0, FLOAT_H
    for _ in range(40):                                # waterline by bisection on the submerged envelope volume
        z = (lo + hi) / 2
        sub = (env ^ Manifold.cube((400, 400, z)).translate((-200, -200, 0))).volume() / 1000 * WATER
        lo, hi = (z, hi) if sub < load else (lo, z)
    return plastic, mass, full * WATER, load, (lo + hi) / 2


if __name__ == "__main__":
    for d in FILES:
        name = f"thermometer-float-{d:g}mm"
        body, env = parts(d)
        tm = export(body, HERE, name)
        ok = printcheck(name, tm)
        comps = sorted(c.volume() for c in body.decompose())
        print(f"{'':34s} one solid part with {len(comps) - 1} sealed air chambers inside "
              f"(trimesh counts {tm.body_count} surfaces; the chambers are the {len(comps) - 1} inner ones)")
        plastic, mass, lift, load, zw = buoyancy(body, env)
        print(f"{'':34s} PETG {plastic:.1f} cm3 = {mass:.0f} g; fully under it would displace {lift:.0f} g of water")
        print(f"{'':34s} with a {THERMO_G:.0f} g thermometer: load {load:.0f} g -> floats, waterline {zw:.1f} mm "
              f"of {FLOAT_H:.0f} mm ({zw / FLOAT_H * 100:.0f}%), spare lift {lift - load:.0f} g")
        _, _, _, load0, zw0 = buoyancy(body, env, 0.0)
        worst = -comps[0] / 1000 * WATER                # the largest chamber, flooded
        print(f"{'':34s} empty: waterline {zw0:.1f} mm. If the largest chamber leaked full of water, lift would drop "
              f"to {lift - worst:.0f} g: {'still floats' if lift - worst > load else 'SINKS'} with the {THERMO_G:.0f} g thermometer. "
              f"If all chambers flooded it would sink (solid PETG is {PETG} g/cm3).")
