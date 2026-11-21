#!/usr/bin/env python3
"""Measuring scoop with volume lines (ml), for learning and portioning the water you throw on the stones.

The lines inside are placed by computing the volume of the printed cavity, not by guessing.
Prints upright, cup on the bed, handle rising at 55 degrees, no supports.
NOT for the hot room and NOT for hot water: see LISTING.md.
Run:  python3 scoop.py         (writes stl/ and 3mf/ next to this file and prints the volume check)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import CrossSection, Manifold  # noqa: E402
from dvx_cad import export, printcheck, rect, rounded  # noqa: E402
from dvx_cad import poly as _poly  # noqa: E402
from dvx_text import text  # noqa: E402

# ---------------- parameters (mm, ml) ----------------
MARKS = [50, 100, 150]    # volume lines, ml (1 ml = 1000 mm3)
INNER_D = 64.0            # inside diameter of the cup
FILLET = 8.0              # rounded inside bottom edge (easy to clean)
WALL = 2.4                # side wall
FLOOR = 3.0               # bottom
FREEBOARD = 12.0          # rim this far above the top line
HANDLE_L = 135.0          # handle length along its slope
HANDLE_ANGLE = 55.0       # handle slope from the table, degrees (45 or more prints without supports)
HANDLE_W = 16.0           # handle width
HANDLE_T = 7.0            # handle thickness
HOLE_D = 6.0              # hanging hole near the end of the handle (0 = none)
LINE_D = 0.8              # depth of the volume lines (grooves), inside and outside
DIGIT_H = 7.0             # height of the numbers on the outside
DIGIT_UP = 0.8            # numbers stand this far out from the wall
# -----------------------------------------------------
RI = INNER_D / 2
RO = RI + WALL
SEG = 128


def poly(points):
    """2D polygon, either winding."""
    cs = _poly(points)
    return cs if cs.area() > 0 else _poly(points[::-1])


def cavity(top):
    """The inside of the cup from the inner floor up to height `top` (a solid of revolution)."""
    f = FILLET
    pts = [(0, FLOOR)]
    for i in range(17):
        a = math.radians(-90 + 90 * i / 16)
        pts.append((RI - f + f * math.cos(a), FLOOR + f + f * math.sin(a)))
    pts += [(RI, top), (0, top)]
    return poly(pts).revolve(SEG)


def level_for(ml, solid=None):
    """Height of the water surface for `ml`, by bisection on the volume of the cavity
    (or, if a finished cup is given, on the volume enclosed by its mesh)."""
    lo, hi = FLOOR, FLOOR + 400
    for _ in range(50):
        mid = (lo + hi) / 2
        v = water(mid, solid)
        lo, hi = (mid, hi) if v < ml * 1000 else (lo, mid)
    return (lo + hi) / 2


def water(z, solid=None):
    """Volume (mm3) of water standing up to height z: from the plain cavity, or from the finished mesh."""
    if solid is None:
        return cavity(z).volume() if z > FLOOR else 0.0
    probe = Manifold.cylinder(z, RI + 0.2, RI + 0.2, SEG)          # everything inside the bore up to z ...
    return (probe - solid).volume()                                # ... that is not plastic


LEVELS = [level_for(m) for m in MARKS]
H = LEVELS[-1] + FREEBOARD


def _groove(z, r, inside):
    """A V-groove ring at height z on a wall of radius r. The upper face is steep (60 degrees), so it prints."""
    d = LINE_D
    up = d * math.tan(math.radians(60))
    if inside:
        prof = poly([(r - 0.01, z - 0.15), (r + d, z), (r + d, z + 0.15), (r - 0.01, z + 0.15 + up)])
    else:
        prof = poly([(r + 0.01, z - 0.15), (r - d, z), (r - d, z + 0.15), (r + 0.01, z + 0.15 + up)])
    return prof.revolve(SEG)


def scoop():
    """x = handle direction (handle on -x), z = up. Printed in this orientation."""
    body = Manifold.cylinder(H, RO, RO, SEG) - cavity(H + 1)
    for z in LEVELS:
        body -= _groove(z, RI, True)
        body -= _groove(z, RO, False)
    # numbers on the outside, opposite the handle, just above each line, wrapped around the wall
    for ml, z in zip(MARKS, LEVELS):
        label = f"{ml} ml" if ml == MARKS[-1] else f"{ml}"
        t = text(label, DIGIT_H).translate((0, 1.8))
        num = t.extrude(DIGIT_UP + 1.0).translate((0, 0, -1.0))         # x = along the wall, y = up, z = out
        num = num.warp(lambda v, z0=z: ((RO + v[2]) * math.cos(v[0] / RO), (RO + v[2]) * math.sin(v[0] / RO), z0 + v[1]))
        body += num
    # handle: a slab rising from the rim at HANDLE_ANGLE, rounded end, optional hanging hole
    a = math.radians(HANDLE_ANGLE)
    ux, uz = -math.cos(a), math.sin(a)
    start = 14.0                                  # the slab starts inside the cup, where the bore cuts it away
    x0, z0 = -RO + start, H - 2.0 - start * math.tan(a)
    slab = rounded(rect(0, -HANDLE_W / 2, start / math.cos(a) + HANDLE_L, HANDLE_W / 2), HANDLE_W / 2 - 0.5).extrude(HANDLE_T).translate((0, 0, -HANDLE_T / 2))
    # slab is drawn along +x; tilt it up by the handle angle and point it away from the cup
    slab = slab.rotate((0, -HANDLE_ANGLE, 0)).rotate((0, 0, 180)).translate((x0, 0, z0))
    body += slab - Manifold.cylinder(H + 1, RI + 0.5, RI + 0.5, SEG)
    if HOLE_D > 0:
        hx = x0 + ux * (start / math.cos(a) + HANDLE_L - HANDLE_W / 2)
        hz = z0 + uz * (start / math.cos(a) + HANDLE_L - HANDLE_W / 2)
        body -= Manifold.cylinder(80, HOLE_D / 2, HOLE_D / 2, 48).translate((hx, 0, hz - 40))
    return body


if __name__ == "__main__":
    s = scoop()
    tm = export(s, HERE, "measuring-scoop")
    # the only parts facing down more than 45 degrees are the undersides of the 0.8 mm raised numbers
    printcheck("measuring-scoop", tm, max_overhang_mm2=60)
    # re-read the exported STL and measure the water it holds, so the check covers the file itself
    import numpy as np
    from manifold3d import Mesh
    s = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))
    print("volume check on the exported STL (water standing inside the printed cup):")
    for ml, z in zip(MARKS, LEVELS):
        print(f"  {ml:4d} ml line at {z - FLOOR:5.1f} mm above the inside floor ({z:5.1f} mm from the bed): "
              f"mesh holds {water(z, s) / 1000:6.1f} ml")
    print(f"  full to the rim: {water(H, s) / 1000:.0f} ml")
