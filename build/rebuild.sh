#!/bin/sh
# The whole chain, in the one order that works. Run it from anywhere.
#
#   ./build/rebuild.sh
#
# svgo only honours a single -f per invocation, which is why the folders are
# listed one at a time — passing three silently optimises only the last.
set -e
cd "$(dirname "$0")"

python3 antinode_font.py          # cuts ../font from glyphs.py
python3 build-antinode.py         # rewrites ../logos and ../type-study
python3 specimen.py               # rewrites ../specimen
python3 bench.py                  # recuts ../bench.html around the new face

cd ..
for d in logos type-study specimen; do
  npx --yes svgo -f "$d" --multipass >/dev/null
done
printf '  svgo    %s SVGs optimised\n' "$(ls logos type-study specimen | grep -c '\.svg$')"

cd build
python3 assets.py                 # subsets page fonts, bundles every mark
python3 page.py                   # rewrites ../index.html

# PNG twins of the chosen cuts, 4x the SVG's own size, transparent. Headless
# Chrome, not ImageMagick: IM's built-in SVG parser silently drops the rust
# wave. No --user-data-dir — with a fresh one Chrome hangs; without it a
# second instance renders fine while Chrome is open. The rm + test -s pair is
# there so a Chrome that exits 0 without drawing anything fails the build.
# ponytail: one scale (4x); per-size exports when a spec asks for them.
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ -x "$CHROME" ]; then
  n=0
  for svg in ../logos/antinode-L-*.svg ../logos/antinode-M-*.svg; do
    png="$(pwd)/${svg%.svg}.png"
    w=$(sed -n 's/.* width="\([0-9]*\)".*/\1/p' "$svg" | head -1)
    h=$(sed -n 's/.* height="\([0-9]*\)".*/\1/p' "$svg" | head -1)
    rm -f "$png"
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
      --force-device-scale-factor=4 --window-size="$w,$h" \
      --default-background-color=00000000 --screenshot="$png" \
      "file://$(pwd)/$svg" >/dev/null 2>&1
    test -s "$png" || { echo "png: Chrome wrote nothing for $svg" >&2; exit 1; }
    n=$((n + 1))
  done
  printf '  png     %s rasterised at 4x\n' "$n"
else
  echo "png: Chrome not found at $CHROME — PNGs not refreshed (set CHROME=...)" >&2
fi
