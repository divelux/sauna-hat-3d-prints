"""Preview renders for the phone stand (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import phone_stand as ps
from manifold3d import Manifold
from dvx_cad import rect, rounded, to_trimesh
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); BODY = (52, 52, 56); SCREEN = (30, 34, 44); TIME = (240, 236, 228); CABLE = (235, 235, 232)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
TURN = (0, 0, 180)     # the renderer looks from -y (the front of the stand); turn it to see the back
from dvx_text import text

PT = 9.0
def phone():
    """A 75 x 155 x 9 mm phone resting on the seat, with a timer on the screen."""
    b = rounded(rect(-37.5, 0, 37.5, 155), 9).extrude(PT)
    scr = rounded(rect(-34.5, 3, 34.5, 152), 7).extrude(0.4).translate((0, 0, -0.2))
    t = text("12:00", 14, max_width=52).mirror((1, 0)).translate((0, 80)).extrude(0.4).translate((0, 0, -0.5))
    tilt = (ps.ANGLE - 90, 0, 0)          # stand the phone up and lean it back against the support
    place = lambda m: m.translate((0, 0, -PT)).rotate((90, 0, 0)).rotate((0, 0, 180)).rotate((-(90 - ps.ANGLE), 0, 0)).translate((0, ps.Y0, ps.SEAT_Z + 0.2))
    return place(b), place(scr), place(t)


def cable():
    pts = [(0, ps.Y0 - PT / 2 - 0.5, ps.SEAT_Z - 1), (0, ps.Y0 - PT / 2 - 0.5, ps.BASE_T + 2.5), (0, ps.Y0 + 6, ps.BASE_T + 2.0),
           (0, ps.DEPTH + 25, ps.BASE_T + 2.0), (0, ps.DEPTH + 40, 2.0)]
    out = None
    for a, b in zip(pts[:-1], pts[1:]):
        seg = Manifold.batch_hull([Manifold.sphere(2.0, 24).translate(a), Manifold.sphere(2.0, 24).translate(b)])
        out = seg if out is None else out + seg
    plug = Manifold.cube((11, 6.5, 22)).translate((-5.5, ps.Y0 - PT / 2 - 3.75, ps.SEAT_Z - 21))
    return out + plug


s = ps.stand()
b, scr, t = phone()
full = [(to_trimesh(s), C1), (to_trimesh(b), BODY), (to_trimesh(scr), SCREEN),
        (to_trimesh(t), TIME), (to_trimesh(cable()), CABLE)]
render(full, az=28, el=16, size=(900, 1000)).save(os.path.join(d, "stand-with-phone.png"))
render([(to_trimesh(s), C1)], az=30, el=22).save(os.path.join(d, "stand-front.png"))
render([(to_trimesh(s.rotate(TURN)), C1), (to_trimesh(cable().rotate(TURN)), CABLE)], az=30, el=28).save(os.path.join(d, "stand-back.png"))
render([(to_trimesh(s.rotate(TURN)), C1), (to_trimesh(b.rotate(TURN)), BODY), (to_trimesh(cable().rotate(TURN)), CABLE)], az=90, el=0).save(os.path.join(d, "stand-side.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("stand-with-phone.png", "A phone up to 15 mm thick, at 65 degrees"), ("stand-front.png", "One part, prints as shown"),
    ("stand-back.png", "The cable drops through the seat, out the back"), ("stand-side.png", "Side view")]]
sheet(tiles, 2, os.path.join(d, "stand-preview.png"), "Changing-room phone stand", tile=(700, 700))
