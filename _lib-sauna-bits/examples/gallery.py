#!/usr/bin/env python3
"""Renders img/gallery.png from the four examples (needs Pillow). Not needed to use the library."""
import importlib.util, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from manifold3d import Manifold  # noqa: E402
from sauna_bits import cad  # noqa: E402
from sauna_bits.render import render, sheet  # noqa: E402

C = (214, 170, 120); DARK = (96, 62, 40)


def ex(name):
    spec = importlib.util.spec_from_file_location(name[:-3], os.path.join(ROOT, "examples", name))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


out = os.path.join(ROOT, "img"); os.makedirs(out, exist_ok=True)
big = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))
rail = list(ex("01_peg_rail.py").build().values())[0]
tag = list(ex("02_name_tag.py").build().values())[0]
cup = list(ex("03_measuring_cup.py").build().values())[0]
flt = list(ex("04_float.py").build()[0].values())[0]
tiles = [
    (render([(cad.to_trimesh(rail.rotate((90, 0, 0))), C)], az=25, el=18, size=(700, 560)), "01 peg rail: peg, jigsaw knob, countersunk holes"),
    (render([(cad.to_trimesh(tag ^ big.translate((0, 0, -47.6))), (240, 228, 206)), (cad.to_trimesh(tag ^ big.translate((0, 0, 2.4))), DARK)], az=10, el=40, size=(700, 560)), "02 name tag: text outlines and the hat icon"),
    (render([(cad.to_trimesh(cup), (226, 222, 214))], az=-40, el=35, size=(700, 560)), "03 cup: lines placed by volume"),
    (render([(cad.to_trimesh(flt ^ Manifold.cube((200, 200, 100)).translate((-200, -100, -1))), (236, 120, 60))], az=-70, el=20, size=(700, 560)), "04 float: sealed chambers, 45 degree roofs"),
]
sheet(tiles, 2, os.path.join(out, "gallery.png"), "sauna-bits examples", tile=(700, 560))
