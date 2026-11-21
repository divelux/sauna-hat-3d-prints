"""Printable building blocks used across the DIVELUX sauna accessories.

Every function returns a manifold3d Manifold (3D) or CrossSection (2D) in millimeters. The shapes are designed
to print without supports in the orientation given in each docstring (z = up on the print bed).
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math

from manifold3d import CrossSection, Manifold

from .cad import circle, poly, rect, rounded

SEG = 96


# ---------------- holes ----------------
def countersunk_hole(d=4.4, head_d=8.6, plate_t=6.0, z_top=None):
    """Vertical screw hole through a plate lying on the bed, countersunk (90 degrees) from the top face.
    Subtract it. z_top = height of the top face (default plate_t)."""
    z_top = plate_t if z_top is None else z_top
    sink = (head_d - d) / 2
    hole = Manifold.cylinder(z_top + 2, d / 2, d / 2, 48).translate((0, 0, -1))
    cone = Manifold.cylinder(sink + 0.5, d / 2, head_d / 2 + 0.5, 48).translate((0, 0, z_top - sink))
    return hole + cone


def teardrop_hole(d, length, axis="y"):
    """Horizontal hole with a 45 degree pointed top, so it prints without supports. Centered on the origin,
    running along x or y. Subtract it."""
    r = d / 2
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(-225, 46, 10)]
    pts.append((0, r * math.sqrt(2)))
    m = poly(pts).extrude(length).translate((0, 0, -length / 2)).rotate((90, 0, 0))     # along y
    return m.rotate((0, 0, 90)) if axis == "x" else m


def pilot_hole(d=3.2, depth=14.0):
    """Blind vertical pilot hole for a self-tapping screw, open at z = 0, with a pointed top (no bridge)."""
    return Manifold.cylinder(depth, d / 2, d / 2, 32) + Manifold.cylinder(d / 2, d / 2, 0.01, 32).translate((0, 0, depth))


# ---------------- joints ----------------
def jigsaw_knob(r=8.5, neck=11.0, grow=0.0):
    """2D jigsaw knob pointing to +x from x = 0, centered on y = 0. Cut the socket with grow = clearance
    (0.2 mm) from the neighbour, add the knob with grow = 0. Both parts print flat."""
    n = rect(-1, -neck / 2 - grow, 8.0, neck / 2 + grow)
    return n + circle(r + grow, 8.0 + r * 0.55, 0)


def dovetail_profile(width, depth, lean_deg=30.0, z0=0.0):
    """2D (x, z) trapezoid of a dovetail track: `width` at z0, narrower by tan(lean) per mm going up.
    Extrude it along the track to cut a slot; offset by -clearance for the part that slides in."""
    t = math.tan(math.radians(lean_deg))
    b = width / 2
    return poly([(-b, z0), (b, z0), (b - t * depth, z0 + depth), (-b + t * depth, z0 + depth)])


def spigot_tube(d=24.0, bore=15.0, length=22.0, chamfer=1.0):
    """Vertical spigot tube standing on z = 0, chamfered top. Its socket is a bore of d/2 + 0.25 mm."""
    r, ri = d / 2, bore / 2
    prof = poly([(ri, 0), (r, 0), (r, length - chamfer), (r - chamfer, length), (ri, length)])
    return prof.revolve(SEG)


# ---------------- shapes ----------------
def peg(width=16.0, depth=14.0, length=50.0, lip=12.0, root=4.0):
    """Towel / hat peg standing on z = 0 (glue it onto a plate printed back-down). The tip rises by `lip`
    toward +y at about 48 degrees, so it prints straight up without supports."""
    sec = rounded(rect(-width / 2, -depth / 2, width / 2, depth / 2), 4.0)
    base = rounded(rect(-width / 2 - root, -depth / 2 - root, width / 2 + root, depth / 2 + root), 6.0)
    flare = Manifold.batch_hull([base.extrude(0.01), sec.extrude(0.01).translate((0, 0, 5))])
    z0 = length - lip * 1.1 - 2                       # where the tip starts to rise
    shaft = sec.extrude(z0 + 1.0)                     # overlaps the tip by 1 mm (no coincident faces)
    head = CrossSection.batch_hull([sec, sec.translate((0, lip))])
    top = rounded(rect(-width / 2 + 1, -depth / 2 + 1, width / 2 - 1, depth / 2 + lip - 1), 3.0)
    tip = Manifold.batch_hull([sec.extrude(0.01).translate((0, 0, z0)), head.extrude(0.01).translate((0, 0, length - 2.01)),
                               top.extrude(0.01).translate((0, 0, length - 0.01))])
    return flare + shaft + tip


def cup_cavity(inner_d, top, floor=3.0, fillet=8.0, seg=128):
    """Solid of revolution filling a cup from its inner floor (z = floor) up to z = top, with a rounded
    bottom edge. Subtract it from a cylinder to make a cup; measure it to place volume lines."""
    ri, f = inner_d / 2, fillet
    pts = [(0, floor)]
    for i in range(17):
        a = math.radians(-90 + 90 * i / 16)
        pts.append((ri - f + f * math.cos(a), floor + f + f * math.sin(a)))
    pts += [(ri, top), (0, top)]
    return poly(pts).revolve(seg)


def level_for_volume(ml, inner_d, floor=3.0, fillet=8.0):
    """Height (z, from the bed) of the water surface when the cup holds `ml` milliliters (1 ml = 1000 mm3)."""
    lo, hi = floor, floor + 500
    for _ in range(50):
        mid = (lo + hi) / 2
        v = cup_cavity(inner_d, mid, floor, fillet).volume() if mid > floor else 0.0
        lo, hi = (mid, hi) if v < ml * 1000 else (lo, mid)
    return (lo + hi) / 2


def v_groove_ring(r, z, depth=0.8, inside=True, seg=128):
    """A ring-shaped V groove at height z in a wall of radius r (inside or outside face). The upper face is
    60 degrees from the horizontal, so it prints. Subtract it."""
    up = depth * math.tan(math.radians(60))
    s = 1 if inside else -1
    prof = poly([(r - s * 0.01, z - 0.15), (r + s * depth, z), (r + s * depth, z + 0.15), (r - s * 0.01, z + 0.15 + up)])
    return prof.revolve(seg)


def cone_cavity(base_r, z0=0.0, seg=128):
    """45 degree cone with its base on z0 (open at the bottom), apex base_r above it. Intersect it with the
    inside of a solid printed base-down to hollow it without any internal overhang."""
    return poly([(0, z0 - 1), (base_r + 1, z0 - 1), (0, z0 + base_r)]).revolve(seg)


def gable_ring_cells(r_in, r_out, height, wall=2.0, cells=3):
    """2D (r, z) profiles of `cells` ring-shaped air chambers with 45 degree gable roofs between r_in and r_out,
    leaving `wall` everywhere. Revolve and subtract them from a float to make sealed, support-free chambers."""
    w = (r_out - r_in - (cells - 1) * wall) / cells
    out = None
    for k in range(cells):
        a = r_in + k * (w + wall)
        zr = height - wall - w / 2 - 0.3
        c = poly([(a, wall), (a + w, wall), (a + w, zr), (a + w / 2, zr + w / 2), (a, zr)])
        out = c if out is None else out + c
    return out
