# 2026-10-25 · Ba chế độ kênh A2G cho CHORD: R50 ≈ 500 / 200 / 100 m (CLAUDE.md §8 mục 163)

**Mục đích:** thể hiện ba mức môi trường phức tạp bằng bán kính phát hiệu quả của UAV (R50: khoảng cách ngang mà xác suất một gói 127 B tới được node còn 1/2), rồi chạy P\* (CHORD-T) trên một bản đồ ở cả bốn chế độ.

## Cách làm

**Mô hình:**
- Giữ kênh đang dùng: không gian tự do tới 100 m, sau đó số mũ 3; Rician K = 2 bốc lại mỗi gói; UAV phát +10 dBm.
- Cộng thêm một suy hao cố định η (dB) trên mọi liên kết UAV–node, tượng trưng cho vật cản quanh node và suy hao xuyên tường.
- Kênh G2G mặt đất không đổi.

**ns-3:** `coop-pass --lossDb`.
- Một `MatrixPropagationLossModel` chèn giữa suy hao đường truyền và fading; khâu này không bốc số ngẫu nhiên.
- Binary pass v3 nằm trong `scratchpad/CAMP-BIN3`, sha256 `6f700762…`; các thư viện giống bộ `CAMP-BIN`.
- Hồi quy với η = 0: bitmap và strip giống hệt v2 (`regress-v3-loss0.md`).

**Hiệu chỉnh trên ns-3** (`uav-l2/tools/a2g_env.py`, `calibrate.md`):
- Bay cụm c1 của k2-s4 (1 675 node).
- Mỗi cặp (node, gói) được xếp theo khoảng cách ngang lúc gói được phát, rồi đo p(r).
- Dò η theo phương pháp cát tuyến cho tới khi R50 trúng mục tiêu trong 2 %.

| chế độ | η (dB) | R50 đo (m) | R10 đo (m) | p(0) | p(100 m) | p(200 m) | p(500 m) |
|---|---|---|---|---|---|---|---|
| open | 0 | 1015 | 1366 | 0,999 | 0,999 | 0,996 | 0,950 |
| r500 | 9,03 | 498 | 678 | 0,998 | 0,993 | 0,968 | 0,494 |
| r200 | 19,77 | 199 | 284 | 0,960 | 0,887 | 0,495 | 0,000 |
| r100 | 25,74 | 99 | 162 | 0,838 | 0,496 | 0,014 | 0,000 |

- Mô hình giải tích `a2g_radius.py` (ngưỡng −101 dBm) cho cùng các con số (`radius-analytic.md`).
- Hình: `uav-l2/docs/figures/a2g-env-p-of-r-4modes.png`.

**`mission.py --env {open,r500,r200,r100}`** (bảng `ENV_LOSS`):
- Truyền `--lossDb` cho lượt bay.
- Ghi `env.txt`; một thư mục đã bay ở chế độ khác thì dừng, không chạy tiếp.
- Ghi `lossDb` vào `plan-opts.json` để kế hoạch River và phân tích dùng cùng kênh.

## Sửa trong kế hoạch River (lỗi lộ ra ở r100)

**Triệu chứng:** lần chạy đầu ở r100 (`P-r100-k8-s1.md`), River dừng ở giới hạn 900 s tại 6/8 cụm.

**Nguyên nhân:**
- Với `--axeNear`, gói phát khi UAV ở ngay ngoài mép cụm vẫn được giao cho cell gần nhất của cụm.
- Ở r100 không node nào nghe được 11–273 gói như vậy mỗi cụm (`need-unheld.md`, `seg-unheld.md`).
- Gói phát khi UAV ở trên cell của chính cụm thì luôn được cell Axe đó giữ, ở cả bốn chế độ.

**Sửa:** hàm `river_plan.plan(near_loss)` và tham số `river_export --lossDb`.
- BS dùng mô hình kênh của chế độ: một gói ngoài mép chỉ vào Seg(h) nếu xác suất không node nào của h nghe được ≤ 10⁻⁶.
- Phân tích (`mission_report.load_map`) lập lại kế hoạch giống hệt.

**Kiểm tra** (`replan-*.md`):
- Kế hoạch của open và r500 không đổi ở cả 8 cụm.
- r200 bỏ bớt một ít gói ngoài mép; D còn 4 467–5 713.
- r100 còn D 4 045–4 329, vẫn ≥ 4 041 tức một bản tập manh mối.
- River chạy lại cho r200 và r100 (`P-r200-k8-s1-gate.md`, `P-r100-k8-s1-gate.md`); lượt bay giữ nguyên. Kết quả cũ chuyển sang `scratchpad/ENV-old/`.

## Kết quả: P\* trên k8-s1 (8 cụm, 45 critical cell, 100 lần bốc lớp 1; `cmp-table-out.md`)

| chế độ | tour 45° (s) | rời cụm TB (s) | River xong TB / p90 / max (s) | đủ 12 manh mối | T\* P\* TB / trung vị (s) | T\* kéo thẳng (s) | T\* không hợp tác (s) | khung mặt đất River / kéo thẳng |
|---|---|---|---|---|---|---|---|---|
| open | 782 | 328 | 8 / 18 / 35 | 100 % | 762 / 643 | 762 | 781 | 146 k / 138 k |
| r500 | 782 | 328 | 54 / 103 / 160 | 100 % | 808 / 723 | 806 | 1 408 | 1 556 k / 1 621 k |
| r200 | 782 | 328 | 99 / 208 / 216 | 100 % | 860 / 728 | 858 | 3 122 | 2 795 k / 2 481 k |
| r100 | 782 | 328 | 121 / 233 / 270 | 100 % | 878 / 763 | 872 | 3 402 | 3 326 k / 2 825 k |

**Nhận xét:**
- **Hợp tác mặt đất đổi vai trò khi môi trường khó lên.**
  - Ở open, không hợp tác chỉ chậm hơn 19 s.
  - Ở r500 / r200 / r100, không hợp tác chậm hơn 600 / 2 262 / 2 524 s.
  - Lý do: không có hợp tác thì critical cell thiếu manh mối nên đối sánh kém, và đội 2 phải thăm nhiều cell sai trước khi tới c\*.
  - Với hợp tác, T\* chỉ tăng 46–116 s so với open; mọi critical cell vẫn đủ 12 manh mối.
- **River so với kéo thẳng:**
  - T\* như nhau ở mọi chế độ (lệch ≤ 6 s, kéo thẳng hơi nhanh hơn ở r100).
  - Ở r200 và r100, River tốn khung hơn kéo thẳng (+13 % và +18 %). Bank đặt ở 1,75 cell (≈ 300 m) vốn dựa trên giả định Bank đã có gần đủ dữ liệu. Ở R50 ≤ 200 m Bank gần như không nghe được gì, nên Axe phải đẩy cả đoạn ra Bank.
  - Hướng nên thử: độ rộng River theo bán kính phát hiệu quả của chế độ.
- **Lớp 2 không đổi:** tour và thời điểm rời cụm giống nhau ở mọi chế độ, vì việc giao một bản tập manh mối được tính theo hình học. Ở r100, mỗi node ngay dưới đường bay chỉ nghe khoảng 9 % bản đó.
- Đây là số của **một bản đồ**, chỉ để định hướng.

## Dang dở
- Các baseline mức mô hình (B2, B3, B5, B8) vẫn tính PER bằng Nakagami m = 1,8, chưa theo chế độ kênh.
- Ablation k-medoids chưa chạy ở các chế độ mới.
- Độ rộng River theo chế độ kênh: chưa thử.
