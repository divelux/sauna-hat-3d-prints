#!/usr/bin/env python3
"""Sauna whisk (vihta / venik) drying arm - a braced wall arm that holds one or two whisks away from the wall,
leaves down, so air gets all around them.

Prints on its side (the profile lies on the bed), no supports.
Run:  python3 whisk_hanger.py     (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import clean, export, filleted, printcheck, rect, stroke  # noqa: E402

# ---------------- parameters (mm) ----------------
REACH = 150.0         # how far the arm reaches out from the wall
WIDTH = 22.0          # arm width (print height)
BAND = 7.0            # thickness of the plate, arm and brace
POST_H = 14.0         # height of the two posts that keep the cord loops from sliding off
MID_POST = 0.53       # position of the middle post as a share of REACH
BRACE_DROP = 95.0     # how far below the arm the brace meets the wall plate
BRACE_AT = 0.62       # where the brace meets the arm, as a share of REACH
SCREW_D = 4.6         # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0          # countersink diameter
# -------------------------------------------------

R = BAND / 2
Y_TOP_SCREW = POST_H + R + 12.0          # above the posts, so a screwdriver reaches it
Y_BOT_SCREW = -BRACE_DROP - 14.0         # below the brace
PLATE_TOP = Y_TOP_SCREW + 10.0
PLATE_BOT = Y_BOT_SCREW - 10.0


def profile():
    """x = out from the wall, y = up, the arm's center line is y = 0."""
    band = stroke([(R, PLATE_BOT + R), (R, PLATE_TOP - R)], R)                      # wall plate
    band += stroke([(R, 0), (REACH, 0), (REACH, POST_H)], R)                        # arm and end post
    band += stroke([(REACH * MID_POST, 0), (REACH * MID_POST, POST_H)], R)          # middle post
    band += stroke([(R, -BRACE_DROP), (REACH * BRACE_AT, 0)], R)                    # brace
    band = filleted(band, 6.0)
    # flat against the wall
    return clean(band + rect(0, PLATE_BOT + R, R, PLATE_TOP - R))


def whisk_hanger():
    body = profile().extrude(WIDTH)
    sink_h = (HEAD_D - SCREW_D) / 2
    for y in (Y_TOP_SCREW, Y_BOT_SCREW):
        hole = Manifold.cylinder(BAND + 2, SCREW_D / 2, SCREW_D / 2, 48)
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, BAND + 1 - sink_h))
        # cylinders are made along z; turn them to point along x (out from the wall)
        body -= (hole + sink).translate((0, 0, -1)).rotate((0, 90, 0)).translate((0, y, WIDTH / 2))
    return body


if __name__ == "__main__":
    # the two short horizontal screw holes bridge without supports; nothing else overhangs
    printcheck("whisk-hanger", export(whisk_hanger(), HERE, "whisk-hanger"), max_overhang_mm2=60)
