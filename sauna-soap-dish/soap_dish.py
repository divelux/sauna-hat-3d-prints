#!/usr/bin/env python3
"""Soap dish with a drain: ribs keep the bar out of the water, the floor slopes to a spout at the front.

One part, prints as it stands, no supports.
Run:  python3 soap_dish.py        (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, poly, printcheck, rect, rounded  # noqa: E402

# ---------------- parameters (mm) ----------------
LENGTH = 124.0        # outside, left to right
WIDTH = 88.0          # outside, front to back
HEIGHT = 22.0         # wall height
CORNER = 22.0         # corner radius (outside)
WALL = 2.4            # wall thickness
FLOOR_BACK = 5.6      # floor thickness at the back wall
FLOOR_FRONT = 3.0     # floor thickness at the spout (the floor slopes toward it)
RIBS = 6              # number of ribs the soap rests on
RIB_W = 3.2           # rib width
RIB_TOP = 11.0        # height of the rib tops above the bed (level, so the soap sits flat)
SPOUT_W = 30.0        # width of the drain opening in the front wall
SPOUT_L = 12.0        # the spout sticks out this far in front of the wall
SLOTS = False         # True = also cut drain slots through the floor (for a dish that stands over a drain)
# -------------------------------------------------


def _along(profile, length, axis):
    """Extrude a 2D profile drawn as (u, z) symmetrically along x ('x') or y ('y')."""
    m = profile.extrude(length).translate((0, 0, -length / 2)).rotate((90, 0, 0))   # profile (u, z) -> (x, z), along y
    return m.rotate((0, 0, 90)) if axis == "x" else m


def soap_dish():
    """x = left to right, y = front (-) to back (+), z = up. Printed in this orientation."""
    hl, hw = LENGTH / 2, WIDTH / 2
    outer = rounded(rect(-hl, -hw, hl, hw), CORNER)
    inner = outer.offset(-WALL)
    il, iw = hl - WALL, hw - WALL
    body = outer.extrude(HEIGHT) - inner.extrude(HEIGHT + 1).translate((0, 0, FLOOR_FRONT))
    # sloped floor: thicker at the back, down to FLOOR_FRONT at the front wall
    wedge = poly([(-iw - 1, FLOOR_FRONT - 0.01), (iw + 1, FLOOR_FRONT - 0.01), (iw + 1, FLOOR_BACK), (-iw - 1, FLOOR_FRONT)])
    body += _along(wedge, 2 * il + 2, "x") ^ inner.extrude(HEIGHT)
    # ribs, running front to back so water runs between them; rounded tops, level
    pitch = (2 * il - 16) / (RIBS - 1)
    rib = rect(-RIB_W / 2, 0, RIB_W / 2, RIB_TOP - RIB_W / 2) + rounded(rect(-RIB_W / 2, RIB_TOP - RIB_W, RIB_W / 2, RIB_TOP), RIB_W / 2 - 0.01)
    rib_len = 2 * iw - 14
    for i in range(RIBS):
        x = -il + 8 + i * pitch
        body += _along(rib, rib_len, "y").translate((x, 3.0, 0))
    # drain: an opening in the front wall down to the floor, and a short spout with a channel
    sw = SPOUT_W / 2
    body -= rounded(rect(-sw, -hw - 1, sw, -iw + 1), 0.5).extrude(HEIGHT).translate((0, 0, FLOOR_FRONT))
    tongue = rounded(rect(-sw - WALL, -hw - SPOUT_L, sw + WALL, -iw + 2), 6.0) ^ rect(-sw - WALL - 1, -hw - SPOUT_L - 1, sw + WALL + 1, -hw + 1)
    body += tongue.extrude(FLOOR_FRONT)
    channel = poly([(-sw + 2, -hw - SPOUT_L - 1), (sw - 2, -hw - SPOUT_L - 1), (sw - 2, -iw + 1), (-sw + 2, -iw + 1)])
    body -= channel.extrude(2).translate((0, 0, FLOOR_FRONT - 1.0))
    if SLOTS:
        for i in range(RIBS - 1):
            x = -il + 8 + (i + 0.5) * pitch
            body -= rounded(rect(x - 2.5, -iw + 12, x + 2.5, iw - 12), 2.4).extrude(20).translate((0, 0, -1))
    return body


if __name__ == "__main__":
    printcheck("soap-dish", export(soap_dish(), HERE, "soap-dish"))
    SLOTS = True
    printcheck("soap-dish-with-slots", export(soap_dish(), HERE, "soap-dish-with-slots"))
