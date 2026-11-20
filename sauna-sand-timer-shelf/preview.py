"""Preview renders for the sand timer shelf (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import timer_shelf as ts
from manifold3d import Manifold
from dvx_cad import to_trimesh, poly
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); WOODK = (150, 104, 66); GLASS = (205, 220, 226); SAND = (226, 150, 84)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
D = 50
s = ts.timer_shelf(D)
cy = ts.PLATE_T + (D + ts.CLEAR) / 2


def hourglass(dia=50, h=120):
    """A plain cylindrical sand timer for scale: two end caps, three rods, glass."""
    cap = Manifold.cylinder(8, dia / 2, dia / 2, 64)
    rods = None
    for a in (30, 150, 270):
        r = Manifold.cylinder(h - 16, 2.5, 2.5, 24).translate(((dia / 2 - 5) * math.cos(math.radians(a)),
                                                                (dia / 2 - 5) * math.sin(math.radians(a)), 8))
        rods = r if rods is None else rods + r
    frame = cap + cap.translate((0, 0, h - 8)) + rods
    gh, gr = (h - 16) / 2, dia / 2 - 10
    prof = [(0, 0)] + [(gr * math.sin(math.pi * i / 20) ** 0.6 * (1 - 0.82 * (i / 20) ** 3), gh * i / 20) for i in range(1, 21)]
    prof = [(max(x, 2.2), y) if 0 < y else (x, y) for x, y in prof] + [(0, gh)]
    bulb = poly(prof).revolve(48)
    glass = bulb.translate((0, 0, 8)) + bulb.mirror((0, 0, 1)).translate((0, 0, h - 8))
    sand = (bulb ^ Manifold.cylinder(gh * 0.45, dia, dia, 24)).scale((0.9, 0.9, 1)).translate((0, 0, 8.01))
    return frame, glass, sand


# the renderer looks from -y, so turn everything to face the camera
TURN = (0, 0, 180)
frame, glass, sand = [m.translate((0, cy, ts.FLOOR)).rotate(TURN) for m in hourglass(D)]
wall = Manifold.cube((120, 6, 180)).translate((-60, 0, -30))
stm = to_trimesh(s.rotate(TURN))
timer = [(to_trimesh(frame), WOODK), (to_trimesh(glass), GLASS)]
render([(stm, C1), (to_trimesh(wall), WALL)] + timer, az=38, el=16).save(os.path.join(d, "timer-shelf-mounted.png"))
render([(stm, C1)], az=35, el=28).save(os.path.join(d, "timer-shelf-empty.png"))
render([(stm, C1)] + timer, az=90, el=0).save(os.path.join(d, "timer-shelf-side.png"))
render([(stm, C1)], az=0, el=89).save(os.path.join(d, "timer-shelf-top.png"))
row = []
for i, dd in enumerate((40, 50, 60)):
    row.append((to_trimesh(ts.timer_shelf(dd).rotate(TURN).translate((i * 80, 0, 0))), C1))
render(row, az=30, el=30, size=(900, 900)).save(os.path.join(d, "timer-shelf-sizes.png"))
tiles = [(Image.open(os.path.join(d, f)), c) for f, c in [
    ("timer-shelf-mounted.png", "On the wall with a 50 mm sand timer"), ("timer-shelf-empty.png", "Cup, front opening, drain hole"),
    ("timer-shelf-side.png", "Side view"), ("timer-shelf-sizes.png", "Released sizes: 40, 50 and 60 mm")]]
sheet(tiles, 2, os.path.join(d, "timer-shelf-preview.png"), "Sand timer wall shelf")
