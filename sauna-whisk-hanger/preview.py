"""Preview renders for the whisk drying arm (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import whisk_hanger as wh
from manifold3d import Manifold
from dvx_cad import to_trimesh, poly, circle
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); TWIG = (120, 88, 60); LEAF = (104, 132, 84); CORD = (222, 206, 170)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
h = wh.whisk_hanger()
# profile x = out from the wall, y = up, z = width  ->  world: out = -Y (toward the camera), up = Z, width = X
T = np.eye(4); T[:3, :3] = np.array([[0, 0, 1], [-1, 0, 0], [0, 1, 0]]); T[0, 3] = -wh.WIDTH / 2
ht = to_trimesh(h); ht.apply_transform(T)


def whisk(out, scale=1.0):
    """A birch whisk for scale, hanging leaves-down from a cord loop at distance `out` from the wall."""
    loop = (circle(26) - circle(23.5)).extrude(3).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((-1.5, -out, -24 + wh.R))
    handle = Manifold.cylinder(130, 17, 20, 32).translate((0, -out, -175))
    wrap = Manifold.cylinder(14, 22, 22, 32).translate((0, -out, -70))
    prof = [(0, 0), (20, 0), (70, -60), (130, -190), (140, -270), (95, -330), (0, -345)]
    leaves = poly(prof[::-1]).revolve(40).scale((1, 0.26, 1)).translate((0, -out, -175))
    return [(to_trimesh(loop), CORD), (to_trimesh(handle), TWIG), (to_trimesh(wrap), CORD), (to_trimesh(leaves), LEAF)]


wall = to_trimesh(Manifold.cube((340, 6, 640)).translate((-170, 0, -560)))
render([(ht, C1), (wall, WALL)] + whisk(118) + whisk(42), az=50, el=10, size=(900, 900)).save(os.path.join(d, "whisk-hanger-in-use.png"))
wall2 = to_trimesh(Manifold.cube((120, 6, 200)).translate((-60, 0, -135)))
render([(ht, C1), (wall2, WALL)], az=48, el=16).save(os.path.join(d, "whisk-hanger-mounted.png"))
render([(ht, C1)], az=90, el=0).save(os.path.join(d, "whisk-hanger-side.png"))
render([(to_trimesh(h), C1)], az=20, el=40).save(os.path.join(d, "whisk-hanger-print.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("whisk-hanger-in-use.png", "One or two whisks, leaves down"), ("whisk-hanger-mounted.png", "Reaches 150 mm from the wall"), ("whisk-hanger-side.png", "Two saddles, two posts, two screws"),
    ("whisk-hanger-print.png", "Prints on its side, no supports")]]
sheet(tiles, 2, os.path.join(d, "whisk-hanger-preview.png"), "Sauna whisk drying arm")
