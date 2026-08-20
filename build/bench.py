#!/usr/bin/env python3
"""Rebuild the tuning bench. The face is inlined, so the bench has to be recut
whenever the face is — otherwise it draws a letterform the masters no longer
have."""
import base64, os

HERE = os.path.dirname(os.path.abspath(__file__))
FACE = os.path.join(HERE, os.pardir, "font", "Antinode-Regular.woff2")
OUT = os.path.join(HERE, os.pardir, "bench.html")

tpl = open(os.path.join(HERE, "bench.tpl.html")).read()
out = tpl.replace("{{FONT}}", base64.b64encode(open(FACE, "rb").read()).decode())
assert "{{" not in out
open(OUT, "w").write(out)
print(f"bench.html  {len(out) / 1024:.0f}KB")
