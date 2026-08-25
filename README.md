# ant

Logo study for **ANTINODE** — an antinode being the point of a standing wave that
swings furthest from rest.

Open [`index.html`](index.html) in a browser. It is self-contained: fonts, the sketch
photo and every mark are inlined, so it works from `file://` with nothing served.

## What is here

`logos/` holds the vector masters. **J**, **K** and **L/M** are set in Antinode, the face drawn
for them (`font/`); everything else is Cormorant Garamond Light.

**L/M — the K family at the bench's numbers.** The pick. K's construction cut lighter — the
mark's pen is the word's pen, 1.01× — with the crest marked by a small × cut from the wave
itself (the rising and falling phases, the same two lines the wave is drawn from) instead of a
dot. Laid out two ways. **L** puts the axis on the baseline: the rule runs past the wave and
under the whole name. **M** puts the lobe in the A's slot, spaced as a letter, and NTINODE runs
out of it along the same line — the sketch's own reading, at a weight that can stand beside
other type. M is the one that ships.

These marks alone are cut at a softer arch than the face (superellipse exponent 3.2 against the
shipping 2.5); the override is local to them, because changing it globally re-spaces the glyphs
and J's word no longer measures one period.

The numbers are the bench's *Light* preset and its cross, pasted from the spec it prints. Three
depart from the bench's defaults on purpose: tracking 0 (bench 0.11), no leg on M's lobe (bench
0.14), and only the crest marked (the bench marks the trough too). Retune on the bench, then
paste into `build-antinode.py`.

| file | |
|---|---|
| `M-lockup` | **primary** — the lobe as the A, bare |
| `M-carried` | with the ghosted phase carried under the name, and the rule |
| `L-lockup` | the axis as baseline, rule under the whole name |
| `L-icon` | one antinode, redrawn at this family's numbers |
| `*-1c` | each of the above in one ink |
| `*.png` | each of the above rasterised at 4×, transparent |

**K — two antinodes, at working weight.** C's reading — one phase solid, the opposite ghosted,
the antinode marked — cut to a single wavelength and drawn at the weight of the logo already in
use. One crest, one trough, a dot on each: those two points are the only places on a standing
wave that swing furthest from rest, which is the whole name.

The mark carries the punch so the name does not have to. The mark's pen is **4× the word's**,
and the word stays in the face's own light weight, wide and tracked. Two colour by default —
rust mark, ink name — with a one-ink cut (`-1c`) of everything alongside.

Two things learned by building it, both worth keeping:

- The ghost and the rule have to be **hairlines**. At the mark's own weight the dashes collide
  with the solid phase at every node and the whole thing turns to noise.
- A closed lens on its own **reads as a diamond** at every weight tried. It is the rule through
  it that says the shape is swinging about a rest position — which is why the icon keeps the
  axis and drops everything else.

| file | |
|---|---|
| `K-lockup` | **primary** — mark left, name right, on one axis |
| `K-quiet` | without the ghosted phase |
| `K-bare` | without the ghost or the rule — closest to the logo in use |
| `K-stacked` | mark over name, name set to the mark's width |
| `K-mark` | the wave alone |
| `K-icon` | one antinode, redrawn: lens plus rule, no dashes, no dot |
| `K-word` | ANTINODE set plain |

**J — the drawing, whole.** The top sketch rebuilt to its own measurements. Three lobes above the
axis, three mirrored below — a standing wave at both extremes of its swing, which makes three lens
shapes in a row. The name lives *inside* them: it starts at the second node and its set width is
exactly one full period, so word and wave finish together. The opening lens is the A; it keeps
full ink because it is doing a letter's job, and the two behind the name are the diagram carrying
on.

Nothing in it was chosen by eye. The wave's upper envelope was traced column by column off the
photograph, the axis found from its ink profile, the lettering measured from its bounding box:

| measured on the photo | | in cap heights |
|---|---|---|
| cap height | 31 px | 1.00 |
| amplitude, axis to crest | 85 px | **2.74** |
| half period, node to node | 112 px | **3.61** |
| word set width | 217 px | **7.00** — one full period |
| stroke | ~3 px | 0.095 |

The build asserts the word measures `2 × L` to within half a unit and fails if a glyph ever
changes width.

The weights were probed the same way — vertically through the crest, horizontally through the
stems — and they are **not** all one pen. The pencil holds a clear hierarchy:

| | on the photo | at cap 100 |
|---|---|---|
| the letters | 4 px | `9.43` |
| the drawn lobe | 3 px | `6.98` |
| the axis | 2–3 px | `6.22` |
| the carried lobes | 1 px | `2.83` |
| the × at the crest | heaviest | `11.87` |

The name is the heaviest thing in the mark, the wave is a drawing behind it, and the carried part
is a trace. Each weight is a ratio of the typeface's own stroke (`glyphs.W / glyphs.CAP`), so
changing the face re-weights the whole mark. The carried lobes are thin rather than tinted —
an opacity does not survive one-colour printing.

| file | |
|---|---|
| `J-lockup` | **primary** — first lens at full weight, the carried two as hairlines, × at the crest |
| `J-plain` | the same without the × |
| `J-reflected` | plus the mirrored word below the axis, as the sketch draws it |
| `J-dashed` | the carried lobes dashed instead of tinted |
| `J-solid` | every lens at the wave's weight, no decay |
| `J-mark` | the three-lens figure alone |
| `J-stacked` | mark over word, widths aligned |
| `J-icon` | one lens, redrawn at the small cut's weight (`-cross` adds the ×) |
| `J-word` | ANTINODE set plain (`-alt` uses the round E) |

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

