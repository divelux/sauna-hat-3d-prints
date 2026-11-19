"""Small software renderer (numpy z-buffer, orthographic) for preview images. No GPU needed."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (246, 243, 238)
import os
FONT_B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_fonts", "BricolageGrotesque-Bold.ttf")


def _rot(az, el):
    az, el = math.radians(az), math.radians(el)
    rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    # camera looks along -y after rotating; tilt by elevation about x
    rx = np.array([[1, 0, 0], [0, math.cos(el), -math.sin(el)], [0, math.sin(el), math.cos(el)]])
    return rx @ rz


def render(items, az=35, el=25, size=(900, 900), ss=2, margin=0.08, edges=True):
    """items: list of (trimesh, (r,g,b)). Returns PIL image."""
    W, H = size[0] * ss, size[1] * ss
    R = _rot(az, el)
    allv = []
    prepared = []
    for tm, col in items:
        v = tm.vertices @ R.T          # x right, y depth (toward +y = away), z up
        prepared.append((v, tm.faces, col))
        allv.append(v)
    allv = np.vstack(allv)
    lo, hi = allv.min(0), allv.max(0)
    scale = (1 - 2 * margin) * min(W / (hi[0] - lo[0]), H / (hi[2] - lo[2]))
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    zbuf = np.full((H, W), np.inf)
    img = np.zeros((H, W, 3), dtype=np.float32)
    img[:] = BG
    idbuf = np.full((H, W), -1, dtype=np.int32)
    nbuf = np.zeros((H, W, 3), dtype=np.float32)
    light = np.array([-0.45, -0.55, 0.75]); light /= np.linalg.norm(light)
    fill = np.array([0.6, -0.3, 0.3]); fill /= np.linalg.norm(fill)
    for oid, (v, faces, col) in enumerate(prepared):
        px = (v[:, 0] - cx) * scale + W / 2
        py = H / 2 - (v[:, 2] - cz) * scale
        d = v[:, 1]
        tri = v[faces]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1
        n = n / ln[:, None]
        col = np.array(col, dtype=np.float32)
        for fi, f in enumerate(faces):
            nn = n[fi]
            if nn[1] > 0:      # back face (normal pointing away from camera at -y)
                continue
            x0, x1, x2 = px[f]; y0, y1, y2 = py[f]
            minx = max(int(math.floor(min(x0, x1, x2))), 0); maxx = min(int(math.ceil(max(x0, x1, x2))), W - 1)
            miny = max(int(math.floor(min(y0, y1, y2))), 0); maxy = min(int(math.ceil(max(y0, y1, y2))), H - 1)
            if minx > maxx or miny > maxy:
                continue
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-12:
                continue
            xs = np.arange(minx, maxx + 1) + 0.5
            ys = np.arange(miny, maxy + 1) + 0.5
            X, Y = np.meshgrid(xs, ys)
            w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
            w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            depth = w0 * d[f[0]] + w1 * d[f[1]] + w2 * d[f[2]]
            sub = zbuf[miny:maxy + 1, minx:maxx + 1]
            m = inside & (depth < sub)
            if not m.any():
                continue
            sub[m] = depth[m]
            sh = 0.42 + 0.5 * max(0.0, float(nn @ light)) + 0.16 * max(0.0, float(nn @ fill))
            img[miny:maxy + 1, minx:maxx + 1][m] = np.clip(col * sh, 0, 255)
            idbuf[miny:maxy + 1, minx:maxx + 1][m] = oid
            nbuf[miny:maxy + 1, minx:maxx + 1][m] = nn
    if edges:
        e = np.zeros((H, W), dtype=bool)
        zb = np.where(np.isinf(zbuf), 1e9, zbuf)
        for ax in (0, 1):
            dn = np.abs(np.diff(nbuf, axis=ax)).sum(-1) > 0.5
            dz = np.abs(np.diff(zb, axis=ax)) > 2.0
            di = np.diff(idbuf, axis=ax) != 0
            ee = dn | dz | di
            if ax == 0:
                e[1:, :] |= ee; e[:-1, :] |= ee
            else:
                e[:, 1:] |= ee; e[:, :-1] |= ee
        img[e] = img[e] * 0.35
    out = Image.fromarray(img.astype(np.uint8)).resize(size, Image.LANCZOS)
    return out


def sheet(tiles, cols, path, title=None, tile=(700, 700)):
    """tiles: list of (PIL image, caption)."""
    rows = math.ceil(len(tiles) / cols)
    pad, cap, top = 24, 46, (90 if title else 24)
    Wt = cols * tile[0] + (cols + 1) * pad
    Ht = top + rows * (tile[1] + cap + pad)
    im = Image.new("RGB", (Wt, Ht), BG)
    dr = ImageDraw.Draw(im)
    if title:
        dr.text((pad, 26), title, fill=(27, 21, 18), font=ImageFont.truetype(FONT_B, 40))
    f = ImageFont.truetype(FONT_B, 24)
    for i, (t, c) in enumerate(tiles):
        x = pad + (i % cols) * (tile[0] + pad)
        y = top + (i // cols) * (tile[1] + cap + pad)
        im.paste(t.resize(tile, Image.LANCZOS), (x, y))
        dr.text((x + 6, y + tile[1] + 8), c, fill=(61, 51, 44), font=f)
    im.save(path, optimize=True)
