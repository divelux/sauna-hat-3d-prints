"""Preview renders for the thermometer float (not needed for printing). The thermometer is a simple stand-in."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import thermo_float as fl
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

C1 = (236, 120, 60); WATER = (150, 192, 214); GLASS = (230, 232, 236); RED = (190, 40, 40); CAP = (60, 60, 64)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
body, env = fl.parts(25)
_, _, _, _, zw = fl.buoyancy(body, env)


def thermometer(dia=25.0, length=190.0, z_top=None):
    r = dia / 2
    tube = Manifold.cylinder(length, r, r, 64)
    head = Manifold.cylinder(18, r + 1.5, r + 1.5, 64).translate((0, 0, length))
    bulb = Manifold.cylinder(length * 0.55, 2.2, 2.2, 32).translate((0, 0, 12)) + Manifold.sphere(4.5, 32).translate((0, 0, 12))
    off = (z_top if z_top is not None else fl.FLOAT_H + fl.COLLAR_H + 25) - length
    return [(to_trimesh(tube.translate((0, 0, off))), GLASS), (to_trimesh(head.translate((0, 0, off))), CAP),
            (to_trimesh(bulb.translate((0, -r + 1.2, off))), RED)]


def water(z, cut=False):
    w = Manifold.cylinder(1.0, 88, 88, 128).translate((0, 0, z - 1.0)) - env.hull()
    if cut:
        w = w ^ Manifold.cube((300, 300, 10)).translate((-300, -150, z - 5))
    return (to_trimesh(w), WATER)


render([(to_trimesh(body), C1)], az=30, el=28, size=(1050, 900)).save(os.path.join(d, "float-alone.png"))
render([(to_trimesh(body), C1)] + thermometer() + [water(zw)], az=30, el=14, size=(1050, 900)).save(os.path.join(d, "float-in-water.png"))
half = body ^ Manifold.cube((300, 300, 200)).translate((-300, -150, -1))
render([(to_trimesh(half), C1), water(zw, cut=True)], az=-90, el=5, size=(1050, 900)).save(os.path.join(d, "float-section.png"))
row = []
for i, dd in enumerate(fl.FILES):
    b, _ = fl.parts(dd)
    row.append((to_trimesh(b.translate((i * 140 - 140, 0, 0))), C1))
render(row, az=0, el=35, size=(1050, 900)).save(os.path.join(d, "float-sizes.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("float-in-water.png", "Floats about 60% deep with a 60 g thermometer"), ("float-alone.png", "Slotted collar grips, eye for a cord"),
    ("float-section.png", "Cut through: three sealed air rings"), ("float-sizes.png", "For 16, 25 and 35 mm thermometers")]]
sheet(tiles, 2, os.path.join(d, "float-preview.png"), "Cold plunge thermometer float", tile=(700, 600))
