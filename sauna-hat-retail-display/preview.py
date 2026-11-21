"""Preview renders for the hat display (not needed for printing). The hat is a simple stand-in shape."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import display as dp
from manifold3d import Manifold
from dvx_cad import rect, to_trimesh
from dvx_text import bell_hat
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); FELT = [(150, 150, 146), (176, 112, 82), (226, 218, 200), (92, 104, 96), (60, 58, 62)]
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)


def hat(width=196.0, height=185.0, felt=4.5):
    sil = bell_hat(width, height)
    shell = (sil - sil.offset(-felt)) ^ rect(0, 0.01, 200, 400)
    m = shell.revolve(128)
    return m, height - felt          # the inside top of the crown


def stand(posts, x, y, color):
    parts, top = dp.pedestal(posts)
    h, inner_top = hat()
    items = [(to_trimesh(p.translate((x, y, 0))), C1) for p in parts]
    if color is not None:
        items.append((to_trimesh(h.translate((x, y, top - inner_top))), color))
    return items


# five pedestals, staggered heights, hats on
scene = []
for i, (k, col) in enumerate(zip((1, 2, 3, 2, 1), FELT)):
    scene += stand(k, (i - 2) * 215, (abs(i - 2) * -60), col)
render(scene, az=0, el=12, size=(1600, 900), margin=0.05).save(os.path.join(d, "display-five-hats.png"))
# one pedestal without and with a hat
render(stand(2, 0, 0, None), az=30, el=18, size=(700, 1000)).save(os.path.join(d, "display-pedestal.png"))
render(stand(1, 0, 0, FELT[1]), az=30, el=18, size=(700, 900)).save(os.path.join(d, "display-one-hat.png"))
# the parts, pulled apart
parts = [dp.base(), dp.post().translate((0, 0, dp.BASE_T + 40)), dp.cap().translate((0, 0, dp.BASE_T + dp.POST_L + 80))]
render([(to_trimesh(p), C1) for p in parts], az=30, el=10, size=(700, 1000)).save(os.path.join(d, "display-parts.png"))
# cut through the cap: hollow, 45 degree cone inside
half = dp.cap() ^ Manifold.cube((200, 200, 200)).translate((-200, -100, -1))
render([(to_trimesh(half), C1)], az=-70, el=15, size=(800, 600)).save(os.path.join(d, "display-cap-section.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("display-five-hats.png", "Five pedestals: 1, 2, 3, 2 and 1 posts"), ("display-parts.png", "Base, post, cap: plug together"),
    ("display-cap-section.png", "The cap is hollow and prints without supports"), ("display-one-hat.png", "Lowest pedestal, 228 mm")]]
sheet(tiles, 2, os.path.join(d, "display-preview.png"), "Sauna hat display pedestals", tile=(760, 560))
