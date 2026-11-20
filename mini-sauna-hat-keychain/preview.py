"""Preview renders for the mini hat keychain (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import keychain as kc
from manifold3d import Manifold
from dvx_cad import to_trimesh, circle
from render import render, sheet
from PIL import Image

FELT = (150, 152, 158); CREAM = (232, 222, 200); C1 = (214, 170, 120); STEEL = (170, 172, 178)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
h3, hf = kc.hat_3d(), kc.hat_flat()
zc = kc.HAT_H - kc.LOOP_SINK + kc.LOOP_R
# a 25 mm split key ring through the loop
ring = (circle(12.5) - circle(11.0)).extrude(1.6).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((-0.8, 0, zc + 10.5))
render([(to_trimesh(h3), FELT), (to_trimesh(ring), STEEL)], az=35, el=18).save(os.path.join(d, "keychain-3d.png"))
cut = h3 - Manifold.cube((60, 60, 80)).translate((0, -60, -5))
render([(to_trimesh(cut.rotate((0, 0, 35))), FELT)], az=0, el=12).save(os.path.join(d, "keychain-3d-cutaway.png"))
render([(to_trimesh(hf.rotate((90, 0, 0))), CREAM)], az=22, el=14).save(os.path.join(d, "keychain-flat.png"))
both = [(to_trimesh(h3), C1), (to_trimesh(hf.translate((42, -14, 0))), C1)]
render(both, az=25, el=40).save(os.path.join(d, "keychain-print.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("keychain-3d.png", "3D hat, 34 x 42 mm, with a key ring"), ("keychain-3d-cutaway.png", "Hollow inside (cutaway)"),
    ("keychain-flat.png", "Flat tag, 33 x 40 x 3.8 mm"), ("keychain-print.png", "Both print as shown, no supports")]]
sheet(tiles, 2, os.path.join(d, "keychain-preview.png"), "Mini sauna hat keychain", tile=(560, 560))
