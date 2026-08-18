#!/usr/bin/env python3
"""Build every ANTINODE mark from the geometry up.

    python3 build-antinode.py            # writes ./out

Nothing here is traced. The lobes are a real sine, the letters are real font
outlines converted to paths, and the stroke weight is measured off the
typeface rather than picked by eye. Re-running regenerates all of it.

    A  standing wave   three antinodes, both phases solid
    B  single antinode one lobe, one side
    C  phase           one instant solid, the other ghosted, crest marked
    D  reflection      the word on the axis with its mirror under it
    E  enclosed        the word inside one antinode
    F  enclosed pair   the word and its mirror, both inside one antinode

A-C set the word in Cormorant Garamond Light; D-F in Archivo, following the
second sketch's heavier letterforms.
"""
import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "logos")   # the deliverables
TMP = os.path.join(HERE, "tmp")                # page-only, not a logo
WORD = "ANTINODE"
INK = "#141312"


# ---------------------------------------------------------------- flattening
class Flatten(BasePen):
    """Sample outlines to polylines so stroke weights can be measured."""

    def __init__(self, glyphSet, steps=24):
        super().__init__(glyphSet)
        self.steps, self.contours, self.cur = steps, [], []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, c1, c2, p):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            u = 1 - t
            self.cur.append((
                u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p[0],
                u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p[1],
            ))

    def _closePath(self):
        if self.cur:
            self.contours.append(self.cur)
            self.cur = []

    def _endPath(self):
        self._closePath()


class Face:
    """One typeface, ready to hand back outlined words in output units."""

    def __init__(self, path, axes=None):
        font = TTFont(path)
        if axes:
            font = instancer.instantiateVariableFont(font, axes, inplace=False)
        self.upem = font["head"].unitsPerEm
        self.cap = font["OS/2"].sCapHeight
        self.cmap = font.getBestCmap()
        self.glyphs = font.getGlyphSet()
        self.hmtx = font["hmtx"]

    def hairline(self):
        """Thinnest stroke in the face: the top of the O, measured not guessed."""
        pen = Flatten(self.glyphs)
        self.glyphs[self.cmap[ord("O")]].draw(pen)
        pen._endPath()
        xs = [p[0] for c in pen.contours for p in c]
        x = (min(xs) + max(xs)) / 2
        hits = []
        for c in pen.contours:
            for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
                if (x0 - x) * (x1 - x) < 0:
                    hits.append(y0 + (x - x0) / (x1 - x0) * (y1 - y0))
        hits.sort()
        return hits[-1] - hits[-2]

    def word(self, text, cap_height, tracking, transform=None):
        """Outlined caps sitting on y=0, growing up. Returns (path, advance)."""
        s = cap_height / self.cap
        track = tracking * self.upem
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.2f}")
        x = 0.0
        for i, ch in enumerate(text):
            name = self.cmap[ord(ch)]
            t = Transform(s, 0, 0, -s, x * s, 0)
            if transform:
                t = transform.transform(t)
            self.glyphs[name].draw(TransformPen(pen, t))
            x += self.hmtx[name][0] + (track if i < len(text) - 1 else 0)
        return pen.getCommands(), x * s


FONTS = os.path.join(HERE, "fonts")
serif = Face(os.path.join(FONTS, "CormorantGaramond-Light.ttf"))
grot = Face(os.path.join(FONTS, "Archivo[wdth,wght].ttf"), {"wght": 700, "wdth": 100})


# ---------------------------------------------------------------- the wave
def sine(A, L, lobes, mirror=False, horizontal=False, x0=0.0, reverse=False, move=True):
    """x = A sin(pi t / L) as cubics carrying the sine's own tangents.

    Handles of length step/3 make this a Hermite fit, third order, so accuracy
    comes from subdivision: four segments per lobe holds the curve within
    0.09% of the true sine — a tenth of the stroke, and therefore invisible.
    `horizontal` swaps the roles so the axis runs left to right instead.
    """
    sgn = -1 if mirror else 1
    k = math.pi / L
    off = lambda t: sgn * A * math.sin(k * (t - x0))
    dof = lambda t: sgn * A * k * math.cos(k * (t - x0))
    pt = (lambda t, o: f"{t:.2f} {o:.2f}") if horizontal else (lambda t, o: f"{o:.2f} {t:.2f}")
    n = lobes * 4
    step = (lobes * L) / n
    # reversed, the same curve is walked backwards; a negative step keeps the
    # Hermite handles correct, so no separate maths is needed
    spans = [(x0 + i * step, x0 + (i + 1) * step) for i in range(n)]
    if reverse:
        spans = [(b, a) for a, b in reversed(spans)]
    d = [f"M {pt(*((spans[0][0],) + (off(spans[0][0]),)))}"] if move else []
    for a, b in spans:
        step = b - a
        d.append(
            f"C {pt(a + step / 3, off(a) + dof(a) * step / 3)} "
            f"{pt(b - step / 3, off(b) - dof(b) * step / 3)} {pt(b, off(b))}"
        )
    return " ".join(d)


