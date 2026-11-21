#!/usr/bin/env python3
"""Felting form (hat block) for a bell-shaped sauna hat, for felt makers. Prints in parts on a 220 x 220 bed.

The form is a hollow shell in two rings and a crown. Each joint has a registration step (tongue and rabbet with
45 degree bevels) and three screw lugs inside; the screws go in from below through the open brim end.
Nothing needs supports: the rings lean in at more than 45 degrees, the crown is hollowed with a 45 degree cone.
Run:  python3 form.py          (writes stl/ and 3mf/ next to this file)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import Manifold  # noqa: E402
from dvx_cad import export, printcheck  # noqa: E402
from dvx_cad import poly as _poly  # noqa: E402

# ---------------- parameters (mm) ----------------
HEAD_C = 610.0        # circumference of the form at the brim line (about a 61 cm head; a hat of about 24 in)
FORM_H = 200.0        # form height, brim line to the top of the crown
FLARE = 0.03          # the bell widens this much toward the brim (share of the radius)
SHAPE = 2.4           # crown fullness: higher = fuller, flatter top
WALL = 4.0            # shell thickness
SPLITS = [72.0, 138.0]  # joint heights; the crown (above the last joint) is hollowed with a 45 degree cone
TONGUE_H = 6.0        # registration step height at each joint
CLEAR = 0.25          # gap in the registration step
LUGS = 3              # screw lugs per joint
PILOT_D = 3.2         # pilot hole in the upper lug for a #8 / 4 mm screw (the screw cuts its own thread)
SCREW_D = 4.5         # clearance hole in the lower lug
HEAD_D = 8.6          # countersink for the flat screw head (from below)
BED = 220.0
# -------------------------------------------------
SEG = 128
R_BRIM = HEAD_C / (2 * math.pi)
R0 = R_BRIM / (1 + FLARE)


def poly(points):
    cs = _poly(points)
    return cs if cs.area() > 0 else _poly(points[::-1])


def radius(z):
    """Outer radius of the form at height z (0 = brim line, FORM_H = top of the crown)."""
    t = min(max(1 - z / FORM_H, 0.0), 1.0)          # 0 at the top, 1 at the brim
    return R0 * (1 - (1 - t) ** SHAPE) ** 0.5 + R0 * FLARE * t ** 8


def slope_deg(z, dz=0.5):
    """Angle of the outside surface from the horizontal at height z."""
    dr = radius(z - dz) - radius(z + dz)
    return math.degrees(math.atan2(2 * dz, max(dr, 1e-9)))


def outline(n=100):
    """(r, z) points of the outside, from the brim up to the top."""
    pts = [(radius(FORM_H * i / n), FORM_H * i / n) for i in range(n)]
    return pts + [(0.0, FORM_H)]


def solid():
    return poly([(0, 0)] + outline()).revolve(SEG)


def inner_solid():
    """The outside moved in by WALL (measured square to the surface, approximately)."""
    pts = []
    out = outline()
    for (r0, z0), (r1, z1) in zip(out[:-1], out[1:]):
        dr, dz = r1 - r0, z1 - z0
        L = math.hypot(dr, dz)
        nr, nz = dz / L, -dr / L                       # outward normal
        pts.append((r0 - WALL * nr, z0 - WALL * nz))
    pts = [(max(r, 0.0), z) for r, z in pts if r > 0.5]
    return poly([(0, -1), (pts[0][0], -1)] + pts + [(0, pts[-1][1])]).revolve(SEG)


def _band(z0, z1):
    return Manifold.cylinder(z1 - z0, 400, 400, 8).translate((0, 0, z0))


def _lug_angles():
    return [90 + 360 * k / LUGS for k in range(LUGS)]


def form_parts():
    """Returns the list of parts, each in place (z as on the assembled form)."""
    shell = solid() - inner_solid()
    zs = [0.0] + SPLITS + [FORM_H + 1]
    parts = []
    for i in range(len(zs) - 1):
        lo, hi = zs[i], zs[i + 1]
        p = shell ^ _band(lo, hi)
        if i == len(zs) - 2:                           # crown: fill, then hollow with a 45 degree cone from below
            crown = solid() ^ _band(lo, hi)
            # the apex is set so the cone stays inside the shell everywhere (its roof never flatter than 45 degrees)
            apex = min(z + radius(z) - WALL * 1.5 for z in [lo + (FORM_H - lo) * i / 200 for i in range(201)])
            cone = poly([(0, lo - 1), (apex - lo + 1, lo - 1), (0, apex)]).revolve(SEG) ^ inner_solid()
            p = crown - cone
        parts.append(p)
    # joints: registration step on the outer half of the wall + screw lugs inside
    for j, z in enumerate(SPLITS):
        lower, upper = parts[j], parts[j + 1]
        ro = radius(z)
        rm = ro - WALL / 2                              # middle of the wall
        b = WALL / 2                                    # 45 degree bevel size
        # tongue: the lower part continues up on the outer half of the wall
        tongue = poly([(rm + CLEAR / 2, z - 0.01), (ro + 5, z - 0.01), (ro + 5, z + TONGUE_H), (rm + CLEAR / 2 + b, z + TONGUE_H)])
        lower = lower + (tongue.revolve(SEG) ^ solid())
        # rabbet: the same ring, a little larger, cut out of the upper part
        k = b / TONGUE_H                                # the inner faces lean out: b over TONGUE_H (about 70 degrees)
        rabbet = poly([(rm - CLEAR / 2 - k, z - 1), (ro + 6, z - 1), (ro + 6, z + TONGUE_H + CLEAR),
                       (rm - CLEAR / 2 + k * (TONGUE_H + CLEAR), z + TONGUE_H + CLEAR)])
        upper = upper - rabbet.revolve(SEG)
        # lugs: lower one is a corbel (45 degree underside) with a countersink from below; upper one sits on the joint
        ri = ro - WALL
        lug_w, lug_d = 16.0, 16.0
        for a in _lug_angles():
            c = (ri - lug_d / 2 + 1.0)
            low = poly([(-lug_d / 2 - 1, z), (lug_d / 2 + 1, z), (lug_d / 2 + 1, z - lug_d - 2)])            # (radial, z) corbel
            low = low.extrude(lug_w).translate((0, 0, -lug_w / 2)).rotate((90, 0, 0))                          # radial -> x, along y
            low = low.translate((c, 0, 0)).rotate((0, 0, a))
            up = Manifold.cube((lug_d, lug_w, 12)).translate((c - lug_d / 2 - 1, -lug_w / 2, z)).rotate((0, 0, a))
            hx, hy = c * math.cos(math.radians(a)), c * math.sin(math.radians(a))
            lower = (lower + (low ^ solid())) - Manifold.cylinder(40, SCREW_D / 2, SCREW_D / 2, 32).translate((hx, hy, z - 30))
            sink = (HEAD_D - SCREW_D) / 2
            lower = lower - Manifold.cylinder(sink + 6, HEAD_D / 2 + 6, SCREW_D / 2, 32).translate((hx, hy, z - 10 - sink - 6))
            pilot = Manifold.cylinder(14, PILOT_D / 2, PILOT_D / 2, 32) + Manifold.cylinder(PILOT_D / 2, PILOT_D / 2, 0.01, 32).translate((0, 0, 14))
            upper = (upper + (up ^ solid())) - pilot.translate((hx, hy, z - 0.5))     # pointed top: no bridge
        parts[j], parts[j + 1] = lower, upper
    return parts


NAMES = ["felting-form-1-brim-ring", "felting-form-2-middle-ring", "felting-form-3-crown"]

if __name__ == "__main__":
    parts = form_parts()
    print(f"brim radius {R_BRIM:.1f} mm (circumference {HEAD_C:.0f} mm), height {FORM_H:.0f} mm")
    for z in SPLITS:
        print(f"joint at {z:.0f} mm: outside slope {slope_deg(z):.0f} deg from the horizontal, radius {radius(z):.1f} mm")
    zs = [0.0] + SPLITS
    for name, p, z0 in zip(NAMES, parts, zs):
        printcheck(name, export(p.translate((0, 0, -z0)), HERE, name), bed=BED)
    ov = sum((a ^ b).volume() for a, b in zip(parts[:-1], parts[1:]))
    print("assembled: overlap between neighbouring parts %.3f mm3, smallest gap %.2f mm" % (ov, min(a.min_gap(b, 2.0) for a, b in zip(parts[:-1], parts[1:]))))
