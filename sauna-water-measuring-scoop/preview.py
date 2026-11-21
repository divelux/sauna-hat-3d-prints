"""Preview renders for the measuring scoop (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import scoop as sc
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

C1 = (226, 222, 214); WATER = (120, 170, 205)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
s = sc.scoop()
tm = to_trimesh(s)
water = sc.cavity(sc.LEVELS[1]) ^ Manifold.cylinder(sc.LEVELS[1], sc.RI - 0.05, sc.RI - 0.05, 128)
render([(tm, C1)], az=-62, el=12, size=(800, 900)).save(os.path.join(d, "scoop-numbers.png"))
render([(tm, C1), (to_trimesh(water), WATER)], az=-35, el=42, size=(800, 900)).save(os.path.join(d, "scoop-100ml.png"))
render([(tm, C1)], az=180, el=62, size=(800, 900)).save(os.path.join(d, "scoop-lines-inside.png"))
render([(tm, C1)], az=0, el=0, size=(800, 900)).save(os.path.join(d, "scoop-side.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("scoop-numbers.png", "Lines at 50, 100 and 150 ml"), ("scoop-100ml.png", "Filled to the 100 ml line"),
    ("scoop-lines-inside.png", "The lines are inside too"), ("scoop-side.png", "Prints upright, no supports")]]
sheet(tiles, 2, os.path.join(d, "scoop-preview.png"), "Measuring scoop (not for the hot room)", tile=(620, 700))
