"""Preview renders for the cookie cutter (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import cookie_cutter as cc
from manifold3d import Manifold, JoinType
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); DOUGH = (226, 190, 132); TRAY = (120, 118, 116)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
plain, imp = cc.cutter_plain(), cc.cutter_imprint()
render([(to_trimesh(plain), C1)], az=28, el=38).save(os.path.join(d, "cutter-plain.png"))
render([(to_trimesh(imp), C1)], az=28, el=38).save(os.path.join(d, "cutter-imprint.png"))
# the cookie the imprint version makes: outline cut, lines pressed in
shape = cc.outline()
cookie = shape.offset(-0.3, JoinType.Round).extrude(cc.DOUGH)
press = imp.mirror((0, 0, 1)).translate((0, 0, cc.HEIGHT))          # cutter turned edge-down on the table
cookie -= press
render([(to_trimesh(cookie), DOUGH)], az=14, el=52).save(os.path.join(d, "cookie.png"))
render([(to_trimesh(imp.mirror((0, 0, 1)).translate((0, 0, cc.HEIGHT))), C1)], az=28, el=30).save(os.path.join(d, "cutter-in-use.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("cutter-plain.png", "Plain cutter, 85 x 91 x 14 mm"), ("cutter-imprint.png", "Imprint version: brim line and loop"),
    ("cookie.png", "The cookie: about 75 x 81 mm"), ("cutter-in-use.png", "Edge down, press on the rim")]]
sheet(tiles, 2, os.path.join(d, "cutter-preview.png"), "Sauna hat cookie cutter", tile=(560, 560))
