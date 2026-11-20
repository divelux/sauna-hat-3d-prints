"""Preview renders for the bucket and ladle rack (not needed for printing)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import bucket_rack as br
from manifold3d import Manifold
from dvx_cad import to_trimesh, circle, poly, arc, stroke
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); WALL = (236, 230, 220); WOODK = (150, 104, 66); STEEL = (150, 152, 158); COPPER = (196, 122, 78)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
UP = (90, 0, 0)          # plate on the bed -> on the wall, facing the camera
r = br.bucket_rack()
rt = to_trimesh(r.rotate(UP))
wall = to_trimesh(Manifold.cube((330, 6, 330)).translate((-165, 0, -230)))

# ladle lying across the two forks (handle 22 mm, 400 mm long, bowl on the right)
hr = 11.0
ly = br.FORK_Y + hr / math.tan(math.radians(br.ARM_ANGLE / 2)) + 3      # where a round handle settles in the V
handle = Manifold.cylinder(330, hr, hr, 48).rotate((0, 90, 0)).translate((-190, ly, br.PLATE_T + hr))
bowl = (Manifold.sphere(42, 48) - Manifold.sphere(39, 48).translate((0, 0, 2))
        - Manifold.cube((100, 100, 60)).translate((-50, -50, 0))).scale((1, 1, 0.75))
bowl = bowl.rotate((-90, 0, 0)).translate((165, ly - 36, br.PLATE_T + hr + 26))
neck = Manifold.cylinder(46, 4, 4, 24).rotate((90, 0, 0)).translate((140, ly + 4, br.PLATE_T + hr))
# bucket handle: wooden grip on the hook and a wire bail going down to the bucket
gr = 14.0
gy = br.HOOK_Y + gr / math.tan(math.radians(br.ARM_ANGLE / 2)) + 4
grip = Manifold.cylinder(110, gr, gr, 48).rotate((0, 90, 0)).translate((-55, gy, br.PLATE_T + gr))
bail_pts = [(-130, gy - 150), (-128, gy - 60)] + arc(-98, gy - 30, 30, 180, 90, 12) + [(98, gy)] + arc(98, gy - 30, 30, 90, 0, 12) + [(128, gy - 60), (130, gy - 150)]
bail = stroke(bail_pts, 3.0).extrude(6).translate((0, 0, br.PLATE_T + gr - 3))
rim = (Manifold.cylinder(60, 134, 128, 96) - Manifold.cylinder(62, 124, 118, 96).translate((0, 0, -1))).rotate((90, 0, 0)).translate((0, gy - 150, br.PLATE_T + 134 + 2))
mock = [(to_trimesh(m.rotate(UP)), c) for m, c in ((handle, WOODK), (bowl, COPPER), (neck, COPPER), (grip, WOODK), (bail, STEEL))]
render([(rt, C1), (wall, WALL)] + mock, az=26, el=14).save(os.path.join(d, "rack-in-use.png"))
wall2 = to_trimesh(Manifold.cube((240, 6, 170)).translate((-120, 0, -110)))
render([(rt, C1), (wall2, WALL)], az=30, el=16, size=(1100, 800)).save(os.path.join(d, "rack-mounted.png"))
render([(rt, C1)] + mock[:1] + mock[3:4], az=-90, el=0).save(os.path.join(d, "rack-side.png"))
render([(to_trimesh(r), C1)], az=25, el=38, size=(1100, 800)).save(os.path.join(d, "rack-print.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("rack-in-use.png", "Bucket handle on the hook, ladle across the forks"), ("rack-mounted.png", "200 x 124 mm plate, four screws"),
    ("rack-side.png", "Side view: handles settle into the V"), ("rack-print.png", "Prints plate-down, arms at 45 degrees")]]
sheet(tiles, 2, os.path.join(d, "rack-preview.png"), "Sauna bucket and ladle rack")
