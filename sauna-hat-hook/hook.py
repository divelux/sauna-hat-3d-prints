#!/usr/bin/env python3
"""Sauna hat hooks - a wall hook with a wide rounded "mushroom" cap, and an over-the-door / over-the-rail hook.

Both print without supports. Run:  python3 hook.py   (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import circle, export, filleted, poly, rect, report, rounded, stroke  # noqa: E402

# ---------------- wall hook parameters (mm) ----------------
PLATE_W, PLATE_L, PLATE_T = 44, 124, 5     # back plate
PLATE_R = 10                               # plate corner radius
STEM_R = 12                                # stem radius
STEM_L = 16                                # straight stem length (gap for the felt behind the cap)
CAP_R = 35                                 # cap radius - wide, so it does not dent the felt
CAP_EDGE_R = 6                             # rounding of the cap rim
CAP_DOME = 6                               # height of the domed front of the cap
SCREW_D = 4.6                              # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0                               # countersink diameter
SCREW_OFFSET = 50                          # hole distance from the plate center
# ---------------- door / rail hook parameters (mm) ---------
DOOR_T = 35.5                              # door thickness: 35.5 = 1-3/8 in interior door, 45 = 1-3/4 in
STRAP_T = 2.4                              # strap over the top of the door (thin, to clear the frame)
BACK_LIP = 38                              # how far the strap hangs down the back of the door
FRONT_L = 105                              # front plate length
FRONT_T = 4
HOOK_W = 56                                # hook width (print height)
BULB_R = 17                                # radius of the rounded bar the hat rests on
BULB_GAP = 13                              # gap between the door-side plate and the bar
BULB_CHAMFER = 6                           # 45 degree bevel on both ends of the bar
# -----------------------------------------------------------


def wall_hook():
    """Prints plate-down. The underside of the cap is a 45 degree cone, so no supports."""
    plate = rounded(rect(-PLATE_W / 2, -PLATE_L / 2, PLATE_W / 2, PLATE_L / 2), PLATE_R).extrude(PLATE_T)
    # profile of the stem + cap in (radius, height), revolved around the axis
    z0 = PLATE_T
    rim_r = CAP_R - CAP_EDGE_R                       # center of the rim rounding
    cone_h = rim_r + CAP_EDGE_R * math.cos(math.radians(45)) - STEM_R              # 45 degree cone: rise = run
    z_cone0 = z0 + STEM_L
    z_rim = z_cone0 + cone_h + CAP_EDGE_R * math.sin(math.radians(45))             # rim circle center height
    pts = [(0, 0), (STEM_R + 3, 0), (STEM_R + 3, z0), (STEM_R, z0 + 3), (STEM_R, z_cone0)]
    # rim rounding from the 45 degree cone (angle -45) up to the dome (angle 90)
    for i in range(0, 13):
        a = math.radians(-45 + 135 * i / 12)
        pts.append((rim_r + CAP_EDGE_R * math.cos(a), z_rim + CAP_EDGE_R * math.sin(a)))
    # low dome across the front, flat where it meets the rim and at the center
    z_top = z_rim + CAP_EDGE_R
    for i in range(1, 25):
        r = rim_r * (1 - i / 24)
        pts.append((r, z_top + CAP_DOME * (1 - (r / rim_r) ** 2) ** 1.5))
    body = poly(pts).revolve(128)
    out = plate + body
    for sy in (-1, 1):
        hole = Manifold.cylinder(PLATE_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((0, sy * SCREW_OFFSET, -1))
        sink_h = (HEAD_D - SCREW_D) / 2
        sink = Manifold.cylinder(sink_h + 0.01, SCREW_D / 2, HEAD_D / 2, 48).translate((0, sy * SCREW_OFFSET, PLATE_T - sink_h))
        out -= hole + sink
    return out


def door_hook(door_t=DOOR_T):
    """Prints on its side (the profile below lies on the bed), no supports. x = out from the door, y = up."""
    clip = (rect(-door_t - STRAP_T, 0, FRONT_T, STRAP_T)                 # strap over the door top
            + rect(-door_t - STRAP_T, -BACK_LIP, -door_t, STRAP_T)       # back lip
            + rect(0, -FRONT_L, FRONT_T, STRAP_T))                       # front plate
    bx = FRONT_T + BULB_GAP + BULB_R
    by = -FRONT_L + BULB_R + 8
    # arm: out from the bottom of the plate, then up into the middle of the bar
    neck = stroke([(FRONT_T / 2, -FRONT_L + 6), (bx - 4, -FRONT_L + 6), (bx, -FRONT_L + 10), (bx, by)], 6)
    arm = filleted(neck + rect(0, -FRONT_L, FRONT_T, -FRONT_L + 45), 6)
    arm = arm ^ rect(0, -FRONT_L - 20, 200, 0)          # keep the door side of the plate flat
    body = (clip + arm).extrude(HOOK_W)
    # the bar the hat rests on: a cylinder with 45 degree bevels on both ends, so the felt meets no sharp edge
    c, r = BULB_CHAMFER, BULB_R
    bar = poly([(0, 0), (r - c, 0), (r, c), (r, HOOK_W - c), (r - c, HOOK_W), (0, HOOK_W)]).revolve(128)
    return body + bar.translate((bx, by, 0))


if __name__ == "__main__":
    parts = {
        "hat-hook-wall": wall_hook(),
        "hat-hook-door-35mm": door_hook(35.5),
        "hat-hook-door-45mm": door_hook(45.0),
        "hat-hook-rail-20mm": door_hook(20.5),
    }
    for name, man in parts.items():
        report(name, export(man, HERE, name))
