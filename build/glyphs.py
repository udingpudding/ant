#!/usr/bin/env python3
"""ANTINODE — the alphabet.

Drawn from the sketch's own rules rather than chosen from a library, because
the drawing uses a letter no font ships: its N is an arch, the wave lobe one
size down. Once that N exists the rest of the system follows, and the A never
has to be written at all — the lobe stands in its slot and the axis rule is
its bar.

Every glyph is a skeleton inflated by one pen. Nothing here is a filled shape.
"""
import math
from geom import (Contour, stroke_line, stroke_curve, stroke_closed, ring,
                  ellipse, superellipse_pts, arc_pts)

# ---------------------------------------------------------------- metrics
UPEM = 1000
CAP = 700
W = 66                 # the pen. 0.094 cap, measured off the pencil
GW = 560               # glyph width. the sketch runs 0.77-0.83 cap; 0.80 splits it
SB = 91                # sidebearing. the sketch's letter gap is 0.26 cap
ADV = GW + 2 * SB      # 742
OVER = 11              # round overshoot, 1.6% of cap
ASC, DESC = 760, -190

L, R = SB, SB + GW                 # ink box
XL, XR = L + W / 2, R - W / 2      # stem centrelines
XM = (L + R) / 2
YB, YT = W / 2, CAP - W / 2        # bar centrelines, ink flush to baseline/cap
AX = (XR - XL) / 2                 # half the span between stems

SEGS = 16              # cubic spans per stroked curve; holds the fit under 0.3 units
ARCH_N = 2.5           # superellipse exponent. 2 is an ellipse; above it the
                       # shoulder flattens on top and stands vertical on the stem
SHOULDER = 0.48 * CAP  # ink height of the arch's dome, traced off the sketch's N
NJ = CAP - SHOULDER    # where the dome lands on the legs
BARY = 0.40 * CAP      # the A's bar. in the logo this is the axis
MIDY = 0.50 * CAP      # E, F, H crossbars
E_OPEN = 52.0          # degrees off horizontal to the E's terminals

DESCENDERS = {"comma", "semicolon", "parenleft", "parenright", "Q"}


# ---------------------------------------------------------------- the pen
_err = []


def vstem(x, y0, y1):
    return [stroke_line([(x, y0), (x, y1)], W)]


def hbar(y, x0, x1):
    return [stroke_line([(x0, y), (x1, y)], W)]


def seg(p, q):
    return [stroke_line([p, q], W)]


def path(*pts):
    return [stroke_line(list(pts), W)]


def curve(pts):
    # one cubic span per ~50 units of skeleton, so a long sweep is not fitted
    # more coarsely than a short one
    ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
    c, e = stroke_curve(pts, W, max(SEGS, int(ln / 25)))
    _err.append(e)
    return [c]


def arch(x0, x1, y_join, ink_edge, down=False):
    """The signature curve. Half a superellipse springing from two stems,
    vertical where it meets them. Used at four scales: N, A, U and D's bowl.
    `ink_edge` is where the ink stops, so the dome lands flush on cap or
    baseline whichever way it points."""
    cx, a = (x0 + x1) / 2, (x1 - x0) / 2
    b = (y_join - (ink_edge + W / 2)) if down else ((ink_edge - W / 2) - y_join)
    return curve(superellipse_pts(cx, y_join, a, -b if down else b, ARCH_N, 0, math.pi))


def bowl(x, y_top, y_bot, width):
    """A right-hand bowl hung off a stem: D, B, P, R."""
    cy, b = (y_top + y_bot) / 2, (y_top - y_bot) / 2
    return curve(superellipse_pts(x, cy, width, b, ARCH_N, math.pi / 2, -math.pi / 2))


def se_pts(cx, cy, a, b, t0=0.0, t1=2 * math.pi, steps=600):
    """The face's curve, at any size and any sweep."""
    return superellipse_pts(cx, cy, a, b, ARCH_N, t0, t1, steps)


def sering(cx=None, cy=None, rx=None, ry=None, w=None):
    """The O and its family. Built on the same superellipse as the N's shoulder
    and the D's bowl — a circle here would read as a visitor from another
    alphabet, which is exactly what it did before."""
    cx = XM if cx is None else cx
    cy = CAP / 2 if cy is None else cy
    rx = AX if rx is None else rx
    ry = (CAP / 2 + OVER - W / 2) if ry is None else ry
    o, i, e = stroke_closed(se_pts(cx, cy, rx, ry), W if w is None else w, 28)
    _err.append(e)
    return [o, i]


