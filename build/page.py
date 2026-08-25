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


plate_m = plate("M", "The lobe as the A",
    "K's construction at a lighter setting: the mark's pen is the word's pen, the tracking is "
    "closed to nothing, the arch is a shade softer (exponent 3.2 against the face's 2.5), and "
    "the crest is marked with a small &times; cut from the wave itself rather than a dot. Shown "
    "bare, which is the chosen cut; then carried, with the ghost and the rule; then L, the same "
    "family laid on one rule under the whole name.",
    single("M-lockup", "M-carried", "L-lockup", tag="L"),
    "Reads as a wordmark first and a diagram second, which is the right order for a name, and sits beside other type without "
    "arguing with it.",
    "There is no heavy element to carry it small. Below about 160&nbsp;px wide the &times; goes "
    "first and the lobe soon after; use the icon cut there, and the one-ink cut wherever rust "
    "cannot be guaranteed. Every cut ships in one ink.")


plate_k = plate("K", "Two antinodes, at working weight",
    "C's reading — one phase solid, the opposite ghosted, the antinode marked — cut down to a "
    "single wavelength and drawn at the weight of the logo already in use. One crest, one trough, "
    "a dot on each: those two points are the only places on a standing wave that swing furthest "
    "from rest, which is the whole name. The mark carries the punch so the name does not have to, "
    "and stays in the face's own light weight — <strong>4&times;</strong> the difference. Two "
    "colour by default; every cut also ships in one ink.",
    single("K-lockup", "K-quiet", "K-stacked", tag="K"),
    "The most flexible thing here by a distance. The mark splits off cleanly for a favicon or an "
    "app tile, the lockup drops into the slot your current logo already occupies, and nothing in "
    "it depends on the reader completing a letter.",
    "The mark and the name are pulling in opposite directions on purpose — heavy against light — "
    "and that only holds while they stay at these relative sizes. Shrink the lockup far enough "
    "and the name thins out before the mark does; below about 120&nbsp;px wide, use the mark "
    "alone.")


plate_j = plate("J", "The drawing, whole",
    "The top sketch, rebuilt to its own measurements. Three lobes above the axis and three "
    "mirrored below — a standing wave drawn at both extremes of its swing, which makes three "
    "lens shapes in a row. The name lives <em>inside</em> them: it starts at the second node "
    "and its set width is exactly one full period, so the word and the wave finish together. "
    "The opening lens is the A. It keeps full ink because it is doing a letter's job; the two "
    "behind the name are the diagram carrying on. Set in <strong>Antinode</strong>, a face cut "
    "for this mark — see below for why it had to be. Shown carried, reflected, then dashed.",
    single("J-lockup", "J-reflected", "J-dashed", tag="J"),
    "Every number in it was traced off the photograph, not chosen — the proportions and the "
    "weights both. Four pens, in the ratio the pencil actually holds: the name is the heaviest "
    "thing in the mark, the drawn lobe and the axis sit under it, and the carried lobes are a "
    "trace. All four are ratios of the typeface's own stroke, so the whole mark re-weights if "
    "the face does.",
    "The carried lobes cross the letters, which is what the pencil does too — and at "
    "0.30&thinsp;&times; the letter stroke they are the first thing to go at small sizes. That "
    "is what the redrawn icon cut is for; do not shrink the display cut past about 80&nbsp;px.")


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

plates = [group("Where it landed",
                "One weight, one line, one idea: the A is the antinode."),
          plate_m,
          group("The working-weight version",
                "Heavy mark, quiet name, two colours — C's idea at the weight and flexibility "
                "of the logo already in use."),
          plate_k,
          group("What you actually drew",
                "Three lobes, their mirrors, and the name inside them — measured off the "
                "photograph and rebuilt, in a face cut for it."),
          plate_j,
          group("The sketch, read right",
                "The same reading, stripped to one lobe and set in a borrowed face. Where this "
                "started."),
          plate_h,
          group("The vertical set",
                "Built from the rotated photo, before the drawing was read the right way up. A "
                "different logo from the one on the paper, but finished — and the only cuts that "
                "give a tall lockup."),
          plates[0], plates[1], plates[2]]

FACES = [
    ("face-anybody-quiet", "Anybody Expanded Thin <span>200 / 150</span>",
     "The widest here and the closest to <em>Dune</em> — stretched almost past comfort, which is "
     "exactly where those titles live."),
    ("face-saira-quiet", "Saira Expanded Light <span>200 / 125</span>",
     "The same move, less extreme. Neutral enough to carry a whole identity rather than one title card."),
    ("face-encodesans-quiet", "Encode Sans Expanded Thin <span>200 / 125</span>",
     "A shade more mechanical than Saira. The flattened O keeps it from turning decorative."),
    ("face-outfit-quiet", "Outfit Thin <span>200</span>",
     "Pure geometry — circular O, single-storey forms. <em>Passengers</em> rather than <em>Dune</em>: "
     "not wide, just quiet."),
    ("face-josefin-quiet", "Josefin Sans Thin <span>200</span>",
     "Deco bones under the sci-fi. Small caps for its em, so it sets lighter than it measures."),
    ("face-exo2-quiet", "Exo 2 Thin <span>150</span>",
     "The most adjustable of the set — weight is a dial rather than a decision."),
    ("face-jura-quiet", "Jura Light <span>300</span>",
     "The floor of its axis, and still the closest of any of them to the hand in the sketch."),
    ("face-megrim-quiet", "Megrim <span>static</span>",
     "Compass and ruler, nothing else. The most delicate thing on the page and the most fragile — "
     "its E is a constructed oddity you either love or redraw."),
    ("face-orbitron-quiet", "Orbitron <span>400, its floor</span>",
     "Kept only to mark the boundary: its lightest weight is still the heaviest thing here. Square "
     "sci-fi cannot reach the register those films sit in."),
    ("H-quiet", "Cormorant Garamond Light <span>the incumbent</span>",
     "High contrast, so the wave's pen can only ever split the difference between hairline and stem."),
]

faces_html = "\n".join(
    f'<div class="face"><div class="meta"><span class="nm">{name}</span>'
    f'<p class="why">{why}</p></div>{d["marks"][key]}</div>'
    for key, name, why in FACES)

subs = {"FACES": faces_html, "ANTINODE_WOFF2": d["antinode"]["woff2"],
        "ANTINODE_OTF": d["antinode"]["otf"], "FONT_REGULAR": d["faces"]["regular"], "FONT_BOLD": d["faces"]["bold"],
        "FONT_BLACK": d["faces"]["black"], "FONT_BLACKIT": d["faces"]["blackit"],
        "SKETCH": d["sketch"], "PLATES": "\n".join(plates), **d["marks"]}

missing = [k for k in re.findall(r"\{\{([\w-]+)\}\}", tpl) if k not in subs]
assert not missing, f"no asset for: {missing}"
out = re.sub(r"\{\{([\w-]+)\}\}", lambda m: subs[m.group(1)], tpl)
assert "{{" not in out
open(os.path.join(HERE, os.pardir, "index.html"), "w").write(out)
print(f"index.html  {len(out) / 1024:.0f}KB  ({len(re.findall(r'<svg', out))} inline marks)")
