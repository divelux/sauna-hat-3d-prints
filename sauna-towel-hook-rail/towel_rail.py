#!/usr/bin/env python3
"""Towel hook rail with name plates: a row of pegs, and a slide-in name plate above each one.

The rail prints back-down, the pegs grow straight up from it, no supports. The name plates slide down into
dovetail tracks from the top edge of the rail and hide the screw heads. Rails longer than three hooks are
printed in segments that lock together with a jigsaw joint.
Run:  python3 towel_rail.py        (writes stl/ and 3mf/ next to this file)
      python3 towel_rail.py ANNA   (also writes a name plate with your own text)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import CrossSection, Manifold  # noqa: E402
from dvx_cad import circle, export, poly, printcheck, rect, rounded  # noqa: E402
from dvx_text import text  # noqa: E402

# ---------------- parameters (mm) ----------------
PITCH = 70.0          # distance between hooks = width of one hook module
RAIL_H = 100.0        # rail height on the wall
RAIL_T = 8.0          # rail thickness
CORNER = 6.0          # corner radius of the rail outline
PEG_Y = 24.0          # height of the peg center above the bottom edge of the rail
PEG_W = 16.0          # peg width (left-right)
PEG_D = 14.0          # peg depth (up-down on the wall)
PEG_L = 50.0          # how far the peg stands out from the rail face
LIP = 12.0            # the tip of the peg rises this much, so a towel loop cannot slide off
PLATE_W = 54.0        # name plate width (at its back face)
PLATE_LOW = 46.0      # bottom of the name plate track, above the bottom edge of the rail
PLATE_PROUD = 5.0     # the name plate stands this much above the rail, so you can lift it out
PLATE_T = 3.0         # name plate thickness
TRACK_D = 3.4         # depth of the name plate track
LEAN = 30.0           # dovetail angle of the track sides, degrees from vertical
CLEAR = 0.25          # gap between the name plate and each side of the track
TEXT_CAP = 11.0       # cap height of the name, mm
TEXT_UP = 1.0         # letters stand this high above the plate
SCREW_D = 4.4         # one #8 / 4 mm flat-head wood screw per hook, hidden behind the name plate
HEAD_D = 8.6          # countersink diameter
JOINT_R = 8.5         # jigsaw joint knob radius (segmented rails)
JOINT_CLEAR = 0.2     # gap all round the knob
# -------------------------------------------------
import math  # noqa: E402

FLOOR_Z = RAIL_T - TRACK_D
TAN = math.tan(math.radians(LEAN))


def _knob(grow=0.0):
    """Jigsaw knob pointing to +x from x = 0, centered at PEG_Y (below the name plate track)."""
    neck = rect(-1, PEG_Y - 5.5 - grow, 8.0, PEG_Y + 5.5 + grow)
    return neck + circle(JOINT_R + grow, 8.0 + JOINT_R * 0.55, PEG_Y)


def _track(x):
    """Dovetail track cut, centered at x: wide at the floor, narrower at the face of the rail."""
    zt = RAIL_T + 1
    b = PLATE_W / 2
    t = b - TAN * (zt - FLOOR_Z)
    prof = poly([(-b, FLOOR_Z), (b, FLOOR_Z), (t, zt), (-t, zt)])            # (x, z)
    cut = prof.extrude(RAIL_H + 1 - PLATE_LOW).rotate((90, 0, 0)).translate((x, RAIL_H + 1, 0))
    return cut


def peg():
    """One peg standing on z = 0 (it is joined to the rail face)."""
    sec = rounded(rect(-PEG_W / 2, -PEG_D / 2, PEG_W / 2, PEG_D / 2), 4.0)
    root = rounded(rect(-PEG_W / 2 - 4, -PEG_D / 2 - 4, PEG_W / 2 + 4, PEG_D / 2 + 4), 6.0)
    flare = Manifold.batch_hull([root.extrude(0.01), sec.extrude(0.01).translate((0, 0, 5))])
    shaft = sec.extrude(PEG_L - LIP * 1.1 - 2)
    # the tip: the wall side stays straight, the top side rises at 48 degrees (no supports)
    head = CrossSection.batch_hull([sec, sec.translate((0, LIP))])
    lip = Manifold.batch_hull([sec.extrude(0.01).translate((0, 0, PEG_L - LIP * 1.1 - 2.01)),
                               head.extrude(0.01).translate((0, 0, PEG_L - 2.01))])
    lip = lip + Manifold.batch_hull([head.extrude(0.01).translate((0, 0, PEG_L - 2.01)),
                                     rounded(rect(-PEG_W / 2 + 1, -PEG_D / 2 + 1, PEG_W / 2 - 1, PEG_D / 2 + LIP - 1), 3.0)
                                     .extrude(0.01).translate((0, 0, PEG_L - 0.01))])
    return flare + shaft + lip


def rail(hooks=3, left_joint=False, right_joint=False):
    """x = along the rail, y = up the wall, z = out from the wall. Printed in this orientation, back on the bed.
    left_joint: a socket on the left end; right_joint: a knob sticking out on the right end."""
    w = hooks * PITCH
    xs = [(i + 0.5) * PITCH for i in range(hooks)]
    outline = rounded(rect(0, 0, w, RAIL_H), CORNER)
    if left_joint:     # square the left end and cut the socket
        outline = (outline + rect(0, 0, CORNER + 1, RAIL_H)) - _knob(JOINT_CLEAR)
    if right_joint:
        outline = (outline + rect(w - CORNER - 1, 0, w, RAIL_H)) + _knob().translate((w, 0))
    body = outline.extrude(RAIL_T)
    sink_h = (HEAD_D - SCREW_D) / 2
    for x in xs:
        body -= _track(x)
        body += peg().translate((x, PEG_Y, RAIL_T - 0.01))
        sy = (PLATE_LOW + RAIL_H) / 2
        body -= Manifold.cylinder(RAIL_T + 2, SCREW_D / 2, SCREW_D / 2, 48).translate((x, sy, -1))
        body -= Manifold.cylinder(sink_h + 0.5, SCREW_D / 2, HEAD_D / 2 + 0.5, 48).translate((x, sy, FLOOR_Z - sink_h))
    return body


def plate(name=""):
    """Name plate, printed back-down, letters up. Its sides lean in to match the track."""
    length = RAIL_H - PLATE_LOW + PLATE_PROUD - 0.3
    b = PLATE_W / 2 - CLEAR
    z0 = 0.05
    t = PLATE_W / 2 - TAN * (PLATE_T + z0) - CLEAR
    b2 = PLATE_W / 2 - TAN * z0 - CLEAR
    prof = poly([(-b2, 0), (b2, 0), (t, PLATE_T), (-t, PLATE_T)])
    body = prof.extrude(length).rotate((90, 0, 0)).translate((0, length, 0))
    # round the two top corners of the part that stands above the rail
    corner = rect(-b - 1, length - 6, b + 1, length + 1) - rounded(rect(-b, -20, b, length), 6.0)
    body -= corner.extrude(PLATE_T + 2).translate((0, 0, -1))
    if name:
        cap = TEXT_CAP
        letters = text(name.upper(), cap, tracking=0.8, max_width=2 * t - 8).translate((0, (length - PLATE_PROUD) / 2 - cap / 2 + 1))
        body += letters.extrude(TEXT_UP + 0.5).translate((0, 0, PLATE_T - 0.5))
    # a short grip bar on the part above the rail
    body += rounded(rect(-12, length - PLATE_PROUD + 0.8, 12, length - 1.0), 1.0).extrude(TEXT_UP + 0.5).translate((0, 0, PLATE_T - 0.5))
    return body


def assembled(hooks=3, names=()):
    """The rail with plates in place (for previews and the fit check)."""
    r = rail(hooks)
    ps = []
    for i in range(hooks):
        p = plate(names[i] if i < len(names) else "")
        ps.append(p.translate(((i + 0.5) * PITCH, PLATE_LOW + 0.3, FLOOR_Z + 0.05)))
    return r, ps


PLATES = ["", "1", "2", "3", "4", "5", "DAD", "MOM", "GUEST", "KIDS"]

if __name__ == "__main__":
    extra = [a for a in sys.argv[1:]]
    if not extra:
        parts = {"towel-rail-3-hooks": rail(3),
                 "towel-rail-segment-left-2-hooks": rail(2, right_joint=True),
                 "towel-rail-segment-middle-1-hook": rail(1, left_joint=True, right_joint=True),
                 "towel-rail-segment-right-2-hooks": rail(2, left_joint=True)}
        for n in PLATES:
            parts["name-plate-" + (n.lower() or "blank")] = plate(n)
    else:
        parts = {"name-plate-" + n.lower(): plate(n) for n in extra}
    for name, man in parts.items():
        printcheck(name, export(man, HERE, name))
    if not extra:
        r, ps = assembled(3, ["DAD", "MOM", "GUEST"])
        print("plates in the rail: overlap %.3f mm3, smallest gap %.2f mm" % (sum((r ^ p).volume() for p in ps), min(r.min_gap(p, 2.0) for p in ps)))
        a = rail(2, right_joint=True)
        b = rail(1, left_joint=True, right_joint=True).translate((2 * PITCH, 0, 0))
        print("jigsaw joint: overlap %.3f mm3, gap %.2f mm" % ((a ^ b).volume(), a.min_gap(b, 2.0)))
