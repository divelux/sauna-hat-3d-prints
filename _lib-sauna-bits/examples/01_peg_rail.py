#!/usr/bin/env python3
"""Example 1: a two-peg wall rail with countersunk screw holes and a jigsaw joint on the right end.
Shows: parts.peg, parts.countersunk_hole, parts.jigsaw_knob, cad.printcheck.
Run from the repository root:  python3 examples/01_peg_rail.py   (writes examples/out/)"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sauna_bits import cad, parts  # noqa: E402

PITCH, HEIGHT, THICK = 70.0, 60.0, 7.0


def build():
    w = 2 * PITCH
    outline = cad.rounded(cad.rect(0, 0, w, HEIGHT), 6.0) + cad.rect(w - 8, 0, w, HEIGHT)
    outline += parts.jigsaw_knob().translate((w, HEIGHT / 2))
    rail = cad.clean(outline).extrude(THICK)
    for i in range(2):
        x = (i + 0.5) * PITCH
        rail += parts.peg(length=45, lip=10).translate((x, 22, THICK - 0.01))
        rail -= parts.countersunk_hole(plate_t=THICK).translate((x, HEIGHT - 12, 0))
    return {"peg-rail-2": rail}


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    for name, m in build().items():
        cad.printcheck(name, cad.export(m, out, name))