def closed_lens(A, L, horizontal=False):
    """One antinode as a single closed contour. Two separate strokes meeting
    at a node leave a notch once the pen gets heavy — butt caps cannot form a
    point. Closing the path lets the join do it."""
    return (sine(A, L, 1, horizontal=horizontal) + " "
            + sine(A, L, 1, mirror=True, horizontal=horizontal, reverse=True, move=False)
            + " Z")


# ---------------------------------------------------------------- geometry
A = 100.0          # amplitude
L = 200.0          # one lobe, node to node
LOBES = 3
WAVE = LOBES * L
CAPH = 52.0        # wordmark cap height, A-C
TRACK = 0.30       # letterspacing in em, A-C
SW = round(serif.hairline() / serif.cap * CAPH * 1.55, 2)

OVER = 46.0        # axis above the wave
GAP = 96.0         # wave to wordmark
TAIL = 58.0        # axis past the wordmark
SHORT = 60.0       # axis past a single-antinode mark
ICON_SW = 11.0     # the small cut's pen
ICON_STUB = 24.0

_, WORDLEN = serif.word(WORD, CAPH, TRACK)


def svg(w, h, body, vx=0.0, vy=0.0):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {w:.1f} {h:.1f}" '
        f'width="{w:.0f}" height="{h:.0f}" fill="{INK}">\n{body}\n</svg>\n'
    )


def stroked(paths, dash=None, sw=None):
    sw = SW if sw is None else sw
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<g fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="butt" stroke-linejoin="miter"{d}>\n'
        + "\n".join(f'  <path d="{p}"/>' for p in paths)
        + "\n</g>"
    )


# ---------------------------------------------------------- A-C: the wave
def vertical(wave_paths, wave_end, dashed=None, dot=False):
    """Wave on the axis, ANTINODE hanging off the same line. The string at
    rest is the type's baseline — one line doing both jobs."""
    top, word_top = -OVER, wave_end + GAP
    bottom = word_top + WORDLEN + TAIL
    # rotate 90 cw: text reads downward, letters fall right of the axis
    rot = Transform().translate(0, word_top).rotate(math.pi / 2)
    path, _ = serif.word(WORD, CAPH, TRACK, rot)
    body = [stroked([f"M 0 {top:.1f} L 0 {bottom:.1f}"] + wave_paths)]
    if dashed:
        body.append(stroked(dashed, dash=f"{SW * 7:.2f} {SW * 5:.2f}"))
    if dot:
        body.append(f'<circle cx="{A:.1f}" cy="{L / 2:.1f}" r="{SW * 1.9:.2f}"/>')
    body.append(f'<path d="{path}"/>')
    pad = 40.0
    return svg(2 * A + 2 * pad, bottom - top + 2 * pad, "\n".join(body), -A - pad, top - pad)


def mark_body(paths, dashed=None, dot=False, left=True):
    body = [stroked([f"M 0 {-SHORT:.1f} L 0 {L + SHORT:.1f}"] + paths)]
    if dashed:
        body.append(stroked(dashed, dash=f"{SW * 7:.2f} {SW * 5:.2f}"))
    if dot:
        body.append(f'<circle cx="{A:.1f}" cy="{L / 2:.1f}" r="{SW * 1.9:.2f}"/>')
    return body, (-A if left else -SW), A


def horizontal(paths, dashed=None, dot=False, left=True):
    """Compact mark left, ANTINODE right. A three-lobe wave is seven times its
    own amplitude tall and cannot sit beside a line of type; one antinode can."""
    body, x0, x1 = mark_body(paths, dashed, dot, left)
    gap = CAPH * 1.5
    path, wlen = serif.word(WORD, CAPH, TRACK,
                            Transform().translate(x1 + gap, L / 2 + CAPH / 2))
    body.append(f'<path d="{path}"/>')
    pad = 40.0
    return svg((x1 + gap + wlen) - x0 + 2 * pad, L + 2 * SHORT + 2 * pad,
               "\n".join(body), x0 - pad, -SHORT - pad)


