#!/usr/bin/env python3
"""Sauna hat drying stand - two flat arch ribs that cross slot-in-slot, plus a base ring.

Every part prints flat on a 220 x 220 mm bed with no supports.
Run:  python3 stand.py        (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import JoinType  # noqa: E402
from dvx_cad import circle, export, poly, rect, report, rounded  # noqa: E402

# ---------------- parameters (mm) ----------------
HAT_CIRCUMFERENCE = 610   # about 24 in; inner diameter is about 194 mm
WIDTH = 170               # rib width - kept smaller than the hat so the felt hangs loose
HEIGHT = 198              # rib height above the base
LEG_HEIGHT = 50           # straight part of the legs before the dome starts
DOME_POWER = 2.0          # 2 = ellipse, higher = boxier shoulders
BAND = 16                 # width of the arch band
CROWN = 50                # solid depth at the top where the two ribs cross
THICK = 5                 # rib thickness (print height)
CLEAR = 0.3               # total clearance added to every slot
TAB_W = 12                # foot tab width
BASE_T = 6                # base ring thickness = tab length
BASE_BAND = 34            # base ring width
VENT_R = 0                # optional vent holes in the crown (radius, 0 = none)
# -------------------------------------------------

assert WIDTH <= 0.92 * HAT_CIRCUMFERENCE / math.pi, "rib is too wide for the hat"
assert max(WIDTH, HEIGHT + BASE_T) <= 208, "rib does not fit a 210 mm deep bed"

LEG_X = WIDTH / 2 - BAND / 2          # center of each leg
SLOT = THICK + CLEAR


def outline(y_bottom=0.0):
    pts = [(WIDTH / 2, y_bottom)]
    n = 120
    for i in range(n + 1):
        t = math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = WIDTH / 2 * math.copysign(abs(c) ** (2 / DOME_POWER), c)
        y = LEG_HEIGHT + (HEIGHT - LEG_HEIGHT) * abs(s) ** (2 / DOME_POWER)
        pts.append((x, y))
    pts.append((-WIDTH / 2, y_bottom))
    return poly(pts)


def rib(kind):
    """kind 'A' has its crown slot open downward, 'B' open upward."""
    outer = outline()
    # opening between the legs: the outline moved in by BAND, capped below the crown
    inner = outline(-60).offset(-BAND, JoinType.Round) ^ rect(-WIDTH, -40, WIDTH, HEIGHT - CROWN)
    inner = rounded(inner, 10)
    shape = outer - inner
    # foot tabs with a small lead-in taper
    for sx in (-1, 1):
        cx = sx * LEG_X
        shape += poly([(cx - TAB_W / 2, 0.01), (cx - TAB_W / 2, -BASE_T + 1.2), (cx - TAB_W / 2 + 1.2, -BASE_T),
                       (cx + TAB_W / 2 - 1.2, -BASE_T), (cx + TAB_W / 2, -BASE_T + 1.2), (cx + TAB_W / 2, 0.01)])
    mid = HEIGHT - CROWN / 2
    if kind == "A":
        shape -= rect(-SLOT / 2, HEIGHT - CROWN - 5, SLOT / 2, mid + CLEAR / 2)
    else:
        shape -= rect(-SLOT / 2, mid - CLEAR / 2, SLOT / 2, HEIGHT + 5)
    if VENT_R:
        for sx in (-1, 1):
            shape -= circle(VENT_R, sx * 26, HEIGHT - CROWN + 18)
    return shape.extrude(THICK)


def base():
    r_out = WIDTH / 2 + 8
    ring = circle(r_out) - circle(r_out - BASE_BAND)
    for a in range(4):
        slot = rect(LEG_X - (TAB_W + CLEAR) / 2, -SLOT / 2, LEG_X + (TAB_W + CLEAR) / 2, SLOT / 2)
        ring -= slot.rotate(90 * a)
    return ring.extrude(BASE_T)


def assembled():
    """Parts in their assembled position (for previews only)."""
    a = rib("A").translate((0, 0, -THICK / 2)).rotate((90, 0, 0)).translate((0, 0, BASE_T))
    b = rib("B").translate((0, 0, -THICK / 2)).rotate((90, 0, 90)).translate((0, 0, BASE_T))
    return a, b, base()


if __name__ == "__main__":
    parts = {"hat-stand-rib-A": rib("A"), "hat-stand-rib-B": rib("B"), "hat-stand-base-ring": base()}
    for name, man in parts.items():
        report(name, export(man, HERE, name))
    a, b, c = assembled()
    print("assembled overlap volume A&B: %.3f mm3, A&base: %.3f, B&base: %.3f"
          % ((a ^ b).volume(), (a ^ c).volume(), (b ^ c).volume()))
