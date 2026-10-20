"""Layer-1 scoring model (CLAUDE.md §8 items 110-114; paper/L1-MODEL-vi.md).

No target is modelled (item 112). Every critical cell's camera holds M crops recorded in the query window. The BS
broadcasts a clue set: L reference images, each with an aspect (face, body, part), a size, a recognizability r
(near 1, not 1) and an importance w the BS assigns (item 114).

  aspect similarity  crop i has a_it in [-1, 1] to the target on aspect t (strangers: per-aspect normals;
                     a share RHO of crops are dressed like the target: high a on 'part')
  match value        m_ij = r_j a_i,t(j) + e_ij,  e ~ N(0, (1 - a^2)(1 - r_j^2) / DIM)
                     (unit embeddings: the parts of crop and clue orthogonal to the target's aspect direction
                     are near-orthogonal to each other in DIM effective dimensions)
  crop score         per aspect t, est_it = sum w_j m_ij / sum w_j r_j over the held clues of t; then
                     S_i(H) = sum_t W_t est_it / sum_t W_t over the aspects present in the clues H the cell holds
  cell report        S_c = max_i S_i(H_c), with the bitmap of H_c (a few bytes over the CH's LoRa)
  verified score     U_c = max_i sum_t W_t a_it / sum_t W_t, W_t = sum of w_j over clues of aspect t: what the
                     full reference set (team 2's large file) measures exactly
The BS turns (S_c, H_c) into a normal posterior of U_c, calibrated by simulating this model (calib), and the
probability that each cell holds the highest verified score (p_best).
"""
import math

import numpy as np

ASPECTS = ("face", "body", "part")
# stranger aspect similarity (cosine to the target on that aspect): mean, sd   (scenario parameters)
STRANGER = {"face": (0.10, 0.10), "body": (0.35, 0.12), "part": (0.45, 0.15)}
RHO, LOOK = 0.02, (0.85, 0.05)        # look-alike share and their 'part' similarity
DIM = 128                             # effective embedding dimension
M = 223                               # crops per store in the query window
# the clue set: (aspect, count, kB each, importance w each, recognizability range), about 400 kB
CLUESET = [("face", 2, 24.9, 4.0, (0.80, 0.90)), ("body", 4, 49.9, 2.0, (0.88, 0.95)),
           ("part", 6, 24.9, 2 / 3, (0.95, 0.99))]   # 4 036 packets of 99 B: inside the 4 041 of 400 kB


def clues(spec=CLUESET):
    """The clue list: dicts aspect, t (aspect index), kB, w, r (spread evenly over the range)."""
    out = []
    for asp, n, kb, w, (r0, r1) in spec:
        for i in range(n):
            out.append(dict(aspect=asp, t=ASPECTS.index(asp), kB=kb, w=w,
                            r=r0 + (r1 - r0) * (i + 0.5) / n))
    return out


def order(C, kind="interleaved"):
    """Broadcast order (indices into C). grouped: by aspect, most important aspect first. interleaved: each
    aspect's clues spread evenly along the stream (by bytes), so any stretch of it holds a mix (item 113)."""
    if kind == "grouped":
        return sorted(range(len(C)), key=lambda j: (-C[j]["w"], j))
    tot = sum(c["kB"] for c in C)
    pos = {}
    for t in range(len(ASPECTS)):
        js = [j for j in range(len(C)) if C[j]["t"] == t]
        for k, j in enumerate(js):
            pos[j] = (k + 0.5) / len(js) + 1e-3 * t   # target fraction of the stream
    return sorted(range(len(C)), key=lambda j: pos[j])


def layout(C, seq, payload=99):
    """Clue j occupies stream packets [start_j, end_j) (one copy, in order seq); returns starts, ends, Q."""
    start, end, p = np.zeros(len(C), int), np.zeros(len(C), int), 0
    for j in seq:
        n = math.ceil(C[j]["kB"] * 1000 / payload)
        start[j], end[j] = p, p + n
        p += n
    return start, end, p


def stores(rng, n, m=None):
    """n cameras x m crops x aspects: stranger aspect similarities, look-alikes on 'part'."""
    m = M if m is None else m
    a = np.empty((n, m, len(ASPECTS)))
    for t, asp in enumerate(ASPECTS):
        a[..., t] = rng.normal(*STRANGER[asp], (n, m))
    look = rng.random((n, m)) < RHO
    a[..., ASPECTS.index("part")][look] = rng.normal(*LOOK, look.sum())
    return np.clip(a, -1, 1)


def matches(rng, a, C, dim=None):
    """m_ij for every camera, crop and clue: (n, m, L)."""
    dim = DIM if dim is None else dim
    r = np.array([c["r"] for c in C])
    at = a[..., [c["t"] for c in C]]
    e = rng.standard_normal(at.shape) * np.sqrt((1 - at ** 2) * (1 - r ** 2) / dim)
    return r * at + e


def weights(C):
    w = np.array([c["w"] for c in C])
    W = np.array([sum(c["w"] for c in C if c["t"] == t) for t in range(len(ASPECTS))])
    return w, W


