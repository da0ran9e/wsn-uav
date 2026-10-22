# Hình từng bước thuật toán River trên C3 (l3_report_figs.py)

- Bắt đầu: 2026-10-22 09:28:00, chạy 4 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l3_report_figs.py --data docs/data/cap80-c3long --k 3 --bits /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/l2dep/pass3b-bits-r1.bin --trace '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/c3trace/{s}' --figs docs/figures --name tr-l3
```

**Kết quả**

```text
alg1: 5703 packets along the track, 4685 over 17 Axe cells (packets 510-5194); Seg sizes [361, 255, 285, 361, 317, 170, 71, 343, 360, 260, 281, 360, 322, 151, 90, 338, 360]
alg2: u from (9, -8) to (5, 6); the shown Axe cell (7, -1): paths [[(7, -1), (6, -1), (5, 0)], [(7, -1), (8, -1), (9, -2)]]; River 51 cells, 24 Banks; omega 303 m
alg3: mu 0.531, sd 0.154; > mu+2sd (0.840): [(8, -2), (9, -7)]; mu+sd..mu+2sd (0.685): 10 cells, local winners [(4, 6)]; CH (8, -5); critical [(4, 6), (8, -5), (8, -2), (9, -7)]
alg4: (9, -7) member 1 (9, -8): Axe cells (9, -8)..(8, -6) (3 Seg), Banks [(9, -8), (10, -7)], paths [0, 2, 2] cells
alg4: (9, -7) member 2 (10, -8): Axe cells (8, -5)..(7, -3) (3 Seg), Banks [(9, -4), (10, -6), (10, -5)], paths [2, 3, 4] cells
alg4: (9, -7) member 3 (8, -7): Axe cells (8, -3)..(7, -1) (3 Seg), Banks [(6, -2), (9, -3), (9, -2)], paths [5, 5, 6] cells
alg4: (9, -7) member 4 (10, -7): Axe cells (7, 0)..(6, 2) (3 Seg), Banks [(6, 1), (6, 2), (9, -1)], paths [6, 8, 9] cells
alg4: (9, -7) member 5 (8, -6): Axe cells (6, 3)..(6, 4) (3 Seg), Banks [(5, 4), (6, 3), (6, 4)], paths [9, 10, 10] cells
alg4: (9, -7) member 6 (9, -6): Axe cells (5, 5)..(5, 6) (2 Seg), Banks [(6, 5), (6, 6)], paths [11, 12] cells
gather t=1 s: 2850 of 9105 gather frames; critical CL shares (4, 6) 0.50, (8, -5) 0.68, (8, -2) 0.84, (9, -7) 0.58
gather t=3 s: 6260 of 9105 gather frames; critical CL shares (4, 6) 0.53, (8, -5) 0.73, (8, -2) 0.91, (9, -7) 0.63
gather t=10 s: 9105 of 9105 gather frames; critical CL shares (4, 6) 0.74, (8, -5) 0.89, (8, -2) 1.00, (9, -7) 0.76
run t=8 s, last 2 s: {'circlefill': 8077, 'gather': 843, 'control': 75, 'pull': 3}; critical CL shares (4, 6) 0.69, (8, -5) 0.86, (8, -2) 1.00, (9, -7) 0.74
run t=12 s, last 2 s: {'pull': 1879, 'circlefill': 4610}; critical CL shares (4, 6) 0.78, (8, -5) 0.91, (8, -2) 1.00, (9, -7) 0.79
run t=18 s, last 2 s: {'pull': 620, 'circlefill': 1869}; critical CL shares (4, 6) 0.85, (8, -5) 0.94, (8, -2) 1.00, (9, -7) 0.89
run t=25 s, last 2 s: {'circlefill': 2955, 'pull': 627}; critical CL shares (4, 6) 0.90, (8, -5) 0.94, (8, -2) 1.00, (9, -7) 0.92
run t=32 s, last 2 s: {'circlefill': 3858, 'pull': 658}; critical CL shares (4, 6) 0.95, (8, -5) 0.96, (8, -2) 1.00, (9, -7) 0.99
run t=37.2 s, last 2 s: {'pull': 587, 'circlefill': 206}; critical CL shares (4, 6) 1.00, (8, -5) 1.00, (8, -2) 1.00, (9, -7) 1.00
done at: (4, 6) 37.2 s, (8, -5) 35.8 s, (8, -2) 7.5 s, (9, -7) 32.9 s
```