## The typeface

In the sketch both N's are arches — the wave's lobe one size down. **No shipping font has that
letter**, so every cut before J had to substitute a diagonal N and lose the idea. So it was drawn.

`font/Antinode-Regular.{otf,ttf,woff2}` — a monoline geometric face, A–Z, 0–9 and basic
punctuation, 54 glyphs over 78 codepoints. Lowercase is mapped to the caps so it never drops a
character. Built from scratch with fontTools; there is no source in Glyphs or FontForge, because
there are no hand-placed points to keep — `build/glyphs.py` *is* the source.

The system it buys: one superellipse (exponent 2.5; L/M alone are cut at 3.2) does the arch work — the wave's lobe, the N,
the A (the same arch with a bar, which is exactly what the axis does to the opening lens), the U
inverted, D's bowl turned a quarter, and the E's. The round letters — O, C, G, Q, S and the digit
bowls — are ellipses. `specimen/parts.svg` draws it.

Moving the round group onto the superellipse too was tried and reverted. A superellipse only parts
company with an ellipse when it is far from square, and the O is 247&times;328 — near enough to
circular that at exponent 2.5 the two curves differ by a couple of percent. It changed sixteen
glyphs to fix one and none of it was visible. The exponent, not the curve family, is the control
that moves; the bench carries it.

Why a superellipse and not the sine itself: over the same span the two nearly agree, but at the
node a sine leaves the axis at 63° and a letter has to stand at 90°. `specimen/arch.svg`.

| | |
|---|---|
| metrics | 1000 upem, cap 700, pen **66** (0.094 cap), width 560 (0.80 cap), sidebearing 91 |
| method | skeletons miter-offset to constant width, refitted as cubics |
| accuracy | band width 66.000 units at every sample; worst curve fit **0.44 units**, 0.06% of cap |
| features | `ss01` swaps in the conventional square E; `kern` carries 16 pairs |
| spacing | fitted per glyph, not one advance for all — see below |
| overlaps | removed with skia-pathops — clean cuts, not contours relying on winding order |

**The E is the sketch's**: a C-form, closed left, open right, with a middle arm that stops short
of the bowl's widest point so all three right-hand ends line up on one vertical. That alignment
is what makes it an E and not a euro sign; the opening is what keeps it off a theta, which a
closed bowl reads as at every weight tried. The conventional spine-and-three-arms cut is on
`ss01`.

**Spacing is fitted per glyph.** One advance for every glyph is what makes a monoline face look
gappy — a bare stem like the I floats in a box built for an O. Each glyph is now fitted to its own
ink, with the sidebearing chosen by what sits at the edge: a flat stem needs the most air, a curve
meets its neighbour at a single point and needs less, an open corner already carries its own white
and needs least. The I went from a 742-unit advance to 248. Measured over ANTINODE — mean optical
gap 176 units, spread **4%** of the mean. Figures are tabular so columns line up.

Seven letters come straight off your paper — **A N T I O D E**. The other nineteen are
extrapolated to the same rules; **B G K Q R S W** are the ones to look hardest at. The one place
the face could be judged confusable is that A and N differ only by a bar. That is the system, and
it is why the mark works; if it bothers you when set, the fix is to splay the A's legs slightly
and keep the arch shared.

## Typeface study, before it was drawn

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

None of the nine has the sketch's **arched N** (`∩`). That is what sent this to a drawn alphabet.
They stay on the board because the search is worth seeing — and because if the drawn face is ever
the wrong answer, **Saira Expanded Light** is where I would go instead.

## Rebuilding

Nothing is traced or hand-tuned. The lobes are a real sine, the letters are real font
outlines converted to paths, and stroke weights are measured off the typefaces.

```sh
python3 -m pip install fonttools brotli skia-pathops
./build/rebuild.sh
```

That is the whole chain in the one order that works — font, marks, specimens, svgo, page. Run
the steps by hand if you like, but note **svgo only honours a single `-f` per invocation**:
passing three folders silently optimises only the last, and `build-antinode.py` rewrites
`type-study/` as well as `logos/`, so both need a pass after it.

The last step rasterises the L/M cuts to PNG at 4× with headless Chrome (`CHROME=` to point it
elsewhere; skipped with a warning if absent). Chrome and not ImageMagick because ImageMagick's
own SVG parser silently drops the rust wave.

`skia-pathops` is optional. Without it the fonts still render correctly — nonzero winding unions
same-direction contours — but the build says so instead of claiming a clean cut.

`build/geom.py` is the geometry engine (skeleton → constant-width outline), `build/glyphs.py` the
alphabet, `build/setter.py` sets text from those outlines without the font installed. Change the
pen or the width in `glyphs.py` and the whole face re-cuts — and the wordmark with it.

## Still to do

A one-colour reversed set, and clear-space plus minimum-size rules, for M now that it is
picked.

## Type

**Antinode** is drawn here — see `font/`. It carries Uday Sapra as designer and
"all rights reserved" in its name table; change that in `build/antinode_font.py` before it
goes anywhere.

A–C and H are set in [Cormorant Garamond](https://github.com/CatharsisFonts/Cormorant); this page
is set in [Archivo](https://github.com/google/fonts/tree/main/ofl/archivo). Both SIL Open Font
License — see `build/fonts/`. Every wordmark is outlined, so no font is needed to render a logo.