def report(mv, C, held):
    """S_c = max_i S_i(H) for cameras (n, m, L) and a held mask (L,) or (n, L); -inf if nothing held.
    Per aspect t, the held clues of t estimate a_it: sum w_j m_ij / sum w_j r_j; the aspects present are then
    combined by their importance W_t (so a missing body view leaves the body's weight to the other views, and a
    missing aspect drops out with the rest rescaled)."""
    w = np.array([c["w"] for c in C])
    r = np.array([c["r"] for c in C])
    t = np.array([c["t"] for c in C])
    _, W = weights(C)
    h = np.broadcast_to(held, mv.shape[:1] + (len(C),)).astype(bool)
    num, den = np.zeros(mv.shape[:2]), np.zeros(len(mv))
    for a in range(len(ASPECTS)):
        wa = (h & (t == a)) * w
        d = (wa * r).sum(axis=1)
        ok = d > 0
        est = np.einsum("nml,nl->nm", mv, wa) / np.where(ok, d, 1.0)[:, None]
        num += np.where(ok[:, None], W[a] * est, 0.0)
        den += np.where(ok, W[a], 0.0)
    out = np.full(len(mv), -np.inf)
    ok = den > 0
    out[ok] = (num[ok] / den[ok, None]).max(axis=1)
    return out


def verified(a, C):
    _, W = weights(C)
    return (a @ W / W.sum()).max(axis=1)


def ncdf(z):
    """Standard normal CDF, vectorised (Abramowitz-Stegun 7.1.26 erf, |error| < 1.5e-7)."""
    x = np.abs(z) / math.sqrt(2)
    t = 1 / (1 + 0.3275911 * x)
    y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x)
    return 0.5 * (1 + np.sign(z) * y)


_CAL, _POOL = {}, {}
GRID = np.linspace(0.25, 0.80, 551)   # verified scores live in about 0.35-0.65


def calib(C, held, n=2000, seed=114, m=None, truth=None):
    """BS-side calibration for a held mask: U ~ alpha + beta S, residual sd, and prior samples of U.
    C: the weights the cells score with; truth: the weights of the verified score (default C). One simulated
    pool of n cameras serves every mask."""
    truth = C if truth is None else truth
    m = M if m is None else m
    key = (tuple(int(x) for x in held), m, DIM, RHO, tuple(c["w"] for c in C), tuple(c["w"] for c in truth))
    if key not in _CAL:
        pk = (n, seed, m, DIM, RHO, tuple(c["r"] for c in C))
        if pk not in _POOL:
            rng = np.random.default_rng(seed)
            a = stores(rng, n, m)
            _POOL[pk] = (a, matches(rng, a, C))
        a, mv = _POOL[pk]
        U = verified(a, truth)
        if not np.any(held):
            _CAL[key] = (float(U.mean()), 0.0, float(U.std()), U)
        else:
            S = report(mv, C, np.asarray(held, bool))
            beta, alpha = np.polyfit(S, U, 1)
            _CAL[key] = (float(alpha), float(beta), float(np.std(U - alpha - beta * S)), U)
    return _CAL[key]


_PRIOR = {}


def prior_grid(samples):
    """Smoothed pdf and cdf of the prior samples on GRID (Gaussian kernel, Silverman bandwidth)."""
    key = id(samples)
    if key not in _PRIOR:
        bw = 1.06 * float(np.std(samples)) * len(samples) ** -0.2
        pdf = np.zeros_like(GRID)
        for c in np.array_split(samples, 8):
            pdf += np.exp(-0.5 * ((GRID[:, None] - c[None, :]) / bw) ** 2).sum(axis=1)
        pdf /= pdf.sum() * (GRID[1] - GRID[0])
        cdf = np.cumsum(pdf) * (GRID[1] - GRID[0])
        _PRIOR[key] = (pdf, np.minimum(cdf, 1.0))
    return _PRIOR[key]


def p_best(known, prior, done):
    """P(each candidate holds the highest verified score), on GRID.
    known: [(mu, sd)] normal posteriors of reported unvisited cells; prior: (samples, n) for the n cells not
    reported yet (one shared prior); done: verified scores of visited cells. Returns (p_known, p_one_unreported)."""
    samples, n_un = prior
    u, du = GRID, GRID[1] - GRID[0]
    ppdf, pcdf = prior_grid(samples)
    tot = n_un * np.log(np.maximum(pcdf, 1e-300))
    for v in done:
        tot = tot + np.where(u >= v, 0.0, -np.inf)
    if known:
        mu, sd = np.array(known).T
        z = (u[None, :] - mu[:, None]) / sd[:, None]
        logc = np.log(np.maximum(ncdf(z), 1e-300))
        pdf = np.exp(-z * z / 2) / (sd[:, None] * math.sqrt(2 * math.pi))
        tot = tot + logc.sum(axis=0)
        pk = (pdf * np.exp(tot[None, :] - logc)).sum(axis=1) * du
    else:
        pk = np.zeros(0)
    pu = float((ppdf * np.exp(tot - np.log(np.maximum(pcdf, 1e-300)))).sum() * du) if n_un else 0.0
    return list(pk), pu
