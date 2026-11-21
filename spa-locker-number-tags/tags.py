#!/usr/bin/env python3
"""Spa locker number tags: one tag per number, raised digits, a slot for a key ring, coil wristband or elastic.

Prints flat, digits up, no supports; two colors with one filament swap.
Run:  python3 tags.py             (tags 1 to 40: one STL + 3MF per tag, and 3MF print plates of 20 tags)
      python3 tags.py 41 80       (any other range)
License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import trimesh  # noqa: E402
from manifold3d import CrossSection, JoinType  # noqa: E402
from dvx_cad import circle, clean, export, printcheck, rect, rounded, to_trimesh  # noqa: E402
from dvx_text import text  # noqa: E402

# ---------------- parameters (mm) ----------------
FIRST, LAST = 1, 40   # range of numbers
LENGTH = 46.0         # tag length
WIDTH = 30.0          # tag width
BASE = 2.4            # plate thickness (swap filament here for two colors)
UP = 1.0              # digits and border stand this high
DIGIT_CAP = 15.0      # digit height
SLOT_W = 4.5          # slot for the ring or band: width ...
SLOT_L = 14.0         # ... and length (a 25 mm split ring, a coil wristband or 3 mm elastic cord fits)
BORDER_W = 1.6        # raised border line
PREFIX = ""           # text before the number, e.g. "A" for A1, A2 ...
PLATE_COLS, PLATE_ROWS = 4, 5   # tags per print plate in the 3MF plate files (fits 220 x 220)
# -------------------------------------------------


def tag(n):
    """x = along the tag (slot on the left), y = across, z = up."""
    hl, hw = LENGTH / 2, WIDTH / 2
    outline = CrossSection.batch_hull([circle(hw, -hl + hw, 0), rounded(rect(-hl + hw, -hw, hl, hw), 5.0)])
    sx = -hl + 10.0
    slot = rounded(rect(sx - SLOT_W / 2, -SLOT_L / 2, sx + SLOT_W / 2, SLOT_L / 2), SLOT_W / 2 - 0.01)
    body = clean(outline - slot).extrude(BASE)
    border = outline.offset(-1.6, JoinType.Round) - outline.offset(-1.6 - BORDER_W, JoinType.Round)
    ring = slot.offset(1.6 + BORDER_W, JoinType.Round) - slot.offset(1.6, JoinType.Round)
    field_l, field_r = sx + SLOT_W / 2 + 4.0, hl - 4.5
    label = text(f"{PREFIX}{n}", DIGIT_CAP, tracking=0.6, max_width=field_r - field_l)
    label = label.translate(((field_l + field_r) / 2, -DIGIT_CAP / 2))
    raised = clean(border + ring + label)
    return body + raised.extrude(UP + 0.5).translate((0, 0, BASE - 0.5))


def plate_files(first, last):
    """3MF print plates, each holding up to PLATE_COLS x PLATE_ROWS separate tags."""
    per = PLATE_COLS * PLATE_ROWS
    nums = list(range(first, last + 1))
    out = []
    for k in range(0, len(nums), per):
        group = nums[k:k + per]
        scene = trimesh.Scene()
        for i, n in enumerate(group):
            c, r = i % PLATE_COLS, i // PLATE_COLS
            x = (c - (PLATE_COLS - 1) / 2) * (LENGTH + 6)
            y = ((PLATE_ROWS - 1) / 2 - r) * (WIDTH + 6)
            scene.add_geometry(to_trimesh(tag(n).translate((x, y, 0))), node_name=f"tag-{n}", geom_name=f"tag-{n}")
        name = f"locker-tags-plate-{group[0]}-{group[-1]}.3mf"
        os.makedirs(os.path.join(HERE, "3mf"), exist_ok=True)
        scene.export(os.path.join(HERE, "3mf", name))
        ext = scene.bounds[1] - scene.bounds[0]
        out.append((name, len(group), ext))
    return out


if __name__ == "__main__":
    if len(sys.argv) == 3:
        FIRST, LAST = int(sys.argv[1]), int(sys.argv[2])
    bad = 0
    for n in range(FIRST, LAST + 1):
        ok = printcheck(f"locker-tag-{n}", export(tag(n), HERE, f"locker-tag-{n}"))
        bad += not ok
    for name, count, ext in plate_files(FIRST, LAST):
        print(f"{name}: {count} tags, plate area {ext[0]:.0f} x {ext[1]:.0f} mm")
    print(f"{LAST - FIRST + 1} tags, {bad} with problems")
