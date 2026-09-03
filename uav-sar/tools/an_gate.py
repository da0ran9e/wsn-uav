"""Score what Phase 2 waited for.

The question is not "did it work" but "how much did waiting cost". Three
triggers are minutes apart, so the columns that matter are when the gate opened,
how long the rotary team then had, and what it managed in that time.

  gate_s     when Phase 2 was released
  lora_s     when the first candidate flag reached the base (flag arm only)
  first_del  first delivery -- the gate is only useful if this follows it
  live       adverts (SUMMON or re-aim) still going out AFTER the gate opened.
             If this is large and nothing follows it, the team was released in
             time and still never learned where to go.
  taken      of those, how many a UAV actually accepted. A SUMMON is a single
             one-hop broadcast: only a UAV airborne within reach at that instant
             hears it, so a team parked at base misses by construction and
             catching a later re-aim is luck.
"""
import csv, glob, math, os, re, statistics as st, sys


def analyse(run):
    ev = list(csv.DictReader(open(os.path.join(run, "events.csv"))))
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    at = lambda name: [float(r["t"]) for r in ev if r["event"] == name]
    gate = at("gate_open")
    lora = at("lora_flag")
    dels = at("deliver_start")
    # a candidate is "live" while its leader is still summoning or retargeting
    summons, last_ad = [], 0.0
    for r in ev:
        if r["event"] == "summon_start":
            mm = re.search(r"target=([-\d.]+);([-\d.]+)", r["detail"])
            if mm:
                summons.append((float(r["t"]), float(mm.group(1)), float(mm.group(2))))
        if r["event"] in ("summon_start", "retarget"):
            last_ad = max(last_ad, float(r["t"]))
    g0 = min(gate) if gate else 0.0
    served = 0
    dpos = [(float(r["t"]), float(r["x"]), float(r["y"])) for r in ev
            if r["event"] in ("deliver_start", "deliver_move")]
    for _, sx, sy in summons:
        if any(math.hypot(dx - sx, dy - sy) <= 60 for _, dx, dy in dpos):
            served += 1
    ads = sorted(float(r["t"]) for r in ev
                 if r["event"] in ("summon_start", "retarget"))
    acc = sorted(float(r["t"]) for r in ev
                 if r["event"] in ("divert", "retarget_divert"))
    live = [a for a in ads if a > g0]
    taken = sum(1 for a in live if any(a <= x <= a + 6.0 for x in acc))
    return dict(gate=g0, lora=(min(lora) if lora else float("nan")),
                first_del=(min(dels) if dels else float("nan")),
                ndel=len(dels), summons=len(summons), served=served,
                last_ad=last_ad, live=len(live), taken=taken, nacc=len(acc),
                loc=int(m["victimsLocated"]), vic=int(m["victimCount"]),
                kJ=float(m["uavEnergyJ"]) / 1000.0, tfix=float(m["timeToFixAtBS_s"]))


def main():
    root, arms = sys.argv[1], sys.argv[2:]
    hdr = (f"{'trigger':<9}{'n':>3}{'gate_s':>8}{'lora_s':>8}{'first_del':>10}"
           f"{'served':>9}{'live':>6}{'taken':>7}{'loc':>8}{'kJ':>7}{'tFix':>7}")
    print(hdr); print("-" * len(hdr))
    for arm in arms:
        rs = []
        for d in sorted(glob.glob(f"{root}/{arm}/s*"), key=lambda p: int(p.split("s")[-1])):
            if os.path.exists(os.path.join(d, "metrics.csv")):
                try: rs.append(analyse(d))
                except Exception: pass
        if not rs:
            print(f"{arm:<9} (no runs)"); continue
        g = lambda k: st.mean(x[k] for x in rs)
        fd = [x["first_del"] for x in rs if x["first_del"] == x["first_del"]]
        lo = [x["lora"] for x in rs if x["lora"] == x["lora"]]
        tf = [x["tfix"] for x in rs if x["tfix"] > 0]
        print(f"{arm:<9}{len(rs):>3}{g('gate'):8.0f}"
              f"{(st.mean(lo) if lo else float('nan')):8.0f}"
              f"{(st.mean(fd) if fd else float('nan')):10.0f}"
              f"{sum(x['served'] for x in rs):4d}/{sum(x['summons'] for x in rs):<4}"
              f"{sum(x['live'] for x in rs):6d}{sum(x['taken'] for x in rs):7d}"
              f"{sum(x['loc'] for x in rs):4d}/{sum(x['vic'] for x in rs):<3}"
              f"{g('kJ'):7.0f}{(st.mean(tf) if tf else float('nan')):7.0f}")


if __name__ == "__main__":
    main()
