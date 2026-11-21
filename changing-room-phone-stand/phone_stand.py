#!/usr/bin/env python3
"""Changing-room phone stand: holds a phone upright as a sauna timer, with a slot for the charging cable.

Prints standing up as it is used, no supports. The cable drops through a slot in the seat and leaves at the back.
Run:  python3 phone_stand.py        (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, filleted, printcheck, rect, rounded
from dvx_cad import poly as _poly  # noqa: E402

# ---------------- parameters (mm) ----------------
WIDTH = 80.0          # stand width
ANGLE = 65.0          # phone angle from the table, degrees
PHONE_T = 15.0        # gap for the phone: phone plus case up to this thickness
SEAT_Z = 22.0         # height of the seat the phone stands on (room for the cable plug below)
LIP_H = 8.0           # front lip above the seat
LIP_T = 4.0           # front lip thickness
BACK_L = 105.0        # length of the back support along the phone
BACK_T = 6.0          # back support thickness
BASE_T = 4.0          # base plate thickness
DEPTH = 112.0         # base depth, front to back (stability)
CABLE_W = 14.0        # width of the cable slot (most USB-C and Lightning plugs are 11-13 mm wide)
LEG_W = 16.0          # width of each rear leg; the cable leaves between them
# -------------------------------------------------

A = math.radians(ANGLE)
Y0 = LIP_T + PHONE_T                       # where the back of the phone meets the seat
UX, UZ = math.cos(A), math.sin(A)          # up the phone
NX, NZ = math.sin(A), -math.cos(A)         # normal into the back support


def poly(points):
    """2D polygon, either winding."""
    cs = _poly(points)
    return cs if cs.area() > 0 else _poly(points[::-1])


def _along_x(profile_yz, x0, x1):
    """Extrude a 2D profile drawn as (y, z) along the x axis from x0 to x1."""
    return profile_yz.extrude(x1 - x0).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((x0, 0, 0))


def stand():
    """x = across, y = front to back, z = up. Printed in this orientation."""
    top = (Y0 + UX * BACK_L, SEAT_Z + UZ * BACK_L)
    back = poly([(Y0, SEAT_Z), top, (top[0] + NX * BACK_T, top[1] + NZ * BACK_T),
                 (Y0 + NX * BACK_T + 2, SEAT_Z + NZ * BACK_T - 4), (Y0 + 2, 0), (Y0, 0)])
    seat = rect(0, 0, Y0 + 3, SEAT_Z) + rect(0, 0, LIP_T, SEAT_Z + LIP_H)
    base = rect(0, 0, DEPTH, BASE_T)
    # rear legs: from the upper half of the back support down to the back of the base
    def on_back(f):     # a point on the back face of the support, f = share of its length
        return (Y0 + UX * BACK_L * f + NX * BACK_T, SEAT_Z + UZ * BACK_L * f + NZ * BACK_T)
    q1, q2 = on_back(0.50), on_back(0.80)
    leg = poly([(q1[0] - NX, q1[1] - NZ), (q2[0] - NX, q2[1] - NZ), (DEPTH, BASE_T + 8), (DEPTH, 0), (DEPTH - 16, 0)])
    front = filleted(rounded(seat + back, 1.5) + base, 3.0)
    body = _along_x(front, -WIDTH / 2, WIDTH / 2)
    for sx in (-1, 1):
        x0 = WIDTH / 2 - LEG_W
        body += _along_x(filleted(leg + base, 4.0), x0, WIDTH / 2).mirror((1, 0, 0)) if sx < 0 else \
            _along_x(filleted(leg + base, 4.0), x0, WIDTH / 2)
    # cable slot: down through the seat to the base plate, open to the back
    # in the phone gap it is open at the top; under the back support it has a 45 degree roof (prints without supports)
    body -= rect(-CABLE_W / 2, LIP_T + 1.5, CABLE_W / 2, Y0 - 0.5).extrude(SEAT_Z + 10).translate((0, 0, BASE_T))
    roof = poly([(-CABLE_W / 2, BASE_T), (CABLE_W / 2, BASE_T), (CABLE_W / 2, SEAT_Z - 4 - CABLE_W / 2),
                 (0, SEAT_Z - 4), (-CABLE_W / 2, SEAT_Z - 4 - CABLE_W / 2)])          # (x, z)
    body -= roof.extrude(DEPTH + 2 - Y0).rotate((90, 0, 0)).translate((0, DEPTH + 1, 0))
    return body


if __name__ == "__main__":
    s = stand()
    tm = export(s, HERE, "phone-stand")
    printcheck("phone-stand", tm)
    c = tm.center_mass
    print("center of mass y = %.1f mm (base runs 0 to %.0f)" % (c[1], DEPTH))