def ORING(rx=None, ry=None):
    return sering(rx=rx, ry=ry)


def cring(a0, a1, rx=None, ry=None, cx=None, cy=None):
    """An open ring — C, G, S, the E, and the digits' bowls."""
    return curve(se_pts(XM if cx is None else cx,
                        CAP / 2 if cy is None else cy,
                        AX if rx is None else rx,
                        (CAP / 2 + OVER - W / 2) if ry is None else ry,
                        math.radians(a0), math.radians(a1)))


def rad(d):
    return math.radians(d)


# ---------------------------------------------------------------- letters
def g_N():
    return vstem(XL, 0, NJ) + vstem(XR, 0, NJ) + arch(XL, XR, NJ, CAP)


def g_A():
    # the same arch, plus the bar. in the lockup that bar is the axis itself,
    # which is why the drawing never writes an A
    return g_N() + hbar(BARY, XL, XR)


def g_U():
    return vstem(XL, CAP - NJ, CAP) + vstem(XR, CAP - NJ, CAP) + \
        arch(XL, XR, CAP - NJ, 0, down=True)


def g_B():
    waist = 0.52 * CAP
    return (vstem(XL, 0, CAP)
            + bowl(XL, YT, waist, (XR - XL) * 0.88)
            + bowl(XL, waist, YB, (XR - XL)))


def g_C():
    return cring(55, 305)


def g_D():
    return vstem(XL, 0, CAP) + bowl(XL, YT, YB, XR - XL)


def g_E():
    """The sketch's E: a C-form, closed on the left, open on the right, with a
    middle arm that stops short of the bowl's widest point so all three
    right-hand ends line up on one vertical.

    Drawn on the face's own superellipse, not a circle — the same curve as the
    N's shoulder and the D's bowl, so it belongs to the alphabet rather than
    visiting from another one.
    """
    t = rad(E_OPEN)
    ex = math.copysign(abs(math.cos(t)) ** (2 / ARCH_N), math.cos(t))
    return cring(E_OPEN, 360 - E_OPEN) + hbar(MIDY, XM - AX, XM + AX * ex)


def g_Ealt():
    """The upper sketch's E: spine and three arms, the conventional cut. Kept
    on ss01 for anywhere the round one is too much."""
    return (vstem(XL, 0, CAP) + hbar(YT, XL, R) + hbar(YB, XL, R)
            + hbar(MIDY, XL, R - GW * 0.15))


def g_F():
    return vstem(XL, 0, CAP) + hbar(YT, XL, R) + hbar(MIDY, XL, R - GW * 0.15)


def g_G():
    # the bowl comes all the way up the right side, then the bar runs in
    return cring(55, 360) + hbar(MIDY, XM, R)


def g_H():
    return vstem(XL, 0, CAP) + vstem(XR, 0, CAP) + hbar(MIDY, XL, XR)


def g_I():
    return vstem(XM, 0, CAP)


def g_J():
    j = 0.34 * CAP
    return vstem(XR, j, CAP) + arch(XL, XR, j, 0, down=True)


def g_K():
    j = 0.49 * CAP
    return vstem(XL, 0, CAP) + seg((XL, j), (XR, CAP)) + seg((XL, j), (XR, 0))


def g_L():
    return vstem(XL, 0, CAP) + hbar(YB, XL, R)


def g_M():
    x0, x1 = XL, XL + (GW * 1.20 - W)
    return path((x0, 0), (x0, CAP), ((x0 + x1) / 2, 0.26 * CAP), (x1, CAP), (x1, 0))


def g_O():
    return ORING()


def g_P():
    return vstem(XL, 0, CAP) + bowl(XL, YT, 0.44 * CAP, (XR - XL) * 0.94)


def g_Q():
    return ORING() + seg((XM + AX * 0.42, CAP * 0.30), (XM + AX * 1.16, -CAP * 0.09))


def g_R():
    j = 0.44 * CAP
    return (vstem(XL, 0, CAP) + bowl(XL, YT, j, (XR - XL) * 0.94)
            + seg((XL + (XR - XL) * 0.30, j), (XR, 0)))


