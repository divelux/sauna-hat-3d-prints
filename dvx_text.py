"""Text and small shared shapes for the DIVELUX printable sauna accessories.

Needs:  pip install manifold3d fonttools
Text is turned into 2D outlines from any TrueType font. Set the environment variable DVX_FONT or pass font=...
to use your own .ttf; by default the first font found in FONT_CANDIDATES is used.
All dimensions are millimeters. License: CC BY 4.0 - DIVELUX, https://diveluxsaunahat.com
"""
import os

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from manifold3d import CrossSection, FillRule

from dvx_cad import poly

_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = [
    os.environ.get("DVX_FONT", ""),
    os.path.join(_HERE, "..", "_fonts", "BricolageGrotesque-Bold.ttf"),   # the font used for the released files
    os.path.join(_HERE, "fonts", "BricolageGrotesque-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
_cache = {}


def find_font(font=None):
    for f in ([font] if font else FONT_CANDIDATES):
        if f and os.path.exists(f):
            return f
    raise FileNotFoundError("No .ttf font found. Set DVX_FONT=/path/to/a/bold/font.ttf")


class _FlatPen(BasePen):
    """Collects glyph contours as polylines (curves cut into short straight pieces)."""

    def __init__(self, glyph_set, steps=10):
        super().__init__(glyph_set)
        self.contours, self.cur, self.steps = [], [], steps

    def _moveTo(self, p):
        self._flush()
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
            self.cur.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                             a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))

    def _flush(self):
        if len(self.cur) > 2:
            self.contours.append(self.cur)
        self.cur = []

    _closePath = _endPath = _flush


def text(string, cap_height, font=None, tracking=0.0, align="center", max_width=None):
    """2D outline of a line of text.

    cap_height - height of a capital letter in mm; the baseline is y = 0.
    tracking   - extra space between letters, in mm.
    align      - "center", "left" or "right" (around x = 0).
    max_width  - if set, the text is scaled down evenly to fit this width.
    """
    path = find_font(font)
    if path not in _cache:
        tt = TTFont(path)
        _cache[path] = (tt, tt.getGlyphSet(), tt.getBestCmap())
    tt, glyphs, cmap = _cache[path]
    caps = getattr(tt["OS/2"], "sCapHeight", 0) or 0.7 * tt["head"].unitsPerEm
    k = cap_height / caps
    contours, x = [], 0.0
    for ch in string:
        name = cmap.get(ord(ch))
        if name is None:
            raise ValueError(f"the font has no glyph for {ch!r}")
        pen = _FlatPen(glyphs)
        glyphs[name].draw(pen)
        pen._flush()
        for c in pen.contours:
            contours.append([(x + px * k, py * k) for px, py in c])
        x += glyphs[name].width * k + tracking
    width = x - tracking
    cs = CrossSection(contours, FillRule.NonZero) if contours else CrossSection()
    if max_width and width > max_width:
        s = max_width / width
        cs, width = cs.scale((s, s)), width * s
    shift = {"center": -width / 2, "left": 0.0, "right": -width}[align]
    return cs.translate((shift, 0))


def bell_hat(width, height, flare=0.07, n=64):
    """2D silhouette of a classic bell-shaped sauna hat: brim on y = 0, crown at y = height, centered on x = 0."""
    r0 = width / 2 / (1 + flare)
    half = []
    for i in range(n + 1):
        t = i / n                                   # 0 = top of the crown, 1 = brim
        r = r0 * (1 - (1 - t) ** 2.4) ** 0.5 + r0 * flare * t ** 8
        half.append((r, height * (1 - t)))
    pts = half + [(-x, y) for x, y in half[-1:0:-1]]
    cs = poly(pts)
    return cs if cs.area() > 0 else poly(pts[::-1])