def mark_only(paths, dashed=None, dot=False, left=True):
    body, x0, x1 = mark_body(paths, dashed, dot, left)
    pad = 34.0
    return svg(x1 - x0 + 2 * pad, L + 2 * SHORT + 2 * pad, "\n".join(body),
               x0 - pad, -SHORT - pad)


def icon(paths, dot=False, left=True, extra=""):
    """The small cut. A hairline at 24px is not a light logo, it is no logo:
    the stroke goes sub-pixel and the mark greys out. So the icon is redrawn,
    not scaled — same curve, tighter crop, heavier pen, no dashes."""
    x0, x1 = (-A if left else -ICON_SW / 2), A
    body = [stroked([f"M 0 {-ICON_STUB:.1f} L 0 {L + ICON_STUB:.1f}"] + paths, sw=ICON_SW)]
    if dot:
        body.append(f'<circle cx="{A:.1f}" cy="{L / 2:.1f}" r="{ICON_SW * 1.5:.2f}"/>')
    if extra:
        body.append(extra)
    pad = 10.0
    return svg(x1 - x0 + 2 * pad, L + 2 * ICON_STUB + 2 * pad, "\n".join(body),
               x0 - pad, -ICON_STUB - pad)


# ------------------------------------------------- D-F: text inside the wave
GCAP = 100.0       # cap height for the Archivo cuts
GTRACK = 0.03      # grotesque caps want far less letterspacing than the serif
# hairline comes back in font units; scale it to the cap height actually used
GHAIR = grot.hairline() / grot.cap * GCAP
RULE = round(GHAIR * 0.45, 2)          # the axis, well under the lightest stroke
GHOST = round(GHAIR * 0.22, 2)         # outline weight for a reflected word
_, GWORD = grot.word(WORD, GCAP, GTRACK)

# How much of the lens length the word fills. Raising it shortens the tips but
# drops the curve at the word's ends, so the lens has to get taller to keep the
# clearance — E wants a compact eye, F has two lines to clear and would turn
# into a diamond at the same setting, so they are tuned apart.
FRAC = {"E": 0.80, "F": 0.70}


def lens_fit(frac, half_height, slack=0.22):
    """Size a lobe around the word. Returns (length, margin, amplitude).
    The curve is lowest where the word starts, so that is the only place
    clearance has to be checked."""
    lam = GWORD / frac
    margin = (lam - GWORD) / 2
    amp = (half_height + slack * GCAP) / math.sin(math.pi * margin / lam)
    return lam, margin, amp


SEAM = round(RULE * 2.4, 2)   # air between a word and its reflection, so the
                              # axis reads as one line instead of fragments
                              # showing only in the gaps between letters


def enclosed(mirrored):
    """The word inside one antinode. E centres it; F sets it on the axis and
    hangs its reflection underneath, which is the second sketch exactly."""
    half = GCAP + SEAM / 2 if mirrored else GCAP / 2
    LAM, MARGIN, amp = lens_fit(FRAC["F" if mirrored else "E"], half)
    curve = [closed_lens(amp, LAM, horizontal=True)]
    body = [stroked(curve, sw=RULE)]
    if mirrored:
        for t in (Transform().translate(MARGIN, -SEAM / 2),
                  Transform(1, 0, 0, -1, MARGIN, SEAM / 2)):
            body.append(f'<path d="{grot.word(WORD, GCAP, GTRACK, t)[0]}"/>')
        # the axis runs node to node, the full span of the lobe
        body.append(f'<path d="M 0 0 L {LAM:.1f} 0" fill="none" '
                    f'stroke="{INK}" stroke-width="{RULE}"/>')
    else:
        body.append(f'<path d="{grot.word(WORD, GCAP, GTRACK, Transform().translate(MARGIN, GCAP / 2))[0]}"/>')
    pad = 46.0
    return svg(LAM + 2 * pad, 2 * amp + 2 * pad, "\n".join(body), -pad, -amp - pad)


