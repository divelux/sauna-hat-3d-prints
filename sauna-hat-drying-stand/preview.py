"""Preview renders for the drying stand (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import stand
from dvx_cad import to_trimesh, poly
from render import render, sheet

WOOD = (214, 170, 120); WOOD2 = (190, 140, 92); BASE = (120, 82, 52); FELT = (150, 152, 158)
a, b, c = [to_trimesh(m) for m in stand.assembled()]
asm = [(a, WOOD), (b, WOOD2), (c, BASE)]

# a simple bell hat (24 in circumference, 4.5 mm felt) for scale, cut open to show the stand inside
R = 610 / math.pi / 2
n = 48
outer = []
for i in range(n + 1):
    t = i / n                                  # 0 = top of the crown, 1 = brim
    y = 205 * (1 - t) ** 1.0
    r = R * (1 - (1 - t) ** 2.4) ** 0.5 + 5 * t ** 8
    outer.append((r, y))
inner = [(max(r - 4.5, 0.0), min(y, 200.5)) for r, y in outer]
ring = outer[1:] + inner[:0:-1] + [(0, 200.5), (0, 205)]
cs = poly(ring)
if cs.area() <= 0:
    cs = poly(ring[::-1])
hat = cs.revolve(96, 250).rotate((0, 0, 295)).translate((0, 0, 3.5))
hat_full = cs.revolve(96).translate((0, 0, 3.5))
print("hat volume cm3", hat_full.volume() / 1000)
hat_tm, hat_full_tm = to_trimesh(hat), to_trimesh(hat_full)

d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
render(asm, az=30, el=22).save(os.path.join(d, "stand-assembled.png"))
render(asm, az=75, el=55).save(os.path.join(d, "stand-top.png"))
render(asm + [(hat_tm, FELT)], az=30, el=18).save(os.path.join(d, "stand-with-hat-cutaway.png"))
render([(c, BASE), (hat_full_tm, FELT)], az=30, el=18).save(os.path.join(d, "stand-with-hat.png"))
# exploded
import trimesh
a2 = a.copy(); a2.apply_translation((0, 0, 95)); b2 = b.copy(); b2.apply_translation((0, 0, 35))
render([(a2, WOOD), (b2, WOOD2), (c, BASE)], az=30, el=20).save(os.path.join(d, "stand-exploded.png"))
# print layout
ra = to_trimesh(stand.rib("A")); rb = to_trimesh(stand.rib("B")); rb.apply_translation((185, 0, 0))
bs = to_trimesh(stand.base()); bs.apply_translation((93 + 185 + 190, 95, 0))
render([(ra, WOOD), (rb, WOOD2), (bs, BASE)], az=0, el=65, size=(1400, 700)).save(os.path.join(d, "stand-parts.png"))
from PIL import Image
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("stand-assembled.png", "Assembled: 186 x 186 x 204 mm"), ("stand-with-hat-cutaway.png", "Hat on the stand (cutaway)"),
    ("stand-exploded.png", "Three flat parts, no glue"), ("stand-top.png", "Open to air on all sides")]]
sheet(tiles, 2, os.path.join(d, "stand-preview.png"), "Sauna hat drying stand")
aa, bb, cc = stand.assembled()
print("stand/hat interference mm3:", ((aa + bb) ^ hat_full).volume())
