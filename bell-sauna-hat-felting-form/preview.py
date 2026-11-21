"""Preview renders for the felting form (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import form as fm
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

COLS = [(214, 170, 120), (226, 190, 146), (200, 156, 108)]
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
parts = fm.form_parts()
render([(to_trimesh(p), c) for p, c in zip(parts, COLS)], az=30, el=15, size=(900, 900)).save(os.path.join(d, "form-assembled.png"))
gap = [0, 45, 90]
render([(to_trimesh(p.translate((0, 0, g))), c) for p, c, g in zip(parts, COLS, gap)], az=30, el=22, size=(900, 900)).save(os.path.join(d, "form-exploded.png"))
cut = Manifold.cube((400, 400, 400)).translate((-400, -200, -1))
render([(to_trimesh(p ^ cut), c) for p, c in zip(parts, COLS)], az=-62, el=12, size=(900, 900)).save(os.path.join(d, "form-section.png"))
zs = [0.0] + fm.SPLITS
row = [(to_trimesh(p.translate((0, 0, -z)).translate((x, 0, 0))), c) for p, z, x, c in zip(parts, zs, (-215, 0, 195), COLS)]
render(row, az=0, el=38, size=(1350, 900)).save(os.path.join(d, "form-print-parts.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("form-assembled.png", "610 mm around the brim line, 200 mm tall"), ("form-exploded.png", "Three parts with stepped joints"),
    ("form-section.png", "Cut through: hollow, screw lugs inside"), ("form-print-parts.png", "Each part fits a 220 x 220 bed")]]
sheet(tiles, 2, os.path.join(d, "form-preview.png"), "Felting form for a bell sauna hat", tile=(700, 700))
