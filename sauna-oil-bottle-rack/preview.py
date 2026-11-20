"""Preview renders for the oil bottle rack (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import oil_rack as orack
from manifold3d import Manifold
from dvx_cad import to_trimesh, poly
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); AMBER = (150, 84, 40); CAP = (40, 36, 34); LABEL = (240, 232, 214)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
TURN = (0, 0, 180)       # the renderer looks from -y, so turn the front toward the camera


def bottle(dia=25.0, h=52.0):
    """A 10 ml dropper bottle for scale."""
    r = dia / 2
    glass = poly([(0, 0), (r - 1.5, 0), (r, 1.5), (r, h - 8), (r - 6, h), (0, h)]).revolve(48)
    cap = Manifold.cylinder(15, 9, 8.5, 48).translate((0, 0, h))
    label = (Manifold.cylinder(24, r + 0.3, r + 0.3, 48) - Manifold.cylinder(26, r - 1, r - 1, 48).translate((0, 0, -1))).translate((0, 0, 21))
    return glass, cap, label


def scene(count, dia, bd, fill=None):
    rack = orack.oil_rack(count, dia)
    bore = dia + orack.CLEAR
    pitch = bore + orack.WALL
    items = [(to_trimesh(rack.rotate(TURN)), C1)]
    for i in range(count):
        if fill is not None and i not in fill:
            continue
        x = (i - (count - 1) / 2) * pitch
        for m, col in zip(bottle(bd), (AMBER, CAP, LABEL)):
            items.append((to_trimesh(m.translate((x, orack.PLATE_T + bore / 2 + 1.2, orack.FLOOR)).rotate(TURN)), col))
    return items


wall = to_trimesh(Manifold.cube((230, 6, 150)).translate((-115, 0, -40)))
render(scene(5, 30, 28) + [(wall, WALL)], az=24, el=18, size=(1100, 800)).save(os.path.join(d, "oil-rack-mounted.png"))
render(scene(5, 30, 28, fill=()), az=28, el=32, size=(1100, 800)).save(os.path.join(d, "oil-rack-empty.png"))
render(scene(5, 30, 28, fill=(2,)), az=-90, el=0).save(os.path.join(d, "oil-rack-side.png"))
render(scene(6, 26, 25, fill=(0, 1, 2, 4)), az=24, el=24, size=(1100, 800)).save(os.path.join(d, "oil-rack-6x26.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("oil-rack-mounted.png", "Five bottles up to 30 mm"), ("oil-rack-empty.png", "Prints as shown, no supports"),
    ("oil-rack-6x26.png", "Six-cup version for 10 ml bottles"), ("oil-rack-side.png", "Side view")]]
sheet(tiles, 2, os.path.join(d, "oil-rack-preview.png"), "Essential oil bottle rack", tile=(700, 510))
