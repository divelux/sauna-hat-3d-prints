"""Preview renders for the hat name tags (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import name_tags as nt
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

LIGHT = (240, 228, 206); DARK = (96, 62, 40); C1 = (214, 170, 120); FELT = (150, 152, 158)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
UP = (90, 0, 0)
big = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))


def two_color(m, dx=0.0, dz=0.0):
    """A tag as it looks after a filament swap at TAG_T."""
    lo = (m ^ big.translate((0, 0, nt.TAG_T - 50))).rotate(UP).translate((dx, 0, dz))
    hi = (m ^ big.translate((0, 0, nt.TAG_T))).rotate(UP).translate((dx, 0, dz))
    return [(to_trimesh(lo), LIGHT), (to_trimesh(hi), DARK)]


items = []
for i, label in enumerate(nt.RELEASED):
    items += two_color(nt.name_tag(label), dx=(i % 6) * 46, dz=-(i // 6) * 60)
render(items, az=0, el=0, size=(1500, 640), margin=0.04).save(os.path.join(d, "tags-set.png"))
render(two_color(nt.name_tag("GUEST")) , az=20, el=12).save(os.path.join(d, "tag-guest.png"))
render([(to_trimesh(nt.name_tag("A")), C1)], az=25, el=42).save(os.path.join(d, "tag-print.png"))
# on the loop of a hat: the top of a felt hat with its hanging loop, tag hooked on
from dvx_cad import poly, circle
import math
crown = poly([(0, 0), (70, 0), (66, 18), (52, 34), (30, 44), (0, 48)]).revolve(64).translate((0, 0, -60))
strap = ((circle(15) - circle(11)).extrude(9).rotate((90, 0, 0)).rotate((0, 0, 90)).translate((-4.5, 0, -2)))
tag = nt.name_tag("A")
cy = nt.TAG_H + nt.RING_IN - 0.6
# ring around the top of the strap, tag lying on the crown
big2 = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))
out = []
for part, col in ((tag ^ big2.translate((0, 0, nt.TAG_T - 50)), LIGHT), (tag ^ big2.translate((0, 0, nt.TAG_T)), DARK)):
    out.append((to_trimesh(part.translate((0, -cy, 0)).rotate((35, 0, 0)).translate((0, -2, 8))), col))
render([(to_trimesh(crown), FELT), (to_trimesh(strap), FELT)] + out, az=28, el=14).save(os.path.join(d, "tag-on-hat.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("tag-guest.png", "Two colors with one filament swap"), ("tag-on-hat.png", "Hangs on the loop of the hat"),
    ("tag-print.png", "38 x 52 x 3.2 mm, prints flat")]]
sheet(tiles, 3, os.path.join(d, "tags-preview.png"), "Sauna hat name tags", tile=(520, 520))
