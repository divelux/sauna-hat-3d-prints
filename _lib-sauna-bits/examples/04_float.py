#!/usr/bin/env python3
"""Example 4: a small sealed float with two ring chambers, and the buoyancy computed from the mesh.
Shows: parts.gable_ring_cells, cad.poly(...).revolve, measuring volumes with manifold3d.
Run from the repository root:  python3 examples/04_float.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from manifold3d import Manifold  # noqa: E402
from sauna_bits import cad, parts  # noqa: E402

R, H, BORE, WALL = 40.0, 30.0, 8.0, 2.0
DENSITY = 1.27            # PETG, g/cm3


def build():
    env = cad.poly([(BORE, 0), (R - 3, 0), (R, 3), (R, H), (BORE, H)]).revolve(128)
    cells = parts.gable_ring_cells(BORE + WALL, R - WALL, H, WALL, cells=2) ^ cad.poly([(BORE, 0), (R - 3, 0), (R, 3), (R, H), (BORE, H)]).offset(-WALL)
    return {"float-80mm": env - cells.revolve(128)}, env


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    parts_, env = build()
    for name, m in parts_.items():
        tm = cad.export(m, out, name)
        cad.report(name, tm)
        mass = m.volume() / 1000 * DENSITY
        lift = env.volume() / 1000
        print(f"  PETG {m.volume() / 1000:.1f} cm3 = {mass:.0f} g, lift fully under {lift:.0f} g -> "
              f"{'floats' if lift > mass else 'sinks'} with {lift - mass:.0f} g to spare")
        print(f"  {len(m.decompose())} surfaces: the outside and {len(m.decompose()) - 1} sealed chambers")
