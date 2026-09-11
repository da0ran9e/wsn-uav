# uav-screening-depth

A UAV broadcasts a signature set of `k` files over a pre-deployed sensor network;
ground clusters screen their own data against it and flag themselves; the UAV then
re-flies to verify only the flagged clusters. **How large should `k` be?**

The campaign measures whether `T_total(k) = T1(k) + r(k)·T2(k) + (1−r(k))·T_miss`
has a unique interior minimum, and how that minimum scales with the cluster count.
`AGENT-BRIEF.md` is the contract; `STATUS.md` is the current state of truth.

## Reproduce the E0 gate

```bash
python3.10 -m pytest tests/ -q          # 108 tests; the brief's tables are the oracle
python3.10 tools/run_e0.py              # ~19 s -> results/E0/
python3.10 tools/make_report.py all     # -> report/E0.html, report/index.html
```

Open `report/index.html` in a browser — the reports are self-contained and need no
network. `results/E0/verdict.json` is the machine-readable gate decision.

## Layout

| path | what |
|---|---|
| `config/default.yaml` | every parameter, with units. No magic numbers in code. |
| `src/screening/model.py` | `dose_kernel`, `theta_all_k`, `theta_m_of_k`, `t_total` |
| `tools/run_e0.py` | the E0 sweep |
| `tools/make_report.py` | experiment → self-contained HTML |
| `tools/assert_one_build.py` | refuses to aggregate across mixed build provenance |
| `docs/AUDIT-E0.md` | self-audit: assumptions, divergences, every reported number |

## Status in one line

E0 gate is **GO, conditional**: an interior `k*` exists robustly only when `m`
scales with `k`; with `m` fixed there is no optimum at all. See `STATUS.md`.

## Note on repository location

The brief calls for this to be a standalone repository. It currently lives as a
self-contained subtree inside `wsn-uav` because push access was scoped to that
repo; it imports nothing from its parent and extracts with
`git subtree split -P uav-screening-depth`. See `STATUS.md` → Open problems.
