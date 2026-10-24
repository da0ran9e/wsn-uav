# 2026-10-24 · MEANDER chia cụm theo các CH có sẵn (CLAUDE.md §8 mục 155)

**Mục đích:** CH coi là thiết bị có sẵn, vị trí cố định và ngẫu nhiên. MEANDER phải dựng cụm quanh đúng các CH đó, không được tự chọn CH dưới đường bay. Để công bằng, dùng đúng bộ CH của mạng cụm có sẵn (CHORD-T, cụm k-medoids, CH là node mạnh nhất cụm ở bất kỳ đâu, `--chAnywhere`, `logs/2026-10-24_0522-ch-anywhere/`). Hai phương án vì thế phục vụ cùng 5 CH, đã kiểm tra trùng toạ độ. Bản đồ: k8 seed 1–3, K = 5.

**Mã (`meander_lane.py --chFrom DIR`):**

- **Đọc CH:** lấy CH từ `DIR/c*-nodes-s35.csv`.
- **Chọn luồng:** quét hướng 5° và 6 độ lệch luồng. Ưu tiên phương án không có luồng nào thiếu CH, rồi đến tour ước lượng ngắn nhất. Tour ước lượng gồm phần đã cắt, phần cụm thiếu so với minAxe, và phần dài thêm do uốn tới CH; một chỗ uốn biên độ a thêm a^1,5·√π/(4√(2ρ)) mét.
- **Chia cụm:** mỗi luồng được cắt giữa các CH nằm trong nó, mỗi CH một cụm. Điểm cắt đặt theo phần đất chia đều, giữ cách CH ít nhất một cell.
- **Cắt đầu luồng:** từng đầu cắt riêng và không vượt qua CH đầu hoặc cuối. Phần đầu này không cắt được thì đầu kia cắt bù.
- **Luồng không có CH:** không bay; cell của nó nhập vào cụm kề.
- **Deploy:** CH lấy đúng cell của CH cho trước, margin 0 (sửa `swath_mission.stage_deploy`).
- **`trim_sweep.py`:** thêm biến thể `par-trim5-chord`.

**Lệnh:**

- `sweep.md`: chạy quét (thư mục làm việc `T154`, dùng chung với mục 154).
- `ml-s*-par-trim5-chord.md`: luồng 8 cell.
- `ml-s*-par-trim5-chord-lane10.md`: luồng 10 cell, chạy tay.
- `try-s1.md`: bản thử đầu, cắt đầu luồng đối xứng.
- `given-ch-table.md`: bảng kết quả.
- `fig-s*.md`: lệnh sinh hình.

**Kết quả: tour ở 45°, đã cộng thời gian bù giao đủ (s); trong ngoặc là số cụm phải bù**

| seed | CHORD-T (cụm có sẵn) | MEANDER tự chọn CH (mục 154) | MEANDER theo CH có sẵn, luồng 8 cell | MEANDER theo CH có sẵn, luồng 10 cell | critical trong 5 cell: CHORD-T / luồng 8 / luồng 10 |
|---|---|---|---|---|---|
| 1 | 578 (2) | 480 (2) | **533** (1) | **530** (3) | 81 % / 95 % / 95 % |
| 2 | 554 (4) | 484 (2) | 569 (2) | **549** (4) | 73 % / 87 % / 92 % |
| 3 | 577 (5) | 562 (1) | 624 (1) | **529** (3) | 64 % / 91 % / 81 % |

- **Mất quyền chọn CH, MEANDER chậm thêm 53–85 s** (so với bản tự chọn CH). Luồng nào cũng phải chứa CH, nên hướng và độ lệch luồng bị bó buộc; đường bay phải uốn tới 690 m; s3 cần tới 5 luồng.
- **Luồng 8 cell:** MEANDER thắng CHORD-T 1/3 bản đồ (−45, +15, +47 s).
- **Luồng 10 cell:** MEANDER thắng 3/3 (−48, −5, −48 s), vì ít luồng hơn (3–4) nên ít vòng quay đầu hơn.
  - Đổi lại có 3–4 cụm phải giảm tốc hoặc lượn bù. Ở s2 có cụm chỉ được 0,42 km Axe.
  - Luồng rộng 10 cell nghĩa là cell xa nhất cách đường bay khoảng 5 cell, đúng ngưỡng người dùng chấp nhận ở mục 151.
- **Gần critical cell:** MEANDER vẫn hơn CHORD-T rõ rệt (81–95 % so với 64–81 %).

**Dang dở:** chưa chạy ns-3. Pass ns-3 bay đều 50 m/s nên chưa mô phỏng được phần lượn bù; điều này ảnh hưởng nhiều hơn tới luồng 10 cell.
