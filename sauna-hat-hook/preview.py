"""Preview renders for the hat hooks (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import hook
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); DOOR = (228, 222, 212)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
w = hook.wall_hook()
wall = Manifold.cube((160, 8, 200)).translate((-80, 0, -100))
mounted = w.rotate((90, 0, 0))
render([(to_trimesh(mounted), C1), (to_trimesh(wall), WALL)], az=40, el=15).save(os.path.join(d, "wall-hook-mounted.png"))
render([(to_trimesh(mounted), C1)], az=90, el=0).save(os.path.join(d, "wall-hook-side.png"))
render([(to_trimesh(w), C1)], az=30, el=30).save(os.path.join(d, "wall-hook-print.png"))
dh = hook.door_hook()
# mounted: profile x = out from the door, y = up, z = width  ->  world: out = -Y (toward camera), up = Z, width = X
import numpy as np
T = np.eye(4); T[:3, :3] = np.array([[0, 0, 1], [-1, 0, 0], [0, 1, 0]]); T[0, 3] = -hook.HOOK_W / 2
mt = to_trimesh(dh); mt.apply_transform(T)
door = to_trimesh(Manifold.cube((180, hook.DOOR_T - 0.6, 220)).translate((-90, 0.3, -220)))
import trimesh
render([(mt, C1), (door, DOOR)], az=40, el=18).save(os.path.join(d, "door-hook-mounted.png"))
render([(mt, C1), (door, DOOR)], az=90, el=0).save(os.path.join(d, "door-hook-side.png"))
render([(to_trimesh(dh), C1)], az=25, el=35).save(os.path.join(d, "door-hook-print.png"))
tiles = [(Image.open(os.path.join(d, f)), c) for f, c in [
    ("wall-hook-mounted.png", "Wall hook: 70 mm cap, two screws"), ("wall-hook-side.png", "Side view"),
    ("wall-hook-print.png", "Prints plate-down, no supports"),
    ("door-hook-mounted.png", "Over-the-door hook"), ("door-hook-side.png", "Side view on a 35 mm door"),
    ("door-hook-print.png", "Prints on its side, no supports")]]
sheet(tiles, 3, os.path.join(d, "hook-preview.png"), "Sauna hat hooks", tile=(560, 560))
