#!/usr/bin/env python3
"""Set text in the face without needing it installed — the logo generator and
the specimen both draw from the same contours the font is built from."""
import glyphs


def glyph_svg(name, scale=1.0, dx=0.0, dy=0.0, flip=True):
    """One glyph as SVG path data. flip turns font coordinates (y up) into SVG
    coordinates (y down) about the baseline."""
    cs, _ = glyphs.build(name)
    s = scale
    fn = (lambda p: (dx + p[0] * s, dy - p[1] * s)) if flip else (lambda p: (dx + p[0] * s, dy + p[1] * s))
    return " ".join(c.transform(fn).svg() for c in cs)


def word(text, cap_height, tracking=0.0, x=0.0, y=0.0, flip=True, alt=()):
    """Outlined caps sitting on the baseline y. `tracking` is in em.

    Returns (path data, advance). Mirrors Face.word() in build-antinode.py so
    the two generators stay interchangeable.
    """
    s = cap_height / glyphs.CAP
    track = tracking * glyphs.UPEM * s
    d, pen = [], x
    for i, ch in enumerate(text):
        name = glyphs.CMAP[ord(ch)]
        if i in alt and name == "E":
            name = "E.alt"
        d.append(glyph_svg(name, s, pen, y, flip))
        pen += glyphs.advance(name) * s + track
    return " ".join(p for p in d if p), pen - x - track


def ink_width(text, cap_height, tracking=0.0, alt=()):
    """Left edge of the first letter's ink to the right edge of the last —
    what a designer measures, not what the advances add up to."""
    s = cap_height / glyphs.CAP
    track = tracking * glyphs.UPEM * s
    pen, lo, hi = 0.0, None, None
    for i, ch in enumerate(text):
        name = glyphs.CMAP[ord(ch)]
        if i in alt and name == "E":
            name = "E.alt"
        cs, _ = glyphs.build(name)
        for c in cs:
            for p in c.points():
                lo = p[0] * s + pen if lo is None else min(lo, p[0] * s + pen)
                hi = p[0] * s + pen if hi is None else max(hi, p[0] * s + pen)
        pen += glyphs.advance(name) * s + track
    return hi - lo, lo
