"""Preview renders for the locker tags (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import tags as tg
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

COLS = [((240, 228, 206), (96, 62, 40)), ((60, 66, 72), (236, 230, 220)), ((214, 170, 120), (60, 40, 28))]
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
big = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))


def two(m, cols):
    lo = m ^ big.translate((0, 0, tg.BASE - 50)); hi = m ^ big.translate((0, 0, tg.BASE))
    return [(to_trimesh(lo), cols[0]), (to_trimesh(hi), cols[1])]


items = []
for i, n in enumerate([7, 12, 23, 38]):
    items += two(tg.tag(n).rotate((0, 0, -8 + 6 * i)).translate(((i % 2) * 56 - 28, (i // 2) * -38 + 19, 0)), COLS[i % 3])
render(items, az=10, el=55, size=(1050, 800)).save(os.path.join(d, "tags-set.png"))
render(two(tg.tag(17), COLS[0]), az=20, el=35, size=(1050, 800)).save(os.path.join(d, "tag-detail.png"))
plate = []
for i, n in enumerate(range(1, 21)):
    c, r = i % tg.PLATE_COLS, i // tg.PLATE_COLS
    plate.append((to_trimesh(tg.tag(n).translate(((c - 1.5) * (tg.LENGTH + 6), (2 - r) * (tg.WIDTH + 6), 0))), (214, 170, 120)))
render(plate, az=0, el=62, size=(1050, 800)).save(os.path.join(d, "tags-plate.png"))
# a tag on a split ring and a coil band (stand-ins)
ring = Manifold.cylinder(1.4, 13, 13, 96) - Manifold.cylinder(2, 11.6, 11.6, 96).translate((0, 0, -0.3))
ring = ring.rotate((90, 0, 0)).translate((-tg.LENGTH / 2 + 10.0, 0, 1.2 + 11.6))
render(two(tg.tag(5), COLS[1]) + [(to_trimesh(ring), (190, 190, 196))], az=25, el=20, size=(1050, 800)).save(os.path.join(d, "tag-ring.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("tags-set.png", "Two colors with one swap at 2.4 mm"), ("tag-detail.png", "46 x 30 mm, digits 15 mm tall"),
    ("tag-ring.png", "Slot for a split ring, coil band or cord"), ("tags-plate.png", "Print plates of 20 tags (3MF)")]]
sheet(tiles, 2, os.path.join(d, "tags-preview.png"), "Spa locker number tags", tile=(700, 533))
