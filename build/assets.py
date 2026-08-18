#!/usr/bin/env python3
"""Prepare everything index.html inlines: subset page fonts, the sketch photo,
and currentColor copies of every mark so they can take the page's colour."""
import base64, json, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
LOGOS = os.path.join(HERE, os.pardir, "logos")
TMP = os.path.join(HERE, "tmp")
TYPE = os.path.join(HERE, os.pardir, "type-study")
SKETCH = os.path.join(HERE, "sketch.jpg")
FONTS = os.path.join(HERE, "fonts")

# every character the page sets, plus the symbols the spec table uses
CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         " .,:;'\"!?()[]{}/\\-–—·×÷°+=<>%&@#*~^_|λπμ≈±→…‘’“”")

CUTS = {
    "regular": ("Archivo[wdth,wght].ttf", {"wght": 400, "wdth": 100}),
    "bold":    ("Archivo[wdth,wght].ttf", {"wght": 700, "wdth": 100}),
    "black":   ("Archivo[wdth,wght].ttf", {"wght": 800, "wdth": 100}),
    "blackit": ("Archivo-Italic[wdth,wght].ttf", {"wght": 800, "wdth": 100}),
}

faces = {}
for name, (fname, axes) in CUTS.items():
    font = instancer.instantiateVariableFont(TTFont(os.path.join(FONTS, fname)), axes, inplace=False)
    opts = subset.Options(layout_features=["kern", "liga"], desubroutinize=True)
    opts.flavor = "woff2"
    sub = subset.Subsetter(options=opts)
    sub.populate(text=CHARS)
    sub.subset(font)
    font.flavor = "woff2"
    path = os.path.join(TMP, f"_archivo-{name}.woff2")
    font.save(path)
    faces[name] = base64.b64encode(open(path, "rb").read()).decode()
    print(f"  archivo {name:8s} {os.path.getsize(path) / 1024:5.1f}KB")

# the sketch photo is a committed input: levels already stretched so the
# graphite reads against the grey paper
sketch = base64.b64encode(open(SKETCH, "rb").read()).decode()

marks = {}
for folder in (LOGOS, TMP, TYPE):
    for f in sorted(os.listdir(folder)):
        if not f.endswith(".svg"):
            continue
        s = open(os.path.join(folder, f)).read().strip()
        s = s.replace("#141312", "currentColor").replace("#2d6b5f", "var(--rust)")
        s = re.sub(r'\swidth="[\d.]+"\sheight="[\d.]+"', "", s, count=1)
        key = f[:-4].replace("antinode-", "")
        marks[("face-" + key) if folder == TYPE else key] = s

bundle = os.path.join(TMP, "_assets.json")
json.dump({"faces": faces, "sketch": sketch, "marks": marks}, open(bundle, "w"))
print(f"  sketch {os.path.getsize(SKETCH) / 1024:.0f}KB · {len(marks)} marks "
      f"· bundle {os.path.getsize(bundle) / 1024:.0f}KB")