def g_S():
    """Two arcs sharing a tangent at the waist, so the spine is smooth."""
    ry = (CAP / 2 + OVER - W / 2) / 2
    rx = AX
    up, lo = CAP / 2 + ry, CAP / 2 - ry
    top = se_pts(XM, up, rx, ry, rad(35), rad(270))
    bot = se_pts(XM, lo, rx, ry, rad(90), rad(-145))
    return curve(top) + curve(bot)


def g_T():
    return hbar(YT, L, R) + vstem(XM, 0, CAP)


def g_V():
    return path((XL, CAP), (XM, YB), (XR, CAP))


def g_W():
    x0, x1 = XL, XL + (GW * 1.24 - W)
    d = (x1 - x0) * 0.29
    return path((x0, CAP), (x0 + d, YB), ((x0 + x1) / 2, 0.64 * CAP),
                (x1 - d, YB), (x1, CAP))


def g_X():
    return seg((XL, CAP), (XR, 0)) + seg((XL, 0), (XR, CAP))


def g_Y():
    f = 0.40 * CAP
    return path((XL, CAP), (XM, f), (XR, CAP)) + vstem(XM, 0, f)


def g_Z():
    return hbar(YT, L, R) + hbar(YB, L, R) + seg((XR, YT), (XL, YB))


# ---------------------------------------------------------------- digits
def g_zero():
    return sering(XM, CAP / 2, AX * 0.82)


def g_one():
    return vstem(XM, 0, CAP) + seg((XM - GW * 0.20, CAP - GW * 0.18), (XM, CAP))


def g_two():
    r = 0.42 * CAP
    cy = CAP - r
    end = rad(-28)
    px = XM + AX * math.cos(end)
    py = cy + (r - W / 2) * math.sin(end)
    return (curve(se_pts(XM, cy, AX, r - W / 2, rad(192), end))
            + seg((px, py), (XL, YB)) + hbar(YB, L, R))


def g_three():
    w = 0.52 * CAP
    return (bowl(XL + GW * 0.04, YT, w, (XR - XL) * 0.86)
            + bowl(XL + GW * 0.04, w, YB, (XR - XL) * 0.94))


def g_four():
    f = 0.30 * CAP
    return path((XR - GW * 0.16, CAP), (XL, f), (R, f)) + vstem(XR - GW * 0.16, 0, CAP)


def g_five():
    cy, ry = 0.29 * CAP, 0.29 * CAP - W / 2 + OVER
    return (hbar(YT, XL, R) + vstem(XL, cy + ry * math.sin(rad(150)), CAP)
            + curve(se_pts(XM, cy, AX, ry, rad(150), rad(-150))))


def g_six():
    # a closed lower bowl, and one stroke that leaves its left flank and rises
    rb = 0.31 * CAP
    ry = rb - W / 2 + OVER
    return (sering(XM, rb, AX, ry)
            + curve(se_pts(XM + AX * 0.62, rb, AX * 1.62, CAP - W / 2 - rb,
                           rad(180), rad(90))))


def g_seven():
    return hbar(YT, L, R) + seg((R - W / 2, YT), (XM - GW * 0.14, 0))


def g_eight():
    r = 0.27 * CAP
    return (sering(XM, CAP - r - OVER / 2, AX * 0.84, r - W / 2)
            + sering(XM, r + OVER / 2, AX, CAP / 2 - r - W / 2 + OVER))


def g_nine():
    return [c.transform(lambda p: (2 * XM - p[0], CAP - p[1])) for c in g_six()]


# ---------------------------------------------------------------- marks
def g_space():
    return []


def _dot(x, y):
    return [ellipse(x, y, W / 2, W / 2)]


def g_period():
    return _dot(XM, W / 2)


def g_comma():
    return [stroke_line([(XM + W * 0.18, W / 2), (XM - W * 0.30, -CAP * 0.16)], W)]


def g_colon():
    return _dot(XM, W / 2) + _dot(XM, CAP * 0.42)


def g_semicolon():
    return g_comma() + _dot(XM, CAP * 0.42)


def g_hyphen():
    return hbar(MIDY, XM - GW * 0.24, XM + GW * 0.24)


def g_endash():
    return hbar(MIDY, L, R)


def g_emdash():
    return hbar(MIDY, L - SB * 0.6, R + SB * 0.6)


def g_slash():
    return seg((XL, -CAP * 0.08), (XR, CAP * 1.02))


