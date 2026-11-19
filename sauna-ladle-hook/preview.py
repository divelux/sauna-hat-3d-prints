"""Preview renders for the ladle hook (not needed for printing)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import ladle_hook as lh
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image
C1 = (214, 170, 120); WALL = (236, 230, 220)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
h = lh.ladle_hook()
T = np.eye(4); T[:3, :3] = np.array([[0, 0, 1], [-1, 0, 0], [0, 1, 0]]); T[0, 3] = -lh.WIDTH / 2
m = to_trimesh(h); m.apply_transform(T)
wall = to_trimesh(Manifold.cube((120, 6, 150)).translate((-60, 0, -25)))
render([(m, C1), (wall, WALL)], az=40, el=15).save(os.path.join(d, "ladle-hook-mounted.png"))
render([(m, C1)], az=90, el=0).save(os.path.join(d, "ladle-hook-side.png"))
render([(to_trimesh(h), C1)], az=25, el=35).save(os.path.join(d, "ladle-hook-print.png"))
tiles = [(Image.open(os.path.join(d, f)), c) for f, c in [
    ("ladle-hook-mounted.png", "Two screws into a stud or batten"), ("ladle-hook-side.png", "30 mm opening"),
    ("ladle-hook-print.png", "Prints on its side, no supports")]]
sheet(tiles, 3, os.path.join(d, "ladle-hook-preview.png"), "Sauna ladle and bucket hook", tile=(560, 560))
