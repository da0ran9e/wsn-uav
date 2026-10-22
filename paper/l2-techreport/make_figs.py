"""Copy the figures of the Layer-2 technical report (CLAUDE.md §8 item 127) into figs/, so the LaTeX folder is
self-contained (e.g. for Overleaf). The MEANDER step figures are pairs of panels; each pair is split into its two
panels. Every panel is trimmed to its content. No figure carries text (item 63).

    python3 paper/l2-techreport/make_figs.py
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "..", "uav-l2", "docs", "figures")
OUT = os.path.join(HERE, "figs")


def box(im, pad=6):
    a = np.asarray(im.convert("RGB")).astype(int)
    ys, xs = np.nonzero(np.abs(a - a[1, 1]).sum(axis=2) > 30)
    return max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad + 1), min(im.height, ys.max() + pad + 1)


def save(im, name, crop=None):
    im = im.crop(crop or box(im))
    im.save(os.path.join(OUT, name))
    print(f"{name}: {im.width} x {im.height}")


os.makedirs(OUT, exist_ok=True)
save(Image.open(os.path.join(FIG, "cap80-river.png")), "chord-before.png")
save(Image.open(os.path.join(FIG, "cap80-c3long-river.png")), "chord-after.png")
halves = []                                       # the eight MEANDER steps, cropped alike so they share one scale
for pair in ("12", "34", "56", "78"):
    im = Image.open(os.path.join(FIG, f"meander-k6-s3-b220-w1-step-{pair}.png"))
    halves += [im.crop((0, 0, im.width // 2, im.height)), im.crop((im.width // 2, 0, im.width, im.height))]
boxes = [box(h) for h in halves]
union = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
for h, step in zip(halves, "abcdefgh"):
    save(h, f"meander-{step}.png", union)
for src, name in (("meander-bend-ch.png", "bend.png"), ("meander-k6-s3-b220-w1-compare.png", "compare.png"),
                  ("sat-domain.png", "sat-domain.png"), ("l2-diag.png", "diag.png")):
    save(Image.open(os.path.join(FIG, src)), name)
