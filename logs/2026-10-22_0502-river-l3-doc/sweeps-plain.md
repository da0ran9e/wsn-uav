# sweeps-plain

- Bắt đầu: 2026-10-22 05:03:06, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-coop2`

**Lệnh**

```bash
python3 tools/river_sweep_figure.py --runs docs/data/camp54 --figs docs/figures --name ns3-sweeps-plain.png --plain
```

**Kết quả**

```text
  docs/figures/ns3-sweeps-plain.png

missions per configuration: [20]; unfinished critical cells: 0
per configuration, mean ± 95 % (mean over critical cells | last | frames):
  c3  w3.5 k7  full:   17.0± 0.3 s |   33.0± 1.5 s |   67.4± 0.9 k
  c4  w3.5 k7  full:   16.6± 0.3 s |   32.0± 1.4 s |   67.4± 0.9 k
  c7  w2.5 k7  full:   15.4± 0.3 s |   32.4± 1.4 s |   69.6± 1.1 k
  c7  w3.5 k1  d   :    5.9± 0.1 s |    5.9± 0.1 s |    1.2± 0.0 k
  c7  w3.5 k1  full:    5.7± 0.1 s |    5.7± 0.1 s |    1.9± 0.0 k
  c7  w3.5 k4  d   :   20.8± 0.6 s |   34.5± 1.2 s |   71.4± 0.8 k
  c7  w3.5 k4  full:   18.3± 0.6 s |   31.8± 1.4 s |   56.9± 0.8 k
  c7  w3.5 k7  d   :   20.4± 0.5 s |   37.0± 1.4 s |   85.2± 1.0 k
  c7  w3.5 k7  full:   16.4± 0.3 s |   31.8± 1.4 s |   67.4± 0.9 k
  c7  w3.5 k10 d   :   17.9± 0.3 s |   37.1± 1.3 s |   95.6± 1.0 k
  c7  w3.5 k10 full:   15.5± 0.3 s |   32.9± 1.3 s |   75.3± 0.9 k
  c7  w3.5 k16 d   :   31.1± 0.7 s |   57.3± 2.0 s |  204.6± 2.0 k
  c7  w3.5 k16 full:   20.5± 0.6 s |   37.6± 2.0 s |  159.2± 1.4 k
  c7  w4.5 k7  full:   15.9± 0.3 s |   31.0± 1.4 s |   67.7± 0.8 k
  c7  w6.5 k7  full:   16.0± 0.3 s |   31.4± 1.3 s |   68.5± 0.8 k
  c13 w3.5 k7  full:   16.4± 0.3 s |   31.7± 1.4 s |   67.4± 0.9 k
paired differences B - A, mean ± 95 %:
  A = 7 màu, B = 3 màu (20 lượt); mean +0.6±0.1s (B<A 0/20); last +1.2±0.3s (B<A 0/20); frames +0.0±0.0k (B<A 0/20)
  A = 7 màu, B = 4 màu (20 lượt); mean +0.2±0.1s (B<A 1/20); last +0.2±0.1s (B<A 5/20); frames +0.0±0.0k (B<A 0/20)
  A = 7 màu, B = 13 màu (20 lượt); mean -0.0±0.0s (B<A 15/20); last -0.1±0.1s (B<A 13/20); frames +0.0±0.0k (B<A 0/20)
  A = River 3,5, B = River 2.5 (20 lượt); mean -1.0±0.1s (B<A 20/20); last +0.6±0.3s (B<A 5/20); frames +2.2±0.6k (B<A 1/20)
  A = River 3,5, B = River 4.5 (20 lượt); mean -0.5±0.0s (B<A 20/20); last -0.8±0.2s (B<A 20/20); frames +0.3±0.2k (B<A 4/20)
  A = River 3,5, B = River 6.5 (20 lượt); mean -0.4±0.1s (B<A 20/20); last -0.5±0.5s (B<A 13/20); frames +1.1±0.2k (B<A 1/20)
  A = kéo thẳng, B = River, 1 critical (20 lượt); mean -0.3±0.1s (B<A 20/20); last -0.3±0.1s (B<A 20/20); frames +0.8±0.0k (B<A 0/20)
  A = kéo thẳng, B = River, 4 critical (20 lượt); mean -2.5±0.8s (B<A 19/20); last -2.7±1.6s (B<A 16/20); frames -14.5±0.9k (B<A 20/20)
  A = kéo thẳng, B = River, 7 critical (20 lượt); mean -4.0±0.5s (B<A 20/20); last -5.2±1.4s (B<A 19/20); frames -17.8±0.9k (B<A 20/20)
  A = kéo thẳng, B = River, 10 critical (20 lượt); mean -2.5±0.4s (B<A 20/20); last -4.2±1.3s (B<A 19/20); frames -20.3±1.0k (B<A 20/20)
  A = kéo thẳng, B = River, 16 critical (20 lượt); mean -10.6±0.9s (B<A 20/20); last -19.7±2.9s (B<A 20/20); frames -45.4±2.1k (B<A 20/20)
```
