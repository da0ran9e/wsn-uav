# 2026-10-27 · Chiến dịch bốn phương án × 10 seed × 3 bản đồ × 4 kênh (CLAUDE.md §8 mục 187–188)

**Mục đích:** lấy số cho bảng của khung evaluation mới (mục 187). Bốn phương án:
- CHORD + River (đề xuất 1). CHORD ở đây là **CHORD thường**: dây cung dài nhất qua CH, chọn riêng từng cụm, không `--chordTour`.
- LM-Tour + River (đề xuất 2): `lm_tour.py plan --dtspn --weight cl --wmin 1`.
- FC + DTSP-N (DN): toàn hệ thống lớp 2+3 so với hai đề xuất.
- DTSP-N + River (`--dtspnRiver`, kèm `prefly.py`): lợi ích của River so với FC + DTSP-N.

Kèm theo, gần như không tốn thêm: không phát quảng bá (B1, rotary TSP) và oracle (B7).

**Đang chạy** (bảng kết quả điền khi xong từng seed).

**DTSP-N + River (mục 191–193):**
- 02:30: tạm dừng vì người dùng nghi có lỗi.
- Kiểm tra (`logs/2026-10-28_0240-dtspn-check`) cho thấy pass chỉ vào đĩa của 50–70 % critical cell.
- 03:00: sửa (`through_crit`, `logs/2026-10-28_0310-dtspn-fix`), rồi khởi động lại chiến dịch.
- Lượt cũ để ở `C4/DR-old`; dòng DR trong `score-ns3.csv` của 5 tác vụ đầu là bản cũ và bị `table.py` bỏ qua.
- Bản sửa có dấu riêng `done-dr` và kết quả `score-dr.csv`. Các tác vụ đã có `done` chỉ chạy thêm phần DTSP-N + River.

**Hàng đợi job (mục 199, từ 2026-10-28 07:45):**
- Đo trên seed 1: River tốn khoảng 19 giờ-lõi mỗi seed (CHORD 7,9; LM-Tour 6,9; DTSP-N + River 4,2). Các bước Python (lập kế hoạch, chấm điểm) thêm khoảng 2 giờ-lõi.
- Máy có 4 lõi, nên nếu xếp kín thì mỗi seed chỉ cần khoảng 5–6 giờ. Cách chạy cũ mất khoảng 10 giờ:
  - `task.sh` chạy ba phương án của một ô nối tiếp nhau, mỗi mission `--jobs 2`;
  - trong các bước Python và ở đuôi mỗi mission, nửa số lõi đứng không.
- `camp2.sh FIRST LAST` + `job.sh SCH R ENV K`:
  - mỗi (phương án, seed, kênh, bản đồ) là một job, mission chạy `--jobs 1`;
  - bốn job chạy cùng lúc, trộn seed và phương án;
  - trước hàng đợi, hình học CHORD của mọi seed R > 1 được chép từ seed 1 (kèm `runseed.txt`), nên LM-Tour và DTSP-N + River không phải chờ mission CHORD.
- Dấu xong: `done-cp`, `done-lmd`, `done-dr`. Dấu `done` của `task.sh` được hiểu là `done-cp` + `done-lmd`.
- Điểm số: `score-cp.csv`, `score-lmd.csv`, `score-dr.csv`.
- `mission.py` giờ chỉ ghi `env.txt`, `runseed.txt`, `plan-opts.json` khi tệp chưa có hoặc khác nội dung. Lý do: LM-Tour và DTSP-N + River đọc các tệp này của thư mục CHORD qua symlink trong lúc CHORD đang chạy.
- Khởi động lại: `setsid nohup bash camp2.sh 2 10 &`.

## Cách hiểu "10 seed"
- Bản đồ cố định: k8-s1, k12-s1, k16-s1, giống `uav-l2/docs/data/results/raw/` và `logs/2026-10-27_1800-lm-dtspn/`.
- Seed mô phỏng R = 1…10 (`mission.py --runSeed R`, ghi `runseed.txt` trong thư mục chạy). R thay đổi:
  - chỉ số mission ns-3: 100000·K + 100·1 + k + 10⁷·(R − 1). Chỉ số này quyết định fading của pass, bóng che và fading G2G, các lần bốc của MAC;
  - khoá hiện thực hoá phía Python: `CHORDFC/…`, `DN/…`, `FC/…` thêm `/rR`;
  - khối lượt bốc lớp 1: draw 100·(R − 1) … 100·R − 1, và pha LoRa lấy hạt giống từ `k8-s1/rR`.