def g_parenleft():
    return curve(se_pts(XM + GW * 0.30, CAP * 0.42, GW * 0.42, CAP * 0.66,
                        rad(140), rad(220)))


def g_parenright():
    return [c.transform(lambda p: (2 * XM - p[0], p[1])) for c in g_parenleft()]


def g_quotesingle():
    return vstem(XM, CAP * 0.70, CAP)


def g_quotedbl():
    return vstem(XM - GW * 0.17, CAP * 0.70, CAP) + vstem(XM + GW * 0.17, CAP * 0.70, CAP)


def g_exclam():
    return vstem(XM, CAP * 0.26, CAP) + _dot(XM, W / 2)


def g_question():
    # the bowl has to land on the stem, so it sweeps round to the bottom of its
    # own circle where the tangent is horizontal and x is back at the centre
    r = AX * 0.86
    cy = CAP - r - OVER
    return (curve(se_pts(XM, cy, r, r, rad(200), rad(-80)))
            + vstem(XM, CAP * 0.26, cy - r * 0.98) + _dot(XM, W / 2))


def g_ampersand():
    """Kept geometric: a small upper loop, a wide lower loop, one tail."""
    rt = AX * 0.52
    return (curve(se_pts(XM - AX * 0.34, CAP - rt - OVER, rt, rt, rad(-60), rad(240)))
            + curve(se_pts(XM - AX * 0.14, rt * 1.15, rt * 1.15, rt * 1.15,
                           rad(30), rad(330)))
            + seg((XM - AX * 0.34 - rt * 0.5, CAP - rt * 1.5), (XR, YB)))


def g_notdef():
    return [stroke_line([(L, 0), (R, 0), (R, CAP), (L, CAP), (L, 0)], W)]


# ---------------------------------------------------------------- the set
GLYPHS = {
    "A": g_A, "B": g_B, "C": g_C, "D": g_D, "E": g_E, "F": g_F, "G": g_G,
    "H": g_H, "I": g_I, "J": g_J, "K": g_K, "L": g_L, "M": g_M, "N": g_N,
    "O": g_O, "P": g_P, "Q": g_Q, "R": g_R, "S": g_S, "T": g_T, "U": g_U,
    "V": g_V, "W": g_W, "X": g_X, "Y": g_Y, "Z": g_Z,
    "zero": g_zero, "one": g_one, "two": g_two, "three": g_three,
    "four": g_four, "five": g_five, "six": g_six, "seven": g_seven,
    "eight": g_eight, "nine": g_nine,
    "space": g_space, "period": g_period, "comma": g_comma, "colon": g_colon,
    "semicolon": g_semicolon, "hyphen": g_hyphen, "endash": g_endash,
    "emdash": g_emdash, "slash": g_slash, "parenleft": g_parenleft,
    "parenright": g_parenright, "quotesingle": g_quotesingle,
    "quotedbl": g_quotedbl, "exclam": g_exclam, "question": g_question,
    "ampersand": g_ampersand, "E.alt": g_Ealt,
}

# ---------------------------------------------------------------- spacing
# One advance for every glyph is what makes a monoline face look gappy: a bare
# stem like the I floats in a box built for an O. So each glyph is fitted to
# its own ink, and the sidebearing is chosen by what sits at the edge —
# a flat stem needs the most air, a curve meets the neighbour at a single point
# and needs less, an open corner (the underside of a T, the shoulder of an L)
# already carries its own white and needs least of all.
FLAT = SB                  # a vertical stem at the edge
ROUND = round(SB * 0.64)   # a curve: the extreme is one point, not a wall
OPEN = round(SB * 0.72)    # a diagonal or an open corner

