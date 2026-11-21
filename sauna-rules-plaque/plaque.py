#!/usr/bin/env python3
"""Raised sauna rules plaque: a title and six short rules in raised letters, for a two-color print with one swap.

Prints flat, letters up, no supports.
Run:  python3 plaque.py                              (writes stl/ and 3mf/ next to this file)
      python3 plaque.py "HOUSE RULES" "RULE ONE" "RULE TWO" ...   (your own title and rules, up to 7)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from manifold3d import JoinType, Manifold  # noqa: E402
from dvx_cad import export, printcheck, rect, rounded  # noqa: E402
from dvx_text import bell_hat, text  # noqa: E402

# ---------------- parameters (mm) ----------------
TITLE = "SAUNA RULES"
RULES = [
    "SHOWER BEFORE YOU GO IN",
    "SIT ON A TOWEL",
    "ASK BEFORE ADDING STEAM",
    "KEEP YOUR VOICE LOW",
    "COOL DOWN, DRINK WATER",
    "LEAVE IF YOU FEEL UNWELL",
]
WIDTH = 210.0         # plaque width
HEIGHT = 160.0        # plaque height
CORNER = 10.0         # corner radius
BASE = 2.4            # plate thickness (swap filament here for two colors)
UP = 1.0              # letters, bullets and border stand this high
BORDER_IN = 5.0       # raised border line, inset from the edge
BORDER_W = 2.0        # raised border line width
TITLE_CAP = 13.0      # title cap height
RULE_CAP = 6.2        # rule cap height (6 mm or more keeps the letter strokes printable with a 0.4 mm nozzle)
HOLE_D = 4.2          # two countersunk holes for #6 / 3.5 mm screws (0 = none, use mounting tape)
HEAD_D = 8.0
# -------------------------------------------------


def plaque(title=TITLE, rules=RULES):
    """x = across, y = up the wall, z = out (printed face up)."""
    w, h = WIDTH, HEIGHT
    plate = rounded(rect(-w / 2, -h / 2, w / 2, h / 2), CORNER)
    body = plate.extrude(BASE)
    raised = plate.offset(-BORDER_IN, JoinType.Round) - plate.offset(-BORDER_IN - BORDER_W, JoinType.Round)
    inner_l, inner_r = -w / 2 + BORDER_IN + BORDER_W + 8, w / 2 - BORDER_IN - BORDER_W - 8
    # title
    ty = h / 2 - BORDER_IN - BORDER_W - 8 - TITLE_CAP
    raised += text(title, TITLE_CAP, tracking=TITLE_CAP * 0.12, max_width=inner_r - inner_l).translate((0, ty))
    raised += rect(-28, ty - 7.5, 28, ty - 6.0)                     # short rule under the title
    # rules with small hat bullets
    top = ty - 16
    bottom = -h / 2 + BORDER_IN + BORDER_W + 9
    step = (top - bottom) / max(len(rules), 1)
    for i, line in enumerate(rules):
        y = top - (i + 0.5) * step - RULE_CAP / 2
        hat = bell_hat(RULE_CAP * 1.25, RULE_CAP * 1.3).translate((inner_l + RULE_CAP * 0.62, y - 0.3))
        words = text(line, RULE_CAP, tracking=0.25, align="left", max_width=inner_r - inner_l - RULE_CAP * 2.2)
        raised += hat + words.translate((inner_l + RULE_CAP * 2.0, y))
    body += raised.extrude(UP + 0.5).translate((0, 0, BASE - 0.5))
    if HOLE_D > 0:
        sink = (HEAD_D - HOLE_D) / 2
        for sx in (-1, 1):
            x, y = sx * (w / 2 - BORDER_IN - 10), h / 2 - BORDER_IN - 10
            body -= Manifold.cylinder(BASE + 2, HOLE_D / 2, HOLE_D / 2, 48).translate((x, y, -1))
            body -= Manifold.cylinder(sink + 0.5, HOLE_D / 2, HEAD_D / 2 + 0.5, 48).translate((x, y, BASE - sink))
    return body


if __name__ == "__main__":
    if len(sys.argv) > 2:
        name, m = "sauna-rules-plaque-custom", plaque(sys.argv[1], sys.argv[2:9])
    else:
        name, m = "sauna-rules-plaque", plaque()
    printcheck(name, export(m, HERE, name))
