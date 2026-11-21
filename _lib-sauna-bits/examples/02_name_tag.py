#!/usr/bin/env python3
"""Example 2: a name tag with a bell hat icon and raised text, ready for a two-color print (swap at 2.4 mm).
Shows: text.text, text.bell_hat, cad.rounded, cad.clean.
Run from the repository root:  python3 examples/02_name_tag.py ANNA"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sauna_bits import cad, text  # noqa: E402

BASE, UP = 2.4, 1.0


def build(name="ANNA"):
    plate = cad.rounded(cad.rect(-40, -14, 40, 14), 6.0)
    body = (plate - cad.circle(3.0, -33, 0)).extrude(BASE)
    raised = text.bell_hat(14, 15).translate((-21, -7.5))
    raised += text.text(name, 10, max_width=48, align="left").translate((-10, -5))
    body += cad.clean(raised).extrude(UP + 0.5).translate((0, 0, BASE - 0.5))
    return {f"name-tag-{name.lower()}": body}


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    for name, m in build(*(sys.argv[1:2] or ["ANNA"])).items():
        cad.printcheck(name, cad.export(m, out, name))
