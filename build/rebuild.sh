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
