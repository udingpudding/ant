#!/usr/bin/env python3
"""Rebuild the tuning bench. The face is inlined, so the bench has to be recut
whenever the face is — otherwise it draws a letterform the masters no longer
have."""
import base64, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import antinode_font

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "bench.html")

# the curve exponent is the one control CSS cannot fake, so the bench carries a
# cut of the face at each setting and switches between them
CUTS = {"FONT25": 2.5, "FONT32": 3.2, "FONT40": 4.0, "FONT55": 5.5}

tpl = open(os.path.join(HERE, "bench.tpl.html")).read()
out = tpl
for key, n in CUTS.items():
    out = out.replace("{{%s}}" % key,
                      base64.b64encode(antinode_font.woff2_at(n)).decode())
assert "{{" not in out
open(OUT, "w").write(out)
print(f"bench.html  {len(out) / 1024:.0f}KB  ({len(CUTS)} cuts of the face)")
