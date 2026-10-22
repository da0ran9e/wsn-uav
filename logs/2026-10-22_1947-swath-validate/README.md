# 2026-10-22 · Kiểm tra các phương án lớp 2 trên 16 bản đồ, ghép cặp (CLAUDE.md §8 mục 136)

**Mục đích:** chốt lớp 2 của propose trước chiến dịch. So với bản trước (k-medoids, đường thẳng dài nhất qua CH) bằng cùng P\* và cùng thế giới lớp 1 (ghép cặp theo tên bản đồ).

**Bản đồ:** 4 mỗi cỡ, `random.Random(136)` từ 40 bản đồ chiến dịch: k2-s4, s9, s10, s23; k4-s2, s13, s20, s21; k6-s9, s11, s13, s20; k8-s1, s8, s10, s11.

**Lệnh** (từ `uav-l2/`, binary đóng băng scratchpad `BIN/`):
- `job.sh` (`jobs.txt`): KD = k-medoids (`mission.py --windowAt crit --critRing domain --axeNear`), SW = SWATH-K (`swath_mission.py --axeNear`). Ba bản đồ k4-s2, k6-s9, k8-s10 dùng lại các lần chạy của `logs/2026-10-22_1806-propose-iter/` vòng 5.
- `job-lat.sh`: SWL = SWATH-K `--routeBy latency`.
- `job-ct.sh` (`jobs-ct.txt`, `jobs-ct34.txt`, `jobs-ct5.txt`): CHORD-T `--chordTour FRAC,CLUE`, trên bản sao thư mục KD (lượt bay giữ cho cụm không đổi hướng): CT1 0,6/0,8; CT2 0,7/0,9; CT3 0,6/0,7; CT4 0,5/0,8; CT5 0,5/0,6.
- Chấm điểm: `score-*.md` (`l1_rank.py`, 100 lượt bốc), `l2m-16.md` (`l2_metrics.py`), `compare.py` → `compare-all.txt`. Hình học trước khi chạy: `route_proxy.py`, `chord_tour.py` (`chord-geom-0.6-0.8.md`).
- Mọi lần chạy thoát 0 (`done*.txt`).

**Đầu ra:** thư mục làm việc trong scratchpad `VA/` (3,1 GB, không commit; liên kết đặt tên theo bản đồ ở `VB/<set>/<map>`). Bảng: `uav-l2/docs/data/l2iter/` (draws gzip, summary, cells, l2m). Hình: `uav-l2/docs/figures/l2-variants-16maps.png`, `chordT-tradeoff-16maps.png`, `chordT-k6-s9-kmedoids-vs-chordT1.png`.

**Kết quả** (chênh so với k-medoids, 16 bản đồ, ghép cặp):

| Phương án | ΔT\* (tốt hơn) | ΔT\* p90 | Δ tour đội 1 | critical cell đủ 12 manh mối | Δ khung River |
|---|---|---|---|---|---|
| SWATH-K | +6 s (8/16) | −6 s | +22 s | — | +38 k |
| SWATH-L | −4 s (10/16) | −47 s | +42 s | — | +94 k |
| CHORD-T CLUE 90 % | −14 s (13/16) | −24 s | −20 s | 100 % | +63 k |
| **CHORD-T CLUE 80 %** | **−29 s (16/16)** | −37 s | −64 s | 84 % | +105 k |
| CHORD-T CLUE 70 % | −38 s (16/16) | −50 s | −83 s | 63 % | +128 k |
| CHORD-T CLUE 60 % | −38 s (16/16) | −46 s | −84 s | 59 % | +117 k |

Lợi của hợp tác (không hợp tác trừ P\*): k-medoids +19 s, CHORD-T 80 % +50 s. Báo cáo: `uav-l2/docs/PROPOSE-ITER-vi.md`.

**Dang dở:** chọn CLUE (đề xuất 80 %), chốt N, chiến dịch và baseline.

**Thêm sau:** độ nhạy D = 64 / 256 (`sens-dim*.md`): CHORD-T 80 % −30 / −29 s, 70 % −37 / −36 s. Kéo thẳng trên thư mục CHORD-T 80 % (`job-d.sh`, `CT1d-*.md`, `score-ct1-direct.md`): T\* bằng River (+0,5 s), River ít hơn 11 % khung.
