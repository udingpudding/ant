#!/usr/bin/env python3
"""Skeleton-to-outline geometry: everything the face is drawn with.

A glyph here is a skeleton — polylines and parametric curves — inflated to a
constant width. That is the whole conceit of the face: one pen across the
alphabet, and every weight in the mark is set as a ratio of it. Nothing is
drawn as a filled shape by hand.
"""
import math

# ---------------------------------------------------------------- contours
# A contour is a start point plus a list of ops:
#   ("l", (x, y))                 line to
#   ("c", (c1, c2, (x, y)))       cubic to
# Contours are closed implicitly.


class Contour:
    def __init__(self, start):
        self.start = start
        self.ops = []
        self.hole = False

    def line(self, p):
        self.ops.append(("l", p))
        return self

    def curve(self, c1, c2, p):
        self.ops.append(("c", (c1, c2, p)))
        return self

    def points(self):
        """Every on-curve point, for area and bounds."""
        out = [self.start]
        for kind, v in self.ops:
            out.append(v if kind == "l" else v[2])
        return out

    def area(self):
        """Signed area of the on-curve polygon. Negative = clockwise in y-up."""
        p = self.points()
        return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1]
                   for i in range(len(p))) / 2

    def reverse(self):
        """Walk the same contour backwards. points() is [S, P1 .. Pn] and ops[i]
        runs points[i] -> points[i+1]; the close runs Pn -> S. Reversed, we
        start at Pn, replay each op backwards with its handles swapped, and the
        implicit close takes S back to Pn."""
        pts = self.points()
        out = Contour(pts[-1])
        out.hole = self.hole
        for i in range(len(self.ops) - 1, -1, -1):
            kind, v = self.ops[i]
            if kind == "l":
                out.line(pts[i])
            else:
                out.curve(v[1], v[0], pts[i])
        return out

    def wind(self, clockwise=True):
        """Force a direction. Nonzero fill unions same-direction contours, so
        every outer contour must agree and every hole must disagree."""
        if (self.area() < 0) != clockwise:
            return self.reverse()
        return self

    def draw(self, pen):
        pen.moveTo(self.start)
        for kind, v in self.ops:
            pen.lineTo(v) if kind == "l" else pen.curveTo(*v)
        pen.closePath()

    def svg(self):
        d = [f"M {self.start[0]:.1f} {self.start[1]:.1f}"]
        for kind, v in self.ops:
            if kind == "l":
                d.append(f"L {v[0]:.1f} {v[1]:.1f}")
            else:
                (a, b, c) = v
                d.append(f"C {a[0]:.1f} {a[1]:.1f} {b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}")
        return " ".join(d) + " Z"

    def transform(self, fn):
        out = Contour(fn(self.start))
        out.hole = self.hole
        for kind, v in self.ops:
            out.line(fn(v)) if kind == "l" else out.curve(fn(v[0]), fn(v[1]), fn(v[2]))
        return out


def poly(pts):
    """A closed contour of straight edges."""
    c = Contour(pts[0])
    for p in pts[1:]:
        c.line(p)
    return c


# ---------------------------------------------------------------- polylines
def _unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n) if n else (0.0, 0.0)


def arclen(pts):
    return [0.0] + list(_cum(pts))


def _cum(pts):
    s = 0.0
    for a, b in zip(pts, pts[1:]):
        s += math.hypot(b[0] - a[0], b[1] - a[1])
        yield s


def resample(pts, n):
    """n+1 points spaced evenly by arc length. Keeps both ends exactly."""
    s = arclen(pts)
    total = s[-1]
    out, j = [], 0
    for i in range(n + 1):
        t = total * i / n
        while j + 1 < len(s) - 1 and s[j + 1] < t:
            j += 1
        span = s[j + 1] - s[j]
        f = 0.0 if span == 0 else (t - s[j]) / span
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return out


def resample_turn(pts, n, k=140.0):
    """Resample so each span carries the same amount of *bending*, not the same
    length. Arc-length spacing under-resolves the corners of a high-exponent
    superellipse, which is exactly where a fitted cubic drifts."""
    acc, prev = [0.0], None
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        t = _unit((b[0] - a[0], b[1] - a[1]))
        turn = 0.0
        if prev:
            dot = max(-1.0, min(1.0, prev[0] * t[0] + prev[1] * t[1]))
            turn = math.acos(dot)
        prev = t
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]) + k * turn)
    total, out, j = acc[-1], [], 0
    for i in range(n + 1):
        t = total * i / n
        while j + 1 < len(acc) - 1 and acc[j + 1] < t:
            j += 1
        span = acc[j + 1] - acc[j]
        f = 0.0 if span == 0 else (t - acc[j]) / span
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return out


def offset_poly(pts, d):
    """Miter offset. Exact for the polyline: each vertex moves along the
    bisector by d / cos(half-angle), so the band's width is d everywhere."""
    n = len(pts)
    segn = []
    for a, b in zip(pts, pts[1:]):
        t = _unit((b[0] - a[0], b[1] - a[1]))
        segn.append((-t[1], t[0]))          # left normal
    out = []
    for i in range(n):
        if i == 0:
            nx, ny = segn[0]; scale = 1.0
        elif i == n - 1:
            nx, ny = segn[-1]; scale = 1.0
        else:
            u, v = segn[i - 1], segn[i]
            bx, by = _unit((u[0] + v[0], u[1] + v[1]))
            cos_half = bx * u[0] + by * u[1]
            nx, ny = bx, by
            scale = 1.0 / cos_half if abs(cos_half) > 0.2 else 5.0
        out.append((pts[i][0] + nx * d * scale, pts[i][1] + ny * d * scale))
    return out


