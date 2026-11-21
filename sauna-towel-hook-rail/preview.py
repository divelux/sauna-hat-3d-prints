"""Preview renders for the towel hook rail (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import towel_rail as tr
from manifold3d import Manifold
from dvx_cad import to_trimesh
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); DARK = (96, 62, 40); PL = (240, 228, 206); WALL = (236, 230, 220)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
UP = (90, 0, 0)          # back on the bed -> on the wall, facing the camera
big = Manifold.cube((400, 400, 60)).translate((-200, -200, 0))


def plate_items(p, z_swap):
    lo = p ^ big.translate((0, 0, z_swap - 60))
    hi = p ^ big.translate((0, 0, z_swap))
    return [(to_trimesh(lo.rotate(UP)), PL), (to_trimesh(hi.rotate(UP)), DARK)]


def scene(names, wall=True):
    r, ps = tr.assembled(len(names), names)
    items = [(to_trimesh(r.rotate(UP)), C1)]
    for p in ps:
        items += plate_items(p, tr.FLOOR_Z + 0.05 + tr.PLATE_T)
    if wall:
        w = len(names) * tr.PITCH
        items.append((to_trimesh(Manifold.cube((w + 60, 150, 4)).translate((-30, -25, -4)).rotate(UP)), WALL))
    return items


render(scene(["DAD", "MOM", "GUEST"]), az=22, el=16, size=(1200, 800)).save(os.path.join(d, "rail-mounted.png"))
render(scene(["DAD", "MOM", "GUEST"], wall=False), az=0, el=0, size=(1200, 650), margin=0.06).save(os.path.join(d, "rail-front.png"))
# side view of one peg: the tip rises so a loop stays on
render(scene(["1"], wall=True), az=-90, el=0, size=(800, 800)).save(os.path.join(d, "rail-side.png"))
# a five-hook rail from three segments, pulled apart
segs = [tr.rail(2, right_joint=True), tr.rail(1, left_joint=True, right_joint=True).translate((2 * tr.PITCH + 14, 0, 0)),
        tr.rail(2, left_joint=True).translate((3 * tr.PITCH + 28, 0, 0))]
render([(to_trimesh(s), C1) for s in segs], az=0, el=50, size=(1400, 650), margin=0.05).save(os.path.join(d, "rail-5-segments.png"))
# a name plate sliding in from the top
r = tr.rail(1)
p = tr.plate("ANNA").translate((0.5 * tr.PITCH, tr.PLATE_LOW + 0.3 + 38, tr.FLOOR_Z + 0.05))
render([(to_trimesh(r.rotate(UP)), C1)] + plate_items(p, tr.FLOOR_Z + 0.05 + tr.PLATE_T), az=30, el=25, size=(800, 900)).save(os.path.join(d, "rail-plate-slide.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("rail-mounted.png", "Three hooks, 210 x 100 mm"), ("rail-plate-slide.png", "Name plates slide in from the top"),
    ("rail-side.png", "The tip of each peg rises 12 mm"), ("rail-5-segments.png", "Five hooks: three segments, jigsaw joints")]]
sheet(tiles, 2, os.path.join(d, "rail-preview.png"), "Towel hook rail with name plates", tile=(700, 480))
