#!/usr/bin/env python3
"""Sauna ladle / bucket hook - a simple two-screw J hook, printed on its side for strength, no supports.

Run:  python3 ladle_hook.py   (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import arc, circle, export, rect, report, rounded, stroke  # noqa: E402

# ---------------- parameters (mm) ----------------
WIDTH = 24            # hook width (print height)
PLATE_L = 92          # back plate length
HOOK_R = 15           # inside radius of the J - fits a ladle handle loop, a cord or a bucket bail
HOOK_T = 6            # thickness of the plate and the J
TIP_RISE = 14         # how far the tip rises above the center of the J
SCREW_D = 4.6         # clearance hole for a #8 / 4 mm wood screw
HEAD_D = 9.0          # countersink diameter
# -------------------------------------------------


def profile():
    """x = out from the wall, y = up. One continuous rounded band: back plate, J curve, raised tip."""
    t = HOOK_T / 2
    rr = HOOK_R + t
    cx, cy = t + rr, t + rr
    path = [(t, PLATE_L - t)] + arc(cx, cy, rr, 180, 360, 48) + [(cx + rr, cy + TIP_RISE)]
    band = stroke(path, t) + circle(t + 1.2, cx + rr, cy + TIP_RISE)
    # square off the top of the plate and keep the wall side flat
    return band + rounded(rect(0, PLATE_L - 20, HOOK_T, PLATE_L), 1.5)


def ladle_hook():
    body = profile().extrude(WIDTH)
    holes = []
    y1 = 2 * HOOK_R + HOOK_T + 22
    for y in (y1, PLATE_L - 12):
        hole = Manifold.cylinder(HOOK_T + 2, SCREW_D / 2, SCREW_D / 2, 48)
        sink_h = (HEAD_D - SCREW_D) / 2
        sink = Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((0, 0, HOOK_T + 1 - sink_h))
        # cylinders are made along z; turn them to point along x (out from the wall)
        holes.append((hole + sink).translate((0, 0, -1)).rotate((0, 90, 0)).translate((0, y, WIDTH / 2)))
    for h in holes:
        body -= h
    return body


if __name__ == "__main__":
    report("ladle-hook", export(ladle_hook(), HERE, "ladle-hook"))