def catmull(pts):
    """Polyline -> C1 cubic chain. Tangent at P[i] is (P[i+1]-P[i-1])/2, so the
    handles are a sixth of the neighbouring chord — a Catmull-Rom spline
    written in Bezier form."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    c = Contour(pts[0])
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        c.curve(c1, c2, p2)
    return c


def _bez(p0, c1, c2, p3, t):
    u = 1 - t
    return (u*u*u*p0[0] + 3*u*u*t*c1[0] + 3*u*t*t*c2[0] + t*t*t*p3[0],
            u*u*u*p0[1] + 3*u*u*t*c1[1] + 3*u*t*t*c2[1] + t*t*t*p3[1])


def fit_error(contour, pts):
    """Largest distance from the dense polyline to the fitted cubic chain."""
    sampled = []
    cur = contour.start
    for kind, v in contour.ops:
        if kind == "l":
            sampled += [cur, v]; cur = v
        else:
            c1, c2, p = v
            sampled += [_bez(cur, c1, c2, p, i / 12) for i in range(13)]
            cur = p
    # both lists run along the curve in the same order, so the nearest edge is
    # always near the proportional index — a window keeps this linear
    edges = list(zip(sampled, sampled[1:]))
    step = max(1, len(pts) // 120)          # 120 probes is plenty for a max
    return max(min(_seg_dist(pts[i], a, b) for a, b in edges)
               for i in range(0, len(pts), step))


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = 0.0 if n == 0 else max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / n))
    return math.hypot(p[0] - (a[0] + dx*t), p[1] - (a[1] + dy*t))


# ---------------------------------------------------------------- the pen
def stroke_line(pts, w):
    """A straight-sided skeleton inflated to width w, butt ends, miter joins.
    Exact — no fitting, so stems and diagonals carry no error at all."""
    a = offset_poly(pts, w / 2)
    b = offset_poly(pts, -w / 2)
    return poly(a + list(reversed(b)))


def stroke_curve(pts, w, segments=10):
    """A sampled curve inflated to width w and refitted as cubics.

    The skeleton is resampled by arc length, offset both ways, then each side
    is subsampled to `segments` spans and splined. Returns the contour and the
    worst fitting error so the caller can assert on it.
    """
    dense = resample(pts, 400)
    a_d, b_d = offset_poly(dense, w / 2), offset_poly(dense, -w / 2)
    a_f, b_f = resample_turn(a_d, segments), resample_turn(b_d, segments)
    ca, cb = catmull(a_f), catmull(list(reversed(b_f)))
    err = max(fit_error(ca, a_d), fit_error(cb, list(reversed(b_d))))
    c = Contour(ca.start)
    c.ops = list(ca.ops)
    c.line(cb.start)
    c.ops += list(cb.ops)
    return c, err


# ---------------------------------------------------------------- curves
K = 0.5522847498307936          # circle-to-cubic constant


def ellipse(cx, cy, rx, ry, clockwise=True):
    """Four cubics. 0.02% off a true ellipse, an order under the pen."""
    q = [(cx + rx, cy), (cx, cy + ry), (cx - rx, cy), (cx, cy - ry)]
    h = [((cx + rx, cy + ry * K), (cx + rx * K, cy + ry)),
         ((cx - rx * K, cy + ry), (cx - rx, cy + ry * K)),
         ((cx - rx, cy - ry * K), (cx - rx * K, cy - ry)),
         ((cx + rx * K, cy - ry), (cx + rx, cy - ry * K))]
    c = Contour(q[0])
    for i in range(4):
        c.curve(h[i][0], h[i][1], q[(i + 1) % 4])
    return c.wind(clockwise)


def ring(cx, cy, rx, ry, w):
    """Two concentric ellipses, opposite winding. A real hole, not an overlap."""
    outer = ellipse(cx, cy, rx + w / 2, ry + w / 2, True)
    inner = ellipse(cx, cy, rx - w / 2, ry - w / 2, False)
    inner.hole = True
    return [outer, inner]


def superellipse_pts(cx, cy, a, b, n, t0, t1, steps=400):
    """|x/a|^n + |y/b|^n = 1, walked by angle from t0 to t1 (radians).

    n = 2 is an ellipse; above 2 the corners square up. The face uses ~2.35:
    flat enough on top to read as a shoulder, and vertical where it lands on a
    stem — which a sine lobe never is (its tangent at the node is 68 degrees).
    """
    out = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        ct, st = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(ct) ** (2 / n), ct)
        y = b * math.copysign(abs(st) ** (2 / n), st)
        out.append((cx + x, cy + y))
    return out


def arc_pts(cx, cy, rx, ry, a0, a1, steps=400):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / steps),
             cy + ry * math.sin(a0 + (a1 - a0) * i / steps)) for i in range(steps + 1)]
