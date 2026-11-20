"""Preview renders for the gauge cradle (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import gauge_cradle as gc
from manifold3d import Manifold
from dvx_cad import to_trimesh, rect, circle
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); CASE = (176, 128, 84); DIAL = (245, 240, 228); INK = (60, 50, 44); RED = (200, 70, 40)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
D, DEPTH = 100, 26
UP = (90, 0, 0)          # print orientation -> on the wall, facing the camera


def gauge(dia=D, depth=DEPTH):
    """A plain round gauge for scale: case, dial, tick marks, needle."""
    case = Manifold.cylinder(depth, dia / 2, dia / 2, 96) - Manifold.cylinder(3, dia / 2 - 6, dia / 2 - 6, 96).translate((0, 0, depth - 2))
    dial = Manifold.cylinder(1, dia / 2 - 6, dia / 2 - 6, 96).translate((0, 0, depth - 2.5))
    marks = None
    for i in range(13):
        a = 225 - i * 22.5
        t = rect(dia / 2 - 15, -0.9, dia / 2 - 8, 0.9).rotate(a).extrude(0.8).translate((0, 0, depth - 1.6))
        marks = t if marks is None else marks + t
    needle = (rect(-6, -1.1, dia / 2 - 12, 1.1) + circle(4)).rotate(70).extrude(1.2).translate((0, 0, depth - 1.2))
    return [m.translate((0, 0, gc.BACK_T)) for m in (case, dial, marks, needle)]


c = gc.gauge_cradle(D)
g = gauge()
cols = [CASE, DIAL, INK, RED]
wall = Manifold.cube((170, 6, 170)).translate((-85, 0, -85))
ctm = to_trimesh(c.rotate(UP))
gt = [(to_trimesh(m.rotate(UP)), col) for m, col in zip(g, cols)]
render([(ctm, C1), (to_trimesh(wall), WALL)] + gt, az=28, el=14).save(os.path.join(d, "cradle-with-gauge.png"))
render([(ctm, C1), (to_trimesh(wall), WALL)], az=28, el=14).save(os.path.join(d, "cradle-empty.png"))
lifted = [(to_trimesh(m.translate((0, 62, 0)).rotate(UP)), col) for m, col in zip(g, cols)]
render([(ctm, C1)] + lifted, az=28, el=14).save(os.path.join(d, "cradle-drop-in.png"))
render([(to_trimesh(c), C1)], az=30, el=38).save(os.path.join(d, "cradle-print.png"))
render([(ctm, C1)] + gt, az=-90, el=0).save(os.path.join(d, "cradle-side.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("cradle-with-gauge.png", "100 mm gauge in the cradle"), ("cradle-empty.png", "Open back ring, three screws"),
    ("cradle-drop-in.png", "The gauge drops in from above"), ("cradle-print.png", "Prints back-down, no supports")]]
sheet(tiles, 2, os.path.join(d, "cradle-preview.png"), "Thermometer and hygrometer cradle")