def reflection(ghost):
    """Sketch two without the container: the word standing on the axis with
    its own reflection beneath. The two phases of the wave, made of type."""
    over = GCAP * 0.42
    top, _ = grot.word(WORD, GCAP, GTRACK, Transform().translate(0, -SEAM / 2))
    low, _ = grot.word(WORD, GCAP, GTRACK, Transform(1, 0, 0, -1, 0, SEAM / 2))
    body = [f'<path d="{top}"/>']
    body.append(
        f'<path d="{low}" fill="none" stroke="{INK}" stroke-width="{GHOST}"/>'
        if ghost else f'<path d="{low}"/>'
    )
    body.append(f'<path d="M {-over:.1f} 0 L {GWORD + over:.1f} 0" fill="none" '
                f'stroke="{INK}" stroke-width="{RULE}"/>')
    pad = 40.0
    return svg(GWORD + 2 * over + 2 * pad, 2 * GCAP + 2 * pad, "\n".join(body),
               -over - pad, -GCAP - pad)


def on_the_line(face=None, cap=None, track=None, rule=None, trail=False):
    """The sketch read the right way up: a horizontal axis, the word standing
    on it as a baseline, and one antinode wrapped around the opening letter.

    The first pass ran the wave the whole length of the word, which is what
    the pencil looks like it does. It does not survive translation: three
    lobes crossing eight bold caps leaves curve fragments in the counters and
    between letters, and neither the word nor the wave reads. Both sketches
    actually put the lobe at the front, with the word running out of it.
    """
    face = face or grot
    cap = cap or GCAP
    track = GTRACK if track is None else track
    rule = rule or RULE
    word, wlen = face.word(WORD, cap, track)
    initial = face.hmtx[face.cmap[ord(WORD[0])]][0] / face.cap * cap
    ll, amp = cap * 1.62, cap * 1.34        # a tall, narrow lobe, as drawn
    x0 = initial / 2 - ll / 2               # centred on the opening letter
    over = cap * 0.40
    left, right = min(x0, -over), wlen + over

    body = [f'<g transform="translate({x0:.1f} 0)">'
            + stroked([closed_lens(amp, ll, horizontal=True)], sw=rule) + '</g>']
    if trail:
        # The opposite phase carrying on under the word. One lobe, downward
        # only: a second lobe swings back up through the caps and leaves dash
        # fragments in the counters, which is noise rather than a wave.
        body.append(f'<g transform="translate({x0 + ll:.1f} 0)">' + stroked(
            [sine(amp * 0.52, wlen - (x0 + ll), 1, horizontal=True)],
            dash=f"{rule * 3.4:.2f} {rule * 2.6:.2f}", sw=rule) + '</g>')
    body.append(f'<path d="M {left:.1f} 0 L {right:.1f} 0" fill="none" '
                f'stroke="{INK}" stroke-width="{rule}"/>')
    body.append(f'<path d="{word}"/>')      # type last: the lobe passes behind it
    pad = 40.0
    return svg(right - left + 2 * pad, 2 * amp + 2 * pad, "\n".join(body),
               left - pad, -amp - pad)


def tilde(cx, cy, width, amp):
    """One full period of the same sine, small enough to live inside a lobe —
    the squiggle from the sketch, drawn with the curve it stands for."""
    half = width / 2
    return (f'<g transform="translate({cx:.1f} {cy:.1f})">'
            f'{stroked([sine(amp, half, 2, horizontal=True, x0=-half)], sw=ICON_SW)}</g>')


# ---------------------------------------------------------------- assembly
full = [sine(A, L, LOBES), sine(A, L, LOBES, mirror=True)]
lens = [closed_lens(A, L)]                                 # one antinode of A
half = [sine(A, L, 1)]                                     # one antinode of B
solid, ghost = [sine(A, L, LOBES)], [sine(A, L, LOBES, mirror=True)]
solid1, ghost1 = [sine(A, L, 1)], [sine(A, L, 1, mirror=True)]
squiggle = tilde(0, L / 2, A * 1.1, A * 0.19)

