"""Still frames of the replay players (docs/anim/*.html) for the Layer-3 technical report (CLAUDE.md §8 item 125).

    python3 tools/anim_shots.py docs/anim/mission-replay.html docs/figures/tr-shot-mission c:35.9 t:40 t:95

Each ITEM is c:SHOW (seconds on the player's step bar) or t:SECONDS (mission time, mapped to the step bar by
bisection on the player's own time warp). The player keeps its state inside a closure, so a copy with a seek hook is
loaded instead of the file itself. Writes OUT-<c|t><value>.png: the map canvas only, light theme, trimmed to its
content. Prints the chapter starts and each UAV leg over a cluster so the times can be picked.
"""
import asyncio, json, sys

import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

TAIL = "setPlay(false); draw(show); requestAnimationFrame(loop);\n})();"
HOOK = ("window.__seek = v => { show = v; dirty = true; }; window.__mt = missionTime;\n"
        "window.__info = () => ({starts, TOTAL, names: CH.map(c => c.n), legs: legs.map(l => [l.k, l.t0, l.t1])});\n")


def trim(path, pad=24):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    diff = np.abs(a - a[2, 2]).sum(axis=2) > 24
    ys, xs = np.nonzero(diff)
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad))
    im.crop(box).save(path)


async def main(page, out, items):
    src = open(page).read()
    assert src.count(TAIL) == 1, "player tail not found"
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1100, "height": 900}, device_scale_factor=2, color_scheme="light")
        await pg.set_content(src.replace(TAIL, HOOK + TAIL))
        await pg.wait_for_timeout(800)
        info = await pg.evaluate("__info()")
        print(json.dumps({k: info[k] for k in ("names", "starts", "legs")}))
        m0 = info["starts"][-1]
        for it in items:
            kind, v = it.split(":")
            v = float(v)
            show = v
            if kind == "t":
                lo, hi = 0.0, info["TOTAL"] - m0
                for _ in range(50):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if await pg.evaluate(f"__mt({mid})") < v else (lo, mid)
                show = m0 + hi
            await pg.evaluate(f"__seek({show})")
            await pg.wait_for_timeout(300)
            path = f"{out}-{kind}{v:g}.png"
            await pg.locator("#map").screenshot(path=path)
            trim(path)
            print(f"{it}: step bar {show:.2f} s -> {path}")
        await b.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3:]))
