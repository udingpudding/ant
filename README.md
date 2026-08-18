# ant

Logo study for **ANTINODE** — an antinode being the point of a standing wave that
swings furthest from rest.

Open [`index.html`](index.html) in a browser. It is self-contained: fonts, the sketch
photo and every mark are inlined, so it works from `file://` with nothing served.

## What is here

`logos/` holds the vector masters, black on transparent. Seven directions:

| | | |
|---|---|---|
| **G** | On the line | the sketch read the right way up — horizontal axis, word standing on it, one antinode around the opening letter. Cut in Archivo, in Archivo with the opposite phase dashed, and in Cormorant. |
| **D** | Reflection | the word on the axis with its own reflection beneath. Solid, and with the reflection reduced to an outline. |
| **E** | Enclosed | the word inside one antinode. |
| **F** | Enclosed pair | the word and its reflection, both inside one antinode. |
| **A** | Standing wave | three antinodes, both phases solid. Vertical. |
| **B** | Single antinode | one lobe, one side. Vertical. |
| **C** | Phase | one instant solid, the other ghosted, the crest marked. Vertical. |

A–C stand on a vertical axis because the first photo of the sketch arrived rotated a
quarter turn. Righted, the drawing is horizontal — that is what G is. A–C are finished
work either way, and they are the only cuts that give a tall lockup.

Each direction ships a display cut and an **icon cut**. The icon is redrawn, not
resized: below roughly 80px the display stroke goes sub-pixel and the mark greys out,
so the icon takes a tighter crop, a stroke about four times heavier, and no dashes.

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

Waiting on a direction being picked, since there is no sense cutting these seven times
over: PNG exports at set sizes, a one-colour reversed set, and clear-space plus
minimum-size rules.

## Type

[Cormorant Garamond](https://github.com/CatharsisFonts/Cormorant) and
[Archivo](https://github.com/google/fonts/tree/main/ofl/archivo), both SIL Open Font
License — see `build/fonts/`. The wordmarks are outlined, so neither font is needed to
render a logo.
