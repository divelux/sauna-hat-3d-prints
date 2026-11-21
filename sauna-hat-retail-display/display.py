#!/usr/bin/env python3
"""Retail display for sauna hats: pedestals of three heights for a shop counter or a spa reception desk.

Each pedestal = base + 1, 2 or 3 posts + a dome cap the hat sits on. Parts plug together with spigots
(0.25 mm clearance), no glue. The base-post and post-post joints can be locked with one M4 bolt and nut through
a teardrop hole; the cap simply sits on the top spigot.
All parts print upright without supports.
Run:  python3 display.py        (writes stl/ and 3mf/ next to this file)
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
BASE_D = 170.0        # base diameter
BASE_T = 12.0         # base thickness
POST_D = 34.0         # post diameter
POST_L = 150.0        # post length (without the spigot); 1, 2 or 3 posts give the three heights
SPIGOT_D = 24.0       # spigot diameter
SPIGOT_ID = 15.0      # the spigot is a tube, this is its bore
SPIGOT_L = 22.0       # spigot length (how far the parts slide into each other)
CLEAR = 0.25          # radial gap between spigot and socket
CAP_D = 120.0         # dome cap diameter (fits inside the crown of a bell sauna hat)
CAP_H = 66.0          # dome cap height
WALL = 3.0            # wall of the posts and the cap
BOLT_D = 4.4          # cross hole for an M4 bolt (use 3.4 for M3); 0 = no holes
BOLT_Z = 11.0         # height of the cross hole above each joint
SCREW_D = 4.6         # three countersunk holes in the base for #8 / 4 mm wood screws (0 = none)
# -------------------------------------------------
SEG = 128
SOCKET = SPIGOT_D / 2 + CLEAR       # socket bore radius


def poly(points):
    cs = _poly(points)
    return cs if cs.area() > 0 else _poly(points[::-1])


def _teardrop(r):
    """Horizontal hole along y with a pointed top, so it prints without supports. Centered at the origin."""
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(-225, 46, 10)]
    pts += [(0, r * math.sqrt(2))]
    return poly(pts).extrude(POST_D + 20).translate((0, 0, -(POST_D + 20) / 2)).rotate((90, 0, 0))


def spigot(z0, hole=True):
    """Spigot tube standing on z0, with a chamfered top edge."""
    r, ri, c = SPIGOT_D / 2, SPIGOT_ID / 2, 1.0
    prof = poly([(ri, 0), (r, 0), (r, SPIGOT_L - c), (r - c, SPIGOT_L), (ri, SPIGOT_L)])
    s = prof.revolve(SEG).translate((0, 0, z0))
    if BOLT_D > 0 and hole:
        s -= _teardrop(BOLT_D / 2).translate((0, 0, z0 + BOLT_Z))
    return s


def base():
    r, c = BASE_D / 2, 2.0
    body = poly([(0, 0), (r, 0), (r, BASE_T - c), (r - c, BASE_T), (0, BASE_T)]).revolve(SEG)
    body += spigot(BASE_T - 0.01)
    if SCREW_D > 0:
        head = 9.0
        for k in range(3):
            a = math.radians(90 + 120 * k)
            x, y = 0.36 * BASE_D * math.cos(a), 0.36 * BASE_D * math.sin(a)
            body -= Manifold.cylinder(BASE_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((x, y, -1))
            sink = (head - SCREW_D) / 2
            body -= Manifold.cylinder(sink + 0.5, SCREW_D / 2, head / 2 + 0.5, 48).translate((x, y, BASE_T - sink))
    return body


def post():
    """A tube with a socket at the bottom and a spigot on top. The bore narrows at 45 degrees below the spigot."""
    R = POST_D / 2
    body = Manifold.cylinder(POST_L, R, R, SEG)
    rs, ri = SOCKET, SPIGOT_ID / 2
    cone_h = rs - ri
    bore = poly([(0, -1), (rs, -1), (rs, POST_L - 6 - cone_h), (ri, POST_L - 6), (ri, POST_L + 1), (0, POST_L + 1)]).revolve(SEG)
    body -= bore
    if BOLT_D > 0:
        body -= _teardrop(BOLT_D / 2).translate((0, 0, BOLT_Z))
    return body + spigot(POST_L - 0.01)


def cap():
    """Dome the hat sits on. Hollow: the inside is a 45 degree cone open at the bottom, so it prints without supports;
    a central tube holds the socket."""
    R, H = CAP_D / 2, CAP_H
    n = 48
    pts = [(0, 0), (R, 0)]
    for i in range(1, n + 1):                      # super-ellipse: full near the brim, rounded on top
        t = i / n * math.pi / 2
        pts.append((R * math.cos(t) ** 0.8, H * math.sin(t) ** 1.0))
    dome = poly(pts).revolve(SEG)
    inner = [(x * (R - WALL) / R, z * (H - WALL) / H) for x, z in pts]       # the dome shrunk by about one wall
    apex = H - WALL * math.sqrt(2) - 1.0
    cone = poly([(0, -1), (apex + 1, -1), (0, apex)]).revolve(SEG) ^ poly(inner[:1] + [(R - WALL, -1)] + inner[1:]).revolve(SEG)
    tube_r = SOCKET + WALL + 1.0
    tube = Manifold.cylinder(apex, tube_r, tube_r, SEG)
    socket = poly([(0, -1), (SOCKET, -1), (SOCKET, SPIGOT_L + 0.5), (0, SPIGOT_L + 0.5 + SOCKET)]).revolve(SEG)
    return dome - (cone - tube) - socket          # the cap just sits on its spigot (no bolt: it is 120 mm wide)


def pedestal(posts):
    """Assembled pedestal (for previews and the fit check): list of placed parts."""
    parts = [base()]
    z = BASE_T
    for _ in range(posts):
        parts.append(post().translate((0, 0, z)))
        z += POST_L
    parts.append(cap().translate((0, 0, z)))
    return parts, z + CAP_H


if __name__ == "__main__":
    for name, man in (("display-base", base()), ("display-post", post()), ("display-cap", cap())):
        printcheck(name, export(man, HERE, name))
    parts, h = pedestal(2)
    ov = sum((a ^ b).volume() for i, a in enumerate(parts) for b in parts[i + 1:])
    print("pedestal with 2 posts: overlap between parts %.3f mm3, smallest gap %.2f mm, height %.0f mm"
          % (ov, min(parts[i].min_gap(parts[i + 1], 2.0) for i in range(len(parts) - 1)), h))
    for k in (1, 2, 3):
        print(f"  {k} post(s): top of the cap at {BASE_T + k * POST_L + CAP_H:.0f} mm")
