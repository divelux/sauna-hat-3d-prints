"""Preview renders for the door sign (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import door_sign as ds
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

LIGHT = (240, 228, 206); DARK = (96, 62, 40); SLIDE = (214, 170, 120); C1 = (214, 170, 120)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
UP = (90, 0, 0)          # flat on the bed -> on the door, facing the camera
big = Manifold.cube((400, 400, 50)).translate((-200, -200, 0))


def two_color(b):
    """Base as it looks after a filament swap at FLOOR height."""
    lo = b ^ big.translate((0, 0, ds.FLOOR - 50))
    hi = b ^ big.translate((0, 0, ds.FLOOR))
    return [(to_trimesh(lo.rotate(UP)), LIGHT), (to_trimesh(hi.rotate(UP)), DARK)]


for pos, name in ((0.0, "sign-in-use"), (1.0, "sign-free")):
    b, s = ds.assembled(pos)
    render(two_color(b) + [(to_trimesh(s.rotate(UP)), SLIDE)], az=0, el=0, size=(1200, 600), margin=0.06).save(os.path.join(d, name + ".png"))
b, s = ds.assembled(0.0)
render(two_color(b) + [(to_trimesh(s.rotate(UP)), SLIDE)], az=28, el=18, size=(1200, 700)).save(os.path.join(d, "sign-angle.png"))
# one color, slider on its way in from the open end
s2 = ds.slider().translate((ds.LENGTH / 2 + 12, 0, ds.RIDE + 0.05))
render([(to_trimesh(ds.base().rotate(UP)), C1), (to_trimesh(s2.rotate(UP)), DARK)], az=-30, el=20, size=(1200, 700)).save(os.path.join(d, "sign-slide-in.png"))
# print layout
sl = ds.slider().translate((-ds.FIELD_W / 2, -70, 0))
render([(to_trimesh(ds.base()), C1), (to_trimesh(sl), C1)], az=0, el=60, size=(1200, 900)).save(os.path.join(d, "sign-parts.png"))
# close-up of the open end: rails, runner strips, catch
end = ds.base() ^ Manifold.cube((40, 60, 20)).translate((ds.LENGTH / 2 - 40, ds.Y_BOT - 1, -1))
render([(to_trimesh(end), C1)], az=-62, el=32, size=(900, 900)).save(os.path.join(d, "sign-track-detail.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("sign-in-use.png", "Slider left: IN USE"), ("sign-free.png", "Slider right: FREE"),
    ("sign-slide-in.png", "The slider goes in from the open end"), ("sign-parts.png", "Two flat parts, 161 x 73 mm")]]
sheet(tiles, 2, os.path.join(d, "sign-preview.png"), "Sauna door sign with slider", tile=(700, 420))