SIDE = {
    "A": (FLAT, FLAT), "B": (FLAT, ROUND), "C": (ROUND, round(ROUND * 0.75)),
    "D": (FLAT, ROUND), "E": (round(ROUND * 1.14), round(ROUND * 0.60)),
    "F": (FLAT, round(OPEN * 0.45)), "G": (ROUND, round(FLAT * 0.80)),
    "H": (FLAT, FLAT), "I": (FLAT, FLAT), "J": (round(OPEN * 0.60), FLAT),
    "K": (FLAT, round(OPEN * 0.70)), "L": (FLAT, round(OPEN * 0.40)),
    "M": (FLAT, FLAT), "N": (FLAT, FLAT), "O": (ROUND, ROUND),
    "P": (FLAT, round(OPEN * 0.70)), "Q": (ROUND, ROUND),
    "R": (FLAT, round(OPEN * 0.80)), "S": (round(ROUND * 0.85), round(ROUND * 0.85)),
    "T": (round(OPEN * 0.50), round(OPEN * 0.50)), "U": (FLAT, FLAT),
    "V": (round(OPEN * 0.60), round(OPEN * 0.60)),
    "W": (round(OPEN * 0.60), round(OPEN * 0.60)),
    "X": (round(OPEN * 0.75), round(OPEN * 0.75)),
    "Y": (round(OPEN * 0.55), round(OPEN * 0.55)),
    "Z": (round(OPEN * 0.80), round(OPEN * 0.80)),
    "E.alt": (FLAT, round(OPEN * 0.45)),
    "period": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "comma": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "colon": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "semicolon": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "exclam": (round(FLAT * 0.70), round(FLAT * 0.70)),
    "quotesingle": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "quotedbl": (round(FLAT * 0.60), round(FLAT * 0.60)),
    "hyphen": (round(FLAT * 0.55), round(FLAT * 0.55)),
    "endash": (round(FLAT * 0.55), round(FLAT * 0.55)),
    "emdash": (round(FLAT * 0.40), round(FLAT * 0.40)),
    "slash": (round(OPEN * 0.35), round(OPEN * 0.35)),
    "parenleft": (round(FLAT * 0.70), round(OPEN * 0.45)),
    "parenright": (round(OPEN * 0.45), round(FLAT * 0.70)),
    "question": (ROUND, round(ROUND * 0.80)),
    "ampersand": (round(OPEN * 0.80), round(OPEN * 0.70)),
}
SPACE_ADV = round(ADV * 0.58)
FIGURES = ("zero", "one", "two", "three", "four", "five",
           "six", "seven", "eight", "nine")


def _bounds(cs):
    xs = [p[0] for c in cs for p in c.points()]
    return (min(xs), max(xs)) if xs else (0.0, 0.0)


def _tabular():
    """Figures share one advance so columns of them line up — the face is meant
    for readouts as much as headlines."""
    w = 0.0
    for n in FIGURES:
        x0, x1 = _bounds(GLYPHS[n]())
        w = max(w, ROUND + (x1 - x0) + ROUND)
    return round(w)


TAB = None      # resolved on first use; building every figure at import is slow


def _space(name, cs):
    """Fit the glyph to its own ink and return (contours, advance)."""
    global TAB
    if not cs:
        return cs, SPACE_ADV
    x0, x1 = _bounds(cs)
    if name in FIGURES:
        if TAB is None:
            TAB = _tabular()
        adv, dx = TAB, (TAB - (x1 - x0)) / 2 - x0
    else:
        l, r = SIDE.get(name, (FLAT, FLAT))
        adv, dx = round(l + (x1 - x0) + r), l - x0
    if abs(dx) > 0.01:
        cs = [c.transform(lambda p, d=dx: (p[0] + d, p[1])) for c in cs]
    return cs, adv


CMAP = {ord(c): c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
CMAP.update({ord(c): n for c, n in zip("0123456789", [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])})
CMAP.update({0x20: "space", 0x2E: "period", 0x2C: "comma", 0x3A: "colon",
             0x3B: "semicolon", 0x2D: "hyphen", 0x2013: "endash", 0x2014: "emdash",
             0x2F: "slash", 0x28: "parenleft", 0x29: "parenright",
             0x27: "quotesingle", 0x22: "quotedbl", 0x21: "exclam",
             0x3F: "question", 0x26: "ampersand"})
# lowercase types the caps, so the face never drops a character
CMAP.update({ord(c.lower()): c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})


def advance(name):
    build(name)
    return _cache[name][2]


_cache = {}


def build(name):
    """Contours for one glyph. Every outer contour is wound the same way so
    nonzero fill unions the overlapping strokes; holes are wound against them."""
    if name not in _cache:
        _err.clear()
        cs = [c.wind(not c.hole) for c in GLYPHS[name]()]
        err = max(_err) if _err else 0.0
        cs, adv = _space(name, cs)
        _cache[name] = (cs, err, adv)
    return _cache[name][0], _cache[name][1]
