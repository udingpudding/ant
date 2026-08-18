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


plate_h = plate("H", "The implied A",
    "The sketch, whole. The axis runs horizontally and the name stands on it, and the wave's "
    "opening crest is not next to the A — it <em>is</em> the A, sitting in its slot with the rule "
    "crossing it where the bar would go. That is why only the first lobe is solid: it is the one "
    "doing a letter's job, and the wave carrying on behind the name is the diagram, drawn as one. "
    "Shown carried, then quiet, then bare.",
    single("H-lockup", "H-quiet", "H-bare", tag="H"),
    "The name has one letter fewer to set and one more thing to say. Horizontal, so it fits a "
    "header, a card and an app bar with no second lockup, and the A alone makes the mark.",
    "It only works while a reader completes the A. Set it too small, or crop the lobe out, and the "
    "word starts at N.")

plates = [
    plate("A", "Standing wave",
          "Three antinodes, both phases solid — the whole figure, every position the string passes "
          "through. Built from the rotated photo, so it stands on a vertical axis.",
          split("A"),
          "One closed silhouette. Nothing in it can break at size, on fabric, or in one colour.",
          "The lens chain is handsome enough to read as ornament before it reads as physics."),
    plate("B", "Single antinode",
          "One lobe, one side. The smallest true statement the name can make, and literally the "
          "first lobe of A, so the two are one drawing at different crops.",
          split("B"),
          "Behaves like a letterform. It sits beside type without a fight and survives smallest.",
          "Half a lobe is just a bow. Alone it reads as a <em>D</em> or a <em>P</em> before it reads as a wave."),
    plate("C", "Phase",
          "One instant solid, the opposite instant ghosted, and the crest marked — including the "
          "small &times; you put at the top lobe. That mark is the antinode itself.",
          split("C"),
          "Unmistakably a diagram. Most distinctive of the vertical three, hardest to arrive at by accident.",
          "Dashes break up long before hairlines do. Under roughly 80&nbsp;px it falls back to A's silhouette."),
]

plates = [group("The sketch, read right",
                "The A is never drawn. Start here."),
          plate_h,
          group("The vertical set",
                "Built from the rotated photo, before the drawing was read the right way up. A "
                "different logo from the one on the paper, but finished — and the only cuts that "
                "give a tall lockup."),
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
