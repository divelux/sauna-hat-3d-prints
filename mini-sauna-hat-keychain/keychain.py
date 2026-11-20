#!/usr/bin/env python3
"""Mini sauna hat keychain - a tiny bell-shaped sauna hat with a loop on top, in two styles:
a hollow 3D hat and a flat tag. Both print without supports.

Run:  python3 keychain.py         (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import JoinType  # noqa: E402
from dvx_cad import circle, clean, export, poly, printcheck, rect  # noqa: E402
from dvx_text import bell_hat  # noqa: E402

# ---------------- 3D hat parameters (mm) ----------------
HAT_D = 34.0          # diameter at the brim
HAT_H = 33.0          # height of the hat without the loop
FLARE = 0.07          # how much the brim flares out
SHELL = 2.2           # wall thickness ("felt")
LOOP_R = 6.5          # outer radius of the loop
LOOP_HOLE = 3.0       # radius of the hole in the loop (fits a standard split key ring)
LOOP_T = 3.6          # loop thickness
LOOP_SINK = 3.5       # how deep the loop sits in the crown
# ---------------- flat tag parameters (mm) --------------
TAG_W, TAG_H = 33.0, 31.0   # hat silhouette
TAG_T = 3.0                 # plate thickness
TAG_RELIEF = 0.8            # raised outline and brim band
TAG_LOOP_R = 5.6            # outer radius of the loop
TAG_LOOP_HOLE = 2.7         # radius of the hole
# --------------------------------------------------------


def _teardrop(r):
    """A hole that prints cleanly when its axis is horizontal: a circle with a 45 degree peak on top."""
    s = r * 2 ** 0.5
    return circle(r) + poly([(-r / 2 ** 0.5, r / 2 ** 0.5), (r / 2 ** 0.5, r / 2 ** 0.5), (0, s)])


def hat_3d():
    """Printed brim-down. The inside is hollow with a 45 degree cone ceiling, so nothing needs support."""
    r0 = HAT_D / 2 / (1 + FLARE)
    n = 72
    outer = []
    for i in range(n + 1):
        t = i / n                                   # 0 = top of the crown, 1 = brim
        outer.append((r0 * (1 - (1 - t) ** 2.4) ** 0.5 + r0 * FLARE * t ** 8, HAT_H * (1 - t)))
    solid = poly([(0, 0)] + outer[::-1]).revolve(96)
    apex = HAT_H - SHELL - 2.0                      # top of the cone ceiling
    inner = [(max(r - SHELL, 0.0), z) for r, z in outer]
    inner = [(min(r, apex - z), z) for r, z in inner if z < apex]      # 45 degree ceiling
    cavity = poly([(0, -1), (inner[-1][0], -1)] + inner[::-1] + [(0, apex)]).revolve(96)
    # loop: a ring standing on the crown
    zc = HAT_H - LOOP_SINK + LOOP_R
    ring = (circle(LOOP_R) + rect(-LOOP_R * 0.75, -LOOP_R, LOOP_R * 0.75, 0)) - _teardrop(LOOP_HOLE)
    loop = ring.extrude(LOOP_T).rotate((90, 0, 0)).translate((0, LOOP_T / 2, zc))
    return solid + loop - cavity


def hat_flat():
    """Printed flat. A hat silhouette with a raised outline and brim band, and a loop for the key ring."""
    hat = bell_hat(TAG_W, TAG_H)
    cy = TAG_H + TAG_LOOP_R - 2.2
    plate = hat + circle(TAG_LOOP_R, 0, cy)
    hole = circle(TAG_LOOP_HOLE, 0, cy)
    # full-height block, then the field inside the outline is cut down to leave the outline, the brim band
    # and a rim around the hole standing
    field = plate.offset(-1.5, JoinType.Round) - rect(-TAG_W, -1, TAG_W, 6.0) - circle(TAG_LOOP_HOLE + 1.6, 0, cy)
    body = plate.extrude(TAG_T + TAG_RELIEF) - clean(field).extrude(TAG_RELIEF + 1).translate((0, 0, TAG_T))
    return body - hole.extrude(TAG_T + TAG_RELIEF + 2).translate((0, 0, -1))


if __name__ == "__main__":
    for name, man in {"mini-hat-keychain-3d": hat_3d(), "mini-hat-keychain-flat": hat_flat()}.items():
        printcheck(name, export(man, HERE, name))
