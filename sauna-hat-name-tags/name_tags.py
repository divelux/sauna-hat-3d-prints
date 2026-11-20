#!/usr/bin/env python3
"""Name tags for sauna hats - a small hat-shaped tag with a split ring that twists onto the hanging loop of the hat.

Run:  python3 name_tags.py                 (writes the released set to stl/ and 3mf/ next to this file)
      python3 name_tags.py Anna "J.R." 7   (writes tags with your own text)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import JoinType  # noqa: E402
from dvx_cad import circle, clean, export, printcheck, rect  # noqa: E402
from dvx_text import bell_hat, text  # noqa: E402

# ---------------- parameters (mm) ----------------
TAG_W, TAG_H = 38.0, 35.0   # hat-shaped body
TAG_T = 2.4                 # plate thickness (swap filament at this height for two-color letters)
RELIEF = 0.8                # height of the raised letters and outline
BORDER = 1.3                # width of the raised outline (0 = none)
RING_IN = 7.5               # inside radius of the ring: the hat's loop goes through here
RING_BAND = 2.6             # width of the ring
SLIT = 0.6                  # width of the cut in the ring (0 = closed ring, tie it on with twine)
SLIT_AT = 38.0              # position of the cut, degrees from the top of the ring
FONT = None                 # path to a .ttf, or None for the default bold font
RELEASED = ["A", "B", "C", "D", "E", "F", "G", "H", "DAD", "MOM", "GUEST", ""]
# -------------------------------------------------


def name_tag(label=""):
    """Printed flat, letters up."""
    hat = bell_hat(TAG_W, TAG_H)
    ring_out = RING_IN + RING_BAND
    cy = TAG_H + RING_IN - 0.6                     # ring center: the band merges into the crown of the hat
    plate = hat + circle(ring_out, 0, cy)
    opening = circle(RING_IN, 0, cy)
    if SLIT > 0:
        # a slanted cut through the band; twist the two ends apart to hook the tag on
        cut = rect(-SLIT / 2, -RING_BAND * 1.6, SLIT / 2, RING_BAND * 1.6).rotate(42).translate((0, RING_IN + RING_BAND / 2))
        opening += cut.rotate(-SLIT_AT).translate((0, cy))
    # the field inside the raised outline is cut down; letters are left standing in it
    field = hat.offset(-BORDER, JoinType.Round) if BORDER > 0 else hat.offset(-0.01, JoinType.Round)
    field -= circle(ring_out + 0.01, 0, cy)        # the ring itself stays at plate height...
    low = circle(ring_out + 1, 0, cy) - hat        # ...so it flexes: cut the whole ring down to TAG_T
    if label:
        one = len(label) == 1
        cap = TAG_H * (0.50 if one else 0.27)
        t = text(label, cap, font=FONT, max_width=TAG_W - (16 if one else 8.5), tracking=0 if one else cap * 0.06)
        b = t.bounds()
        field -= t.translate((0, (TAG_H * (0.46 if one else 0.36)) - (b[1] + b[3]) / 2))
    body = plate.extrude(TAG_T + RELIEF)
    body -= clean(field + low).extrude(RELIEF + 1).translate((0, 0, TAG_T))
    return body - opening.extrude(TAG_T + RELIEF + 2).translate((0, 0, -1))


def file_name(label):
    return "hat-tag-" + (re.sub(r"[^A-Za-z0-9]+", "-", label).strip("-") or "blank")


if __name__ == "__main__":
    for label in (sys.argv[1:] or RELEASED):
        name = file_name(label)
        printcheck(name, export(name_tag(label), HERE, name))
