# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A logo study for **ANTINODE**, plus a monoline typeface drawn for it. Everything shipped
(`logos/`, `type-study/`, `specimen/`, `font/`, `index.html`, `bench.html`) is **generated** —
never hand-edit those; edit the Python in `build/` and rebuild. `README.md` explains the design
reasoning for each direction (A–C, H, J, K, L/M — M is the pick) and the face; read it before
changing a mark.

## Commands

```sh
python3 -m pip install fonttools brotli skia-pathops   # deps (not installed by default here)
./build/rebuild.sh                                     # the whole chain, in the one order that works
```

Individual stages (run from `build/`; each rewrites its output dir wholesale):

| script | writes | notes |
|---|---|---|
| `antinode_font.py` | `font/` | cuts OTF/TTF/WOFF2 from `glyphs.py`; asserts curve fit < 0.5 units |
| `build-antinode.py` | `logos/`, `type-study/` | every mark; asserts J's word measures exactly one period |
| `specimen.py` | `specimen/` | alphabet, waterfall, arch, parts sheets |
| `bench.py` | `bench.html` | inlines 4 cuts of the face at different superellipse exponents |
| `assets.py` → `page.py` | `build/tmp/_assets.json` → `index.html` | subsets page fonts, inlines all marks; must run after svgo |
| (in `rebuild.sh`) | `logos/antinode-{L,M}-*.png` | headless Chrome at 4×, transparent; not ImageMagick, whose SVG parser drops the rust wave |

`rebuild.sh` runs `npx --yes svgo -f <dir> --multipass` on each SVG folder separately (svgo only
honours one `-f`). `build/tmp/` is gitignored scratch.

There is no test suite; the build's `assert`s are the checks. A stage that fails an assert means
the geometry drifted, not that the assert is wrong.

## Architecture

The pipeline is geometry → font → marks → page, with one source of truth at the top:

- **`geom.py`** — skeleton-to-outline: polylines/parametric curves inflated to a constant pen
  width, refitted as cubics. `superellipse_pts` (exponent `ARCH_N`, 2.5) is the single arch that
  builds the N, A, U, D and E; round letters are ellipses. The L/M marks alone are cut at 3.2,
  by a local override in `build-antinode.py` (swap `ARCH_N`, clear `glyphs._cache` and `TAB`,
  restore) — the same trick `antinode_font.woff2_at` uses for the bench.
- **`glyphs.py`** — *is* the font source (no Glyphs/FontForge file exists). Metrics at the top
  (`UPEM`, `CAP`, `W` = the pen, `GW`, `SB`); one `g_<name>()` per glyph returning skeleton
  contours; `GLYPHS` registry, `CMAP`, per-glyph fitted spacing (`SIDE`, `_space`), `build(name)`.
  Change the pen or width here and the whole face, wordmark and bench re-cut.
- **`setter.py`** — sets text straight from `glyphs.build()` contours as SVG paths, so the logo
  generator and specimen never need the font installed. Mirrors `Face.word()` in
  `build-antinode.py`; keep the two interchangeable.
- **`antinode_font.py`** — fontTools `FontBuilder` assembly, skia-pathops overlap removal,
  `ss01` (square E) and `kern`. `woff2_at(exponent)` is what the bench uses.
- **`build-antinode.py`** — every mark. `Face` wraps a shipping TTF (Cormorant, the type-study
  faces) and measures its stroke off the `O` (`Face.pen()`, `hairline()`), so wave weights are
  ratios of the typeface's own stroke, never picked numbers. Sections per direction: A–C
  (vertical, `sine`/`vertical`/`horizontal`/`icon`), H (`implied`), the type-study loop, J/K/L/M
  (set in Antinode via `glyphs`/`setter`). Constants like `JPEN = glyphs.W / glyphs.CAP * JCAP`
  are how the face's pen propagates into the marks.
- **`assets.py` + `page.py` + `board.tpl.html`** — `index.html` is fully self-contained (works
  from `file://`): page fonts are instanced from the variable TTFs in `build/fonts/` and subset
  to `CHARS`, marks are rewritten to `currentColor` and base64-inlined, plates assembled per
  direction.
- **`bench.py` + `bench.tpl.html`** — a tuning page for the face; carries the exponent as the
  one control CSS cannot fake.

Conventions worth knowing: inks are `INK #141312` / `RUST #cf5b2e`; icon cuts are *redrawn* at
a heavier pen (`ICON_SW`), not resized; carried/ghost strokes are thin rather than tinted so
they survive one-colour print; the project deliberately has no dark mode.
