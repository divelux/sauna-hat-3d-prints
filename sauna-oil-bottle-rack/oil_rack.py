#!/usr/bin/env python3
"""Wall rack for essential oil bottles - a row of cups on a back plate.

Prints as it hangs on the wall (cups up, floor on the bed), no supports.
Run:  python3 oil_rack.py         (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import circle, clean, export, filleted, printcheck, rect, rounded  # noqa: E402

# ---------------- parameters (mm) ----------------
COUNT = 5             # number of bottles
BOTTLE_D = 30.0       # largest bottle diameter the cups take (10 ml bottles are about 25, 15 ml about 28-29)
CLEAR = 1.0           # each cup is this much wider than BOTTLE_D
WALL = 2.4            # wall between and around the cups
FLOOR = 3.0           # cup floor thickness
CUP_H = 18.0          # cup depth
PLATE_T = 4.0         # back plate thickness
PLATE_H = 46.0        # back plate height, measured from the bottom of the rack
SCREW_D = 4.6         # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0          # countersink diameter
# -------------------------------------------------


def oil_rack(count=COUNT, bottle_d=BOTTLE_D):
    """x = left/right, y = out from the wall (wall at y = 0), z = up. Printed in this orientation."""
    bore = bottle_d + CLEAR
    pitch = bore + WALL
    r_out = bore / 2 + WALL
    cy = PLATE_T + bore / 2 + 1.2             # the cups stand just clear of the back plate
    xs = [(i - (count - 1) / 2) * pitch for i in range(count)]
    half_w = xs[-1] + r_out
    top = FLOOR + CUP_H
    assert PLATE_H >= top + 18, "back plate too low for the screws"

    # top view: scalloped front, straight back
    outline = rect(-half_w, 0, half_w, cy)
    for x in xs:
        outline += circle(r_out, x, cy)
    outline = clean(filleted(outline, 3.0))
    body = outline.extrude(PLATE_H)
    # keep the back plate full height, cut everything in front of it down to the cup height
    body -= Manifold.cube((2 * half_w + 2, 2 * r_out + cy, PLATE_H)).translate((-half_w - 1, PLATE_T, top))
    # round the two top corners of the back plate
    rad = 8.0
    corners = rect(-half_w - 1, PLATE_H - rad, half_w + 1, PLATE_H + 1) - rounded(rect(-half_w, -30, half_w, PLATE_H), rad)
    body -= corners.extrude(PLATE_T + 2).rotate((90, 0, 0)).translate((0, PLATE_T + 1, 0))
    for x in xs:
        body -= Manifold.cylinder(CUP_H + 1, bore / 2, bore / 2, 96).translate((x, cy, FLOOR))
        body -= Manifold.cylinder(1.0, bore / 2, bore / 2 + 1.0, 96).translate((x, cy, top - 0.8))   # lead-in chamfer
    sink_h = (HEAD_D - SCREW_D) / 2
    for x in ((xs[0] + xs[1]) / 2, (xs[-1] + xs[-2]) / 2):
        hole = Manifold.cylinder(PLATE_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((0, 0, -1))
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, PLATE_T - sink_h))
        body -= (hole + sink).rotate((-90, 0, 0)).translate((x, 0, (top + PLATE_H) / 2))
    return body


if __name__ == "__main__":
    for count, dia in ((4, 30), (5, 30), (6, 26)):
        name = f"oil-rack-{count}x{dia}mm"
        # the two short horizontal screw holes bridge without supports; nothing else overhangs
        printcheck(name, export(oil_rack(count, dia), HERE, name), max_overhang_mm2=60)
