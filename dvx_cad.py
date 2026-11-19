"""Tiny CAD helpers for the DIVELUX printable sauna accessories.

Needs:  pip install manifold3d trimesh numpy
All dimensions are millimeters. License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold, set_circular_segments

set_circular_segments(96)


def poly(points):
    """2D polygon from a list of (x, y) points."""
    return CrossSection([[(float(x), float(y)) for x, y in points]])


def rect(x0, y0, x1, y1):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def circle(r, x=0.0, y=0.0):
    return CrossSection.circle(r).translate((x, y))


def rounded(cs, r):
    """Round convex corners of a 2D shape with radius r."""
    return cs.offset(-r, JoinType.Round).offset(r, JoinType.Round)


def filleted(cs, r):
    """Fill concave corners of a 2D shape with radius r."""
    return cs.offset(r, JoinType.Round).offset(-r, JoinType.Round)


def clean(cs, eps=0.03):
    """Remove hairline slivers and pinch points (open, then close, by eps)."""
    return (cs.offset(-eps, JoinType.Round).offset(2 * eps, JoinType.Round)
            .offset(-eps, JoinType.Round).simplify(0.002))


def stroke(points, r):
    """Thick rounded line (radius r) through a list of 2D points."""
    out = None
    for a, b in zip(points[:-1], points[1:]):
        seg = CrossSection.batch_hull([circle(r, *a), circle(r, *b)])
        out = seg if out is None else out + seg
    return clean(out)


def arc(cx, cy, r, a0, a1, n=40):
    """Points on an arc, angles in degrees."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def to_trimesh(man):
    m = man.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:, :3],
                         faces=np.asarray(m.tri_verts), process=True)
    return tm


def export(man, folder, name):
    """Write <folder>/stl/<name>.stl and <folder>/3mf/<name>.3mf, return the trimesh."""
    tm = to_trimesh(man)
    for ext in ("stl", "3mf"):
        os.makedirs(os.path.join(folder, ext), exist_ok=True)
        tm.export(os.path.join(folder, ext, f"{name}.{ext}"))
    # re-read the STL the way a slicer would, so the check covers the file itself
    return trimesh.load(os.path.join(folder, "stl", f"{name}.stl"))


def report(name, tm):
    size = tm.bounds[1] - tm.bounds[0]
    print(f"{name:34s} watertight={tm.is_watertight} winding={tm.is_winding_consistent} "
          f"bodies={tm.body_count} size={size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm "
          f"volume={tm.volume / 1000:.1f} cm3 faces={len(tm.faces)}")
