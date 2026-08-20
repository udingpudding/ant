#!/usr/bin/env python3
"""Cut ANTINODE to OTF, TTF and WOFF2.

The outlines come from glyphs.py, which draws them as skeletons under one pen.
Nothing here is hand-placed: change the pen or the width in glyphs.py and the
whole face re-cuts, the wordmark with it.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphs
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "font")

FAMILY = "Antinode"
STYLE = "Regular"
VERSION = "1.000"
DESIGNER = "Uday Sapra"
DESCRIPTION = ("A monoline geometric face drawn for the ANTINODE mark. Its N is an "
               "arch — the standing wave's lobe one size down — and its A is "
               "that same arch with a bar, which is why the wordmark never has to "
               "write one.")

ORDER = [".notdef", "space"] + [n for n in glyphs.GLYPHS if n != "space"]

# The face is drawn to be set with air around it, so it barely kerns: A, N, U
# and the bowls all stand on vertical sides. Only the open forms need help.
KERN = [("L", "T", -55), ("L", "V", -50), ("L", "W", -50), ("L", "Y", -55),
        ("T", "period", -70), ("T", "comma", -70), ("V", "period", -60),
        ("W", "period", -55), ("Y", "period", -70), ("Y", "comma", -70),
        ("F", "period", -60), ("P", "period", -60), ("T", "A", -25),
        ("A", "T", -25), ("A", "V", -20), ("V", "A", -20)]

FEA = """
feature ss01 {
    sub E by E.alt;
} ss01;

