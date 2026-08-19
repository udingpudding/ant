#!/usr/bin/env python3
"""Specimen sheets for the face: the alphabet, a waterfall, and the drawing
that makes the argument — one curve doing five jobs."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glyphs, setter
from geom import stroke_line, stroke_curve, superellipse_pts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "specimen")
INK = "#141312"
ACC = "#2d6b5f"          # the page maps this to its accent; never part of a mark


def svg(w, h, body, vx=0.0, vy=0.0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} '
            f'{w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}" fill="{INK}">\n{body}\n</svg>\n')


def rows(lines, cap, track, lead, x=0.0, pad=40.0):
    d, wide = [], 0.0
    for i, line in enumerate(lines):
        p, adv = setter.word(line, cap, track, x=x, y=pad + cap + i * lead)
        d.append(p); wide = max(wide, adv)
    return ("\n".join(f'<path d="{p}"/>' for p in d),
            wide + 2 * pad, pad + cap + (len(lines) - 1) * lead + pad)


def alphabet():
    body, w, h = rows(["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "0123456789",
                       "&().,:;-!?'\"/"], 100.0, 0.09, 150.0, x=40.0)
    return svg(w, h, body)


def waterfall():
    sizes = [(140, 0.02), (96, 0.05), (64, 0.09), (44, 0.13), (30, 0.18), (20, 0.24)]
    d, y, wide = [], 40.0, 0.0
    for cap, tr in sizes:
        y += cap
        p, adv = setter.word("ANTINODE", cap, tr, x=40.0, y=y)
        d.append(f'<path d="{p}"/>')
        y += cap * 0.62
        wide = max(wide, adv)
    return svg(wide + 80, y - sizes[-1][0] * 0.62 + 40, "\n".join(d))


def parts():
    """The system, drawn. The wave's lobe, then the same superellipse standing
    in for a letter at four orientations — which is the reason the face had to
    be drawn rather than chosen."""
    CAP = glyphs.CAP
    W = glyphs.W
    GAP = CAP * 0.62
    cells, x, labels = [], 0.0, []

    def place(contours, accent, label, width):
        nonlocal x
        ink = "\n".join(f'<path d="{c.transform(lambda p: (x + p[0] - glyphs.L, -p[1])).svg()}"/>'
                        for c in contours)
        acc = "\n".join(f'<path fill="{ACC}" d="{c.transform(lambda p: (x + p[0] - glyphs.L, -p[1])).svg()}"/>'
                        for c in accent)
        cells.append(ink + "\n" + acc)
        labels.append((x + width / 2, label))
        x += width + GAP

    # 1 - the wave's own lobe, at the letters' scale
    amp, half = CAP * 0.62, CAP * 0.82
    lobe = superellipse_pts(half / 2, 0, half / 2, amp, 2.5, 0, math.pi)
    c, _ = stroke_curve(lobe, W, 24)
    place([], [c.transform(lambda p: (p[0] + glyphs.L, p[1]))], "the lobe", half)

    # 2..5 - the same curve doing a letter's work
    for name, label in (("N", "N"), ("A", "A"), ("U", "U"), ("D", "D")):
        cs, _ = glyphs.build(name)
        # the arch is the last curved part in each of these; find it by point count
        curved = max(cs, key=lambda c: len(c.ops))
        place([c for c in cs if c is not curved], [curved], label, glyphs.GW)

    lab = "\n".join(f'<text x="{cx:.0f}" y="{CAP * 0.40:.0f}" fill="{ACC}" font-size="{CAP * 0.20:.0f}" '
                    f'font-family="ui-sans-serif,system-ui,sans-serif" letter-spacing="0.14em" '
                    f'text-anchor="middle" class="dim">{t}</text>' for cx, t in labels)
    pad = CAP * 0.30
    return svg(x - GAP + 2 * pad, CAP + CAP * 0.52 + 2 * pad,
               "\n".join(cells) + "\n" + lab, -pad, -CAP - pad)


def arch_study():
    """Why the letter's arch is not the wave's sine. Over the same span the two
    curves are close — but at the node the sine leaves the axis at 68 degrees
    and the superellipse stands at 90, and a letter has to stand up straight."""
    CAP, W = glyphs.CAP, glyphs.W
    a, b = (glyphs.XR - glyphs.XL) / 2, glyphs.SHOULDER - W / 2
    cx, y0 = glyphs.XM, CAP - glyphs.SHOULDER
    pen = W * 0.30
    sup = superellipse_pts(cx, y0, a, b, glyphs.ARCH_N, 0, math.pi)
    k = math.pi / (2 * a)
    sin = [(cx + a - t, y0 + b * math.sin(k * t)) for t in
           [2 * a * i / 200 for i in range(201)]]

    def line(pts, colour, dash=""):
        d = " ".join(("M" if i == 0 else "L") + f" {p[0]:.1f} {-p[1]:.1f}"
                     for i, p in enumerate(pts))
        return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{pen:.1f}" '
                f'stroke-linecap="round" {dash}/>')

    body = [line(sin, ACC, f'stroke-dasharray="{pen * 3:.1f} {pen * 3:.1f}"'), line(sup, INK)]
    for xx in (glyphs.XL, glyphs.XR):                       # the legs
        body.append(line([(xx, 0), (xx, y0)], INK))
    body.append(line([(glyphs.L - 60, y0), (glyphs.R + 60, y0)], ACC,
                     f'stroke-dasharray="{pen * 1.6:.1f} {pen * 2.6:.1f}"'))

    # the tangents at the left node, which is the whole argument
    ray = CAP * 0.26
    body.append(line([(glyphs.XL, y0 - ray * 0.30), (glyphs.XL, y0 + ray)], INK))
    ang = math.atan2(b * k, 1.0)                            # the sine's slope there
    body.append(line([(glyphs.XL - ray * 0.28 * math.cos(ang), y0 - ray * 0.28 * math.sin(ang)),
                      (glyphs.XL + ray * math.cos(ang), y0 + ray * math.sin(ang))], ACC))
    lab = (f'<text x="{glyphs.XL - CAP * 0.10:.0f}" y="{-(y0 + ray * 0.66):.0f}" fill="{INK}" '
           f'font-size="{CAP * 0.15:.0f}" font-family="ui-sans-serif,system-ui,sans-serif" '
           f'text-anchor="end">90&#176;</text>'
           f'<text x="{glyphs.XL + ray * 1.16:.0f}" y="{-(y0 + ray * 0.52):.0f}" fill="{ACC}" '
           f'font-size="{CAP * 0.15:.0f}" font-family="ui-sans-serif,system-ui,sans-serif">'
           f'{math.degrees(ang):.0f}&#176;</text>')
    pad, room = 90.0, CAP * 0.60      # room for the angle labels on the left
    return svg(glyphs.GW + 120 + 2 * pad + room, CAP + 2 * pad,
               "\n".join(body) + "\n" + lab, glyphs.L - 60 - pad - room, -CAP - pad)


FILES = {"alphabet.svg": alphabet, "waterfall.svg": waterfall,
         "parts.svg": parts, "arch.svg": arch_study}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FILES.items():
        open(os.path.join(OUT, name), "w").write(fn())
    print(f"{len(FILES)} specimens -> {OUT}")
