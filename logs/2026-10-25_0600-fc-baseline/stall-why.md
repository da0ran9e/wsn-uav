# stall-why

- Bắt đầu: 2026-10-25 07:18:28, chạy 8 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 logs/2026-10-25_0600-fc-baseline/stall_why.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k16-s1 1 9
```

**Kết quả**

```text
C1 crit (0, 1): lacks packet 3831 (window 539-4579); Axe segment [(-1, 9)]; held by 30 node(s) in cells [(-2, 8), (-2, 9), (-2, 10), (-1, 8), (-1, 9), (0, 8)]; last packet it got at 49.6 s
C9 crit (-8, 16): lacks packet 3910 (window 482-4695); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 92.6 s
C9 crit (-8, 19): lacks packet 3910 (window 509-4722); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 98.3 s
C9 crit (-7, 24): lacks packet 3910 (window 545-4758); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 116.1 s
C9 crit (-6, 17): lacks packet 3910 (window 482-4695); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 101.2 s
C9 crit (-3, 23): lacks packet 3910 (window 482-4695); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 116.8 s
C9 crit (-2, 19): lacks packet 3910 (window 482-4695); Axe segment [(-13, 21)]; held by 10 node(s) in cells [(-12, 21)]; last packet it got at 119.2 s
```
