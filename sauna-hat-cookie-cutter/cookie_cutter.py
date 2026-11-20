#!/usr/bin/env python3
"""Sauna hat cookie cutter - a bell-shaped sauna hat with its hanging loop, about 75 x 81 mm.

Two versions: a plain outline cutter, and one with a back plate that also presses the brim line and the loop
into the dough. Both print flange-down, cutting edge up, no supports.
Run:  python3 cookie_cutter.py    (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import JoinType  # noqa: E402
from dvx_cad import arc, circle, clean, export, filleted, printcheck, rect, rounded, stroke  # noqa: E402
from dvx_text import bell_hat  # noqa: E402

# ---------------- parameters (mm) ----------------
HAT_W, HAT_H = 76.0, 70.0   # the hat itself (the loop adds a little height)
LOOP_W, LOOP_H = 13.0, 11.0  # the hanging loop on top: a short, wide tab, so the dough does not tear
HEIGHT = 14.0               # total height of the cutter
WALL = 2.0                  # wall thickness
EDGE = 0.8                  # thickness at the cutting edge
EDGE_H = 3.0                # the wall thins down to EDGE over this height
FLANGE = 5.0                # width of the rim you press on
FLANGE_T = 2.4              # thickness of the rim
PLATE_T = 1.6               # back plate of the imprint version
IMPRINT_DEPTH = 2.0         # how deep the lines press into dough rolled 5.5 mm (about 1/4 in) thick
DOUGH = 5.5
RIDGE = 2.0                 # imprint ridge thickness at its base (thins to 1.0 at the tip)
PUSH_D = 16.0               # holes in the back plate for pushing the dough out
# -------------------------------------------------


def outline():
    """The cookie: hat silhouette plus the loop, with all corners softened."""
    tab = rounded(rect(-LOOP_W / 2, HAT_H - 6, LOOP_W / 2, HAT_H + LOOP_H), LOOP_W / 2 - 0.5)
    return clean(rounded(filleted(bell_hat(HAT_W, HAT_H) + tab, 4.0), 2.0)).simplify(0.01)


def _grow(shape, by):
    """Offset outward with round corners, without the hairline segments an offset can leave behind."""
    return shape.offset(by, JoinType.Round).simplify(0.01)


def _walls(shape, plate=False):
    """Stack of nested solids: flange, wall, and a wall that steps down to the cutting edge."""
    body = _grow(shape, FLANGE).extrude(FLANGE_T)
    steps = 4
    body += _grow(shape, WALL).extrude(HEIGHT - EDGE_H)
    for i in range(1, steps + 1):
        w = WALL - (WALL - EDGE) * i / steps
        body += _grow(shape, w).extrude(HEIGHT - EDGE_H + EDGE_H * i / steps)
    z0 = PLATE_T if plate else -1.0
    return body - shape.extrude(HEIGHT + 2).translate((0, 0, z0))


def cutter_plain():
    return _walls(outline())


def cutter_imprint():
    shape = outline()
    body = _walls(shape, plate=True)
    # lines pressed into the cookie: the brim band and the base of the loop
    brim = stroke(arc(0, 9.0 + 170.0, 170.0, 270 - 14.5, 270 + 14.5, 24), 0.5)      # brim band, curving up at the ends
    eye = stroke(arc(0, HAT_H + LOOP_H - LOOP_W / 2, LOOP_W / 2 - 3.4, 0, 360, 24)
                 + [(LOOP_W / 2 - 3.4, HAT_H + LOOP_H - LOOP_W / 2)], 0.5)             # the opening of the loop
    lines = brim + eye
    top = HEIGHT - (DOUGH - IMPRINT_DEPTH)
    inside = _grow(shape, 0.5)
    ridge = (_grow(lines, RIDGE / 2 - 0.5) ^ inside).extrude(top - 2.0)
    ridge += (_grow(lines, 0.25) ^ inside).extrude(top - 1.0)
    ridge += (lines ^ inside).extrude(top)
    body += ridge
    for x, y in ((0, 40.0), (-16, 27.0), (16, 27.0)):
        body -= circle(PUSH_D / 2, x, y).extrude(PLATE_T + 2).translate((0, 0, -1))
    return body


if __name__ == "__main__":
    o = outline().bounds()
    print("cookie size: %.1f x %.1f mm" % (o[2] - o[0], o[3] - o[1]))
    for name, man in {"hat-cookie-cutter-plain": cutter_plain(), "hat-cookie-cutter-imprint": cutter_imprint()}.items():
        printcheck(name, export(man, HERE, name))
