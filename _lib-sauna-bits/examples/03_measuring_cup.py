#!/usr/bin/env python3
"""Example 3: a small measuring cup with lines at 20, 40 and 60 ml placed by volume, checked on the exported STL.
Shows: parts.cup_cavity, parts.level_for_volume, parts.v_groove_ring, cad.to_manifold.
Run from the repository root:  python3 examples/03_measuring_cup.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from manifold3d import Manifold  # noqa: E402
from sauna_bits import cad, parts  # noqa: E402

INNER_D, WALL, FLOOR, FILLET = 46.0, 2.4, 3.0, 6.0
MARKS = [20, 40, 60]


def levels():
    return [parts.level_for_volume(ml, INNER_D, FLOOR, FILLET) for ml in MARKS]


def build():
    zs = levels()
    top = zs[-1] + 8
    ro = INNER_D / 2 + WALL
    cup = Manifold.cylinder(top, ro, ro, 128) - parts.cup_cavity(INNER_D, top + 1, FLOOR, FILLET)
    for z in zs:
        cup -= parts.v_groove_ring(INNER_D / 2, z, inside=True)
        cup -= parts.v_groove_ring(ro, z, inside=False)
    return {"measuring-cup-60ml": cup}


def water_in(solid, z):
    """ml of water standing up to z inside the given cup."""
    return (Manifold.cylinder(z, INNER_D / 2 + 0.2, INNER_D / 2 + 0.2, 128) - solid).volume() / 1000


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    for name, m in build().items():
        tm = cad.export(m, out, name)
        cad.printcheck(name, tm)
        stl = cad.to_manifold(tm)
        for ml, z in zip(MARKS, levels()):
            print(f"  {ml} ml line at z = {z:.1f} mm: the STL holds {water_in(stl, z):.1f} ml")
