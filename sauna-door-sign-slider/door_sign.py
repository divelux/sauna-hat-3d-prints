#!/usr/bin/env python3
"""Sauna door sign with a slider: FREE / IN USE. Two flat parts, no glue, no supports.

The slider runs in a dovetail track and clicks in past a small catch, so it cannot fall out.
Run:  python3 door_sign.py        (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, poly, printcheck, rect, rounded  # noqa: E402
from dvx_text import bell_hat, text  # noqa: E402

# ---------------- parameters (mm) ----------------
TITLE = "SAUNA"       # header line ("" = no header text)
WORD_LEFT = "FREE"    # shown when the slider is on the right
WORD_RIGHT = "IN USE"  # shown when the slider is on the left
FIELD_W = 74.0        # width of one word field = slider length
FIELD_H = 34.0        # height of the track
HEADER_H = 24.0       # height of the header field
BORDER = 5.0          # frame and rail width
FLOOR = 2.0           # back plate thickness (swap filament at this height for two-color letters)
TEXT_UP = 0.8         # letters stand this high above the floor
RUNNER = 1.0          # the slider rides on two strips this high, clear of the letters
SLIDER_T = 2.7        # slider thickness
LEAN = 30.0           # dovetail angle of the rails, degrees from vertical
CLEAR = 0.25          # gap between the slider and each rail
CATCH = 0.8           # the catch stands this high above the underside of the slider (it flexes over it once)
SCREW_D = 4.2         # two holes for #6 / 3.5 mm pan-head screws (0 = no holes, use mounting tape)
# -------------------------------------------------

RAIL_TOP = FLOOR + RUNNER + SLIDER_T + 0.3          # top of the frame and rails
HH = FIELD_H / 2                                    # half height of the track at the runner level
RIDE = FLOOR + RUNNER                               # height the slider slides at
RAMP = 7.0                                          # length of the catch ramp at the open end
LENGTH = BORDER + 2 * FIELD_W + 1.0 + RAMP
X_L = -LENGTH / 2 + BORDER                          # closed (left) end of the track
X_CATCH = X_L + 2 * FIELD_W + 1.0
Y_BOT = -HH - BORDER
Y_TOP = HH + BORDER + HEADER_H + BORDER
assert RUNNER >= TEXT_UP + 0.2, "letters would rub on the slider"


def _along_x(profile_yz, x0, x1):
    """Extrude a 2D profile drawn as (y, z) along the x axis from x0 to x1."""
    return profile_yz.extrude(x1 - x0).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((x0, 0, 0))


def _rail_y(z):
    """Half width of the track at height z (the rails lean in toward the top)."""
    return HH - math.tan(math.radians(LEAN)) * (z - RIDE)


def base():
    """Printed face-up. x = along the sign, y = up on the door, z = out from the door."""
    block = rounded(rect(-LENGTH / 2, Y_BOT, LENGTH / 2, Y_TOP), 4.0).extrude(RAIL_TOP)
    # dovetail track, open at the right end
    zt = RAIL_TOP + 1
    track = _along_x(poly([(-HH, RIDE), (HH, RIDE), (_rail_y(zt), zt), (-_rail_y(zt), zt)]), X_L, LENGTH / 2 + 1)
    # floor of the track between the two runner strips
    well = rect(X_L, -HH + 3.0, LENGTH / 2 + 1, HH - 3.0).extrude(RUNNER + 1).translate((0, 0, FLOOR))
    # header field
    header = rounded(rect(X_L, HH + BORDER, LENGTH / 2 - BORDER, HH + BORDER + HEADER_H), 2.0)
    body = block - track - well - header.extrude(RAIL_TOP).translate((0, 0, FLOOR))

    def raised(cs, up):
        return cs.extrude(up + 0.5).translate((0, 0, FLOOR - 0.5))

    cap = FIELD_H * 0.42
    for word, cx in ((WORD_LEFT, X_L + FIELD_W / 2), (WORD_RIGHT, X_L + 1.5 * FIELD_W)):
        body += raised(text(word, cap, max_width=FIELD_W - 12).translate((cx, -cap / 2)), TEXT_UP)
    if TITLE:
        hcap = HEADER_H * 0.5
        hx = (X_L + LENGTH / 2 - BORDER) / 2
        body += raised(text(TITLE, hcap, tracking=hcap * 0.22, max_width=LENGTH - 60)
                       .translate((hx, HH + BORDER + HEADER_H / 2 - hcap / 2)), TEXT_UP + 0.4)
    # catch: square face toward the slider, ramp toward the open end
    top = RIDE + CATCH
    ramp = poly([(X_CATCH, FLOOR - 0.5), (X_CATCH + RAMP, FLOOR - 0.5), (X_CATCH + RAMP, FLOOR + 0.2), (X_CATCH + 1.2, top), (X_CATCH, top)])
    body += ramp.extrude(12).rotate((90, 0, 0)).translate((0, 6, 0))
    if SCREW_D > 0:
        for x in (X_L + 9, LENGTH / 2 - BORDER - 9):
            body -= Manifold.cylinder(FLOOR + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((x, HH + BORDER + HEADER_H / 2, -1))
    return body


def slider():
    """Printed flat, wide face down. Slides in from the open right end and clicks past the catch."""
    z0 = 0.05                                        # running gap above the runner strips
    b, t = _rail_y(RIDE + z0) - CLEAR, _rail_y(RIDE + z0 + SLIDER_T) - CLEAR
    body = _along_x(poly([(-b, 0), (b, 0), (t, SLIDER_T), (-t, SLIDER_T)]), 0, FIELD_W)
    cx = FIELD_W / 2
    # grip: a small bell hat and two finger bars, standing above the frame
    hat_h = FIELD_H * 0.5
    grip = bell_hat(hat_h * 1.05, hat_h).translate((cx, -hat_h / 2))
    for dx in (-FIELD_W * 0.3, FIELD_W * 0.3):
        grip += rounded(rect(cx + dx - 1.6, -hat_h / 2, cx + dx + 1.6, hat_h / 2), 1.5)
    return body + grip.extrude(1.8 + 0.5).translate((0, 0, SLIDER_T - 0.5))


def assembled(pos=0.0):
    """Base and slider in place. pos 0 = slider on the left (IN USE shows), 1 = on the right (FREE shows)."""
    travel = X_CATCH - 0.3 - (X_L + 0.3) - FIELD_W
    return base(), slider().translate((X_L + 0.3 + pos * travel, 0, RIDE + 0.05))


if __name__ == "__main__":
    parts = {"door-sign-base": base(), "door-sign-slider": slider()}
    for name, man in parts.items():
        printcheck(name, export(man, HERE, name))
    for pos in (0.0, 1.0):
        b, s = assembled(pos)
        print("slider at %.0f: overlap with base %.3f mm3, smallest gap %.2f mm" % (pos, (b ^ s).volume(), b.min_gap(s, 2.0)))
