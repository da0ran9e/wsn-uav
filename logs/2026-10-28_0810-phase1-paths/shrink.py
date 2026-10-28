"""Shrink the PNGs of a folder in place: RGBA -> an adaptive 256-colour palette (the panels are flat fills and lines,
so the difference is not visible), about a third of the size.
    python3 shrink.py DIR
"""
import glob, os, sys

from PIL import Image

for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.png"))):
    a = os.path.getsize(p)
    im = Image.open(p).convert("RGB")
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(p, optimize=True)
    print(f"{os.path.basename(p)} {a // 1024} -> {os.path.getsize(p) // 1024} KB")
