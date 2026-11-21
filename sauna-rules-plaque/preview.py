"""Preview renders for the sauna rules plaque (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import plaque as pq
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

LIGHT = (240, 228, 206); DARK = (96, 62, 40); WALL = (214, 170, 120)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
UP = (90, 0, 0)
big = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))
p = pq.plaque()
lo = p ^ big.translate((0, 0, pq.BASE - 50))
hi = p ^ big.translate((0, 0, pq.BASE))
two = [(to_trimesh(lo.rotate(UP)), LIGHT), (to_trimesh(hi.rotate(UP)), DARK)]
render(two, az=0, el=0, size=(1050, 800), margin=0.05).save(os.path.join(d, "plaque-front.png"))
render(two, az=25, el=12, size=(1050, 800)).save(os.path.join(d, "plaque-angle.png"))
render([(to_trimesh(p), WALL)], az=20, el=55, size=(1050, 800)).save(os.path.join(d, "plaque-one-color.png"))
corner = p ^ Manifold.cube((70, 42, 10)).translate((-105, 40, -1))
render([(to_trimesh(corner), WALL)], az=25, el=40, size=(1050, 800)).save(os.path.join(d, "plaque-detail.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("plaque-front.png", "Two colors: one filament swap at 2.4 mm"), ("plaque-angle.png", "210 x 160 mm, letters 1 mm high"),
    ("plaque-one-color.png", "One color, as it prints"), ("plaque-detail.png", "Countersunk screw holes in the corners")]]
sheet(tiles, 2, os.path.join(d, "plaque-preview.png"), "Raised sauna rules plaque", tile=(700, 533))
