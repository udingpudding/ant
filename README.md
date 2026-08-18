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

## Typeface study

`type-study/` cuts the same H lockup in nine faces, plus Cormorant for comparison. The register
the reference films share — *Dune*, *Passengers*, *Stowaway* — is thin, wide and generously
tracked: quiet and technical rather than the heavy square sci-fi of a game title. So each face
sits near the light end of its weight axis, and the wide ones are pushed out on width as well.

Anybody Expanded Thin, Saira Expanded Light, Encode Sans Expanded Thin, Outfit Thin, Josefin Sans
Thin, Exo 2 Thin, Jura Light, Megrim, and Orbitron — the last kept only to mark the boundary,
since its lightest weight is still the heaviest of the set. Two cuts per face: `-carried` with
the wave running behind the name, `-quiet` with just the opening lobe.

Monoline matters here beyond the look. A high-contrast serif has no single stroke for the wave
to match, so its pen is a compromise between hairline and stem. A monoline face has exactly one
stroke, and `Face.pen()` hands the wave that number — the curve and the letters become literally
the same pen. Every weight on this page is measured off its own font's `O`, never chosen.

None of the six has the sketch's **arched N** (`∩`), which is the lobe's own form one size down.
That would have to be drawn.

## Rebuilding

Nothing is traced or hand-tuned. The lobes are a real sine, the letters are real font
outlines converted to paths, and stroke weights are measured off the typefaces.

```sh
cd build
python3 -m pip install fonttools brotli
python3 build-antinode.py     # rewrites ../logos and ../type-study
python3 assets.py             # subsets fonts, bundles the marks
python3 page.py               # rewrites ../index.html
```

Optional, and worth it — it takes about 15% off the paths:

```sh
npx svgo -f logos -f type-study --multipass   # from the repo root, between steps one and two
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
