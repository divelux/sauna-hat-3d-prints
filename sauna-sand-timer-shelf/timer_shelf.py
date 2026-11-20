#!/usr/bin/env python3
"""Sand timer wall shelf - a small cup-shaped shelf for a free-standing cylindrical sand timer (hourglass).

Lift the timer out, turn it over, set it back. Prints as it hangs on the wall (floor on the bed), no supports.
Run:  python3 timer_shelf.py        (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import CrossSection, Manifold  # noqa: E402
from dvx_cad import circle, export, poly, printcheck, rect, rounded  # noqa: E402

# ---------------- parameters (mm) ----------------
TIMER_D = 50          # diameter of the end caps of your sand timer (the released files: 40, 50, 60)
CLEAR = 1.5           # the cup is this much wider than the timer
WALL = 3.0            # cup and side wall thickness
FLOOR = 4.0           # shelf floor thickness
RIM = 14.0            # height of the cup rim above the floor
FRONT_OPEN = 0.42     # width of the front opening as a share of TIMER_D (0 = closed rim)
DRAIN_D = 12.0        # hole in the floor: no water or dust collects in the cup (0 = none)
PLATE_T = 5.0         # back plate thickness
PLATE_H = 78.0        # back plate height
ARM_H = 46.0          # height of the side walls where they meet the back plate
SCREW_D = 4.6         # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0          # countersink diameter
SCREW_Z = (32.0, 64.0)  # screw heights above the bottom of the shelf
# -------------------------------------------------


def _along_x(profile_yz, x0, x1):
    """Extrude a 2D profile drawn as (y, z) along the x axis from x0 to x1."""
    return profile_yz.extrude(x1 - x0).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((x0, 0, 0))


def timer_shelf(timer_d=TIMER_D):
    """x = left/right, y = out from the wall (wall at y = 0), z = up. Printed in this orientation."""
    r_in = (timer_d + CLEAR) / 2
    r_out = r_in + WALL
    cy = PLATE_T + r_in                      # center of the cup; the back plate is the back of the cup
    front = cy + r_out
    assert PLATE_H >= ARM_H + 14 and ARM_H > FLOOR + RIM

    outer = CrossSection.batch_hull([circle(r_out, 0, cy), rect(-r_out, 0, r_out, cy)])
    pocket = CrossSection.batch_hull([circle(r_in, 0, cy), rect(-r_in, PLATE_T, r_in, cy)])

    # one solid block with the cup hollowed out, then trimmed by a side profile that sweeps down
    # from the back plate to the rim of the cup
    body = outer.extrude(PLATE_H) - pocket.extrude(PLATE_H).translate((0, 0, FLOOR))
    low, n = FLOOR + RIM, 24
    side = [(-1, -1), (front + 1, -1), (front + 1, low)]
    for i in range(n + 1):
        u = i / n                            # 0 at the cup center, 1 at the back plate
        y = cy - u * (cy - PLATE_T)
        side.append((y, low + (ARM_H - low) * u ** 2.2))
    side += [(PLATE_T, PLATE_H + 1), (-1, PLATE_H + 1)]
    body ^= _along_x(poly(side), -r_out - 1, r_out + 1)
    # round the top corners of the back plate
    rad = min(12.0, r_out - 6, PLATE_H - ARM_H - 2)
    corners = rect(-r_out - 1, PLATE_H - rad, r_out + 1, PLATE_H + 1) - rounded(rect(-r_out, -30, r_out, PLATE_H), rad)
    body -= corners.extrude(PLATE_T + 2).rotate((90, 0, 0)).translate((0, PLATE_T + 1, 0))

    if FRONT_OPEN > 0:
        w = FRONT_OPEN * timer_d / 2
        body -= rounded(rect(-w, cy, w, front + 5), 2.0).extrude(PLATE_H).translate((0, 0, FLOOR))
    if DRAIN_D > 0:
        body -= Manifold.cylinder(FLOOR + 2, DRAIN_D / 2, DRAIN_D / 2, 64).translate((0, cy, -1))
    for z in SCREW_Z:
        sink_h = (HEAD_D - SCREW_D) / 2
        hole = Manifold.cylinder(PLATE_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((0, 0, -1))
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, PLATE_T - sink_h))
        body -= (hole + sink).rotate((-90, 0, 0)).translate((0, 0, z))     # axis now points out from the wall
    return body


def _box(x0, y0, x1, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


if __name__ == "__main__":
    for d in (40, 50, 60):
        name = f"sand-timer-shelf-{d}mm"
        # the two short horizontal screw holes bridge without supports; nothing else overhangs
        printcheck(name, export(timer_shelf(d), HERE, name), max_overhang_mm2=60)
