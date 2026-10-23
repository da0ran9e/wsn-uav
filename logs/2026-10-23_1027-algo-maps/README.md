# 2026-10-23 · Các thuật toán trên cùng một bản đồ (CLAUDE.md §8 mục 141)

**Mục đích:** hình so sánh các thuật toán trên cùng bản đồ, dùng lại các lượt chạy của `logs/2026-10-23_0706-baselines/` (không chạy ns-3 mới).

**Mã:** `uav-l2/tools/algo_map_fig.py` (mới: `phase1` gồm P\*, B5, B8-500, B3-500, B6; `layer3` gồm River, kéo thẳng, Trickle, critical cell tô theo doneS); `uav-l2/tools/iter_fig.py` (lớp 2).

**Lệnh:** `layer2-<map>.md`, `phase1-<map>.md`, `layer3-<map>.md` cho k6-s11 và k8-s1. Mọi lệnh thoát 0.

**Đầu ra:** `uav-l2/docs/figures/cmp-<map>-{layer2,phase1,layer3}-*.png` (6 hình, ghi trong `INDEX.md`).

**T\* trên hai bản đồ (100 lượt bốc), s:**

| | P\* | kéo thẳng | Trickle | không hợp tác | k-medoids | SWATH-K | MEANDER-K | subCH-K | B5 | B8-500 | B3-500 | B6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k6-s11 | 681 | 680 | 680 | 714 | 713 | 672 | 753 | 693 | 765 | 1 122 | 1 718 | 1 835 |
| k8-s1 | 740 | 741 | 744 | 785 | 767 | 778 | 934 | 792 | 936 | 1 240 | 1 944 | 2 302 |

**Lớp 3 (critical cell đủ cửa sổ sau khi UAV rời cụm; khung mặt đất):** k6-s11 River TB 10,7 s, chậm nhất 51 s, 192 k khung; kéo thẳng 11,8 / 43 s, 224 k; Trickle 20,6 / 66 s, 1 414 k. k8-s1 River 10,7 / 43 s, 252 k; kéo thẳng 12,6 / 42 s, 295 k; Trickle 21,1 / 69 s, 1 723 k.
