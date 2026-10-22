# Ảnh chụp trình phát mission-replay (cluster có sẵn)

- Bắt đầu: 2026-10-22 09:28:10, chạy 9 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/anim_shots.py docs/anim/mission-replay.html docs/figures/tr-shot-mission c:35.9 t:40 t:95
```

**Kết quả**

```text
{"names": ["grow", "fill", "lakes", "nodes", "partition", "roles", "scan", "tour", "plan", "mission"], "starts": [0, 4, 6.5, 8.5, 11, 14.5, 18, 25, 30, 36], "legs": [[2, 20.09, 75.75], [4, 79.47, 131.21], [1, 165.25, 227.38], [3, 238.87, 292.28]]}
c:35.9: step bar 35.90 s -> docs/figures/tr-shot-mission-c35.9.png
t:40: step bar 39.64 s -> docs/figures/tr-shot-mission-t40.png
t:95: step bar 50.21 s -> docs/figures/tr-shot-mission-t95.png
```
