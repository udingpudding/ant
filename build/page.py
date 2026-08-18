#!/usr/bin/env python3
"""Assemble index.html: plates for every direction, assets inlined."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "tmp", "_assets.json")))
tpl = open(os.path.join(HERE, "board.tpl.html")).read()

ICON_PX = (16, 24, 32, 48, 64)


def sized(svg, px):
    """Pin an icon to a true pixel height so the size row is not a claim."""
    vb = [float(v) for v in re.search(r'viewBox="([-\d. ]+)"', svg).group(1).split()]
    return svg.replace("<svg ", f'<svg height="{px}" width="{round(px * vb[2] / vb[3], 1)}" ', 1)


def sizes(tag):
    cells = "".join(
        f'<div class="size">{sized(d["marks"][f"{tag}-icon"], px)}'
        f'<span>{px}{" px" if px == ICON_PX[-1] else ""}</span></div>'
        for px in ICON_PX)
    return f'<div class="card sizes">{cells}</div>'


def plate(tag, title, blurb, body, strength, risk):
    return f'''
  <section class="plate">
    <div class="plate-head">
      <div class="row"><span class="tag">{tag}</span><h2>{title}</h2></div>
      <p class="note">{blurb}</p>
    </div>
    {body}
    <dl class="verdict">
      <dt>Strength</dt><dd>{strength}</dd>
      <dt>Risk</dt><dd>{risk}</dd>
    </dl>
  </section>'''


def split(tag):
    return f'''<div class="split">
      <div class="card tall">{d["marks"][f"{tag}-stacked"]}</div>
      <div class="right">
        <div class="card wide">{d["marks"][f"{tag}-horizontal"]}</div>
        {sizes(tag)}
      </div>
    </div>'''


def single(*keys, tag):
    """One card per lockup, then the shared icon row for the family."""
    cards = "\n    ".join(f'<div class="card one">{d["marks"][k]}</div>' for k in keys)
    return f'{cards}\n    {sizes(tag)}'


def group(title, blurb):
    return f'''
  <section class="col" style="gap:.9rem;padding-bottom:0">
    <h2>{title}</h2>
    <p class="note">{blurb}</p>
  </section>'''


plates = [
    plate("A", "Standing wave",
          "Three antinodes, both phases solid — the whole figure, every position the string passes "
          "through. Closest to your third sketch, and the most self-assured of the six.",
          split("A"),
          "One closed silhouette. Nothing in it can break at size, on fabric, or in one colour.",
          "The lens chain is handsome enough to read as ornament before it reads as physics."),
    plate("B", "Single antinode",
          "One lobe, one side — your middle sketch. The smallest true statement the name can make, "
          "and literally the first lobe of A, so the two are one drawing at different crops.",
          split("B"),
          "Behaves like a letterform. It sits beside type without a fight and survives smallest.",
          "Half a lobe is just a bow. Alone it reads as a <em>D</em> or a <em>P</em> before it reads as a wave."),
    plate("C", "Phase",
          "One instant solid, the opposite instant ghosted, and the crest marked — your first sketch, "
          "including the small &times; at the top lobe. That mark is the antinode itself, so the logo "
          "names its own subject.",
          split("C"),
          "The only one that is unmistakably a diagram. Most distinctive, hardest to arrive at by accident.",
          "Dashes break up long before hairlines do. Under roughly 80&nbsp;px it falls back to A's silhouette."),
    plate("D", "Reflection",
          "Sketch two with nothing around it: the word standing on the axis with its own reflection "
          "beneath — the two extremes of the swing, made of type instead of drawn beside it. Shown "
          "solid as you drew it, then with the reflection reduced to an outline.",
          single("D-lockup", "D-ghost", tag="D"),
          "No mark to place. The wordmark <em>is</em> the logo, and it fits wherever a line of type fits.",
          "A mirrored word is a well-worn device. The outline cut is what keeps it from reading as a "
          "reflection effect rather than a wave."),
    plate("E", "Enclosed",
          "The word inside one antinode. The lobe is sized by the word rather than the other way "
          "round — you choose how much of its length the word fills, and the amplitude falls out of "
          "the clearance needed at the ends.",
          single("E-lockup", tag="E"),
          "A closed badge. It stamps, embroiders, and drops into a circular avatar without redrawing.",
          "The lobe reads as an eye or a leaf first. Enclosing the word costs some of the physics."),
    plate("F", "Enclosed pair",
          "Your second sketch, complete: the word on the axis, its reflection under it, both held "
          "inside the lobe. The axis runs node to node, the full span of the antinode.",
          single("F-lockup", tag="F"),
          "Says the most of the six — container, axis and both phases in one shape.",
          "Also carries the most. Two lines of type inside a lobe need room; there is no small "
          "version of this one, which is why D&ndash;F share a separate mark for icon sizes."),
]


plate_g = plate("G", "On the line",
    "The sketch, upright. The axis runs horizontally and the word stands on it, so the line is the "
    "wave's centre and the type's baseline at once. One antinode wraps the opening letter and the "
    "name runs out of it — which is what both sketches do, and what neither of them does is run the "
    "wave the whole length of the word. Shown in Archivo, then with the opposite phase dashed "
    "underneath, then cut in Cormorant.",
    single("G-lockup", "G-phase", "G-serif", tag="G"),
    "The only one that is the drawing on the paper. Horizontal, so it fits a header, a business card "
    "and an app bar without a second lockup.",
    "The lobe hangs below a baseline the type never crosses, so the lower half is empty by design — "
    "that space is the other phase. The dashed cut fills it if the asymmetry reads as a mistake to you.")

plates = [group("The sketch, read right",
                "Start here. This is the horizontal reading, and the one the pencil actually shows."),
          plate_g,
          group("The word as the wave",
                "Three ways to put the type inside the physics rather than beside it — the reflection "
                "you drew, and the two containers it implies."),
          plates[3], plates[4], plates[5],
          group("The vertical set",
                "Built from the rotated photo. A different logo from the one on the paper, but "
                "finished, and the only cuts that give you a tall lockup."),
          plates[0], plates[1], plates[2]]

subs = {"FONT_REGULAR": d["faces"]["regular"], "FONT_BOLD": d["faces"]["bold"],
        "FONT_BLACK": d["faces"]["black"], "FONT_BLACKIT": d["faces"]["blackit"],
        "SKETCH": d["sketch"], "PLATES": "\n".join(plates), **d["marks"]}

missing = [k for k in re.findall(r"\{\{([\w-]+)\}\}", tpl) if k not in subs]
assert not missing, f"no asset for: {missing}"
out = re.sub(r"\{\{([\w-]+)\}\}", lambda m: subs[m.group(1)], tpl)
assert "{{" not in out
open(os.path.join(HERE, os.pardir, "index.html"), "w").write(out)
print(f"index.html  {len(out) / 1024:.0f}KB  ({len(re.findall(r'<svg', out))} inline marks)")
