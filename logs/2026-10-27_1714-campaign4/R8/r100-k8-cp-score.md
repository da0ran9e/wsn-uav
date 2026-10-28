# r100-k8-cp-score

- Bắt đầu: 2026-10-28 22:46:05, chạy 17 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/lm_tour.py score /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/CP/r100/R8/k8-s1 --mode ns3 --out logs/2026-10-27_1714-campaign4/score/R8/r100-k8/score-cp
```

**Kết quả**

```text
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/CP/r100/R8/k8-s1 [ns3]: T* 977 s (sd 649), team 1 784 s, mean River ready 452 s
```

> Job `cp 8 r100 8` bị dừng lúc 22:43 (mục 209) sau khi mission (22:43:17) và `l1_rank` (22:44:02) đã xong, trước bước đánh dấu `done-cp`. `score-cp.csv` bị xoá nhầm nên chấm lại bằng lệnh trên; T\* 977 s khớp `score-cp.log` gốc. Log Markdown của job không còn.
