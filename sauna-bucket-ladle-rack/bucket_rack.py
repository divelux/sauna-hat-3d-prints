#!/usr/bin/env python3
"""Sauna bucket and ladle wall rack - one plate with three angled arms.

The bucket hangs by its handle on the wide center hook; the ladle lies across the two side forks above it,
clear of the bucket. Prints plate-down, the arms lean at 45 degrees, no supports.
Run:  python3 bucket_rack.py      (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, filleted, printcheck, rect, rounded, stroke  # noqa: E402

# ---------------- parameters (mm) ----------------
BAR_W, BAR_H = 200.0, 38.0     # top bar of the T-shaped plate (BAR_W must fit your bed)
STEM_W, STEM_H = 52.0, 84.0    # stem that carries the bucket hook
PLATE_T = 5.0                  # plate thickness
HOOK_W = 36.0                  # bucket hook width
HOOK_T = 10.0                  # bucket hook thickness
HOOK_L = 58.0                  # bucket hook length: takes a handle grip up to about 32 mm thick
FORK_W = 14.0                  # ladle fork width
FORK_T = 8.0                   # ladle fork thickness
FORK_L = 40.0                  # ladle fork length: takes a ladle handle up to about 26 mm thick
FORK_INSET = 16.0              # fork center to the end of the bar
ARM_ANGLE = 45.0               # arms rise at this angle from the plate (45 prints without supports)
SCREW_D = 4.6                  # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0                   # countersink diameter
# -------------------------------------------------

HOOK_Y = -STEM_H + 8.0         # where the bucket hook leaves the plate (y = 0 is the lower edge of the bar)
FORK_Y = 6.0                   # where the forks leave the plate
SCREWS = [(-BAR_W / 2 + 42, BAR_H / 2), (BAR_W / 2 - 42, BAR_H / 2), (0, BAR_H - 11), (0, HOOK_Y + HOOK_L * 0.72 + 16)]


def plate_outline():
    t = rect(-BAR_W / 2, 0, BAR_W / 2, BAR_H) + rect(-STEM_W / 2, -STEM_H, STEM_W / 2, 1)
    return filleted(rounded(t, 10.0), 14.0)


def arm(y0, length, thick, width):
    """One arm: a rounded bar that rises from the plate toward +y (up on the wall) at ARM_ANGLE.
    Drawn as a (y, z) profile and extruded along x; the corner between arm and plate is filled in."""
    a = math.radians(ARM_ANGLE)
    r = thick / 2
    start = (y0, PLATE_T - r)                       # buried in the plate
    tip = (y0 + length * math.cos(a), PLATE_T + length * math.sin(a))
    prof = stroke([start, tip], r)
    # root: fill the acute corner between the arm and the plate (this is where the handle rests)
    prof = filleted(prof + rect(y0 - r, 0, y0 + length * 0.8, PLATE_T), min(4.0, r))
    prof ^= rect(y0 - r, 0.5, y0 + 2 * length, PLATE_T + 2 * length)     # stay inside the plate
    return prof.extrude(width).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((-width / 2, 0, 0))


def bucket_rack():
    """Print orientation: plate on the bed. On the wall: +y is up, +z points into the room."""
    body = plate_outline().extrude(PLATE_T)
    body += arm(HOOK_Y, HOOK_L, HOOK_T, HOOK_W)
    for sx in (-1, 1):
        body += arm(FORK_Y, FORK_L, FORK_T, FORK_W).translate((sx * (BAR_W / 2 - FORK_INSET), 0, 0))
    sink_h = (HEAD_D - SCREW_D) / 2
    for x, y in SCREWS:
        hole = Manifold.cylinder(PLATE_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((0, 0, -1))
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, PLATE_T - sink_h))
        body -= (hole + sink).translate((x, y, 0))
    return body


if __name__ == "__main__":
    printcheck("bucket-ladle-rack", export(bucket_rack(), HERE, "bucket-ladle-rack"))
