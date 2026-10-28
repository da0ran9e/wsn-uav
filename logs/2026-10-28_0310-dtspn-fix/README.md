# 2026-10-28 · Sửa DTSP-N + River cho đi qua mọi critical cell (CLAUDE.md §8 mục 193)

**Vấn đề** (`logs/2026-10-28_0240-dtspn-check`): pass của DTSP-N + River chỉ vào đĩa B(v, ξ) của 50–70 % critical cell, và góc quay trong cụm chỉ khoảng 100°. Nguyên nhân:
- `every_crit` uốn đường thẳng bằng các bump Gauss liên tiếp, bump sau kéo lệch bump trước;
- bump nào làm đường ra khỏi cụm rồi vào lại thì bị bỏ.

**Sửa** (`uav-l2/tools/lm_tour.py`): `through_crit` thay cho `every_crit`.
1. Xếp các critical cell theo thứ tự chiếu lên hướng b (b = 0, 30, …, 150°). Đường vì vậy zigzag ngang cụm mà không quay ngược.
2. Mỗi cell một điểm mốc trong đĩa của nó (≤ 0,95 ξ), đặt ở chỗ đường gấp khúc qua các mốc cắt góc được nhiều nhất (lặp 30 lần).
3. Đường vào và ra thẳng theo hướng b, bắt đầu và kết thúc cách ô ngoài cùng của cụm 60 m.
4. Nối các mốc bằng cung Dubins bán kính r ∈ {R_LOOP = 63,7; 2 R_LOOP; R_TURN = 255} m. Hướng tại mỗi mốc là một trong 8 hướng quanh hướng của đường gấp khúc, chọn bằng quy hoạch động cho tổng độ dài ngắn nhất (bản đầu chỉ lấy phân giác nên có vòng lượn thừa).
5. `kin_time.profile` giảm tốc ở khúc cua chặt hơn R_TURN.
6. `assert`: mọi critical cell cách đường ≤ ξ + 1 m.
7. Ưu tiên đường cắt cụm một lần. Thứ tự cụm, hướng, chiều và r chọn chung bằng `chord_tour.choose`, như trước.

**Kiểm tra trên r200 k16-s1** (`passes-r200-k16.md`; `C4/DRT` là bản lập kế hoạch thử):

| phương án | độ dài trong cụm (m) | thời gian trong cụm (s) | tốc độ (m/s) | góc quay trong cụm | crit trong ξ | tổng pass (s) |
|---|---|---|---|---|---|---|
| CHORD | 2099 | 43,3 | 48,3 | 14° | 42/92 | 850 |
| LM-Tour | 1560 | 40,5 | 38,5 | 111° | 36/92 | 784 |
| DTSP-N + River cũ | 1674 | 40,5 | 41,3 | 103° | 47/92 | 879 |
| **DTSP-N + River đã sửa** | 2438 | **62,4** | 39,6 | 346° | **92/92** | **1462** |

- Đúng như dự đoán ở mục 192: đường đi qua mọi critical cell thì chậm hơn CHORD rõ (62 so với 43 s mỗi cụm; tổng pass 1462 so với 850 s).
- Chỉ C6 có hai đoạn ngắn (430 m, 345 m) bay ra ngoài cụm qua một vịnh. Đường không vòng ngược.
- Hình (không chữ, `uav-l2/docs/figures/dtspn-river-k16-r200-c{8,6,1}-chord-old-zigzag.png`, `dr_fig.py`):
  - xám: CHORD;
  - xanh nét đứt: DTSP-N + River cũ;
  - cam: DTSP-N + River đã sửa.

**Trong chiến dịch** (`logs/2026-10-27_1714-campaign4`):
- Các lượt DTSP-N + River cũ chuyển sang `C4/DR-old`. Số cũ không còn trong bảng.
- `task.sh` chạy DTSP-N + River bằng bản sửa, có dấu riêng `done-dr` và tệp kết quả `score-dr.csv`. Các tác vụ đã xong chỉ chạy thêm phần này.
- Hai tác vụ k8 đang chạy dở bị dừng để khởi động lại; mất khoảng 2 phút River.
