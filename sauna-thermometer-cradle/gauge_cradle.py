#!/usr/bin/env python3
"""Wall cradle for a round sauna thermometer or hygrometer.

The gauge drops in from above and rests in a half-round cradle; a lip around the lower rim keeps it from
sliding out. The back is an open ring, so the back of the gauge is not pressed against the wall.
Prints back-down, no supports.  Run:  python3 gauge_cradle.py   (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import circle, export, poly, printcheck, rect  # noqa: E402

# ---------------- parameters (mm) ----------------
GAUGE_D = 100         # largest diameter of the gauge, bezel included (the released files: 100, 120, 130)
GAUGE_DEPTH = 30      # the gauge may be this deep or shallower (back of the case to the front of the bezel)
CLEAR = 1.0           # the cradle is this much wider than the gauge
WALL = 3.0            # cradle wall thickness
BACK_T = 4.0          # back ring thickness
BACK_BAND = 17.0      # back ring width
LIP = 4.0             # how far the lip reaches in over the front of the gauge
LIP_ANGLE = 50.0      # slope of the underside of the lip, degrees from the bed (45 or more prints clean)
LIP_ARC = 150.0       # how much of the circle the lip covers, centered on the bottom
SWEEP = 0.55          # the wall sweeps down toward its two ends over this share of the radius (0 = square ends)
END_H = 9.0           # wall height above the back ring at its two ends
DRAIN_W = 8.0         # gap at the very bottom so condensation can run out (0 = none)
SCREW_D = 4.6         # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0          # countersink diameter
# -------------------------------------------------


def gauge_cradle(gauge_d=GAUGE_D, depth=GAUGE_DEPTH):
    """Print orientation: back ring on the bed. On the wall: +y is up, +z points into the room."""
    r_in = (gauge_d + CLEAR) / 2
    r_out = r_in + WALL
    r_hide = r_in - 1.5                       # the upper half of the back ring stays hidden behind the gauge
    z_lip = BACK_T + depth
    z_top = z_lip + LIP * math.tan(math.radians(LIP_ANGLE)) + 1.2

    # back: an open ring; its lower half reaches into the cradle wall
    ring = circle(r_hide) + (circle(r_in + WALL / 2) ^ rect(-r_out, -r_out, r_out, 0))
    back = (ring - circle(r_hide - BACK_BAND)).extrude(BACK_T)

    # cradle wall around the lower half
    wall = poly([(r_in, 0), (r_out, 0), (r_out, z_top - 1), (r_out - 1, z_top), (r_in, z_top)]).revolve(96, 180).rotate((0, 0, 180))
    # lip: a ledge that leans in over the front of the gauge, self-supporting when printed
    lip = poly([(r_in + WALL / 2, z_top), (r_in - LIP, z_top), (r_in - LIP, z_top - 1.2), (r_in, z_lip),
                (r_in + WALL / 2, z_lip - 1)]).revolve(96, LIP_ARC).rotate((0, 0, 270 - LIP_ARC / 2))
    body = back + wall + lip
    if SWEEP > 0:
        # trim the top of the wall with a profile drawn as (y, z): full height at the bottom of the cradle,
        # an elliptical sweep down to END_H at the two ends
        y1, z_end, n = -SWEEP * r_out, BACK_T + END_H, 24
        prof = [(-r_out - 1, -1), (r_out + 1, -1), (r_out + 1, z_end), (0, z_end)]
        prof += [(y1 * math.sin(math.pi / 2 * i / n), z_end + (z_top - z_end) * (1 - math.cos(math.pi / 2 * i / n)))
                 for i in range(1, n + 1)]
        prof += [(y1, z_top + 1), (-r_out - 1, z_top + 1)]
        body ^= poly(prof).extrude(2 * r_out + 2).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((-r_out - 1, 0, 0))
    if DRAIN_W > 0:
        body -= Manifold.cube((DRAIN_W, WALL + LIP + 6, z_top)).translate((-DRAIN_W / 2, -r_out - 1, BACK_T))

    r_screw = r_hide - BACK_BAND / 2
    sink_h = (HEAD_D - SCREW_D) / 2
    for a in (90, 210, 330):
        hole = Manifold.cylinder(BACK_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((0, 0, -1))
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, BACK_T - sink_h))
        body -= (hole + sink).translate((r_screw * math.cos(math.radians(a)), r_screw * math.sin(math.radians(a)), 0))
    return body


if __name__ == "__main__":
    for d in (100, 120, 130):
        name = f"gauge-cradle-{d}mm"
        printcheck(name, export(gauge_cradle(d), HERE, name))
