# 2026-10-26 · Bảng chung CHORD và sáu baseline (CLAUDE.md §8 mục 181–182)

**Mục đích:** chạy các baseline đã đề xuất ở mục 181 (Pd, B4, B1, B7) cùng CHORD, FC và DN trên cùng 12 tổ hợp (3 bản đồ × 4 kênh), rồi dựng một bảng chung như bảng của mục 167. Các phần chạy được thì chạy song song.

## Đầu vào
- 12 thư mục `scratchpad/FIX/{open,r500,r200,r100}/k{8,12,16}-s1`. Đây là các thư mục của mục 169 (CHORD, River `--repair 20`, binary CAMP-BIN4).
- Bản lưu các thư mục này: `uav-l2/docs/data/results/raw/`.

## Các bước và log
| Bước | Lệnh / log | Kết quả |
|---|---|---|
| Thêm B4 vào `l1_rank` | `try-b4-r200-k8.md` (5 lượt bốc) | B4 = CHORD không River: cùng đường bay và mã fountain, chỉ báo phần cell tự giải được. |
| ns-3 kéo trực tiếp (`--schemes d`) cho 8 thư mục k12, k16 | `pd-run.sh`, 4 tiến trình song song → `pd-<kênh>-k<K>-s1.md`, `pd-done.txt` | 8/8 xong, mã thoát 0, khoảng 55 phút. |
| Kiểm tra binary | `pd-r200-k8-s1-check.md` | Chạy lại k8 r200 bằng CAMP-BIN4 trên bản sao (`scratchpad/PDCHECK`) cho 8/8 `r*-d-crit.csv` giống hệt từng byte bản cũ (CAMP-BIN3). Vì vậy k8 dùng lại các lượt `d` đã có. |
| Chấm phần 1: CHORD, FC, DN, B4, B1, B7 | `score.sh 1 2` → `score-part1.md`, `l1rank/part1-*` | 466 s. CHORD, FC, DN cho lại đúng số của mục 169. |
| Chấm phần 2: Pd | `score.sh 2 4` → `score-part2.md`, `l1rank/part2-*` | 85 s. |
| Bảng chung | `table.md` (`uav-l2/tools/cmp_table.py`) → `uav-l2/docs/data/results/baselines.{md,csv}` | |
| River và kéo trực tiếp ở mức cell | `river-vs-direct.md` (`river_cmp.py`) | |
| Cập nhật bản lưu k12, k16 (thêm các lượt `d`) | `archive.md` | 8 tệp, 1,7–2,2 MB mỗi tệp. |

## Kết quả chính
Bảng đầy đủ và cách đọc: `uav-l2/docs/RESULTS-vi.md` mục 6.

T\* trung bình (s), 100 lượt bốc:

| kênh | bản đồ | CHORD | FC | DN | Pd | B4 | B1 | B7 |
|---|---|---|---|---|---|---|---|---|
| open | k8 / k12 / k16 | 647 / 686 / 863 | 660 / 815 / 949 | 708 / 805 / 967 | 647 / 686 / 863 | 650 / 687 / 862 | 2926 / 4168 / 5169 | 322 / 402 / 404 |
| r500 | k8 / k12 / k16 | 784 / 950 / 1107 | 1138 / 1451 / 1801 | 1078 / 1388 / 1750 | 806 / 950 / 1115 | 1379 / 2030 / 2549 | như trên | như trên |
| r200 | k8 / k12 / k16 | 876 / 975 / 1192 | 2285 / 3288 / 3964 | 1904 / 2482 / 3469 | 850 / 990 / 1192 | 3711 / 5277 / 6298 | như trên | như trên |
| r100 | k8 / k12 / k16 | 872 / 990 / 1215 | 2463 / 3460 / 4368 | 2190 / 3248 / 4468 | 875 / 990 / 1334 | 3860 / 5308 / 6358 | như trên | như trên |

- **B4 so với CHORD:** cần hợp tác dưới mặt đất. Không có nó, T\* chậm hơn 1,8–5,4 lần từ r500 trở xuống.
- **Pd so với CHORD:** River và kéo trực tiếp cho T\* gần như bằng nhau. Pd chỉ chậm hơn rõ ở k16 r100, vì 6 cell kéo trực tiếp kẹt (kéo trực tiếp chưa có `--repair`). Ở r200 và r100, kéo trực tiếp tốn ít lượt truyền hơn River 15–20 %.
- **B1:** chậm hơn CHORD 3,3–6 lần. **B7:** chặn dưới.

## Thay đổi mã
- `uav-l2/tools/l1_rank.py`: thêm B4 với `-kt -fcd`.
- `uav-l2/tools/cmp_table.py` (mới): bảng ghép cặp mọi phương án.
- `river_cmp.py` (trong thư mục log này): so River với kéo trực tiếp ở mức cell.

## Còn dang dở
- Kéo trực tiếp chưa có cơ chế sửa gói thiếu như River `--repair`. Nếu muốn so công bằng hoàn toàn ở k16 r100 thì cần thêm cơ chế này vào scheme `direct` và chạy lại (7–30 phút cho một thư mục k16 trên ns-3).
- Mỗi cỡ bản đồ vẫn chỉ có một bản đồ (chiến dịch nhiều bản đồ ở mục 165 chưa chạy).
