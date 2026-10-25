# 2026-10-25 · Vì sao CHORD thua, và sửa để CHORD thắng rõ (CLAUDE.md §8 mục 169)

**Mục đích:** người dùng thấy đội 1 của CHORD thường xong sớm hơn mà CHORD vẫn thua, và yêu cầu sửa để CHORD thắng rõ.

**Chẩn đoán** (`logs/2026-10-25_0600-fc-baseline/l1rank/all-*`):
- CHORD chỉ thua ở kênh open. Nguyên nhân là báo cáo của c\* về BS muộn hơn FC 100–150 s; pha 2 sau đó gần như bằng nhau.
- Hai lý do:
  - FC và DN được mã fountain, CHORD thì không.
  - Ở kênh open, FC chỉ cần ghé khoảng một phần ba số critical cell.
- Ngoài ra, River có hai lỗ hổng làm 8 critical cell không xong (k16 open và k16 r100).

## Các bước và log
| Bước | Lệnh / log | Kết quả |
|---|---|---|
| CHORD có mã fountain (`-fcd`), chấm thử | `try-fcd-k8.md`, `try-fcd-open.md` | T\* ở open: k8 762 → 647, k12 939 → 686, k16 1 161 → 863 s; r200 giữ nguyên. Lượt đầu ở r200 bị kéo lên 1 442 s vì báo cáo tự giải mã đến muộn đã đè lên báo cáo River; sửa bằng cách cho mỗi báo cáo cộng dồn mọi thứ cell đã có |
| Lần theo gói kẹt trong River | `logs/2026-10-25_0600-fc-baseline/stall-*.md`, `stall_why.py` | C9: gói thuộc Seg của cell Axe nhưng chỉ cell bên cạnh nghe được. C1 và C6: một khung "gửi thành công" mà không radio nào nhận được (ACK nhầm, vì ACK 802.15.4 chỉ có số thứ tự 8 bit). Đoạn mã chẩn đoán tạm đã gỡ khỏi nguồn |
| Sửa River `--repair` | `repair-test.sh` → `repair-test.md` | Tắt: trùng từng byte với binary cũ. Bật: C1, C9, C6 đều xong (71 / 119 / 55 s) |
| Đóng băng `CAMP-BIN4` | sha256 `river-bin` 2e636b6d…; `deploy-bin` và `pass-bin` như CAMP-BIN3 | |
| River với `--repair 20` trên 12 thư mục | `river-fix.sh` → `fix-<kênh>-k<K>-s1.md`, `fix-done.txt` | 0/812 critical cell kẹt (trước là 8). Thời gian River gần như không đổi |
| Chấm 4 phương án × 12 tổ hợp | `score.sh` → `score-all.md`, `l1rank/all-*.csv`; bảng `table-all.md` | xem `uav-l2/docs/RESULTS-vi.md` |
| Animation ba thuật toán (bản mới) | `anim-export-k8.md` | https://claude.ai/artifact/L1Fv5Yq8NVPtVYbUyrDhkh (lượt bốc 2); khung `figures/cmp3v2-k8-s1-r200-mid-frame.png` |
| Bản lưu 12 thư mục `FIX/` | `archive-all.md` | `uav-l2/docs/data/results/raw/`, 20 MB |

## Kết quả chính
- CHORD nhanh hơn cả FC và DN ở 12/12 tổ hợp, có ý nghĩa thống kê ở 11/12 (so sánh ghép cặp theo lượt bốc):
  - open: nhanh hơn 2 / 15 / 9 %;
  - r500: 27 / 32 / 37 %;
  - r200: 54 / 61 / 66 %;
  - r100: 60 / 70 / 72 % (k8 / k12 / k16).
- k8 open gần như hoà: −13 ± 34 s, CHORD nhanh hơn ở 66 % số lượt bốc. Bản đồ nhỏ và bán kính nghe 1 km nên tuyến nào cũng phủ hết rất sớm; phần còn lại là pha 2, giống nhau ở mọi phương án.

## Thay đổi mã
- `uav-coop2/examples/coop2-river.cc`: tuỳ chọn `--repair=S`.
  - Cell Axe lấy nốt gói thuộc Seg của nó từ cell kề bên.
  - Critical cell im lặng S giây mà vẫn thiếu thì hỏi lại theo chuỗi Circle → Bank → Axe.
  - Mặc định tắt.
- `uav-l2/tools/mission.py`: `--riverRepair S`.
- `uav-l2/tools/l1_rank.py`: tuỳ chọn `-fcd` cho P+prog.
- `uav-l2/tools/fc_baseline.py`: ghi thêm `<tag>-cells.csv`.
- `uav-l2/tools/fc_table.py`: thêm hàng CHORD (mới) và CHORD-0.
- `uav-l2/tools/cmp3_anim.py`, `uav-l2/docs/anim/cmp3-body.html`: panel CHORD tính cả phần tự giải mã.

## Còn dang dở
- **Cải tiến thêm cho kênh open trên bản đồ nhỏ (chưa làm):** CHORD có thể bỏ qua dây cung của cụm mà mọi critical cell đã đủ dữ liệu từ các lượt bay trước, như FC đang làm. Ước tính lợi ích nhỏ, vì các cell đã được phục vụ sớm.
- **Chiến dịch nhiều bản đồ (mục 165)** vẫn chờ người dùng chốt.
