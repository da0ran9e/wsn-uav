# 2026-10-24 · CH ở vị trí ngẫu nhiên cho cả CHORD-T và MEANDER (CLAUDE.md §8 mục 154)

**Mục đích:** bỏ lợi thế tự chọn vị trí CH để so sánh công bằng hơn. Hiện nay mỗi phương án được chọn CH theo cách có lợi cho mình:

- CHORD-T lấy node mạnh nhất cách biên ≥ 300 m.
- MEANDER lấy node mạnh nhất nằm dưới đường luồng.

Ở đây cả hai cùng lấy **node mạnh nhất cụm, ở bất kỳ đâu** (`--chAnywhere`: không ràng buộc khoảng cách tới biên, không giới hạn ô dưới đường bay). Điểm năng lực của các node là ngẫu nhiên độc lập, nên CH rơi vào vị trí ngẫu nhiên. Cả hai phương án vẫn phải bay qua CH (pass ns-3 kiểm tra dPath < 1 m):

- CHORD-T: dây cung đi qua CH, hướng chọn cùng với tour như trước.
- MEANDER: luồng thẳng bị uốn để ghim vào CH, theo bước 6 (`bend_lane`).

Bản đồ, số cụm và cách chia cụm giữ nguyên như `logs/2026-10-24_0514-meander-trim/`: k8 seed 1–3, K = 5, MEANDER `--parallel --trim 5 --minAxe 2.1`. Chỉ thay quy tắc chọn CH.

**Mã:** thêm cờ `--chAnywhere` vào bốn tệp:

- `mission.py`: thử margin 0 trước.
- `swath_mission.stage_deploy`: không dùng `--chCells`, thử margin 0 trước.
- `meander_lane.py`.
- `trim_sweep.py`: truyền cờ cho cả hai phương án.

Ở cả 21 lần deploy, margin 0 đều khả thi; không lần nào phải lùi sang margin lớn hơn.

**Lệnh:** `sweep.md`; từng lần chạy ở `ml-*.md` và `chord-*.md`. Bảng kết quả ở `ch-anywhere-table.md`; hình sinh từ `fig-s*.md`.

**Kết quả: tour ở 45°, đã cộng thời gian bù giao đủ (s); trong ngoặc là số cụm phải bù**

| seed | CHORD-T, CH tốt nhất | CHORD-T, CH ngẫu nhiên | MEANDER, CH tốt nhất | MEANDER, CH ngẫu nhiên | critical trong 5 cell (CH ngẫu nhiên): CHORD-T / MEANDER |
|---|---|---|---|---|---|
| 1 | 506 (2) | 578 (2) | 490 (1) | **480** (2) | 81 % / 92 % |
| 2 | 515 (2) | 554 (4) | 485 (1) | **484** (2) | 73 % / 92 % |
| 3 | 490 (2) | 577 (5) | 499 (1) | **562** (1) | 64 % / 84 % |

- **CHORD-T chậm thêm 39–87 s.** Dây cung bắt buộc đi qua CH; khi CH nằm gần biên, dây cung nằm trong cụm ngắn đi. Số cụm phải bù tăng từ 2 lên 2–5, và đoạn nối cùng đường về BS dài ra.
- **MEANDER gần như không đổi ở s1, s2** (−10 và −1 s) **và chậm thêm 63 s ở s3.** Luồng uốn tới CH, dịch ngang tới 700 m, nhưng độ cong vẫn trong giới hạn (k·ρ ≤ 0,53). Trên s1, s2 phần dài thêm trên cụm bù cho phần nối giữa các luồng ngắn đi; ở s3 đường bay trên cụm dài thêm 2 km.
- **Với CH ngẫu nhiên, MEANDER nhanh hơn CHORD-T trên cả 3 bản đồ:** −98, −70, −15 s. Tỉ lệ critical cell nằm trong 5 cell quanh đường bay cũng cao hơn (84–92 % so với 64–81 %).

**Lưu ý về công bằng:** hai phương án chia cụm khác nhau (k-medoids và luồng), nên CH của chúng không phải cùng một node. Chỉ có quy tắc chọn CH là giống nhau.

**Dang dở:**

- Chưa chạy ns-3.
- Đường MEANDER không còn thẳng hẳn, vì phải uốn tới CH. Có thể bỏ yêu cầu bay qua CH (CH nhận dữ liệu qua River như mọi critical cell khác) để giữ đường thẳng, nhưng đây là thay đổi trong mô hình, cần người dùng quyết.
