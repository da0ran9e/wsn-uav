# 2026-10-25 · LM-Tour: bước A (bộ dự đoán River) và bước C (LM-Tour bằng Python) (CLAUDE.md §8 mục 171–175)

**Mục đích:**
- **Bước A.** Học một bộ dự đoán thời gian River của từng critical cell. Mọi đầu vào phải là thứ BS biết trước khi đội 1 cất cánh. Bộ dự đoán học trên các lượt ns-3 đã có.
- **Bước C.** Cài LM-Tour (mục V của draft) bằng Python, dùng bộ dự đoán đó, và thử trên một bản đồ.

## Đầu vào
- 12 thư mục `scratchpad/FIX/{open,r500,r200,r100}/k{8,12,16}-s1`: CHORD, River `--repair 20`, binary CAMP-BIN4, 812 critical cell.
- Bản lưu các thư mục này: `uav-l2/docs/data/results/raw/`.

## Các bước và log
| Bước | Lệnh / log | Kết quả |
|---|---|---|
| A. Bảng đặc trưng và khớp mô hình | `a-surrogate.md` (`river_surrogate.py`) | Xem dưới. Kế hoạch River tính lại khớp với `plan{k}.txt` mà ns-3 đã chạy (sai lệch tối đa 2 gói ở biên cell). |
| A. Hình | `fig-surrogate.md` → `figures/lm-surrogate-pred-vs-ns3.png` | |
| C. Kiểm tra bộ chấm điểm | `c-validate-ns3.md` | `lm_tour.py score --mode ns3` cho lại đúng T\* của từng lượt bốc mà `l1_rank` đã chấm cho CHORD trên r200/k8-s1 (sai khác 0,0 s). |
| C. CHORD chấm bằng River dự đoán | `c-chord-pred-k8.md` | T\* k8: 647 / 783 / 870 / 881 s (open / r500 / r200 / r100), ns-3 là 647 / 784 / 876 / 872 s. |
| C. Sweep 1: hàm mục tiêu từng cụm chưa tính đoạn nối | `c-sweep.sh` → `c-plan-*`, `c-score-*` | Xem dưới. |
| C. Sweep 2: hàm mục tiêu tính cả đoạn nối Dubins | `c-sweep2.sh` → `c2-plan-*`, `c2-score-*` | Xem dưới. |
| C. Hình | `fig-passes.md` → `figures/lm-k8-s1-r100-R450-chord-vs-lm.png` | |

## Kết quả chính

### Bước A
Kiểm tra theo kiểu bỏ một bản đồ ra (leave-one-map-out): bản đồ k8, k12 và k16, mỗi bản đồ đủ 4 kênh, lần lượt làm tập thử.

| Mô hình | MAE (s) | R² |
|---|---|---|
| trung bình | 42,4 | −0,02 |
| **công thức** | **22,8** | **0,60** |
| tuyến tính, đủ 12 đặc trưng | 23,0 | 0,60 |
| cây tăng cường | 26,1 | 0,40 |

Bỏ một kênh ra: công thức đạt 22,3 s / 0,63, cây đạt 28,6 s / 0,55.

- **Công thức:** doneS ≈ 0,7 + 2,3·hops + 2,0·lackCell/1000 + 4,3·cluLack/1000 (giây).
- **89 % phương sai nằm giữa các cụm.** Đại lượng quyết định là cluLack, tổng số gói mà các critical cell của cụm còn thiếu, tức lượng River phải chuyển. Khoảng cách tới đường bay ảnh hưởng ít.
- **Lượng thiếu dự đoán từ `hear_model` khớp ns-3:** r = 1,000.
- **Mô hình cây không hơn công thức** trên bản đồ nó chưa thấy. Dữ liệu hiện có chỉ gồm 3 bản đồ.
- **Phần đuôi bị dự đoán thấp.** Các cell River kéo dài 150–310 s đều bị dự đoán thấp hơn thực tế.

### Bước C
- **Cách làm trên cluster có sẵn:**
  - Bước 1–2 của LM-Tour (R-net, tour qua đĩa) rút về chính dây cung CHORD qua CH.
  - Phần riêng của LM-Tour là bước chèn: uốn dây cung vào đĩa B(c, R/2) của critical cell. Mỗi lần chèn cell làm giảm nhiều nhất J_k = Σ ready + n_k·t_in + θ·N_after·(t_in + dur + t_out), với θ = 1.
- **Cách đo:** chênh lệch T\* ghép cặp so với CHORD, cả hai đều chấm bằng River dự đoán, 100 lượt bốc, bản đồ k8-s1, khoảng tin cậy 95 %. Đơn vị: giây.

| | open | r500 | r200 | r100 | tour đội 1 |
|---|---|---|---|---|---|
| Sweep 2, R = 200 | −0,8 ± 3,5 | +1,4 ± 5,9 | −7,3 ± 14,5 | −5,3 ± 4,6 | −4 |
| Sweep 2, R = 450 | −1,2 ± 3,3 | +8,0 ± 27,5 | −1,5 ± 8,1 | **−10,7 ± 7,4** | −12 |
| Sweep 2, R = 800 | −3,1 ± 3,0 | +14,9 ± 25,0 | +0,6 ± 6,3 | −3,7 ± 4,4 | −7 |
| Sweep 1, R = 200 | +2,8 ± 3,3 | +18,0 ± 29,3 | −4,7 ± 15,0 | **+9,8 ± 7,9** | +10…+18 |

**Kết luận bước C:** LM-Tour gần như bằng CHORD, hơn nhiều nhất khoảng 1 %, và phần lớn nằm trong nhiễu.
- Mỗi lần uốn chỉ rút River của cụm đi 0–5 s, vì cluLack hầu như không đổi.
- Cụm đã được làm chậm để nhận đủ một bản sao, nên không critical cell nào tự giải mã được từ pass.
- Pha 2 chiếm khoảng nửa T\*.
- Ở sweep 1, khi chưa tính đoạn nối, uốn dây cung làm tour dài thêm và T\* xấu đi ở r100.

## Thay đổi mã
- `uav-l2/tools/river_surrogate.py` (mới): đặc trưng, bảng dữ liệu, các mô hình, kiểm tra chéo.
- `uav-l2/tools/lm_tour.py` (mới): `plan` (LM-Tour) và `score` (chấm toàn nhiệm vụ ở mức mô hình, theo cùng đường mã của `l1_rank`).
- `uav-l2/tools/pass_speed.py`: tách hàm `fit` khỏi `run`. Đầu ra không đổi, đã kiểm trên FIX r200 k8-s1.
- `uav-l2/tools/meander_lane.py`: `bend_lane` nhận thêm `cap`. Mặc định không đổi.
- Dữ liệu: `uav-l2/docs/data/results/river-surrogate{.csv,-scores.csv,-fit.json}`.

## Còn dang dở
- **Bước D chưa làm** (chạy ns-3 trên đường LM-Tour), chờ người dùng quyết.
- Điểm từng lượt bốc và `lm.json` của mọi cấu hình: `uav-l2/docs/data/results/lm-tour/` (LM = sweep 1, LM2 = sweep 2).
- Các thư mục LM-Tour nằm ở `scratchpad/LM*/R*/<kênh>/k8-s1`. Mỗi thư mục là các liên kết tới FIX cộng các pass mới; chỉ `lm.json` và các pass mới là có thật trong thư mục.
- Nếu chạy D: `river_export` cần `--banks local` vì pass đã cong.
