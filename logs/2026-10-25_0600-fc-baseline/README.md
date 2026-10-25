# 2026-10-25 · Baseline FC và DN so với CHORD trên 3 cỡ bản đồ × 4 kênh (CLAUDE.md §8 mục 166–168)

**Mục đích:**
- Mục 166: dựng baseline FC (mã fountain, không River, đội 1 lượn qua từng critical cell) và so với CHORD trên 3 kênh × 3 cỡ miền, mỗi cỡ một bản đồ chung.
- Mục 167: lưu bảng kết quả và seed để chạy lại.
- Mục 168: dựng baseline DN (gom critical cell thành nhóm neighbor nhỏ, đội 1 bay theo DTSP-N), và làm animation ba thuật toán trên cùng bản đồ.

**Kết quả chính:** xem `uav-l2/docs/RESULTS-vi.md` (bảng đầy đủ, seed, lệnh chạy lại).
- Ở kênh open, FC và DN nhanh hơn CHORD 16–22 %.
- Từ r500 trở xuống, CHORD nhanh hơn baseline tốt nhất 25–69 %, và khoảng cách tăng theo cỡ bản đồ.

## Các bước và log
| Bước | Lệnh / log | Ghi chú |
|---|---|---|
| CHORD trên k12-s1, k16-s1 ở r100, r200, r500 | `chord-env.sh`, `P-<kênh>-k<K>-s1.md`, `done.txt` | binary `scratchpad/CAMP-BIN3`; k8-s1 đã có từ mục 163; kênh open của k12 và k16 lấy từ mục 164 |
| FC, chấm thử k8 | `score-k8.md`, `fig-k8.md` | hình `uav-l2/docs/figures/fc-k8-s1-chord-vs-fc-4env.png` |
| Bảng và bản lưu (mục 167) | `table-k8.md`, `archive-k8.md`, `roundtrip.sh`/`roundtrip.md` | Giải nén `r200-k8-s1` rồi chạy lại: 32/32 tệp giống hệt từng byte |
| DN, chấm k8 ba phương án | `score-k8-dn.md` | Tách phần dùng chung của FC xong, FC vẫn cho kết quả y hệt |
| Animation ba thuật toán | `anim-export-k8.md` | https://claude.ai/artifact/L1Fv5Yq8NVPtVYbUyrDhkh; khung `figures/cmp3-k8-s1-r200-mid-frame.png` |
| Chấm cả 12 tổ hợp | `score.sh` → `score-all.md`, `l1rank/all-*.csv`; bảng `table-all.md` | 100 lượt bốc lớp 1 mỗi tổ hợp; `score-k12k16-r100r200.md` là lượt chấm sớm một phần, cho kết quả trùng với lượt chấm đầy đủ |
| Bản lưu cả 12 thư mục | `archive.sh` → `archive-all.md` | `uav-l2/docs/data/results/raw/`, 20 MB |
| Các cell River kẹt | `stall-trace.sh`/`.md`, `stall_why.py` → `stall-why.md` | Chạy lại River có vết cho C1, C9 của k16-s1 ở r100: khớp từng cell với lượt chính |

## Thay đổi mã
- `uav-l2/tools/fc_baseline.py` (mới): baseline FC, cùng phần dùng chung `Ground`, `fly`, `realise`.
- `uav-l2/tools/dn_baseline.py` (mới): baseline DN.
- `uav-l2/tools/fc_table.py` (mới): bảng kết quả và bảng seed.
- `uav-l2/tools/cmp3_anim.py` (mới), cùng `uav-l2/docs/anim/cmp3-head.html` và `cmp3-body.html`: trang replay ba thuật toán.
- `uav-l2/tools/l1_rank.py`:
  - thêm phương pháp FC và DN;
  - một cell River không xong (doneS −1) giờ báo cáo lúc rời cụm + 900 s với phần tự nghe được, thay vì lúc rời cụm − 1 s;
  - ghi vết đội 2 và thời điểm báo cáo cho B5, FC, DN.

## Còn dang dở
- **Lỗi River** (`RESULTS-vi.md` mục 2.1): 8 critical cell (1 ở k16 open, 7 ở k16 r100) thiếu đúng 1 gói. Có hai nguyên nhân: gói thuộc Seg của cell Axe nhưng chỉ cell bên cạnh nghe được; và gói rơi trên đường mà không được hỏi lại. Sửa nghĩa là dựng lại `river-bin` và chạy lại River trên cả 12 thư mục. Chờ người dùng quyết định.
- Chiến dịch nhiều bản đồ (mục 165) chưa chạy: chờ người dùng chốt danh sách baseline, số bản đồ và cách xử lý lỗi River.
