"""How far the UAV's broadcast reaches under a few A2G environments (CLAUDE.md §8 item 158).

    python3 tools/a2g_radius.py

Per environment: the chance a 127 B packet gets through to a ground node at horizontal distance x from the UAV
(altitude H = 100 m), the distance where that chance falls to 50 % (R50) and 10 % (R10), the packets a node at
lateral offset x hears from one long straight pass (one packet per 0.5 m: 50 m/s, 10 ms), and so the largest
fountain-coded file one node can decode alone from that pass (K <= heard / 1.05).
  received power  P_tx - PL(d); a packet gets through when the faded power is at least -101 dBm (the 50 % PER
                  point of a 127 B PSDU measured on the ns-3 PHY, coop-params.h)
  current         the model in use: free space to 100 m, then exponent 3 (coop-a2g.h), Rician K = 2 per packet,
                  +10 dBm
  indoor, indoor20   the same plus 15 or 20 dB building entry loss (nodes indoors or under a roof)
  cc2420          the same with a 0 dBm transmitter and -95 dBm sensitivity
  urban, dense, highrise   Al-Hourani et al. 2014 (IEEE WCL 3(6)): LoS with probability
                  1 / (1 + a exp(-b (theta - a))), theta the elevation in degrees; free space plus eta_LoS
                  (Rician K = 2) or eta_NLoS (Rayleigh) dB; (a, b, eta_LoS, eta_NLoS) = (9.61, 0.16, 1, 20),
                  (12.08, 0.11, 1.6, 23), (27.23, 0.08, 2.3, 34); averaged over LoS and NLoS; -0dBm: a 0 dBm UAV
"""
import math

import numpy as np

H, F_DB, THR = 100.0, 40.05, -101.0


def ok(mean_db, K, thr=THR):
    """P(faded power >= thr) for mean power mean_db (dBm), Rician K (0: Rayleigh)."""
    z = 10 ** ((thr - mean_db) / 10)   # threshold over the mean power
    if K == 0:
        return math.exp(-z)
    g = np.linspace(z, z + 60.0 / (K + 1), 6000)
    f = (K + 1) * math.exp(-K) * np.exp(-(K + 1) * g) * np.i0(2 * np.sqrt(K * (K + 1) * g))
    return float(min(1.0, np.trapezoid(f, g)))


def two_seg(d, alpha=3.0):
    return F_DB + 20 * math.log10(min(d, H)) + (10 * alpha * math.log10(d / H) if d > H else 0)


def hourani(a, b, eta_los, eta_nlos, tx=10.0):
    def p(x):
        d = math.hypot(x, H)
        th = math.degrees(math.atan2(H, x))
        pl = 1 / (1 + a * math.exp(-b * (th - a)))
        fs = F_DB + 20 * math.log10(d)
        return pl * ok(tx - fs - eta_los, 2) + (1 - pl) * ok(tx - fs - eta_nlos, 0)
    return p


ENV = {
    "current": lambda x: ok(10 - two_seg(math.hypot(x, H)), 2),
    "indoor": lambda x: ok(10 - two_seg(math.hypot(x, H)) - 15, 2),
    "indoor20": lambda x: ok(10 - two_seg(math.hypot(x, H)) - 20, 2),
    "cc2420": lambda x: ok(0 - two_seg(math.hypot(x, H)), 2, -95.0),
    "urban": hourani(9.61, 0.16, 1.0, 20.0),
    "dense": hourani(12.08, 0.11, 1.6, 23.0),
    "urban-0dBm": hourani(9.61, 0.16, 1.0, 20.0, tx=0.0),
    "dense-0dBm": hourani(12.08, 0.11, 1.6, 23.0, tx=0.0),
    "highrise": hourani(27.23, 0.08, 2.3, 34.0),
}
XS = (0, 100, 200, 300, 500, 800)


def main():
    grid = np.arange(0, 3001, 5.0)
    print("| môi trường | " + " | ".join(f"p({x} m)" for x in XS) + " | R50 (m) | R10 (m) | "
          + " | ".join(f"gói nghe được, lệch {x} m" for x in (0, 100, 200, 300)) + " | file fountain tối đa, lệch 0 m (gói / kB) |")
    print("|---" * (len(XS) + 8) + "|")
    for name, p in ENV.items():
        pg = np.array([p(x) for x in grid])
        r50 = grid[np.argmax(pg < 0.5)] if (pg < 0.5).any() else math.inf
        r10 = grid[np.argmax(pg < 0.1)] if (pg < 0.1).any() else math.inf
        heard = []
        for x in (0, 100, 200, 300):   # a pass along y: the node at lateral offset x, packets every 0.5 m
            y = np.arange(-3000, 3000, 0.5)
            heard.append(float(np.interp(np.hypot(x, y), grid, pg).sum()))
        k = heard[0] / 1.05
        print(f"| {name} | " + " | ".join(f"{p(x):.2f}" for x in XS) + f" | {r50:.0f} | {r10:.0f} | "
              + " | ".join(f"{h:.0f}" for h in heard) + f" | {k:.0f} / {k * 99 / 1000:.0f} |")


if __name__ == "__main__":
    main()