files = {
    # A - the full standing wave, both phases solid
    "antinode-A-stacked.svg": vertical(full, WAVE),
    "antinode-A-horizontal.svg": horizontal(lens),
    "antinode-A-mark.svg": mark_only(lens),
    "antinode-A-icon.svg": icon(lens),
    # B - a single antinode; the mark is the whole logo
    "antinode-B-stacked.svg": vertical(half, L),
    "antinode-B-horizontal.svg": horizontal(half, left=False),
    "antinode-B-mark.svg": mark_only(half, left=False),
    "antinode-B-icon.svg": icon(half, left=False),
    # C - one instant solid, the opposite instant ghosted, the crest marked
    "antinode-C-stacked.svg": vertical(solid, WAVE, dashed=ghost, dot=True),
    "antinode-C-horizontal.svg": horizontal(solid1, dashed=ghost1, dot=True),
    "antinode-C-mark.svg": mark_only(solid1, dashed=ghost1, dot=True),
    # C's ghost goes solid at icon size and the crest dot is dropped: at 32px it
    # stops reading as a marked point and only thickens the curve. So A and C
    # share an icon, and the dot stays a display-only detail.
    "antinode-C-icon.svg": icon(lens),
    # D - the word and its reflection about the axis; no container
    "antinode-D-lockup.svg": reflection(ghost=False),
    "antinode-D-ghost.svg": reflection(ghost=True),
    # G - the sketch upright: wave along a horizontal axis, word on the axis
    "antinode-G-lockup.svg": on_the_line(),
    "antinode-G-phase.svg": on_the_line(trail=True),
    "antinode-G-serif.svg": on_the_line(face=serif, cap=CAPH * 1.7, track=TRACK, rule=SW * 1.7),
    # E - the word inside one antinode
    "antinode-E-lockup.svg": enclosed(mirrored=False),
    # F - the word and its reflection, both inside one antinode
    "antinode-F-lockup.svg": enclosed(mirrored=True),
}
def def_icon():
    """D, E and F share one mark: the sketch's oval with the squiggle in it.
    No axis stem here — a stem through a tilde reads as a collision, and the
    two node points where the curves meet already say where the axis is."""
    pad = 10.0
    body = stroked(lens, sw=ICON_SW) + "\n" + tilde(0, L / 2, A * 1.05, A * 0.155)
    return svg(2 * A + 2 * pad, L + 2 * pad, body, -A - pad, -pad)


for tag in "DEFG":
    files[f"antinode-{tag}-icon.svg"] = def_icon()


def diagram():
    """Construction drawing for the board: one antinode and the two numbers
    everything else derives from. Annotations use a second colour the page
    maps to its accent, so they never print as part of the mark."""
    ACC = "#2d6b5f"
    t, b = -SHORT, L + SHORT
    tick = lambda x, y, dx, dy: (
        f'<path d="M {x - dx:.1f} {y - dy:.1f} L {x + dx:.1f} {y + dy:.1f}" '
        f'stroke="{ACC}" stroke-width="{SW}"/>')
    a = [f'<path d="M 0 {L / 2} L {A} {L / 2}" stroke="{ACC}" stroke-width="{SW}" '
         f'stroke-dasharray="{SW * 3:.1f} {SW * 3:.1f}"/>',
         tick(0, L / 2, 0, 9) + tick(A, L / 2, 0, 9),
         f'<text x="{A / 2:.0f}" y="{L / 2 - 14:.0f}" fill="{ACC}" text-anchor="middle" class="dim">A</text>']
    x = -A - 46
    a += [f'<path d="M {x} 0 L {x} {L}" stroke="{ACC}" stroke-width="{SW}"/>',
          tick(x, 0, 9, 0) + tick(x, L, 9, 0),
          f'<text x="{x - 14}" y="{L / 2 + 5:.0f}" fill="{ACC}" text-anchor="end" class="dim">&#955;/2</text>']
    for y in (0, L):
        a.append(f'<circle cx="0" cy="{y}" r="{SW * 1.6:.1f}" fill="{ACC}"/>')
    a.append(f'<circle cx="{A}" cy="{L / 2}" r="{SW * 1.6:.1f}" fill="{ACC}"/>')
    pad = 30.0
    return svg(2 * A + 100 + 2 * pad, b - t + 2 * pad,
               stroked([f"M 0 {t:.1f} L 0 {b:.1f}"] + lens) + "\n" + "\n".join(a),
               -A - 100 - pad, t - pad)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for name, data in files.items():
        open(os.path.join(OUT, name), "w").write(data)
    open(os.path.join(TMP, "_diagram.svg"), "w").write(diagram())
    print(f"serif  cap {CAPH:.0f}  stroke {SW}  word {WORDLEN:.0f}")
    print(f"grot   cap {GCAP:.0f}  rule {RULE}  ghost {GHOST}  word {GWORD:.0f}")
    for tag, half in (("E", GCAP / 2), ("F", GCAP + SEAM / 2)):
        lam, _, amp = lens_fit(FRAC[tag], half)
        print(f"lens {tag}  {lam:.0f} x {2 * amp:.0f}  ({lam / (2 * amp):.2f}:1)")
    print(f"{len(files)} files -> {OUT}")