- Seed 1 cho đúng các khoá cũ, nên R1 so thẳng được với số của phiên trước.
- Mọi phương án trong cùng (R, kênh, bản đồ) dùng chung lượt bốc lớp 1 và pha LoRa, nên là so sánh ghép cặp.
- Mỗi (phương án, kênh, bản đồ) có 10 × 100 = 1000 mẫu T\*. Các mẫu này đến từ 10 hiện thực mạng ns-3.

## Binary
- Dựng lại từ mã hiện tại (`build.md`), đóng băng tại `scratchpad/CAMP-BIN5`:
  - deploy 508c170d8d7af589;
  - pass 4bb3832ed668ac76;
  - river 60a32c1245fd473c.
- Kiểm chứng trên r500-k8-s1, CHORD-T (`validate-r500-k8.md`):
  - pass: `pass*-runs.csv` và `pass*-nodes.csv` giống từng byte với bản lưu trữ ở 8/8 cụm;
  - River: `r*-rf-crit.csv` và `r*-rf-runs.csv` giống từng byte ở 8/8 cụm, trừ cột thời gian thực wallS.
- Bản đồ k16-s1 sinh lại từ đầu (cụm, CH, node, điểm CL) giống từng byte với `raw/r100-k16-s1.tar.xz`.

## Tệp
- `task.sh R ENV K`: một tác vụ, tức bốn phương án trên một (seed, kênh, bản đồ):
  - CP: mission;
  - LMD: plan, rồi mission;
  - DR: plan, `prefly.py`, rồi mission;
  - chấm điểm bằng `lm_tour.py score` (CP, LMD, DR) và `l1_rank.py` (CHORD để đối chiếu, DN, B1, B7);
  - xoá vết từng gói của pass (raw/strip/track), vì River và phần chấm điểm không đọc chúng.
- `camp.sh`: hai tác vụ cùng lúc (mỗi mission `--jobs 2`), theo thứ tự seed → bản đồ lớn trước → kênh khắc nghiệt trước. `done.txt` ghi mỗi tác vụ xong.
- `prefly.py`: bản sao từ `logs/2026-10-27_1800-lm-dtspn/`, có đường dẫn tools tương đối và chỉ số mission theo seed.
- `R<R>/<env>-k<K>.md`: log từng tác vụ.
- `score/R<R>/<env>-k<K>/`: `score-ns3.csv` (CP / LMD / DR), `l1-draws.csv` (CHORD, DN, B1, B7), log của từng bước, `lmd.json`, `dr.json`.

## Lưu ý vận hành (container cloud)
- Container bị thu hồi khi phiên rảnh mà không có tác vụ nền nào do phiên theo dõi:
  - 18:22–19:35 và 19:38–20:50 đều mất tiến trình, máy khởi động lại khi phiên được đánh thức;
  - các tệp trong scratchpad vẫn còn.
- Luôn giữ một `Bash run_in_background` (timeout tối đa 2 giờ) chờ `done.txt` có dòng mới, và đặt lại mỗi khi nó kết thúc.
  - Tác vụ nền này giữ container sống ít nhất 51 phút khi phiên rảnh (21:51–22:42).
  - Nó không chặn được mọi lần khởi động lại: máy vẫn khởi động lại lúc 23:00.
  - Khi đó phiên được báo ngay là tác vụ nền đã mất, nên có thể chạy lại `camp.sh` gần như tức thì.
- Sau khi máy khởi động lại, chạy lại `setsid nohup bash camp.sh 1 10 &`:
  - tác vụ đã có `done` được bỏ qua;
  - `mission.py` bỏ qua pass và River đã xong;
  - River đang chạy dở thì chạy lại từ đầu.
- Máy mới cần `pip install scikit-learn` (`pip.md`). Thiếu gói này thì `lm_tour.py plan` dừng (`river_surrogate`).