feature kern {
%s
} kern;
""" % "\n".join(f"    pos {a} {b} {v};" for a, b, v in KERN)


def contours(name):
    return glyphs.build(name)[0] if name != ".notdef" else glyphs.g_notdef()


def draw(name, pen):
    for c in contours(name):
        c.draw(pen)


def build():
    os.makedirs(OUT, exist_ok=True)
    widths = {n: (glyphs.advance(n) if n in glyphs.GLYPHS else glyphs.ADV) for n in ORDER}

    worst = 0.0
    for n in glyphs.GLYPHS:
        worst = max(worst, glyphs.build(n)[1])
    assert worst < 0.5, f"curve fit drifted to {worst:.3f} units"

    # ---- OTF (CFF). PostScript wants the opposite winding to the one the
    # glyphs are drawn in, so every contour is reversed on the way out.
    fb = FontBuilder(glyphs.UPEM, isTTF=False)
    fb.setupGlyphOrder(ORDER)
    fb.setupCharacterMap(glyphs.CMAP)
    cs = {}
    for n in ORDER:
        p = T2CharStringPen(widths[n], None)
        draw(n, ReverseContourPen(p))
        cs[n] = p.getCharString()
    fb.setupCFF(f"{FAMILY}-{STYLE}", {"FullName": f"{FAMILY} {STYLE}",
                                      "FamilyName": FAMILY, "Weight": STYLE,
                                      "version": VERSION}, cs, {})
    _common(fb, widths)
    otf = os.path.join(OUT, f"{FAMILY}-{STYLE}.otf")
    fb.save(otf)

    # ---- TTF (glyf). Cubics become quadratics; 0.1 units of tolerance is a
    # seventh of a thousandth of the em, well under the fitting error already
    # accepted upstream.
    fb = _ttf()
    ttf = os.path.join(OUT, f"{FAMILY}-{STYLE}.ttf")
    fb.save(ttf)

    # ---- WOFF2, for the page
    f = TTFont(ttf)
    f.flavor = "woff2"
    woff = os.path.join(OUT, f"{FAMILY}-{STYLE}.woff2")
    f.save(woff)

    clean = _dedup(ttf, otf)
    verify(otf, ttf)
    for p in (otf, ttf, woff):
        print(f"  {os.path.basename(p):26s} {os.path.getsize(p) / 1024:6.1f}KB")
    print(f"  {len(ORDER)} glyphs · {len(glyphs.CMAP)} cmap entries · "
          f"worst curve fit {worst:.3f} units · overlaps "
          f"{'removed' if clean else 'left to nonzero winding'}")
    return worst, clean


def _ttf():
    """The quadratic cut, in memory. Shared by the file build and by the bench,
    which needs the face at several curve exponents at once."""
    widths = {n: (glyphs.advance(n) if n in glyphs.GLYPHS else glyphs.ADV) for n in ORDER}
    fb = FontBuilder(glyphs.UPEM, isTTF=True)
    fb.setupGlyphOrder(ORDER)
    fb.setupCharacterMap(glyphs.CMAP)
    gl = {}
    for n in ORDER:
        tp = TTGlyphPen(None)
        draw(n, Cu2QuPen(tp, 0.1))
        gl[n] = tp.glyph()
    fb.setupGlyf(gl)
    _common(fb, widths)
    return fb


def woff2_at(exponent):
    """The face recut at a different curve exponent, as WOFF2 bytes. The bench
    switches between these live, because the exponent is the one control that
    cannot be faked with CSS."""
    import io
    prev = glyphs.ARCH_N
    glyphs.ARCH_N = exponent
    glyphs._cache.clear()
    glyphs.TAB = None
    try:
        fb = _ttf()
        buf = io.BytesIO()
        fb.save(buf)
        f = TTFont(buf)
        f.flavor = "woff2"
        out = io.BytesIO()
        f.save(out)
        return out.getvalue()
    finally:
        glyphs.ARCH_N = prev
        glyphs._cache.clear()
        glyphs.TAB = None


def _common(fb, widths):
    fb.setupHorizontalMetrics({n: (widths[n], _lsb(n)) for n in ORDER})
    fb.setupHorizontalHeader(ascent=glyphs.ASC, descent=glyphs.DESC, lineGap=0)
    fb.setupNameTable({
        "familyName": FAMILY, "styleName": STYLE,
        "uniqueFontIdentifier": f"{DESIGNER}: {FAMILY} {STYLE}: {VERSION}",
        "fullName": f"{FAMILY} {STYLE}", "psName": f"{FAMILY}-{STYLE}",
        "version": f"Version {VERSION}", "designer": DESIGNER,
        "description": DESCRIPTION, "copyright": f"© {DESIGNER}. All rights reserved.",
    })
    fb.setupOS2(sTypoAscender=glyphs.ASC, sTypoDescender=glyphs.DESC, sTypoLineGap=0,
                usWinAscent=glyphs.ASC, usWinDescent=-glyphs.DESC,
                sCapHeight=glyphs.CAP, sxHeight=glyphs.CAP, achVendID="UDSA",
                fsType=0, usWeightClass=300, usWidthClass=5)
    fb.setupPost(isFixedPitch=0)
    fb.addOpenTypeFeatures(FEA)


def _lsb(name):
    cs = contours(name)
    xs = [p[0] for c in cs for p in c.points()]
    return round(min(xs)) if xs else 0


def _dedup(*paths):
    """Overlap removal needs skia-pathops. Try for it; if it is not there the
    fonts still render — nonzero winding unions same-direction contours — but
    say so rather than claiming a clean production cut."""
    try:
        from fontTools.ttLib.removeOverlaps import removeOverlaps
    except ImportError:
        try:
            r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                                "--timeout", "15", "skia-pathops"],
                               capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            return False
        if r.returncode != 0:
            return False
        try:
            from fontTools.ttLib.removeOverlaps import removeOverlaps
        except ImportError:
            return False
    for p in paths:
        f = TTFont(p)
        removeOverlaps(f)
        f.save(p)
    return True


def verify(otf, ttf):
    """Every mapped codepoint must land on a glyph that actually has ink."""
    for path in (otf, ttf):
        f = TTFont(path)
        gs = f.getGlyphSet()
        cmap = f.getBestCmap()
        assert len(cmap) == len(glyphs.CMAP), f"{path}: cmap lost entries"
        for cp, name in cmap.items():
            assert name in gs, f"{path}: U+{cp:04X} -> missing {name}"
            if name == "space":
                continue
            from fontTools.pens.boundsPen import BoundsPen
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            assert bp.bounds, f"{path}: U+{cp:04X} ({name}) draws nothing"
        assert "GSUB" in f and "GPOS" in f, f"{path}: features missing"
        assert f["OS/2"].sCapHeight == glyphs.CAP


if __name__ == "__main__":
    build()
