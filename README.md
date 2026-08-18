# ant

Logo study for **ANTINODE** — an antinode being the point of a standing wave that
swings furthest from rest.

Open [`index.html`](index.html) in a browser. It is self-contained: fonts, the sketch
photo and every mark are inlined, so it works from `file://` with nothing served.

## What is here

`logos/` holds the vector masters, black on transparent, all set in Cormorant Garamond Light.

**H — the implied A.** The sketch, read whole. The axis runs horizontally and the name stands
on it, and the wave's opening crest is not *beside* the A — it **is** the A, sitting in its slot
with the rule crossing it where the bar would go. That is why only the first lobe is solid: it is
the one doing a letter's job, and the wave carried on behind the name is the diagram.

| file | |
|---|---|
| `H-lockup` | the wave carried behind the whole name, ghosted |
| `H-quiet` | just the opening lobe and its opposite phase |
| `H-bare` | the lobe alone, no ghost, no × |
| `H-nocross` | carried, without the × at the crest |
| `H-icon` | the A on its own, at the small cut's weight |

**A, B, C — the vertical set.** Three antinodes both phases solid; one lobe one side; and one
instant solid with the other ghosted. Each ships stacked, horizontal, mark and icon.

These stand on a *vertical* axis because the first photo of the sketch arrived rotated a quarter
turn. Righted, the drawing is horizontal — that is what H is. A–C are finished work either way,
and they are the only cuts that give a tall lockup.

An Archivo family (D–G) was cut and dropped: too thick for the drawing, and it kept arriving at
type sitting beside a wave rather than type made out of one. It is in the first commit if it is
ever wanted.

Every direction ships a display cut and an **icon cut**. The icon is redrawn, not resized: below
roughly 80px the display stroke goes sub-pixel and the mark greys out, so the icon takes a tighter
crop, a heavier stroke, and no dashes.

## Rebuilding

Nothing is traced or hand-tuned. The lobes are a real sine, the letters are real font
outlines converted to paths, and stroke weights are measured off the typefaces.

```sh
cd build
python3 -m pip install fonttools brotli
python3 build-antinode.py     # rewrites ../logos
python3 assets.py             # subsets fonts, bundles the marks
python3 page.py               # rewrites ../index.html
```

Optional, and worth it — it takes about 15% off the paths:

```sh
npx svgo -f logos --multipass   # from the repo root, between the first and second step
```

## Still to do

Waiting on a direction being picked, since there is no sense cutting these four times
over: PNG exports at set sizes, a one-colour reversed set, and clear-space plus
minimum-size rules.

## Type

The logos are [Cormorant Garamond](https://github.com/CatharsisFonts/Cormorant); this page
is set in [Archivo](https://github.com/google/fonts/tree/main/ofl/archivo). Both SIL Open
Font License — see `build/fonts/`. The wordmarks are outlined, so neither font is needed
to render a logo.
